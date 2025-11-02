/**
 * @file sd_logger.h
 * @brief Sistema de logging persistente a SD card con rotación automática
 * 
 * Características:
 * - Logs categorizados (INFO, WARN, ERROR, DEBUG)
 * - Rotación automática por tamaño (max 1MB por archivo)
 * - Auto-borrado de logs antiguos (mantiene últimos 10 archivos)
 * - Timestamps en cada entrada
 * - Thread-safe con mutex
 */

#ifndef SD_LOGGER_H
#define SD_LOGGER_H

#include <stdio.h>
#include <stdint.h>
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "esp_vfs_fat.h"
#include "sdmmc_cmd.h"

// Configuración de logging
#define SD_MOUNT_POINT "/sdcard"
#define LOG_FILE_PREFIX "gateway_"
#define LOG_FILE_EXT ".log"
#define MAX_LOG_FILE_SIZE (1024 * 1024)  // 1 MB por archivo
#define MAX_LOG_FILES 10                  // Mantener últimos 10 archivos
#define LOG_BUFFER_SIZE 256

// Niveles de log
typedef enum {
    SD_LOG_DEBUG = 0,
    SD_LOG_INFO,
    SD_LOG_WARN,
    SD_LOG_ERROR
} sd_log_level_t;

class SDLogger {
public:
    SDLogger();
    ~SDLogger();
    
    /**
     * @brief Inicializa el sistema de SD card
     * @return true si se inicializó correctamente
     */
    bool init();
    
    /**
     * @brief Detiene y desmonta la SD card
     */
    void deinit();
    
    /**
     * @brief Escribe un log en la SD card
     * @param level Nivel de log
     * @param tag Tag/módulo del log
     * @param format Formato printf
     * @param ... Argumentos variables
     */
    void log(sd_log_level_t level, const char* tag, const char* format, ...);
    
    /**
     * @brief Obtiene información del uso de la SD
     * @param total_mb Puntero para almacenar espacio total en MB
     * @param used_mb Puntero para almacenar espacio usado en MB
     * @return true si se obtuvo la información
     */
    bool get_disk_info(uint32_t* total_mb, uint32_t* used_mb);
    
    /**
     * @brief Fuerza la rotación del archivo de log actual
     */
    void rotate_log();
    
    /**
     * @brief Limpia logs antiguos (mantiene solo MAX_LOG_FILES)
     */
    void cleanup_old_logs();
    
    /**
     * @brief Verifica si la SD está montada y funcionando
     */
    bool is_ready() const { return sd_mounted_; }
    
private:
    bool sd_mounted_;
    FILE* current_log_file_;
    uint32_t current_log_size_;
    uint32_t log_file_counter_;
    SemaphoreHandle_t log_mutex_;
    sdmmc_card_t* card_;
    
    /**
     * @brief Abre un nuevo archivo de log
     * @return true si se abrió correctamente
     */
    bool open_new_log_file();
    
    /**
     * @brief Cierra el archivo de log actual
     */
    void close_current_log();
    
    /**
     * @brief Obtiene el nombre del archivo de log actual
     * @param buffer Buffer de salida
     * @param size Tamaño del buffer
     */
    void get_log_filename(char* buffer, size_t size);
    
    /**
     * @brief Cuenta cuántos archivos de log existen
     * @return Número de archivos de log
     */
    int count_log_files();
    
    /**
     * @brief Convierte nivel de log a string
     */
    const char* level_to_string(sd_log_level_t level);
};

// Macros de conveniencia
#define SD_LOGD(tag, format, ...) if(sd_logger) sd_logger->log(SD_LOG_DEBUG, tag, format, ##__VA_ARGS__)
#define SD_LOGI(tag, format, ...) if(sd_logger) sd_logger->log(SD_LOG_INFO, tag, format, ##__VA_ARGS__)
#define SD_LOGW(tag, format, ...) if(sd_logger) sd_logger->log(SD_LOG_WARN, tag, format, ##__VA_ARGS__)
#define SD_LOGE(tag, format, ...) if(sd_logger) sd_logger->log(SD_LOG_ERROR, tag, format, ##__VA_ARGS__)

// Instancia global (declarada en sd_logger.cpp)
extern SDLogger* sd_logger;

#endif // SD_LOGGER_H
