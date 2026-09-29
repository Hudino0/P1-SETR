/*
 * counter.c
 * ---------
 * Contador BCD (0-9) y la tarea genérica que lo ejecuta.
 * La MISMA función counter_task() se usa para Counter1 y Counter2; lo que las
 * diferencia es el counter_config_t que recibe cada una por pvParameters
 * (mismo principio que Task_Blink en el ejemplo FOUR_LEDS).
 */
#include "counter.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

/* Inicializa el contador; "% 10" garantiza que el valor sea un dígito BCD válido. */
void counter_init(bcd_counter_t *counter, uint8_t initial_value)
{
    if (counter != NULL)
    {
        counter->value = initial_value % 10U;
    }
}

/* Avanza o retrocede una unidad con envoltura 9->0 (UP) y 0->9 (DOWN). */
void counter_step(bcd_counter_t *counter, count_direction_t direction)
{
    if (counter == NULL)
    {
        return;
    }

    if (direction == COUNT_UP)
    {
        counter->value = (counter->value >= 9U) ? 0U : (uint8_t)(counter->value + 1U);
    }
    else
    {
        counter->value = (counter->value == 0U) ? 9U : (uint8_t)(counter->value - 1U);
    }
}

uint8_t counter_get_value(const bcd_counter_t *counter)
{
    return (counter != NULL) ? counter->value : 0U;
}

void counter_task(void *pvParameters)
{
    /* Recuperamos la estructura propia de ESTA tarea (cast de void*). */
    counter_config_t *config = (counter_config_t *)pvParameters;
    bcd_counter_t counter;

    if (config == NULL)
    {
        vTaskDelete(NULL);   /* sin parámetros no hay nada que hacer */
        return;
    }

    counter_init(&counter, config->value);

    for (;;)
    {
        /* Resincroniza con config->value: el Manager puede haberlo modificado
         * (ajuste al pasar de OPPOSITE a SAME). */
        counter_init(&counter, config->value);

        counter_step(&counter, config->direction);
        config->value = counter_get_value(&counter);

        /*
         * El display NO se escribe aquí directamente.
         * La tarea display_refresh_task() multiplexa ambos displays
         * usando los valores publicados por counter1 y counter2.
         */

        /* Espera el periodo actual (500 ms o 250 ms según lo configure el Manager).
         * Mientras espera la tarea está BLOCKED; si el Manager la suspende pasa a
         * SUSPENDED y al reanudarla continúa de inmediato tras esta línea. */
        vTaskDelay(pdMS_TO_TICKS(config->period_ms));
    }
}
