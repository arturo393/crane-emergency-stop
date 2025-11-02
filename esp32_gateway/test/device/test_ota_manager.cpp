/**
 * @file test_ota_manager.cpp
 * @brief Device integration tests for OTA Manager
 * 
 * Tests de actualización Over-The-Air:
 * - Información de particiones
 * - Validación de firmware
 * - Rollback
 * - Actualización desde buffer
 * 
 * @note Este test debe ejecutarse EN el ESP32 hardware
 */

#include "unity.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "ota_manager.h"
#include <string.h>

static const char *TAG = "TEST_OTA";

/**
 * @brief Setup: Initialize OTA manager before each test
 */
void setUp(void) {
    ESP_LOGI(TAG, "Setting up OTA Manager test...");
}

/**
 * @brief Teardown: Cleanup after each test
 */
void tearDown(void) {
    vTaskDelay(pdMS_TO_TICKS(100));
}

/**
 * @brief Test 1: OTA Manager Initialization
 * 
 * Verifica que:
 * - OTA manager se inicializa correctamente
 * - Se pueden obtener particiones
 */
void test_ota_init(void) {
    ESP_LOGI(TAG, "Test: OTA Manager Initialization");
    
    OtaManager manager;
    esp_err_t ret = manager.init();
    
    TEST_ASSERT_EQUAL_MESSAGE(ESP_OK, ret, "OTA manager should initialize successfully");
    
    ESP_LOGI(TAG, "✓ OTA manager initialized");
}

/**
 * @brief Test 2: Get Running Partition Info
 * 
 * Verifica que:
 * - Se puede obtener información de la partición actual
 * - Label y versión son válidos
 */
void test_ota_get_partition_info(void) {
    ESP_LOGI(TAG, "Test: Get Running Partition Info");
    
    OtaManager manager;
    TEST_ASSERT_EQUAL(ESP_OK, manager.init());
    
    char label[17] = {0};
    char version[32] = {0};
    
    esp_err_t ret = manager.get_running_partition_info(label, version);
    
    TEST_ASSERT_EQUAL_MESSAGE(ESP_OK, ret, "Should retrieve partition info");
    TEST_ASSERT_MESSAGE(strlen(label) > 0, "Label should not be empty");
    TEST_ASSERT_MESSAGE(strlen(version) > 0, "Version should not be empty");
    
    ESP_LOGI(TAG, "Running partition: %s", label);
    ESP_LOGI(TAG, "Firmware version: %s", version);
    ESP_LOGI(TAG, "✓ Partition info retrieved");
}

/**
 * @brief Test 3: Pending Validation Check
 * 
 * Verifica que:
 * - Se puede verificar si hay firmware pendiente de validación
 * - El estado se reporta correctamente
 */
void test_ota_pending_validation(void) {
    ESP_LOGI(TAG, "Test: Pending Validation Check");
    
    OtaManager manager;
    TEST_ASSERT_EQUAL(ESP_OK, manager.init());
    
    bool pending = manager.is_pending_validation();
    
    ESP_LOGI(TAG, "Pending validation: %s", pending ? "YES" : "NO");
    
    // Si hay validación pendiente, marcar como válido
    if (pending) {
        ESP_LOGW(TAG, "Firmware pendiente de validación detectado");
        esp_err_t ret = manager.mark_as_valid();
        TEST_ASSERT_EQUAL_MESSAGE(ESP_OK, ret, "Should mark as valid successfully");
        ESP_LOGI(TAG, "✓ Firmware marked as valid");
    } else {
        ESP_LOGI(TAG, "✓ No pending validation");
    }
}

/**
 * @brief Test 4: OTA State Management
 * 
 * Verifica que:
 * - El estado inicial es IDLE
 * - Los estados cambian correctamente
 */
