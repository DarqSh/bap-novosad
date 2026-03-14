import network
import socket
from machine import Pin, UART
import time

# LiDAR UART setup
uart = UART(0, baudrate=230400, tx=Pin(0), rx=Pin(1))

# Wi-Fi Access Point
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid="henlo", password="there12345")
print("AP started, IP:", ap.ifconfig()[0])

# TCP server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 9000))
server.listen(1)

while True:
    print("Waiting for client...")
    client, addr = server.accept()
    print("Client connected:", addr)
    client.setblocking(False)

    try:
        while True:
            # send all available UART data
            if uart.any():
                data = uart.read()
                if data:
                    try:
                        client.send(data)
                    except OSError:
                        # client disconnected
                        break
            time.sleep_ms(1)
    except Exception as e:
        print("Client disconnected or error:", e)
    finally:
        client.close()
        print("Client socket closed, waiting for new connection")