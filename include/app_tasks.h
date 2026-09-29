#ifndef APP_TASKS_H
#define APP_TASKS_H

#include "system_state.h"

/* Tarea que interpreta los botones y gobierna el sistema. */
void task_manager(void *pvParameters);

/* Crea todas las tareas de la aplicación (contadores, botones, display, manager). */
void create_application_tasks(app_context_t *context);

#endif
