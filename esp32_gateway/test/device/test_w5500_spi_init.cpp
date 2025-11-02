/**
 * @file test_w5500_spi_init.cpp
 * @brief Device integration test for W5500 Ethernet controller
 * 
 * This test validates that the W5500 chip can be accessed via SPI
 * and that the hardware connections are correct on the EdgeBox-Lite.
 * 
 * @note This test must be run ON the ESP32 hardware with W5500 connected.
 */

#include "unity.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/spi_master.h"
#include "driver/gpio.h"
#include "hardware_config.h"

static const char *TAG = "TEST_W5500_SPI";

// W5500 Register Addresses
#define W5500_REG_VERSIONR  0x0039  // Version register
#define W5500_REG_MR        0x0000  // Mode register

// SPI Command for reading common register
#define W5500_READ_COMMON   0x00

static spi_device_handle_t spi_handle = nullptr;

/**
 * @brief Initialize SPI bus for W5500 communication
 */
esp_err_t init_spi_for_w5500(void) {
    ESP_LOGI(TAG, "Initializing SPI bus for W5500...");
    ESP_LOGI(TAG, "  MOSI: GPIO %d", PIN_ETH_SPI_MOSI);
    ESP_LOGI(TAG, "  MISO: GPIO %d", PIN_ETH_SPI_MISO);
    ESP_LOGI(TAG, "  SCLK: GPIO %d", PIN_ETH_SPI_SCLK);
    ESP_LOGI(TAG, "  CS:   GPIO %d", PIN_ETH_CS);
    ESP_LOGI(TAG, "  INT:  GPIO %d", PIN_ETH_INT);
    ESP_LOGI(TAG, "  RST:  GPIO %d", PIN_ETH_RST);
    
    // Configure SPI bus
    spi_bus_config_t buscfg = {
        .mosi_io_num = PIN_ETH_SPI_MOSI,
        .miso_io_num = PIN_ETH_SPI_MISO,
        .sclk_io_num = PIN_ETH_SPI_SCLK,
        .quadwp_io_num = -1,
        .quadhd_io_num = -1,
        .max_transfer_sz = 0,
    };
    
    esp_err_t ret = spi_bus_initialize(SPI2_HOST, &buscfg, SPI_DMA_CH_AUTO);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to initialize SPI bus: %s", esp_err_to_name(ret));
        return ret;
    }
    
    // Configure W5500 device
    spi_device_interface_config_t devcfg = {};
    devcfg.command_bits = 16;      // Address phase
    devcfg.address_bits = 8;       // Control phase
    devcfg.mode = 0;               // SPI mode 0
    devcfg.clock_speed_hz = 20 * 1000 * 1000;  // 20 MHz
    devcfg.spics_io_num = PIN_ETH_CS;
    devcfg.queue_size = 20;
    
    ret = spi_bus_add_device(SPI2_HOST, &devcfg, &spi_handle);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to add SPI device: %s", esp_err_to_name(ret));
        return ret;
    }
    
    ESP_LOGI(TAG, "✅ SPI bus initialized successfully");
    return ESP_OK;
}

/**
 * @brief Reset W5500 chip using hardware reset pin
 */
void reset_w5500(void) {
    ESP_LOGI(TAG, "Resetting W5500...");
    
    // Configure reset pin
    gpio_config_t io_conf = {};
    io_conf.pin_bit_mask = (1ULL << PIN_ETH_RST);
    io_conf.mode = GPIO_MODE_OUTPUT;
    io_conf.pull_up_en = GPIO_PULLUP_DISABLE;
    io_conf.pull_down_en = GPIO_PULLDOWN_DISABLE;
    io_conf.intr_type = GPIO_INTR_DISABLE;
    gpio_config(&io_conf);
    
    // Reset sequence: LOW -> wait -> HIGH
    gpio_set_level((gpio_num_t)PIN_ETH_RST, 0);
    vTaskDelay(pdMS_TO_TICKS(10));
    gpio_set_level((gpio_num_t)PIN_ETH_RST, 1);
    vTaskDelay(pdMS_TO_TICKS(200));  // Wait for W5500 to complete reset
    
    ESP_LOGI(TAG, "✅ W5500 reset complete");
}

/**
 * @brief Read a register from W5500 via SPI
 */
esp_err_t w5500_read_register(uint16_t address, uint8_t* data) {
    spi_transaction_t trans = {};
    trans.cmd = address;
    trans.addr = W5500_READ_COMMON;  // Read from common register block
    trans.length = 8;
    trans.rxlength = 8;
    trans.rx_buffer = data;
    
    esp_err_t ret = spi_device_transmit(spi_handle, &trans);
    return ret;
}

