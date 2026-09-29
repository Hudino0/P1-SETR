/*
 * app_tasks.c
 * -----------
 * Task Manager y creación de tareas.
 *  - El Task Manager es el ÚNICO que interpreta los botones y modifica la
 *    configuración del sistema.
 *  - Usa los TaskHandle_t de Counter1 y Counter2 para suspenderlas/reanudarlas.
 *  - No se usan queues, semáforos, mutex, event groups ni software timers:
 *    la comunicación se hace con flags "pending" y estructuras compartidas.
 */
#include "app_tasks.h"
#include "app_config.h"
#include "buttons.h"
#include "counter.h"
#include "display.h"
#include "esp_log.h"

static const char *TAG = "TASK_MANAGER";

/* Devuelve la dirección contraria. */
static count_direction_t opposite_direction(count_direction_t direction)
{
    return (direction == COUNT_UP) ? COUNT_DOWN : COUNT_UP;
}

/* Traduce el estado global (dirección base, modo, velocidad) a la
 * configuración individual de cada contador. */
static void apply_configuration(app_context_t *c)
{
    uint32_t period;

    /* Counter1 siempre sigue la dirección base. */
    c->counter1.direction = c->system.master_direction;

    /* Counter2: igual (SAME) o contraria (OPPOSITE). Ver tabla de la práctica. */
    if (c->system.coupling_mode == COUPLING_SAME)
    {
        c->counter2.direction = c->system.master_direction;
    }
    else
    {
        c->counter2.direction = opposite_direction(c->system.master_direction);
    }

    /* Velocidad: 500 ms (lento) o 250 ms (rápido) para ambos contadores. */
    period = (c->system.speed_mode == SPEED_FAST) ? FAST_PERIOD_MS : SLOW_PERIOD_MS;

    c->counter1.period_ms = period;
    c->counter2.period_ms = period;
}

/* Suspende o reanuda ambos contadores usando sus handles. */
static void set_counters_running(app_context_t *c, bool running)
{
    if (running)
    {
        vTaskResume(c->counter1_handle);
        vTaskResume(c->counter2_handle);
    }
    else
    {
        vTaskSuspend(c->counter1_handle);
        vTaskSuspend(c->counter2_handle);
    }
}

/* Al pasar de OPPOSITE a SAME los dos contadores se igualan:
 *  - cuenta DOWN -> ambos al dígito de menor valor,
 *  - cuenta UP   -> ambos al dígito de mayor valor. */
static void align_counters_for_same(app_context_t *c)
{
    uint8_t v1 = c->counter1.value;
    uint8_t v2 = c->counter2.value;
    uint8_t target;

    if (c->system.master_direction == COUNT_DOWN)
    {
        target = (v1 < v2) ? v1 : v2;
    }
    else
    {
        target = (v1 > v2) ? v1 : v2;
    }

    c->counter1.value = target;
    c->counter2.value = target;
}

