#ifndef CONFIG_MANAGER_H
#define CONFIG_MANAGER_H

#include "esp_err.h"
#include <stdint.h>

/**
 * @brief Clase para gestionar configuración persistente en NVS
 * 
 * Permite almacenar y recuperar configuración del sistema:
 * - Parámetros CAN (NodeID, bitrate, pines)
 * - Credenciales WiFi/Ethernet
 * - Configuración de red (IP, gateway, etc.)
 */
class ConfigManager {
public:
    /**
     * @brief Configuración CAN
     */
    struct CANConfig {
        uint8_t node_id;          ///< Node ID CANopen (1-127)
        uint32_t bitrate;         ///< Bitrate en kbps (125, 250, 500, 1000)
        int tx_gpio;              ///< Pin GPIO para TX
        int rx_gpio;              ///< Pin GPIO para RX
    };

    /**
     * @brief Configuración WiFi
     */
    struct WiFiConfig {
        char ssid[32];            ///< SSID de la red WiFi
        char password[64];        ///< Contraseña WiFi
        bool use_dhcp;            ///< true para DHCP, false para IP estática
        char static_ip[16];       ///< IP estática (si use_dhcp = false)
        char gateway[16];         ///< Gateway (si use_dhcp = false)
        char netmask[16];         ///< Máscara de red (si use_dhcp = false)
    };

    /**
     * @brief Configuración Ethernet
     */
    struct EthernetConfig {
        bool enabled;             ///< true si Ethernet está habilitado
        uint8_t module_type;      ///< 0=W5500, 1=LAN8720
        bool use_dhcp;            ///< true para DHCP, false para IP estática
        char static_ip[16];       ///< IP estática (si use_dhcp = false)
        char gateway[16];         ///< Gateway (si use_dhcp = false)
        char netmask[16];         ///< Máscara de red (si use_dhcp = false)
        
        // Pines W5500
        int w5500_miso;
        int w5500_mosi;
        int w5500_sclk;
        int w5500_cs;
        int w5500_int;
        int w5500_rst;
        
        // Pines LAN8720
        int lan8720_phy_addr;
        int lan8720_mdc;
        int lan8720_mdio;
        int lan8720_rst;
        int lan8720_pwr;
    };

    /**
     * @brief Constructor
     */
    ConfigManager();

    /**
     * @brief Destructor
     */
    ~ConfigManager();

    /**
     * @brief Inicializar el módulo de configuración
     * @return ESP_OK si la inicialización fue exitosa
     */
    esp_err_t init();

    /**
     * @brief Cargar configuración CAN desde NVS
     * @param config Puntero a estructura para almacenar configuración
     * @return ESP_OK si se cargó correctamente
     */
    esp_err_t load_can_config(CANConfig* config);

    /**
     * @brief Guardar configuración CAN en NVS
     * @param config Configuración a guardar
     * @return ESP_OK si se guardó correctamente
     */
    esp_err_t save_can_config(const CANConfig* config);

    /**
     * @brief Cargar configuración WiFi desde NVS
     * @param config Puntero a estructura para almacenar configuración
     * @return ESP_OK si se cargó correctamente
     */
    esp_err_t load_wifi_config(WiFiConfig* config);

    /**
     * @brief Guardar configuración WiFi en NVS
     * @param config Configuración a guardar
     * @return ESP_OK si se guardó correctamente
     */
    esp_err_t save_wifi_config(const WiFiConfig* config);

    /**
     * @brief Cargar configuración Ethernet desde NVS
     * @param config Puntero a estructura para almacenar configuración
     * @return ESP_OK si se cargó correctamente
     */
    esp_err_t load_ethernet_config(EthernetConfig* config);

    /**
     * @brief Guardar configuración Ethernet en NVS
     * @param config Configuración a guardar
     * @return ESP_OK si se guardó correctamente
     */
    esp_err_t save_ethernet_config(const EthernetConfig* config);

    /**
     * @brief Restaurar configuración por defecto
     * @return ESP_OK si se restauró correctamente
     */
    esp_err_t restore_defaults();

    /**
     * @brief Borrar toda la configuración
     * @return ESP_OK si se borró correctamente
     */
    esp_err_t erase_all();

    /**
     * @brief Obtener configuración CAN por defecto
     * @param config Puntero a estructura para almacenar configuración
     */
    static void get_default_can_config(CANConfig* config);

    /**
     * @brief Obtener configuración WiFi por defecto
     * @param config Puntero a estructura para almacenar configuración
     */
    static void get_default_wifi_config(WiFiConfig* config);

    /**
     * @brief Obtener configuración Ethernet por defecto
     * @param config Puntero a estructura para almacenar configuración
     */
    static void get_default_ethernet_config(EthernetConfig* config);

private:
    /**
     * @brief Namespace NVS para la configuración
     */
    static constexpr const char* NVS_NAMESPACE = "esp32_gw";

    bool initialized_;                  ///< Estado de inicialización
};

#endif // CONFIG_MANAGER_H
