# Packet structure was taken from https://gibbard.me/lidar/



# Main Packet Format
# ----------------------------------------------------------------------
# All fields are little endian
# Header (1 byte) = 0x54
# Length (1 byte) = 0x2C (assumed to be constant)
# Speed (2 bytes) Rotation speed in degrees per second
# Start angle (2 bytes) divide by 100.0 to get angle in degrees
# Data Measurements (MEASUREMENT_LENGTH * 3 bytes) 
#                   See "Format of each data measurement" below
# Stop angle (2 bytes) divide by 100.0 to get angle in degrees
# Timestamp (2 bytes) In milliseconds
# CRC (1 bytes) Poly: 0x4D, Initial Value: 0x00, Final Xor Value: 0x00
#               Input reflected: False, Result Reflected: False
#               http://www.sunshine2k.de/coding/javascript/crc/crc_js.html
#
# Format of each data measurement
# Distance (2 bytes) # In millimeters
# Confidence (1 byte)

# MEASUREMENT_LENGTH = 12

import socket
import struct
import numpy as np
import open3d as o3d
import time
import threading
import queue # lists designed specifically for work with threads
from datetime import datetime


# !!! CONSTANTS !!!
PICO_IP = "192.168.4.1"
PORT = 1234
PACKET_SIZE = 28 
MEASUREMENT_COUNT = 12

# VARS
MAX_POINTS = 700_000 # downsampling will occur in visualisation software based on MAX_POINTS and VOXEL_SIZE
SCAN_STEP_DEG = 0.8 # has to be a multiple of 0.1deg(one step of a motor accounting for 1:2 and 1:9 reduction ratios on motor driver and gearbox respectively from 1.8deg base step of a stepper)
FULL_ROTATION_STEPS = round(360/SCAN_STEP_DEG) # DON'T CHANGE
PLATFORM_TILT_DEG = 64.


print(f"steps for full rotation: {FULL_ROTATION_STEPS}")

stop_event = threading.Event() # will stop at stop_event.wait() and will resume on stop_event.set() https://www.youtube.com/watch?v=Kae9aV9DO7k&list=PL7yh-TELLS1F3KytMVZRFO-xIo_S2_Jg1&index=5
point_queue = queue.Queue() # FIFO https://www.youtube.com/watch?v=6zmI_BU18xk
                            # will be used to communicate between receiver_thread and main thread (runs o3d)


def sendConfig(sock):
    config_msg = f"config {SCAN_STEP_DEG}\n".encode()
    sock.sendall(config_msg)

    ack = b""
    while b"\n" not in ack:
        ack += sock.recv(64)

    str_ack:str = ack.decode().strip() # intellisense

    if str_ack.startswith("config_error"):
        raise ValueError("SEND CONFIG ERROR:", str_ack)

    if not str_ack.startswith("config_response"): # not necessary unless the connection is really screwed
        raise ValueError("WEIRD CONFIG RESPONSE:", str_ack)
    
    motor_steps_per_scan = str_ack.split()[1]

    print(f"accepted pico config_response: {motor_steps_per_scan} steps")

def lidarTo3D(distance_mm:float, scan_angle_deg:float, azimuth_deg:float): # type hinting for Intellisense recognition
    r = distance_mm/1000. # mm -> m
    # scan_angle_rad = np.deg2rad(scan_angle_deg) # possible misalignment of holes on the platform/brass inserts might have not been inserted precisely
    scan_angle_rad = np.deg2rad(scan_angle_deg-1.0) # possible misalignment of holes on the platform/brass inserts might have not been inserted precisely
    tilt = np.deg2rad(PLATFORM_TILT_DEG)
    azimuth_rad = np.deg2rad(azimuth_deg)

    # lidar local 2d plane
    x = r*np.cos(scan_angle_rad)
    y = r*np.sin(scan_angle_rad)
    # z = r*np.sin(0) # possible error in lidar's internal structure
    z = r*np.sin(np.deg2rad(1.5)) # possible error in lidar's internal structure

    # tilt around x axis
    x_t = x
    y_t = y * np.cos(tilt) - z * np.sin(tilt)
    z_t = y * np.sin(tilt) + z * np.cos(tilt)

    # azimuth rotation around z axis
    x_a = x_t * np.cos(azimuth_rad) - y_t * np.sin(azimuth_rad)
    y_a = x_t * np.sin(azimuth_rad) + y_t * np.cos(azimuth_rad)
    z_a = -z_t # scene was mirrored; the sign fixes it

    return [x_a,y_a,z_a]


def parseStream(data: bytes, azimuth_deg:float): # type hinting for Intellisense recognition
    points = []
    i = 0
    n = len(data)

    while i + PACKET_SIZE <= n:

        packet = data[i:i+PACKET_SIZE]

        # extracting angles
        start_angle = struct.unpack_from("<H", packet, 0)[0] / 100.0 # < means little endian, > would have been big endian, h/H is signed/unsigned short (hex)
                                                                     # returns a tuple containing values unpacked according to the format string
                                                                     # we're extracting the value from 1-element tuple
        stop_angle  = struct.unpack_from("<H", packet, 26)[0] / 100.0

        # solving wrap-around of an angle. Using these values for trig functions won't make any difference
        if stop_angle < start_angle:
            stop_angle += 360.0

        for j in range(MEASUREMENT_COUNT):
            distance_mm = struct.unpack_from("<H", packet, 2 + 2*j)[0]  # mm

            if distance_mm == 0: # lots of trailing zeros found in the lidar stream. See notes.txt for the example of the output stream
                continue

            if distance_mm < 300: # clutter close to lidar, added 16.5.
                continue

            scan_angle = start_angle + (stop_angle - start_angle) * (j / (MEASUREMENT_COUNT - 1)) # in deg

            points.append(lidarTo3D(distance_mm, scan_angle, azimuth_deg))

        i += PACKET_SIZE
    if points:
        return np.array(points)
    return np.empty((0,3))


