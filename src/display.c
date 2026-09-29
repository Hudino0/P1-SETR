/*
 * display.c
 * ---------
 * Manejo de dos displays de 7 segmentos de CÁTODO COMÚN multiplexados.
 *  - Los 7 segmentos (a..g) son compartidos por ambos displays.
 *  - Cada cátodo común (COM) va DIRECTO a un GPIO (sin transistor):
 *      GPIO = 0 -> el pin absorbe la corriente -> display encendido.
 *      GPIO = 1 -> COM a 3.3 V -> no circula corriente -> display apagado.
 *    El nivel que enciende se define en app_config.h (DISPLAY_EN_ACTIVE_LEVEL).
 * Se enciende un display a la vez, muy rápido, y el ojo ve ambos encendidos.
 */
#include <stdio.h>
#include "display.h"
#include "app_config.h"
#include "system_state.h"
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

/* Patrones de segmentos para 0-9. Bit0 = a, bit1 = b, ... bit6 = g.
 * Ej.: 0x3F = 0b0111111 = a,b,c,d,e,f encendidos = "0". */
static const uint8_t DIGITS[10] =
{
    0x3FU, 0x06U, 0x5BU, 0x4FU, 0x66U,
    0x6DU, 0x7DU, 0x07U, 0x7FU, 0x6FU
};

/* Orden de pines: el índice i corresponde al bit i del patrón. */
static const gpio_num_t SEGMENTS[7] =
{
    SEG_A, SEG_B, SEG_C, SEG_D, SEG_E, SEG_F, SEG_G
};

/* Apaga ambos displays (COM al nivel contrario al de habilitación). */
static void disable_displays(void)
{
    gpio_set_level(DISPLAY_1_EN, !DISPLAY_EN_ACTIVE_LEVEL);
    gpio_set_level(DISPLAY_2_EN, !DISPLAY_EN_ACTIVE_LEVEL);
}

/* Escribe un patrón en las 7 líneas de segmentos. */
static void write_segments(uint8_t pattern)
{
    uint8_t i;

    for (i = 0U; i < 7U; ++i)
    {
        gpio_set_level(SEGMENTS[i], (pattern >> i) & 0x01U);
    }
}

void display_init(void)
{
    uint8_t i;

    /* Siete segmentos como salidas. */
    for (i = 0U; i < 7U; ++i)
    {
        gpio_reset_pin(SEGMENTS[i]);
        gpio_set_direction(SEGMENTS[i], GPIO_MODE_OUTPUT);
    }

    /* Líneas de habilitación (cátodo común de cada display) como salidas. */
    gpio_reset_pin(DISPLAY_1_EN);
    gpio_set_direction(DISPLAY_1_EN, GPIO_MODE_OUTPUT);

    gpio_reset_pin(DISPLAY_2_EN);
    gpio_set_direction(DISPLAY_2_EN, GPIO_MODE_OUTPUT);

    disable_displays();
    write_segments(0U);
}

/* Muestra "digit" en el display indicado (1 o 2). */
void display_show_digit(uint8_t display_id, uint8_t digit)
{
    if (digit > 9U)
    {
        return;   /* dígito inválido: no se muestra nada */
    }

    /* Primero apagar y luego cambiar segmentos: evita "fantasmas" del
     * dígito anterior en el otro display. */
    disable_displays();
    write_segments(DIGITS[digit]);

    if (display_id == 1U)
    {
        gpio_set_level(DISPLAY_1_EN, DISPLAY_EN_ACTIVE_LEVEL);
    }
    else if (display_id == 2U)
    {
        gpio_set_level(DISPLAY_2_EN, DISPLAY_EN_ACTIVE_LEVEL);
    }
}

/* Apaga un display concreto. */
void display_blank(uint8_t display_id)
{
    if (display_id == 1U)
    {
        gpio_set_level(DISPLAY_1_EN, !DISPLAY_EN_ACTIVE_LEVEL);
    }
    else if (display_id == 2U)
    {
        gpio_set_level(DISPLAY_2_EN, !DISPLAY_EN_ACTIVE_LEVEL);
    }
}

void display_refresh_task(void *pvParameters)
{
    app_context_t *context = (app_context_t *)pvParameters;

    if (context == NULL)
    {
        vTaskDelete(NULL);
        return;
    }

    display_init();

#if DISPLAY_SEGMENT_TEST
    /* Prueba de cableado: cada segmento se enciende 1.5 s en ambos displays. */
    {
        static const char NAMES[7] = { 'a', 'b', 'c', 'd', 'e', 'f', 'g' };
        uint8_t seg = 0U;
        uint32_t t;

        for (;;)
        {
            printf("PRUEBA: segmento %c (GPIO%d) en ambos displays\n", NAMES[seg], (int)SEGMENTS[seg]);
            for (t = 0U; t < 75U; ++t)
            {
                disable_displays();
                write_segments((uint8_t)(1U << seg));
                gpio_set_level(DISPLAY_1_EN, DISPLAY_EN_ACTIVE_LEVEL);
                vTaskDelay(pdMS_TO_TICKS(DISPLAY_SLOT_MS));
                disable_displays();
                gpio_set_level(DISPLAY_2_EN, DISPLAY_EN_ACTIVE_LEVEL);
                vTaskDelay(pdMS_TO_TICKS(DISPLAY_SLOT_MS));
            }
            seg = (uint8_t)((seg + 1U) % 7U);
        }
    }
#endif

    for (;;)
    {
        /* Turno del Display 1: muestra el valor publicado por Counter1. */
        display_show_digit(1U, context->counter1.value);
        vTaskDelay(pdMS_TO_TICKS(DISPLAY_SLOT_MS));

        /* Turno del Display 2: muestra el valor publicado por Counter2. */
        display_show_digit(2U, context->counter2.value);
        vTaskDelay(pdMS_TO_TICKS(DISPLAY_SLOT_MS));
    }
}
