
#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/uart.h"

#define UART_ID         uart0
#define BAUD_RATE       230400
#define UART_TX_PIN     0
#define UART_RX_PIN     1
#define READ_CHUNK_SIZE 200

int main() {
    stdio_usb_init();
    sleep_ms(500);

    uart_init(UART_ID, BAUD_RATE);
    gpio_set_function(UART_TX_PIN, GPIO_FUNC_UART);
    gpio_set_function(UART_RX_PIN, GPIO_FUNC_UART);
    uart_set_hw_flow(UART_ID, false, false);
    uart_set_format(UART_ID, 8, 1, UART_PARITY_NONE);

    while (true) {
        if (uart_is_readable(UART_ID)) {
            uint8_t buf[READ_CHUNK_SIZE];
            uint len = 0;

            while (len < READ_CHUNK_SIZE && uart_is_readable(UART_ID)) {
                buf[len++] = uart_getc(UART_ID);
            }

            if (len > 0) {
                for (uint i = 0; i < len; i++) {
                    putchar_raw(buf[i]);
                }
            }
        }

        sleep_ms(1);

        // Bidirectional optional:
        // int ch;
        // while ((ch = getchar_timeout_us(0)) != PICO_ERROR_TIMEOUT) {
        //     uart_putc(UART_ID, (uint8_t)ch);
        // }
    }

    return 0;
}