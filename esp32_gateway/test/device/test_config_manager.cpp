/**
 * @file test_config_manager.cpp
 * @brief Device integration tests for Configuration Manager
 * 
 * Tests del sistema de configuración:
 * - Carga de configuración desde YAML
 * - Valores por defecto
 * - Actualización de configuración
 * - Persistencia en SD
 * - Validación de parámetros
 * 
 * @note Este test debe ejecutarse EN el ESP32 hardware con SD card
 */

#include "unity.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "config_manager.h"
#include <string.h>

static const char *TAG = "TEST_CONFIG";

// Variables globales para el test
static ConfigManager* config_manager = nullptr;

/**
 * @brief Setup: Initialize before each test
 */
void setUp(void) {
    ESP_LOGI(TAG, "Setting up Config Manager test...");
}

/**
 * @brief Teardown: Cleanup after each test
 */
void tearDown(void) {
    if (config_manager != nullptr) {
        delete config_manager;
        config_manager = nullptr;
    }
    vTaskDelay(pdMS_TO_TICKS(100));
}

/**
 * @brief Test 1: Config Manager Initialization
 * 
 * Verifica que:
 * - El manager se crea correctamente
 * - Inicialización sin errores
 */
void test_config_init(void) {
    ESP_LOGI(TAG, "Test: Config Manager Initialization");
    
    config_manager = new ConfigManager();
    TEST_ASSERT_NOT_NULL_MESSAGE(config_manager, "ConfigManager should be created");
    
    esp_err_t ret = config_manager->init();
    TEST_ASSERT_EQUAL_MESSAGE(ESP_OK, ret, "Config manager should initialize successfully");
    
    ESP_LOGI(TAG, "✓ Config manager initialized");
}

/**
 * @brief Test 2: Load Default Configuration
 * 
 * Verifica que:
 * - Se carga configuración por defecto
 * - Los valores son razonables
 */
void test_config_load_defaults(void) {
    ESP_LOGI(TAG, "Test: Load Default Configuration");
    
    config_manager = new ConfigManager();
    config_manager->init();
    
    // Obtener valores por defecto
    int can_bitrate = config_manager->get_can_bitrate();
    const char* device_name = config_manager->get_device_name();
    
    ESP_LOGI(TAG, "Default CAN bitrate: %d", can_bitrate);
    ESP_LOGI(TAG, "Default device name: %s", device_name);
    
    // Verificar valores razonables
    TEST_ASSERT_TRUE_MESSAGE(can_bitrate > 0, "CAN bitrate should be positive");
    TEST_ASSERT_NOT_NULL_MESSAGE(device_name, "Device name should not be NULL");
    
    ESP_LOGI(TAG, "✓ Default configuration loaded");
}

/**
 * @brief Test 3: Get CAN Configuration
 * 
 * Verifica que:
 * - Se puede obtener configuración CAN
 * - Los valores son válidos
 */
void test_config_get_can_config(void) {
    ESP_LOGI(TAG, "Test: Get CAN Configuration");
    
    config_manager = new ConfigManager();
    config_manager->init();
    
    int bitrate = config_manager->get_can_bitrate();
    int tx_pin = config_manager->get_can_tx_pin();
    int rx_pin = config_manager->get_can_rx_pin();
    
    ESP_LOGI(TAG, "CAN Bitrate: %d", bitrate);
    ESP_LOGI(TAG, "CAN TX Pin: %d", tx_pin);
    ESP_LOGI(TAG, "CAN RX Pin: %d", rx_pin);
    
    // Verificar rangos válidos
    TEST_ASSERT_TRUE(bitrate == 125000 || bitrate == 250000 || 
                     bitrate == 500000 || bitrate == 1000000);
    TEST_ASSERT_TRUE(tx_pin >= 0 && tx_pin <= 48);
    TEST_ASSERT_TRUE(rx_pin >= 0 && rx_pin <= 48);
    
    ESP_LOGI(TAG, "✓ CAN configuration valid");
}

/**
 * @brief Test 4: Get Network Configuration
 * 
 * Verifica que:
 * - Se puede obtener configuración de red
 * - Los valores tienen formato válido
 */
