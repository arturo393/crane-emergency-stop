/**
 * @file test_digital_io.cpp
 * @brief Device integration test for digital I/O on EdgeBox-Lite
 * 
 * This test validates that digital inputs and outputs are correctly
 * configured and can be read/written according to the hardware manual.
 * 
 * @note This test requires manual wiring for loopback testing.
 */

#include "unity.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "hardware_config.h"

static const char *TAG = "TEST_DIGITAL_IO";

/**
 * @brief Test digital output configuration
 * 
 * Validates that all 6 digital outputs (DO0-DO5) can be configured
 * as GPIO outputs without errors.
 */
void test_digital_output_config(void) {
    ESP_LOGI(TAG, "=================================================");
    ESP_LOGI(TAG, "  TEST: Digital Output Configuration");
    ESP_LOGI(TAG, "=================================================");
    
    const int output_pins[] = {
        PIN_DO_0, PIN_DO_1, PIN_DO_2,
        PIN_DO_3, PIN_DO_4, PIN_DO_5
    };
    
    const char* pin_names[] = {
        "DO0", "DO1", "DO2", "DO3", "DO4", "DO5"
    };
    
    for (int i = 0; i < 6; i++) {
        ESP_LOGI(TAG, "Configuring %s (GPIO %d)...", pin_names[i], output_pins[i]);
        
        gpio_config_t io_conf = {};
        io_conf.pin_bit_mask = (1ULL << output_pins[i]);
        io_conf.mode = GPIO_MODE_OUTPUT;
        io_conf.pull_up_en = GPIO_PULLUP_DISABLE;
        io_conf.pull_down_en = GPIO_PULLDOWN_DISABLE;
        io_conf.intr_type = GPIO_INTR_DISABLE;
        
        esp_err_t ret = gpio_config(&io_conf);
        TEST_ASSERT_EQUAL_MESSAGE(ESP_OK, ret, "Failed to configure digital output");
        
        if (ret == ESP_OK) {
            ESP_LOGI(TAG, "  ✅ %s configured successfully", pin_names[i]);
        }
    }
    
    ESP_LOGI(TAG, "✅ All digital outputs configured");
    ESP_LOGI(TAG, "=================================================");
}

/**
 * @brief Test digital input configuration
 * 
 * Validates that all 4 digital inputs (DI0-DI3) can be configured
 * as GPIO inputs without errors.
 */
void test_digital_input_config(void) {
    ESP_LOGI(TAG, "=================================================");
    ESP_LOGI(TAG, "  TEST: Digital Input Configuration");
    ESP_LOGI(TAG, "=================================================");
    
    const int input_pins[] = {PIN_DI_0, PIN_DI_1, PIN_DI_2, PIN_DI_3};
    const char* pin_names[] = {"DI0", "DI1", "DI2", "DI3"};
    
    for (int i = 0; i < 4; i++) {
        ESP_LOGI(TAG, "Configuring %s (GPIO %d)...", pin_names[i], input_pins[i]);
        
        gpio_config_t io_conf = {};
        io_conf.pin_bit_mask = (1ULL << input_pins[i]);
        io_conf.mode = GPIO_MODE_INPUT;
        io_conf.pull_up_en = GPIO_PULLUP_ENABLE;  // Enable pull-up for stability
        io_conf.pull_down_en = GPIO_PULLDOWN_DISABLE;
        io_conf.intr_type = GPIO_INTR_DISABLE;
        
        esp_err_t ret = gpio_config(&io_conf);
        TEST_ASSERT_EQUAL_MESSAGE(ESP_OK, ret, "Failed to configure digital input");
        
        if (ret == ESP_OK) {
            ESP_LOGI(TAG, "  ✅ %s configured successfully", pin_names[i]);
        }
    }
    
    ESP_LOGI(TAG, "✅ All digital inputs configured");
    ESP_LOGI(TAG, "=================================================");
}

/**
 * @brief Test digital output toggle
 * 
 * Cycles through all outputs, setting them HIGH then LOW,
 * which can be visually verified with an LED or multimeter.
 */
void test_digital_output_toggle(void) {
    ESP_LOGI(TAG, "=================================================");
    ESP_LOGI(TAG, "  TEST: Digital Output Toggle");
    ESP_LOGI(TAG, "=================================================");
    ESP_LOGI(TAG, "💡 TIP: Connect LEDs to outputs to see them blink");
    ESP_LOGI(TAG, "\n");
    
    const int output_pins[] = {
        PIN_DO_0, PIN_DO_1, PIN_DO_2,
        PIN_DO_3, PIN_DO_4, PIN_DO_5
    };
    
    const char* pin_names[] = {
        "DO0", "DO1", "DO2", "DO3", "DO4", "DO5"
    };
    
    // Toggle each output 3 times
    for (int cycle = 0; cycle < 3; cycle++) {
        ESP_LOGI(TAG, "Cycle %d/3:", cycle + 1);
        
        for (int i = 0; i < 6; i++) {
            ESP_LOGI(TAG, "  %s: HIGH", pin_names[i]);
            gpio_set_level((gpio_num_t)output_pins[i], 1);
            vTaskDelay(pdMS_TO_TICKS(200));
            
            ESP_LOGI(TAG, "  %s: LOW", pin_names[i]);
            gpio_set_level((gpio_num_t)output_pins[i], 0);
            vTaskDelay(pdMS_TO_TICKS(200));
        }
    }
    
    ESP_LOGI(TAG, "✅ Digital output toggle test completed");
    ESP_LOGI(TAG, "=================================================");
}

