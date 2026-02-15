from machine import Pin, UART
import time
import sys

led = Pin("LED", Pin.OUT)

uart = UART(0, baudrate=230400, tx=Pin(0), rx=Pin(1), bits=8, parity=None, stop=1, timeout=10)

time.sleep_ms(1000)
print("USB ↔ UART bridge started @ 230400 baud (Pico 2 W)")

while True:
    try:
        led.on()
        # print("CUSTOM CODE IS RUNNING!")  # comment this out later if spam causes issues
        time.sleep_ms(1) # this delay changes the pitch of the noise produced by Pico, at 1ms it is more high-pitched thus less annnoying

        if uart.any():
            data = uart.read(200)
            if data:
                sys.stdout.buffer.write(data)

        # Bidirectional part if enabled...
        # while True:
        #     ch = sys.stdin.buffer.read(1)
        #     if not ch: break
        #     uart.write(ch)

        time.sleep_ms(1)

    except KeyboardInterrupt:
        # print("KeyboardInterrupt caught - continuing anyway...")
        # Optionally: led.off() or cleanup here
        # But do NOT break/return — just continue the loop
        continue

    except Exception as e: # catch-all for unexpected errors, without it the program crashes!!!
        # print("Unexpected error:", e)
        time.sleep(1)  # prevent spam if error loops
