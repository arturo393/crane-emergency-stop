# CMakeLists.txt para el componente main

# CMakeLists.txt SIMPLIFICADO - Solo lo esencial

idf_component_register(
    SRCS
        "main.cpp"
        "can_manager.cpp"
        "ethernet_manager.cpp"
        "wifi_manager.cpp"
        "config_manager.cpp"
        "auth_manager.cpp"
        "sd_logger.cpp"
        "ota_manager.cpp"
        "web_server.cpp"
        "../components/canopen/cia402.cpp"
    INCLUDE_DIRS
        "."
        "../components/canopen"
    REQUIRES
        nvs_flash
        driver
        esp_eth
        esp_event
        esp_netif
        esp_wifi
        fatfs
        sdmmc
        app_update
        esp_https_ota
        esp_http_server
)
