import math
import random

from data import WORLD_W, WORLD_H, BLOCK, LANE, DIRS, DIR_ANGLE
from entities.npcs import Cop
from entities.vehicles import CopCar
from .traffic import snap_to_lane


def ai_update_cop(state, cc, dt):
    edge = BLOCK // 2
    if cc.ai_dir == 1 and cc.x > WORLD_W - edge:
        cc.ai_dir = 3; snap_to_lane(cc, 3); return
    if cc.ai_dir == 3 and cc.x < edge:
        cc.ai_dir = 1; snap_to_lane(cc, 1); return
    if cc.ai_dir == 2 and cc.y > WORLD_H - edge:
        cc.ai_dir = 0; snap_to_lane(cc, 0); return
    if cc.ai_dir == 0 and cc.y < edge:
        cc.ai_dir = 2; snap_to_lane(cc, 2); return

    vx, vy = DIRS[cc.ai_dir]
    positive = (vx + vy) > 0
    player = state.player
    dx = player.x - cc.x
    dy = player.y - cc.y
    dist = math.hypot(dx, dy)

    if dist < 220 and state.world.is_on_road(cc.x, cc.y):
        cc.speed += (0 - cc.speed) * min(1.0, dt * 5.0)
        if cc.speed < 1.0:
            cc.speed = 0.0
        cc.angle = math.atan2(dy, dx)
        cc.deploy_t -= dt
        if cc.deploy_t <= 0 and cc.deployed < cc.max_deploy:
            a = random.random() * math.tau
            px = cc.x + math.cos(a) * 55
            py = cc.y + math.sin(a) * 55
            if not state.world.hits_building(px, py, 12):
                state.cops.append(Cop(px, py))
                cc.deployed += 1
                cc.deploy_t = 0.6
        return

    target_speed = 240.0
    for o in state.cars:
        rx, ry = o.x - cc.x, o.y - cc.y
        dot = rx * vx + ry * vy
        perp = abs(rx * (-vy) + ry * vx)
        if 0 < dot < 90 and perp < 36:
            target_speed = 0.0
            break

    ahead_x = cc.x + vx * 70
    ahead_y = cc.y + vy * 70
    if state.world.hits_building(ahead_x, ahead_y, cc.radius + 4):
        target_speed = 0.0

    cc.speed += (target_speed - cc.speed) * min(1.0, dt * 4.5)
    if cc.speed < 0.5:
        cc.speed = 0.0

    if cc.speed < 20 and dist > 220:
        cc.stuck_t += dt
    else:
        cc.stuck_t = 0.0
    cc.change_cd = max(0.0, cc.change_cd - dt)

    state.world.try_move(cc, vx * cc.speed * dt, vy * cc.speed * dt, cc.radius)

    if not state.world.is_on_road(cc.x, cc.y):
        gx = round(cc.x / BLOCK); gy = round(cc.y / BLOCK)
        dxr = abs(cc.x - gx * BLOCK); dyr = abs(cc.y - gy * BLOCK)
        if dxr < dyr: cc.x = gx * BLOCK
        else:         cc.y = gy * BLOCK
        cc.speed = 0.0
        return

    axis = cc.x if vx else cc.y
    if cc.target_axis is None:
        if positive:
            cc.target_axis = (math.floor(axis / BLOCK) + 1) * BLOCK
        else:
            cc.target_axis = (math.ceil(axis / BLOCK) - 1) * BLOCK

    crossed = ((positive and axis >= cc.target_axis) or
               ((not positive) and axis <= cc.target_axis))

    if cc.stuck_t > 1.5 and cc.change_cd <= 0:
        cc.ai_dir = (cc.ai_dir + random.choice([1, 3])) % 4
        snap_to_lane(cc, cc.ai_dir)
        cc.speed = 0.0
        cc.stuck_t = 0.0
        cc.change_cd = 1.5
        cc.target_axis = None
        return

    if not crossed:
        return

    ix = cc.target_axis
    if vx: inter_x, inter_y = ix, cc.y
    else:  inter_x, inter_y = cc.x, ix

    dxp = player.x - inter_x
    dyp = player.y - inter_y

    opposite = (cc.ai_dir + 2) % 4
    best_dir = cc.ai_dir
    best_score = -1e9
    for d in range(4):
        if d == opposite: continue
        dvx, dvy = DIRS[d]
        score = dvx * dxp + dvy * dyp
        if d != cc.ai_dir:
            score -= 60
        if score > best_score:
            best_score = score
            best_dir = d

    cc.ai_dir = best_dir
    if cc.ai_dir in (1, 3):
        road_y = round(inter_y / BLOCK) * BLOCK
        cc.y = road_y + (LANE if cc.ai_dir == 1 else -LANE)
        cc.x = inter_x
    else:
        road_x = round(inter_x / BLOCK) * BLOCK
        cc.x = road_x + (LANE if cc.ai_dir == 0 else -LANE)
        cc.y = inter_y

    cc.angle = DIR_ANGLE[cc.ai_dir]

    nvx, nvy = DIRS[cc.ai_dir]
    npos = (nvx + nvy) > 0
    a2 = cc.x if nvx else cc.y
    if npos:
        cc.target_axis = (math.floor((a2 + 0.5) / BLOCK) + 1) * BLOCK
    else:
        cc.target_axis = (math.ceil((a2 - 0.5) / BLOCK) - 1) * BLOCK


