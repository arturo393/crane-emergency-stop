#ifndef TCP_SERVER_MANAGER_H
#define TCP_SERVER_MANAGER_H

#include "esp_err.h"
#include "esp_event.h"
#include "lwip/sockets.h"
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <freertos/queue.h>
#include <string>
#include <vector>
#include <functional>

/**
 * @brief Clase para gestionar servidor TCP/IP del ESP32 Gateway
 *
 * Esta clase maneja conexiones TCP entrantes, recibe comandos JSON
 * y coordina con otros managers (CAN, OTA) para ejecutar operaciones.
 */
class TCPServerManager {
public:
    /**
     * @brief Estados del TCP Server
     */
    enum ServerState {
        SERVER_STOPPED,
        SERVER_STARTING,
        SERVER_RUNNING,
        SERVER_ERROR
    };

    /**
     * @brief Tipos de comandos soportados
     */
    enum CommandType {
        CMD_EMERGENCY_STOP,
        CMD_RESET,
        CMD_GET_STATUS,
        CMD_SET_VELOCITY,
        CMD_SET_POSITION,
        CMD_GET_POSITION,
        CMD_GET_VELOCITY,
        CMD_CAN_SEND,
        CMD_CAN_RECEIVE,
        CMD_OTA_UPDATE,
        CMD_SYSTEM_INFO
    };

    /**
     * @brief Estructura para comandos
     */
    struct Command {
        CommandType type;
        std::string data;
        int client_socket;
    };

    /**
     * @brief Callback para procesar comandos
     */
    typedef std::function<esp_err_t(const Command& cmd, std::string& response)> CommandCallback;

    /**
     * @brief Constructor
     */
    TCPServerManager();

    /**
     * @brief Destructor
     */
    ~TCPServerManager();

    /**
     * @brief Inicializar el servidor TCP
     * @param port Puerto TCP para escuchar
     * @return ESP_OK si la inicialización fue exitosa
     */
    esp_err_t init(uint16_t port = 8888);

    /**
     * @brief Iniciar el servidor TCP
     * @return ESP_OK si se inició correctamente
     */
    esp_err_t start();

    /**
     * @brief Detener el servidor TCP
     * @return ESP_OK si se detuvo correctamente
     */
    esp_err_t stop();

    /**
     * @brief Obtener estado actual del servidor
     * @return Estado del servidor
     */
    ServerState get_state();

    /**
     * @brief Verificar si el servidor está ejecutándose
     * @return true si está ejecutándose
     */
    bool is_running();

    /**
     * @brief Registrar callback para procesar comandos
     * @param callback Función callback
     */
    void register_command_callback(CommandCallback callback);

    /**
     * @brief Obtener estadísticas del servidor
     * @param connections Número de conexiones activas
     * @param total_commands Número total de comandos procesados
     * @param errors Número de errores
     */
    void get_stats(uint32_t* connections, uint32_t* total_commands, uint32_t* errors);

    /**
     * @brief Limpiar estadísticas
     */
    void clear_stats();

private:
    /**
     * @brief Tarea principal del servidor TCP
     * @param arg Argumento de la tarea
     */
    static void server_task(void* arg);

    /**
     * @brief Tarea para manejar cliente TCP
     * @param arg Argumento de la tarea (socket del cliente)
     */
    static void client_task(void* arg);

    /**
     * @brief Procesar comando JSON recibido
     * @param json_str String JSON con el comando
     * @param client_socket Socket del cliente
     * @return Comando procesado
     */
    Command parse_command(const std::string& json_str, int client_socket);

    /**
     * @brief Enviar respuesta al cliente
     * @param client_socket Socket del cliente
     * @param response Respuesta JSON
     * @return ESP_OK si se envió correctamente
     */
    esp_err_t send_response(int client_socket, const std::string& response);

    ServerState state_;                ///< Estado actual del servidor
    int server_socket_;                ///< Socket del servidor
    uint16_t port_;                    ///< Puerto TCP
    TaskHandle_t server_task_;         ///< Handle de la tarea del servidor

    CommandCallback command_callback_; ///< Callback para procesar comandos

    // Estadísticas
    uint32_t active_connections_;      ///< Conexiones activas
    uint32_t total_commands_;          ///< Total de comandos procesados
    uint32_t error_count_;             ///< Contador de errores
};

#endif // TCP_SERVER_MANAGER_H