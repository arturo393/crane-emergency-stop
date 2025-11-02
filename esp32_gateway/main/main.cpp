#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "freertos/semphr.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "lwip/err.h"
#include "lwip/sockets.h"
#include "lwip/sys.h"
#include <lwip/netdb.h>

#include "hardware_config.h" // Centralized pin definitions
#include "can_manager.h"
#include "ethernet_manager.h"
#include "wifi_manager.h"
#include "config_manager.h"
#include "auth_manager.h"
#include "sd_logger.h"
#include "ota_manager.h"
#include "web_server.h"
#include "../components/canopen/cia402.h"
#include "../components/canopen/pdo.h"

static const char *TAG = "D13_GATEWAY";


// --- Estructuras de Comunicación ---
typedef enum {
    CMD_SHUTDOWN,
    CMD_SWITCH_ON,
    CMD_ENABLE_OPERATION,
    CMD_DISABLE_OPERATION,
    CMD_QUICK_STOP,
    CMD_GET_STATUS
} GatewayCommand;

typedef struct {
    GatewayCommand command;
    int client_socket; // Socket del cliente para enviar respuesta
} NetworkMessage;

typedef struct {
    uint16_t status_word;
    Cia402State state;
} StatusMessage;

// --- Globales ---
static CANManager* can_manager = nullptr;
static EthernetManager* eth_manager = nullptr;
static AuthManager* auth_manager = nullptr;
static WebServer* web_server = nullptr;
static Cia402Controller cia402;
static const uint8_t NODE_ID = 0x01;

// --- Colas y Sincronización ---
static QueueHandle_t network_to_gateway_queue = nullptr;
static QueueHandle_t gateway_to_network_queue = nullptr;
static SemaphoreHandle_t cia402_mutex = nullptr;

// --- Declaración de Tareas ---
void can_task(void *pvParameters);
void network_task(void *pvParameters);
void gateway_logic_task(void *pvParameters);


