#ifndef CAN_MANAGER_H
#define CAN_MANAGER_H

#include "esp_err.h"
#include "driver/twai.h"
#include <freertos/FreeRTOS.h>
#include <freertos/queue.h>

/**
 * @brief Clase para gestionar la comunicación CAN del ESP32
 *
 * Esta clase maneja la configuración del controlador CAN/TWAI,
 * recepción y transmisión de mensajes, y integración con CANopen.
 */
class CANManager {
public:
    /**
     * @brief Estados del CAN Manager
     */
    enum CANState {
        CAN_STOPPED,
        CAN_STARTING,
        CAN_RUNNING,
        CAN_ERROR
    };

    /**
     * @brief Constructor
     */
    CANManager();

    /**
     * @brief Destructor
     */
    ~CANManager();

    /**
     * @brief Inicializar el módulo CAN
     * @param tx_pin Pin TX del CAN
     * @param rx_pin Pin RX del CAN
     * @return ESP_OK si la inicialización fue exitosa
     */
    esp_err_t init(gpio_num_t tx_pin = GPIO_NUM_21, gpio_num_t rx_pin = GPIO_NUM_22);

    /**
     * @brief Iniciar la comunicación CAN
     * @return ESP_OK si se inició correctamente
     */
    esp_err_t start();

    /**
     * @brief Detener la comunicación CAN
     * @return ESP_OK si se detuvo correctamente
     */
    esp_err_t stop();

    /**
     * @brief Obtener estado actual del CAN
     * @return Estado del CAN Manager
     */
    CANState get_state();

    /**
     * @brief Verificar si CAN está conectado
     * @return true si está conectado
     */
    bool is_connected();

    /**
     * @brief Enviar mensaje CAN
     * @param identifier ID del mensaje
     * @param data Datos del mensaje
     * @param data_len Longitud de los datos (0-8)
     * @return ESP_OK si se envió correctamente
     */
    esp_err_t send_message(uint32_t identifier, const uint8_t* data, size_t data_len);

    /**
     * @brief Recibir mensaje CAN (no bloqueante)
     * @param message Puntero a estructura para almacenar el mensaje
     * @return ESP_OK si se recibió un mensaje
     */
    esp_err_t receive_message(twai_message_t* message);

    /**
     * @brief Configurar bitrate del CAN
     * @param bitrate Bitrate en bps (125000, 250000, 500000, 1000000)
     * @return ESP_OK si se configuró correctamente
     */
    esp_err_t set_bitrate(uint32_t bitrate);

    /**
     * @brief Obtener estadísticas del CAN
     * @param tx_count Número de mensajes transmitidos
     * @param rx_count Número de mensajes recibidos
     * @param error_count Número de errores
     */
    void get_stats(uint32_t* tx_count, uint32_t* rx_count, uint32_t* error_count);

    /**
     * @brief Limpiar estadísticas
     */
    void clear_stats();

private:
    /**
     * @brief Tarea de recepción de mensajes CAN
     * @param arg Argumento de la tarea
     */
    static void can_receive_task(void* arg);

    /**
     * @brief Configurar pines GPIO para CAN
     * @param tx_pin Pin TX
     * @param rx_pin Pin RX
     */
    void configure_pins(gpio_num_t tx_pin, gpio_num_t rx_pin);

    /**
     * @brief Instalar controlador TWAI
     * @return ESP_OK si se instaló correctamente
     */
    esp_err_t install_driver();

    /**
     * @brief Desinstalar controlador TWAI
     * @return ESP_OK si se desinstaló correctamente
     */
    esp_err_t uninstall_driver();

    CANState state_;                    ///< Estado actual del CAN
    twai_timing_config_t timing_config_; ///< Configuración de timing
    twai_filter_config_t filter_config_; ///< Configuración de filtro
    QueueHandle_t rx_queue_;            ///< Cola de mensajes RX
    TaskHandle_t rx_task_;              ///< Handle de la tarea RX

    // Estadísticas
    uint32_t tx_count_;                 ///< Contador de TX
    uint32_t rx_count_;                 ///< Contador de RX
    uint32_t error_count_;              ///< Contador de errores

    // Configuración de pines
    gpio_num_t tx_pin_;                 ///< Pin TX configurado
    gpio_num_t rx_pin_;                 ///< Pin RX configurado
};

#endif // CAN_MANAGER_H