/**
 * @file test_cia402.cpp
 * @brief Tests nativos para CiA 402 State Machine
 * 
 * Estos tests ejecutan el código C++ REAL del ESP32 en tu Mac,
 * sin necesidad de hardware físico.
 * 
 * Compilar:
 *   cd esp32_gateway/test/native
 *   mkdir build && cd build
 *   cmake ..
 *   make
 *   ./test_cia402
 */

#include <iostream>
#include <iomanip>
#include <cassert>
#include <vector>

// Código REAL del ESP32
#include "cia402.h"

// Colores para output
#define COLOR_RESET   "\033[0m"
#define COLOR_GREEN   "\033[32m"
#define COLOR_RED     "\033[31m"
#define COLOR_YELLOW  "\033[33m"
#define COLOR_BLUE    "\033[34m"

// Helper para imprimir estado
std::string state_to_string(Cia402State state) {
    switch(state) {
        case Cia402State::NotReadyToSwitchOn: return "NOT_READY_TO_SWITCH_ON";
        case Cia402State::SwitchOnDisabled: return "SWITCH_ON_DISABLED";
        case Cia402State::ReadyToSwitchOn: return "READY_TO_SWITCH_ON";
        case Cia402State::SwitchedOn: return "SWITCHED_ON";
        case Cia402State::OperationEnabled: return "OPERATION_ENABLED";
        case Cia402State::QuickStopActive: return "QUICK_STOP_ACTIVE";
        case Cia402State::FaultReactionActive: return "FAULT_REACTION_ACTIVE";
        case Cia402State::Fault: return "FAULT";
        default: return "UNKNOWN";
    }
}

// Test counter
int tests_passed = 0;
int tests_failed = 0;

// Macro para tests
#define TEST_ASSERT(condition, message) \
    if (condition) { \
        std::cout << COLOR_GREEN << "  ✅ " << message << COLOR_RESET << "\n"; \
        tests_passed++; \
    } else { \
        std::cout << COLOR_RED << "  ❌ " << message << COLOR_RESET << "\n"; \
        tests_failed++; \
    }

#define TEST_SECTION(name) \
    std::cout << "\n" << COLOR_BLUE << "▶ " << name << COLOR_RESET << "\n";

// Test: Estado inicial
void test_initial_state() {
    TEST_SECTION("Test 1: Estado Inicial");
    
    Cia402Controller cia402;
    
    Cia402State initial_state = cia402.state();
    std::cout << "  Estado inicial: " << state_to_string(initial_state) << "\n";
    
    TEST_ASSERT(
        initial_state == Cia402State::NotReadyToSwitchOn,
        "Estado inicial debe ser NOT_READY_TO_SWITCH_ON"
    );
    
    uint16_t status = cia402.status_word();
    std::cout << "  Status Word: 0x" << std::hex << std::setw(4) << std::setfill('0') << status << std::dec << "\n";
}

// Test: Transición Shutdown (NOT_READY -> READY_TO_SWITCH_ON)
void test_shutdown_transition() {
    TEST_SECTION("Test 2: Transición Shutdown");
    
    Cia402Controller cia402;
    
    // Control Word: Shutdown (0x0006)
    // Bits: 0000 0000 0000 0110
    //       bit 0 (Switch On) = 0
    //       bit 1 (Enable Voltage) = 1
    //       bit 2 (Quick Stop) = 1
    //       bit 3 (Enable Operation) = 0
    uint16_t control_word = 0x0006;
    
    std::cout << "  Enviando Control Word: 0x" << std::hex << std::setw(4) << std::setfill('0') << control_word << std::dec << "\n";
    
    cia402.process_control_word(control_word);
    
    Cia402State new_state = cia402.state();
    std::cout << "  Nuevo estado: " << state_to_string(new_state) << "\n";
    
    TEST_ASSERT(
        new_state == Cia402State::ReadyToSwitchOn,
        "Después de Shutdown debe estar en READY_TO_SWITCH_ON"
    );
}

// Test: Transición Switch On (READY -> SWITCHED_ON)
void test_switch_on_transition() {
    TEST_SECTION("Test 3: Transición Switch On");
    
    Cia402Controller cia402;
    
    // Primero Shutdown
    cia402.process_control_word(0x0006);
    
    // Luego Switch On (0x0007)
    // Bits: 0000 0000 0000 0111
    //       bit 0 (Switch On) = 1
    //       bit 1 (Enable Voltage) = 1
    //       bit 2 (Quick Stop) = 1
    uint16_t control_word = 0x0007;
    
    std::cout << "  Enviando Control Word: 0x" << std::hex << std::setw(4) << std::setfill('0') << control_word << std::dec << "\n";
    
    cia402.process_control_word(control_word);
    
    Cia402State new_state = cia402.state();
    std::cout << "  Nuevo estado: " << state_to_string(new_state) << "\n";
    
    TEST_ASSERT(
        new_state == Cia402State::SwitchedOn,
        "Después de Switch On debe estar en SWITCHED_ON"
    );
}

