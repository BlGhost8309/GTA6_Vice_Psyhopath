import os
import sys
import math
import random


def resource_path(rel):
    """Возвращает путь к ресурсу, работающий и как .py, и внутри PyInstaller-exe.
    rel — путь вроде "assets/splash.png" (без ведущего слэша)."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, rel)
    return os.path.join(os.path.abspath("."), rel)


def get_facing_row(angle):
    """Угол в радианах → строка спрайт-листа (0=юг, 1=запад, 2=север, 3=восток)."""
    deg = (math.degrees(angle) + 360) % 360
    if 45 <= deg < 135: return 0
    if 135 <= deg < 225: return 1
    if 225 <= deg < 315: return 3
    return 2


def facing_row_from_deg(deg):
    deg = (deg + 360) % 360
    if 45 <= deg < 135: return 0
    if 135 <= deg < 225: return 1
    if 225 <= deg < 315: return 3
    return 2


def add_floater(floaters, x, y, text, color=(255, 255, 100),
                size="big", life=3.0):
    floaters.append({"x": x, "y": y, "text": text, "color": color,
                     "life": life, "max": life, "size": size, "vy": -50})


def add_hit_marker(floaters, x, y, dmg, crit=False):
    add_floater(floaters, x + random.randint(-8, 8), y - 20,
                str(dmg) + ("!" if crit else ""),
                (255, 60, 60) if crit else (255, 255, 255),
                "small", life=0.8)
