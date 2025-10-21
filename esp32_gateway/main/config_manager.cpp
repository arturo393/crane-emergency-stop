#include "config_manager.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "nvs.h"
#include <string.h>

static const char *TAG = "CONFIG_MGR";

ConfigManager::ConfigManager() : initialized_(false) {
}

ConfigManager::~ConfigManager() {
}

esp_err_t ConfigManager::init() {
    ESP_LOGI(TAG, "Inicializando Config Manager...");
    
    initialized_ = true;
    ESP_LOGI(TAG, "Config Manager inicializado");
    return ESP_OK;
}

esp_err_t ConfigManager::load_can_config(CANConfig* config) {
    if (!initialized_ || config == nullptr) {
        return ESP_ERR_INVALID_STATE;
    }

    nvs_handle_t handle;
    esp_err_t err = nvs_open(NVS_NAMESPACE, NVS_READONLY, &handle);
    if (err != ESP_OK) {
        ESP_LOGW(TAG, "No se pudo abrir NVS, usando configuración por defecto");
        get_default_can_config(config);
        return ESP_ERR_NVS_NOT_FOUND;
    }

    size_t required_size = sizeof(CANConfig);
    err = nvs_get_blob(handle, "can_config", config, &required_size);
    
    if (err != ESP_OK) {
        ESP_LOGW(TAG, "Configuración CAN no encontrada, usando valores por defecto");
        get_default_can_config(config);
        nvs_close(handle);
        return ESP_ERR_NVS_NOT_FOUND;
    }

    nvs_close(handle);
    ESP_LOGI(TAG, "Configuración CAN cargada: NodeID=0x%02X, Bitrate=%d kbps", 
             config->node_id, config->bitrate);
    return ESP_OK;
}

esp_err_t ConfigManager::save_can_config(const CANConfig* config) {
    if (!initialized_ || config == nullptr) {
        return ESP_ERR_INVALID_STATE;
    }

    nvs_handle_t handle;
    esp_err_t err = nvs_open(NVS_NAMESPACE, NVS_READWRITE, &handle);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Error al abrir NVS: %s", esp_err_to_name(err));
        return err;
    }

    err = nvs_set_blob(handle, "can_config", config, sizeof(CANConfig));
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Error al guardar configuración CAN: %s", esp_err_to_name(err));
        nvs_close(handle);
        return err;
    }

    err = nvs_commit(handle);
    nvs_close(handle);

    if (err == ESP_OK) {
        ESP_LOGI(TAG, "Configuración CAN guardada correctamente");
    }
    return err;
}

esp_err_t ConfigManager::load_wifi_config(WiFiConfig* config) {
    if (!initialized_ || config == nullptr) {
        return ESP_ERR_INVALID_STATE;
    }

    nvs_handle_t handle;
    esp_err_t err = nvs_open(NVS_NAMESPACE, NVS_READONLY, &handle);
    if (err != ESP_OK) {
        ESP_LOGW(TAG, "No se pudo abrir NVS, usando configuración WiFi por defecto");
        get_default_wifi_config(config);
        return ESP_ERR_NVS_NOT_FOUND;
    }

    size_t required_size = sizeof(WiFiConfig);
    err = nvs_get_blob(handle, "wifi_config", config, &required_size);
    
    if (err != ESP_OK) {
        ESP_LOGW(TAG, "Configuración WiFi no encontrada, usando valores por defecto");
        get_default_wifi_config(config);
        nvs_close(handle);
        return ESP_ERR_NVS_NOT_FOUND;
    }

    nvs_close(handle);
    ESP_LOGI(TAG, "Configuración WiFi cargada: SSID=%s", config->ssid);
    return ESP_OK;
}

esp_err_t ConfigManager::save_wifi_config(const WiFiConfig* config) {
    if (!initialized_ || config == nullptr) {
        return ESP_ERR_INVALID_STATE;
    }

    nvs_handle_t handle;
    esp_err_t err = nvs_open(NVS_NAMESPACE, NVS_READWRITE, &handle);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Error al abrir NVS: %s", esp_err_to_name(err));
        return err;
    }

    err = nvs_set_blob(handle, "wifi_config", config, sizeof(WiFiConfig));
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Error al guardar configuración WiFi: %s", esp_err_to_name(err));
        nvs_close(handle);
        return err;
    }

    err = nvs_commit(handle);
    nvs_close(handle);

    if (err == ESP_OK) {
        ESP_LOGI(TAG, "Configuración WiFi guardada correctamente");
    }
    return err;
}

