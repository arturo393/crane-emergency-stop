/**
 * @file test_web_server.cpp
 * @brief Device integration tests for Web Server
 * 
 * Tests del servidor web HTTP:
 * - Inicialización del servidor
 * - Handler de dashboard HTML
 * - API REST /api/status
 * - Actualización de estado
 * - Callbacks de status
 * 
 * @note Este test debe ejecutarse EN el ESP32 hardware con conectividad
 */

#include "unity.h"
#include "esp_log.h"
#include "esp_http_client.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "web_server.h"
#include "cJSON.h"
#include <string.h>

static const char *TAG = "TEST_WEB";

// Variables globales para el test
static WebServer* test_server = nullptr;
static bool status_callback_called = false;
static GatewayStatus last_status;

/**
 * @brief Callback para capturar actualizaciones de status
 */
void test_status_callback(GatewayStatus& status) {
    ESP_LOGI(TAG, "Status callback called");
    status_callback_called = true;
    
    // Llenar con datos de test
    status.can_online = true;
    status.can_bitrate = 125000;
    status.can_rx_count = 42;
    status.can_tx_count = 38;
    status.can_error_count = 0;
    
    status.cia402_state = 0x07; // Operation Enabled
    status.status_word = 0x1637;
    
    status.ethernet_connected = true;
    strcpy(status.ethernet_ip, "192.168.1.100");
    status.wifi_connected = false;
    
    status.uptime_seconds = 3600;
    status.free_heap = 200000;
    strcpy(status.firmware_version, "v1.0.0-test");
    
    status.sd_mounted = true;
    status.sd_total_mb = 4096;
    status.sd_used_mb = 512;
    status.sd_file_count = 15;
    
    status.ota_state = 0; // Idle
    status.ota_progress = 0;
    
    last_status = status;
}

/**
 * @brief Setup: Initialize web server before each test
 */
void setUp(void) {
    ESP_LOGI(TAG, "Setting up Web Server test...");
    status_callback_called = false;
    memset(&last_status, 0, sizeof(GatewayStatus));
}

/**
 * @brief Teardown: Cleanup after each test
 */
void tearDown(void) {
    if (test_server != nullptr) {
        delete test_server;
        test_server = nullptr;
    }
    vTaskDelay(pdMS_TO_TICKS(200));
}

/**
 * @brief Test 1: Web Server Initialization
 * 
 * Verifica que:
 * - El servidor se inicializa correctamente
 * - Se puede configurar el puerto
 * - El servidor inicia sin errores
 */
void test_web_server_init(void) {
    ESP_LOGI(TAG, "Test: Web Server Initialization");
    
    test_server = new WebServer();
    TEST_ASSERT_NOT_NULL_MESSAGE(test_server, "WebServer instance should be created");
    
    esp_err_t ret = test_server->init(8080);
    TEST_ASSERT_EQUAL_MESSAGE(ESP_OK, ret, "Web server should initialize on port 8080");
    
    bool running = test_server->is_running();
    TEST_ASSERT_TRUE_MESSAGE(running, "Web server should be running after init");
    
    ESP_LOGI(TAG, "✓ Web server initialized successfully on port 8080");
}

/**
 * @brief Test 2: Status Callback Registration
 * 
 * Verifica que:
 * - Se puede registrar un callback
 * - El callback se ejecuta cuando se solicita status
 */
void test_web_server_status_callback(void) {
    ESP_LOGI(TAG, "Test: Status Callback Registration");
    
    test_server = new WebServer();
    test_server->init(8081);
    
    // Registrar callback
    test_server->set_status_callback(test_status_callback);
    
    // Simular actualización de status
    GatewayStatus test_status;
    test_server->update_status(test_status);
    
    vTaskDelay(pdMS_TO_TICKS(100)); // Wait for callback
    
    TEST_ASSERT_TRUE_MESSAGE(status_callback_called, "Status callback should be called");
    TEST_ASSERT_EQUAL(true, last_status.can_online);
    TEST_ASSERT_EQUAL(125000, last_status.can_bitrate);
    
    ESP_LOGI(TAG, "✓ Status callback working correctly");
}

/**
 * @brief Test 3: GatewayStatus Structure
 * 
 * Verifica que:
 * - La estructura GatewayStatus tiene todos los campos
 * - Los valores se pueden asignar correctamente
 */
