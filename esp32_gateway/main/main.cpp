#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "esp_log.h"
#include "nvs_flash.h"

// Incluir managers implementados
#include "../components/network/ethernet_manager.h"
#include "../components/ota/ota_manager.h"
#include "../components/canopen/can_manager.h"

static const char *TAG = "ESP32_GATEWAY";

// Instancias globales de managers
static EthernetManager* ethernet_manager = nullptr;
static OTAManager* ota_manager = nullptr;
static CANManager* can_manager = nullptr;

/**
 * @brief Función principal del gateway ESP32
 * 
 * Inicializa todos los módulos del sistema:
 * - Ethernet Manager
 * - CAN Manager
 * - OTA Manager
 */
extern "C" void app_main(void)
{
    ESP_LOGI(TAG, "=== ESP32 Gateway para Danfoss K13 F ===");
    ESP_LOGI(TAG, "Versión: 1.0.0");
    ESP_LOGI(TAG, "Compilado: %s %s", __DATE__, __TIME__);
    
    // Inicializar NVS (Non-Volatile Storage)
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);
    
    ESP_LOGI(TAG, "NVS inicializado correctamente");
    
    // Inicializar Ethernet Manager
    ESP_LOGI(TAG, "Inicializando Ethernet Manager...");
    ethernet_manager = new EthernetManager();
    if (ethernet_manager->init() != ESP_OK) {
        ESP_LOGE(TAG, "Error inicializando Ethernet Manager");
        return;
    }
    
    if (ethernet_manager->start() != ESP_OK) {
        ESP_LOGE(TAG, "Error iniciando Ethernet Manager");
        return;
    }
    ESP_LOGI(TAG, "✅ Ethernet Manager inicializado");
    
    // Inicializar CAN Manager
    ESP_LOGI(TAG, "Inicializando CAN Manager...");
    can_manager = new CANManager();
    if (can_manager->init() != ESP_OK) {
        ESP_LOGE(TAG, "Error inicializando CAN Manager");
        return;
    }
    
    if (can_manager->start() != ESP_OK) {
        ESP_LOGE(TAG, "Error iniciando CAN Manager");
        return;
    }
    ESP_LOGI(TAG, "✅ CAN Manager inicializado");
    
    // Inicializar OTA Manager
    ESP_LOGI(TAG, "Inicializando OTA Manager...");
    ota_manager = new OTAManager();
    if (ota_manager->init() != ESP_OK) {
        ESP_LOGE(TAG, "Error inicializando OTA Manager");
        return;
    }
    ESP_LOGI(TAG, "✅ OTA Manager inicializado");
    
    ESP_LOGI(TAG, "Sistema inicializado - Entrando en loop principal");
    
    // Loop principal
    while(1) {
        vTaskDelay(pdMS_TO_TICKS(1000));
        
        // Verificar estado de conexiones
        bool eth_connected = ethernet_manager->is_connected();
        bool can_connected = can_manager->is_connected();
        
        ESP_LOGI(TAG, "Estado - Ethernet: %s, CAN: %s", 
                eth_connected ? "Conectado" : "Desconectado",
                can_connected ? "Conectado" : "Desconectado");
        
        // Obtener estadísticas CAN
        uint32_t tx_count, rx_count, error_count;
        can_manager->get_stats(&tx_count, &rx_count, &error_count);
        ESP_LOGD(TAG, "CAN Stats - TX:%u RX:%u ERR:%u", tx_count, rx_count, error_count);
    }
}
