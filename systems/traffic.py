import math
import random

from data import (WORLD_W, WORLD_H, BLOCK, LANE, DIRS, DIR_ANGLE)


# ---------- утилиты маршрутизации ----------
def snap_to_lane(car, new_dir):
    if new_dir in (1, 3):
        road_y = round(car.y / BLOCK) * BLOCK
        car.y = road_y + (LANE if new_dir == 1 else -LANE)
    else:
        road_x = round(car.x / BLOCK) * BLOCK
        car.x = road_x + (LANE if new_dir == 0 else -LANE)
    car.angle = DIR_ANGLE[new_dir]
    nvx, nvy = DIRS[new_dir]
    npos = (nvx + nvy) > 0
    a2 = car.x if nvx else car.y
    if npos:
        car.target_axis = (math.floor(a2 / BLOCK) + 1) * BLOCK
    else:
        car.target_axis = (math.ceil(a2 / BLOCK) - 1) * BLOCK


def snap_car_to_road(car):
    gx = round(car.x / BLOCK)
    gy = round(car.y / BLOCK)
    dx = abs(car.x - gx * BLOCK)
    dy = abs(car.y - gy * BLOCK)
    if dx < dy:
        car.x = gx * BLOCK
    else:
        car.y = gy * BLOCK
    snap_to_lane(car, car.ai_dir)
    car.speed = 0.0
    car.stuck_t = 0.0
    car.change_cd = 1.5


def ai_update(state, car, dt):
    edge = BLOCK // 2
    if car.ai_dir == 1 and car.x > WORLD_W - edge:
        car.ai_dir = 3; snap_to_lane(car, 3); return
    if car.ai_dir == 3 and car.x < edge:
        car.ai_dir = 1; snap_to_lane(car, 1); return
    if car.ai_dir == 2 and car.y > WORLD_H - edge:
        car.ai_dir = 0; snap_to_lane(car, 0); return
    if car.ai_dir == 0 and car.y < edge:
        car.ai_dir = 2; snap_to_lane(car, 2); return

    vx, vy = DIRS[car.ai_dir]
    positive = (vx + vy) > 0
    target = 185.0
    blocked = False

    for o in state.cars:
        if o is car: continue
        rx, ry = o.x - car.x, o.y - car.y
        dot = rx * vx + ry * vy
        perp = abs(rx * (-vy) + ry * vx)
        if 0 < dot < 85 and perp < 34:
            target = 0.0
            blocked = True
            break
    if target > 0 and state.player.in_car is None:
        rx, ry = state.player.x - car.x, state.player.y - car.y
        dot = rx * vx + ry * vy
        perp = abs(rx * (-vy) + ry * vx)
        if 0 < dot < 70 and perp < 26:
            target = 0.0
            blocked = True

    car.speed += (target - car.speed) * min(1.0, dt * 4.5)
    if car.speed < 0.5: car.speed = 0.0

    if blocked and car.speed < 20:
        car.stuck_t += dt
    else:
        car.stuck_t = 0.0

    car.change_cd = max(0, car.change_cd - dt)

    if car.stuck_t > 1.5 and car.change_cd <= 0:
        if random.random() < 0.7:
            if random.random() < 0.5:
                new_dir = (car.ai_dir + 1) % 4
            else:
                new_dir = (car.ai_dir - 1) % 4
            snap_to_lane(car, new_dir)
            car.ai_dir = new_dir
            car.speed = 0.0
            car.stuck_t = 0.0
            car.change_cd = 2.0
            return

    if vx: car.x += vx * car.speed * dt
    else:  car.y += vy * car.speed * dt

    if not state.world.is_on_road(car.x, car.y):
        snap_car_to_road(car)
        return

    axis = car.x if vx else car.y
    if car.target_axis is None:
        car.target_axis = ((math.floor(axis / BLOCK) + 1) * BLOCK if positive
                           else (math.ceil(axis / BLOCK) - 1) * BLOCK)

    crossed = ((positive and axis >= car.target_axis) or
               ((not positive) and axis <= car.target_axis))
    if not crossed:
        return

    ix = car.target_axis
    r = random.random()
    if r < 0.24:
        car.ai_dir = (car.ai_dir + 1) % 4
    elif r < 0.48:
        car.ai_dir = (car.ai_dir - 1) % 4

    if vx: inter_x, inter_y = ix, car.y
    else:  inter_x, inter_y = car.x, ix

    if car.ai_dir in (1, 3):
        car.y = round(inter_y / BLOCK) * BLOCK + (LANE if car.ai_dir == 1 else -LANE)
        car.x = inter_x
    else:
        car.x = round(inter_x / BLOCK) * BLOCK + (LANE if car.ai_dir == 0 else -LANE)
        car.y = inter_y

    car.angle = DIR_ANGLE[car.ai_dir]

    nvx, nvy = DIRS[car.ai_dir]
    npos = (nvx + nvy) > 0
    a2 = car.x if nvx else car.y
    car.target_axis = ((math.floor((a2 + 0.5) / BLOCK) + 1) * BLOCK if npos
                       else (math.ceil((a2 - 0.5) / BLOCK) - 1) * BLOCK)


def resolve_car_collisions(state):
    cars = state.cars
    for i in range(len(cars)):
        for j in range(i + 1, len(cars)):
            a, b = cars[i], cars[j]
            dx, dy = b.x - a.x, b.y - a.y
            d = math.hypot(dx, dy)
            md = a.radius + b.radius
            if 0.001 < d < md:
                ov = (md - d) / 2
                nx, ny = dx / d, dy / d
                a.x -= nx * ov; a.y -= ny * ov
                b.x += nx * ov; b.y += ny * ov
                a.speed *= 0.35; b.speed *= 0.35
                state.world.clamp_world(a, a.radius)
                state.world.clamp_world(b, b.radius)


def update(state, real_dt, actions):
    if state.game_over or state.show_help or state.confirm_exit:
        return
    dt = real_dt * state.time_scale
    for c in state.cars:
        if c.ai:
            ai_update(state, c, dt)
        state.world.clamp_world(c, c.radius)
    resolve_car_collisions(state)

    # сбивание педов и копов машиной игрока
    car = state.player.in_car
    if car and abs(car.speed) > 110:
        for p in state.peds[:]:
            if (p.x - car.x) ** 2 + (p.y - car.y) ** 2 < (car.radius + p.radius) ** 2:
                state.peds.remove(p)
                state.blood.append([p.x, p.y, 6.0])
                from utils import add_floater
                add_floater(state.floaters, p.x, p.y - 20, "+50$",
                            (0, 255, 120), "small", 1.5)
                state.player.money += 50
                state.wanted = min(15, state.wanted + 0.6)
                state.wanted_cool = 4.0
                state.shake = max(state.shake, 0.35)
        for c in state.cops[:]:
            if (c.x - car.x) ** 2 + (c.y - car.y) ** 2 < (car.radius + c.radius) ** 2:
                state.cops.remove(c)
                state.blood.append([c.x, c.y, 6.0])
                state.wanted = min(15, state.wanted + 1.2)
                state.wanted_cool = 5.0
        for g in state.gangsters[:]:
            if (g.x - car.x) ** 2 + (g.y - car.y) ** 2 < (car.radius + g.radius) ** 2:
                state.gangsters.remove(g)
                state.blood.append([g.x, g.y, 6.0])
                state.player.money += 150