def update(state, real_dt, actions):
    if state.game_over or state.show_help or state.confirm_exit:
        return
    dt = real_dt * state.time_scale

    # апдейт копов-пешеходов
    for c in state.cops:
        targets = [("player", state.player)]
        if state.pimp is not None:
            targets.append(("pimp", state.pimp))
        for g in state.gangsters:
            targets.append(("gang", g))
        best_t, bd = state.player, 1e9
        for nm, t in targets:
            d = math.hypot(t.x - c.x, t.y - c.y)
            if d < bd:
                bd, best_t = d, t
        cdx, cdy = best_t.x - c.x, best_t.y - c.y
        c.angle = math.atan2(cdy, cdx)
        if bd > 130:
            state.world.try_move(c, cdx / bd * c.speed * dt, cdy / bd * c.speed * dt, c.radius)
        else:
            c.shoot_cool -= dt
            if c.shoot_cool <= 0:
                c.shoot_cool = 0.75
                from entities.projectiles import Bullet
                state.bullets.append(Bullet(c.x, c.y,
                                            c.angle + random.uniform(-0.13, 0.13),
                                            "cop", dmg=12))

    # спавн патрулей
    state.cop_car_cd -= dt
    if state.wanted >= 1 and state.cop_car_cd <= 0 and len(state.cop_cars) < min(3, int(state.wanted)):
        state.cop_car_cd = random.uniform(4.0, 7.0)
        ang = random.random() * math.tau
        dist = random.uniform(500, 800)
        cx = max(80, min(WORLD_W - 80, state.player.x + math.cos(ang) * dist))
        cy = max(80, min(WORLD_H - 80, state.player.y + math.sin(ang) * dist))
        gx = round(cx / BLOCK); gy = round(cy / BLOCK)
        if abs(cx - gx * BLOCK) < abs(cy - gy * BLOCK):
            cx = gx * BLOCK + LANE
        else:
            cy = gy * BLOCK + LANE
        new_cc = CopCar(cx, cy)
        new_cc.ai_dir = random.choice([0, 1, 2, 3])
        new_cc.angle = DIR_ANGLE[new_cc.ai_dir]
        new_cc.target_axis = None
        state.cop_cars.append(new_cc)

    for cc in state.cop_cars[:]:
        cc.blink += dt * 8
        ai_update_cop(state, cc, dt)
        if cc.deployed >= cc.max_deploy:
            state.cop_cars.remove(cc)

    # поддержание количества копов под звёзды
    target_cops = int(state.wanted)
    while len(state.cops) < target_cops:
        ang = random.random() * math.tau
        px = max(60, min(WORLD_W - 60, state.player.x + math.cos(ang) * 800))
        py = max(60, min(WORLD_H - 60, state.player.y + math.sin(ang) * 800))
        if not state.world.hits_building(px, py, 14):
            state.cops.append(Cop(px, py))
        else:
            break
    while len(state.cops) > target_cops + 2:
        state.cops.pop()
