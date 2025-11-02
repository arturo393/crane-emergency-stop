/**
 * @file auth_manager.cpp
 * @brief Implementación del gestor de autenticación
 */

#include "auth_manager.h"
#include "esp_log.h"
#include "esp_random.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <stdio.h>

static const char *TAG = "AUTH_MGR";

AuthManager::AuthManager() {
    // Inicializar con token por defecto
    strncpy(auth_token_, DEFAULT_AUTH_TOKEN, MAX_TOKEN_LENGTH);
    auth_token_[MAX_TOKEN_LENGTH] = '\0';
    
    // Limpiar tabla de intentos fallidos
    for (int i = 0; i < 3; i++) {
        failed_attempts_[i].ip = 0;
        failed_attempts_[i].attempts = 0;
        failed_attempts_[i].last_attempt_time = 0;
    }
    
    ESP_LOGI(TAG, "AuthManager inicializado");
    ESP_LOGW(TAG, "⚠️  Usando token por defecto. Cambiar en producción!");
}

bool AuthManager::set_token(const char* token) {
    if (token == nullptr || strlen(token) == 0) {
        ESP_LOGE(TAG, "Token inválido (nulo o vacío)");
        return false;
    }
    
    if (strlen(token) > MAX_TOKEN_LENGTH) {
        ESP_LOGE(TAG, "Token demasiado largo (máx %d caracteres)", MAX_TOKEN_LENGTH);
        return false;
    }
    
    strncpy(auth_token_, token, MAX_TOKEN_LENGTH);
    auth_token_[MAX_TOKEN_LENGTH] = '\0';
    
    ESP_LOGI(TAG, "Token actualizado correctamente");
    return true;
}

bool AuthManager::verify_token(const char* token) {
    if (token == nullptr) {
        return false;
    }
    
    // Comparación constante en tiempo para evitar timing attacks
    size_t token_len = strlen(token);
    size_t auth_len = strlen(auth_token_);
    
    if (token_len != auth_len) {
        return false;
    }
    
    uint8_t diff = 0;
    for (size_t i = 0; i < auth_len; i++) {
        diff |= (token[i] ^ auth_token_[i]);
    }
    
    return (diff == 0);
}

bool AuthManager::generate_random_token(char* output, size_t len) {
    if (output == nullptr || len < 17) {
        ESP_LOGE(TAG, "Buffer de salida inválido");
        return false;
    }
    
    // Generar 8 bytes aleatorios (16 caracteres hex + null terminator)
    uint32_t random1 = esp_random();
    uint32_t random2 = esp_random();
    
    snprintf(output, len, "%08lX%08lX", 
             (unsigned long)random1, 
             (unsigned long)random2);
    
    ESP_LOGI(TAG, "Token aleatorio generado");
    return true;
}

bool AuthManager::register_failed_attempt(uint32_t client_ip) {
    uint32_t current_time = xTaskGetTickCount() * portTICK_PERIOD_MS;
    
    // Buscar entrada existente para esta IP
    for (int i = 0; i < 3; i++) {
        if (failed_attempts_[i].ip == client_ip) {
            // Resetear si pasó más de 5 minutos
            if ((current_time - failed_attempts_[i].last_attempt_time) > 300000) {
                failed_attempts_[i].attempts = 1;
            } else {
                failed_attempts_[i].attempts++;
            }
            failed_attempts_[i].last_attempt_time = current_time;
            
            if (failed_attempts_[i].attempts >= MAX_AUTH_ATTEMPTS) {
                ESP_LOGW(TAG, "⚠️  IP bloqueada temporalmente: %lu.%lu.%lu.%lu",
                         (client_ip >> 24) & 0xFF,
                         (client_ip >> 16) & 0xFF,
                         (client_ip >> 8) & 0xFF,
                         client_ip & 0xFF);
                return false;
            }
            return true;
        }
    }
    
    // No encontrada, buscar slot libre o más antiguo
    int oldest_idx = 0;
    uint32_t oldest_time = failed_attempts_[0].last_attempt_time;
    
    for (int i = 0; i < 3; i++) {
        if (failed_attempts_[i].ip == 0) {
            oldest_idx = i;
            break;
        }
        if (failed_attempts_[i].last_attempt_time < oldest_time) {
            oldest_time = failed_attempts_[i].last_attempt_time;
            oldest_idx = i;
        }
    }
    
    failed_attempts_[oldest_idx].ip = client_ip;
    failed_attempts_[oldest_idx].attempts = 1;
    failed_attempts_[oldest_idx].last_attempt_time = current_time;
    
    return true;
}

void AuthManager::clear_failed_attempts(uint32_t client_ip) {
    for (int i = 0; i < 3; i++) {
        if (failed_attempts_[i].ip == client_ip) {
            failed_attempts_[i].ip = 0;
            failed_attempts_[i].attempts = 0;
            failed_attempts_[i].last_attempt_time = 0;
            ESP_LOGI(TAG, "Intentos fallidos limpiados para IP");
            return;
        }
    }
}
