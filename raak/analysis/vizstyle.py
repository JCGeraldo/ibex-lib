"""[raak local] Estilo comun de los graficos (Fase 4).

Paleta categorica del skill de visualizacion (orden fijo, validada para vision con deficiencia de
color en pares adyacentes); cada serie tiene SIEMPRE el mismo color, independientemente de cuantas
series haya en el grafico. Marcas finas, rejilla recesiva, texto en tinta neutra.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ranuras 1..8 de la paleta de referencia (modo claro)
SLOTS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]

# color fijo por variante (nivel 1 y nivel 2) y por modo trigonometrico (Fase 2)
VARIANT_COLOR = {
    "af2_k0": SLOTS[0], "af2_k3": SLOTS[1],
    "raa_k0": SLOTS[2], "raa_k3": SLOTS[3],
    "aa_k0":  SLOTS[4], "aa_k3":  SLOTS[5],
    "xn":     SLOTS[6],
}
VARIANT_LABEL = {
    "af2_k0": "AF2", "af2_k3": "AF2 + k-nomial",
    "raa_k0": "RAA", "raa_k3": "RAA + k-nomial",
    "aa_k0":  "AA",  "aa_k3":  "AA + k-nomial",
    "xn":     "X-Taylor (control)",
}
# k=3 se dibuja discontinuo: codificacion secundaria ademas del color
VARIANT_STYLE = {v: ("--" if v.endswith("k3") else "-") for v in VARIANT_COLOR}
MODE_COLOR = {"legacy": SLOTS[0], "cheb": SLOTS[1], "minrange": SLOTS[2]}
MODE_LABEL = {"legacy": "original del plugin (Gauss 2 pts)", "cheb": "cuerda (Chebyshev, RAA)", "minrange": "min-range"}

TEXT = "#0b0b0b"; TEXT2 = "#52514e"; GRID = "#e6e5e1"; SURFACE = "#fcfcfb"


def setup():
    plt.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "axes.edgecolor": GRID, "axes.labelcolor": TEXT2, "xtick.color": TEXT2, "ytick.color": TEXT2,
        "text.color": TEXT, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
        "axes.spines.top": False, "axes.spines.right": False, "lines.linewidth": 2.0,
        "lines.markersize": 6, "font.size": 10, "legend.frameon": False, "figure.dpi": 130,
    })


def variant_key(label):
    """'compo_af2_k3' -> 'af2_k3'; 'xn' -> 'xn'."""
    for lr in ("compo_", "art_"):
        if label.startswith(lr):
            return label[len(lr):]
    return label