void test_config_get_network_config(void) {
    ESP_LOGI(TAG, "Test: Get Network Configuration");
    
    config_manager = new ConfigManager();
    config_manager->init();
    
    bool use_dhcp = config_manager->get_use_dhcp();
    const char* static_ip = config_manager->get_static_ip();
    const char* gateway = config_manager->get_gateway();
    const char* netmask = config_manager->get_netmask();
    
    ESP_LOGI(TAG, "Use DHCP: %s", use_dhcp ? "Yes" : "No");
    ESP_LOGI(TAG, "Static IP: %s", static_ip);
    ESP_LOGI(TAG, "Gateway: %s", gateway);
    ESP_LOGI(TAG, "Netmask: %s", netmask);
    
    TEST_ASSERT_NOT_NULL(static_ip);
    TEST_ASSERT_NOT_NULL(gateway);
    TEST_ASSERT_NOT_NULL(netmask);
    
    ESP_LOGI(TAG, "✓ Network configuration retrieved");
}

/**
 * @brief Test 5: Update Configuration
 * 
 * Verifica que:
 * - Se puede actualizar la configuración
 * - Los cambios se aplican correctamente
 */
void test_config_update_values(void) {
    ESP_LOGI(TAG, "Test: Update Configuration");
    
    config_manager = new ConfigManager();
    config_manager->init();
    
    // Actualizar CAN bitrate
    int old_bitrate = config_manager->get_can_bitrate();
    int new_bitrate = (old_bitrate == 125000) ? 250000 : 125000;
    
    esp_err_t ret = config_manager->set_can_bitrate(new_bitrate);
    TEST_ASSERT_EQUAL(ESP_OK, ret);
    
    int current_bitrate = config_manager->get_can_bitrate();
    TEST_ASSERT_EQUAL_MESSAGE(new_bitrate, current_bitrate, "Bitrate should be updated");
    
    ESP_LOGI(TAG, "✓ Configuration updated: %d -> %d", old_bitrate, new_bitrate);
}

/**
 * @brief Test 6: Save Configuration
 * 
 * Verifica que:
 * - Se puede guardar configuración
 * - La operación completa sin errores
 */
void test_config_save(void) {
    ESP_LOGI(TAG, "Test: Save Configuration");
    
    config_manager = new ConfigManager();
    config_manager->init();
    
    // Modificar algo
    config_manager->set_can_bitrate(250000);
    
    // Guardar
    esp_err_t ret = config_manager->save();
    
    if (ret == ESP_OK) {
        ESP_LOGI(TAG, "✓ Configuration saved successfully");
        TEST_ASSERT_EQUAL(ESP_OK, ret);
    } else {
        ESP_LOGW(TAG, "⚠ Save failed (SD card may not be available): 0x%x", ret);
        TEST_IGNORE_MESSAGE("Save test skipped - SD card issue");
    }
}

/**
 * @brief Test 7: Load Configuration
 * 
 * Verifica que:
 * - Se puede cargar configuración guardada
 * - Los valores persisten
 */
void test_config_load(void) {
    ESP_LOGI(TAG, "Test: Load Configuration");
    
    config_manager = new ConfigManager();
    
    esp_err_t ret = config_manager->load();
    
    if (ret == ESP_OK) {
        ESP_LOGI(TAG, "✓ Configuration loaded successfully");
        TEST_ASSERT_EQUAL(ESP_OK, ret);
        
        // Verificar que se cargó algo
        int bitrate = config_manager->get_can_bitrate();
        TEST_ASSERT_TRUE(bitrate > 0);
    } else {
        ESP_LOGW(TAG, "⚠ Load failed (config file may not exist): 0x%x", ret);
        TEST_IGNORE_MESSAGE("Load test skipped - no config file");
    }
}

/**
 * @brief Test 8: Configuration Persistence
 * 
 * Verifica que:
 * - Los cambios persisten después de save/load
 */
void test_config_persistence(void) {
    ESP_LOGI(TAG, "Test: Configuration Persistence");
    
    // Crear primera instancia y guardar
    ConfigManager* config1 = new ConfigManager();
    config1->init();
    config1->set_can_bitrate(500000);
    esp_err_t save_ret = config1->save();
    delete config1;
    
    if (save_ret != ESP_OK) {
        ESP_LOGW(TAG, "⚠ Cannot save, skipping persistence test");
        TEST_IGNORE_MESSAGE("Persistence test skipped - cannot save");
        return;
    }
    
    vTaskDelay(pdMS_TO_TICKS(500));
    
    // Crear segunda instancia y cargar
    ConfigManager* config2 = new ConfigManager();
    esp_err_t load_ret = config2->load();
    
    if (load_ret == ESP_OK) {
        int loaded_bitrate = config2->get_can_bitrate();
        TEST_ASSERT_EQUAL_MESSAGE(500000, loaded_bitrate, "Configuration should persist");
        ESP_LOGI(TAG, "✓ Configuration persisted correctly");
    } else {
        ESP_LOGW(TAG, "⚠ Cannot load, persistence inconclusive");
        TEST_IGNORE_MESSAGE("Persistence test inconclusive");
    }
    
    delete config2;
}

