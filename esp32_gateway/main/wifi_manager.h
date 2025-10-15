#pragma once

#include "esp_err.h"
#include "esp_wifi.h"

/**
 * @brief Clase para gestionar conexión WiFi
 * 
 * Funcionalidades:
 * - Modo cliente (STA) con DHCP
 * - Modo Access Point (AP) para configuración
 * - Reconnect automático
 * - Configuración IP estática opcional
 */
class WiFiManager {
public:
    WiFiManager();
    ~WiFiManager();
    
    /**
     * @brief Inicializar WiFi en modo cliente
     * @param ssid SSID de la red
     * @param password Contraseña de la red
     * @param use_dhcp true para DHCP, false para IP estática
     * @return ESP_OK si exitoso
     */
    esp_err_t init_sta(const char* ssid, const char* password, bool use_dhcp = true);
    
    /**
     * @brief Inicializar WiFi en modo Access Point
     * @param ssid SSID del AP
     * @param password Contraseña del AP
     * @return ESP_OK si exitoso
     */
    esp_err_t init_ap(const char* ssid, const char* password);
    
    /**
     * @brief Verificar si está conectado
     * @return true si conectado
     */
    bool is_connected();
    
    /**
     * @brief Obtener IP asignada
     * @return Dirección IP como string
     */
    const char* get_ip_address();
    
private:
    bool connected;
    char ip_address[16];
    
    static void wifi_event_handler(void* arg, esp_event_base_t event_base,
                                   int32_t event_id, void* event_data);
};
