#pragma once

#include "esp_err.h"
#include "driver/twai.h"

/**
 * @brief Clase para gestionar comunicación CAN/TWAI
 * 
 * Funcionalidades:
 * - Driver TWAI (CAN 2.0) para ESP32-S3
 * - Protocolo CANopen básico
 * - Buffer de mensajes con FreeRTOS
 * - Heartbeat y monitoreo
 */
class CANManager {
public:
    CANManager();
    ~CANManager();
    
    /**
     * @brief Inicializar CAN bus
     * @param tx_pin GPIO para TX
     * @param rx_pin GPIO para RX
     * @param bitrate Velocidad en bps (default: 250000)
     * @return ESP_OK si exitoso
     */
    esp_err_t init(int tx_pin, int rx_pin, uint32_t bitrate = 250000);
    
    /**
     * @brief Enviar mensaje CAN
     * @param id ID del mensaje
     * @param data Datos a enviar
     * @param len Longitud de datos
     * @return ESP_OK si exitoso
     */
    esp_err_t send_message(uint32_t id, const uint8_t* data, uint8_t len);
    
    /**
     * @brief Recibir mensaje CAN (bloqueante)
     * @param message Estructura para recibir mensaje
     * @param timeout_ms Timeout en milisegundos
     * @return ESP_OK si exitoso
     */
    esp_err_t receive_message(twai_message_t* message, uint32_t timeout_ms);
    
    /**
     * @brief Enviar heartbeat CANopen
     * @param node_id ID del nodo
     * @return ESP_OK si exitoso
     */
    esp_err_t send_heartbeat(uint8_t node_id);
    
    /**
     * @brief Iniciar tarea de recepción en background
     */
    void start_receive_task();
    
private:
    bool initialized;
    
    static void receive_task(void* arg);
};
