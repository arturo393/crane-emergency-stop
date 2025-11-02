/**
 * @file ota_manager.cpp
 * @brief Implementación del OTA Manager
 */

#include "ota_manager.h"
#include "esp_log.h"
#include "esp_https_ota.h"
#include "esp_http_client.h"
#include "esp_app_format.h"
#include "sd_logger.h"
#include <string.h>

static const char *TAG = "OTA_MANAGER";

// Instancia global
OtaManager* ota_manager = nullptr;

OtaManager::OtaManager() :
    state_(OtaState::IDLE),
    update_handle_(0),
    update_partition_(nullptr),
    running_partition_(nullptr),
    bytes_written_(0),
    initialized_(false) {
}

OtaManager::~OtaManager() {
    cleanup();
}

esp_err_t OtaManager::init() {
    if (initialized_) {
        return ESP_OK;
    }

    OTA_LOGI("Initializing OTA Manager...");

    // Obtener partición actual
    running_partition_ = esp_ota_get_running_partition();
    if (!running_partition_) {
        OTA_LOGE("Failed to get running partition");
        return ESP_FAIL;
    }

    OTA_LOGI("Running partition: %s (type %d, subtype %d, address 0x%lx, size %lu KB)",
             running_partition_->label,
             running_partition_->type,
             running_partition_->subtype,
             running_partition_->address,
             running_partition_->size / 1024);

    // Verificar si hay actualización pendiente de validación
    esp_ota_img_states_t ota_state;
    if (esp_ota_get_state_partition(running_partition_, &ota_state) == ESP_OK) {
        if (ota_state == ESP_OTA_IMG_PENDING_VERIFY) {
            OTA_LOGW("⚠️  Pending OTA validation detected!");
            OTA_LOGW("New firmware needs validation. Call mark_as_valid() if working correctly.");
            OTA_LOGW("Will auto-rollback on next boot if not validated.");
        } else if (ota_state == ESP_OTA_IMG_VALID) {
            OTA_LOGI("✓ Current firmware is validated");
        } else if (ota_state == ESP_OTA_IMG_INVALID) {
            OTA_LOGW("Current firmware marked as invalid");
        }
    }

    // Obtener partición OTA siguiente
    update_partition_ = esp_ota_get_next_update_partition(NULL);
    if (!update_partition_) {
        OTA_LOGE("Failed to get next update partition");
        return ESP_FAIL;
    }

    OTA_LOGI("Update partition: %s (address 0x%lx, size %lu KB)",
             update_partition_->label,
             update_partition_->address,
             update_partition_->size / 1024);

    initialized_ = true;
    state_ = OtaState::IDLE;

    return ESP_OK;
}

bool OtaManager::is_pending_validation() {
    if (!running_partition_) {
        return false;
    }

    esp_ota_img_states_t ota_state;
    if (esp_ota_get_state_partition(running_partition_, &ota_state) == ESP_OK) {
        return ota_state == ESP_OTA_IMG_PENDING_VERIFY;
    }

    return false;
}

esp_err_t OtaManager::mark_as_valid() {
    OTA_LOGI("Marking current firmware as valid...");

    if (!running_partition_) {
        OTA_LOGE("No running partition");
        return ESP_FAIL;
    }

    esp_err_t ret = esp_ota_mark_app_valid_cancel_rollback();
    if (ret != ESP_OK) {
        OTA_LOGE("Failed to mark as valid: %s", esp_err_to_name(ret));
        return ret;
    }

    OTA_LOGI("✓ Firmware validated successfully");
    return ESP_OK;
}

esp_err_t OtaManager::rollback() {
    OTA_LOGW("Initiating rollback to previous firmware...");

    state_ = OtaState::ROLLBACK;

    const esp_partition_t* last_valid = esp_ota_get_last_invalid_partition();
    if (!last_valid) {
        OTA_LOGE("No valid partition to rollback to");
        state_ = OtaState::ERROR;
        return ESP_FAIL;
    }

    OTA_LOGI("Rolling back to partition: %s", last_valid->label);

    esp_err_t ret = esp_ota_set_boot_partition(last_valid);
    if (ret != ESP_OK) {
        OTA_LOGE("Failed to set boot partition: %s", esp_err_to_name(ret));
        state_ = OtaState::ERROR;
        return ret;
    }

    OTA_LOGI("✓ Rollback configured. Rebooting...");
    vTaskDelay(pdMS_TO_TICKS(1000));
    esp_restart();

    return ESP_OK; // No alcanzará aquí
}

