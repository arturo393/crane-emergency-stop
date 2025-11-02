#pragma once
#include <stdint.h>
#include <unistd.h> // for usleep

#define pdMS_TO_TICKS(x) (x)
typedef uint32_t TickType_t;

inline TickType_t xTaskGetTickCount() {
    return 0; // No es relevante para estos tests
}

inline void vTaskDelay(const TickType_t xTicksToDelay) {
    usleep(xTicksToDelay * 1000);
}
