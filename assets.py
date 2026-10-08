import pygame

from utils import resource_path


def clean_magenta(surf):
    surf = surf.convert_alpha()
    w, h = surf.get_size()
    for x in range(w):
        for y in range(h):
            r, g, b, a = surf.get_at((x, y))
            if r > 180 and b > 180 and g < 120:
                surf.set_at((x, y), (0, 0, 0, 0))
    return surf


def load_spritesheet(path, cols, rows):
    try:
        sheet = pygame.image.load(resource_path(path))
    except Exception as e:
        print(f"[SPRITE] {path} не найден — использую заглушку. ({e})")
        return None
    sheet = clean_magenta(sheet)
    sw, sh = sheet.get_size()
    fw, fh = sw // cols, sh // rows
    frames = []
    for r in range(rows):
        row = []
        for c in range(cols):
            rect = pygame.Rect(c * fw, r * fh, fw, fh)
            row.append(sheet.subsurface(rect).copy())
        frames.append(row)
    return frames


def load_single(path):
    try:
        img = pygame.image.load(resource_path(path))
    except Exception as e:
        print(f"[SPRITE] {path} не найден — заглушка. ({e})")
        return None
    return clean_magenta(img)


def load_sheet_row(path, cols):
    try:
        img = pygame.image.load(resource_path(path))
    except Exception as e:
        print(f"[SPRITE] {path} не найден — заглушка. ({e})")
        return None
    img = clean_magenta(img)
    sw, sh = img.get_size()
    fw = sw // cols
    return [img.subsurface(pygame.Rect(c * fw, 0, fw, sh)).copy()
            for c in range(cols)]


_scaled_cache = {}
_img_scaled_cache = {}


def get_scaled(surf, size):
    key = (id(surf), size)
    if key not in _scaled_cache:
        _scaled_cache[key] = pygame.transform.scale(surf, (size, size))
    return _scaled_cache[key]


def scale_to_width(img, target_w):
    if img is None:
        return None
    key = (id(img), target_w)
    if key in _img_scaled_cache:
        return _img_scaled_cache[key]
    ratio = target_w / img.get_width()
    new_h = max(1, int(img.get_height() * ratio))
    scaled = pygame.transform.scale(img, (target_w, new_h))
    _img_scaled_cache[key] = scaled
    return scaled


class Assets:
    """Контейнер всех загруженных спрайтов. Живёт в state.assets."""
    pass


def load_all(progress_cb=None):
    """Загружает все спрайты.
    progress_cb(done, total) — вызывается после каждого шага, если передан.
    """
    a = Assets()
    counter = {"done": 0, "total": 0}

    sheets = [
        ("player",     "assets/player.png", 4, 4),
        ("ped",        "assets/ped.png", 4, 4),
        ("prostitute", "assets/prostitute.png", 4, 4),
        ("cop",        "assets/cop.png", 4, 4),
        ("gangster",   "assets/gangster.png", 4, 4),
        ("pimp",       "assets/pimp.png", 4, 4),
        ("boss",       "assets/boss_smorch.png", 4, 4),
    ]
    singles = [
        ("boss_car", "assets/boss_car.png"),
        ("tank",     "assets/tank.png"),
        ("cop_car",  "assets/cop_car.png"),
    ]
    rows = [
        ("heli",    "assets/heli.png", 2),
        ("weapons", "assets/weapons.png", 4),
    ]

    total = len(sheets) + len(singles) + len(rows) + 5 + 1
    counter["total"] = total

    def tick():
        counter["done"] += 1
        if progress_cb:
            progress_cb(counter["done"], total)

    for name, path, cols, rows_n in sheets:
        setattr(a, name, load_spritesheet(path, cols, rows_n))
        tick()

    for name, path in singles:
        setattr(a, name, load_single(path))
        tick()

    for name, path, cols in rows:
        setattr(a, name, load_sheet_row(path, cols))
        tick()

    a.cars = []
    for i in range(1, 6):
        img = load_single(f"assets/cars/car_{i}.png")
        if img:
            a.cars.append(img)
        tick()

    if not a.cars:
        fallback = load_single("assets/car.png")
        if fallback:
            a.cars = [fallback]
            print("[SPRITE] Использую fallback assets/car.png для всех машин")
    print(f"[SPRITE] Загружено спрайтов машин: {len(a.cars)}")
    tick()

    return a
