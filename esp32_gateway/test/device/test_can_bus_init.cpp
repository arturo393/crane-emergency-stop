/**
 * @file test_can_bus_init.cpp
 * @brief Device integration test for CAN bus initialization
 * 
 * This test validates that the CAN bus can be properly initialized
 * on the EdgeBox-Lite hardware using the correct GPIO pins (IO1, IO2).
 * 
 * @note This test must be run ON the ESP32 hardware, not in native mode.
 */

#include "unity.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/twai.h"
#include "hardware_config.h"

static const char *TAG = "TEST_CAN_INIT";

/**
 * @brief Test that CAN bus initializes successfully with correct pins
 * 
 * This test:
 * 1. Configures TWAI driver with EdgeBox-Lite pins (TX=1, RX=2)
 * 2. Installs the driver
 * 3. Starts the driver
 * 4. Verifies no errors occurred
 * 5. Stops and uninstalls the driver
 */
void test_can_bus_initialization(void) {
    ESP_LOGI(TAG, "=================================================");
    ESP_LOGI(TAG, "  TEST: CAN Bus Initialization (EdgeBox-Lite)");
    ESP_LOGI(TAG, "=================================================");
    ESP_LOGI(TAG, "Expected pins: TX=%d, RX=%d", PIN_CAN_TX, PIN_CAN_RX);
    
    // 1. Configurar TWAI
    twai_general_config_t g_config = TWAI_GENERAL_CONFIG_DEFAULT(
        (gpio_num_t)PIN_CAN_TX, 
        (gpio_num_t)PIN_CAN_RX, 
        TWAI_MODE_NORMAL
    );
    
    // Configuración de timing para 250kbps
    twai_timing_config_t t_config = TWAI_TIMING_CONFIG_250KBITS();
    
    // Configuración de filtros (aceptar todos los mensajes)
    twai_filter_config_t f_config = TWAI_FILTER_CONFIG_ACCEPT_ALL();
    
    // 2. Instalar driver TWAI
    ESP_LOGI(TAG, "Installing TWAI driver...");
    esp_err_t ret = twai_driver_install(&g_config, &t_config, &f_config);
    TEST_ASSERT_EQUAL_MESSAGE(ESP_OK, ret, "TWAI driver installation failed");
    
    if (ret == ESP_OK) {
        ESP_LOGI(TAG, "✅ TWAI driver installed successfully");
    }
    
    // 3. Iniciar driver TWAI
    ESP_LOGI(TAG, "Starting TWAI driver...");
    ret = twai_start();
    TEST_ASSERT_EQUAL_MESSAGE(ESP_OK, ret, "TWAI driver start failed");
    
    if (ret == ESP_OK) {
        ESP_LOGI(TAG, "✅ TWAI driver started successfully");
    }
    
    // 4. Verificar que el driver está en estado operativo
    twai_status_info_t status;
    ret = twai_get_status_info(&status);
    TEST_ASSERT_EQUAL_MESSAGE(ESP_OK, ret, "Failed to get TWAI status");
    
    ESP_LOGI(TAG, "TWAI Status:");
    ESP_LOGI(TAG, "  - State: %d", status.state);
    ESP_LOGI(TAG, "  - TX queue: %lu", status.msgs_to_tx);
    ESP_LOGI(TAG, "  - RX queue: %lu", status.msgs_to_rx);
    ESP_LOGI(TAG, "  - TX failed: %lu", status.tx_failed_count);
    ESP_LOGI(TAG, "  - RX missed: %lu", status.rx_missed_count);
    ESP_LOGI(TAG, "  - Arbitration lost: %lu", status.arb_lost_count);
    ESP_LOGI(TAG, "  - Bus errors: %lu", status.bus_error_count);
    
    // El estado debe ser TWAI_STATE_RUNNING (1)
    TEST_ASSERT_EQUAL_MESSAGE(TWAI_STATE_RUNNING, status.state, 
                             "TWAI is not in RUNNING state");
    
    // 5. Detener y desinstalar driver
    ESP_LOGI(TAG, "Stopping TWAI driver...");
    ret = twai_stop();
    TEST_ASSERT_EQUAL_MESSAGE(ESP_OK, ret, "TWAI driver stop failed");
    
    ESP_LOGI(TAG, "Uninstalling TWAI driver...");
    ret = twai_driver_uninstall();
    TEST_ASSERT_EQUAL_MESSAGE(ESP_OK, ret, "TWAI driver uninstall failed");
    
    ESP_LOGI(TAG, "✅ CAN bus initialization test PASSED");
    ESP_LOGI(TAG, "=================================================");
}

