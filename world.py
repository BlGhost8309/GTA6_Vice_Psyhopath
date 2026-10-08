import math
import random

from data import (WORLD_W, WORLD_H, BLOCK, ROAD_W, LANE,
                  GANG_COLORS, WEAPON_ORDER)


class World:
    """Статическая геометрия: дороги, здания, зоны банд."""

    def __init__(self):
        self.buildings  = []
        self.roads_v    = []
        self.roads_h    = []
        self.gang_zone  = []
        self.zone_cols  = WORLD_W // BLOCK
        self.zone_rows  = WORLD_H // BLOCK
        self.generate()

    # ---------- ГЕНЕРАЦИЯ ----------
    def generate(self):
        self.buildings, self.roads_v, self.roads_h = [], [], []

        for gx in range(WORLD_W // BLOCK + 1):
            self.roads_v.append(pygame_rect(gx * BLOCK - ROAD_W // 2, 0,
                                            ROAD_W, WORLD_H))
        for gy in range(WORLD_H // BLOCK + 1):
            self.roads_h.append(pygame_rect(0, gy * BLOCK - ROAD_W // 2,
                                            WORLD_W, ROAD_W))

        self.gang_zone = [[(gx + gy) % len(GANG_COLORS)
                           for gy in range(self.zone_rows)]
                          for gx in range(self.zone_cols)]

        for gx in range(self.zone_cols):
            for gy in range(self.zone_rows):
                bx = gx * BLOCK + ROAD_W // 2 + 25
                by = gy * BLOCK + ROAD_W // 2 + 25
                bw = BLOCK - ROAD_W - 50
                bh = BLOCK - ROAD_W - 50
                if random.random() < 0.88:
                    g = self.gang_zone[gx][gy]
                    gc = GANG_COLORS[g]
                    base = (random.randint(60, 100),
                            random.randint(60, 100),
                            random.randint(70, 110))
                    tint = (min(255, base[0] + gc[0] // 6),
                            min(255, base[1] + gc[1] // 6),
                            min(255, base[2] + gc[2] // 6))
                    rect = pygame_rect(bx, by, bw, bh)
                    door = pygame_rect(bx + bw // 2 - 24,
                                       by + bh - 12, 48, 14)
                    weapon = None
                    if random.random() < 0.35:
                        wtype = random.choice(WEAPON_ORDER)
                        weapon = {"type": wtype,
                                  "x": random.randint(150, 600),
                                  "y": random.randint(150, 350),
                                  "taken": False}
                    self.buildings.append({
                        "rect": rect, "color": tint, "door": door,
                        "gang": g, "weapon": weapon})

    # ---------- КОЛЛИЗИИ ----------
    def hits_building(self, x, y, r):
        for b in self.buildings:
            rect = b["rect"]
            nx = max(rect.left, min(x, rect.right))
            ny = max(rect.top, min(y, rect.bottom))
            dx, dy = x - nx, y - ny
            if dx * dx + dy * dy < r * r:
                return True
        return False

    def try_move(self, ent, dx, dy, r):
        if not self.hits_building(ent.x + dx, ent.y, r):
            ent.x += dx
        if not self.hits_building(ent.x, ent.y + dy, r):
            ent.y += dy
        self.clamp_world(ent, r)

    def clamp_world(self, e, r=20):
        e.x = max(r + 12, min(WORLD_W - r - 12, e.x))
        e.y = max(r + 12, min(WORLD_H - r - 12, e.y))

    # ---------- КООРДИНАТЫ ----------
    def is_on_road(self, x, y):
        gx = round(x / BLOCK)
        gy = round(y / BLOCK)
        if abs(x - gx * BLOCK) < ROAD_W // 2:
            return True
        if abs(y - gy * BLOCK) < ROAD_W // 2:
            return True
        return False

    def zone_at(self, x, y):
        gx = max(0, min(self.zone_cols - 1, int(x // BLOCK)))
        gy = max(0, min(self.zone_rows - 1, int(y // BLOCK)))
        return self.gang_zone[gx][gy]

    def rand_free_pos(self, r=16):
        for _ in range(60):
            x = random.uniform(80, WORLD_W - 80)
            y = random.uniform(80, WORLD_H - 80)
            if not self.hits_building(x, y, r):
                return x, y
        return WORLD_W / 2, WORLD_H / 2

    def rand_parked_car(self):
        for _ in range(40):
            if random.random() < 0.5:
                gx = random.randint(0, WORLD_W // BLOCK)
                gy = random.randint(1, WORLD_H // BLOCK - 1)
                offset = random.choice([-1, 1]) * (ROAD_W // 2 - 22)
                x = gx * BLOCK + offset
                y = gy * BLOCK + random.randint(-120, 120)
                angle = math.pi / 2 if random.random() < 0.5 else -math.pi / 2
            else:
                gx = random.randint(1, WORLD_W // BLOCK - 1)
                gy = random.randint(0, WORLD_H // BLOCK)
                offset = random.choice([-1, 1]) * (ROAD_W // 2 - 22)
                x = gx * BLOCK + random.randint(-120, 120)
                y = gy * BLOCK + offset
                angle = 0 if random.random() < 0.5 else math.pi
            x = max(60, min(WORLD_W - 60, x))
            y = max(60, min(WORLD_H - 60, y))
            if not self.hits_building(x, y, 22):
                return x, y, angle
        x, y = self.rand_free_pos(30)
        return x, y, 0


# ленивый Rect — чтобы не тащить pygame в data
import pygame


def pygame_rect(x, y, w, h):
    return pygame.Rect(int(x), int(y), int(w), int(h))
