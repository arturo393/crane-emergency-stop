#ifndef OTA_MANAGER_H
#define OTA_MANAGER_H

#include "esp_err.h"
#include "esp_http_client.h"

/**
 * @brief Clase para gestionar actualizaciones OTA (Over-The-Air) del ESP32
 *
 * Esta clase maneja descargas seguras de firmware, verificación de integridad,
 * y rollback automático en caso de fallos.
 */
class OTAManager {
public:
    /**
     * @brief Estados del proceso OTA
     */
    enum OTAState {
        OTA_IDLE,
        OTA_CHECKING,
        OTA_DOWNLOADING,
        OTA_VERIFYING,
        OTA_UPDATING,
        OTA_SUCCESS,
        OTA_FAILED
    };

    /**
     * @brief Constructor
     */
    OTAManager();

    /**
     * @brief Destructor
     */
    ~OTAManager();

    /**
     * @brief Inicializar el módulo OTA
     * @return ESP_OK si la inicialización fue exitosa
     */
    esp_err_t init();

    /**
     * @brief Verificar si hay actualizaciones disponibles
     * @param url URL del servidor de versiones
     * @return ESP_OK si hay actualización disponible
     */
    esp_err_t check_for_updates(const char* url);

    /**
     * @brief Iniciar actualización OTA
     * @param url URL del firmware
     * @return ESP_OK si la actualización se inició correctamente
     */
    esp_err_t start_update(const char* url);

    /**
     * @brief Obtener estado actual del OTA
     * @return Estado del proceso OTA
     */
    OTAState get_state();

    /**
     * @brief Obtener progreso de descarga (0-100)
     * @return Porcentaje de progreso
     */
    int get_progress();

    /**
     * @brief Cancelar actualización en curso
     * @return ESP_OK si se canceló correctamente
     */
    esp_err_t cancel_update();

    /**
     * @brief Rollback a versión anterior
     * @return ESP_OK si el rollback fue exitoso
     */
    esp_err_t rollback();

    /**
     * @brief Configurar certificado CA para HTTPS
     * @param cert Certificado CA en formato PEM
     * @param cert_len Longitud del certificado
     * @return ESP_OK si se configuró correctamente
     */
    esp_err_t set_ca_cert(const char* cert, size_t cert_len);

    /**
     * @brief Configurar timeout de conexión
     * @param timeout_ms Timeout en milisegundos
     * @return ESP_OK si se configuró correctamente
     */
    esp_err_t set_timeout(int timeout_ms);

private:
    /**
     * @brief Manejador de eventos HTTP
     * @param evt Evento HTTP
     * @return Código de resultado
     */
    static esp_err_t http_event_handler(esp_http_client_event_t *evt);

    /**
     * @brief Verificar integridad del firmware descargado
     * @param data Datos del firmware
     * @param len Longitud de los datos
     * @return true si es válido
     */
    bool verify_firmware(const char* data, size_t len);

    /**
     * @brief Calcular hash SHA256
     * @param data Datos a hashear
     * @param len Longitud de los datos
     * @param hash Buffer para el hash (32 bytes)
     * @return ESP_OK si se calculó correctamente
     */
    esp_err_t calculate_sha256(const char* data, size_t len, uint8_t* hash);

    OTAState state_;                    ///< Estado actual del OTA
    int progress_;                      ///< Progreso de descarga (0-100)
    const char* ca_cert_;               ///< Certificado CA para HTTPS
    size_t ca_cert_len_;                ///< Longitud del certificado CA
    int timeout_ms_;                    ///< Timeout de conexión
    esp_ota_handle_t ota_handle_;       ///< Handle del OTA
    const esp_partition_t* update_partition_; ///< Partición de actualización
};

#endif // OTA_MANAGER_H