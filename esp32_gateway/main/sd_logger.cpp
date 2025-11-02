/**
 * @file sd_logger.cpp
 * @brief Implementación del sistema de logging a SD card
 */

#include "sd_logger.h"
#include "esp_log.h"
#include "driver/sdmmc_host.h"
#include "driver/sdspi_host.h"
#include "driver/spi_common.h"
#include "hardware_config.h"
#include <string.h>
#include <time.h>
#include <sys/time.h>
#include <dirent.h>
#include <sys/stat.h>
#include <stdarg.h>
#include <unistd.h>

static const char *TAG = "SD_LOGGER";

// Instancia global
SDLogger* sd_logger = nullptr;

SDLogger::SDLogger() : 
    sd_mounted_(false),
    current_log_file_(nullptr),
    current_log_size_(0),
    log_file_counter_(0),
    log_mutex_(nullptr),
    card_(nullptr) {
    
    log_mutex_ = xSemaphoreCreateMutex();
}

SDLogger::~SDLogger() {
    deinit();
    if (log_mutex_) {
        vSemaphoreDelete(log_mutex_);
    }
}

bool SDLogger::init() {
    ESP_LOGI(TAG, "Inicializando SD card logger...");
    
    // Configuración del host SPI para SD card
    sdmmc_host_t host = SDSPI_HOST_DEFAULT();
    
    spi_bus_config_t bus_cfg = {
        .mosi_io_num = PIN_SD_MOSI,
        .miso_io_num = PIN_SD_MISO,
        .sclk_io_num = PIN_SD_CLK,
        .quadwp_io_num = -1,
        .quadhd_io_num = -1,
        .max_transfer_sz = 4000,
    };
    
    esp_err_t ret = spi_bus_initialize((spi_host_device_t)host.slot, &bus_cfg, SDSPI_DEFAULT_DMA);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to initialize SPI bus: %s", esp_err_to_name(ret));
        return false;
    }
    
    // Configuración del slot de SD
    sdspi_device_config_t slot_config = SDSPI_DEVICE_CONFIG_DEFAULT();
    slot_config.gpio_cs = static_cast<gpio_num_t>(PIN_SD_CS);
    slot_config.host_id = (spi_host_device_t)host.slot;
    
    // Opciones de montaje
    esp_vfs_fat_sdmmc_mount_config_t mount_config = {
        .format_if_mount_failed = true,
        .max_files = 5,
        .allocation_unit_size = 16 * 1024
    };
    
    ret = esp_vfs_fat_sdspi_mount(SD_MOUNT_POINT, &host, &slot_config, &mount_config, &card_);
    
    if (ret != ESP_OK) {
        if (ret == ESP_FAIL) {
            ESP_LOGE(TAG, "Failed to mount filesystem");
        } else {
            ESP_LOGE(TAG, "Failed to initialize SD card: %s", esp_err_to_name(ret));
        }
        return false;
    }
    
    sd_mounted_ = true;
    
    // Imprimir info de la tarjeta
    sdmmc_card_print_info(stdout, card_);
    
    // Limpiar logs antiguos al inicio
    cleanup_old_logs();
    
    // Abrir primer archivo de log
    if (!open_new_log_file()) {
        ESP_LOGE(TAG, "Failed to create initial log file");
        deinit();
        return false;
    }
    
    ESP_LOGI(TAG, "✅ SD card logger inicializado correctamente");
    log(SD_LOG_INFO, TAG, "=== SD Logger iniciado ===");
    
    return true;
}

void SDLogger::deinit() {
    if (!sd_mounted_) {
        return;
    }
    
    ESP_LOGI(TAG, "Desmontando SD card...");
    
    close_current_log();
    
    esp_vfs_fat_sdcard_unmount(SD_MOUNT_POINT, card_);
    spi_bus_free(SDSPI_DEFAULT_HOST);
    
    sd_mounted_ = false;
    ESP_LOGI(TAG, "SD card desmontada");
}

void SDLogger::log(sd_log_level_t level, const char* tag, const char* format, ...) {
    if (!sd_mounted_ || !current_log_file_) {
        return;
    }
    
    // Tomar mutex
    if (xSemaphoreTake(log_mutex_, pdMS_TO_TICKS(100)) != pdTRUE) {
        return;
    }
    
    // Obtener timestamp
    struct timeval tv;
    gettimeofday(&tv, NULL);
    time_t now = tv.tv_sec;
    struct tm timeinfo;
    localtime_r(&now, &timeinfo);
    
    char time_buffer[32];
    strftime(time_buffer, sizeof(time_buffer), "%Y-%m-%d %H:%M:%S", &timeinfo);
    
    // Formatear mensaje con timestamp y nivel
    char buffer[LOG_BUFFER_SIZE];
    int len = snprintf(buffer, sizeof(buffer), "[%s.%03ld] [%s] %s: ",
                       time_buffer, tv.tv_usec / 1000,
                       level_to_string(level), tag);
    
    // Agregar mensaje del usuario
    va_list args;
    va_start(args, format);
    len += vsnprintf(buffer + len, sizeof(buffer) - len, format, args);
    va_end(args);
    
    // Asegurar newline
    if (len < (int)sizeof(buffer) - 2 && buffer[len - 1] != '\n') {
        buffer[len++] = '\n';
        buffer[len] = '\0';
    }
    
    // Escribir a archivo
    size_t written = fwrite(buffer, 1, len, current_log_file_);
    fflush(current_log_file_);
    
    current_log_size_ += written;
    
    // Verificar si necesita rotación
    if (current_log_size_ >= MAX_LOG_FILE_SIZE) {
        ESP_LOGI(TAG, "Log file reached max size, rotating...");
        rotate_log();
    }
    
    xSemaphoreGive(log_mutex_);
}