extern "C" void app_main(void)
{
    ESP_LOGI(TAG, "==============================================");
    ESP_LOGI(TAG, "   D13 Gateway - Control Puente Grúa (FreeRTOS)");
    ESP_LOGI(TAG, "   Compilado: %s %s", __DATE__, __TIME__);
    ESP_LOGI(TAG, "==============================================");

    // Inicializar NVS
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    // Crear colas de comunicación entre tareas
    network_to_gateway_queue = xQueueCreate(10, sizeof(NetworkMessage));
    gateway_to_network_queue = xQueueCreate(10, sizeof(StatusMessage));
    
    // Crear mutex para proteger cia402
    cia402_mutex = xSemaphoreCreateMutex();

    // Inicializar managers
    can_manager = new CANManager();
    eth_manager = new EthernetManager();
    auth_manager = new AuthManager();
    
    // Inicializar SD logger (opcional - no bloquea si falla)
    sd_logger = new SDLogger();
    if (sd_logger->init()) {
        ESP_LOGI(TAG, "✅ SD Logger inicializado");
        SD_LOGI(TAG, "Sistema D13 Gateway iniciado");
    } else {
        ESP_LOGW(TAG, "⚠️  SD Logger no disponible - continuando sin logging a SD");
    }
    
    // Inicializar OTA manager
    ota_manager = new OtaManager();
    if (ota_manager->init() == ESP_OK) {
        ESP_LOGI(TAG, "✅ OTA Manager inicializado");
        
        // Verificar si hay actualización pendiente de validación
        if (ota_manager->is_pending_validation()) {
            ESP_LOGW(TAG, "⚠️  OTA pendiente de validación detectada");
            ESP_LOGW(TAG, "Firmware actual será validado en 30 segundos si funciona correctamente");
            SD_LOGW(TAG, "OTA PENDING VALIDATION - Auto-validación en 30s");
            
            // Auto-validar después de 30 segundos si todo funciona
            vTaskDelay(pdMS_TO_TICKS(30000));
            if (ota_manager->mark_as_valid() == ESP_OK) {
                ESP_LOGI(TAG, "✅ Firmware OTA validado exitosamente");
                SD_LOGI(TAG, "OTA firmware validado - sistema estable");
            }
        }
        
        char version[32];
        if (ota_manager->get_running_partition_info(nullptr, version) == ESP_OK) {
            ESP_LOGI(TAG, "Firmware version: %s", version);
            SD_LOGI(TAG, "Firmware version: %s", version);
        }
    } else {
        ESP_LOGW(TAG, "⚠️  OTA Manager no disponible");
    }

    // Inicializar servidor web
    web_server = new WebServer();
    if (web_server->init(80) == ESP_OK) {
        ESP_LOGI(TAG, "✅ Servidor Web inicializado en puerto 80");
        SD_LOGI(TAG, "Web Server inicializado - Dashboard disponible");
        
        // Configurar callback para obtener status
        web_server->set_status_callback([](GatewayStatus& status) {
            // CAN status - valores simulados por ahora
            status.can_online = can_manager != nullptr;
            status.can_rx_count = 0;  // TODO: agregar contador a CANManager
            status.can_tx_count = 0;  // TODO: agregar contador a CANManager
            status.can_errors = 0;    // TODO: agregar contador a CANManager
            
            // CiA402 status (protegido por mutex)
            if (cia402_mutex && xSemaphoreTake(cia402_mutex, pdMS_TO_TICKS(10))) {
                status.cia402_state = static_cast<uint8_t>(cia402.state());
                status.status_word = cia402.status_word();
                status.control_word = 0;  // TODO: agregar a cia402
                xSemaphoreGive(cia402_mutex);
            }
            
            // Network status
            status.eth_connected = eth_manager && eth_manager->is_connected();
            if (eth_manager && status.eth_connected) {
                char ip_temp[16];
                eth_manager->get_ip(ip_temp);
                strncpy(status.ip_address, ip_temp, sizeof(status.ip_address) - 1);
            } else {
                strncpy(status.ip_address, "0.0.0.0", sizeof(status.ip_address) - 1);
            }
            status.tcp_port = 5000; // Puerto TCP del gateway
            status.clients_connected = 0; // TODO: implementar contador de clientes
            
            // System status
            status.uptime_seconds = xTaskGetTickCount() * portTICK_PERIOD_MS / 1000;
            status.free_heap = esp_get_free_heap_size();
            status.cpu_usage = 0; // TODO: implementar medición de CPU
            
            // SD Logger status
            status.sd_mounted = sd_logger && sd_logger->is_ready();
            status.sd_total_mb = 0;   // TODO: implementar get_storage_info
            status.sd_used_mb = 0;    // TODO: implementar get_storage_info
            status.log_files_count = 0; // TODO: implementar contador de archivos
            
            // OTA status
            if (ota_manager) {
                char partition[32];
                ota_manager->get_running_partition_info(partition, status.firmware_version);
                strncpy(status.ota_partition, partition, sizeof(status.ota_partition) - 1);
                status.ota_pending = ota_manager->is_pending_validation();
            } else {
                strncpy(status.firmware_version, "unknown", sizeof(status.firmware_version) - 1);
                strncpy(status.ota_partition, "unknown", sizeof(status.ota_partition) - 1);
                status.ota_pending = false;
            }
        });
    } else {
        ESP_LOGW(TAG, "⚠️  Servidor Web no disponible");
    }

    ESP_LOGI(TAG, "✅ Sincronización inicializada:");
    ESP_LOGI(TAG, "   - Colas de mensajes creadas");
    ESP_LOGI(TAG, "   - Mutex de CiA402 creado");

    // Crear tareas
    xTaskCreate(can_task, "CAN_Task", 4096, NULL, 10, NULL);
    xTaskCreate(network_task, "Network_Task", 8192, NULL, 8, NULL);
    xTaskCreate(gateway_logic_task, "Gateway_Logic_Task", 4096, NULL, 5, NULL);

    ESP_LOGI(TAG, "✅ Tareas principales creadas. El sistema está operativo.");
}

