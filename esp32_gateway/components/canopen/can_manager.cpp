#include "can_manager.h"
#include "esp_log.h"
#include "driver/gpio.h"
#include <string.h>

static const char *TAG = "CAN_MANAGER";

CANManager::CANManager() :
    state_(CAN_STOPPED),
    rx_queue_(NULL),
    rx_task_(NULL),
    tx_count_(0),
    rx_count_(0),
    error_count_(0),
    tx_pin_(GPIO_NUM_21),
    rx_pin_(GPIO_NUM_22) {

    // Configuración por defecto: 250kbps (estándar CANopen)
    timing_config_ = TWAI_TIMING_CONFIG_250KBITS();

    // Filtro por defecto: aceptar todos los mensajes
    filter_config_ = TWAI_FILTER_CONFIG_ACCEPT_ALL();
}

CANManager::~CANManager() {
    stop();
}

esp_err_t CANManager::init(gpio_num_t tx_pin, gpio_num_t rx_pin) {
    ESP_LOGI(TAG, "Inicializando CAN Manager...");

    tx_pin_ = tx_pin;
    rx_pin_ = rx_pin;

    // Configurar pines GPIO
    configure_pins(tx_pin_, rx_pin_);

    // Crear cola para mensajes RX
    rx_queue_ = xQueueCreate(10, sizeof(twai_message_t));
    if (rx_queue_ == NULL) {
        ESP_LOGE(TAG, "Error creando cola RX");
        return ESP_ERR_NO_MEM;
    }

    ESP_LOGI(TAG, "CAN Manager inicializado correctamente (TX:%d, RX:%d)", tx_pin_, rx_pin_);
    return ESP_OK;
}

esp_err_t CANManager::start() {
    ESP_LOGI(TAG, "Iniciando comunicación CAN...");
    state_ = CAN_STARTING;

    esp_err_t ret = install_driver();
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Error instalando driver CAN: %s", esp_err_to_name(ret));
        state_ = CAN_ERROR;
        return ret;
    }

    // Iniciar tarea de recepción
    BaseType_t task_ret = xTaskCreate(
        can_receive_task,
        "can_rx_task",
        4096,
        this,
        10,
        &rx_task_
    );

    if (task_ret != pdPASS) {
        ESP_LOGE(TAG, "Error creando tarea RX");
        uninstall_driver();
        state_ = CAN_ERROR;
        return ESP_ERR_NO_MEM;
    }

    state_ = CAN_RUNNING;
    ESP_LOGI(TAG, "Comunicación CAN iniciada correctamente");
    return ESP_OK;
}

esp_err_t CANManager::stop() {
    ESP_LOGI(TAG, "Deteniendo comunicación CAN...");

    if (rx_task_ != NULL) {
        vTaskDelete(rx_task_);
        rx_task_ = NULL;
    }

    esp_err_t ret = uninstall_driver();

    if (rx_queue_ != NULL) {
        vQueueDelete(rx_queue_);
        rx_queue_ = NULL;
    }

    state_ = CAN_STOPPED;
    ESP_LOGI(TAG, "Comunicación CAN detenida");
    return ret;
}

CANManager::CANState CANManager::get_state() {
    return state_;
}

bool CANManager::is_connected() {
    if (state_ != CAN_RUNNING) {
        return false;
    }

    // Verificar estado del bus CAN
    twai_status_info_t status_info;
    esp_err_t ret = twai_get_status_info(&status_info);

    if (ret != ESP_OK) {
        return false;
    }

    // Considerar conectado si no hay errores críticos
    return (status_info.state == TWAI_STATE_RUNNING ||
            status_info.state == TWAI_STATE_BUS_OFF) &&
           (status_info.bus_error_count < 100);
}

esp_err_t CANManager::send_message(uint32_t identifier, const uint8_t* data, size_t data_len) {
    if (state_ != CAN_RUNNING) {
        return ESP_ERR_INVALID_STATE;
    }

    if (data_len > 8) {
        return ESP_ERR_INVALID_SIZE;
    }

    twai_message_t message = {
        .identifier = identifier,
        .data_length_code = data_len,
        .data = {0}
    };

    if (data != NULL && data_len > 0) {
        memcpy(message.data, data, data_len);
    }

    esp_err_t ret = twai_transmit(&message, pdMS_TO_TICKS(100));
    if (ret == ESP_OK) {
        tx_count_++;
        ESP_LOGD(TAG, "Mensaje enviado: ID=0x%03X, DLC=%d", identifier, data_len);
    } else {
        error_count_++;
        ESP_LOGW(TAG, "Error enviando mensaje: %s", esp_err_to_name(ret));
    }

    return ret;
}