void test_ota_state_management(void) {
    ESP_LOGI(TAG, "Test: OTA State Management");
    
    OtaManager manager;
    TEST_ASSERT_EQUAL(ESP_OK, manager.init());
    
    // Estado inicial debe ser IDLE
    OtaState state = manager.get_state();
    TEST_ASSERT_EQUAL_MESSAGE((int)OtaState::IDLE, (int)state, "Initial state should be IDLE");
    
    // No debe haber actualización en progreso
    bool updating = manager.is_updating();
    TEST_ASSERT_FALSE_MESSAGE(updating, "Should not be updating initially");
    
    ESP_LOGI(TAG, "✓ State management working");
}

/**
 * @brief Test 5: Invalid Buffer Update (Error Handling)
 * 
 * Verifica que:
 * - Actualización con buffer NULL falla apropiadamente
 * - Actualización con tamaño 0 falla apropiadamente
 * - Errores se manejan correctamente
 */
void test_ota_invalid_buffer_update(void) {
    ESP_LOGI(TAG, "Test: Invalid Buffer Update");
    
    OtaManager manager;
    TEST_ASSERT_EQUAL(ESP_OK, manager.init());
    
    // Probar con buffer NULL
    OtaResult result1 = manager.update_from_buffer(nullptr, 1024);
    TEST_ASSERT_FALSE_MESSAGE(result1.success, "NULL buffer should fail");
    ESP_LOGI(TAG, "✓ NULL buffer rejected: %s", result1.error_msg);
    
    // Probar con tamaño 0
    uint8_t dummy_data[10];
    OtaResult result2 = manager.update_from_buffer(dummy_data, 0);
    TEST_ASSERT_FALSE_MESSAGE(result2.success, "Zero size should fail");
    ESP_LOGI(TAG, "✓ Zero size rejected: %s", result2.error_msg);
    
    ESP_LOGI(TAG, "✓ Error handling working correctly");
}

/**
 * @brief Test 6: Cancel Update
 * 
 * Verifica que:
 * - Se puede cancelar una actualización
 * - El estado regresa a IDLE
 */
void test_ota_cancel_update(void) {
    ESP_LOGI(TAG, "Test: Cancel Update");
    
    OtaManager manager;
    TEST_ASSERT_EQUAL(ESP_OK, manager.init());
    
    esp_err_t ret = manager.cancel_update();
    TEST_ASSERT_EQUAL_MESSAGE(ESP_OK, ret, "Should cancel successfully");
    
    OtaState state = manager.get_state();
    TEST_ASSERT_EQUAL_MESSAGE((int)OtaState::IDLE, (int)state, "State should be IDLE after cancel");
    
    ESP_LOGI(TAG, "✓ Cancel update working");
}

/**
 * @brief Test 7: Small Buffer Update (Simulated)
 * 
 * Verifica que:
 * - Se puede escribir un pequeño buffer de prueba
 * - El proceso de actualización funciona
 * 
 * ADVERTENCIA: Este test NO debe ejecutarse en producción
 * ya que sobrescribe la partición OTA con datos de prueba.
 * Solo para validación en entorno de desarrollo.
 */
void test_ota_small_buffer_update(void) {
    ESP_LOGI(TAG, "Test: Small Buffer Update (DEVELOPMENT ONLY)");
    ESP_LOGW(TAG, "⚠️  Este test sobrescribe la partición OTA - NO ejecutar en producción");
    
    // SKIP this test by default
    ESP_LOGW(TAG, "⏭️  Test SKIPPED por seguridad");
    ESP_LOGI(TAG, "Para habilitar, descomentar el código y flashear desde desarrollo");
    
    /* DESCOMENTAR SOLO EN DESARROLLO:
    OtaManager manager;
    TEST_ASSERT_EQUAL(ESP_OK, manager.init());
    
    // Crear un buffer pequeño de prueba (4KB)
    const size_t test_size = 4096;
    uint8_t* test_data = (uint8_t*)malloc(test_size);
    TEST_ASSERT_NOT_NULL(test_data);
    
    // Llenar con patrón de prueba
    for (size_t i = 0; i < test_size; i++) {
        test_data[i] = (i % 256);
    }
    
    ESP_LOGI(TAG, "Attempting small buffer update (%u bytes)...", test_size);
    
    OtaResult result = manager.update_from_buffer(test_data, test_size, nullptr);
    
    free(test_data);
    
    // El resultado probablemente será error porque no es firmware válido
    // Pero nos permite verificar que el proceso de escritura funciona
    ESP_LOGI(TAG, "Update result: success=%d, error=%s", result.success, result.error_msg);
    ESP_LOGI(TAG, "Bytes written: %u", result.bytes_written);
    
    TEST_ASSERT_GREATER_THAN_MESSAGE(0, result.bytes_written, "Should have written some bytes");
    
    ESP_LOGI(TAG, "✓ Buffer write mechanism working");
    */
}