// ====================================================================
// TAREA 1: Gestión de la comunicación CAN
// Responsabilidades:
// - Inicializar el bus CAN.
// - Recibir mensajes CAN (especialmente el Control Word).
// - Enviar mensajes CAN (Heartbeat, Status Word).
// - Actualizar la máquina de estados CiA402 con mensajes del bus.
// ====================================================================
void can_task(void *pvParameters) {
    ESP_LOGI(TAG, "[CAN Task] Inicializando...");

    if (can_manager->init(PIN_CAN_TX, PIN_CAN_RX, 250000) != ESP_OK) {
        ESP_LOGE(TAG, "[CAN Task] ❌ FALLO: No se pudo inicializar CAN. La tarea se eliminará.");
        SD_LOGE(TAG, "CAN Task FAILED: No se pudo inicializar CAN bus");
        vTaskDelete(NULL);
        return;
    }
    ESP_LOGI(TAG, "[CAN Task] ✅ CAN bus listo en TX:%d, RX:%d.", PIN_CAN_TX, PIN_CAN_RX);
    SD_LOGI(TAG, "CAN bus inicializado correctamente (TX:%d, RX:%d, 250kbps)", PIN_CAN_TX, PIN_CAN_RX);

    const PdoIds pdo = make_pdo_ids(NODE_ID);
    TickType_t last_heartbeat = xTaskGetTickCount();
    TickType_t last_status_send = xTaskGetTickCount();


    while (1) {
        // 1. Recibir mensajes del bus CAN
        twai_message_t msg;
        if (can_manager->receive_message(&msg, 10) == ESP_OK) {
            if (msg.identifier == pdo.rpdo1 && msg.data_length_code >= 2) {
                uint16_t control_word = parse_control_word(msg.data);
                ESP_LOGI(TAG, "[CAN Task] 📥 Control Word recibido del bus: 0x%04X", control_word);
                
                // Proteger acceso a cia402 con mutex
                if (xSemaphoreTake(cia402_mutex, pdMS_TO_TICKS(100)) == pdTRUE) {
                    cia402.process_control_word(control_word);
                    xSemaphoreGive(cia402_mutex);
                }
            }
        }

        // 2. Enviar Heartbeat (cada 1s)
        if (xTaskGetTickCount() - last_heartbeat >= pdMS_TO_TICKS(1000)) {
            uint8_t state = 0x05; // Operational
            can_manager->send_message(pdo.heartbeat, &state, 1);
            ESP_LOGD(TAG, "[CAN Task] 💓 Heartbeat enviado.");
            last_heartbeat = xTaskGetTickCount();
        }

        // 3. Enviar Status Word (cada 50ms)
        if (xTaskGetTickCount() - last_status_send >= pdMS_TO_TICKS(50)) {
            uint8_t data[8] = {0};
            
            // Proteger acceso a cia402 con mutex
            if (xSemaphoreTake(cia402_mutex, pdMS_TO_TICKS(100)) == pdTRUE) {
                build_status_word(cia402.status_word(), data);
                xSemaphoreGive(cia402_mutex);
            }
            
            can_manager->send_message(pdo.tpdo1, data, 8);
            last_status_send = xTaskGetTickCount();
        }
        
        vTaskDelay(pdMS_TO_TICKS(5)); // Pequeña pausa
    }
}

