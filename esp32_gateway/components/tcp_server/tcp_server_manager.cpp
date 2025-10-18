#include "tcp_server_manager.h"
#include "esp_log.h"
#include "esp_system.h"
#include "lwip/err.h"
#include "lwip/sys.h"
#include <cstring>
#include <cJSON.h>

static const char *TAG = "TCP_SERVER";

TCPServerManager::TCPServerManager()
    : state_(SERVER_STOPPED)
    , server_socket_(-1)
    , port_(8888)
    , server_task_(nullptr)
    , command_callback_(nullptr)
    , active_connections_(0)
    , total_commands_(0)
    , error_count_(0)
{
    ESP_LOGI(TAG, "TCP Server Manager creado");
}

TCPServerManager::~TCPServerManager()
{
    stop();
    ESP_LOGI(TAG, "TCP Server Manager destruido");
}

esp_err_t TCPServerManager::init(uint16_t port)
{
    port_ = port;
    ESP_LOGI(TAG, "TCP Server inicializado en puerto %d", port_);
    return ESP_OK;
}

esp_err_t TCPServerManager::start()
{
    if (state_ != SERVER_STOPPED) {
        ESP_LOGW(TAG, "Servidor ya está ejecutándose");
        return ESP_ERR_INVALID_STATE;
    }

    state_ = SERVER_STARTING;

    // Crear socket del servidor
    server_socket_ = socket(AF_INET, SOCK_STREAM, IPPROTO_IP);
    if (server_socket_ < 0) {
        ESP_LOGE(TAG, "Error creando socket del servidor");
        state_ = SERVER_ERROR;
        return ESP_FAIL;
    }

    // Configurar socket para reutilizar dirección
    int opt = 1;
    setsockopt(server_socket_, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    // Configurar dirección del servidor
    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    server_addr.sin_port = htons(port_);

    // Bind del socket
    if (bind(server_socket_, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        ESP_LOGE(TAG, "Error en bind del socket");
        close(server_socket_);
        server_socket_ = -1;
        state_ = SERVER_ERROR;
        return ESP_FAIL;
    }

    // Listen
    if (listen(server_socket_, 5) < 0) {
        ESP_LOGE(TAG, "Error en listen");
        close(server_socket_);
        server_socket_ = -1;
        state_ = SERVER_ERROR;
        return ESP_FAIL;
    }

    // Crear tarea del servidor
    if (xTaskCreate(server_task, "tcp_server", 4096, this, 5, &server_task_) != pdPASS) {
        ESP_LOGE(TAG, "Error creando tarea del servidor");
        close(server_socket_);
        server_socket_ = -1;
        state_ = SERVER_ERROR;
        return ESP_FAIL;
    }

    state_ = SERVER_RUNNING;
    ESP_LOGI(TAG, "Servidor TCP iniciado en puerto %d", port_);
    return ESP_OK;
}

esp_err_t TCPServerManager::stop()
{
    if (state_ == SERVER_STOPPED) {
        return ESP_OK;
    }

    state_ = SERVER_STOPPED;

    // Cerrar socket del servidor
    if (server_socket_ >= 0) {
        close(server_socket_);
        server_socket_ = -1;
    }

    // Detener tarea del servidor
    if (server_task_ != nullptr) {
        vTaskDelete(server_task_);
        server_task_ = nullptr;
    }

    ESP_LOGI(TAG, "Servidor TCP detenido");
    return ESP_OK;
}

TCPServerManager::ServerState TCPServerManager::get_state()
{
    return state_;
}

bool TCPServerManager::is_running()
{
    return state_ == SERVER_RUNNING;
}

void TCPServerManager::register_command_callback(CommandCallback callback)
{
    command_callback_ = callback;
}

void TCPServerManager::get_stats(uint32_t* connections, uint32_t* total_commands, uint32_t* errors)
{
    if (connections) *connections = active_connections_;
    if (total_commands) *total_commands = total_commands_;
    if (errors) *errors = error_count_;
}

void TCPServerManager::clear_stats()
{
    active_connections_ = 0;
    total_commands_ = 0;
    error_count_ = 0;
}

void TCPServerManager::server_task(void* arg)
{
    TCPServerManager* server = static_cast<TCPServerManager*>(arg);

    ESP_LOGI(TAG, "Tarea del servidor TCP iniciada");

    while (server->state_ == SERVER_RUNNING) {
        struct sockaddr_in client_addr;
        socklen_t client_addr_len = sizeof(client_addr);

        // Aceptar conexión del cliente
        int client_socket = accept(server->server_socket_,
                                 (struct sockaddr*)&client_addr,
                                 &client_addr_len);

        if (client_socket < 0) {
            if (server->state_ == SERVER_RUNNING) {
                ESP_LOGE(TAG, "Error aceptando conexión del cliente");
                server->error_count_++;
            }
            continue;
        }

        ESP_LOGI(TAG, "Cliente conectado desde %s:%d",
                inet_ntoa(client_addr.sin_addr),
                ntohs(client_addr.sin_port));

        server->active_connections_++;

        // Crear tarea para manejar el cliente
        TaskHandle_t client_task;
        int* client_sock_ptr = new int(client_socket);
        if (xTaskCreate(client_task, "tcp_client", 4096, client_sock_ptr, 4, &client_task) != pdPASS) {
            ESP_LOGE(TAG, "Error creando tarea del cliente");
            close(client_socket);
            delete client_sock_ptr;
            server->active_connections_--;
            server->error_count_++;
        }
    }

    ESP_LOGI(TAG, "Tarea del servidor TCP terminada");
    vTaskDelete(nullptr);
}

void TCPServerManager::client_task(void* arg)
{
    int* client_sock_ptr = static_cast<int*>(arg);
    int client_socket = *client_sock_ptr;
    delete client_sock_ptr;

    TCPServerManager* server = nullptr; // TODO: Obtener referencia al servidor

    ESP_LOGI(TAG, "Tarea del cliente TCP iniciada (socket: %d)", client_socket);

    char buffer[1024];
    bool client_connected = true;

    while (client_connected && server && server->state_ == SERVER_RUNNING) {
        // Recibir datos del cliente
        int len = recv(client_socket, buffer, sizeof(buffer) - 1, 0);

        if (len < 0) {
            ESP_LOGE(TAG, "Error recibiendo datos del cliente");
            break;
        } else if (len == 0) {
            // Cliente cerró la conexión
            ESP_LOGI(TAG, "Cliente cerró la conexión");
            break;
        }

        buffer[len] = '\0';
        std::string received_data(buffer);

        ESP_LOGD(TAG, "Datos recibidos: %s", received_data.c_str());

        // Procesar comando
        if (server->command_callback_) {
            TCPServerManager::Command cmd = server->parse_command(received_data, client_socket);

            if (cmd.type != CMD_SYSTEM_INFO) { // Evitar log excesivo
                ESP_LOGI(TAG, "Comando recibido: tipo=%d", cmd.type);
            }

            std::string response;
            esp_err_t err = server->command_callback_(cmd, response);

            if (err == ESP_OK) {
                server->send_response(client_socket, response);
                server->total_commands_++;
            } else {
                ESP_LOGE(TAG, "Error procesando comando");
                std::string error_response = R"({"status":"error","message":"Command processing failed"})";
                server->send_response(client_socket, error_response);
                server->error_count_++;
            }
        } else {
            ESP_LOGW(TAG, "No hay callback registrado para procesar comandos");
            std::string error_response = R"({"status":"error","message":"No command handler registered"})";
            server->send_response(client_socket, error_response);
        }
    }

    // Cerrar conexión del cliente
    close(client_socket);
    if (server) {
        server->active_connections_--;
    }

    ESP_LOGI(TAG, "Tarea del cliente TCP terminada");
    vTaskDelete(nullptr);
}

TCPServerManager::Command TCPServerManager::parse_command(const std::string& json_str, int client_socket)
{
    Command cmd;
    cmd.client_socket = client_socket;
    cmd.type = CMD_SYSTEM_INFO; // Default
    cmd.data = json_str;

    // Parsear JSON
    cJSON* root = cJSON_Parse(json_str.c_str());
    if (!root) {
        ESP_LOGE(TAG, "Error parseando JSON");
        return cmd;
    }

    // Extraer tipo de comando
    cJSON* cmd_json = cJSON_GetObjectItem(root, "command");
    if (cJSON_IsString(cmd_json)) {
        std::string cmd_str = cmd_json->valuestring;

        if (cmd_str == "emergency_stop") {
            cmd.type = CMD_EMERGENCY_STOP;
        } else if (cmd_str == "reset") {
            cmd.type = CMD_RESET;
        } else if (cmd_str == "get_status") {
            cmd.type = CMD_GET_STATUS;
        } else if (cmd_str == "set_velocity") {
            cmd.type = CMD_SET_VELOCITY;
        } else if (cmd_str == "set_position") {
            cmd.type = CMD_SET_POSITION;
        } else if (cmd_str == "get_position") {
            cmd.type = CMD_GET_POSITION;
        } else if (cmd_str == "get_velocity") {
            cmd.type = CMD_GET_VELOCITY;
        } else if (cmd_str == "can_send") {
            cmd.type = CMD_CAN_SEND;
        } else if (cmd_str == "can_receive") {
            cmd.type = CMD_CAN_RECEIVE;
        } else if (cmd_str == "ota_update") {
            cmd.type = CMD_OTA_UPDATE;
        } else {
            ESP_LOGW(TAG, "Comando desconocido: %s", cmd_str.c_str());
        }
    }

    cJSON_Delete(root);
    return cmd;
}

esp_err_t TCPServerManager::send_response(int client_socket, const std::string& response)
{
    int len = send(client_socket, response.c_str(), response.length(), 0);
    if (len < 0) {
        ESP_LOGE(TAG, "Error enviando respuesta al cliente");
        return ESP_FAIL;
    }

    ESP_LOGD(TAG, "Respuesta enviada: %s", response.c_str());
    return ESP_OK;
}