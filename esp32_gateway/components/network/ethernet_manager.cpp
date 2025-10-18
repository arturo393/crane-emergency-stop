#include "ethernet_manager.h"
#include "esp_log.h"
#include "esp_eth.h"
#include "esp_event.h"
#include "esp_netif.h"
#include "driver/gpio.h"
#include "driver/spi_master.h"
#include <string.h>

static const char *TAG = "ETHERNET_MANAGER";

EthernetManager::EthernetManager() :
    connected_(false),
    use_static_ip_(false) {
    memset(ip_address_, 0, sizeof(ip_address_));
    memset(static_ip_, 0, sizeof(static_ip_));
    memset(static_gateway_, 0, sizeof(static_gateway_));
    memset(static_netmask_, 0, sizeof(static_netmask_));
}

EthernetManager::~EthernetManager() {
    stop();
}

esp_err_t EthernetManager::init() {
    ESP_LOGI(TAG, "Inicializando Ethernet Manager...");

    // Crear interfaz de red para Ethernet
    esp_netif_config_t cfg = ESP_NETIF_DEFAULT_ETH();
    esp_netif_t *eth_netif = esp_netif_new(&cfg);

    if (eth_netif == NULL) {
        ESP_LOGE(TAG, "Error al crear interfaz Ethernet");
        return ESP_FAIL;
    }

    // Configurar Ethernet con SPI (para módulos como W5500)
    spi_bus_config_t buscfg = {
        .mosi_io_num = CONFIG_ETH_SPI_MOSI_GPIO,
        .miso_io_num = CONFIG_ETH_SPI_MISO_GPIO,
        .sclk_io_num = CONFIG_ETH_SPI_SCLK_GPIO,
        .quadwp_io_num = -1,
        .quadhd_io_num = -1,
        .max_transfer_sz = 0,
        .flags = 0,
        .intr_flags = 0
    };

    ESP_ERROR_CHECK(spi_bus_initialize(CONFIG_ETH_SPI_HOST, &buscfg, SPI_DMA_CH_AUTO));

    // Configurar dispositivo Ethernet SPI
    spi_device_interface_config_t devcfg = {
        .command_bits = 0,
        .address_bits = 0,
        .dummy_bits = 0,
        .mode = 0,
        .duty_cycle_pos = 0,
        .cs_ena_pretrans = 0,
        .cs_ena_posttrans = 0,
        .clock_speed_hz = CONFIG_ETH_SPI_CLOCK_MHZ * 1000 * 1000,
        .input_delay_ns = 0,
        .spics_io_num = CONFIG_ETH_SPI_CS_GPIO,
        .flags = 0,
        .queue_size = 0,
        .pre_cb = NULL,
        .post_cb = NULL
    };

    spi_device_handle_t spi_handle;
    ESP_ERROR_CHECK(spi_bus_add_device(CONFIG_ETH_SPI_HOST, &devcfg, &spi_handle));

    // Configurar controlador Ethernet
    eth_w5500_config_t w5500_config = ETH_W5500_DEFAULT_CONFIG(spi_handle);
    w5500_config.int_gpio_num = CONFIG_ETH_INT_GPIO;

    eth_mac_config_t mac_config = ETH_MAC_DEFAULT_CONFIG();
    esp_eth_mac_t *mac = esp_eth_mac_new_w5500(&w5500_config, &mac_config);

    eth_phy_config_t phy_config = ETH_PHY_DEFAULT_CONFIG();
    phy_config.phy_addr = CONFIG_ETH_PHY_ADDR;
    phy_config.reset_gpio_num = CONFIG_ETH_RST_GPIO;
    esp_eth_phy_t *phy = esp_eth_phy_new_w5500(&phy_config);

    esp_eth_config_t config = ETH_DEFAULT_CONFIG(mac, phy);
    esp_eth_handle_t eth_handle = NULL;
    ESP_ERROR_CHECK(esp_eth_driver_install(&config, &eth_handle));

    // Configurar eventos
    ESP_ERROR_CHECK(esp_event_handler_register(ETH_EVENT, ESP_EVENT_ANY_ID,
                                             &EthernetManager::ethernet_event_handler, this));
    ESP_ERROR_CHECK(esp_event_handler_register(IP_EVENT, ESP_EVENT_ANY_ID,
                                             &EthernetManager::ip_event_handler, this));

    // Adjuntar controlador Ethernet a la interfaz de red
    ESP_ERROR_CHECK(esp_netif_attach(eth_netif, esp_eth_new_netif_glue(eth_handle)));

    ESP_LOGI(TAG, "Ethernet Manager inicializado correctamente");
    return ESP_OK;
}