void SDLogger::rotate_log() {
    close_current_log();
    cleanup_old_logs();
    open_new_log_file();
}

bool SDLogger::open_new_log_file() {
    char filename[64];
    get_log_filename(filename, sizeof(filename));
    
    current_log_file_ = fopen(filename, "a");
    if (!current_log_file_) {
        ESP_LOGE(TAG, "Failed to open log file: %s", filename);
        return false;
    }
    
    current_log_size_ = ftell(current_log_file_);
    log_file_counter_++;
    
    ESP_LOGI(TAG, "Opened log file: %s", filename);
    return true;
}

void SDLogger::close_current_log() {
    if (current_log_file_) {
        fclose(current_log_file_);
        current_log_file_ = nullptr;
        current_log_size_ = 0;
    }
}

void SDLogger::get_log_filename(char* buffer, size_t size) {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    time_t now = tv.tv_sec;
    struct tm timeinfo;
    localtime_r(&now, &timeinfo);
    
    snprintf(buffer, size, "%s/%s%04d%02d%02d_%02d%02d%02d%s",
             SD_MOUNT_POINT, LOG_FILE_PREFIX,
             timeinfo.tm_year + 1900, timeinfo.tm_mon + 1, timeinfo.tm_mday,
             timeinfo.tm_hour, timeinfo.tm_min, timeinfo.tm_sec,
             LOG_FILE_EXT);
}

void SDLogger::cleanup_old_logs() {
    DIR* dir = opendir(SD_MOUNT_POINT);
    if (!dir) {
        ESP_LOGW(TAG, "Cannot open SD directory for cleanup");
        return;
    }
    
    // Contar archivos de log
    int log_count = 0;
    struct dirent* entry;
    while ((entry = readdir(dir)) != NULL) {
        if (strstr(entry->d_name, LOG_FILE_PREFIX) && strstr(entry->d_name, LOG_FILE_EXT)) {
            log_count++;
        }
    }
    rewinddir(dir);
    
    // Si hay más de MAX_LOG_FILES, eliminar los más antiguos
    while (log_count > MAX_LOG_FILES) {
        time_t oldest_time = time(NULL);
        char oldest_file[384];  // Aumentado de 128 a 384 para evitar truncamiento
        oldest_file[0] = '\0';
        
        // Encontrar el archivo más antiguo
        while ((entry = readdir(dir)) != NULL) {
            if (strstr(entry->d_name, LOG_FILE_PREFIX) && strstr(entry->d_name, LOG_FILE_EXT)) {
                char filepath[384];  // Aumentado para evitar truncamiento
                snprintf(filepath, sizeof(filepath), "%s/%s", SD_MOUNT_POINT, entry->d_name);
                
                struct stat st;
                if (stat(filepath, &st) == 0) {
                    if (st.st_mtime < oldest_time) {
                        oldest_time = st.st_mtime;
                        strncpy(oldest_file, filepath, sizeof(oldest_file) - 1);
                        oldest_file[sizeof(oldest_file) - 1] = '\0';
                    }
                }
            }
        }
        
        // Eliminar el más antiguo
        if (oldest_file[0] != '\0') {
            if (unlink(oldest_file) == 0) {
                ESP_LOGI(TAG, "Deleted old log: %s", oldest_file);
                log_count--;
            } else {
                ESP_LOGW(TAG, "Failed to delete: %s", oldest_file);
                break;
            }
        }
        
        rewinddir(dir);
    }
    
    closedir(dir);
}

bool SDLogger::get_disk_info(uint32_t* total_mb, uint32_t* used_mb) {
    if (!sd_mounted_) {
        return false;
    }
    
    FATFS* fs;
    DWORD fre_clust;
    
    if (f_getfree("0:", &fre_clust, &fs) != FR_OK) {
        return false;
    }
    
    uint32_t total_sectors = (fs->n_fatent - 2) * fs->csize;
    uint32_t free_sectors = fre_clust * fs->csize;
    
    *total_mb = (total_sectors * fs->ssize) / (1024 * 1024);
    *used_mb = ((total_sectors - free_sectors) * fs->ssize) / (1024 * 1024);
    
    return true;
}

const char* SDLogger::level_to_string(sd_log_level_t level) {
    switch (level) {
        case SD_LOG_DEBUG: return "DEBUG";
        case SD_LOG_INFO:  return "INFO ";
        case SD_LOG_WARN:  return "WARN ";
        case SD_LOG_ERROR: return "ERROR";
        default:           return "?????";
    }
}
