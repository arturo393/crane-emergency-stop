/**
 * @file web_server.h
 * @brief Servidor Web para monitoreo del D13 Gateway
 * 
 * Proporciona:
 * - Servidor HTTP para panel web
 * - WebSocket para datos en tiempo real
 * - API REST para configuración
 * 
 * @author D13 Gateway Team
 * @date 2025-11-01
 */

#pragma once

#include "esp_err.h"
#include "esp_http_server.h"
#include <functional>

/**
 * @brief Estructura de datos en tiempo real
 */
struct GatewayStatus {
    // CAN Status
    bool can_online;
    uint32_t can_rx_count;
    uint32_t can_tx_count;
    uint32_t can_errors;
    
    // CiA402 State
    uint8_t cia402_state;
    uint16_t status_word;
    uint16_t control_word;
    
    // Network Status
    bool eth_connected;
    char ip_address[16];
    uint16_t tcp_port;
    uint8_t clients_connected;
    
    // System Status
    uint32_t uptime_seconds;
    uint32_t free_heap;
    uint8_t cpu_usage;
    
    // SD Logger Status
    bool sd_mounted;
    uint32_t sd_total_mb;
    uint32_t sd_used_mb;
    uint8_t log_files_count;
    
    // OTA Status
    char firmware_version[32];
    char ota_partition[17];
    bool ota_pending;
};

/**
 * @brief Callback para actualizar datos del gateway
 */
using StatusUpdateCallback = std::function<void(GatewayStatus&)>;

/**
 * @brief Gestor del servidor web
 */
class WebServer {
public:
    WebServer();
    ~WebServer();

    /**
     * @brief Inicializa el servidor web
     * @param port Puerto HTTP (por defecto 80)
     * @return ESP_OK si exitoso
     */
    esp_err_t init(uint16_t port = 80);

    /**
     * @brief Detiene el servidor web
     * @return ESP_OK si exitoso
     */
    esp_err_t stop();

    /**
     * @brief Actualiza datos de estado
     * 
     * Envía datos actualizados a todos los clientes WebSocket conectados
     * 
     * @param status Datos de estado actualizados
     */
    void update_status(const GatewayStatus& status);

    /**
     * @brief Registra callback para obtener datos
     * @param callback Función que llena GatewayStatus con datos actuales
     */
    void set_status_callback(StatusUpdateCallback callback);

    /**
     * @brief Verifica si el servidor está corriendo
     * @return true si activo
     */
    bool is_running() const { return server_ != nullptr; }

private:
    httpd_handle_t server_;                 ///< Handle del servidor HTTP
    StatusUpdateCallback status_callback_;  ///< Callback para datos
    
    /**
     * @brief Registra handlers HTTP
     */
    void register_handlers();

    /**
     * @brief Handler para página principal
     */
    static esp_err_t index_handler(httpd_req_t *req);

    /**
     * @brief Handler para WebSocket
     */
    static esp_err_t ws_handler(httpd_req_t *req);

    /**
     * @brief Handler para API de estado
     */
    static esp_err_t api_status_handler(httpd_req_t *req);

    /**
     * @brief Handler para API de configuración
     */
    static esp_err_t api_config_handler(httpd_req_t *req);

    /**
     * @brief Handler para comandos OTA
     */
    static esp_err_t api_ota_handler(httpd_req_t *req);

    /**
     * @brief Envía datos de estado a través de WebSocket
     */
    void send_websocket_update();

    /**
     * @brief Construye JSON con estado del gateway
     */
    static void build_status_json(const GatewayStatus& status, char* buffer, size_t size);
};

