#include <cassert>
#include <cstdio>
#include "../../main/can_manager.h"
#include "mocks/driver/twai.h" // Incluimos el mock

// Declaraciones adelantadas
extern int main_cia402();
int main_can_manager();

// Funciones de ayuda del mock
extern int mock_get_tx_buffer_size();
extern bool mock_get_last_tx_message(twai_message_t* msg);
extern void mock_clear_tx_buffer();

void test_can_manager_init() {
    printf("--- Test: CANManager Initialization ---\n");
    CANManager can_manager;
    
    esp_err_t result = can_manager.init(4, 5, 250000);
    assert(result == ESP_OK && "CANManager init should succeed");
    
    can_manager.stop();
    printf("✅ Passed\n\n");
}

void test_can_manager_send() {
    printf("--- Test: CANManager Send Message ---\n");
    CANManager can_manager;
    can_manager.init(4, 5, 250000);
    
    mock_clear_tx_buffer();
    assert(mock_get_tx_buffer_size() == 0 && "TX Buffer should be empty initially");

    uint8_t data[] = {0x01, 0x02};
    can_manager.send_message(0x123, data, sizeof(data));

    assert(mock_get_tx_buffer_size() == 1 && "TX Buffer should contain one message");

    twai_message_t sent_msg;
    bool found = mock_get_last_tx_message(&sent_msg);
    assert(found && "Should be able to retrieve sent message");
    assert(sent_msg.identifier == 0x123 && "Message ID should match");
    assert(sent_msg.data_length_code == 2 && "Message DLC should match");
    assert(sent_msg.data[0] == 0x01 && "Message data[0] should match");
    assert(sent_msg.data[1] == 0x02 && "Message data[1] should match");

    can_manager.stop();
    printf("✅ Passed\n\n");
}

int main() {
    printf("\n====================================\n");
    printf("   Running All Native Tests\n");
    printf("====================================\n");

    // Llama a los puntos de entrada de cada test
    main_cia402();
    main_can_manager();

    printf("\n====================================\n");
    printf("   All Tests Completed\n");
    printf("====================================\n");

    return 0;
}

int main_can_manager() {
    printf("\n====================================\n");
    printf("   Testing CANManager Component\n");
    printf("====================================\n");
    
    test_can_manager_init();
    test_can_manager_send();

    return 0;
}