esp_err_t EthernetManager::start() {
    ESP_LOGI(TAG, "Iniciando conexión Ethernet...");

    // Configurar IP (DHCP o estática)
    if (use_static_ip_) {
        esp_netif_ip_info_t ip_info;
        ip_info.ip.addr = esp_ip4addr_aton(static_ip_);
        ip_info.gw.addr = esp_ip4addr_aton(static_gateway_);
        ip_info.netmask.addr = esp_ip4addr_aton(static_netmask_);

        ESP_ERROR_CHECK(esp_netif_set_ip_info(esp_netif_get_handle_from_ifkey("ETH_DEF"), &ip_info));
        ESP_LOGI(TAG, "IP estática configurada: %s", static_ip_);
    } else {
        ESP_ERROR_CHECK(esp_netif_dhcpc_start(esp_netif_get_handle_from_ifkey("ETH_DEF")));
        ESP_LOGI(TAG, "DHCP habilitado");
    }

    // Iniciar Ethernet
    ESP_ERROR_CHECK(esp_eth_start(esp_eth_get_handle()));

    ESP_LOGI(TAG, "Conexión Ethernet iniciada");
    return ESP_OK;
}

esp_err_t EthernetManager::stop() {
    ESP_LOGI(TAG, "Deteniendo conexión Ethernet...");

    ESP_ERROR_CHECK(esp_eth_stop(esp_eth_get_handle()));
    connected_ = false;

    ESP_LOGI(TAG, "Conexión Ethernet detenida");
    return ESP_OK;
}

bool EthernetManager::is_connected() {
    return connected_;
}

const char* EthernetManager::get_ip_address() {
    return ip_address_;
}

esp_err_t EthernetManager::set_static_ip(const char* ip, const char* gateway, const char* netmask) {
    if (ip == NULL || gateway == NULL || netmask == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    strncpy(static_ip_, ip, sizeof(static_ip_) - 1);
    strncpy(static_gateway_, gateway, sizeof(static_gateway_) - 1);
    strncpy(static_netmask_, netmask, sizeof(static_netmask_) - 1);
    use_static_ip_ = true;

    ESP_LOGI(TAG, "IP estática configurada: %s/%s/%s", ip, gateway, netmask);
    return ESP_OK;
}

esp_err_t EthernetManager::enable_dhcp() {
    use_static_ip_ = false;
    ESP_LOGI(TAG, "DHCP habilitado");
    return ESP_OK;
}

void EthernetManager::ethernet_event_handler(void* arg, esp_event_base_t event_base,
                                           int32_t event_id, void* event_data) {
    EthernetManager* manager = static_cast<EthernetManager*>(arg);

    switch (event_id) {
        case ETHERNET_EVENT_CONNECTED:
            ESP_LOGI(TAG, "Ethernet conectado");
            manager->connected_ = true;
            break;

        case ETHERNET_EVENT_DISCONNECTED:
            ESP_LOGI(TAG, "Ethernet desconectado");
            manager->connected_ = false;
            memset(manager->ip_address_, 0, sizeof(manager->ip_address_));
            break;

        case ETHERNET_EVENT_START:
            ESP_LOGI(TAG, "Ethernet iniciado");
            break;

        case ETHERNET_EVENT_STOP:
            ESP_LOGI(TAG, "Ethernet detenido");
            break;

        default:
            ESP_LOGW(TAG, "Evento Ethernet desconocido: %d", event_id);
            break;
    }
}

void EthernetManager::ip_event_handler(void* arg, esp_event_base_t event_base,
                                     int32_t event_id, void* event_data) {
    EthernetManager* manager = static_cast<EthernetManager*>(arg);

    switch (event_id) {
        case IP_EVENT_ETH_GOT_IP:
            ip_event_got_ip_t* event = (ip_event_got_ip_t*) event_data;
            ESP_LOGI(TAG, "IP obtenida: " IPSTR, IP2STR(&event->ip_info.ip));
            sprintf(manager->ip_address_, IPSTR, IP2STR(&event->ip_info.ip));
            break;

        case IP_EVENT_ETH_LOST_IP:
            ESP_LOGI(TAG, "IP perdida");
            memset(manager->ip_address_, 0, sizeof(manager->ip_address_));
            break;

        default:
            ESP_LOGW(TAG, "Evento IP desconocido: %d", event_id);
            break;
    }
}