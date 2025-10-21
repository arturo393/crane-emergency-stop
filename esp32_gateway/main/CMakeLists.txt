# CMakeLists.txt para el componente main

# CMakeLists.txt SIMPLIFICADO - Solo lo esencial

idf_component_register(
    SRCS
        "main.cpp"
        "can_manager.cpp"
        "../components/canopen/cia402.cpp"
    INCLUDE_DIRS
        "."
        "../components/canopen"
    REQUIRES
        nvs_flash
        driver
)
