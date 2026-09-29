# CMake raíz del proyecto (igual al del ejemplo FOUR_LEDS)
cmake_minimum_required(VERSION 3.16.0)

# La práctica exige la carpeta src/ (no main/): se registra como componente
# para que también compile con la extensión ESP-IDF / idf.py.
set(EXTRA_COMPONENT_DIRS "${CMAKE_CURRENT_LIST_DIR}/src")

include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(Practica1_DobleContador_FreeRTOS)
