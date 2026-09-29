"""Genera docs/diagrama_tareas.png (diagrama de tareas con pvParameters y TaskHandle_t)."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = os.path.dirname(os.path.abspath(__file__))
fig, ax = plt.subplots(figsize=(15, 9), dpi=110)
ax.set_xlim(0, 150); ax.set_ylim(0, 90); ax.axis("off")

def box(x, y, w, h, title, lines, fc):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.5", fc=fc, ec="#333", lw=1.6))
    ax.text(x + w / 2, y + h - 2.0, title, ha="center", va="top", fontsize=11, fontweight="bold")
    for i, l in enumerate(lines):
        ax.text(x + 1.5, y + h - 5.6 - i * 2.6, l, fontsize=8.0, va="top", family="monospace")

def arrow(p, q, text="", color="#333", off=(0, 1.2), rad=0.0):
    ax.annotate("", xy=q, xytext=p,
                arrowprops=dict(arrowstyle="->", lw=1.8, color=color, connectionstyle=f"arc3,rad={rad}"))
    if text:
        ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], text, fontsize=8.5, color=color,
                ha="center", fontweight="bold", bbox=dict(fc="white", ec="none", pad=0.6))

ax.text(75, 88, "Practica 1 - Diagrama de tareas (pvParameters y TaskHandle_t)", ha="center", fontsize=16, fontweight="bold")

btn = [("BtnStart", "GPIO18", "start_pause_event"), ("BtnDirection", "GPIO19", "direction_event"),
       ("BtnSpeed", "GPIO21", "speed_event"), ("BtnMode", "GPIO22", "mode_event")]
for i, (n, pin, ev) in enumerate(btn):
    y = 66 - i * 16
    box(1, y, 44, 13, f"Tarea {n} (prio 2)",
        ["button_task()", "pvParameters=&button_task_params_t", f"  .pin={pin}  .event=&{ev}"], "#fff3d6")
    arrow((45, y + 6), (54, 44 + (1.5 - i) * 4), "pending=true" if i == 0 else "", "#b7791f", (0, 1.5))

box(54, 6, 46, 56, "app_context_t (compartido)",
    ["system: run_state, master_direction,", "        coupling_mode, speed_mode", "",
     "flags (bool pending):", "  start_pause_event", "  direction_event", "  speed_event", "  mode_event", "",
     "counter1: counter_config_t", "  value direction period_ms", "counter2: counter_config_t", "  value direction period_ms", "",
     "TaskHandle_t:", "  counter1_handle counter2_handle", "  manager_handle"], "#e8f0fe")

box(104, 63, 45, 20, "Tarea TaskManager (prio 3)",
    ["task_manager()", "pvParameters=&context", "handle: manager_handle", "unico que interpreta flags y", "usa los handles"], "#e6f6e6")
box(104, 36, 45, 19, "Tarea Counter1 (prio 2)",
    ["counter_task()", "pvParameters=&context.counter1", "handle: counter1_handle", "-> Display 1"], "#fde8e8")
box(104, 8, 45, 19, "Tarea Counter2 (prio 2)",
    ["counter_task()  <- MISMA funcion", "pvParameters=&context.counter2", "handle: counter2_handle", "-> Display 2"], "#fde8e8")
box(54, 64, 46, 19, "Tarea DisplayRefresh (prio 2)",
    ["display_refresh_task()", "pvParameters=&context", "lee counter1.value y counter2.value"], "#efe6f8")

arrow((100, 50), (104, 68), "lee flags\nescribe config", "#2f855a", (-1, -3))
arrow((126, 64), (126, 55), "vTaskSuspend / vTaskResume (counter1_handle)", "#c53030", (0, 0.5))
arrow((149, 64), (149, 27), "", "#c53030", rad=-0.25)
ax.text(140, 30.5, "vTaskSuspend / Resume\n(counter2_handle)", fontsize=8.5, color="#c53030", ha="center",
        fontweight="bold", bbox=dict(fc="white", ec="none", pad=0.6))
arrow((104, 44), (100, 40), "value", "#555", (0, 1.4))
arrow((104, 16), (100, 22), "value", "#555", (0, 1.4))
arrow((77, 60), (77, 64), "", "#6b46c1")

ax.text(1, 2.5, "Sin queues, semaforos, mutex, event groups ni software timers: comunicacion por flags y estructuras compartidas.",
        fontsize=9.5, style="italic")
fig.savefig(os.path.join(OUT, "diagrama_tareas.png"), bbox_inches="tight", facecolor="white")
