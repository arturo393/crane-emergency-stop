#pragma once
#include <cstdint>

struct PdoIds {
    uint16_t rpdo1; // RPDO1 COB-ID base 0x200 + node
    uint16_t tpdo1; // TPDO1 COB-ID base 0x180 + node
    uint16_t heartbeat; // 0x700 + node
};

inline PdoIds make_pdo_ids(uint8_t node_id) {
    return PdoIds{ (uint16_t)(0x200 + node_id), (uint16_t)(0x180 + node_id), (uint16_t)(0x700 + node_id) };
}

inline uint16_t parse_control_word(const uint8_t data[8]) {
    return (uint16_t)data[0] | ((uint16_t)data[1] << 8);
}

inline void build_status_word(uint16_t status, uint8_t out[8]) {
    out[0] = (uint8_t)(status & 0xFF);
    out[1] = (uint8_t)((status >> 8) & 0xFF);
    // rest zero
    for (int i = 2; i < 8; ++i) out[i] = 0;
}
