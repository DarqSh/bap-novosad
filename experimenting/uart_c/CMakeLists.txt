cmake_minimum_required(VERSION 3.13)

# initialize the SDK based on PICO_SDK_PATH
include(pico_sdk_import.cmake)

project(lidar_usb_forwarder C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

pico_sdk_init()

add_executable(lidar_forwarder
    uart.c
)

# enable stdio over USB + disable UART stdio (clean raw binary forwarding)
pico_enable_stdio_usb(lidar_forwarder 1)   # USB CDC = ON
pico_enable_stdio_uart(lidar_forwarder 0)  # UART stdio = OFF  ← very important!

# Add required libraries
target_link_libraries(lidar_forwarder
    pico_stdlib
    hardware_uart
)

# create map/bin/hex/uf2 output etc.
pico_add_extra_outputs(lidar_forwarder)


