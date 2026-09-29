# Registra el componente principal con todos sus .c y la carpeta de cabeceras.
idf_component_register(
    SRCS
        "main.c"
        "app_tasks.c"
        "buttons.c"
        "counter.c"
        "display.c"
        "system_state.c"
    INCLUDE_DIRS "../include"
    REQUIRES esp_driver_gpio log freertos
)