void task_manager(void *pvParameters)
{
    app_context_t *c = (app_context_t *)pvParameters;

    if (c == NULL)
    {
        vTaskDelete(NULL);
        return;
    }

    /* Configuración inicial y arranque en PAUSA: los contadores se suspenden
     * antes de que hayan contado nada (el Manager tiene mayor prioridad). */
    apply_configuration(c);
    set_counters_running(c, false);

    for (;;)
    {
        /* --- Botón Start/Pause: siempre atendido --- */
        if (c->start_pause_event.pending)
        {
            c->start_pause_event.pending = false;   /* evento consumido */

            c->system.run_state = (c->system.run_state == SYSTEM_RUNNING)
                                  ? SYSTEM_PAUSED : SYSTEM_RUNNING;

            set_counters_running(c, c->system.run_state == SYSTEM_RUNNING);

            ESP_LOGI(TAG, "STATE=%s", run_state_to_string(c->system.run_state));
            /* eTaskGetState devuelve eSuspended(3) o eBlocked(2), etc. */
            ESP_LOGI(TAG, "Counter1 state=%d Counter2 state=%d",
                     (int)eTaskGetState(c->counter1_handle),
                     (int)eTaskGetState(c->counter2_handle));
        }

        /*
         * Dirección, velocidad y modo se ignoran estando en PAUSE.
         */
        if (c->system.run_state == SYSTEM_RUNNING)
        {
            if (c->direction_event.pending)
            {
                c->direction_event.pending = false;
                c->system.master_direction = (c->system.master_direction == COUNT_DOWN)
                                             ? COUNT_UP : COUNT_DOWN;
                apply_configuration(c);
                ESP_LOGI(TAG, "DIR=%s", direction_to_string(c->system.master_direction));
            }

            if (c->speed_event.pending)
            {
                c->speed_event.pending = false;
                c->system.speed_mode = (c->system.speed_mode == SPEED_SLOW)
                                       ? SPEED_FAST : SPEED_SLOW;
                apply_configuration(c);
                ESP_LOGI(TAG, "SPEED=%s", speed_to_string(c->system.speed_mode));
            }

            if (c->mode_event.pending)
            {
                c->mode_event.pending = false;
                c->system.coupling_mode = (c->system.coupling_mode == COUPLING_OPPOSITE)
                                          ? COUPLING_SAME : COUPLING_OPPOSITE;

                /* Ajuste de valores solo al entrar a SAME. */
                if (c->system.coupling_mode == COUPLING_SAME)
                {
                    align_counters_for_same(c);
                }

                apply_configuration(c);
                ESP_LOGI(TAG, "MODE=%s", coupling_to_string(c->system.coupling_mode));
            }
        }
        else
        {
            /* En PAUSE se descartan las pulsaciones de dirección/velocidad/modo
             * para que no se apliquen "de golpe" al reanudar. */
            c->direction_event.pending = false;
            c->speed_event.pending = false;
            c->mode_event.pending = false;
        }

        vTaskDelay(pdMS_TO_TICKS(MANAGER_PERIOD_MS));
    }
}

void create_application_tasks(app_context_t *c)
{
    /* "static": deben seguir existiendo después de que esta función retorne,
     * porque las tareas conservan el puntero recibido en pvParameters
     * (igual que los LedConfig_t static del ejemplo FOUR_LEDS). */
    static button_task_params_t start_params;
    static button_task_params_t direction_params;
    static button_task_params_t speed_params;
    static button_task_params_t mode_params;

    start_params.pin = BTN_START_PAUSE;
    start_params.event = &c->start_pause_event;

    direction_params.pin = BTN_DIRECTION;
    direction_params.event = &c->direction_event;

    speed_params.pin = BTN_SPEED;
    speed_params.event = &c->speed_event;

    mode_params.pin = BTN_MODE;
    mode_params.event = &c->mode_event;

    /*
     * Es la MISMA función counter_task() --> dos instancias diferentes.
     * pvParameters determina qué estructura controla cada tarea.
     * El último argumento guarda el TaskHandle_t para el Task Manager.
     */
    xTaskCreate(counter_task, "Counter1", 1024, &c->counter1, 2, &c->counter1_handle);
    xTaskCreate(counter_task, "Counter2", 1024, &c->counter2, 2, &c->counter2_handle);

    /*
     * Es la misma función button_task() --> cuatro botones distintos.
     * pvParameters parametriza el comportamiento (pin + evento).
     */
    xTaskCreate(button_task, "BtnStart",     1024, &start_params,     2, NULL);
    xTaskCreate(button_task, "BtnDirection", 1024, &direction_params, 2, NULL);
    xTaskCreate(button_task, "BtnSpeed",     1024, &speed_params,     2, NULL);
    xTaskCreate(button_task, "BtnMode",      1024, &mode_params,      2, NULL);

    /* Refresco de displays: recibe el contexto completo para leer ambos valores. */
    xTaskCreate(display_refresh_task, "DisplayRefresh", 2048, c, 2, NULL);

    /* Task Manager: prioridad mayor (3) para suspender los contadores al inicio. */
    xTaskCreate(task_manager, "TaskManager", 3072, c, 3, &c->manager_handle);
}
