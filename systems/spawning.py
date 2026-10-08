import math
import random

from data import (WORLD_W, WORLD_H, BLOCK, LANE, DIRS, DIR_ANGLE)
from entities.vehicles import Car
from entities.npcs import Ped, Gangster, Pimp
from utils import add_floater


def pick_car_img(state):
    if state.assets.cars:
        return random.choice(state.assets.cars)
    return None


def spawn_ai_car(state):
    if random.random() < 0.5:
        m = random.randint(1, WORLD_H // BLOCK - 1)
        road = m * BLOCK
        d = random.choice([1, 3])
        lane = road + (LANE if d == 1 else -LANE)
        c = Car(random.uniform(200, WORLD_W - 200), lane, ai=True,
                img=pick_car_img(state))
    else:
        k = random.randint(1, WORLD_W // BLOCK - 1)
        road = k * BLOCK
        d = random.choice([0, 2])
        lane = road + (LANE if d == 0 else -LANE)
        c = Car(lane, random.uniform(200, WORLD_H - 200), ai=True,
                img=pick_car_img(state))
    c.ai_dir = d
    c.angle = DIR_ANGLE[d]
    return c


def seed_world(state):
    """Заполняет мир стартовыми сущностями. Вызывается из GameState.reset()."""
    w = state.world

    state.cars = [spawn_ai_car(state) for _ in range(18)]
    for _ in range(5):
        cx, cy, ca = w.rand_parked_car()
        state.cars.append(Car(cx, cy, ca,
                              alarm=(random.random() < 0.35),
                              img=pick_car_img(state)))

    for _ in range(55):
        px, py = w.rand_free_pos(12)
        state.peds.append(Ped(px, py))
    for _ in range(8):
        px, py = w.rand_free_pos(12)
        state.peds.append(Ped(px, py, "prostitute"))


def spawn_pimp_and_gang(state):
    ang = random.random() * math.tau
    px = state.player.x + math.cos(ang) * 700
    py = state.player.y + math.sin(ang) * 700
    px = max(80, min(WORLD_W - 80, px))
    py = max(80, min(WORLD_H - 80, py))
    state.pimp = Pimp(px, py)
    for i in range(4):
        a = i * math.pi / 2 + random.uniform(-0.3, 0.3)
        gx = px + math.cos(a) * 90
        gy = py + math.sin(a) * 90
        state.gangsters.append(Gangster(gx, gy))
    add_floater(state.floaters, px, py - 60,
                "СУТЕНЁР ПРИЕХАЛ!", (255, 60, 200), "big", 3.0)


def update(state, real_dt, actions):
    if state.game_over or state.show_help or state.confirm_exit:
        return
    if state.pimp_spawn_timer > 0:
        state.pimp_spawn_timer -= real_dt
        if state.pimp_spawn_timer <= 0 and state.pimp is None:
            spawn_pimp_and_gang(state)
