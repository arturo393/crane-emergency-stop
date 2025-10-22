#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "esp_log.h"
#include "nvs_flash.h"

// Solo lo esencial: CAN Manager y CiA 402
#include "can_manager.h"
#include "../components/canopen/cia402.h"
#include "../components/canopen/pdo.h"

static const char *TAG = "K13_GATEWAY";

// Variables globales simples
static CANManager* can_manager = nullptr;
static Cia402Controller cia402;
static const uint8_t NODE_ID = 0x01;  // NodeID fijo por ahora



/**
 * @brief Gateway ESP32 para control K13 via CANopen
 * 
 * SIMPLE Y DIRECTO:
 * 1. Inicializar CAN bus
 * 2. Enviar heartbeat cada 1s
 * 3. Enviar Status Word cada 50ms
 * 4. Recibir Control Word y cambiar estado
 */
extern "C" void app_main(void)
{
    ESP_LOGI(TAG, "");
    ESP_LOGI(TAG, "==============================================");
    ESP_LOGI(TAG, "   K13 Gateway - Control Puente Grúa");
    ESP_LOGI(TAG, "   Compilado: %s %s", __DATE__, __TIME__);
    ESP_LOGI(TAG, "==============================================");
    ESP_LOGI(TAG, "");
    
    // 1. Inicializar NVS (necesario para WiFi/BT, aunque no lo usemos ahora)
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        nvs_flash_erase();
        ret = nvs_flash_init();
    }
    
    // 2. Inicializar CAN Manager
    ESP_LOGI(TAG, "🔧 Inicializando CAN bus...");
    can_manager = new CANManager();
    
    // GPIO 4 = TX, GPIO 5 = RX, 250 kbps
    if (can_manager->init(4, 5, 250000) != ESP_OK) {
        ESP_LOGE(TAG, "❌ FALLO: No se pudo inicializar CAN");
        ESP_LOGE(TAG, "   Verifica conexiones TX/RX (GPIO 4/5) y transceiver");
        return;
    }
    
    ESP_LOGI(TAG, "✅ CAN bus listo");
    ESP_LOGI(TAG, "");
    
    // 3. Preparar IDs CANopen
    const PdoIds pdo = make_pdo_ids(NODE_ID);
    ESP_LOGI(TAG, "📡 CANopen configurado:");
    ESP_LOGI(TAG, "   Node ID: 0x%02X", NODE_ID);
    ESP_LOGI(TAG, "   RPDO1 (recibe Control Word): 0x%03X", pdo.rpdo1);
    ESP_LOGI(TAG, "   TPDO1 (envía Status Word):   0x%03X", pdo.tpdo1);
    ESP_LOGI(TAG, "   Heartbeat:                   0x%03X", pdo.heartbeat);
    ESP_LOGI(TAG, "");
    
    ESP_LOGI(TAG, "========================================");
    ESP_LOGI(TAG, "🚀 Sistema listo - Loop principal activo");
    ESP_LOGI(TAG, "========================================");
    ESP_LOGI(TAG, "");
    
    // ========================================
    // LOOP PRINCIPAL - Simple y efectivo
    // ========================================
    
    TickType_t last_heartbeat = xTaskGetTickCount();
    TickType_t last_status = xTaskGetTickCount();
    uint32_t msg_count = 0;

    while(1) {
        // 1. RECIBIR: Leer Control Word (RPDO1) si hay mensajes (timeout 10ms)
        twai_message_t msg;
        if (can_manager->receive_message(&msg, 10) == ESP_OK) {
            if (msg.identifier == pdo.rpdo1 && msg.data_length_code >= 2) {
                uint16_t control_word = parse_control_word(msg.data);
                ESP_LOGI(TAG, "📥 Control Word: 0x%04X", control_word);
                cia402.process_control_word(control_word);
                msg_count++;
            }
        }

        // 2. HEARTBEAT: Enviar cada 1 segundo
        if (xTaskGetTickCount() - last_heartbeat >= pdMS_TO_TICKS(1000)) {
            uint8_t state = 0x05; // Operational
            can_manager->send_message(pdo.heartbeat, &state, 1);
            ESP_LOGD(TAG, "💓 Heartbeat");
            last_heartbeat = xTaskGetTickCount();
        }

        // 3. STATUS: Publicar Status Word cada 50ms
        if (xTaskGetTickCount() - last_status >= pdMS_TO_TICKS(50)) {
            uint8_t data[8] = {0};
            build_status_word(cia402.status_word(), data);
            can_manager->send_message(pdo.tpdo1, data, 8);
            last_status = xTaskGetTickCount();
        }

        // Pequeña pausa para no saturar CPU
        vTaskDelay(pdMS_TO_TICKS(5));
    }
}
