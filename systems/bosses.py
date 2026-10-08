import math
import random

from entities.bosses import Boss, TankBoss, Heli
from entities.projectiles import Bullet
from entities.projectiles import Laser
from utils import add_floater


def update(state, real_dt, actions):
    if state.game_over or state.show_help or state.confirm_exit:
        return
    dt = real_dt * state.time_scale
    player = state.player

    # ---------- ПИМП ----------
    if state.pimp is not None:
        pimp = state.pimp
        pdx, pdy = player.x - pimp.x, player.y - pimp.y
        pd = math.hypot(pdx, pdy) or 1
        pimp.angle = math.atan2(pdy, pdx)
        if pd > 90:
            pimp.x += pdx / pd * pimp.speed * dt
            pimp.y += pdy / pd * pimp.speed * dt
        state.world.clamp_world(pimp, pimp.radius)
        pimp.shoot_cool -= dt
        pimp.insult_cool -= dt
        if pd < 550 and pimp.shoot_cool <= 0:
            pimp.shoot_cool = 0.5
            for _ in range(2):
                state.bullets.append(Bullet(pimp.x, pimp.y,
                                            pimp.angle + random.uniform(-0.15, 0.15),
                                            "pimp", dmg=16))
        if pimp.insult_cool <= 0:
            pimp.insult_cool = random.uniform(2.5, 4.0)
            from data import PIMP_INSULTS
            add_floater(state.floaters, pimp.x, pimp.y - 55,
                        random.choice(PIMP_INSULTS), (255, 60, 200), "big", 2.5)
        if pd < 55:
            from .combat import damage_player
            damage_player(state, 35 * dt)
            state.shake = max(state.shake, 0.5)
        if pimp.hp <= 0:
            state.pimp = None
            player.money += 1000
            state.banner, state.banner_t = "СУТЕНЁР УБИТ!  +$1000", 3.0
            for _ in range(8):
                state.blood.append([player.x + random.randint(-80, 80),
                                    player.y + random.randint(-80, 80), 6.0])

    # ---------- БАНДИТЫ ----------
    for g in state.gangsters:
        gdx, gdy = player.x - g.x, player.y - g.y
        gd = math.hypot(gdx, gdy) or 1
        g.angle = math.atan2(gdy, gdx)
        if gd > 120:
            state.world.try_move(g, gdx / gd * g.speed * dt, gdy / gd * g.speed * dt, g.radius)
        else:
            g.shoot_cool -= dt
            if g.shoot_cool <= 0:
                g.shoot_cool = 0.65
                state.bullets.append(Bullet(g.x, g.y,
                                            g.angle + random.uniform(-0.15, 0.15),
                                            "gangster", dmg=10))

    # ---------- БОСС ----------
    if state.wanted >= 15 and state.boss is None and state.tank is None:
        ang = random.random() * math.tau
        state.boss = Boss(player.x + math.cos(ang) * 900,
                          player.y + math.sin(ang) * 900)
        state.world.clamp_world(state.boss, state.boss.radius)
        state.banner, state.banner_t = "ВАСЬКА СМОРЧКОВ ВЫЕХАЛ ЗА ТОБОЙ!", 4.0

    if state.boss is not None:
        boss = state.boss
        boss.life_timer += dt
        bdx, bdy = player.x - boss.x, player.y - boss.y
        bd = math.hypot(bdx, bdy) or 1
        boss.angle = math.atan2(bdy, bdx)

        if boss.on_foot:
            if bd > 70:
                boss.x += bdx / bd * boss.speed * dt
                boss.y += bdy / bd * boss.speed * dt
            state.world.clamp_world(boss, boss.radius)
            boss.shoot_cool -= dt
            if bd < 600 and boss.shoot_cool <= 0:
                boss.shoot_cool = 0.22
                for _ in range(3):
                    state.bullets.append(Bullet(boss.x, boss.y,
                                                boss.angle + random.uniform(-0.2, 0.2),
                                                "boss", dmg=14))
            if bd < 45:
                from .combat import damage_player
                damage_player(state, 50 * dt)
                state.shake = max(state.shake, 0.7)
        else:
            if bd > 95:
                boss.x += bdx / bd * boss.speed * dt
                boss.y += bdy / bd * boss.speed * dt
            state.world.clamp_world(boss, boss.radius)
            boss.shoot_cool -= dt
            if bd < 520 and boss.shoot_cool <= 0:
                boss.shoot_cool = 0.35
                for _ in range(2):
                    state.bullets.append(Bullet(boss.x, boss.y,
                                                boss.angle + random.uniform(-0.16, 0.16),
                                                "boss", dmg=18))
            if bd < 60:
                from .combat import damage_player
                damage_player(state, 40 * dt)
                state.shake = max(state.shake, 0.6)
            if boss.life_timer > 60 and state.tank is None:
                state.tank = TankBoss(boss.x + 300, boss.y)
                state.banner, state.banner_t = "ВАСЬКА-2 НА ТАНКЕ ПРИБЫЛ!", 3.5

    # ---------- ТАНК ----------
    if state.tank is not None:
        tank = state.tank
        tdx, tdy = player.x - tank.x, player.y - tank.y
        td = math.hypot(tdx, tdy) or 1
        tank.angle = math.atan2(tdy, tdx)
        if td > 220:
            tank.x += tdx / td * tank.speed * dt
            tank.y += tdy / td * tank.speed * dt
        state.world.clamp_world(tank, tank.radius)
        tank.shoot_cool -= dt
        if tank.shoot_cool <= 0 and td < 700:
            tank.shoot_cool = 1.2
            state.bullets.append(Bullet(tank.x, tank.y, tank.angle, "tank", dmg=45))
            add_floater(state.floaters, tank.x, tank.y - 50,
                        "БАБАХ!", (255, 140, 40), "big", 1.0)

    # ---------- ВЕРТОЛЁТ ----------
    if state.wanted >= 12 and state.heli is None:
        state.heli = Heli(player.x + 600, player.y - 600)
        state.banner, state.banner_t = "ВЕРТОЛЁТ-ОХОТНИК НА ПОДЛЁТЕ!", 3.0
    if state.heli is not None:
        heli = state.heli
        heli.bob += dt * 4
        hdx, hdy = player.x - heli.x, player.y - heli.y
        hd = math.hypot(hdx, hdy) or 1
        heli.angle = math.atan2(hdy, hdx)
        if hd > 260:
            heli.x += hdx / hd * heli.speed * dt
            heli.y += hdy / hd * heli.speed * dt
        state.world.clamp_world(heli, heli.radius)
        heli.shoot_cool -= dt
        if heli.shoot_cool <= 0 and hd < 700:
            heli.shoot_cool = 0.5
            state.bullets.append(Bullet(heli.x, heli.y,
                                        heli.angle + random.uniform(-0.08, 0.08),
                                        "heli", dmg=16))

    # ---------- ОРБИТАЛЬНЫЙ УДАР ----------
    if state.wanted >= 5:
        state.laser_cd -= dt
        if state.laser_cd <= 0:
            state.laser_cd = 20.0
            lx = player.x + random.uniform(-220, 220)
            ly = player.y + random.uniform(-220, 220)
            state.lasers.append(Laser(lx, ly))
            add_floater(state.floaters, lx, ly - 60,
                        "ОРБИТАЛЬНЫЙ УДАР!", (255, 60, 60), "big", 2.0)

    for L in state.lasers[:]:
        L.t -= dt
        if L.t <= 0:
            if not L.fired:
                L.fired = True
                for p in state.peds[:]:
                    if (p.x - L.x) ** 2 + (p.y - L.y) ** 2 < L.radius ** 2:
                        state.peds.remove(p)
                        state.blood.append([p.x, p.y, 6.0])
                for c in state.cops[:]:
                    if (c.x - L.x) ** 2 + (c.y - L.y) ** 2 < L.radius ** 2:
                        state.cops.remove(c)
                for g in state.gangsters[:]:
                    if (g.x - L.x) ** 2 + (g.y - L.y) ** 2 < L.radius ** 2:
                        state.gangsters.remove(g)
                for _ in range(20):
                    state.explosions.append({
                        "x": L.x + random.randint(-70, 70),
                        "y": L.y + random.randint(-70, 70),
                        "life": 1.2, "max": 1.2, "r": random.randint(25, 55)})
                from .combat import damage_player, damage_car
                if state.player.in_car is None:
                    if (state.player.x - L.x) ** 2 + (state.player.y - L.y) ** 2 < L.radius ** 2:
                        damage_player(state, 60)
                        state.shake = 1.0
                else:
                    car_p = state.player.in_car
                    if (car_p.x - L.x) ** 2 + (car_p.y - L.y) ** 2 < L.radius ** 2:
                        damage_car(state, car_p, 80)
            state.lasers.remove(L)
