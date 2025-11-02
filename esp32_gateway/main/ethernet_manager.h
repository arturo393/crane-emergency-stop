#ifndef ETHERNET_MANAGER_H
#define ETHERNET_MANAGER_H

#include "esp_eth.h"
#include "esp_netif.h"
#include "esp_event.h"
#include "esp_err.h"

/**
 * @brief Clase para gestionar conexión Ethernet en ESP32
 *
 * Soporta módulos W5500 (SPI) y LAN8720 (RMII) con configuración
 * DHCP automática o IP estática.
 */
class EthernetManager {
public:
    /**
     * @brief Estados de la conexión Ethernet
     */
    enum EthState {
        ETH_DISCONNECTED,
        ETH_CONNECTING,
        ETH_CONNECTED,
        ETH_GOT_IP,
        ETH_ERROR
    };

    /**
     * @brief Tipos de módulos Ethernet soportados
     */
    enum EthModule {
        ETH_MODULE_W5500,    ///< Wiznet W5500 (SPI)
        ETH_MODULE_LAN8720   ///< Microchip LAN8720 (RMII)
    };

    /**
     * @brief Configuración de pines para W5500 (SPI)
     */
    struct W5500Config {
        int miso_gpio;
        int mosi_gpio;
        int sclk_gpio;
        int cs_gpio;
        int int_gpio;
        int rst_gpio;
        int spi_clock_mhz;
    };

    /**
     * @brief Configuración de pines para LAN8720 (RMII)
     */
    struct LAN8720Config {
        int phy_addr;
        int mdc_gpio;
        int mdio_gpio;
        int phy_rst_gpio;
        int phy_pwr_gpio;
    };

    /**
     * @brief Constructor
     */
    EthernetManager();

    /**
     * @brief Destructor
     */
    ~EthernetManager();

    /**
     * @brief Inicializar Ethernet con W5500
     * @param use_dhcp true para DHCP, false para IP estática
     * @return ESP_OK si la inicialización fue exitosa
     */
    esp_err_t init_w5500(bool use_dhcp = true);

    /**
     * @brief Inicializar Ethernet con LAN8720
     * @param use_dhcp true para DHCP, false para IP estática
     * @return ESP_OK si la inicialización fue exitosa
     */
    esp_err_t init_lan8720(bool use_dhcp = true);

    /**
     * @brief Configurar IP estática
     * @param ip Dirección IP
     * @param gateway Gateway
     * @param netmask Máscara de red
     * @return ESP_OK si se configuró correctamente
     */
    esp_err_t set_static_ip(const char* ip, const char* gateway, const char* netmask);

    /**
     * @brief Iniciar conexión Ethernet
     * @return ESP_OK si se inició correctamente
     */
    esp_err_t start();

    /**
     * @brief Detener conexión Ethernet
     * @return ESP_OK si se detuvo correctamente
     */
    esp_err_t stop();

    /**
     * @brief Obtener estado actual
     * @return Estado de la conexión
     */
    EthState get_state();

    /**
     * @brief Verificar si está conectado y con IP
     * @return true si está conectado
     */
    bool is_connected();

    /**
     * @brief Obtener dirección IP
     * @param ip_str Buffer para la IP (mínimo 16 bytes)
     * @return ESP_OK si se obtuvo la IP
     */
    esp_err_t get_ip(char* ip_str);

    /**
     * @brief Obtener dirección MAC
     * @param mac_str Buffer para la MAC (mínimo 18 bytes)
     * @return ESP_OK si se obtuvo la MAC
     */
    esp_err_t get_mac(char* mac_str);

    /**
     * @brief Obtener velocidad del enlace
     * @param speed Puntero para almacenar velocidad (10/100)
     * @param duplex Puntero para almacenar duplex (0=half, 1=full)
     * @return ESP_OK si se obtuvo la información
     */
    esp_err_t get_link_info(uint32_t* speed, bool* duplex);

private:
    /**
     * @brief Manejador de eventos Ethernet
     * @param arg Argumentos del usuario
     * @param event_base Base del evento
     * @param event_id ID del evento
     * @param event_data Datos del evento
     */
    static void eth_event_handler(void* arg, esp_event_base_t event_base,
                                  int32_t event_id, void* event_data);

    /**
     * @brief Manejador de eventos IP
     * @param arg Argumentos del usuario
     * @param event_base Base del evento
     * @param event_id ID del evento
     * @param event_data Datos del evento
     */
    static void ip_event_handler(void* arg, esp_event_base_t event_base,
                                int32_t event_id, void* event_data);

    EthState state_;                    ///< Estado actual
    EthModule module_;                  ///< Módulo Ethernet en uso
    bool use_dhcp_;                     ///< true para DHCP, false para IP estática
    esp_eth_handle_t eth_handle_;       ///< Handle del Ethernet
    esp_netif_t* eth_netif_;            ///< Interface de red
    esp_event_handler_instance_t eth_event_handler_instance_;
    esp_event_handler_instance_t ip_event_handler_instance_;
};

#endif // ETHERNET_MANAGER_H