/**
 * @brief Test digital input reading
 * 
 * Reads all digital inputs and displays their current state.
 * User can manually apply voltage to test input detection.
 */
void test_digital_input_read(void) {
    ESP_LOGI(TAG, "=================================================");
    ESP_LOGI(TAG, "  TEST: Digital Input Reading");
    ESP_LOGI(TAG, "=================================================");
    ESP_LOGI(TAG, "📌 Inputs are read with pull-ups enabled");
    ESP_LOGI(TAG, "   (will read HIGH if floating)");
    ESP_LOGI(TAG, "\n");
    
    const int input_pins[] = {PIN_DI_0, PIN_DI_1, PIN_DI_2, PIN_DI_3};
    const char* pin_names[] = {"DI0", "DI1", "DI2", "DI3"};
    
    // Read inputs 5 times with delay
    for (int sample = 0; sample < 5; sample++) {
        ESP_LOGI(TAG, "Sample %d/5:", sample + 1);
        
        for (int i = 0; i < 4; i++) {
            int level = gpio_get_level((gpio_num_t)input_pins[i]);
            ESP_LOGI(TAG, "  %s (GPIO %d): %s", 
                     pin_names[i], 
                     input_pins[i],
                     level ? "HIGH (1)" : "LOW (0)");
        }
        
        ESP_LOGI(TAG, "");
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
    
    ESP_LOGI(TAG, "✅ Digital input reading test completed");
    ESP_LOGI(TAG, "=================================================");
}

/**
 * @brief Interactive loopback test
 * 
 * This test requires the user to wire DO0 to DI0 for verification.
 * The test sets DO0 HIGH/LOW and verifies DI0 reads the same value.
 */
void test_digital_loopback_interactive(void) {
    ESP_LOGI(TAG, "=================================================");
    ESP_LOGI(TAG, "  TEST: Digital I/O Loopback (Interactive)");
    ESP_LOGI(TAG, "=================================================");
    ESP_LOGI(TAG, "");
    ESP_LOGI(TAG, "⚠️  HARDWARE SETUP REQUIRED:");
    ESP_LOGI(TAG, "    Please connect a wire between:");
    ESP_LOGI(TAG, "    - Pin DO0 (GPIO %d)", PIN_DO_0);
    ESP_LOGI(TAG, "    - Pin DI0 (GPIO %d)", PIN_DI_0);
    ESP_LOGI(TAG, "");
    ESP_LOGI(TAG, "Waiting 10 seconds for you to connect the wire...");
    
    for (int i = 10; i > 0; i--) {
        ESP_LOGI(TAG, "  %d...", i);
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
    
    ESP_LOGI(TAG, "Starting loopback test...\n");
    
    // Test HIGH
    ESP_LOGI(TAG, "Setting DO0 = HIGH");
    gpio_set_level((gpio_num_t)PIN_DO_0, 1);
    vTaskDelay(pdMS_TO_TICKS(100));  // Allow signal to stabilize
    
    int level = gpio_get_level((gpio_num_t)PIN_DI_0);
    ESP_LOGI(TAG, "Reading DI0 = %s", level ? "HIGH" : "LOW");
    
    if (level == 1) {
        ESP_LOGI(TAG, "  ✅ DI0 correctly reads HIGH");
    } else {
        ESP_LOGW(TAG, "  ❌ DI0 should be HIGH but reads LOW");
        ESP_LOGW(TAG, "     Check wire connection!");
    }
    
    // Test LOW
    ESP_LOGI(TAG, "Setting DO0 = LOW");
    gpio_set_level((gpio_num_t)PIN_DO_0, 0);
    vTaskDelay(pdMS_TO_TICKS(100));
    
    level = gpio_get_level((gpio_num_t)PIN_DI_0);
    ESP_LOGI(TAG, "Reading DI0 = %s", level ? "HIGH" : "LOW");
    
    if (level == 0) {
        ESP_LOGI(TAG, "  ✅ DI0 correctly reads LOW");
    } else {
        ESP_LOGW(TAG, "  ❌ DI0 should be LOW but reads HIGH");
        ESP_LOGW(TAG, "     Check wire connection!");
    }
    
    ESP_LOGI(TAG, "");
    ESP_LOGI(TAG, "✅ Digital loopback test completed");
    ESP_LOGI(TAG, "   (Check logs for pass/fail details)");
    ESP_LOGI(TAG, "=================================================");
}

// Unity test runner
extern "C" void app_main(void) {
    ESP_LOGI(TAG, "\n\n");
    ESP_LOGI(TAG, "╔═══════════════════════════════════════════════╗");
    ESP_LOGI(TAG, "║   EdgeBox-Lite Device Integration Tests      ║");
    ESP_LOGI(TAG, "║   Test Suite: Digital I/O                    ║");
    ESP_LOGI(TAG, "╚═══════════════════════════════════════════════╝");
    ESP_LOGI(TAG, "\n");
    
    vTaskDelay(pdMS_TO_TICKS(1000));
    
    UNITY_BEGIN();
    
    RUN_TEST(test_digital_output_config);
    RUN_TEST(test_digital_input_config);
    RUN_TEST(test_digital_output_toggle);
    RUN_TEST(test_digital_input_read);
    RUN_TEST(test_digital_loopback_interactive);
    
    UNITY_END();
    
    ESP_LOGI(TAG, "\n");
    ESP_LOGI(TAG, "╔═══════════════════════════════════════════════╗");
    ESP_LOGI(TAG, "║   All Digital I/O Tests Completed            ║");
    ESP_LOGI(TAG, "╚═══════════════════════════════════════════════╝");
}
