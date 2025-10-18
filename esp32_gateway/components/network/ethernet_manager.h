#ifndef ETHERNET_MANAGER_H
#define ETHERNET_MANAGER_H

#include "esp_err.h"
#include "esp_event.h"

/**
 * @brief Clase para gestionar la conectividad Ethernet del ESP32
 *
 * Esta clase maneja la configuración y operación de la interfaz Ethernet,
 * incluyendo DHCP, IP estática, y eventos de conexión/desconexión.
 */
class EthernetManager {
public:
    /**
     * @brief Constructor
     */
    EthernetManager();

    /**
     * @brief Destructor
     */
    ~EthernetManager();

    /**
     * @brief Inicializar el módulo Ethernet
     * @return ESP_OK si la inicialización fue exitosa
     */
    esp_err_t init();

    /**
     * @brief Iniciar la conexión Ethernet
     * @return ESP_OK si la conexión se inició correctamente
     */
    esp_err_t start();

    /**
     * @brief Detener la conexión Ethernet
     * @return ESP_OK si se detuvo correctamente
     */
    esp_err_t stop();

    /**
     * @brief Verificar si Ethernet está conectado
     * @return true si está conectado, false en caso contrario
     */
    bool is_connected();

    /**
     * @brief Obtener la dirección IP actual
     * @return String con la dirección IP
     */
    const char* get_ip_address();

    /**
     * @brief Configurar IP estática
     * @param ip Dirección IP
     * @param gateway Gateway
     * @param netmask Máscara de red
     * @return ESP_OK si se configuró correctamente
     */
    esp_err_t set_static_ip(const char* ip, const char* gateway, const char* netmask);

    /**
     * @brief Habilitar DHCP
     * @return ESP_OK si se habilitó correctamente
     */
    esp_err_t enable_dhcp();

private:
    /**
     * @brief Manejador de eventos Ethernet
     * @param arg Argumento del evento
     * @param event_base Base del evento
     * @param event_id ID del evento
     * @param event_data Datos del evento
     */
    static void ethernet_event_handler(void* arg, esp_event_base_t event_base,
                                     int32_t event_id, void* event_data);

    /**
     * @brief Manejador de eventos IP
     * @param arg Argumento del evento
     * @param event_base Base del evento
     * @param event_id ID del evento
     * @param event_data Datos del evento
     */
    static void ip_event_handler(void* arg, esp_event_base_t event_base,
                                int32_t event_id, void* event_data);

    bool connected_;           ///< Estado de conexión
    char ip_address_[16];      ///< Dirección IP actual
    bool use_static_ip_;       ///< Flag para IP estática vs DHCP
    char static_ip_[16];       ///< IP estática configurada
    char static_gateway_[16];  ///< Gateway estático
    char static_netmask_[16];  ///< Máscara estática
};

#endif // ETHERNET_MANAGER_H