/**
 * @brief Test 8: Multiple Initialization
 * 
 * Verifica que:
 * - Se puede inicializar múltiples veces sin problemas
 * - El estado se mantiene consistente
 */
void test_ota_multiple_init(void) {
    ESP_LOGI(TAG, "Test: Multiple Initialization");
    
    OtaManager manager;
    
    // Primera inicialización
    esp_err_t ret1 = manager.init();
    TEST_ASSERT_EQUAL(ESP_OK, ret1);
    
    // Segunda inicialización (debe ser segura)
    esp_err_t ret2 = manager.init();
    TEST_ASSERT_EQUAL(ESP_OK, ret2);
    
    // Verificar que sigue funcionando
    char version[32];
    esp_err_t ret3 = manager.get_running_partition_info(nullptr, version);
    TEST_ASSERT_EQUAL(ESP_OK, ret3);
    
    ESP_LOGI(TAG, "✓ Multiple initialization safe");
}

/**
 * @brief Main test application
 */
extern "C" void app_main(void) {
    ESP_LOGI(TAG, "====================================");
    ESP_LOGI(TAG, "   OTA MANAGER DEVICE TESTS");
    ESP_LOGI(TAG, "====================================");
    ESP_LOGI(TAG, "");
    ESP_LOGI(TAG, "⚠️  ADVERTENCIA:");
    ESP_LOGI(TAG, "Algunos tests modifican particiones OTA.");
    ESP_LOGI(TAG, "Solo ejecutar en entorno de desarrollo.");
    ESP_LOGI(TAG, "");
    
    vTaskDelay(pdMS_TO_TICKS(2000));
    
    UNITY_BEGIN();
    
    ESP_LOGI(TAG, "Running Test 1: OTA Initialization");
    RUN_TEST(test_ota_init);
    vTaskDelay(pdMS_TO_TICKS(500));
    
    ESP_LOGI(TAG, "Running Test 2: Get Partition Info");
    RUN_TEST(test_ota_get_partition_info);
    vTaskDelay(pdMS_TO_TICKS(500));
    
    ESP_LOGI(TAG, "Running Test 3: Pending Validation");
    RUN_TEST(test_ota_pending_validation);
    vTaskDelay(pdMS_TO_TICKS(500));
    
    ESP_LOGI(TAG, "Running Test 4: State Management");
    RUN_TEST(test_ota_state_management);
    vTaskDelay(pdMS_TO_TICKS(500));
    
    ESP_LOGI(TAG, "Running Test 5: Invalid Buffer");
    RUN_TEST(test_ota_invalid_buffer_update);
    vTaskDelay(pdMS_TO_TICKS(500));
    
    ESP_LOGI(TAG, "Running Test 6: Cancel Update");
    RUN_TEST(test_ota_cancel_update);
    vTaskDelay(pdMS_TO_TICKS(500));
    
    ESP_LOGI(TAG, "Running Test 7: Small Buffer (SKIPPED)");
    RUN_TEST(test_ota_small_buffer_update);
    vTaskDelay(pdMS_TO_TICKS(500));
    
    ESP_LOGI(TAG, "Running Test 8: Multiple Init");
    RUN_TEST(test_ota_multiple_init);
    vTaskDelay(pdMS_TO_TICKS(500));
    
    UNITY_END();
    
    ESP_LOGI(TAG, "");
    ESP_LOGI(TAG, "====================================");
    ESP_LOGI(TAG, "   ALL TESTS COMPLETED");
    ESP_LOGI(TAG, "====================================");
}
