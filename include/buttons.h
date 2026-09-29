#ifndef BUTTONS_H
#define BUTTONS_H

#include <stdbool.h>
#include "driver/gpio.h"
#include "system_state.h"

/* Parámetros de una tarea de botón: qué pin leer y qué evento publicar. */
typedef struct
{
    gpio_num_t pin;
    button_event_t *event;
} button_task_params_t;

void button_init(gpio_num_t pin);
bool button_is_pressed(gpio_num_t pin);
void button_task(void *pvParameters);

#endif
