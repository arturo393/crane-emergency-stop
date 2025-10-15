#include "can_manager.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "CANManager";

CANManager::CANManager() : initialized(false) {
}

CANManager::~CANManager() {
    if (initialized) {
        twai_stop();
        twai_driver_uninstall();
    }
}

esp_err_t CANManager::init(int tx_pin, int rx_pin, uint32_t bitrate) {
    ESP_LOGI(TAG, "Inicializando CAN bus");
    ESP_LOGI(TAG, "TX Pin: %d, RX Pin: %d", tx_pin, rx_pin);
    ESP_LOGI(TAG, "Bitrate: %lu bps", bitrate);
    
    // Configuración general TWAI
    twai_general_config_t g_config = TWAI_GENERAL_CONFIG_DEFAULT(
        (gpio_num_t)tx_pin, 
        (gpio_num_t)rx_pin, 
        TWAI_MODE_NORMAL
    );
    
    // Configuración de timing (250 kbps default)
    twai_timing_config_t t_config = TWAI_TIMING_CONFIG_250KBITS();
    
    // Configuración de filtros (aceptar todos)
    twai_filter_config_t f_config = TWAI_FILTER_CONFIG_ACCEPT_ALL();
    
    // Instalar driver TWAI
    esp_err_t ret = twai_driver_install(&g_config, &t_config, &f_config);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Error instalando driver TWAI: %s", esp_err_to_name(ret));
        return ret;
    }
    
    // Iniciar TWAI
    ret = twai_start();
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Error iniciando TWAI: %s", esp_err_to_name(ret));
        twai_driver_uninstall();
        return ret;
    }
    
    initialized = true;
    ESP_LOGI(TAG, "CAN bus inicializado correctamente");
    
    return ESP_OK;
}

esp_err_t CANManager::send_message(uint32_t id, const uint8_t* data, uint8_t len) {
    if (!initialized) {
        ESP_LOGE(TAG, "CAN no inicializado");
        return ESP_ERR_INVALID_STATE;
    }
    
    twai_message_t message;
    message.identifier = id;
    message.data_length_code = len;
    message.flags = TWAI_MSG_FLAG_NONE;
    
    for (int i = 0; i < len && i < 8; i++) {
        message.data[i] = data[i];
    }
    
    esp_err_t ret = twai_transmit(&message, pdMS_TO_TICKS(1000));
    if (ret == ESP_OK) {
        ESP_LOGI(TAG, "Mensaje enviado: ID=0x%lX, Len=%d", id, len);
    } else {
        ESP_LOGE(TAG, "Error enviando mensaje: %s", esp_err_to_name(ret));
    }
    
    return ret;
}

esp_err_t CANManager::receive_message(twai_message_t* message, uint32_t timeout_ms) {
    if (!initialized) {
        return ESP_ERR_INVALID_STATE;
    }
    
    return twai_receive(message, pdMS_TO_TICKS(timeout_ms));
}

esp_err_t CANManager::send_heartbeat(uint8_t node_id) {
    // Heartbeat CANopen: COB-ID = 0x700 + Node ID
    uint32_t cob_id = 0x700 + node_id;
    uint8_t data[1] = {0x05}; // Estado: Operational
    
    return send_message(cob_id, data, 1);
}

void CANManager::start_receive_task() {
    xTaskCreate(receive_task, "can_receive", 4096, this, 5, NULL);
}

void CANManager::receive_task(void* arg) {
    CANManager* self = (CANManager*)arg;
    twai_message_t message;
    
    ESP_LOGI(TAG, "Tarea de recepción CAN iniciada");
    
    while (1) {
        esp_err_t ret = self->receive_message(&message, 1000);
        
        if (ret == ESP_OK) {
            ESP_LOGI(TAG, "Mensaje recibido: ID=0x%lX, Len=%d", 
                     message.identifier, message.data_length_code);
            
            // TODO: Procesar mensaje según protocolo CANopen
        }
        
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}