esp_err_t CANManager::receive_message(twai_message_t* message) {
    if (state_ != CAN_RUNNING || rx_queue_ == NULL || message == NULL) {
        return ESP_ERR_INVALID_STATE;
    }

    if (xQueueReceive(rx_queue_, message, 0) == pdTRUE) {
        rx_count_++;
        ESP_LOGD(TAG, "Mensaje recibido: ID=0x%03X, DLC=%d", message->identifier, message->data_length_code);
        return ESP_OK;
    }

    return ESP_ERR_TIMEOUT;
}

esp_err_t CANManager::set_bitrate(uint32_t bitrate) {
    if (state_ == CAN_RUNNING) {
        ESP_LOGE(TAG, "No se puede cambiar bitrate mientras CAN está corriendo");
        return ESP_ERR_INVALID_STATE;
    }

    switch (bitrate) {
        case 125000:
            timing_config_ = TWAI_TIMING_CONFIG_125KBITS();
            break;
        case 250000:
            timing_config_ = TWAI_TIMING_CONFIG_250KBITS();
            break;
        case 500000:
            timing_config_ = TWAI_TIMING_CONFIG_500KBITS();
            break;
        case 1000000:
            timing_config_ = TWAI_TIMING_CONFIG_1MBITS();
            break;
        default:
            ESP_LOGE(TAG, "Bitrate no soportado: %u", bitrate);
            return ESP_ERR_INVALID_ARG;
    }

    ESP_LOGI(TAG, "Bitrate configurado: %u bps", bitrate);
    return ESP_OK;
}

void CANManager::get_stats(uint32_t* tx_count, uint32_t* rx_count, uint32_t* error_count) {
    if (tx_count) *tx_count = tx_count_;
    if (rx_count) *rx_count = rx_count_;
    if (error_count) *error_count = error_count_;
}

void CANManager::clear_stats() {
    tx_count_ = 0;
    rx_count_ = 0;
    error_count_ = 0;
    ESP_LOGI(TAG, "Estadísticas limpiadas");
}

void CANManager::can_receive_task(void* arg) {
    CANManager* manager = static_cast<CANManager*>(arg);

    ESP_LOGI(TAG, "Tarea de recepción CAN iniciada");

    while (manager->state_ == CAN_RUNNING) {
        twai_message_t message;

        // Esperar mensaje con timeout
        esp_err_t ret = twai_receive(&message, pdMS_TO_TICKS(100));

        if (ret == ESP_OK) {
            // Enviar a cola (no bloqueante)
            if (xQueueSend(manager->rx_queue_, &message, 0) != pdTRUE) {
                ESP_LOGW(TAG, "Cola RX llena, mensaje descartado");
                manager->error_count_++;
            }
        } else if (ret == ESP_ERR_TIMEOUT) {
            // Timeout normal, continuar
            continue;
        } else {
            ESP_LOGW(TAG, "Error recibiendo mensaje CAN: %s", esp_err_to_name(ret));
            manager->error_count_++;

            // Pequeña pausa para evitar spam de logs
            vTaskDelay(pdMS_TO_TICKS(10));
        }
    }

    ESP_LOGI(TAG, "Tarea de recepción CAN terminada");
    vTaskDelete(NULL);
}

void CANManager::configure_pins(gpio_num_t tx_pin, gpio_num_t rx_pin) {
    ESP_LOGI(TAG, "Configurando pines CAN: TX=%d, RX=%d", tx_pin, rx_pin);

    // Configurar pines como entrada/salida
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << tx_pin) | (1ULL << rx_pin),
        .mode = GPIO_MODE_INPUT_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };

    gpio_config(&io_conf);

    // Configurar como pines TWAI
    gpio_set_level(tx_pin, 1);  // TX idle high
    gpio_set_level(rx_pin, 0);  // RX input
}

esp_err_t CANManager::install_driver() {
    twai_general_config_t g_config = TWAI_GENERAL_CONFIG_DEFAULT(tx_pin_, rx_pin_, TWAI_MODE_NORMAL);

    twai_config_t twai_config = {
        .timing_config = timing_config_,
        .filter_config = filter_config_,
        .rx_queue_len = 10,
        .tx_queue_len = 10,
        .alerts_enabled = TWAI_ALERT_ALL,
        .clkout_divider = 0
    };

    esp_err_t ret = twai_driver_install(&g_config, &twai_config, 0);
    if (ret != ESP_OK) {
        return ret;
    }

    return twai_start();
}

esp_err_t CANManager::uninstall_driver() {
    esp_err_t ret = twai_stop();
    if (ret != ESP_OK) {
        ESP_LOGW(TAG, "Error deteniendo TWAI: %s", esp_err_to_name(ret));
    }

    ret = twai_driver_uninstall();
    if (ret != ESP_OK) {
        ESP_LOGW(TAG, "Error desinstalando driver TWAI: %s", esp_err_to_name(ret));
    }

    return ret;
}