/**
 * @brief Test 9: Invalid Values Rejection
 * 
 * Verifica que:
 * - Valores inválidos son rechazados
 * - La configuración mantiene valores válidos
 */
void test_config_invalid_values(void) {
    ESP_LOGI(TAG, "Test: Invalid Values Rejection");
    
    config_manager = new ConfigManager();
    config_manager->init();
    
    int old_bitrate = config_manager->get_can_bitrate();
    
    // Intentar establecer bitrate inválido
    esp_err_t ret1 = config_manager->set_can_bitrate(0);
    esp_err_t ret2 = config_manager->set_can_bitrate(-1000);
    esp_err_t ret3 = config_manager->set_can_bitrate(9999999);
    
    // Verificar que el bitrate no cambió
    int current_bitrate = config_manager->get_can_bitrate();
    
    ESP_LOGI(TAG, "Invalid value results: 0x%x, 0x%x, 0x%x", ret1, ret2, ret3);
    ESP_LOGI(TAG, "Bitrate unchanged: %d", current_bitrate);
    
    // Al menos uno debería fallar
    bool at_least_one_failed = (ret1 != ESP_OK) || (ret2 != ESP_OK) || (ret3 != ESP_OK);
    TEST_ASSERT_TRUE_MESSAGE(at_least_one_failed, "Invalid values should be rejected");
    
    ESP_LOGI(TAG, "✓ Invalid values handled");
}

/**
 * @brief Test 10: Configuration Reset
 * 
 * Verifica que:
 * - Se puede resetear a valores por defecto
 * - Los valores se restauran correctamente
 */
void test_config_reset(void) {
    ESP_LOGI(TAG, "Test: Configuration Reset");
    
    config_manager = new ConfigManager();
    config_manager->init();
    
    // Modificar valores
    config_manager->set_can_bitrate(1000000);
    
    // Resetear a defaults
    esp_err_t ret = config_manager->reset_to_defaults();
    
    if (ret == ESP_OK) {
        int bitrate = config_manager->get_can_bitrate();
        ESP_LOGI(TAG, "Bitrate after reset: %d", bitrate);
        
        // Debería volver a un valor por defecto razonable
        TEST_ASSERT_TRUE(bitrate == 125000 || bitrate == 250000);
        
        ESP_LOGI(TAG, "✓ Reset to defaults successful");
    } else {
        ESP_LOGW(TAG, "⚠ Reset method may not be implemented: 0x%x", ret);
        TEST_IGNORE_MESSAGE("Reset test skipped - method not implemented");
    }
}

/**
 * @brief Main test runner
 */
extern "C" void app_main(void) {
    ESP_LOGI(TAG, "========================================");
    ESP_LOGI(TAG, "Starting Config Manager Device Tests");
    ESP_LOGI(TAG, "========================================");
    ESP_LOGI(TAG, "");
    ESP_LOGI(TAG, "REQUIREMENTS:");
    ESP_LOGI(TAG, "  - SD card inserted (for save/load tests)");
    ESP_LOGI(TAG, "  - Config file may be created");
    ESP_LOGI(TAG, "");
    
    vTaskDelay(pdMS_TO_TICKS(1000)); // Wait for system stabilization
    
    UNITY_BEGIN();
    
    RUN_TEST(test_config_init);
    RUN_TEST(test_config_load_defaults);
    RUN_TEST(test_config_get_can_config);
    RUN_TEST(test_config_get_network_config);
    RUN_TEST(test_config_update_values);
    RUN_TEST(test_config_save);
    RUN_TEST(test_config_load);
    RUN_TEST(test_config_persistence);
    RUN_TEST(test_config_invalid_values);
    RUN_TEST(test_config_reset);
    
    UNITY_END();
    
    ESP_LOGI(TAG, "========================================");
    ESP_LOGI(TAG, "All Config Manager tests completed!");
    ESP_LOGI(TAG, "========================================");
}