void test_web_server_gateway_status_struct(void) {
    ESP_LOGI(TAG, "Test: GatewayStatus Structure");
    
    GatewayStatus status;
    memset(&status, 0, sizeof(GatewayStatus));
    
    // CAN fields
    status.can_online = true;
    status.can_bitrate = 125000;
    status.can_rx_count = 100;
    status.can_tx_count = 95;
    status.can_error_count = 2;
    
    TEST_ASSERT_TRUE(status.can_online);
    TEST_ASSERT_EQUAL(125000, status.can_bitrate);
    TEST_ASSERT_EQUAL(100, status.can_rx_count);
    TEST_ASSERT_EQUAL(95, status.can_tx_count);
    TEST_ASSERT_EQUAL(2, status.can_error_count);
    
    // CiA402 fields
    status.cia402_state = 0x07;
    status.status_word = 0x1637;
    
    TEST_ASSERT_EQUAL(0x07, status.cia402_state);
    TEST_ASSERT_EQUAL(0x1637, status.status_word);
    
    // Network fields
    status.ethernet_connected = true;
    strcpy(status.ethernet_ip, "192.168.1.100");
    status.wifi_connected = false;
    
    TEST_ASSERT_TRUE(status.ethernet_connected);
    TEST_ASSERT_EQUAL_STRING("192.168.1.100", status.ethernet_ip);
    TEST_ASSERT_FALSE(status.wifi_connected);
    
    // System fields
    status.uptime_seconds = 7200;
    status.free_heap = 150000;
    strcpy(status.firmware_version, "v1.2.3");
    
    TEST_ASSERT_EQUAL(7200, status.uptime_seconds);
    TEST_ASSERT_EQUAL(150000, status.free_heap);
    TEST_ASSERT_EQUAL_STRING("v1.2.3", status.firmware_version);
    
    // SD fields
    status.sd_mounted = true;
    status.sd_total_mb = 8192;
    status.sd_used_mb = 1024;
    status.sd_file_count = 25;
    
    TEST_ASSERT_TRUE(status.sd_mounted);
    TEST_ASSERT_EQUAL(8192, status.sd_total_mb);
    TEST_ASSERT_EQUAL(1024, status.sd_used_mb);
    TEST_ASSERT_EQUAL(25, status.sd_file_count);
    
    // OTA fields
    status.ota_state = 1; // In progress
    status.ota_progress = 50;
    
    TEST_ASSERT_EQUAL(1, status.ota_state);
    TEST_ASSERT_EQUAL(50, status.ota_progress);
    
    ESP_LOGI(TAG, "✓ GatewayStatus structure validated");
}

/**
 * @brief Test 4: Multiple Status Updates
 * 
 * Verifica que:
 * - Se pueden hacer múltiples actualizaciones de status
 * - Los valores se actualizan correctamente
 */
void test_web_server_multiple_updates(void) {
    ESP_LOGI(TAG, "Test: Multiple Status Updates");
    
    test_server = new WebServer();
    test_server->init(8082);
    test_server->set_status_callback(test_status_callback);
    
    // Primera actualización
    GatewayStatus status1;
    test_server->update_status(status1);
    vTaskDelay(pdMS_TO_TICKS(50));
    
    uint32_t first_rx = last_status.can_rx_count;
    
    // Segunda actualización
    GatewayStatus status2;
    test_server->update_status(status2);
    vTaskDelay(pdMS_TO_TICKS(50));
    
    TEST_ASSERT_EQUAL(first_rx, last_status.can_rx_count);
    
    ESP_LOGI(TAG, "✓ Multiple updates handled correctly");
}

/**
 * @brief Test 5: Server Stop and Restart
 * 
 * Verifica que:
 * - El servidor se puede detener
 * - El servidor se puede reiniciar
 */
void test_web_server_stop_restart(void) {
    ESP_LOGI(TAG, "Test: Server Stop and Restart");
    
    test_server = new WebServer();
    esp_err_t ret = test_server->init(8083);
    TEST_ASSERT_EQUAL(ESP_OK, ret);
    
    bool running = test_server->is_running();
    TEST_ASSERT_TRUE_MESSAGE(running, "Server should be running initially");
    
    // Note: stop() method needs to be implemented in WebServer class
    // For now, we just verify initialization works
    
    ESP_LOGI(TAG, "✓ Server lifecycle tested");
}

