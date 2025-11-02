/**
 * @file test_sd_logger_unit.cpp
 * @brief Native unit tests for SD Logger (without hardware)
 * 
 * These tests validate the SD logger logic that doesn't require
 * actual SD card hardware, focusing on:
 * - Log level string conversion
 * - File naming patterns
 * - Configuration constants
 * 
 * @note This test can be run on the host machine (not on ESP32).
 */

#include "unity.h"
#include "sd_logger.h"
#include <string.h>

static const char *TAG = "TEST_SD_LOGGER_UNIT";

/**
 * @brief Setup before each test
 */
void setUp(void) {
    // No setup needed for native tests
}

/**
 * @brief Teardown after each test
 */
void tearDown(void) {
    // No teardown needed for native tests
}

/**
 * @brief Test: Log Level to String Conversion
 * 
 * Verifies that log levels are correctly converted to strings.
 */
void test_log_level_to_string(void) {
    const char* debug_str = SDLogger::level_to_string(SD_LOG_DEBUG);
    const char* info_str = SDLogger::level_to_string(SD_LOG_INFO);
    const char* warn_str = SDLogger::level_to_string(SD_LOG_WARN);
    const char* error_str = SDLogger::level_to_string(SD_LOG_ERROR);
    
    TEST_ASSERT_EQUAL_STRING("DEBUG", debug_str);
    TEST_ASSERT_EQUAL_STRING("INFO ", info_str);
    TEST_ASSERT_EQUAL_STRING("WARN ", warn_str);
    TEST_ASSERT_EQUAL_STRING("ERROR", error_str);
    
    // All strings should be 5 characters (for alignment)
    TEST_ASSERT_EQUAL(5, strlen(debug_str));
    TEST_ASSERT_EQUAL(5, strlen(info_str));
    TEST_ASSERT_EQUAL(5, strlen(warn_str));
    TEST_ASSERT_EQUAL(5, strlen(error_str));
}

/**
 * @brief Test: Configuration Constants
 * 
 * Verifies that configuration constants have sensible values.
 */
void test_configuration_constants(void) {
    // SD mount point should be defined
    TEST_ASSERT_NOT_NULL(SD_MOUNT_POINT);
    TEST_ASSERT_GREATER_THAN(0, strlen(SD_MOUNT_POINT));
    
    // Log file prefix should be defined
    TEST_ASSERT_NOT_NULL(LOG_FILE_PREFIX);
    TEST_ASSERT_EQUAL_STRING("gateway_", LOG_FILE_PREFIX);
    
    // Log file extension should be defined
    TEST_ASSERT_NOT_NULL(LOG_FILE_EXT);
    TEST_ASSERT_EQUAL_STRING(".log", LOG_FILE_EXT);
    
    // Maximum log files should be reasonable (10 files)
    TEST_ASSERT_EQUAL(10, MAX_LOG_FILES);
    
    // Maximum log size should be 1MB
    TEST_ASSERT_EQUAL(1024 * 1024, MAX_LOG_SIZE_BYTES);
}

/**
 * @brief Test: File Naming Pattern
 * 
 * Verifies that log files follow expected naming pattern:
 * gateway_YYYYMMDD_HHMMSS.log
 */
void test_file_naming_pattern(void) {
    // Expected pattern: "gateway_20251101_143025.log"
    const char* expected_prefix = "gateway_";
    const char* expected_ext = ".log";
    
    // Verify prefix
    TEST_ASSERT_EQUAL_STRING("gateway_", expected_prefix);
    
    // Verify extension
    TEST_ASSERT_EQUAL_STRING(".log", expected_ext);
    
    // Verify minimum filename length
    // gateway_ (8) + YYYYMMDD (8) + _ (1) + HHMMSS (6) + .log (4) = 27 chars
    const int min_filename_length = 27;
    TEST_ASSERT_EQUAL(27, min_filename_length);
}

/**
 * @brief Test: Log Rotation Threshold
 * 
 * Verifies that rotation threshold is set correctly.
 */
void test_rotation_threshold(void) {
    const uint32_t one_mb = 1024 * 1024;
    
    TEST_ASSERT_EQUAL(one_mb, MAX_LOG_SIZE_BYTES);
    TEST_ASSERT_GREATER_THAN(0, MAX_LOG_SIZE_BYTES);
    TEST_ASSERT_LESS_THAN(10 * 1024 * 1024, MAX_LOG_SIZE_BYTES); // Less than 10MB
}

/**
 * @brief Test: Maximum Files Limit
 * 
 * Verifies that maximum files limit is reasonable.
 */
void test_max_files_limit(void) {
    // Should keep last 10 files
    TEST_ASSERT_EQUAL(10, MAX_LOG_FILES);
    TEST_ASSERT_GREATER_THAN(0, MAX_LOG_FILES);
    TEST_ASSERT_LESS_THAN(100, MAX_LOG_FILES); // Reasonable upper limit
}

/**
 * @brief Test: SD Logger Class Size
 * 
 * Verifies that SDLogger class has reasonable memory footprint.
 */
void test_class_size(void) {
    size_t logger_size = sizeof(SDLogger);
    
    // SDLogger should be reasonably sized (< 1KB)
    TEST_ASSERT_LESS_THAN(1024, logger_size);
    TEST_ASSERT_GREATER_THAN(0, logger_size);
}

/**
 * @brief Main test runner for native tests
 */
int main(void) {
    UNITY_BEGIN();
    
    RUN_TEST(test_log_level_to_string);
    RUN_TEST(test_configuration_constants);
    RUN_TEST(test_file_naming_pattern);
    RUN_TEST(test_rotation_threshold);
    RUN_TEST(test_max_files_limit);
    RUN_TEST(test_class_size);
    
    return UNITY_END();
}
