#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import socket
from enum import Enum
import struct
import time

# ----------------------------------------------------------------------
# Network settings
# ----------------------------------------------------------------------

PICO_IP = "192.168.4.1"
PORT = 9000

# ----------------------------------------------------------------------
# System Constants
# ----------------------------------------------------------------------

MEASUREMENTS_PER_PLOT = 480
PLOT_MAX_RANGE = 4.0
PLOT_AUTO_RANGE = False
PLOT_CONFIDENCE = True
PLOT_CONFIDENCE_COLOUR_MAP = "bwr_r"
PRINT_DEBUG = False

# ----------------------------------------------------------------------
# Packet format constants
# ----------------------------------------------------------------------

PACKET_LENGTH = 47
MEASUREMENT_LENGTH = 12 
MESSAGE_FORMAT = "<xBHH" + "HB" * MEASUREMENT_LENGTH + "HHB"

State = Enum("State", ["SYNC0", "SYNC1", "SYNC2", "LOCKED", "UPDATE_PLOT"])

# ----------------------------------------------------------------------
# TCP helper
# ----------------------------------------------------------------------

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Connecting to Pico...")
sock.connect((PICO_IP, PORT))
print("Connected")

def read_bytes(n):
    data = b''
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise RuntimeError("Connection closed")
        data += chunk
    return data

# ----------------------------------------------------------------------
# LiDAR parsing
# ----------------------------------------------------------------------

def parse_lidar_data(data):
    length, speed, start_angle, *pos_data, stop_angle, timestamp, crc = \
        struct.unpack(MESSAGE_FORMAT, data)

    start_angle = float(start_angle) / 100.0
    stop_angle = float(stop_angle) / 100.0

    if stop_angle < start_angle:
        stop_angle += 360.0

    step_size = (stop_angle - start_angle) / (MEASUREMENT_LENGTH - 1)

    angle = [start_angle + step_size * i for i in range(MEASUREMENT_LENGTH)]
    distance = pos_data[0::2]
    confidence = pos_data[1::2]

    return list(zip(angle, distance, confidence))


def get_xyc_data(measurements):
    angle = np.array([m[0] for m in measurements])
    distance = np.array([m[1] for m in measurements])
    confidence = np.array([m[2] for m in measurements])

    x = np.sin(np.radians(angle)) * (distance / 1000.0)
    y = np.cos(np.radians(angle)) * (distance / 1000.0)

    return x, y, confidence


running = True

def on_plot_close(event):
    global running
    running = False

# ----------------------------------------------------------------------
# Plot setup
# ----------------------------------------------------------------------

plt.ion()
plt.rcParams['figure.figsize'] = [10, 10]
plt.rcParams['lines.markersize'] = 2.0

if PLOT_CONFIDENCE:
    graph = plt.scatter([], [], c=[], marker=".", vmin=0,
                        vmax=255, cmap=PLOT_CONFIDENCE_COLOUR_MAP)
else:
    graph = plt.plot([], [], ".")[0]

graph.figure.canvas.mpl_connect('close_event', on_plot_close)

plt.xlim(-PLOT_MAX_RANGE, PLOT_MAX_RANGE)
plt.ylim(-PLOT_MAX_RANGE, PLOT_MAX_RANGE)

# ----------------------------------------------------------------------
# Main state machine
# ----------------------------------------------------------------------

measurements = []
data = b''
state = State.SYNC0
counter = 0 # testing
while running: 
    time.sleep(0.03)
    counter = counter + 1 # testing
    print(counter) # testing
    if state == State.SYNC0:
        data = b''
        measurements = []
        print("zero") # testing
        if read_bytes(1) == b'\x54':
            data = b'\x54'
            state = State.SYNC1

    elif state == State.SYNC1:
        print("one") # testing
        if read_bytes(1) == b'\x2C':
            state = State.SYNC2
            data += b'\x2C'
        else:
            state = State.SYNC0

    elif state == State.SYNC2:
        print("two") # testing
        data += read_bytes(PACKET_LENGTH - 2)

        if len(data) != PACKET_LENGTH:
            state = State.SYNC0
            continue

        measurements += parse_lidar_data(data)
        state = State.LOCKED

    elif state == State.LOCKED:
        print("Lock") # testing
        data = read_bytes(PACKET_LENGTH)

        if data[0] != 0x54 or len(data) != PACKET_LENGTH:
            print("WARNING: Serial sync lost")
            state = State.SYNC0
            continue

        measurements += parse_lidar_data(data)

        if len(measurements) > MEASUREMENTS_PER_PLOT:
            state = State.UPDATE_PLOT

    elif state == State.UPDATE_PLOT:
        print("Update") # testing
        x, y, c = get_xyc_data(measurements)

        if PLOT_AUTO_RANGE:
            mav_val = max([max(abs(x)), max(abs(y))]) * 1.2
            plt.xlim(-mav_val, mav_val)
            plt.ylim(-mav_val, mav_val)

        graph.remove()

        if PLOT_CONFIDENCE:
            graph = plt.scatter(x, y, c=c, marker=".",
                                vmin=0, vmax=255,
                                cmap=PLOT_CONFIDENCE_COLOUR_MAP)
        else:
            graph = plt.plot(x, y, 'b.')[0]

        # plt.pause(0.00001)
        plt.pause(0.01)
        state = State.LOCKED
        # print(measurements) # testing
        print("i", counter) # testing
        measurements = []