#include "ethernet_manager.h"
#include "hardware_config.h" // Centralized pin definitions
#include "esp_log.h"
#include "esp_mac.h"
#include "driver/gpio.h"
#include "driver/spi_master.h"
#include "esp_eth_driver.h"
#include "esp_eth_mac.h"
#include "esp_eth_phy.h"
#include <string.h>

static const char *TAG = "ETH_MANAGER";


EthernetManager::EthernetManager() :
    state_(ETH_DISCONNECTED),
    module_(ETH_MODULE_W5500),
    use_dhcp_(true),
    eth_handle_(nullptr),
    eth_netif_(nullptr),
    eth_event_handler_instance_(nullptr),
    ip_event_handler_instance_(nullptr) {
}

EthernetManager::~EthernetManager() {
    stop();
}

esp_err_t EthernetManager::init_w5500(bool use_dhcp) {
    ESP_LOGI(TAG, "Inicializando Ethernet W5500...");
    
    module_ = ETH_MODULE_W5500;
    use_dhcp_ = use_dhcp;
    state_ = ETH_CONNECTING;

    // 1. Inicializar TCP/IP stack y event loop
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());

    // 2. Crear netif para Ethernet
    esp_netif_config_t cfg = ESP_NETIF_DEFAULT_ETH();
    eth_netif_ = esp_netif_new(&cfg);

    // 3. Configurar bus SPI (usando pines de hardware_config.h)
    spi_bus_config_t buscfg = {
        .mosi_io_num = PIN_ETH_SPI_MOSI,
        .miso_io_num = PIN_ETH_SPI_MISO,
        .sclk_io_num = PIN_ETH_SPI_SCLK,
        .quadwp_io_num = -1,
        .quadhd_io_num = -1,
    };
    ESP_ERROR_CHECK(spi_bus_initialize(SPI2_HOST, &buscfg, SPI_DMA_CH_AUTO));

    // 4. Configurar SPI device para W5500
    spi_device_interface_config_t devcfg = {
        .command_bits = 16,
        .address_bits = 8,
        .mode = 0,
        .clock_speed_hz = 20 * 1000 * 1000, // 20 MHz
        .spics_io_num = PIN_ETH_CS,
        .queue_size = 20
    };

    // 5. Configurar W5500
    eth_w5500_config_t w5500_config = ETH_W5500_DEFAULT_CONFIG(SPI2_HOST, &devcfg);
    w5500_config.int_gpio_num = PIN_ETH_INT;

    // 6. Configurar MAC y PHY
    eth_mac_config_t mac_config = ETH_MAC_DEFAULT_CONFIG();
    eth_phy_config_t phy_config = ETH_PHY_DEFAULT_CONFIG();
    phy_config.phy_addr = -1; // W5500 no tiene dirección PHY
    phy_config.reset_gpio_num = PIN_ETH_RST;

    esp_eth_mac_t *mac = esp_eth_mac_new_w5500(&w5500_config, &mac_config);
    esp_eth_phy_t *phy = esp_eth_phy_new_w5500(&phy_config);

    // 6. Instalar driver Ethernet
    esp_eth_config_t eth_config = ETH_DEFAULT_CONFIG(mac, phy);
    ESP_ERROR_CHECK(esp_eth_driver_install(&eth_config, &eth_handle_));

    // 7. Adjuntar netif al driver
    ESP_ERROR_CHECK(esp_netif_attach(eth_netif_, esp_eth_new_netif_glue(eth_handle_)));

    // 8. Registrar manejadores de eventos
    ESP_ERROR_CHECK(esp_event_handler_instance_register(ETH_EVENT, ESP_EVENT_ANY_ID,
                    &eth_event_handler, this, &eth_event_handler_instance_));
    ESP_ERROR_CHECK(esp_event_handler_instance_register(IP_EVENT, IP_EVENT_ETH_GOT_IP,
                    &ip_event_handler, this, &ip_event_handler_instance_));

    ESP_LOGI(TAG, "W5500 inicializado correctamente. Iniciando driver...");
    return start();
}

esp_err_t EthernetManager::init_lan8720(bool use_dhcp) {
    // Esta implementación es para otro tipo de hardware y no se usa en EdgeBox-Lite
    ESP_LOGE(TAG, "LAN8720 no es soportado por este hardware.");
    return ESP_ERR_NOT_SUPPORTED;
}


esp_err_t EthernetManager::set_static_ip(const char* ip, const char* gateway, const char* netmask) {
    if (ip == nullptr || gateway == nullptr || netmask == nullptr) {
        return ESP_ERR_INVALID_ARG;
    }

    ESP_LOGI(TAG, "Configurando IP estática: %s", ip);

    // Detener DHCP si está activo
    esp_netif_dhcpc_stop(eth_netif_);

    // Configurar IP estática
    esp_netif_ip_info_t ip_info;
    ip_info.ip.addr = esp_ip4addr_aton(ip);
    ip_info.gw.addr = esp_ip4addr_aton(gateway);
    ip_info.netmask.addr = esp_ip4addr_aton(netmask);

    esp_err_t err = esp_netif_set_ip_info(eth_netif_, &ip_info);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Error al configurar IP estática: %s", esp_err_to_name(err));
        return err;
    }

    use_dhcp_ = false;
    ESP_LOGI(TAG, "IP estática configurada correctamente");
    return ESP_OK;
}

