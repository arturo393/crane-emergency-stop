#include "can_manager.h"
#include "esp_log.h"
#include "driver/twai.h"
#include "driver/gpio.h"
#include <string.h>

const char *CANManager::TAG = "CAN_MANAGER";

CANManager::CANManager() {}

CANManager::~CANManager() {
    stop();
}

esp_err_t CANManager::init(int tx_pin, int rx_pin, uint32_t bitrate) {
    ESP_LOGI(TAG, "Inicializando CAN Manager...");
    
    twai_general_config_t g_config = TWAI_GENERAL_CONFIG_DEFAULT(
        (gpio_num_t)tx_pin, 
        (gpio_num_t)rx_pin, 
        TWAI_MODE_NORMAL
    );
    twai_timing_config_t t_config = TWAI_TIMING_CONFIG_250KBITS(); // TODO: Configurable
    twai_filter_config_t f_config = TWAI_FILTER_CONFIG_ACCEPT_ALL();

    if (twai_driver_install(&g_config, &t_config, &f_config) != ESP_OK) {
        ESP_LOGE(TAG, "Fallo al instalar el driver TWAI");
        return ESP_FAIL;
    }

    if (twai_start() != ESP_OK) {
        ESP_LOGE(TAG, "Fallo al iniciar el driver TWAI");
        return ESP_FAIL;
    }

    ESP_LOGI(TAG, "CAN Manager inicializado correctamente");
    return ESP_OK;
}

esp_err_t CANManager::stop() {
    ESP_LOGI(TAG, "Deteniendo CAN Manager...");
    twai_stop();
    twai_driver_uninstall();
    return ESP_OK;
}

esp_err_t CANManager::send_message(uint32_t id, const uint8_t* data, uint8_t len) {
    if (len > 8) {
        return ESP_ERR_INVALID_ARG;
    }

    twai_message_t message;
    message.identifier = id;
    message.data_length_code = len;
    memcpy(message.data, data, len);
    message.flags = TWAI_MSG_FLAG_NONE;

    if (twai_transmit(&message, pdMS_TO_TICKS(100)) == ESP_OK) {
        return ESP_OK;
    }
    
    return ESP_FAIL;
}

esp_err_t CANManager::receive_message(twai_message_t* message, uint32_t timeout_ms) {
    if (twai_receive(message, pdMS_TO_TICKS(timeout_ms)) == ESP_OK) {
        return ESP_OK;
    }
    return ESP_ERR_TIMEOUT;
}
