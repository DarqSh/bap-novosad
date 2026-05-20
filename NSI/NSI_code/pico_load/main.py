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

import machine # machine.reset()
from machine import UART, Pin, ADC
import network # controls wifi hardware
import socket # standard TCP/IP communication
import time
from stepper import Stepper
import secrets
import gc


# !!! CONSTANTS !!!
UART_ID = 0 # pico also has UART1, but the Tx of lidar is soldered to UART0_RX
BAUD = 230400 # lidar transmission rate

# VARS
GATHERING_TIME = 200 # in ms, 1000ms is too much and garbage collector cannot free up space that fast
MOTOR_STEPS_PER_SCAN = 0 # will be redefined with receive_config()

motor = Stepper(14,15, steps_per_rev=3600, speed_sps=400) # steps_per_rev = 360deg/0.1deg; play with speed_sps later to find the appropriate speed to not skip any step
motor.stop() # not sure if needed

hall_input = Pin(26, Pin.IN, Pin.PULL_DOWN)

uart = UART(UART_ID, baudrate=BAUD, tx=Pin(0), rx=Pin(1)) 
uart_buffer = bytearray()
read_buffer = bytearray(256)
send_data = bytearray(28) # 2B start angle + 2B*MEASUREMENT_LENGTH + 2B stop angle

def receive_config(client):
    global MOTOR_STEPS_PER_SCAN
    config = bytearray()

    while b"\n" not in config:
        config += client.recv(16)
    
    index = config.find(b"\n")
    str_config:str = config[:index].decode().strip()

    parts = str_config.split()

    if len(parts)!=2:
        client.sendall(b"config_error invalid_format\n")
        raise ValueError("RECEIVE CONFIG ERROR")

    
    MOTOR_STEPS_PER_SCAN = round(float(parts[1])/0.1)
    response = f"config_response {MOTOR_STEPS_PER_SCAN}\n"
    client.sendall(response.encode())


def parse_and_send(buffer, client, send_data): # will be sending back only Start angle, Stop angle, Data Measurements
    # print("inside parse_and_send")
    i = 0 # index will be traversing the buffer that was filled with lidar data.
    buffer_length = len(buffer)

    while i+47 <= buffer_length: # 47 is the packet size, see above

        if buffer[i] != 0x54: # checking for beginning of a packet
            i+=1
            continue

        if buffer[i+1] != 0x2C: # double checking if this is actually a header, something else might have a value of 0x54
            i+=1
            continue

        # little-endianness will be solved at pc side
        
        # start angle
        send_data[0] = buffer[i+4] # tried extracting a good packet first, but it would lead to further allocation of memory and making OUT_OF_MEMORY scenario more probable. Rewriting the code to traversing using an index helps with it
        send_data[1] = buffer[i+5]

        send_data_index = 2
        for j in range(12):     # Data Measurements
                                # distance values, no need for confidence  
            lidar_packet_index = i+(6+3*j)
            send_data[send_data_index] = buffer[lidar_packet_index]
            send_data[send_data_index+1] = buffer[lidar_packet_index+1]
            send_data_index += 2

        # stop angle
        send_data[26] = buffer[i+42]
        send_data[27] = buffer[i+43]

        try:
            client.sendall(send_data) # calls send repeatedly dir(socket.socket.sendall)
        except Exception as e:
            print("Send error:", e)
            raise

        i += 47 # 47 is the packet size, see above
    
    # if i>0: # removing processed byes
    #     del buffer[:i]
    #
    # the above won't work, Micropython doesn't support item deletion
    #   main loop error: 'bytearray' object doesn't support item deletion

    return i

def new_position():
    current_steps_done = motor.steps_done
    motor.free_run(1)
    while True:
        if(motor.steps_done - current_steps_done >= MOTOR_STEPS_PER_SCAN):
            motor.stop() # CRUCIAL !!! after completing the program, automatic de-initialization of the timer isn't the #1 priority, and thus a few more steps are made at the end at high speeds. Learned it the hard way.
            break
    return

def homing():
    motor.free_run(-1)
    while (hall_input.value() == 1): # going outside of default position
        pass
    while motor.steps_done < 200: # going a bit more outside of default position
        pass

    while (hall_input.value() == 0):
        pass
    motor.stop()
    return

ap = network.WLAN(network.AP_IF) # setting up AP
ap.active(True)
ap.config(essid=secrets.secret_ssid, password=secrets.secret_pw)
print("Wifi configured")
# print("IP:", ap.ifconfig()[0])

# jednoduchy web server https://cw.fel.cvut.cz/wiki/_media/courses/b0b37nsi/lectures/nsi-lec04-2026.pdf
addr = socket.getaddrinfo('0.0.0.0', 1234)[0][-1] # 0.0.0.0 -> listen on all interfaces, 1234 -- port number
# try:
#     s.close() # socket from the previous run might not have been cleaned properly and doesn't allow the creation of a new one -- this try except will close it
# except:
#     pass
s = socket.socket()
s.bind(addr) # attaches socket to 0.0.0.0:1234
s.listen(1) # Enable a server to accept connections. The argument is a number of unaccepted connections that the system will allow before refusing new connections. dir(socket.socket.listen)
cl, addr = s.accept() # Wait for an incoming connection.  Return a new socket representing the connection, and the address of the client. dir(socket.socket.accept)
cl.settimeout(None) # set a timeout on socket operations (so that it is non-blocking)
receive_config(cl)
print(f"motor steps:{MOTOR_STEPS_PER_SCAN}")
cl.settimeout(0.1) # set a timeout on socket operations (so that it is non-blocking)
homing()
while True: # main loop
    # print("inside the loop")
    try:
        # wait for trigger from PC
        try:
            cmd = cl.recv(16) # 16 is the "up to" amount that is possible to receive
        except:
            cmd = None

        if cmd == b"r":
            # print("Trigger received")
            start = time.ticks_ms()

            while time.ticks_diff(time.ticks_ms(), start) < GATHERING_TIME: # collecting data for a fixed period of time
                read_buffer_end_index = uart.readinto(read_buffer)
                # print("trying to read data")
                if read_buffer_end_index:
                    # print("data was read")
                    # print(data.hex())
                    uart_buffer.extend(read_buffer[:read_buffer_end_index])

                    last_packet_index = parse_and_send(uart_buffer,cl,send_data)

                    if last_packet_index:
                        uart_buffer = bytearray(uart_buffer[last_packet_index:]) # next uart.read() will complete the last packet
            
            cl.sendall(b"done") # acts as a synchronisation end marker. Otherwise this output may be observed when pc isn't fast enough to process the data:
                                #   >>> 
                                #   motor steps:9
                                #   Send error: [Errno 104] ECONNRESET
                                #   main loop error: [Errno 104] ECONNRESET
            new_position()
            gc.collect()
        elif cmd == b"stop":
            motor.stop()
            cl.sendall(b"restarting\n")
            time.sleep_ms(100) #time for cl.sendall()

            cl.close()
            s.close()

            machine.reset() # start the code again
    except Exception as e:
        print("main loop error:", e)
        break
