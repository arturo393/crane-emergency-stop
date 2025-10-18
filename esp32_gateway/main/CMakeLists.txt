# CMakeLists.txt para el componente main

idf_component_register(
    SRCS
        "main.cpp"
        "../components/network/ethernet_manager.cpp"
        "../components/ota/ota_manager.cpp"
        "../components/canopen/can_manager.cpp"
        "../components/tcp_server/tcp_server_manager.cpp"
    INCLUDE_DIRS
        "."
        "../components/network"
        "../components/ota"
        "../components/canopen"
        "../components/tcp_server"
    REQUIRES
        nvs_flash
        esp_wifi
        esp_netif
        esp_eth
        driver
        json
)
