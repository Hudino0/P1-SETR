# Práctica – Doble contador BCD con FreeRTOS (Lenguaje C)

Código base en C para ESP-IDF.

Objetivos didácticos principales:
- `struct` y `enum`
- apuntadores
- `pvParameters`
- `TaskHandle_t`
- `vTaskSuspend()` / `vTaskResume()`
- Task Manager
- reutilización de una misma función de tarea con parámetros distintos

Restricciones:
- Sin queues
- Sin semáforos
- Sin mutex
- Sin Event Groups
- Sin Software Timers

Modo:
- `COUPLING_OPPOSITE`: Counter1 y Counter2 cuentan en sentidos opuestos.
- `COUPLING_SAME`: ambos cuentan en el sentido seleccionado.

Nota de hardware:
El código base supone dos displays de 7 segmentos multiplexados, con siete líneas
de segmentos compartidas y una línea de habilitación por display. Si se utiliza
otro circuito, debe adaptarse `display.c` y `app_config.h`.