// Test: Transición Enable Operation (SWITCHED_ON -> OPERATION_ENABLED)
void test_enable_operation_transition() {
    TEST_SECTION("Test 4: Transición Enable Operation");
    
    Cia402Controller cia402;
    
    // Secuencia completa: Shutdown -> Switch On -> Enable Operation
    cia402.process_control_word(0x0006);  // Shutdown
    cia402.process_control_word(0x0007);  // Switch On
    
    // Enable Operation (0x000F)
    // Bits: 0000 0000 0000 1111
    //       bit 0 (Switch On) = 1
    //       bit 1 (Enable Voltage) = 1
    //       bit 2 (Quick Stop) = 1
    //       bit 3 (Enable Operation) = 1
    uint16_t control_word = 0x000F;
    
    std::cout << "  Enviando Control Word: 0x" << std::hex << std::setw(4) << std::setfill('0') << control_word << std::dec << "\n";
    
    cia402.process_control_word(control_word);
    
    Cia402State new_state = cia402.state();
    std::cout << "  Nuevo estado: " << state_to_string(new_state) << "\n";
    
    TEST_ASSERT(
        new_state == Cia402State::OperationEnabled,
        "Después de Enable Operation debe estar en OPERATION_ENABLED"
    );
    
    uint16_t status = cia402.status_word();
    std::cout << "  Status Word: 0x" << std::hex << std::setw(4) << std::setfill('0') << status << std::dec << "\n";
}

// Test: Secuencia completa de startup
void test_complete_startup_sequence() {
    TEST_SECTION("Test 5: Secuencia Completa de Startup");
    
    Cia402Controller cia402;
    
    struct Transition {
        uint16_t control_word;
        Cia402State expected_state;
        const char* description;
    };
    
    std::vector<Transition> sequence = {
        {0x0006, Cia402State::ReadyToSwitchOn, "Shutdown"},
        {0x0007, Cia402State::SwitchedOn, "Switch On"},
        {0x000F, Cia402State::OperationEnabled, "Enable Operation"}
    };
    
    for (const auto& transition : sequence) {
        std::cout << "\n  Paso: " << transition.description << "\n";
        std::cout << "    Control Word: 0x" << std::hex << std::setw(4) << std::setfill('0') 
                  << transition.control_word << std::dec << "\n";
        
        cia402.process_control_word(transition.control_word);
        
        Cia402State current_state = cia402.state();
        std::cout << "    Estado resultante: " << state_to_string(current_state) << "\n";
        
        bool success = (current_state == transition.expected_state);
        std::cout << "    " << (success ? COLOR_GREEN "✅" : COLOR_RED "❌") 
                  << " Esperado: " << state_to_string(transition.expected_state) 
                  << COLOR_RESET << "\n";
        
        if (success) tests_passed++;
        else tests_failed++;
    }
}

// Test: Quick Stop
void test_quick_stop() {
    TEST_SECTION("Test 6: Quick Stop");
    
    Cia402Controller cia402;
    
    // Llegar a OPERATION_ENABLED
    cia402.process_control_word(0x0006);  // Shutdown
    cia402.process_control_word(0x0007);  // Switch On
    cia402.process_control_word(0x000F);  // Enable Operation
    
    std::cout << "  Estado antes de Quick Stop: " << state_to_string(cia402.state()) << "\n";
    
    // Quick Stop (0x0002)
    // Bit 2 (Quick Stop) = 0
    uint16_t control_word = 0x0002;
    
    std::cout << "  Enviando Quick Stop: 0x" << std::hex << std::setw(4) << std::setfill('0') 
              << control_word << std::dec << "\n";
    
    cia402.process_control_word(control_word);
    
    Cia402State new_state = cia402.state();
    std::cout << "  Estado después de Quick Stop: " << state_to_string(new_state) << "\n";
    
    TEST_ASSERT(
        new_state == Cia402State::QuickStopActive,
        "Después de Quick Stop debe estar en QUICK_STOP_ACTIVE"
    );
}

// Main para Cia402
int main_cia402() {
    std::cout << "\n";
    std::cout << "========================================\n";
    std::cout << "  Tests Nativos CiA 402 State Machine\n";
    std::cout << "  Ejecutando código C++ REAL del ESP32\n";
    std::cout << "========================================\n";
    
    // Ejecutar tests
    test_initial_state();
    test_shutdown_transition();
    test_switch_on_transition();
    test_enable_operation_transition();
    test_complete_startup_sequence();
    test_quick_stop();
    
    // Resumen
    std::cout << "\n";
    std::cout << "========================================\n";
    std::cout << "  RESUMEN DE TESTS\n";
    std::cout << "========================================\n";
    std::cout << COLOR_GREEN << "  ✅ Pasados: " << tests_passed << COLOR_RESET << "\n";
    std::cout << COLOR_RED   << "  ❌ Fallidos: " << tests_failed << COLOR_RESET << "\n";
    std::cout << "  Total: " << (tests_passed + tests_failed) << "\n";
    std::cout << "========================================\n\n";
    
    // Exit code
    return (tests_failed == 0) ? 0 : 1;
}