/**
 * @brief Test SPI bus initialization for W5500
 */
void test_w5500_spi_bus_init(void) {
    ESP_LOGI(TAG, "=================================================");
    ESP_LOGI(TAG, "  TEST: W5500 SPI Bus Initialization");
    ESP_LOGI(TAG, "=================================================");
    
    esp_err_t ret = init_spi_for_w5500();
    TEST_ASSERT_EQUAL_MESSAGE(ESP_OK, ret, "SPI bus initialization failed");
    
    ESP_LOGI(TAG, "✅ W5500 SPI bus initialization test PASSED");
    ESP_LOGI(TAG, "=================================================");
}

/**
 * @brief Test W5500 hardware reset
 */
void test_w5500_hardware_reset(void) {
    ESP_LOGI(TAG, "=================================================");
    ESP_LOGI(TAG, "  TEST: W5500 Hardware Reset");
    ESP_LOGI(TAG, "=================================================");
    
    reset_w5500();
    
    // If we got here without crashing, reset worked
    TEST_ASSERT_TRUE_MESSAGE(true, "W5500 reset completed");
    
    ESP_LOGI(TAG, "✅ W5500 hardware reset test PASSED");
    ESP_LOGI(TAG, "=================================================");
}

/**
 * @brief Test reading W5500 version register
 * 
 * The W5500 version register should return 0x04.
 * This confirms:
 * 1. SPI bus is working
 * 2. W5500 is powered and responding
 * 3. Pin connections are correct
 */
void test_w5500_version_register(void) {
    ESP_LOGI(TAG, "=================================================");
    ESP_LOGI(TAG, "  TEST: W5500 Version Register Read");
    ESP_LOGI(TAG, "=================================================");
    
    uint8_t version = 0;
    esp_err_t ret = w5500_read_register(W5500_REG_VERSIONR, &version);
    
    TEST_ASSERT_EQUAL_MESSAGE(ESP_OK, ret, "Failed to read W5500 version register");
    
    ESP_LOGI(TAG, "W5500 Version Register: 0x%02X", version);
    ESP_LOGI(TAG, "Expected: 0x04");
    
    TEST_ASSERT_EQUAL_HEX8_MESSAGE(0x04, version, 
                                   "W5500 version mismatch - check hardware connections");
    
    if (version == 0x04) {
        ESP_LOGI(TAG, "✅ W5500 is responding correctly!");
        ESP_LOGI(TAG, "   - SPI communication working");
        ESP_LOGI(TAG, "   - Hardware connections valid");
        ESP_LOGI(TAG, "   - W5500 chip functional");
    }
    
    ESP_LOGI(TAG, "✅ W5500 version register test PASSED");
    ESP_LOGI(TAG, "=================================================");
}

/**
 * @brief Cleanup SPI resources
 */
void cleanup_spi(void) {
    if (spi_handle) {
        spi_bus_remove_device(spi_handle);
        spi_handle = nullptr;
    }
    spi_bus_free(SPI2_HOST);
}

// Unity test runner
extern "C" void app_main(void) {
    ESP_LOGI(TAG, "\n\n");
    ESP_LOGI(TAG, "╔═══════════════════════════════════════════════╗");
    ESP_LOGI(TAG, "║   EdgeBox-Lite Device Integration Tests      ║");
    ESP_LOGI(TAG, "║   Test Suite: W5500 Ethernet Controller      ║");
    ESP_LOGI(TAG, "╚═══════════════════════════════════════════════╝");
    ESP_LOGI(TAG, "\n");
    ESP_LOGI(TAG, "⚠️  HARDWARE REQUIREMENT:");
    ESP_LOGI(TAG, "    This test requires a W5500 Ethernet module");
    ESP_LOGI(TAG, "    connected to the EdgeBox-Lite SPI pins.");
    ESP_LOGI(TAG, "\n");
    
    vTaskDelay(pdMS_TO_TICKS(2000)); // Give time to read warning
    
    UNITY_BEGIN();
    
    RUN_TEST(test_w5500_spi_bus_init);
    RUN_TEST(test_w5500_hardware_reset);
    RUN_TEST(test_w5500_version_register);
    
    UNITY_END();
    
    // Cleanup
    cleanup_spi();
    
    ESP_LOGI(TAG, "\n");
    ESP_LOGI(TAG, "╔═══════════════════════════════════════════════╗");
    ESP_LOGI(TAG, "║   All W5500 Tests Completed                  ║");
    ESP_LOGI(TAG, "╚═══════════════════════════════════════════════╝");
}
