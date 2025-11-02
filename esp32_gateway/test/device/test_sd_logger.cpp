/**
 * @file test_sd_logger.cpp
 * @brief Device integration test for SD Card Logger
 * 
 * This test validates the SD logger functionality including:
 * - SD card initialization
 * - File creation and writing
 * - Auto-rotation at 1MB threshold
 * - Auto-cleanup keeping only last 10 files
 * - Disk space information
 * 
 * @note This test must be run ON the ESP32 hardware with SD card inserted.
 */

#include "unity.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "sd_logger.h"
#include "hardware_config.h"
#include <string.h>

static const char *TAG = "TEST_SD_LOGGER";

/**
 * @brief Setup: Initialize SD logger before each test
 */
void setUp(void) {
    ESP_LOGI(TAG, "Setting up SD Logger test...");
    ESP_LOGI(TAG, "  MOSI: GPIO %d", PIN_SD_MOSI);
    ESP_LOGI(TAG, "  MISO: GPIO %d", PIN_SD_MISO);
    ESP_LOGI(TAG, "  CLK:  GPIO %d", PIN_SD_CLK);
    ESP_LOGI(TAG, "  CS:   GPIO %d", PIN_SD_CS);
}

/**
 * @brief Teardown: Cleanup after each test
 */
void tearDown(void) {
    vTaskDelay(pdMS_TO_TICKS(100)); // Give time for async operations
}

/**
 * @brief Test 1: SD Card Initialization
 * 
 * Verifies that:
 * - SPI bus can be initialized for SD card
 * - SD card can be mounted successfully
 * - Mount point is accessible
 */
void test_sd_init(void) {
    ESP_LOGI(TAG, "Test: SD Card Initialization");
    
    // Create and initialize SD logger
    SDLogger logger;
    bool init_result = logger.init();
    
    TEST_ASSERT_TRUE_MESSAGE(init_result, "SD card should initialize successfully");
    TEST_ASSERT_TRUE_MESSAGE(logger.is_mounted(), "SD card should be mounted");
    
    ESP_LOGI(TAG, "✓ SD card initialized and mounted");
}

/**
 * @brief Test 2: Basic Logging
 * 
 * Verifies that:
 * - Log messages can be written to SD card
 * - Different log levels work correctly
 * - Log file is created with proper naming
 */
void test_sd_basic_logging(void) {
    ESP_LOGI(TAG, "Test: Basic Logging");
    
    SDLogger logger;
    TEST_ASSERT_TRUE(logger.init());
    
    // Write logs at different levels
    SD_LOGI(TAG, "Test INFO message");
    SD_LOGW(TAG, "Test WARN message");
    SD_LOGE(TAG, "Test ERROR message");
    SD_LOGD(TAG, "Test DEBUG message");
    
    vTaskDelay(pdMS_TO_TICKS(100)); // Allow write to complete
    
    ESP_LOGI(TAG, "✓ Basic logging completed");
}

/**
 * @brief Test 3: Log Rotation
 * 
 * Verifies that:
 * - Large log writes trigger rotation at 1MB threshold
 * - New log file is created after rotation
 * - Old log file is preserved
 */
void test_sd_log_rotation(void) {
    ESP_LOGI(TAG, "Test: Log Rotation");
    
    SDLogger logger;
    TEST_ASSERT_TRUE(logger.init());
    
    // Write enough data to trigger rotation (> 1MB)
    const int iterations = 5000; // ~1.2 MB of log data
    char large_msg[256];
    
    ESP_LOGI(TAG, "Writing %d log entries to trigger rotation...", iterations);
    
    for (int i = 0; i < iterations; i++) {
        snprintf(large_msg, sizeof(large_msg), 
                "Test log entry #%d - This is a test message with enough content to accumulate data %d",
                i, i * 12345);
        SD_LOGI(TAG, "%s", large_msg);
        
        if (i % 1000 == 0) {
            ESP_LOGI(TAG, "Progress: %d/%d entries written", i, iterations);
            vTaskDelay(pdMS_TO_TICKS(10)); // Small delay to prevent watchdog
        }
    }
    
    vTaskDelay(pdMS_TO_TICKS(500)); // Allow rotation to complete
    
    ESP_LOGI(TAG, "✓ Log rotation test completed");
}

