# Device Integration Tests for EdgeBox-Lite
# These tests run ON the ESP32 hardware to validate hardware configuration

# Build only the test specified by TEST_COMPONENT variable
# Example: idf.py -DTEST_COMPONENT=test_auth_manager build
if(NOT DEFINED TEST_COMPONENT)
    set(TEST_COMPONENT "test_can_bus_init")  # Default test
endif()

message(STATUS "Building device test: ${TEST_COMPONENT}.cpp")

idf_component_register(
    SRCS 
        "${TEST_COMPONENT}.cpp"
    INCLUDE_DIRS 
        "."
        "../../main"
        "../../components/canopen"
    REQUIRES 
        driver
        esp_eth
        esp_netif
        unity
        nvs_flash
        esp_http_server
        app_update
        esp_https_ota
        fatfs
        sdmmc
        mbedtls
)

# Add Unity test framework
target_compile_definitions(${COMPONENT_LIB} PUBLIC UNITY_INCLUDE_CONFIG_H)