// ====================================================================
// TAREA 2: Gestión de la red (Ethernet/WiFi) y Servidor TCP
// Responsabilidades:
// - Inicializar y mantener la conexión de red.
// - Escuchar conexiones TCP en el puerto 5000.
// - Recibir comandos de texto desde clientes TCP.
// - Enviar comandos a la cola para la tarea de lógica del gateway.
// - Enviar respuestas de estado a los clientes.
// ====================================================================
void network_task(void *pvParameters) {
    ESP_LOGI(TAG, "[Network Task] Inicializando...");

    // Inicializar Ethernet usando la configuración del EdgeBox-Lite
    if (eth_manager->init_w5500(true) != ESP_OK) {
        ESP_LOGE(TAG, "[Network Task] ❌ FALLO: No se pudo inicializar Ethernet W5500.");
        // Podríamos intentar inicializar WiFi como fallback aquí
        vTaskDelete(NULL);
        return;
    }

    // Esperar a que se obtenga una IP
    ESP_LOGI(TAG, "[Network Task] Esperando conexión de red y dirección IP...");
    while (!eth_manager->is_connected()) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
    
    char ip_str[16];
    eth_manager->get_ip(ip_str);
    ESP_LOGI(TAG, "[Network Task] 🌐 IP obtenida: %s", ip_str);

    // Crear socket TCP para servidor
    int listen_sock = socket(AF_INET, SOCK_STREAM, IPPROTO_IP);
    if (listen_sock < 0) {
        ESP_LOGE(TAG, "[Network Task] Error al crear socket");
        vTaskDelete(NULL);
        return;
    }

    int opt = 1;
    setsockopt(listen_sock, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in dest_addr;
    dest_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    dest_addr.sin_family = AF_INET;
    dest_addr.sin_port = htons(5000);

    int err = bind(listen_sock, (struct sockaddr *)&dest_addr, sizeof(dest_addr));
    if (err != 0) {
        ESP_LOGE(TAG, "[Network Task] Error al hacer bind: errno %d", errno);
        close(listen_sock);
        vTaskDelete(NULL);
        return;
    }

    err = listen(listen_sock, 1);
    if (err != 0) {
        ESP_LOGE(TAG, "[Network Task] Error al hacer listen: errno %d", errno);
        close(listen_sock);
        vTaskDelete(NULL);
        return;
    }

    ESP_LOGI(TAG, "[Network Task] 🔌 Servidor TCP escuchando en puerto 5000");

    while (1) {
        ESP_LOGI(TAG, "[Network Task] Esperando conexión...");
        
        struct sockaddr_in source_addr;
        socklen_t addr_len = sizeof(source_addr);
        int sock = accept(listen_sock, (struct sockaddr *)&source_addr, &addr_len);
        
        if (sock < 0) {
            ESP_LOGE(TAG, "[Network Task] Error al aceptar conexión: errno %d", errno);
            continue;
        }

        // Obtener IP del cliente
        uint32_t client_ip = ntohl(source_addr.sin_addr.s_addr);
        ESP_LOGI(TAG, "[Network Task] 📞 Conexión desde: %lu.%lu.%lu.%lu",
                 (client_ip >> 24) & 0xFF,
                 (client_ip >> 16) & 0xFF,
                 (client_ip >> 8) & 0xFF,
                 client_ip & 0xFF);

        // Configurar timeout para recv
        struct timeval timeout;
        timeout.tv_sec = 10;
        timeout.tv_usec = 0;
        setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof timeout);

        // === AUTENTICACIÓN ===
        const char* auth_prompt = "AUTH: Ingrese token de autenticacion\n";
        send(sock, auth_prompt, strlen(auth_prompt), 0);

        char auth_buffer[MAX_TOKEN_LENGTH + 2];
        int auth_len = recv(sock, auth_buffer, sizeof(auth_buffer) - 1, 0);
        
        bool authenticated = false;
        if (auth_len > 0) {
            auth_buffer[auth_len] = 0;
            // Remover newline/carriage return
            char* newline = strchr(auth_buffer, '\n');
            if (newline) *newline = '\0';
            char* cr = strchr(auth_buffer, '\r');
            if (cr) *cr = '\0';
            
            if (auth_manager->verify_token(auth_buffer)) {
                authenticated = true;
                auth_manager->clear_failed_attempts(client_ip);
                const char* success_msg = "AUTH: OK - Autenticado correctamente\n";
                send(sock, success_msg, strlen(success_msg), 0);
                ESP_LOGI(TAG, "[Network Task] ✅ Cliente autenticado");
                SD_LOGI(TAG, "Cliente autenticado desde %lu.%lu.%lu.%lu",
                        (client_ip >> 24) & 0xFF, (client_ip >> 16) & 0xFF,
                        (client_ip >> 8) & 0xFF, client_ip & 0xFF);
            } else {
                if (!auth_manager->register_failed_attempt(client_ip)) {
                    const char* blocked_msg = "AUTH: ERROR - IP bloqueada temporalmente\n";
                    send(sock, blocked_msg, strlen(blocked_msg), 0);
                    ESP_LOGW(TAG, "[Network Task] ⛔ IP bloqueada");
                    SD_LOGW(TAG, "IP bloqueada: %lu.%lu.%lu.%lu (demasiados intentos fallidos)",
                            (client_ip >> 24) & 0xFF, (client_ip >> 16) & 0xFF,
                            (client_ip >> 8) & 0xFF, client_ip & 0xFF);
                } else {
                    const char* fail_msg = "AUTH: ERROR - Token invalido\n";
                    send(sock, fail_msg, strlen(fail_msg), 0);
                    ESP_LOGW(TAG, "[Network Task] ❌ Autenticación fallida");
                    SD_LOGW(TAG, "Autenticacion fallida desde %lu.%lu.%lu.%lu",
                            (client_ip >> 24) & 0xFF, (client_ip >> 16) & 0xFF,
                            (client_ip >> 8) & 0xFF, client_ip & 0xFF);
                }
                close(sock);
                continue;
            }
        } else {
            const char* timeout_msg = "AUTH: ERROR - Timeout de autenticacion\n";
            send(sock, timeout_msg, strlen(timeout_msg), 0);
            ESP_LOGW(TAG, "[Network Task] ⏱️  Timeout de autenticación");
            close(sock);
            continue;
        }
        
        if (!authenticated) {
            close(sock);
            continue;
        }

        ESP_LOGI(TAG, "[Network Task] 🔓 Sesión iniciada - esperando comandos...");

        char rx_buffer[128];
        while (1) {
            int len = recv(sock, rx_buffer, sizeof(rx_buffer) - 1, 0);
            if (len < 0) {
                ESP_LOGW(TAG, "[Network Task] recv failed: errno %d", errno);
                break;
            } else if (len == 0) {
                ESP_LOGI(TAG, "[Network Task] Cliente desconectado");
                break;
            } else {
                rx_buffer[len] = 0; // Null-terminate
                ESP_LOGI(TAG, "[Network Task] 📨 Recibido: %s", rx_buffer);

                // Parsear comando y enviar a la cola
                NetworkMessage net_msg;
                net_msg.client_socket = sock;
                
                const char* cmd_name = "UNKNOWN";

                if (strstr(rx_buffer, "SHUTDOWN")) {
                    net_msg.command = CMD_SHUTDOWN;
                    cmd_name = "SHUTDOWN";
                    xQueueSend(network_to_gateway_queue, &net_msg, 0);
                } else if (strstr(rx_buffer, "SWITCH_ON")) {
                    net_msg.command = CMD_SWITCH_ON;
                    cmd_name = "SWITCH_ON";
                    xQueueSend(network_to_gateway_queue, &net_msg, 0);
                } else if (strstr(rx_buffer, "ENABLE")) {
                    net_msg.command = CMD_ENABLE_OPERATION;
                    cmd_name = "ENABLE";
                    xQueueSend(network_to_gateway_queue, &net_msg, 0);
                } else if (strstr(rx_buffer, "DISABLE")) {
                    net_msg.command = CMD_DISABLE_OPERATION;
                    cmd_name = "DISABLE";
                    xQueueSend(network_to_gateway_queue, &net_msg, 0);
                } else if (strstr(rx_buffer, "QUICK_STOP")) {
                    net_msg.command = CMD_QUICK_STOP;
                    cmd_name = "QUICK_STOP";
                    xQueueSend(network_to_gateway_queue, &net_msg, 0);
                } else if (strstr(rx_buffer, "STATUS")) {
                    net_msg.command = CMD_GET_STATUS;
                    cmd_name = "STATUS";
                    xQueueSend(network_to_gateway_queue, &net_msg, 0);
                } else if (strstr(rx_buffer, "OTA_INFO")) {
                    // Información OTA
                    char label[17], version[32];
                    if (ota_manager && ota_manager->get_running_partition_info(label, version) == ESP_OK) {
                        char response[128];
                        snprintf(response, sizeof(response), 
                                "OTA_INFO: Partition=%s, Version=%s, Pending=%s\n",
                                label, version, 
                                ota_manager->is_pending_validation() ? "YES" : "NO");
                        send(sock, response, strlen(response), 0);
                        SD_LOGI(TAG, "Comando OTA_INFO ejecutado");
                    } else {
                        const char* error_msg = "ERROR: OTA manager no disponible\n";
                        send(sock, error_msg, strlen(error_msg), 0);
                    }
                    continue;
                } else if (strstr(rx_buffer, "OTA_VALIDATE")) {
                    // Validar firmware actual
                    if (ota_manager && ota_manager->mark_as_valid() == ESP_OK) {
                        const char* ok_msg = "OK: Firmware validado exitosamente\n";
                        send(sock, ok_msg, strlen(ok_msg), 0);
                        SD_LOGI(TAG, "Firmware OTA validado manualmente desde %lu.%lu.%lu.%lu",
                                (client_ip >> 24) & 0xFF, (client_ip >> 16) & 0xFF,
                                (client_ip >> 8) & 0xFF, client_ip & 0xFF);
                    } else {
                        const char* error_msg = "ERROR: No se pudo validar firmware\n";
                        send(sock, error_msg, strlen(error_msg), 0);
                    }
                    continue;
                } else if (strstr(rx_buffer, "OTA_ROLLBACK")) {
                    // Revertir a firmware anterior
                    const char* warning_msg = "WARN: Iniciando rollback, gateway se reiniciará...\n";
                    send(sock, warning_msg, strlen(warning_msg), 0);
                    SD_LOGW(TAG, "Rollback OTA solicitado desde %lu.%lu.%lu.%lu",
                            (client_ip >> 24) & 0xFF, (client_ip >> 16) & 0xFF,
                            (client_ip >> 8) & 0xFF, client_ip & 0xFF);
                    
                    vTaskDelay(pdMS_TO_TICKS(500));
                    if (ota_manager) {
                        ota_manager->rollback();
                    }
                    continue;
                } else {
                    const char* error_msg = "ERROR: Comando desconocido. Comandos: SHUTDOWN, SWITCH_ON, ENABLE, DISABLE, QUICK_STOP, STATUS, OTA_INFO, OTA_VALIDATE, OTA_ROLLBACK\n";
                    send(sock, error_msg, strlen(error_msg), 0);
                    SD_LOGW(TAG, "Comando desconocido recibido: %s", rx_buffer);
                    continue;
                }
                
                // Log del comando ejecutado
                SD_LOGI(TAG, "Comando ejecutado: %s desde %lu.%lu.%lu.%lu",
                        cmd_name,
                        (client_ip >> 24) & 0xFF, (client_ip >> 16) & 0xFF,
                        (client_ip >> 8) & 0xFF, client_ip & 0xFF);

                // Esperar respuesta de la cola
                StatusMessage status_msg;
                if (xQueueReceive(gateway_to_network_queue, &status_msg, pdMS_TO_TICKS(1000)) == pdTRUE) {
                    char response[128];
                    snprintf(response, sizeof(response), 
                             "OK: Status=0x%04X, State=%u\n", 
                             status_msg.status_word, (unsigned int)status_msg.state);
                    send(sock, response, strlen(response), 0);
                }
            }
        }

        close(sock);
    }

    close(listen_sock);
    vTaskDelete(NULL);
}