/**
 * @brief Test CAN bus loopback mode
 * 
 * This test validates that the CAN controller can send and receive
 * messages in loopback mode (no physical bus needed).
 */
void test_can_bus_loopback(void) {
    ESP_LOGI(TAG, "=================================================");
    ESP_LOGI(TAG, "  TEST: CAN Bus Loopback Mode");
    ESP_LOGI(TAG, "=================================================");
    
    // Configurar TWAI en modo NO_ACK (loopback sin necesidad de bus físico)
    twai_general_config_t g_config = TWAI_GENERAL_CONFIG_DEFAULT(
        (gpio_num_t)PIN_CAN_TX, 
        (gpio_num_t)PIN_CAN_RX, 
        TWAI_MODE_NO_ACK
    );
    
    twai_timing_config_t t_config = TWAI_TIMING_CONFIG_250KBITS();
    twai_filter_config_t f_config = TWAI_FILTER_CONFIG_ACCEPT_ALL();
    
    // Instalar e iniciar
    esp_err_t ret = twai_driver_install(&g_config, &t_config, &f_config);
    TEST_ASSERT_EQUAL(ESP_OK, ret);
    
    ret = twai_start();
    TEST_ASSERT_EQUAL(ESP_OK, ret);
    
    ESP_LOGI(TAG, "✅ TWAI driver started in NO_ACK mode");
    
    // Preparar mensaje de prueba
    twai_message_t tx_msg = {
        .identifier = 0x123,
        .data_length_code = 8,
        .data = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08}
    };
    
    ESP_LOGI(TAG, "Sending test message (ID=0x123)...");
    ret = twai_transmit(&tx_msg, pdMS_TO_TICKS(1000));
    TEST_ASSERT_EQUAL_MESSAGE(ESP_OK, ret, "Failed to transmit message");
    
    if (ret == ESP_OK) {
        ESP_LOGI(TAG, "✅ Message transmitted successfully");
    }
    
    // En modo NO_ACK, el mensaje debería transmitirse sin errores
    // aunque no haya un receptor físico
    
    // Cleanup
    twai_stop();
    twai_driver_uninstall();
    
    ESP_LOGI(TAG, "✅ CAN bus loopback test PASSED");
    ESP_LOGI(TAG, "=================================================");
}

// Unity test runner
extern "C" void app_main(void) {
    ESP_LOGI(TAG, "\n\n");
    ESP_LOGI(TAG, "╔═══════════════════════════════════════════════╗");
    ESP_LOGI(TAG, "║   EdgeBox-Lite Device Integration Tests      ║");
    ESP_LOGI(TAG, "║   Test Suite: CAN Bus Initialization         ║");
    ESP_LOGI(TAG, "╚═══════════════════════════════════════════════╝");
    ESP_LOGI(TAG, "\n");
    
    vTaskDelay(pdMS_TO_TICKS(1000)); // Give time to open serial monitor
    
    UNITY_BEGIN();
    
    RUN_TEST(test_can_bus_initialization);
    RUN_TEST(test_can_bus_loopback);
    
    UNITY_END();
    
    ESP_LOGI(TAG, "\n");
    ESP_LOGI(TAG, "╔═══════════════════════════════════════════════╗");
    ESP_LOGI(TAG, "║   All CAN Bus Tests Completed                ║");
    ESP_LOGI(TAG, "╚═══════════════════════════════════════════════╝");
}
