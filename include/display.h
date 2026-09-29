#ifndef DISPLAY_H
#define DISPLAY_H

#include <stdint.h>

void display_init(void);
void display_show_digit(uint8_t display_id, uint8_t digit);
void display_blank(uint8_t display_id);

/* Tarea de refresco necesaria porque los dos displays comparten segmentos. */
void display_refresh_task(void *pvParameters);

#endif
