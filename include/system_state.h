#ifndef SYSTEM_STATE_H
#define SYSTEM_STATE_H

/*
 * system_state.h
 * --------------
 * Tipos compartidos por toda la aplicación: enums de estados/modos, structs de
 * configuración y el contexto global que se pasa a las tareas por pvParameters.
 */

#include <stdbool.h>
#include <stdint.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

/* Dirección de cuenta. */
typedef enum
{
    COUNT_UP = 0,
    COUNT_DOWN
} count_direction_t;

/* Acoplamiento entre contadores: opuestos o mismo sentido. */
typedef enum
{
    COUPLING_OPPOSITE = 0,
    COUPLING_SAME
} coupling_mode_t;

/* Estado global del sistema. */
typedef enum
{
    SYSTEM_PAUSED = 0,
    SYSTEM_RUNNING
} run_state_t;

/* Velocidad de cuenta. */
typedef enum
{
    SPEED_SLOW = 0,
    SPEED_FAST
} speed_mode_t;

/* Identificador de cada botón. */
typedef enum
{
    BUTTON_START_PAUSE = 0,
    BUTTON_DIRECTION,
    BUTTON_SPEED,
    BUTTON_MODE
} button_id_t;

/* Configuración general (se conserva de la práctica base). */
typedef struct
{
    count_direction_t direction;
    coupling_mode_t   coupling;
    run_state_t       state;
    speed_mode_t      speed;
    button_id_t       last_button;
} system_config_t;

/*
 * Configuración de UN contador. Es el equivalente a LedConfig_t del ejemplo
 * FOUR_LEDS: cada tarea recibe un puntero a su propia estructura mediante
 * pvParameters. "volatile" porque el Task Manager la escribe y la tarea
 * contadora la lee desde otro contexto de ejecución.
 */
typedef struct
{
    volatile uint8_t value;               /* valor BCD actual (0-9)   */
    volatile count_direction_t direction; /* sentido de cuenta        */
    volatile uint32_t period_ms;          /* periodo entre cuentas    */
    uint8_t display_id;                   /* display asociado (1 o 2) */
} counter_config_t;

/* Evento de botón: la tarea del botón pone pending=true, el Manager lo consume. */
typedef struct
{
    volatile bool pending;
    button_id_t id;
} button_event_t;

/* Estado global gobernado únicamente por el Task Manager. */
typedef struct
{
    volatile run_state_t run_state;
    volatile count_direction_t master_direction; /* dirección base (Display 1) */
    volatile coupling_mode_t coupling_mode;
    volatile speed_mode_t speed_mode;
} system_state_t;

/*
 * Contexto completo de la aplicación. Se declara UNA vez (en main) y se pasa
 * por pvParameters al Task Manager y a la tarea de refresco de displays.
 */
typedef struct
{
    system_state_t system;

    counter_config_t counter1;
    counter_config_t counter2;

    button_event_t start_pause_event;
    button_event_t direction_event;
    button_event_t speed_event;
    button_event_t mode_event;

    /* TaskHandle_t: "identificación" de cada tarea; permite suspenderla y
     * reanudarla desde el Task Manager con vTaskSuspend()/vTaskResume(). */
    TaskHandle_t counter1_handle;
    TaskHandle_t counter2_handle;
    TaskHandle_t manager_handle;
} app_context_t;

void system_state_init(app_context_t *context);

/* Conversión a texto para los logs por UART. */
const char *direction_to_string(count_direction_t direction);
const char *coupling_to_string(coupling_mode_t mode);
const char *run_state_to_string(run_state_t state);
const char *speed_to_string(speed_mode_t speed);

#endif
