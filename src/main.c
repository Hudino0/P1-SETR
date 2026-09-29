/*
 * main.c
 * ------
 * app_main() se limita a lo que pide la práctica: inicializar el contexto y
 * crear la aplicación. Al igual que en el ejemplo FOUR_LEDS, el contexto se
 * declara "static" para que siga existiendo cuando app_main() termine, ya que
 * las tareas conservan punteros hacia él (vía pvParameters).
 */
#include "app_tasks.h"
#include "system_state.h"

void app_main(void)
{
    static app_context_t context;

    system_state_init(&context);          /* valores iniciales de todo el sistema */
    create_application_tasks(&context);   /* crea contadores, botones, display y manager */
}