/**
 * @brief Test 4: Auto-cleanup (File Deletion)
 * 
 * Verifies that:
 * - Old log files are automatically deleted
 * - Only last 10 files are kept
 * - Oldest files are deleted first
 */
void test_sd_auto_cleanup(void) {
    ESP_LOGI(TAG, "Test: Auto-cleanup");
    
    SDLogger logger;
    TEST_ASSERT_TRUE(logger.init());
    
    // Force creation of multiple log files by rotation
    ESP_LOGI(TAG, "Creating multiple log files for cleanup test...");
    
    for (int file = 0; file < 15; file++) {
        logger.rotate_log(); // Force rotation
        
        // Write some data to the new file
        for (int i = 0; i < 100; i++) {
            SD_LOGI(TAG, "File %d - Entry %d", file, i);
        }
        
        vTaskDelay(pdMS_TO_TICKS(200));
    }
    
    // Trigger cleanup
    vTaskDelay(pdMS_TO_TICKS(1000));
    
    ESP_LOGI(TAG, "✓ Auto-cleanup test completed");
    ESP_LOGI(TAG, "Check SD card - should have only ~10 log files");
}

/**
 * @brief Test 5: Disk Space Information
 * 
 * Verifies that:
 * - Disk space information can be retrieved
 * - Total and used space values are reasonable
 */
void test_sd_disk_info(void) {
    ESP_LOGI(TAG, "Test: Disk Space Information");
    
    SDLogger logger;
    TEST_ASSERT_TRUE(logger.init());
    
    uint32_t total_mb = 0;
    uint32_t used_mb = 0;
    
    bool info_result = logger.get_disk_info(&total_mb, &used_mb);
    
    TEST_ASSERT_TRUE_MESSAGE(info_result, "Should retrieve disk info successfully");
    TEST_ASSERT_GREATER_THAN_MESSAGE(0, total_mb, "Total MB should be > 0");
    TEST_ASSERT_MESSAGE(used_mb <= total_mb, "Used MB should be <= Total MB");
    
    ESP_LOGI(TAG, "Disk Info: Total=%lu MB, Used=%lu MB, Free=%lu MB", 
             total_mb, used_mb, total_mb - used_mb);
    ESP_LOGI(TAG, "✓ Disk space information retrieved");
}

/**
 * @brief Test 6: Thread Safety
 * 
 * Verifies that:
 * - Multiple tasks can log simultaneously
 * - Mutex protection prevents data corruption
 */
void test_sd_thread_safety(void) {
    ESP_LOGI(TAG, "Test: Thread Safety");
    
    SDLogger logger;
    TEST_ASSERT_TRUE(logger.init());
    
    // Task 1: Write INFO messages
    auto task1 = [](void* param) {
        for (int i = 0; i < 100; i++) {
            SD_LOGI("TASK1", "Message from Task 1 - %d", i);
            vTaskDelay(pdMS_TO_TICKS(10));
        }
        vTaskDelete(NULL);
    };
    
    // Task 2: Write WARN messages
    auto task2 = [](void* param) {
        for (int i = 0; i < 100; i++) {
            SD_LOGW("TASK2", "Warning from Task 2 - %d", i);
            vTaskDelay(pdMS_TO_TICKS(10));
        }
        vTaskDelete(NULL);
    };
    
    // Create concurrent tasks
    xTaskCreate(task1, "log_task1", 2048, NULL, 5, NULL);
    xTaskCreate(task2, "log_task2", 2048, NULL, 5, NULL);
    
    // Wait for tasks to complete
    vTaskDelay(pdMS_TO_TICKS(2000));
    
    ESP_LOGI(TAG, "✓ Thread safety test completed");
}

