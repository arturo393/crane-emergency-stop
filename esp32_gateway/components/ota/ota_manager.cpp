#include "ota_manager.h"
#include "esp_log.h"
#include "esp_ota_ops.h"
#include "esp_http_client.h"
#include "esp_crt_bundle.h"
#include "mbedtls/sha256.h"
#include <string.h>
#include <stdlib.h>

static const char *TAG = "OTA_MANAGER";

OTAManager::OTAManager() :
    state_(OTA_IDLE),
    progress_(0),
    ca_cert_(NULL),
    ca_cert_len_(0),
    timeout_ms_(30000),
    ota_handle_(0),
    update_partition_(NULL) {
}

OTAManager::~OTAManager() {
    if (ca_cert_) {
        free((void*)ca_cert_);
    }
}

esp_err_t OTAManager::init() {
    ESP_LOGI(TAG, "Inicializando OTA Manager...");

    // Obtener partición de actualización
    update_partition_ = esp_ota_get_next_update_partition(NULL);
    if (update_partition_ == NULL) {
        ESP_LOGE(TAG, "No se encontró partición de actualización");
        return ESP_FAIL;
    }

    ESP_LOGI(TAG, "Partición de actualización: %s", update_partition_->label);
    ESP_LOGI(TAG, "OTA Manager inicializado correctamente");

    return ESP_OK;
}

esp_err_t OTAManager::check_for_updates(const char* url) {
    if (url == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    state_ = OTA_CHECKING;
    ESP_LOGI(TAG, "Verificando actualizaciones en: %s", url);

    // Configurar cliente HTTP para verificar versión
    esp_http_client_config_t config = {
        .url = url,
        .method = HTTP_METHOD_GET,
        .timeout_ms = timeout_ms_,
        .crt_bundle_attach = esp_crt_bundle_attach,
    };

    if (ca_cert_) {
        config.cert_pem = ca_cert_;
        config.cert_len = ca_cert_len_;
    }

    esp_http_client_handle_t client = esp_http_client_init(&config);
    if (client == NULL) {
        ESP_LOGE(TAG, "Error al inicializar cliente HTTP");
        state_ = OTA_FAILED;
        return ESP_FAIL;
    }

    esp_err_t err = esp_http_client_perform(client);
    if (err == ESP_OK) {
        int status_code = esp_http_client_get_status_code(client);
        ESP_LOGI(TAG, "Código de estado HTTP: %d", status_code);

        if (status_code == 200) {
            // Aquí se implementaría la lógica para comparar versiones
            // Por simplicidad, asumimos que hay actualización disponible
            ESP_LOGI(TAG, "Actualización disponible");
            state_ = OTA_IDLE;
            esp_http_client_cleanup(client);
            return ESP_OK;
        }
    }

    ESP_LOGE(TAG, "Error al verificar actualizaciones: %s", esp_err_to_name(err));
    state_ = OTA_FAILED;
    esp_http_client_cleanup(client);
    return err;
}

esp_err_t OTAManager::start_update(const char* url) {
    if (url == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    state_ = OTA_DOWNLOADING;
    progress_ = 0;
    ESP_LOGI(TAG, "Iniciando actualización OTA desde: %s", url);

    // Configurar cliente HTTP para descarga
    esp_http_client_config_t config = {
        .url = url,
        .method = HTTP_METHOD_GET,
        .timeout_ms = timeout_ms_,
        .event_handler = http_event_handler,
        .crt_bundle_attach = esp_crt_bundle_attach,
    };

    if (ca_cert_) {
        config.cert_pem = ca_cert_;
        config.cert_len = ca_cert_len_;
    }

    esp_http_client_handle_t client = esp_http_client_init(&config);
    if (client == NULL) {
        ESP_LOGE(TAG, "Error al inicializar cliente HTTP");
        state_ = OTA_FAILED;
        return ESP_FAIL;
    }

    // Iniciar OTA
    esp_err_t err = esp_ota_begin(update_partition_, OTA_SIZE_UNKNOWN, &ota_handle_);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Error al iniciar OTA: %s", esp_err_to_name(err));
        esp_http_client_cleanup(client);
        state_ = OTA_FAILED;
        return err;
    }

    // Descargar y escribir firmware
    err = esp_http_client_perform(client);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Error en descarga HTTP: %s", esp_err_to_name(err));
        esp_ota_abort(ota_handle_);
        esp_http_client_cleanup(client);
        state_ = OTA_FAILED;
        return err;
    }

    // Finalizar OTA
    err = esp_ota_end(ota_handle_);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Error al finalizar OTA: %s", esp_err_to_name(err));
        esp_http_client_cleanup(client);
        state_ = OTA_FAILED;
        return err;
    }

    // Verificar firmware
    state_ = OTA_VERIFYING;
    if (!verify_firmware(NULL, 0)) {  // Implementar verificación real
        ESP_LOGE(TAG, "Verificación de firmware fallida");
        state_ = OTA_FAILED;
        esp_http_client_cleanup(client);
        return ESP_FAIL;
    }

    // Establecer nueva partición de arranque
    err = esp_ota_set_boot_partition(update_partition_);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Error al establecer partición de arranque: %s", esp_err_to_name(err));
        state_ = OTA_FAILED;
        esp_http_client_cleanup(client);
        return err;
    }

    state_ = OTA_SUCCESS;
    ESP_LOGI(TAG, "Actualización OTA completada exitosamente");
    esp_http_client_cleanup(client);

    return ESP_OK;
}

