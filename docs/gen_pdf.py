"""
Genera docs/Guia_Protoboard_63.pdf: guia ilustrada paso a paso para una
protoboard de 63 columnas (830 puntos). Ejecutar:  python docs/gen_pdf.py
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch, PathPatch, Polygon
from matplotlib.path import Path

OUT = os.path.dirname(os.path.abspath(__file__))
NCOL = 63
FIG = (16.5, 11.0)

SEGCOL = {"a": "#e6194b", "b": "#f58231", "c": "#c9a400", "d": "#3cb44b",
          "e": "#00a3a3", "f": "#4363d8", "g": "#911eb4"}
GPIO = {"a": 13, "b": 16, "c": 14, "d": 27, "e": 26, "f": 25, "g": 33}
BLOCK = {s: 10 + i for i, s in enumerate("abcdefg")}          # columnas 10..16
D1C, D2C = 3, 19                                              # primera columna de cada display
Q = [(26, "Q1", "DISPLAY 1", 32, 5), (34, "Q2", "DISPLAY 2", 23, 21)]  # col0, nombre, disp, gpio, colCOM
BTNS = [(42, "START/PAUSE", 18), (47, "DIRECCION", 19), (52, "VELOCIDAD", 21), (57, "MODO", 22)]

def X(c): return float(c)
def YT(r): return 20.0 - r          # mitad superior: r=0 lejos del canal ... 4 junto al canal
def YB(r): return 13.0 - r          # mitad inferior: r=0 junto al canal ... 4 lejos
Y_RT, Y_RB, Y_ESP = 23.0, 6.0, 31.0


class Drawer:
    def __init__(self, ax, stage):
        self.ax, self.stage = ax, stage

    def vis(self, st):
        return st <= self.stage or self.stage == 6

    def al(self, st):
        return 1.0 if (st == self.stage or self.stage == 6) else 0.28

    # ---- primitivas ----
    def dot(self, x, y, color, a=1.0):
        self.ax.add_patch(Circle((x, y), 0.24, fc=color, ec="k", lw=0.5, zorder=6, alpha=a))

    def wire(self, p, q, color, st, bend=0.0, lw=2.4):
        if not self.vis(st): return
        a = self.al(st)
        (x1, y1), (x2, y2) = p, q
        path = Path([p, ((x1 + x2) / 2, (y1 + y2) / 2 + bend), q], [Path.MOVETO, Path.CURVE3, Path.CURVE3])
        self.ax.add_patch(PathPatch(path, fc="none", ec=color, lw=lw, zorder=5, alpha=a, capstyle="round"))
        self.dot(x1, y1, color, a); self.dot(x2, y2, color, a)

    def esp_pin(self, col, label, st):
        if not self.vis(st): return (X(col), Y_ESP)
        a = self.al(st)
        self.ax.add_patch(Rectangle((X(col) - 0.3, Y_ESP), 0.6, 1.2, fc="#d4af37", ec="none", zorder=3, alpha=a))
        self.ax.text(X(col), Y_ESP + 1.4, label, color="white", rotation=90, ha="center", va="bottom",
                     fontsize=8.5, fontweight="bold", zorder=3, alpha=a)
        return (X(col), Y_ESP)

    # ---- base ----
    def board(self):
        ax = self.ax
        ax.add_patch(FancyBboxPatch((0, 4.6), NCOL + 1.5, 19.6, boxstyle="round,pad=0.1,rounding_size=0.5",
                                    fc="#efe9d8", ec="#8c8571", lw=1.5, zorder=0))
        ax.add_patch(Rectangle((0.3, 13.6), NCOL + 0.9, 1.8, fc="#d9d2bd", ec="none", zorder=1))
        for c in range(1, NCOL + 1):
            for r in range(5):
                ax.add_patch(Circle((X(c), YT(r)), 0.16, fc="#5a5a5a", ec="none", zorder=1))
                ax.add_patch(Circle((X(c), YB(r)), 0.16, fc="#5a5a5a", ec="none", zorder=1))
            if c % 5 == 0 or c in (1, NCOL):
                ax.text(X(c), 21.0, str(c), ha="center", va="bottom", fontsize=7, color="#666", zorder=1)
        for y in (Y_RT, Y_RB):
            ax.plot([0.7, NCOL + 0.8], [y, y], color="#1f5fbf", lw=3, zorder=1)
            ax.text(NCOL + 1.0, y, "GND", color="#1f5fbf", fontsize=8, va="center", fontweight="bold")
        ax.text(1, 4.9, "Cada columna = 5 agujeros unidos (arriba: a-e / abajo: f-j). El canal central separa arriba de abajo.",
                fontsize=7.5, color="#555")

    def esp(self):
        ax = self.ax
        ax.add_patch(FancyBboxPatch((0.5, 32.2), NCOL + 0.0, 9.3, boxstyle="round,pad=0.1,rounding_size=0.6",
                                    fc="#22262e", ec="#000", lw=2, zorder=2))
        ax.text(31.5, 38.3, "ESP32 DevKit V1 (dibujo simplificado: pines reordenados; usa los NUMEROS de GPIO)",
                color="white", ha="center", fontsize=11, fontweight="bold", zorder=3)
        ax.text(31.5, 36.4, "Se alimenta solo por USB. No se usa 3V3 ni VIN.", color="#cfd3dc",
                ha="center", fontsize=9, zorder=3)
        ax.add_patch(Rectangle((27, 40.9), 9, 0.6, fc="#888", ec="none", zorder=3))
        ax.text(31.5, 41.8, "USB", color="#333", ha="center", fontsize=7)

    # ---- componentes ----
    def display(self, c0, name, st):
        if not self.vis(st): return {}
        a, ax = self.al(st), self.ax
        x0, x1 = X(c0) - 0.6, X(c0 + 4) + 0.6
        ax.add_patch(Rectangle((x0, 12.3), x1 - x0, 4.4, fc="#f4f4f4", ec="#333", lw=1.6, zorder=4, alpha=a))
        ax.text((x0 + x1) / 2, 14.5, name, ha="center", va="center", fontsize=9, fontweight="bold", zorder=5, alpha=a)
        top, bot = ["g", "f", "COM", "a", "b"], ["e", "d", "COM", "c", "dp"]
        pos = {}
        for i in range(5):
            cx = X(c0 + i)
            ax.add_patch(Rectangle((cx - 0.18, YT(4) - 0.3), 0.36, 0.9, fc="#bbb", ec="none", zorder=5, alpha=a))
            ax.add_patch(Rectangle((cx - 0.18, YB(0) - 0.6), 0.36, 0.9, fc="#bbb", ec="none", zorder=5, alpha=a))
            ax.text(cx, 15.75, top[i], ha="center", va="center", fontsize=8, zorder=6, alpha=a,
                    color=SEGCOL.get(top[i], "#000"), fontweight="bold")
            ax.text(cx, 13.25, bot[i], ha="center", va="center", fontsize=8, zorder=6, alpha=a,
                    color=SEGCOL.get(bot[i], "#000"), fontweight="bold")
            if top[i] in SEGCOL: pos[top[i]] = (cx, YT(2))
            if bot[i] in SEGCOL: pos[bot[i]] = (cx, YB(3))
        pos["COM"] = (X(c0 + 2), YT(0))
        return pos

    def res220(self, s, st):
        """Punto de union de un segmento (sin resistencia): GPIO -> tira inferior -> ambos displays."""
        if not self.vis(st): return
        a, ax, x = self.al(st), self.ax, X(BLOCK[s])
        self.dot(x, YB(1), "#888", a)
        ax.text(x, 11.2, s.upper(), ha="center", fontsize=9, fontweight="bold", color=SEGCOL[s], alpha=a)

    def en_res(self, gpio, com_col, gpio_col, disp, st):
        """470 ohm en CADA pin COM del display (arriba y abajo) hacia el mismo GPIO de habilitacion."""
        if not self.vis(st): return
        a, ax = self.al(st), self.ax
        for y in (YT(1), YB(1)):
            xa, xb = X(com_col), X(gpio_col)
            ax.plot([xa, xb], [y, y], color="#888", lw=1.5, zorder=4, alpha=a)
            ax.add_patch(FancyBboxPatch(((xa + xb) / 2 - 1.0, y - 0.33), 2.0, 0.66,
                                        boxstyle="round,pad=0,rounding_size=0.25",
                                        fc="#d8b98a", ec="#7a5c2e", zorder=5, alpha=a))
            for k, col in enumerate(["#f1c40f", "#8e44ad", "#6d4c41", "#d4af37"]):
                ax.add_patch(Rectangle(((xa + xb) / 2 - 0.75 + k * 0.42, y - 0.33), 0.18, 0.66,
                                       fc=col, ec="none", zorder=6, alpha=a))
            self.dot(xa, y, "#888", a); self.dot(xb, y, "#888", a)
            ax.text((xa + xb) / 2, y + 0.7, "470", ha="center", fontsize=8, fontweight="bold", zorder=6, alpha=a)
        p = self.esp_pin(gpio_col, f"GPIO{gpio} (COM {disp})", st)
        self.wire(p, (X(gpio_col), YT(0)), "#6a3d9a", st, lw=2.6)
        # puente corto que une la tira superior con la inferior de la columna del GPIO
        self.wire((X(gpio_col), YT(2)), (X(gpio_col), YB(2)), "#6a3d9a", st, bend=0.0, lw=2.2)

    def button(self, c0, name, g, st):
        if not self.vis(st): return
        a, ax = self.al(st), self.ax
        ax.add_patch(Rectangle((X(c0) - 0.2, YB(0) + 0.15), 2.4, 2.9, fc="#222", ec="#000", zorder=5, alpha=a))
        ax.add_patch(Circle((X(c0 + 1), 14.5), 0.9, fc="#c0392b", ec="#000", zorder=6, alpha=a))
        ax.text(X(c0 + 1), 17.6, name, ha="center", fontsize=7.5, fontweight="bold", zorder=6, alpha=a)
        for cc in (c0, c0 + 2):
            ax.add_patch(Rectangle((cc - 0.15, YT(4) - 0.2), 0.3, 0.5, fc="#bbb", ec="none", zorder=5, alpha=a))
            ax.add_patch(Rectangle((cc - 0.15, YB(0) - 0.3), 0.3, 0.5, fc="#bbb", ec="none", zorder=5, alpha=a))
        p = self.esp_pin(c0, f"GPIO{g}", st)
        self.wire(p, (X(c0), YT(0)), "#ff7f00", st)
        self.wire((X(c0), YB(3)), (X(c0), Y_RB), "#111", st, lw=2.2)


def draw_stage(fig, stage, title, lines):
    ax = fig.add_axes([0.02, 0.06, 0.96, 0.78])
    ax.set_xlim(-1.0, NCOL + 4.5); ax.set_ylim(4, 43); ax.set_aspect("equal"); ax.axis("off")
    d = Drawer(ax, stage)
    d.board(); d.esp()
    # Paso 1: GND + displays
    p = d.esp_pin(1, "GND", 1)
    d.wire(p, (X(1), Y_RT), "#111", 1, lw=2.6)
    d.wire((X(2), Y_RT), (X(2), Y_RB), "#111", 1, lw=2.6)
    D1 = d.display(D1C, "DISPLAY 1", 1)
    D2 = d.display(D2C, "DISPLAY 2", 1)
    # Paso 2: resistencias 220 + GPIO
    for s in "abcdefg":
        d.res220(s, 2)
        p = d.esp_pin(BLOCK[s], f"GPIO{GPIO[s]} ({s})", 2)
        d.wire(p, (X(BLOCK[s]), YB(1)), SEGCOL[s], 2)
    # Paso 3: puentes a los displays
    for s in "abcdefg":
        if D1:
            d.wire((X(BLOCK[s]), YB(2)), D1[s], SEGCOL[s], 3, bend=4.5 if D1[s][1] > 15 else -6.0, lw=1.9)
            d.wire((X(BLOCK[s]), YB(3)), D2[s], SEGCOL[s], 3, bend=4.5 if D2[s][1] > 15 else -7.5, lw=1.9)
    # Paso 4: transistores
    d.en_res(32, 5, 8, "D1", 4)
    d.en_res(23, 21, 24, "D2", 4)
    # Paso 5: botones
    for c0, nm, g in BTNS:
        d.button(c0, nm, g, 5)
    fig.text(0.02, 0.95, title, fontsize=19, fontweight="bold")
    y = 0.915
    for ln in lines:
        fig.text(0.02, y, ln, fontsize=11.5); y -= 0.025
    fig.text(0.02, 0.02, "Negro = GND  |  Violeta = GPIO de habilitacion -> COM del display  |  Naranja = GPIO de boton  |  Colores a-g = segmentos.  Amarillo-violeta-cafe = 470 ohm (una en cada pin COM).", fontsize=9, color="#333")


def page_intro(pdf):
    fig = plt.figure(figsize=FIG)
    fig.text(0.04, 0.93, "Practica 1 - Doble contador BCD con FreeRTOS", fontsize=24, fontweight="bold")
    fig.text(0.04, 0.89, "Guia ilustrada de conexiones  -  Protoboard de 63 columnas  -  ESP32 DevKit V1  -  displays de catodo comun",
             fontsize=13, color="#333")
    ax = fig.add_axes([0.04, 0.12, 0.92, 0.72]); ax.set_xlim(0, 100); ax.set_ylim(-3, 62); ax.axis("off")
    ax.text(0, 61, "MATERIAL (minimo)", fontsize=15, fontweight="bold")
    items = [
        ("1", "ESP32 DevKit V1", "esp"), ("2", "Display 7 seg. catodo comun", "disp"),
        ("4", "Resistencia 470 ohm (amarillo-violeta-cafe)", "r1k"), ("4", "Push button", "btn"),
        ("1", "Protoboard 63 col. + jumpers", "jmp"),
    ]
    for i, (n, t, kind) in enumerate(items):
        col, row = i % 2, i // 2
        x0, y0 = col * 50, 55 - row * 8.5
        ax.text(x0, y0 + 2, f"{n} x", fontsize=16, fontweight="bold", color="#1f5fbf")
        ax.text(x0 + 6, y0 + 2, t, fontsize=12.5)
        # dibujitos
        if kind == "r220" or kind == "r1k":
            cols = ["#c62828", "#c62828", "#6d4c41", "#d4af37"] if kind == "r220" else ["#f1c40f", "#8e44ad", "#6d4c41", "#d4af37"]
            ax.plot([x0 + 6, x0 + 30], [y0 - 1.5, y0 - 1.5], color="#888", lw=2)
            ax.add_patch(FancyBboxPatch((x0 + 11, y0 - 2.6), 10, 2.2, boxstyle="round,pad=0,rounding_size=1", fc="#d8b98a", ec="#7a5c2e"))
            for k, c in enumerate(cols):
                ax.add_patch(Rectangle((x0 + 12.5 + k * 2.2, y0 - 2.6), 0.9, 2.2, fc=c, ec="none"))
        elif kind == "q":
            ax.add_patch(Polygon([(x0 + 8, y0 - 3), (x0 + 16, y0 - 3), (x0 + 16, y0 - 1), (x0 + 12, y0 + 0.5), (x0 + 8, y0 - 1)], fc="#2b2b2b", ec="k"))
            for k, l in enumerate("EBC"):
                ax.plot([x0 + 9 + k * 3, x0 + 9 + k * 3], [y0 - 3, y0 - 4.6], color="#888", lw=2)
            ax.text(x0 + 12, y0 - 2, "2N2222", color="white", ha="center", fontsize=6)
        elif kind == "disp":
            ax.add_patch(Rectangle((x0 + 8, y0 - 5), 10, 5, fc="#f4f4f4", ec="k"))
            ax.text(x0 + 13, y0 - 2.5, "8.", ha="center", va="center", fontsize=18, fontweight="bold", color="#c0392b")
        elif kind == "btn":
            ax.add_patch(Rectangle((x0 + 8, y0 - 4.5), 6, 4.5, fc="#222", ec="k"))
            ax.add_patch(Circle((x0 + 11, y0 - 2.2), 1.6, fc="#c0392b", ec="k"))
        elif kind == "esp":
            ax.add_patch(Rectangle((x0 + 8, y0 - 4.5), 14, 4.5, fc="#22262e", ec="k"))
            ax.text(x0 + 15, y0 - 2.2, "ESP32", color="white", ha="center", va="center", fontsize=8)
        elif kind == "jmp":
            for k, c in enumerate(["#e6194b", "#3cb44b", "#4363d8"]):
                ax.plot([x0 + 8 + k * 3, x0 + 12 + k * 3], [y0 - 1, y0 - 4], color=c, lw=3)
    # pinouts
    ax.text(0, 20.5, "PINOUT (verificalo con tus piezas)", fontsize=15, fontweight="bold")
    # display
    ax.add_patch(Rectangle((2, 4), 22, 10, fc="#f4f4f4", ec="k", lw=1.5))
    ax.text(13, 9, "Display visto de frente\n(punto decimal abajo-derecha)", ha="center", va="center", fontsize=8)
    top = ["10 g", "9 f", "8 COM", "7 a", "6 b"]; bot = ["1 e", "2 d", "3 COM", "4 c", "5 dp"]
    for i in range(5):
        ax.plot([4 + i * 4, 4 + i * 4], [14, 16], color="#888", lw=2); ax.text(4 + i * 4, 16.6, top[i], ha="center", fontsize=8.5, fontweight="bold")
        ax.plot([4 + i * 4, 4 + i * 4], [4, 2], color="#888", lw=2); ax.text(4 + i * 4, 0.5, bot[i], ha="center", fontsize=8.5, fontweight="bold")
    # 2N2222
    for k, (l, t) in enumerate([]):
        ax.plot([40 + k * 5, 40 + k * 5], [6, 3], color="#888", lw=2.5)
        ax.text(40 + k * 5, 1.8, l, ha="center", fontsize=10, fontweight="bold")
    ax.text(45, 9, "SIN TRANSISTORES:\ncada pin COM del display va por una\nresistencia de 470 al GPIO 32 (D1) / 23 (D2).\nGPIO = 0 -> display encendido", ha="center", va="center", fontsize=10, fontweight="bold")
    # tabla pines
    rows = ["a=13  b=16  c=14  d=27  e=26  f=25  g=33", "GPIO32 -> 2x470 -> los 2 COM del Display1;  GPIO23 -> 2x470 -> los 2 COM del Display2 (activo en 0)", "Botones: Start/Pause=18  Direccion=19  Velocidad=21  Modo=22", "GND -> riel GND"]
    ax.text(62, 18, "GPIO (app_config.h)", fontsize=12, fontweight="bold")
    for i, r in enumerate(rows):
        ax.text(62, 14 - i * 3.2, r, fontsize=10)
    ax.text(62, 0.5, "Seguridad: arma con el USB desconectado.", fontsize=10, color="#a33")
    pdf.savefig(fig); plt.close(fig)


def page_anatomy(pdf):
    fig = plt.figure(figsize=FIG)
    fig.text(0.02, 0.95, "Como leer la protoboard de 63 columnas", fontsize=19, fontweight="bold")
    for i, ln in enumerate([
        "- Hay 63 columnas numeradas; en cada columna, los 5 agujeros de ARRIBA estan unidos entre si y los 5 de ABAJO estan unidos entre si.",
        "- Arriba y abajo NO estan conectados: el canal central los separa. Los displays, botones y resistencias verticales lo cruzan.",
        "- Las lineas azules son los rieles GND. Se usan ambos: uno cerca de la ESP32 y otro abajo (unidos con un cable negro).",
        "- En estos dibujos la ESP32 esta arriba solo para mostrar a que GPIO va cada cable; en fisico conectas con jumpers macho-hembra o macho-macho."]):
        fig.text(0.02, 0.91 - i * 0.026, ln, fontsize=11.5)
    ax = fig.add_axes([0.02, 0.06, 0.96, 0.62]); ax.set_xlim(-1, NCOL + 4.5); ax.set_ylim(4, 27); ax.set_aspect("equal"); ax.axis("off")
    d = Drawer(ax, 0); d.board()
    ax.add_patch(Rectangle((9.5, YT(4) - 0.4), 1.0, 5.8, fc="none", ec="#e6194b", lw=2.5, zorder=8))
    ax.text(10, 25.3, "una columna:\n5 agujeros unidos", color="#e6194b", ha="center", fontsize=9, fontweight="bold")
    ax.add_patch(Rectangle((9.5, YB(4) - 0.4), 1.0, 5.8, fc="none", ec="#4363d8", lw=2.5, zorder=8))
    ax.text(10, 4.2, "otra tira, NO conectada\ncon la de arriba", color="#4363d8", ha="center", fontsize=9, fontweight="bold")
    ax.annotate("Canal central (sin conexion)", (30, 14.5), (30, 26.3), ha="center", fontsize=10, fontweight="bold",
                arrowprops=dict(arrowstyle="->", lw=2))
    ax.annotate("Riel GND", (50, Y_RT), (50, 25.5), ha="center", fontsize=10, fontweight="bold", color="#1f5fbf",
                arrowprops=dict(arrowstyle="->", lw=2, color="#1f5fbf"))
    pdf.savefig(fig); plt.close(fig)


def page_stage(pdf, stage, title, lines):
    fig = plt.figure(figsize=FIG)
    draw_stage(fig, stage, title, lines)
    pdf.savefig(fig); plt.close(fig)


def page_table(pdf):
    fig = plt.figure(figsize=FIG)
    fig.text(0.04, 0.94, "Tabla de conexiones completa y pruebas", fontsize=20, fontweight="bold")
    rows = [
        ("Segmento a", "GPIO13", "- (col 10, abajo)", "pin a de Display 1 (col 6 arriba) y Display 2 (col 22 arriba)"),
        ("Segmento b", "GPIO16", "- (col 11, abajo)", "pin b de Display 1 (col 7 arriba) y Display 2 (col 23 arriba)"),
        ("Segmento c", "GPIO14", "- (col 12, abajo)", "pin c de Display 1 (col 6 abajo) y Display 2 (col 22 abajo)"),
        ("Segmento d", "GPIO27", "- (col 13, abajo)", "pin d de Display 1 (col 4 abajo) y Display 2 (col 20 abajo)"),
        ("Segmento e", "GPIO26", "- (col 14, abajo)", "pin e de Display 1 (col 3 abajo) y Display 2 (col 19 abajo)"),
        ("Segmento f", "GPIO25", "- (col 15, abajo)", "pin f de Display 1 (col 4 arriba) y Display 2 (col 20 arriba)"),
        ("Segmento g", "GPIO33", "- (col 16, abajo)", "pin g de Display 1 (col 3 arriba) y Display 2 (col 19 arriba)"),
        ("COM Display 1", "GPIO32", "470", "GPIO32 -> col 8; 470 (arriba) y 470 (abajo) entre col 8 y col 5 (los 2 COM del Display 1)"),
        ("COM Display 2", "GPIO23", "470", "GPIO23 -> col 24; 470 (arriba) y 470 (abajo) entre col 24 y col 21 (los 2 COM del Display 2)"),
        ("Start/Pause", "GPIO18", "-", "boton cols 42-44; abajo -> riel GND"),
        ("Direccion", "GPIO19", "-", "boton cols 47-49; abajo -> riel GND"),
        ("Velocidad", "GPIO21", "-", "boton cols 52-54; abajo -> riel GND"),
        ("Modo", "GPIO22", "-", "boton cols 57-59; abajo -> riel GND"),
    ]
    ax = fig.add_axes([0.04, 0.33, 0.92, 0.58]); ax.axis("off")
    tb = ax.table(cellText=rows, colLabels=["Senal", "ESP32", "Componente", "Destino"], loc="upper left", cellLoc="left",
                  colWidths=[0.14, 0.09, 0.14, 0.63])
    tb.auto_set_font_size(False); tb.set_fontsize(10.5); tb.scale(1, 1.75)
    for (r, c), cell in tb.get_celld().items():
        if r == 0: cell.set_facecolor("#dfe6f3"); cell.set_text_props(fontweight="bold")
    tests = ["PRUEBAS: 1) Al energizar: Display 1 = 0, Display 2 = 9, sin contar (PAUSA).  2) GPIO18 -> RUNNING: uno sube, el otro baja.",
             "3) GPIO19 invierte direccion, GPIO21 alterna 500/250 ms, GPIO22 alterna OPPOSITE/SAME.  4) En pausa, 19/21/22 se ignoran.",
             "5) Monitor serie 115200 baud: STATE=, DIR=, SPEED=, MODE=.   Compilar/cargar:  pio run -t upload   |   pio device monitor",
             "FALLAS: nada enciende -> revisa GND comun y que el COM vaya al GPIO32/23.  Ambos displays iguales -> los COM deben ir a GPIO distintos.",
             "Un segmento apagado en ambos -> resistencia/jumper suelto.  Muy tenue -> normal con multiplexado y una sola resistencia por display."]
    for i, t in enumerate(tests):
        fig.text(0.04, 0.27 - i * 0.04, t, fontsize=11)
    pdf.savefig(fig); plt.close(fig)


def main():
    path = os.path.join(OUT, "Guia_Protoboard_63.pdf")
    with PdfPages(path) as pdf:
        page_intro(pdf)
        page_anatomy(pdf)
        page_stage(pdf, 1, "Paso 1 - GND y displays", [
            "1) Cable NEGRO: GND de la ESP32 -> riel GND superior (col 1).",
            "2) Cable NEGRO: riel superior -> riel inferior (col 2), asi hay GND arriba y abajo.",
            "3) Display 1 cruzando el canal en columnas 3-7 y Display 2 en columnas 19-23 (punto decimal abajo-derecha; COM en 5 y 21)."])
        page_stage(pdf, 2, "Paso 2 - Cables de GPIO de los segmentos", [
            "Sin resistencias por segmento. Un jumper de cada GPIO (13,16,14,27,26,25,33) a la fila inferior de las columnas 10 a 16 (orden a,b,c,d,e,f,g).",
            "Esas 7 columnas son el 'bus' de segmentos que en el paso 3 se reparte a los dos displays."])
        page_stage(pdf, 3, "Paso 3 - Puentes de los segmentos a los dos displays", [
            "Desde la tira INFERIOR de cada columna 10-16, dos jumpers del mismo color: uno al pin del segmento en Display 1 y otro al mismo pin en Display 2.",
            "Los pines de arriba del display son g,f,a,b y los de abajo e,d,c (COM y dp no se usan aqui)."])
        page_stage(pdf, 4, "Paso 4 - 470 ohm en los dos COM de cada display, hacia su GPIO", [
            "Display 1: una 470 en cada pin COM (col 5, arriba y abajo) hacia la col 8; jumper de GPIO32 a la col 8 arriba y un puente corto que une col 8 arriba con col 8 abajo.",
            "Display 2: igual con col 21 -> col 24 y GPIO23. Los 470 NO van a GND: van al GPIO. GPIO en 0 = display encendido."])
        page_stage(pdf, 5, "Paso 5 - Los 4 botones", [
            "Cada boton cruza el canal (cols 42-44, 47-49, 52-54, 57-59). Arriba: jumper al GPIO (18, 19, 21, 22).",
            "Abajo: jumper al riel GND inferior. No lleva resistencia: se usa el pull-up interno de la ESP32."])
        page_stage(pdf, 6, "Montaje final", [
            "Revisa contra la imagen: 4 resistencias de 470 ohm, 2 displays, 4 botones y sus jumpers.",
            "Conecta el USB y carga el programa."])
        page_table(pdf)
    print(path)

main()
