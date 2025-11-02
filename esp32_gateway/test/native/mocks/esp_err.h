#pragma once

#ifdef __cplusplus
extern "C" {
#endif

typedef int esp_err_t;

#define ESP_OK          0
#define ESP_FAIL        -1
#define ESP_ERR_INVALID_ARG -2
#define ESP_ERR_INVALID_STATE -3
#define ESP_ERR_NOT_FOUND -4
#define ESP_ERR_TIMEOUT -5

const char* esp_err_to_name(esp_err_t code);

#define ESP_ERROR_CHECK(x)                                      \
    do {                                                        \
        esp_err_t err_rc_ = (x);                                \
        if (err_rc_ != ESP_OK) {                                \
            printf("ESP_ERROR_CHECK failed: %s\n", esp_err_to_name(err_rc_)); \
        }                                                       \
    } while(0)


#ifdef __cplusplus
}
#endif