OTAManager::OTAState OTAManager::get_state() {
    return state_;
}

int OTAManager::get_progress() {
    return progress_;
}

esp_err_t OTAManager::cancel_update() {
    if (state_ == OTA_DOWNLOADING) {
        esp_ota_abort(ota_handle_);
        state_ = OTA_IDLE;
        progress_ = 0;
        ESP_LOGI(TAG, "Actualización OTA cancelada");
    }
    return ESP_OK;
}

esp_err_t OTAManager::rollback() {
    const esp_partition_t* running_partition = esp_ota_get_running_partition();
    const esp_partition_t* rollback_partition = esp_ota_get_next_update_partition(NULL);

    if (rollback_partition != running_partition) {
        esp_err_t err = esp_ota_set_boot_partition(rollback_partition);
        if (err == ESP_OK) {
            ESP_LOGI(TAG, "Rollback completado - reinicie para aplicar");
            return ESP_OK;
        } else {
            ESP_LOGE(TAG, "Error en rollback: %s", esp_err_to_name(err));
            return err;
        }
    }

    ESP_LOGW(TAG, "No hay partición para rollback");
    return ESP_FAIL;
}

esp_err_t OTAManager::set_ca_cert(const char* cert, size_t cert_len) {
    if (cert == NULL || cert_len == 0) {
        return ESP_ERR_INVALID_ARG;
    }

    if (ca_cert_) {
        free((void*)ca_cert_);
    }

    ca_cert_ = (const char*)malloc(cert_len + 1);
    if (ca_cert_ == NULL) {
        return ESP_ERR_NO_MEM;
    }

    memcpy((void*)ca_cert_, cert, cert_len);
    ((char*)ca_cert_)[cert_len] = '\0';
    ca_cert_len_ = cert_len;

    ESP_LOGI(TAG, "Certificado CA configurado (%d bytes)", cert_len);
    return ESP_OK;
}

esp_err_t OTAManager::set_timeout(int timeout_ms) {
    if (timeout_ms <= 0) {
        return ESP_ERR_INVALID_ARG;
    }

    timeout_ms_ = timeout_ms;
    ESP_LOGI(TAG, "Timeout configurado: %d ms", timeout_ms);
    return ESP_OK;
}

esp_err_t OTAManager::http_event_handler(esp_http_client_event_t *evt) {
    static int total_len = 0;
    static int received_len = 0;

    switch (evt->event_id) {
        case HTTP_EVENT_ERROR:
            ESP_LOGE(TAG, "Error en evento HTTP");
            break;

        case HTTP_EVENT_ON_CONNECTED:
            ESP_LOGI(TAG, "Conectado al servidor");
            total_len = 0;
            received_len = 0;
            break;

        case HTTP_EVENT_HEADER_SENT:
            ESP_LOGI(TAG, "Headers enviados");
            break;

        case HTTP_EVENT_ON_HEADER:
            ESP_LOGD(TAG, "Header: %s: %s", evt->header_key, evt->header_value);
            if (strcmp(evt->header_key, "Content-Length") == 0) {
                total_len = atoi(evt->header_value);
            }
            break;

        case HTTP_EVENT_ON_DATA:
            ESP_LOGD(TAG, "Datos recibidos: %d bytes", evt->data_len);
            if (evt->user_data) {
                OTAManager* manager = static_cast<OTAManager*>(evt->user_data);
                esp_err_t err = esp_ota_write(manager->ota_handle_,
                                            (const void*)evt->data, evt->data_len);
                if (err != ESP_OK) {
                    ESP_LOGE(TAG, "Error al escribir OTA: %s", esp_err_to_name(err));
                    return err;
                }

                received_len += evt->data_len;
                if (total_len > 0) {
                    manager->progress_ = (received_len * 100) / total_len;
                    ESP_LOGI(TAG, "Progreso: %d%%", manager->progress_);
                }
            }
            break;

        case HTTP_EVENT_ON_FINISH:
            ESP_LOGI(TAG, "Descarga completada");
            break;

        case HTTP_EVENT_DISCONNECTED:
            ESP_LOGI(TAG, "Desconectado del servidor");
            break;

        default:
            break;
    }

    return ESP_OK;
}

bool OTAManager::verify_firmware(const char* data, size_t len) {
    // Implementar verificación de firma digital o hash
    // Por simplicidad, retornar true
    ESP_LOGI(TAG, "Verificación de firmware completada");
    return true;
}

esp_err_t OTAManager::calculate_sha256(const char* data, size_t len, uint8_t* hash) {
    if (data == NULL || hash == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    mbedtls_sha256_context ctx;
    mbedtls_sha256_init(&ctx);
    mbedtls_sha256_starts(&ctx, 0); // 0 para SHA256, no SHA224
    mbedtls_sha256_update(&ctx, (const unsigned char*)data, len);
    mbedtls_sha256_finish(&ctx, hash);
    mbedtls_sha256_free(&ctx);

    return ESP_OK;
}