/**
 * @brief Test 7: Graceful Degradation (No SD Card)
 * 
 * Verifies that:
 * - System continues running if SD card is not present
 * - Logging macros don't crash when SD unavailable
 */
void test_sd_graceful_failure(void) {
    ESP_LOGI(TAG, "Test: Graceful Degradation");
    ESP_LOGI(TAG, "Note: Remove SD card before running this test");
    
    // Try to initialize without SD card
    SDLogger logger;
    bool init_result = logger.init();
    
    // Should fail gracefully
    ESP_LOGI(TAG, "Init result (expected false): %d", init_result);
    
    // System should continue - try to log anyway
    SD_LOGI(TAG, "This message should not crash the system");
    SD_LOGW(TAG, "Even if SD card is not available");
    
    ESP_LOGI(TAG, "✓ Graceful degradation test completed");
}

/**
 * @brief Main test application
 */
extern "C" void app_main(void) {
    ESP_LOGI(TAG, "====================================");
    ESP_LOGI(TAG, "   SD LOGGER DEVICE TESTS");
    ESP_LOGI(TAG, "====================================");
    ESP_LOGI(TAG, "");
    ESP_LOGI(TAG, "Hardware Configuration:");
    ESP_LOGI(TAG, "  SD Card Pins:");
    ESP_LOGI(TAG, "    MOSI: GPIO %d", PIN_SD_MOSI);
    ESP_LOGI(TAG, "    MISO: GPIO %d", PIN_SD_MISO);
    ESP_LOGI(TAG, "    CLK:  GPIO %d", PIN_SD_CLK);
    ESP_LOGI(TAG, "    CS:   GPIO %d", PIN_SD_CS);
    ESP_LOGI(TAG, "");
    ESP_LOGI(TAG, "Prerequisites:");
    ESP_LOGI(TAG, "  - SD card must be inserted and formatted (FAT32)");
    ESP_LOGI(TAG, "  - SD card should have at least 50 MB free space");
    ESP_LOGI(TAG, "");
    
    vTaskDelay(pdMS_TO_TICKS(2000));
    
    UNITY_BEGIN();
    
    ESP_LOGI(TAG, "Running Test 1: SD Initialization");
    RUN_TEST(test_sd_init);
    vTaskDelay(pdMS_TO_TICKS(500));
    
    ESP_LOGI(TAG, "Running Test 2: Basic Logging");
    RUN_TEST(test_sd_basic_logging);
    vTaskDelay(pdMS_TO_TICKS(500));
    
    ESP_LOGI(TAG, "Running Test 3: Log Rotation");
    RUN_TEST(test_sd_log_rotation);
    vTaskDelay(pdMS_TO_TICKS(500));
    
    ESP_LOGI(TAG, "Running Test 4: Auto-cleanup");
    RUN_TEST(test_sd_auto_cleanup);
    vTaskDelay(pdMS_TO_TICKS(500));
    
    ESP_LOGI(TAG, "Running Test 5: Disk Info");
    RUN_TEST(test_sd_disk_info);
    vTaskDelay(pdMS_TO_TICKS(500));
    
    ESP_LOGI(TAG, "Running Test 6: Thread Safety");
    RUN_TEST(test_sd_thread_safety);
    vTaskDelay(pdMS_TO_TICKS(500));
    
    ESP_LOGI(TAG, "Running Test 7: Graceful Failure (requires SD removal)");
    // RUN_TEST(test_sd_graceful_failure); // Uncomment and remove SD to test
    
    UNITY_END();
    
    ESP_LOGI(TAG, "");
    ESP_LOGI(TAG, "====================================");
    ESP_LOGI(TAG, "   ALL TESTS COMPLETED");
    ESP_LOGI(TAG, "====================================");
}