def receiver_thread(sock):
    receive_buffer = bytearray() # mutable

    for step_counter in range(FULL_ROTATION_STEPS):
        if stop_event.is_set():
            break
        
        azimuth_deg = step_counter*(SCAN_STEP_DEG)

        try:
            sock.sendall(b"r")

            while not stop_event.is_set():
                try:
                    chunk = sock.recv(4096)

                    if not chunk: # will be fulfilled only in the case of pico closing the socket; either this or s.settimeout() will handle this case
                        stop_event.set()
                        return

                    done_index = chunk.find(b"done") # find DONE

                    if done_index != -1: # find() returns -1 if a string/byte sequence wasn't found
                        receive_buffer.extend(chunk[:done_index]) # extracting everything up to DONE, the rest is thrown away
                        break
                    else:
                        receive_buffer.extend(chunk) # extracting everything; DONE hasn't arrived yet
                except socket.timeout:
                    print("socket timeout in receiver_thread") # usually recovers from it after some time
                    pass
            
            if stop_event.is_set():
                return
            
            points = parseStream(receive_buffer, azimuth_deg) # leftover is an incomplete packet; will be completed at the next call of sock.recv()
            receive_buffer = bytearray() # resetting receive_buffer for the next platform position

            if len(points) > 0:
                point_queue.put(points)

            print(f"Step: {step_counter+1}/{FULL_ROTATION_STEPS} | Azimuth: {azimuth_deg:.1f}") # azimuth for debug
        except Exception as e:
            print(f"receiver_thread problem: {e}") # one time caught [Errno 65] No route to host mid-scan
            stop_event.set()
            return
    stop_event.set()



def downsampleNumpy(np_points, len_points_vis):
    voxel_size_vis = len_points_vis / 10_000_000 / 7 + 0.01 # in m; https://www.open3d.org/docs/release/tutorial/geometry/pointcloud.html#Voxel-downsampling
    temp = o3d.geometry.PointCloud()
    temp.points = o3d.utility.Vector3dVector(np_points)
    temp = temp.voxel_down_sample(voxel_size = voxel_size_vis)
    return np.asarray(temp.points)

# connecting to pico
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((PICO_IP, PORT))
sock.settimeout(None) # no timeout during config
sendConfig(sock)

sock.settimeout(0.1)
print("connected to pico!")

thread = threading.Thread(target = receiver_thread, args = (sock,), daemon = True)  # program runs till at least one thread is online
                                                                                    # setting "daemon=True" will ignore the existence of this thread when counting up the # of active threads
                                                                                    # just in case if thread won't be joined in 'finally'
thread.start()

# o3d setup in main thread
pcd_vis = o3d.geometry.PointCloud()
vis = o3d.visualization.Visualizer() # Non-blocking visualisation https://www.open3d.org/docs/release/tutorial/visualization/non_blocking_visualization.html
vis.create_window("LiDAR Point Cloud")
pcd_added = False
points_export = np.empty((0,3)) # dtype = np.float64 by default, (1,3) would be filled with garbage values; this way we're just declaring an array
points_vis = np.empty((0,3)) # dtype = np.float64 by default, (1,3) would be filled with garbage values; this way we're just declaring an array

try:
    while not stop_event.is_set():
        new_batches = [] # container for lists of 3-tuples

        while not point_queue.empty():
            new_batches.append(point_queue.get())

        if new_batches:
            new_points = np.vstack(new_batches) # stacking all lists of 3-tuples into one list of 3-tuples
            points_export = np.vstack((points_export, new_points))
            points_vis = np.vstack((points_vis, new_points))

            len_points_vis = len(points_vis)
            if len_points_vis > MAX_POINTS:
                points_vis = downsampleNumpy(points_vis, len_points_vis)
            
            pcd_vis.points = o3d.utility.Vector3dVector(points_vis)

            if not pcd_added:
                vis.add_geometry(pcd_vis)
                pcd_added = True
            else:
                vis.update_geometry(pcd_vis)
        vis.poll_events()
        vis.update_renderer()

        time.sleep(0.01)
except KeyboardInterrupt as e:
    print(f"Stopping: {e}")
    stop_event.set()
finally:
    thread.join(timeout=1.0)
    if thread.is_alive():
        print("receiver_thread IS STUCK AND WAS NOT STOPPED CORRECTLY")

    try:
        sock.settimeout(2.0)
        sock.sendall(b"stop")

        response = b""
        while b"\n" not in response:
            response += sock.recv(64)
        
        str_response:str = response.decode().strip()
        print("pico", str_response)
    except Exception as e:
        print("EXCEPTION IN FINALLY",e)



    len_export_points = len(points_export)
    timestamp = datetime.now().strftime("%Y.%m.%d_%H:%M:%S")
    filename = f"pcd_{timestamp}_{len_export_points}.ply"

    pcd_export = o3d.geometry.PointCloud()
    pcd_export.points = o3d.utility.Vector3dVector(points_export)
    o3d.io.write_point_cloud(filename, pcd_export) # https://www.open3d.org/docs/release/tutorial/geometry/file_io.html

    vis.destroy_window()
    sock.close()
    print(f"Finished, total points: {len(points_export)}")
