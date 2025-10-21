#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "esp_log.h"
#include "nvs_flash.h"

// Incluir managers implementados
#include "wifi_manager.h"
#include "can_manager.h"
#include "ethernet_manager.h"
#include "../components/ota/ota_manager.h"
#include "../components/canopen/cia402.h"
#include "../components/canopen/pdo.h"

static const char *TAG = "ESP32_GATEWAY";

// Instancias globales de managers
static WiFiManager* wifi_manager = nullptr;
static EthernetManager* ethernet_manager = nullptr;
static OTAManager* ota_manager = nullptr;
static CANManager* can_manager = nullptr;
static Cia402Controller cia402;
static uint8_t node_id = 0x01; // configurable más adelante vía NVS



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
    ESP_LOGI(TAG, "=== ESP32 Gateway para Danfoss R13 F ===");
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
    
    // TODO: Cargar configuración desde NVS (NodeID, pines, credenciales, etc.)
    
    // Inicializar WiFi Manager (opcional - comentado por defecto)
    // ESP_LOGI(TAG, "Inicializando WiFi Manager...");
    // wifi_manager = new WiFiManager();
    // wifi_manager->init("SSID", "PASSWORD");
    // wifi_manager->start();
    // ESP_LOGI(TAG, "✅ WiFi Manager inicializado");
    
    // Inicializar Ethernet Manager (opcional - descomentar si se usa)
    // ESP_LOGI(TAG, "Inicializando Ethernet Manager...");
    // ethernet_manager = new EthernetManager();
    // EthernetManager::W5500Config eth_config = {
    //     .miso_gpio = 19,
    //     .mosi_gpio = 23,
    //     .sclk_gpio = 18,
    //     .cs_gpio = 5,
    //     .int_gpio = 4,
    //     .rst_gpio = -1,
    //     .spi_clock_mhz = 20
    // };
    // if (ethernet_manager->init_w5500(eth_config, true) == ESP_OK) {
    //     ethernet_manager->start();
    //     ESP_LOGI(TAG, "✅ Ethernet Manager inicializado");
    // }
    
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

    // Preparar PDO IDs
    const PdoIds pdo = make_pdo_ids(node_id);
    ESP_LOGI(TAG, "CANopen Node ID: 0x%02X", node_id);
    ESP_LOGI(TAG, "TPDO1: 0x%03X, RPDO1: 0x%03X, Heartbeat: 0x%03X", 
             pdo.tpdo1, pdo.rpdo1, pdo.heartbeat);
    
    // Inicializar OTA Manager
    ESP_LOGI(TAG, "Inicializando OTA Manager...");
    ota_manager = new OTAManager();
    if (ota_manager->init() != ESP_OK) {
        ESP_LOGE(TAG, "Error inicializando OTA Manager");
        // No retornar - OTA es opcional
    } else {
        ESP_LOGI(TAG, "✅ OTA Manager inicializado");
        ESP_LOGI(TAG, "Para OTA: Usar HTTP POST a /ota con URL del firmware");
    }
    
    ESP_LOGI(TAG, "========================================");
    ESP_LOGI(TAG, "Sistema inicializado - Loop principal");
    ESP_LOGI(TAG, "========================================");
    
    // Loop principal
    TickType_t last_hb = xTaskGetTickCount();
    TickType_t last_pdo = xTaskGetTickCount();

    while(1) {
        // Procesar RPDO1 (control word)
        twai_message_t msg;
        if (can_manager->receive_message(&msg) == ESP_OK) {
            if (msg.identifier == pdo.rpdo1 && msg.data_length_code >= 2) {
                uint16_t cw = parse_control_word(msg.data);
                ESP_LOGI(TAG, "RPDO1 recibido CW=0x%04X", cw);
                cia402.process_control_word(cw);
            }
        }

        // Enviar heartbeat cada 1000 ms
        if (xTaskGetTickCount() - last_hb >= pdMS_TO_TICKS(1000)) {
            uint8_t hb_state = 0x05; // Operational
            can_manager->send_message(pdo.heartbeat, &hb_state, 1);
            last_hb = xTaskGetTickCount();
        }

        // Publicar TPDO1 (Status Word) cada 50 ms
        if (xTaskGetTickCount() - last_pdo >= pdMS_TO_TICKS(50)) {
            uint8_t data[8];
            build_status_word(cia402.status_word(), data);
            can_manager->send_message(pdo.tpdo1, data, 8);
            last_pdo = xTaskGetTickCount();
        }

        vTaskDelay(pdMS_TO_TICKS(5));
    }
}
