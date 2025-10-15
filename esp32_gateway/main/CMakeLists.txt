# CMakeLists.txt para el componente main

idf_component_register(
    SRCS 
        "main.cpp"
        "wifi_manager.cpp"
        "can_manager.cpp"
    INCLUDE_DIRS "."
    REQUIRES 
        nvs_flash
        esp_wifi
        esp_netif
        esp_eth
        driver
)
