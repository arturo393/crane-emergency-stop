#pragma once

/**
 * @file hardware_config.h
 * @brief Centralized hardware pinout definitions for the EdgeBox-Lite.
 *
 * This file maps the functional names of peripherals to the specific GPIO
 * pins of the ESP32-S3 as documented in the EdgeBox-Lite User Manual v1.0.
 *
 * @version 1.0
 * @date 2025-11-01
 */

// =================================================================
// EdgeBox-Lite Hardware Pinout (Based on Manual v1.0)
// =================================================================

// --- CAN Bus ---
// Connected to the internal CAN transceiver
#define PIN_CAN_TX 1
#define PIN_CAN_RX 2

// --- Ethernet (W5500 via SPI) ---
// The W5500 chip is connected via the SPI2_HOST
#define PIN_ETH_SPI_MOSI 12 // Master Out, Slave In (ESP32 -> W5500)
#define PIN_ETH_SPI_MISO 11 // Master In, Slave Out (W5500 -> ESP32)
#define PIN_ETH_SPI_SCLK 13 // Serial Clock
#define PIN_ETH_CS       10 // Chip Select
#define PIN_ETH_INT      14 // Interrupt
#define PIN_ETH_RST      15 // Reset

// --- Digital Inputs (DI) ---
#define PIN_DI_0 4
#define PIN_DI_1 5
#define PIN_DI_2 6
#define PIN_DI_3 7

// --- Digital Outputs (DO) ---
#define PIN_DO_0 40
#define PIN_DO_1 39
#define PIN_DO_2 38
#define PIN_DO_3 37
#define PIN_DO_4 36
#define PIN_DO_5 35

// --- Analog Inputs (AI) ---
// Connected to ADS1115 ADC (I2C Address 0x48)
// Note: Pin numbers for AI are ADC channels, not direct GPIOs.
// The actual GPIOs are connected to the ADC chip.

// --- Analog Outputs (AO) ---
// Implemented via PWM + Low-Pass Filter
#define PIN_AO_0 42
#define PIN_AO_1 41

// --- RS485 ---
#define PIN_RS485_TX 17
#define PIN_RS485_RX 18
#define PIN_RS485_RTS 8 // Direction control

// --- 4G/LTE Modem ---
#define PIN_LTE_TX 48
#define PIN_LTE_RX 47
#define PIN_LTE_PWR_KEY 21
#define PIN_LTE_PWR_EN 16

// --- I2C Bus ---
#define PIN_I2C_SDA 20 // Corrected from manual's IO18 which conflicts with RS485
#define PIN_I2C_SCL 19

// --- Debug UART (UART0) ---
#define PIN_UART_TX 3  // Also multiplexed with ACT LED
#define PIN_UART_RX 46 // Also multiplexed with ERR LED

// --- Other Peripherals ---
#define PIN_RESET_BUTTON 0
#define PIN_BEEP 45
#define PIN_RTC_ALARM 9

// --- SD Card (SPI) ---
// SD card slot connected via SPI
// Note: Using different SPI bus than W5500 to avoid conflicts
#define PIN_SD_MOSI 33
#define PIN_SD_MISO 34
#define PIN_SD_CLK  35
#define PIN_SD_CS   36
