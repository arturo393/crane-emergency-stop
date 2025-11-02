/**
 * @file auth_manager.h
 * @brief Gestor de autenticación para servidor TCP
 * 
 * Sistema simple de autenticación basado en token para
 * proteger el acceso al gateway ESP32.
 */

#ifndef AUTH_MANAGER_H
#define AUTH_MANAGER_H

#include <string.h>
#include <stdint.h>

// Token por defecto (debe cambiarse en producción)
#define DEFAULT_AUTH_TOKEN "D13-SECURE-2025"
#define MAX_TOKEN_LENGTH 64
#define MAX_AUTH_ATTEMPTS 3
#define AUTH_TIMEOUT_MS 5000

class AuthManager {
public:
    AuthManager();
    
    /**
     * @brief Configura el token de autenticación
     * @param token Nuevo token (máximo 64 caracteres)
     * @return true si se configuró correctamente
     */
    bool set_token(const char* token);
    
    /**
     * @brief Verifica si un token es válido
     * @param token Token a verificar
     * @return true si el token coincide
     */
    bool verify_token(const char* token);
    
    /**
     * @brief Obtiene el token actual (solo para debug - eliminar en producción)
     * @return Puntero al token actual
     */
    const char* get_token() const { return auth_token_; }
    
    /**
     * @brief Genera un nuevo token aleatorio
     * @param output Buffer de salida (mínimo 17 bytes)
     * @return true si se generó correctamente
     */
    bool generate_random_token(char* output, size_t len);
    
    /**
     * @brief Registra un intento fallido de autenticación
     * @param client_ip IP del cliente
     * @return true si aún se permiten más intentos
     */
    bool register_failed_attempt(uint32_t client_ip);
    
    /**
     * @brief Limpia intentos fallidos para una IP
     * @param client_ip IP del cliente
     */
    void clear_failed_attempts(uint32_t client_ip);
    
private:
    char auth_token_[MAX_TOKEN_LENGTH + 1];
    
    // Simple rate limiting (últimos 3 IPs con intentos fallidos)
    struct {
        uint32_t ip;
        uint8_t attempts;
        uint32_t last_attempt_time;
    } failed_attempts_[3];
};

#endif // AUTH_MANAGER_H