esp_err_t ConfigManager::load_ethernet_config(EthernetConfig* config) {
    if (!initialized_ || config == nullptr) {
        return ESP_ERR_INVALID_STATE;
    }

    nvs_handle_t handle;
    esp_err_t err = nvs_open(NVS_NAMESPACE, NVS_READONLY, &handle);
    if (err != ESP_OK) {
        ESP_LOGW(TAG, "No se pudo abrir NVS, usando configuración Ethernet por defecto");
        get_default_ethernet_config(config);
        return ESP_ERR_NVS_NOT_FOUND;
    }

    size_t required_size = sizeof(EthernetConfig);
    err = nvs_get_blob(handle, "eth_config", config, &required_size);
    
    if (err != ESP_OK) {
        ESP_LOGW(TAG, "Configuración Ethernet no encontrada, usando valores por defecto");
        get_default_ethernet_config(config);
        nvs_close(handle);
        return ESP_ERR_NVS_NOT_FOUND;
    }

    nvs_close(handle);
    ESP_LOGI(TAG, "Configuración Ethernet cargada: Habilitado=%d, Módulo=%d", 
             config->enabled, config->module_type);
    return ESP_OK;
}

esp_err_t ConfigManager::save_ethernet_config(const EthernetConfig* config) {
    if (!initialized_ || config == nullptr) {
        return ESP_ERR_INVALID_STATE;
    }

    nvs_handle_t handle;
    esp_err_t err = nvs_open(NVS_NAMESPACE, NVS_READWRITE, &handle);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Error al abrir NVS: %s", esp_err_to_name(err));
        return err;
    }

    err = nvs_set_blob(handle, "eth_config", config, sizeof(EthernetConfig));
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Error al guardar configuración Ethernet: %s", esp_err_to_name(err));
        nvs_close(handle);
        return err;
    }

    err = nvs_commit(handle);
    nvs_close(handle);

    if (err == ESP_OK) {
        ESP_LOGI(TAG, "Configuración Ethernet guardada correctamente");
    }
    return err;
}

esp_err_t ConfigManager::restore_defaults() {
    ESP_LOGI(TAG, "Restaurando configuración por defecto...");

    CANConfig can_cfg;
    WiFiConfig wifi_cfg;
    EthernetConfig eth_cfg;

    get_default_can_config(&can_cfg);
    get_default_wifi_config(&wifi_cfg);
    get_default_ethernet_config(&eth_cfg);

    esp_err_t err = ESP_OK;
    
    if (save_can_config(&can_cfg) != ESP_OK) err = ESP_FAIL;
    if (save_wifi_config(&wifi_cfg) != ESP_OK) err = ESP_FAIL;
    if (save_ethernet_config(&eth_cfg) != ESP_OK) err = ESP_FAIL;

    if (err == ESP_OK) {
        ESP_LOGI(TAG, "Configuración por defecto restaurada");
    }
    return err;
}

esp_err_t ConfigManager::erase_all() {
    ESP_LOGW(TAG, "Borrando toda la configuración...");

    nvs_handle_t handle;
    esp_err_t err = nvs_open(NVS_NAMESPACE, NVS_READWRITE, &handle);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Error al abrir NVS: %s", esp_err_to_name(err));
        return err;
    }

    err = nvs_erase_all(handle);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Error al borrar configuración: %s", esp_err_to_name(err));
        nvs_close(handle);
        return err;
    }

    err = nvs_commit(handle);
    nvs_close(handle);

    if (err == ESP_OK) {
        ESP_LOGI(TAG, "Configuración borrada correctamente");
    }
    return err;
}

void ConfigManager::get_default_can_config(CANConfig* config) {
    config->node_id = 0x01;           // Node ID por defecto
    config->bitrate = 250;            // 250 kbps (común en CAN industrial)
    config->tx_gpio = 21;             // GPIO 21 para TX
    config->rx_gpio = 22;             // GPIO 22 para RX
}

void ConfigManager::get_default_wifi_config(WiFiConfig* config) {
    strncpy(config->ssid, "ESP32_Gateway", sizeof(config->ssid) - 1);
    strncpy(config->password, "", sizeof(config->password) - 1);
    config->use_dhcp = true;
    strncpy(config->static_ip, "192.168.1.100", sizeof(config->static_ip) - 1);
    strncpy(config->gateway, "192.168.1.1", sizeof(config->gateway) - 1);
    strncpy(config->netmask, "255.255.255.0", sizeof(config->netmask) - 1);
}

void ConfigManager::get_default_ethernet_config(EthernetConfig* config) {
    config->enabled = false;          // Deshabilitado por defecto
    config->module_type = 0;          // W5500 por defecto
    config->use_dhcp = true;
    
    strncpy(config->static_ip, "192.168.1.100", sizeof(config->static_ip) - 1);
    strncpy(config->gateway, "192.168.1.1", sizeof(config->gateway) - 1);
    strncpy(config->netmask, "255.255.255.0", sizeof(config->netmask) - 1);
    
    // Pines W5500 por defecto
    config->w5500_miso = 19;
    config->w5500_mosi = 23;
    config->w5500_sclk = 18;
    config->w5500_cs = 5;
    config->w5500_int = 4;
    config->w5500_rst = -1;
    
    // Pines LAN8720 por defecto
    config->lan8720_phy_addr = 1;
    config->lan8720_mdc = 23;
    config->lan8720_mdio = 18;
    config->lan8720_rst = -1;
    config->lan8720_pwr = -1;
}
