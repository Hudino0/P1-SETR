/*
 * buttons.c
 * ---------
 * Una sola función de tarea (button_task) atiende los cuatro botones; cada
 * instancia recibe por pvParameters su pin y el evento que debe publicar.
 * La tarea NO interpreta el botón: solo levanta un flag; el Task Manager decide.
 */
#include "buttons.h"
#include "app_config.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

/* Configura el pin como entrada con pull-up interno (botón entre GPIO y GND). */
void button_init(gpio_num_t pin)
{
    gpio_reset_pin(pin);
    gpio_set_direction(pin, GPIO_MODE_INPUT);
    gpio_set_pull_mode(pin, GPIO_PULLUP_ONLY);
}

/* Con pull-up, botón presionado = nivel 0. */
bool button_is_pressed(gpio_num_t pin)
{
    return gpio_get_level(pin) == 0;
}

void button_task(void *pvParameters)
{
    button_task_params_t *params = (button_task_params_t *)pvParameters;
    bool previous = false;   /* estado anterior, para detectar el flanco */

    if ((params == NULL) || (params->event == NULL))
    {
        vTaskDelete(NULL);
        return;
    }

    button_init(params->pin);

    for (;;)
    {
        bool current = button_is_pressed(params->pin);

        /* Detección de flanco de pulsación (soltado -> presionado):
         * genera UN solo evento por pulsación aunque se mantenga presionado. */
        if (current && !previous)
        {
            params->event->pending = true;
        }

        previous = current;

        /* El muestreo cada 20 ms también actúa como antirrebote. */
        vTaskDelay(pdMS_TO_TICKS(BUTTON_PERIOD_MS));
    }
}
