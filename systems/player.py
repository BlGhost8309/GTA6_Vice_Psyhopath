import math
import random
import pygame

from data import WEAPONS, ROOM_W, ROOM_H
from entities.projectiles import Bullet
from utils import facing_row_from_deg
from config import W, H


def update(state, real_dt, actions):
    if state.game_over or state.show_help or state.confirm_exit:
        return

    dt = real_dt * state.time_scale
    player = state.player
    keys = actions.keys
    mouse = actions.mouse
    world = state.world

    player.msg_t = max(0, player.msg_t - dt)
    if player.girl_cd > 0:
        player.girl_cd = max(0.0, player.girl_cd - real_dt)

    # ---- ДВИЖЕНИЕ В ПОМЕЩЕНИИ ----
    if state.inside is not None:
        dx = dy = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += 1
        if keys[pygame.K_w] or keys[pygame.K_UP]: dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy += 1
        if dx or dy:
            l = math.hypot(dx, dy)
            player.angle = math.atan2(dy, dx)
            player.moving = True
            player.facing_row = facing_row_from_deg(math.degrees(player.angle))
            player.x = max(40, min(ROOM_W - 40, player.x + dx / l * player.speed * dt))
            player.y = max(40, min(ROOM_H - 40, player.y + dy / l * player.speed * dt))
        else:
            player.moving = False
        return

    # ---- В МАШИНЕ ----
    if player.in_car:
        car = player.in_car
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            car.speed += 750 * dt
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            car.speed -= 750 * dt
        else:
            car.speed *= (0.985 ** (dt * 60))
        car.speed = max(-240, min(450, car.speed))

        turn = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  turn -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: turn += 1
        if turn and abs(car.speed) > 8:
            car.angle += turn * 2.7 * dt * (1 if car.speed > 0 else -1)
        car.speed *= (0.997 ** (dt * 60))

        dxm = math.cos(car.angle) * car.speed * dt
        dym = math.sin(car.angle) * car.speed * dt
        if not world.hits_building(car.x + dxm, car.y, car.radius):
            car.x += dxm
        else:
            car.speed *= -0.2
            state.shake = max(state.shake, 0.4)
        if not world.hits_building(car.x, car.y + dym, car.radius):
            car.y += dym
        else:
            car.speed *= -0.2
            state.shake = max(state.shake, 0.4)
        world.clamp_world(car, car.radius)
        player.x, player.y = car.x, car.y
        player.moving = False
    else:
        # ---- ПЕШКОМ ----
        dx = dy = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += 1
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy += 1
        if dx or dy:
            l = math.hypot(dx, dy)
            player.angle = math.atan2(dy, dx)
            player.moving = True
            player.facing_row = facing_row_from_deg(math.degrees(player.angle))
            if player.energy > 0:
                player.energy = max(0, player.energy - 12 * dt)
                spd = player.speed * 1.35
            else:
                spd = player.speed * 0.55
            world.try_move(player, dx / l * spd * dt, dy / l * spd * dt, player.radius)
        else:
            player.moving = False
            player.energy = min(100, player.energy + 7 * dt)

    # ---- СТРЕЛЬБА ----
    wcfg = WEAPONS[player.weapon]
    player.shoot_cool -= dt
    if mouse[0] and player.shoot_cool <= 0:
        mx, my = actions.mouse_pos
        Bw, Bh = state.zoom_surf.get_size()
        zoom = state.zoom_level

        vw = int(W + (Bw - W) * zoom)
        vh = int(H + (Bh - H) * zoom)
        off_x = (Bw - vw) // 2
        off_y = (Bh - vh) // 2

        # курсор в пикселях дисплея -> в пиксели вида -> в мир
        sx = off_x + mx * (vw / W)
        sy = off_y + my * (vh / H)
        wx = sx + state.cam_x
        wy = sy + state.cam_y

        a = math.atan2(wy - player.y, wx - player.x)
        for _ in range(wcfg["bullets"]):
            aa = a + random.uniform(-wcfg["spread"], wcfg["spread"])
            state.bullets.append(
                Bullet(player.x, player.y, aa, "player", dmg=wcfg["dmg"]))
        player.shoot_cool = wcfg["cool"]

    # ---- АНИМАЦИЯ ----
    if player.moving and not player.in_car:
        player.anim_t += real_dt
        if player.anim_t >= 0.15:
            player.anim_t = 0.0
            player.anim_frame = (player.anim_frame + 1) % 4
    else:
        player.anim_frame = 0
        player.anim_t = 0.0
