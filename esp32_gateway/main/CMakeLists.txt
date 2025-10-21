# CMakeLists.txt para el componente main

idf_component_register(
    SRCS
        "main.cpp"
        "wifi_manager.cpp"
        "can_manager.cpp"
        "ethernet_manager.cpp"
        "config_manager.cpp"
        "../components/ota/ota_manager.cpp"
        "../components/canopen/cia402.cpp"
    INCLUDE_DIRS
        "."
        "../components/ota"
        "../components/canopen"
    REQUIRES
        nvs_flash
        esp_wifi
        esp_netif
        esp_eth
        driver
        mbedtls
        esp_http_client
        app_update
)
