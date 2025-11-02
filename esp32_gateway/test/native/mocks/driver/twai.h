#pragma once
#include "../esp_err.h"
#include "freertos/FreeRTOS.h" // Para TickType_t
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    TWAI_MODE_NORMAL,
    TWAI_MODE_NO_ACK,
    TWAI_MODE_LISTEN_ONLY
} twai_mode_t;

typedef struct {
    twai_mode_t mode;
    int32_t tx_io;
    int32_t rx_io;
    int32_t clkout_io;
    int32_t bus_off_io;
    uint32_t tx_queue_len;
    uint32_t rx_queue_len;
    uint32_t alerts_enabled;
    uint32_t clkout_divider;
    uint32_t intr_flags;
} twai_general_config_t;

#define TWAI_GENERAL_CONFIG_DEFAULT(tx, rx, mode_val) { \
    .mode = mode_val, \
    .tx_io = tx, .rx_io = rx, \
    .clkout_io = -1, .bus_off_io = -1, \
    .tx_queue_len = 5, .rx_queue_len = 5, \
    .alerts_enabled = 0, .clkout_divider = 0, .intr_flags = 0 \
}

typedef struct {
    uint32_t brp;
    uint8_t tseg1;
    uint8_t tseg2;
    uint8_t sjw;
    bool triple_sampling;
} twai_timing_config_t;

typedef struct {
    uint32_t acceptance_code;
    uint32_t acceptance_mask;
    bool single_filter;
} twai_filter_config_t;

#define TWAI_FILTER_CONFIG_ACCEPT_ALL() {.acceptance_code = 0, .acceptance_mask = 0, .single_filter = true}

typedef struct {
    uint32_t identifier;
    uint8_t data_length_code;
    uint32_t flags;
    uint8_t data[8];
    // Ignoramos otros campos por simplicidad
} twai_message_t;

#define TWAI_MSG_FLAG_NONE 0

#define TWAI_TIMING_CONFIG_250KBITS() {.brp = 32, .tseg1 = 15, .tseg2 = 4, .sjw = 3, .triple_sampling = false}

esp_err_t twai_driver_install(const twai_general_config_t *g_config, const twai_timing_config_t *t_config, const twai_filter_config_t *f_config);
esp_err_t twai_driver_uninstall(void);
esp_err_t twai_start(void);
esp_err_t twai_stop(void);
esp_err_t twai_transmit(const twai_message_t *message, TickType_t ticks_to_wait);
esp_err_t twai_receive(twai_message_t *message, TickType_t ticks_to_wait);

#ifdef __cplusplus
}
#endif
