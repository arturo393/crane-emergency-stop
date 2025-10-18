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
#include "../components/tcp_server/tcp_server_manager.h"

static const char *TAG = "ESP32_GATEWAY";

// Instancias globales de managers
static EthernetManager* ethernet_manager = nullptr;
static OTAManager* ota_manager = nullptr;
static CANManager* can_manager = nullptr;
static TCPServerManager* tcp_server = nullptr;

/**
 * @brief Callback para procesar comandos TCP
 * @param cmd Comando recibido
 * @param response Respuesta a enviar
 * @return ESP_OK si se procesó correctamente
 */
static esp_err_t command_callback(const TCPServerManager::Command& cmd, std::string& response)
{
    ESP_LOGI(TAG, "Procesando comando TCP: tipo=%d", cmd.type);
    
    cJSON* root = cJSON_CreateObject();
    cJSON_AddStringToObject(root, "status", "ok");
    
    switch (cmd.type) {
        case TCPServerManager::CMD_EMERGENCY_STOP:
            ESP_LOGW(TAG, "⚠️  PARADA DE EMERGENCIA RECIBIDA VIA TCP");
            // TODO: Enviar comando de parada de emergencia via CAN
            cJSON_AddStringToObject(root, "message", "Emergency stop activated");
            break;
            
        case TCPServerManager::CMD_RESET:
            ESP_LOGI(TAG, "Reset solicitado via TCP");
            // TODO: Enviar comando de reset via CAN
            cJSON_AddStringToObject(root, "message", "Reset command sent");
            break;
            
        case TCPServerManager::CMD_GET_STATUS:
            ESP_LOGI(TAG, "Solicitud de estado via TCP");
            cJSON_AddStringToObject(root, "message", "Status retrieved");
            cJSON_AddBoolToObject(root, "ethernet_connected", ethernet_manager && ethernet_manager->is_connected());
            cJSON_AddBoolToObject(root, "can_connected", can_manager && can_manager->is_connected());
            cJSON_AddStringToObject(root, "ip_address", ethernet_manager ? ethernet_manager->get_ip_address() : "N/A");
            break;
            
        case TCPServerManager::CMD_SET_VELOCITY: {
            ESP_LOGI(TAG, "Configuración de velocidad via TCP");
            // TODO: Parsear velocidad del JSON y enviar via CAN
            cJSON_AddStringToObject(root, "message", "Velocity set");
            break;
        }
            
        case TCPServerManager::CMD_SET_POSITION: {
            ESP_LOGI(TAG, "Configuración de posición via TCP");
            // TODO: Parsear posición del JSON y enviar via CAN
            cJSON_AddStringToObject(root, "message", "Position set");
            break;
        }
            
        case TCPServerManager::CMD_GET_POSITION:
            ESP_LOGI(TAG, "Lectura de posición via TCP");
            // TODO: Leer posición via CAN
            cJSON_AddNumberToObject(root, "position", 0); // Placeholder
            break;
            
        case TCPServerManager::CMD_GET_VELOCITY:
            ESP_LOGI(TAG, "Lectura de velocidad via TCP");
            // TODO: Leer velocidad via CAN
            cJSON_AddNumberToObject(root, "velocity", 0); // Placeholder
            break;
            
        case TCPServerManager::CMD_CAN_SEND:
            ESP_LOGI(TAG, "Envío de mensaje CAN via TCP");
            // TODO: Parsear mensaje CAN del JSON y enviar
            cJSON_AddStringToObject(root, "message", "CAN message sent");
            break;
            
        case TCPServerManager::CMD_CAN_RECEIVE:
            ESP_LOGI(TAG, "Recepción de mensaje CAN via TCP");
            // TODO: Recibir mensaje CAN y enviar respuesta
            cJSON_AddStringToObject(root, "message", "CAN message received");
            break;
            
        case TCPServerManager::CMD_OTA_UPDATE:
            ESP_LOGI(TAG, "Actualización OTA solicitada via TCP");
            // TODO: Iniciar proceso OTA
            cJSON_AddStringToObject(root, "message", "OTA update started");
            break;
            
        default:
            ESP_LOGW(TAG, "Comando desconocido: %d", cmd.type);
            cJSON_Delete(root);
            root = cJSON_CreateObject();
            cJSON_AddStringToObject(root, "status", "error");
            cJSON_AddStringToObject(root, "message", "Unknown command");
            break;
    }
    
    char* json_str = cJSON_Print(root);
    response = std::string(json_str);
    free(json_str);
    cJSON_Delete(root);
    
    return ESP_OK;
}

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
    
    // Inicializar TCP Server Manager
    ESP_LOGI(TAG, "Inicializando TCP Server Manager...");
    tcp_server = new TCPServerManager();
    if (tcp_server->init(8888) != ESP_OK) {
        ESP_LOGE(TAG, "Error inicializando TCP Server Manager");
        return;
    }
    
    // Registrar callback para procesar comandos
    tcp_server->register_command_callback(command_callback);
    
    if (tcp_server->start() != ESP_OK) {
        ESP_LOGE(TAG, "Error iniciando TCP Server Manager");
        return;
    }
    ESP_LOGI(TAG, "✅ TCP Server Manager inicializado");
    
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
        
        // Obtener estadísticas TCP Server
        uint32_t tcp_connections, tcp_commands, tcp_errors;
        tcp_server->get_stats(&tcp_connections, &tcp_commands, &tcp_errors);
        ESP_LOGD(TAG, "TCP Stats - CONN:%u CMD:%u ERR:%u", tcp_connections, tcp_commands, tcp_errors);
    }
}