esp_err_t OtaManager::get_running_partition_info(char* label, char* version) {
    if (!running_partition_) {
        return ESP_FAIL;
    }

    if (label) {
        strncpy(label, running_partition_->label, 16);
        label[16] = '\0';
    }

    if (version) {
        esp_app_desc_t app_desc;
        const esp_partition_t* part = esp_ota_get_running_partition();
        if (esp_ota_get_partition_description(part, &app_desc) == ESP_OK) {
            strncpy(version, app_desc.version, 31);
            version[31] = '\0';
        } else {
            strcpy(version, "unknown");
        }
    }

    return ESP_OK;
}

esp_err_t OtaManager::begin_update() {
    if (state_ != OtaState::IDLE) {
        OTA_LOGE("Update already in progress");
        return ESP_FAIL;
    }

    OTA_LOGI("Beginning OTA update...");
    state_ = OtaState::WRITING;

    esp_err_t ret = esp_ota_begin(update_partition_, OTA_SIZE_UNKNOWN, &update_handle_);
    if (ret != ESP_OK) {
        OTA_LOGE("esp_ota_begin failed: %s", esp_err_to_name(ret));
        state_ = OtaState::ERROR;
        return ret;
    }

    bytes_written_ = 0;
    OTA_LOGI("✓ OTA begin successful");
    return ESP_OK;
}

esp_err_t OtaManager::write_data(const uint8_t* data, size_t size) {
    if (state_ != OtaState::WRITING) {
        OTA_LOGE("Not in WRITING state");
        return ESP_FAIL;
    }

    esp_err_t ret = esp_ota_write(update_handle_, data, size);
    if (ret != ESP_OK) {
        OTA_LOGE("esp_ota_write failed: %s", esp_err_to_name(ret));
        state_ = OtaState::ERROR;
        return ret;
    }

    bytes_written_ += size;
    return ESP_OK;
}

esp_err_t OtaManager::end_update() {
    if (state_ != OtaState::WRITING) {
        OTA_LOGE("Not in WRITING state");
        return ESP_FAIL;
    }

    OTA_LOGI("Finishing OTA update...");
    state_ = OtaState::VALIDATING;

    esp_err_t ret = esp_ota_end(update_handle_);
    if (ret != ESP_OK) {
        OTA_LOGE("esp_ota_end failed: %s", esp_err_to_name(ret));
        state_ = OtaState::ERROR;
        return ret;
    }

    OTA_LOGI("Total bytes written: %u", bytes_written_);

    // Marcar como booteable
    ret = esp_ota_set_boot_partition(update_partition_);
    if (ret != ESP_OK) {
        OTA_LOGE("esp_ota_set_boot_partition failed: %s", esp_err_to_name(ret));
        state_ = OtaState::ERROR;
        return ret;
    }

    state_ = OtaState::READY_TO_BOOT;
    OTA_LOGI("✓ OTA update complete. Ready to reboot.");

    return ESP_OK;
}

bool OtaManager::verify_sha256(const char* expected_sha256) {
    if (!expected_sha256 || strlen(expected_sha256) == 0) {
        OTA_LOGW("No SHA256 provided, skipping verification");
        return true;
    }

    OTA_LOGI("Verifying SHA256...");
    state_ = OtaState::VERIFYING;

    uint8_t sha_256[32] = {0};
    esp_partition_get_sha256(update_partition_, sha_256);

    // Convertir a hex string
    char calculated_sha[65];
    for (int i = 0; i < 32; i++) {
        sprintf(&calculated_sha[i * 2], "%02x", sha_256[i]);
    }
    calculated_sha[64] = '\0';

    if (strcmp(calculated_sha, expected_sha256) == 0) {
        OTA_LOGI("✓ SHA256 verification passed");
        return true;
    } else {
        OTA_LOGE("✗ SHA256 mismatch!");
        OTA_LOGE("Expected:   %s", expected_sha256);
        OTA_LOGE("Calculated: %s", calculated_sha);
        return false;
    }
}