// ====================================================================
// TAREA 3: Lógica del Gateway (Traductor)
// Responsabilidades:
// - Actuar como intermediario entre la tarea de red y la tarea CAN.
// - Traducir comandos de red a Control Words de CANopen.
// - Actualizar la máquina de estados CiA402.
// - Enviar el estado actual de vuelta a la red.
// ====================================================================
void gateway_logic_task(void *pvParameters) {
    ESP_LOGI(TAG, "[Gateway Logic] Inicializando...");

    NetworkMessage net_msg;
    TickType_t last_web_update = 0;
    const TickType_t web_update_interval = pdMS_TO_TICKS(1000); // Actualizar cada 1 segundo
    
    while(1) {
        // Actualizar WebSocket periódicamente
        TickType_t now = xTaskGetTickCount();
        if (web_server && (now - last_web_update >= web_update_interval)) {
            GatewayStatus status = {};
            
            // CAN status
            status.can_online = can_manager != nullptr;
            status.can_rx_count = 0;
            status.can_tx_count = 0;
            status.can_errors = 0;
            
            // CiA402 status (protegido por mutex)
            if (cia402_mutex && xSemaphoreTake(cia402_mutex, pdMS_TO_TICKS(10))) {
                status.cia402_state = static_cast<uint8_t>(cia402.state());
                status.status_word = cia402.status_word();
                status.control_word = 0;
                xSemaphoreGive(cia402_mutex);
            }
            
            // Network status
            status.eth_connected = eth_manager && eth_manager->is_connected();
            if (eth_manager && status.eth_connected) {
                char ip_temp[16];
                eth_manager->get_ip(ip_temp);
                strncpy(status.ip_address, ip_temp, sizeof(status.ip_address) - 1);
            } else {
                strncpy(status.ip_address, "0.0.0.0", sizeof(status.ip_address) - 1);
            }
            status.tcp_port = 5000;
            status.clients_connected = 0;
            
            // System status
            status.uptime_seconds = xTaskGetTickCount() * portTICK_PERIOD_MS / 1000;
            status.free_heap = esp_get_free_heap_size();
            status.cpu_usage = 0;
            
            // SD Logger status
            status.sd_mounted = sd_logger && sd_logger->is_ready();
            status.sd_total_mb = 0;
            status.sd_used_mb = 0;
            status.log_files_count = 0;
            
            // OTA status
            if (ota_manager) {
                char partition[32];
                ota_manager->get_running_partition_info(partition, status.firmware_version);
                strncpy(status.ota_partition, partition, sizeof(status.ota_partition) - 1);
                status.ota_pending = ota_manager->is_pending_validation();
            } else {
                strncpy(status.firmware_version, "unknown", sizeof(status.firmware_version) - 1);
                strncpy(status.ota_partition, "unknown", sizeof(status.ota_partition) - 1);
                status.ota_pending = false;
            }
            
            web_server->update_status(status);
            last_web_update = now;
        }
        
        // Esperar comandos de la tarea de red
        if (xQueueReceive(network_to_gateway_queue, &net_msg, pdMS_TO_TICKS(100)) == pdTRUE) {
            ESP_LOGI(TAG, "[Gateway Logic] 📬 Comando recibido: %d", net_msg.command);

            uint16_t control_word = 0;
            
            // Traducir comando a Control Word
            switch (net_msg.command) {
                case CMD_SHUTDOWN:
                    control_word = 0x0006; // Shutdown
                    ESP_LOGI(TAG, "[Gateway Logic] ➡️  Ejecutando SHUTDOWN");
                    break;
                case CMD_SWITCH_ON:
                    control_word = 0x0007; // Switch On
                    ESP_LOGI(TAG, "[Gateway Logic] ➡️  Ejecutando SWITCH_ON");
                    break;
                case CMD_ENABLE_OPERATION:
                    control_word = 0x000F; // Enable Operation
                    ESP_LOGI(TAG, "[Gateway Logic] ➡️  Ejecutando ENABLE_OPERATION");
                    break;
                case CMD_DISABLE_OPERATION:
                    control_word = 0x0007; // Back to Switch On
                    ESP_LOGI(TAG, "[Gateway Logic] ➡️  Ejecutando DISABLE_OPERATION");
                    break;
                case CMD_QUICK_STOP:
                    control_word = 0x0002; // Quick Stop
                    ESP_LOGI(TAG, "[Gateway Logic] ➡️  Ejecutando QUICK_STOP");
                    break;
                case CMD_GET_STATUS:
                    // Solo leer estado, sin modificar
                    ESP_LOGI(TAG, "[Gateway Logic] 📊 Consultando STATUS");
                    break;
            }

            // Proteger acceso a cia402 con mutex y aplicar el control word
            if (xSemaphoreTake(cia402_mutex, pdMS_TO_TICKS(100)) == pdTRUE) {
                // Guardar estado anterior para logging
                Cia402State old_state = cia402.state();
                uint16_t old_status = cia402.status_word();
                
                if (net_msg.command != CMD_GET_STATUS) {
                    cia402.process_control_word(control_word);
                }

                // Preparar respuesta con el estado actual
                StatusMessage status_msg;
                status_msg.status_word = cia402.status_word();
                status_msg.state = cia402.state();
                
                xSemaphoreGive(cia402_mutex);

                // Log de transición de estado
                if (old_state != status_msg.state || old_status != status_msg.status_word) {
                    SD_LOGI(TAG, "Transición CiA402: State %u->%u, Status 0x%04X->0x%04X, CW=0x%04X",
                            (unsigned int)old_state, (unsigned int)status_msg.state, old_status, status_msg.status_word, control_word);
                }

                // Enviar respuesta a la cola de red
                xQueueSend(gateway_to_network_queue, &status_msg, 0);
                
                ESP_LOGI(TAG, "[Gateway Logic] 📤 Respuesta enviada: Status=0x%04X, State=%u", 
                         status_msg.status_word, (unsigned int)status_msg.state);
            } else {
                ESP_LOGW(TAG, "[Gateway Logic] ⚠️  No se pudo obtener mutex de CiA402");
                SD_LOGW(TAG, "Mutex CiA402 bloqueado, comando %d no procesado", net_msg.command);
            }
        }

        vTaskDelay(pdMS_TO_TICKS(10));
    }
}
