#ifndef COUNTER_H
#define COUNTER_H

#include <stdint.h>
#include "system_state.h"

/* Contador BCD (0-9) puro, sin dependencias de FreeRTOS: se puede probar aparte. */
typedef struct
{
    uint8_t value;
} bcd_counter_t;

void counter_init(bcd_counter_t *counter, uint8_t initial_value);
void counter_step(bcd_counter_t *counter, count_direction_t direction);
uint8_t counter_get_value(const bcd_counter_t *counter);

/* Tarea genérica: la misma función sirve para Counter1 y Counter2. */
void counter_task(void *pvParameters);

#endif