void OtaManager::cleanup() {
    if (update_handle_) {
        esp_ota_abort(update_handle_);
        update_handle_ = 0;
    }
    bytes_written_ = 0;
}

esp_err_t OtaManager::cancel_update() {
    OTA_LOGW("Cancelling OTA update...");
    cleanup();
    state_ = OtaState::IDLE;
    return ESP_OK;
}

OtaResult OtaManager::update_from_buffer(const uint8_t* data, 
                                          size_t size,
                                          const char* expected_sha256) {
    OtaResult result = {false, ESP_FAIL, "Unknown error", 0, ""};

    if (!initialized_) {
        result.error_msg = "OTA manager not initialized";
        OTA_LOGE("%s", result.error_msg);
        return result;
    }

    if (!data || size == 0) {
        result.error_msg = "Invalid data or size";
        OTA_LOGE("%s", result.error_msg);
        return result;
    }

    OTA_LOGI("Starting OTA update from buffer (%u bytes)", size);

    // Comenzar actualización
    esp_err_t ret = begin_update();
    if (ret != ESP_OK) {
        result.error_code = ret;
        result.error_msg = "Failed to begin update";
        return result;
    }

    // Escribir datos
    ret = write_data(data, size);
    if (ret != ESP_OK) {
        result.error_code = ret;
        result.error_msg = "Failed to write data";
        cleanup();
        return result;
    }

    result.bytes_written = bytes_written_;

    // Finalizar
    ret = end_update();
    if (ret != ESP_OK) {
        result.error_code = ret;
        result.error_msg = "Failed to end update";
        cleanup();
        return result;
    }

    // Verificar SHA256 si se proporcionó
    if (expected_sha256 && !verify_sha256(expected_sha256)) {
        result.error_msg = "SHA256 verification failed";
        state_ = OtaState::ERROR;
        return result;
    }

    result.success = true;
    result.error_code = ESP_OK;
    result.error_msg = "Update successful";

    OTA_LOGI("✓ OTA update from buffer completed successfully");

    return result;
}

// Callback para progreso HTTP
static esp_err_t http_event_handler(esp_http_client_event_t *evt) {
    switch (evt->event_id) {
        case HTTP_EVENT_ON_DATA:
            if (!esp_http_client_is_chunked_response(evt->client)) {
                // Log progress
            }
            break;
        default:
            break;
    }
    return ESP_OK;
}

OtaResult OtaManager::update_from_url(const char* url, 
                                       const char* expected_sha256,
                                       OtaProgressCallback progress_cb) {
    OtaResult result = {false, ESP_FAIL, "Unknown error", 0, ""};

    if (!initialized_) {
        result.error_msg = "OTA manager not initialized";
        OTA_LOGE("%s", result.error_msg);
        return result;
    }

    if (!url || strlen(url) == 0) {
        result.error_msg = "Invalid URL";
        OTA_LOGE("%s", result.error_msg);
        return result;
    }

    OTA_LOGI("Starting OTA update from URL: %s", url);
    state_ = OtaState::DOWNLOADING;

    // Configurar cliente HTTP
    esp_http_client_config_t config = {};
    config.url = url;
    config.event_handler = http_event_handler;
    config.keep_alive_enable = true;
    config.timeout_ms = 30000; // 30 segundos

    // Ejecutar actualización HTTPS OTA
    esp_https_ota_config_t ota_config = {};
    ota_config.http_config = &config;

    esp_err_t ret = esp_https_ota(&ota_config);
    
    if (ret == ESP_OK) {
        result.success = true;
        result.error_code = ESP_OK;
        result.error_msg = "Update successful";
        state_ = OtaState::READY_TO_BOOT;
        
        OTA_LOGI("✓ OTA update from URL completed successfully");
        OTA_LOGI("Rebooting in 3 seconds...");
        
        vTaskDelay(pdMS_TO_TICKS(3000));
        esp_restart();
    } else {
        result.error_code = ret;
        result.error_msg = esp_err_to_name(ret);
        state_ = OtaState::ERROR;
        
        OTA_LOGE("OTA update failed: %s", result.error_msg);
    }

    return result;
}
