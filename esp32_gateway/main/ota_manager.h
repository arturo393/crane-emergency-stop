/**
 * @file ota_manager.h
 * @brief OTA (Over-The-Air) Update Manager para D13 Gateway
 * 
 * Sistema de actualización remota de firmware con:
 * - HTTP/HTTPS endpoints para subida de firmware
 * - Verificación SHA256 del firmware
 * - Rollback automático en caso de fallo
 * - Preservación de configuración
 * - Logging de proceso OTA
 * 
 * @author D13 Gateway Team
 * @date 2025-11-01
 */

#pragma once

#include "esp_err.h"
#include "esp_ota_ops.h"
#include <functional>

/**
 * @brief Estados del proceso OTA
 */
enum class OtaState {
    IDLE,               ///< Sin actualización en progreso
    DOWNLOADING,        ///< Descargando firmware
    VERIFYING,          ///< Verificando integridad
    WRITING,            ///< Escribiendo a partición OTA
    VALIDATING,         ///< Validando imagen
    READY_TO_BOOT,      ///< Listo para reiniciar
    ROLLBACK,           ///< Rollback en progreso
    ERROR               ///< Error durante actualización
};

/**
 * @brief Resultado de la operación OTA
 */
struct OtaResult {
    bool success;               ///< True si exitoso
    esp_err_t error_code;       ///< Código de error ESP-IDF
    const char* error_msg;      ///< Mensaje de error
    uint32_t bytes_written;     ///< Bytes escritos
    char version[32];           ///< Versión del firmware
};

/**
 * @brief Callback para progreso de OTA
 * @param bytes_downloaded Bytes descargados hasta ahora
 * @param total_size Tamaño total del firmware
 */
using OtaProgressCallback = std::function<void(size_t bytes_downloaded, size_t total_size)>;

/**
 * @brief Gestor de actualizaciones OTA
 * 
 * Maneja el proceso completo de actualización de firmware:
 * 1. Descarga desde URL HTTP/HTTPS
 * 2. Verificación SHA256
 * 3. Escritura a partición OTA inactiva
 * 4. Validación de imagen
 * 5. Marcado como booteable
 * 6. Rollback si falla primer arranque
 */
class OtaManager {
public:
    OtaManager();
    ~OtaManager();

    /**
     * @brief Inicializa el gestor OTA
     * @return ESP_OK si exitoso
     */
    esp_err_t init();

    /**
     * @brief Actualiza firmware desde URL HTTP
     * @param url URL del firmware (.bin)
     * @param expected_sha256 SHA256 esperado (opcional, NULL para omitir)
     * @param progress_cb Callback de progreso (opcional)
     * @return Resultado de la actualización
     */
    OtaResult update_from_url(const char* url, 
                              const char* expected_sha256 = nullptr,
                              OtaProgressCallback progress_cb = nullptr);

    /**
     * @brief Actualiza firmware desde buffer en memoria
     * @param data Buffer con datos del firmware
     * @param size Tamaño del buffer
     * @param expected_sha256 SHA256 esperado (opcional)
     * @return Resultado de la actualización
     */
    OtaResult update_from_buffer(const uint8_t* data, 
                                  size_t size,
                                  const char* expected_sha256 = nullptr);

    /**
     * @brief Verifica si hay una actualización pendiente de validación
     * @return true si hay actualización pendiente
     */
    bool is_pending_validation();

    /**
     * @brief Marca la actualización actual como válida
     * 
     * Debe llamarse después de arrancar con nuevo firmware
     * y verificar que todo funciona correctamente.
     * 
     * @return ESP_OK si exitoso
     */
    esp_err_t mark_as_valid();

    /**
     * @brief Revierte a la versión anterior del firmware
     * @return ESP_OK si exitoso
     */
    esp_err_t rollback();

    /**
     * @brief Obtiene información de la partición actual
     * @param label Buffer para almacenar label (min 17 bytes)
     * @param version Buffer para almacenar versión (min 32 bytes)
     * @return ESP_OK si exitoso
     */
    esp_err_t get_running_partition_info(char* label, char* version);

    /**
     * @brief Obtiene estado actual del OTA
     * @return Estado actual
     */
    OtaState get_state() const { return state_; }

    /**
     * @brief Verifica si una actualización está en progreso
     * @return true si hay actualización en progreso
     */
    bool is_updating() const { 
        return state_ != OtaState::IDLE && state_ != OtaState::ERROR; 
    }

    /**
     * @brief Cancela actualización en progreso
     * @return ESP_OK si exitoso
     */
    esp_err_t cancel_update();

private:
    OtaState state_;                            ///< Estado actual
    esp_ota_handle_t update_handle_;            ///< Handle de actualización
    const esp_partition_t* update_partition_;   ///< Partición OTA objetivo
    const esp_partition_t* running_partition_;  ///< Partición actual
    size_t bytes_written_;                      ///< Bytes escritos
    bool initialized_;                          ///< Flag de inicialización

    /**
     * @brief Prepara la partición OTA para escritura
     * @return ESP_OK si exitoso
     */
    esp_err_t begin_update();

    /**
     * @brief Escribe datos a la partición OTA
     * @param data Datos a escribir
     * @param size Tamaño de datos
     * @return ESP_OK si exitoso
     */
    esp_err_t write_data(const uint8_t* data, size_t size);

    /**
     * @brief Finaliza la actualización y marca como booteable
     * @return ESP_OK si exitoso
     */
    esp_err_t end_update();

    /**
     * @brief Verifica SHA256 del firmware escrito
     * @param expected_sha256 SHA256 esperado (hex string)
     * @return true si coincide
     */
    bool verify_sha256(const char* expected_sha256);

    /**
     * @brief Limpia recursos de actualización
     */
    void cleanup();
};

// Instancia global
extern OtaManager* ota_manager;

// Macros de logging OTA
#define OTA_LOGI(format, ...) do { \
    ESP_LOGI("OTA", format, ##__VA_ARGS__); \
    if (sd_logger && sd_logger->is_ready()) { \
        sd_logger->log(SD_LOG_INFO, "OTA", format, ##__VA_ARGS__); \
    } \
} while(0)

#define OTA_LOGW(format, ...) do { \
    ESP_LOGW("OTA", format, ##__VA_ARGS__); \
    if (sd_logger && sd_logger->is_ready()) { \
        sd_logger->log(SD_LOG_WARN, "OTA", format, ##__VA_ARGS__); \
    } \
} while(0)

#define OTA_LOGE(format, ...) do { \
    ESP_LOGE("OTA", format, ##__VA_ARGS__); \
    if (sd_logger && sd_logger->is_ready()) { \
        sd_logger->log(SD_LOG_ERROR, "OTA", format, ##__VA_ARGS__); \
    } \
} while(0)