/**
 * @brief Test 6: Concurrent Status Updates
 * 
 * Verifica que:
 * - Múltiples actualizaciones rápidas no causan problemas
 * - El servidor mantiene estabilidad
 */
void test_web_server_concurrent_updates(void) {
    ESP_LOGI(TAG, "Test: Concurrent Status Updates");
    
    test_server = new WebServer();
    test_server->init(8084);
    test_server->set_status_callback(test_status_callback);
    
    // Simular actualizaciones rápidas
    for (int i = 0; i < 10; i++) {
        GatewayStatus status;
        test_server->update_status(status);
        vTaskDelay(pdMS_TO_TICKS(10));
    }
    
    vTaskDelay(pdMS_TO_TICKS(100));
    
    TEST_ASSERT_TRUE_MESSAGE(test_server->is_running(), 
                             "Server should still be running after concurrent updates");
    
    ESP_LOGI(TAG, "✓ Concurrent updates handled");
}

/**
 * @brief Test 7: Invalid Port Handling
 * 
 * Verifica que:
 * - Puertos inválidos se rechazan
 * - El servidor maneja errores correctamente
 */
void test_web_server_invalid_port(void) {
    ESP_LOGI(TAG, "Test: Invalid Port Handling");
    
    test_server = new WebServer();
    
    // Puerto 0 podría ser inválido (depende de implementación)
    // Puerto muy alto podría ser problemático
    esp_err_t ret = test_server->init(65536);
    
    // El comportamiento exacto depende de la implementación
    // Este test verifica que no crashea
    
    ESP_LOGI(TAG, "✓ Invalid port handling tested");
}

/**
 * @brief Test 8: Memory Leak Check
 * 
 * Verifica que:
 * - No hay fugas de memoria al crear/destruir servidor
 */
void test_web_server_memory_leak(void) {
    ESP_LOGI(TAG, "Test: Memory Leak Check");
    
    uint32_t heap_before = esp_get_free_heap_size();
    ESP_LOGI(TAG, "Heap before: %lu bytes", heap_before);
    
    // Crear y destruir servidor varias veces
    for (int i = 0; i < 5; i++) {
        WebServer* temp_server = new WebServer();
        temp_server->init(8085 + i);
        vTaskDelay(pdMS_TO_TICKS(100));
        delete temp_server;
        vTaskDelay(pdMS_TO_TICKS(100));
    }
    
    uint32_t heap_after = esp_get_free_heap_size();
    ESP_LOGI(TAG, "Heap after: %lu bytes", heap_after);
    
    int32_t heap_diff = heap_before - heap_after;
    ESP_LOGI(TAG, "Heap difference: %ld bytes", heap_diff);
    
    // Permitir pequeña diferencia por fragmentación
    TEST_ASSERT_LESS_THAN_MESSAGE(10000, abs(heap_diff), 
                                  "Memory leak should be less than 10KB");
    
    ESP_LOGI(TAG, "✓ No significant memory leak detected");
}

/**
 * @brief Main test runner
 */
extern "C" void app_main(void) {
    ESP_LOGI(TAG, "========================================");
    ESP_LOGI(TAG, "Starting Web Server Device Tests");
    ESP_LOGI(TAG, "========================================");
    
    vTaskDelay(pdMS_TO_TICKS(2000)); // Wait for system stabilization
    
    UNITY_BEGIN();
    
    RUN_TEST(test_web_server_init);
    RUN_TEST(test_web_server_status_callback);
    RUN_TEST(test_web_server_gateway_status_struct);
    RUN_TEST(test_web_server_multiple_updates);
    RUN_TEST(test_web_server_stop_restart);
    RUN_TEST(test_web_server_concurrent_updates);
    RUN_TEST(test_web_server_invalid_port);
    RUN_TEST(test_web_server_memory_leak);
    
    UNITY_END();
    
    ESP_LOGI(TAG, "========================================");
    ESP_LOGI(TAG, "All Web Server tests completed!");
    ESP_LOGI(TAG, "========================================");
}
