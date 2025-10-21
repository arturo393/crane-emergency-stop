#include "cia402.h"

Cia402Controller::Cia402Controller() : state_(Cia402State::SwitchOnDisabled) {}

void Cia402Controller::process_control_word(uint16_t cw) {
    // Bits CiA402 típicos usados
    // 0: Switch on, 1: Enable voltage, 2: Quick stop, 3: Enable operation, 7: Fault reset

    // Fault reset
    if (cw & (1 << 7)) {
        if (state_ == Cia402State::Fault) {
            state_ = Cia402State::SwitchOnDisabled;
            return;
        }
    }

    switch (state_) {
        case Cia402State::SwitchOnDisabled:
            // Forzar transición rápida a ReadyToSwitchOn con 0x0007 (enable voltage + quick stop inactive + switch on)
            if ((cw & 0x0007) == 0x0007) {
                state_ = Cia402State::ReadyToSwitchOn;
            }
            break;
        case Cia402State::QuickStopActive:
            if ((cw & 0x0007) == 0x0007) {
                state_ = Cia402State::ReadyToSwitchOn;
            }
            break;
        case Cia402State::ReadyToSwitchOn:
            if ((cw & 0x000F) == 0x000F) { // + enable operation
                state_ = Cia402State::OperationEnabled;
            } else if ((cw & 0x0003) == 0x0001) {
                state_ = Cia402State::SwitchedOn;
            }
            break;
        case Cia402State::SwitchedOn:
            if ((cw & 0x000F) == 0x000F) {
                state_ = Cia402State::OperationEnabled;
            }
            break;
        case Cia402State::OperationEnabled:
            if ((cw & (1 << 2)) == 0) { // Quick stop asserted
                state_ = Cia402State::QuickStopActive;
            }
            break;
        case Cia402State::FaultReactionActive:
            state_ = Cia402State::Fault;
            break;
        case Cia402State::Fault:
        case Cia402State::NotReadyToSwitchOn:
        default:
            break;
    }
}

uint16_t Cia402Controller::status_word() const {
    // Composición mínima del status word según estado
    // Bits típicos: 0 ready_to_switch_on, 1 switched_on, 2 operation_enabled, 3 fault, 5 quick_stop, 6 switch_on_disabled
    uint16_t sw = 0;
    switch (state_) {
        case Cia402State::SwitchOnDisabled:
            sw |= (1 << 6);
            break;
        case Cia402State::ReadyToSwitchOn:
            sw |= (1 << 0);
            break;
        case Cia402State::SwitchedOn:
            sw |= (1 << 0) | (1 << 1);
            break;
        case Cia402State::OperationEnabled:
            sw |= (1 << 0) | (1 << 1) | (1 << 2);
            break;
        case Cia402State::QuickStopActive:
            sw |= (1 << 5);
            break;
        case Cia402State::FaultReactionActive:
        case Cia402State::Fault:
            sw |= (1 << 3);
            break;
        case Cia402State::NotReadyToSwitchOn:
        default:
            break;
    }
    return sw;
}

void Cia402Controller::reset_fault() {
    if (state_ == Cia402State::Fault) {
        state_ = Cia402State::SwitchOnDisabled;
    }
}
