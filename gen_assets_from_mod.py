"""Cosecha assets del mod (truco-fabric) hacia truco-web/assets/mod/.

Repetible: correrlo de nuevo re-sincroniza todo desde el jar-source del mod.
- Copias 1:1: mate, senas/*, icon del mod, paneles nine-slice de la GUI,
  mesa_de_truco_top (refresco: el usuario la retoco a mano en el mod).
- Compuestos: mesa_grande_top.png (los 4 cuadrantes NW/NE/SW/SE en 32x32) y
  carpincho_<nivel>.png "paperdoll" (frente de cabeza+cuerpo+patas recortado de
  la skin real 64x66; picante/messi llevan el frente del poncho encima).

Los UVs salen de CapybaraModel (26.2): cabeza texOffs(0,26) caja 8x7x8 ->
frente en (8,34) 8x7; cuerpo texOffs(0,0) caja 10x9x15 -> frente en (15,15)
10x9; pata texOffs(34,26) caja 3x4x3 -> frente en (37,29) 3x4; poncho
texOffs(0,43) caja 10x6x15 -> frente en (15,58) 10x6.
"""
from PIL import Image
import os
import shutil

MOD = r"E:\Minecraft Mods Propios\truco-fabric\src\main\resources\assets\truco"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "mod")
TEX = os.path.join(MOD, "textures")


def copy(rel_src, name):
    dst = os.path.join(OUT, name)
    shutil.copyfile(os.path.join(MOD, rel_src), dst)
    print("copiado", name)


def mesa_grande():
    """Los 4 cuadrantes del top de la Mesa Grande en una sola imagen 32x32."""
    out = Image.new("RGBA", (32, 32))
    for name, (x, y) in {"nw": (0, 0), "ne": (16, 0), "sw": (0, 16), "se": (16, 16)}.items():
        out.paste(Image.open(os.path.join(TEX, "block", f"mesa_de_truco_grande_top_{name}.png")), (x, y))
    out.save(os.path.join(OUT, "mesa_grande_top.png"))
    print("compuesto mesa_grande_top.png")


def paperdoll(skin_name, out_name, poncho):
    """Figura frontal 12x22 recortada de la skin: cabeza arriba, cuerpo, 2 patas."""
    skin = Image.open(os.path.join(TEX, "entity", f"{skin_name}.png")).convert("RGBA")
    head = skin.crop((8, 34, 16, 41))    # 8x7
    body = skin.crop((15, 15, 25, 24))   # 10x9
    leg = skin.crop((37, 29, 40, 33))    # 3x4
    fig = Image.new("RGBA", (12, 22))
    fig.paste(head, (2, 0), head)
    fig.paste(body, (1, 7), body)
    if poncho:
        pon = skin.crop((15, 58, 25, 64))  # 10x6, tapa la parte alta del cuerpo
        fig.paste(pon, (1, 7), pon)
    fig.paste(leg, (2, 16), leg)
    fig.paste(leg, (7, 16), leg)
    fig.save(os.path.join(OUT, out_name))
    print("paperdoll", out_name)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(os.path.join(OUT, "senas"), exist_ok=True)
    copy(r"textures\item\mate.png", "mate.png")
    copy(r"textures\block\pava.png", "pava.png")
    copy(r"textures\block\mesa_de_truco_top.png", "mesa_top.png")
    copy("icon.png", "mod_icon.png")
    copy(r"textures\gui\table_frame.png", "table_frame.png")
    copy(r"textures\gui\panel_dark.png", "panel_dark.png")
    copy(r"textures\gui\anotador_paper.png", "anotador_paper.png")
    for s in os.listdir(os.path.join(TEX, "gui", "senas")):
        copy(rf"textures\gui\senas\{s}", os.path.join("senas", s))
    mesa_grande()
    paperdoll("carpincho_tranqui", "nivel_tranqui.png", poncho=False)
    paperdoll("carpincho_canchero", "nivel_canchero.png", poncho=False)
    paperdoll("carpincho_picante", "nivel_picante.png", poncho=True)
    paperdoll("carpincho_messi", "nivel_messi.png", poncho=True)
    print("OK")