esp_err_t EthernetManager::start() {
    ESP_LOGI(TAG, "Iniciando Ethernet...");
    
    if (eth_handle_ == nullptr) {
        ESP_LOGE(TAG, "Ethernet no inicializado");
        return ESP_ERR_INVALID_STATE;
    }

    esp_err_t err = esp_eth_start(eth_handle_);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Error al iniciar Ethernet: %s", esp_err_to_name(err));
        state_ = ETH_ERROR;
        return err;
    }

    ESP_LOGI(TAG, "Ethernet iniciado");
    return ESP_OK;
}

esp_err_t EthernetManager::stop() {
    if (eth_handle_ == nullptr) {
        return ESP_OK;
    }

    ESP_LOGI(TAG, "Deteniendo Ethernet...");

    esp_eth_stop(eth_handle_);
    
    if (eth_event_handler_instance_) {
        esp_event_handler_instance_unregister(ETH_EVENT, ESP_EVENT_ANY_ID, 
                                             eth_event_handler_instance_);
    }
    
    if (ip_event_handler_instance_) {
        esp_event_handler_instance_unregister(IP_EVENT, IP_EVENT_ETH_GOT_IP, 
                                             ip_event_handler_instance_);
    }

    if (eth_netif_) {
        esp_netif_destroy(eth_netif_);
        eth_netif_ = nullptr;
    }

    if (eth_handle_) {
        esp_eth_driver_uninstall(eth_handle_);
        eth_handle_ = nullptr;
    }

    state_ = ETH_DISCONNECTED;
    ESP_LOGI(TAG, "Ethernet detenido");
    return ESP_OK;
}

EthernetManager::EthState EthernetManager::get_state() {
    return state_;
}

bool EthernetManager::is_connected() {
    return state_ == ETH_GOT_IP;
}

esp_err_t EthernetManager::get_ip(char* ip_str) {
    if (ip_str == nullptr) {
        return ESP_ERR_INVALID_ARG;
    }

    if (eth_netif_ == nullptr) {
        return ESP_ERR_INVALID_STATE;
    }

    esp_netif_ip_info_t ip_info;
    esp_err_t err = esp_netif_get_ip_info(eth_netif_, &ip_info);
    if (err != ESP_OK) {
        return err;
    }

    sprintf(ip_str, IPSTR, IP2STR(&ip_info.ip));
    return ESP_OK;
}

esp_err_t EthernetManager::get_mac(char* mac_str) {
    if (mac_str == nullptr) {
        return ESP_ERR_INVALID_ARG;
    }

    if (eth_handle_ == nullptr) {
        return ESP_ERR_INVALID_STATE;
    }

    uint8_t mac[6];
    esp_err_t err = esp_eth_ioctl(eth_handle_, ETH_CMD_G_MAC_ADDR, mac);
    if (err != ESP_OK) {
        return err;
    }

    sprintf(mac_str, "%02x:%02x:%02x:%02x:%02x:%02x",
            mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
    return ESP_OK;
}

esp_err_t EthernetManager::get_link_info(uint32_t* speed, bool* duplex) {
    if (speed == nullptr || duplex == nullptr) {
        return ESP_ERR_INVALID_ARG;
    }

    if (eth_handle_ == nullptr) {
        return ESP_ERR_INVALID_STATE;
    }

    eth_speed_t eth_speed;
    eth_duplex_t eth_duplex;

    esp_err_t err = esp_eth_ioctl(eth_handle_, ETH_CMD_G_SPEED, &eth_speed);
    if (err != ESP_OK) {
        return err;
    }

    err = esp_eth_ioctl(eth_handle_, ETH_CMD_G_DUPLEX_MODE, &eth_duplex);
    if (err != ESP_OK) {
        return err;
    }

    *speed = (eth_speed == ETH_SPEED_10M) ? 10 : 100;
    *duplex = (eth_duplex == ETH_DUPLEX_FULL);

    return ESP_OK;
}

void EthernetManager::eth_event_handler(void* arg, esp_event_base_t event_base,
                                       int32_t event_id, void* event_data) {
    EthernetManager* manager = static_cast<EthernetManager*>(arg);

    switch (event_id) {
        case ETHERNET_EVENT_CONNECTED:
            ESP_LOGI(TAG, "Ethernet conectado");
            manager->state_ = ETH_CONNECTED;
            break;

        case ETHERNET_EVENT_DISCONNECTED:
            ESP_LOGI(TAG, "Ethernet desconectado");
            manager->state_ = ETH_DISCONNECTED;
            break;

        case ETHERNET_EVENT_START:
            ESP_LOGI(TAG, "Ethernet iniciado");
            break;

        case ETHERNET_EVENT_STOP:
            ESP_LOGI(TAG, "Ethernet detenido");
            manager->state_ = ETH_DISCONNECTED;
            break;

        default:
            break;
    }
}

void EthernetManager::ip_event_handler(void* arg, esp_event_base_t event_base,
                                      int32_t event_id, void* event_data) {
    EthernetManager* manager = static_cast<EthernetManager*>(arg);

    if (event_id == IP_EVENT_ETH_GOT_IP) {
        ip_event_got_ip_t* event = (ip_event_got_ip_t*) event_data;
        ESP_LOGI(TAG, "Ethernet obtuvo IP: " IPSTR, IP2STR(&event->ip_info.ip));
        ESP_LOGI(TAG, "Gateway: " IPSTR, IP2STR(&event->ip_info.gw));
        ESP_LOGI(TAG, "Netmask: " IPSTR, IP2STR(&event->ip_info.netmask));
        manager->state_ = ETH_GOT_IP;
    }
}
