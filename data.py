import math

# ---------- МИР ----------
WORLD_W, WORLD_H = 3200, 2400
BLOCK   = 400
ROAD_W  = 120
LANE    = 32
ROOM_W, ROOM_H = 760, 480
MAX_STARS = 15

GRASS         = (58, 110, 60)
ASPHALT       = (62, 62, 68)
ROAD_LINE     = (230, 220, 120)
BUILDING_EDGE = (30, 30, 38)

DIRS      = [(0, -1), (1, 0), (0, 1), (-1, 0)]
DIR_ANGLE = [-math.pi / 2, 0, math.pi / 2, math.pi]

# ---------- БАНДЫ ----------
GANG_COLORS = [(200, 60, 60), (60, 80, 220), (60, 200, 80),
               (230, 200, 60), (200, 60, 200), (60, 200, 200)]
GANG_NAMES  = ["BLOODS", "CRIPS", "GREENS", "YELLOW", "PURPLE", "AZTECS"]

# ---------- ОРУЖИЕ ----------
WEAPONS = {
    "pistol":  {"cool": 0.15, "dmg": 22, "spread": 0.0,  "bullets": 1, "color": (200, 200, 200)},
    "uzi":     {"cool": 0.06, "dmg": 15, "spread": 0.09, "bullets": 1, "color": (255, 200, 60)},
    "shotgun": {"cool": 0.55, "dmg": 18, "spread": 0.28, "bullets": 5, "color": (180, 120, 80)},
    "ak47":    {"cool": 0.10, "dmg": 35, "spread": 0.04, "bullets": 1, "color": (150, 100, 60)},
}
WEAPON_ORDER = ["pistol", "uzi", "shotgun", "ak47"]

# ---------- ЧИТЫ ----------
CHEAT_CODES = ["god", "mortal", "weapons", "vice", "smorch",
               "noweather", "notime"]


def is_cheat_prefix(buf):
    if not buf:
        return False
    for c in CHEAT_CODES:
        for n in range(1, len(buf) + 1):
            if c.startswith(buf[-n:]):
                return True
    return False

# ---------- ФРАЗЫ ----------
GIRL_INSULTS = ["заплати, сука!", "заплати, козел!",
                "заплати, урод!", "заплати, гандон!"]
PIMP_INSULTS = ["Ты чё, лох, кинул мою девочку?!",
                "Я из тебя решето сделаю, козел!",
                "Верни бабки, гандон!",
                "Тебе конец, урод!",
                "Мою телку кидать вздумал?!",
                "Ща порву на британский флаг!"]

# ---------- РАДИО ----------
RADIO_STATIONS = ["", "VICE FM", "WAVE 103", "FLASH FM", "K-CHAT"]
