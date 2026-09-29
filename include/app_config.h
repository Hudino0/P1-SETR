#ifndef APP_CONFIG_H
#define APP_CONFIG_H

/*
 * app_config.h
 * ------------
 * Toda la configuración de hardware y de tiempos en un solo lugar.
 * Si cambias un cable, SOLO se modifica este archivo.
 * (Igual que led_config.h del ejemplo FOUR_LEDS, donde el GPIO y el
 *  periodo se concentran en una estructura de configuración.)
 */

#include <stdint.h>
#include "driver/gpio.h"

/* ---- Segmentos compartidos por ambos displays (multiplexados) ----
 * Cada línea va directo al segmento correspondiente de LOS DOS displays
 * (se conectan en paralelo). La limitación de corriente está en el COM.
 * NOTA: SEG_B usa GPIO16 en lugar de GPIO12: el GPIO12 es pin de "strapping"
 * en el ESP32 y puede impedir el arranque si se fuerza a nivel alto. */
#define SEG_A GPIO_NUM_13
#define SEG_B GPIO_NUM_16
#define SEG_C GPIO_NUM_14
#define SEG_D GPIO_NUM_27
#define SEG_E GPIO_NUM_26
/* f y g intercambiados respecto a la guía para coincidir con el cableado real
 * (con 25=f y 33=g los dígitos 0, 2 y 3 se veían mal). */
#define SEG_F GPIO_NUM_33
#define SEG_G GPIO_NUM_25

/* ---- Habilitación de cada display ----
 * SIN transistores: cada GPIO va, por resistencias de 470 ohm (una en cada pin COM),
 * al cátodo común de su display.
 *   Nivel 0 = el GPIO absorbe la corriente -> display encendido.
 * Con transistores (2N2222) el nivel activo sería 1. */
#define DISPLAY_EN_ACTIVE_LEVEL 0
#define DISPLAY_1_EN GPIO_NUM_32
#define DISPLAY_2_EN GPIO_NUM_23

/* ---- Botones (activos en bajo, con pull-up interno) ---- */
#define BTN_START_PAUSE GPIO_NUM_18
#define BTN_DIRECTION   GPIO_NUM_19
#define BTN_SPEED       GPIO_NUM_21
#define BTN_MODE        GPIO_NUM_22

/* ---- Tiempos (ms) ---- */
#define SLOW_PERIOD_MS    500U  /* periodo de cuenta lento            */
#define FAST_PERIOD_MS    250U  /* periodo de cuenta rápido           */
#define BUTTON_PERIOD_MS  20U   /* muestreo de botones (antirrebote)  */
#define MANAGER_PERIOD_MS 10U   /* ciclo del Task Manager             */

/* Tiempo que permanece encendido cada display en la multiplexación.
 * Con el tick por defecto de FreeRTOS (100 Hz) el mínimo es 10 ms;
 * 2 displays x 10 ms = 50 Hz de refresco por display: sin parpadeo visible. */
#define DISPLAY_SLOT_MS   10U

/* Prueba de cableado: en 1 enciende los segmentos uno por uno (a, b, c ... g)
 * en ambos displays y muestra por UART qué segmento/GPIO debería verse.
 * Dejar en 0 para la práctica normal. */
#define DISPLAY_SEGMENT_TEST 0

#endif
