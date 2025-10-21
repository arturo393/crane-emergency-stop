#pragma once

#include <cstdint>

// Estados CiA 402 (simplificado)
enum class Cia402State : uint16_t {
    NotReadyToSwitchOn = 0,
    SwitchOnDisabled = 1,
    ReadyToSwitchOn = 2,
    SwitchedOn = 3,
    OperationEnabled = 4,
    QuickStopActive = 5,
    FaultReactionActive = 6,
    Fault = 7
};

class Cia402Controller {
public:
    Cia402Controller();

    // Procesa control word (RPDO1) y actualiza estado
    void process_control_word(uint16_t control_word);

    // Calcula status word (TPDO1) a partir del estado actual
    uint16_t status_word() const;

    Cia402State state() const { return state_; }

    // Resetea fallas
    void reset_fault();

private:
    Cia402State state_;
};
