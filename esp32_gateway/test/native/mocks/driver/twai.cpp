#include "twai.h"
#include <stdio.h>
#include <vector>
#include <mutex>

// --- Variables globales para simular el driver ---
static bool driver_installed = false;
static std::vector<twai_message_t> tx_buffer;
static std::mutex buffer_mutex;

// --- Implementaciones Mock ---

esp_err_t twai_driver_install(const twai_general_config_t *g_config, const twai_timing_config_t *t_config, const twai_filter_config_t *f_config) {
    printf("[MOCK] twai_driver_install\n");
    driver_installed = true;
    tx_buffer.clear();
    return ESP_OK;
}

esp_err_t twai_driver_uninstall(void) {
    printf("[MOCK] twai_driver_uninstall\n");
    driver_installed = false;
    return ESP_OK;
}

esp_err_t twai_start(void) {
    printf("[MOCK] twai_start\n");
    if (!driver_installed) return ESP_ERR_INVALID_STATE;
    return ESP_OK;
}

esp_err_t twai_stop(void) {
    printf("[MOCK] twai_stop\n");
    if (!driver_installed) return ESP_ERR_INVALID_STATE;
    return ESP_OK;
}

esp_err_t twai_transmit(const twai_message_t *message, TickType_t ticks_to_wait) {
    printf("[MOCK] twai_transmit: ID=0x%03X, DLC=%d\n", message->identifier, message->data_length_code);
    if (!driver_installed) return ESP_ERR_INVALID_STATE;
    
    std::lock_guard<std::mutex> lock(buffer_mutex);
    tx_buffer.push_back(*message);
    return ESP_OK;
}

esp_err_t twai_receive(twai_message_t *message, TickType_t ticks_to_wait) {
    // No simulamos recepción por ahora, devolvemos timeout
    return ESP_ERR_TIMEOUT;
}

// --- Funciones de ayuda para tests ---
int mock_get_tx_buffer_size() {
    std::lock_guard<std::mutex> lock(buffer_mutex);
    return tx_buffer.size();
}

bool mock_get_last_tx_message(twai_message_t* msg) {
    std::lock_guard<std::mutex> lock(buffer_mutex);
    if (tx_buffer.empty()) {
        return false;
    }
    *msg = tx_buffer.back();
    return true;
}

void mock_clear_tx_buffer() {
    std::lock_guard<std::mutex> lock(buffer_mutex);
    tx_buffer.clear();
}
