import math
import random

from utils import add_hit_marker


def witness_check(state, x, y):
    for p in state.peds:
        if p.headless:
            continue
        if (p.x - x) ** 2 + (p.y - y) ** 2 < 350 ** 2:
            if p.witness_cd <= 0:
                p.witness_cd = 3.0
                state.wanted = min(15, state.wanted + 0.4)
                state.wanted_cool = 4.0
                from utils import add_floater
                add_floater(state.floaters, p.x, p.y - 30,
                            "☎ 911", (255, 80, 80), "small", 1.5)
                return True
    return False


def damage_player(state, amount):
    if state.god_mode:
        return
    state.player.hp -= amount
    if state.player.hp <= 0:
        state.game_over = True


def damage_car(state, car, dmg):
    car.hp -= dmg
    if car.hp > 0:
        return
    for _ in range(14):
        state.explosions.append({
            "x": car.x + random.randint(-30, 30),
            "y": car.y + random.randint(-30, 30),
            "life": 0.9, "max": 0.9, "r": random.randint(22, 44)})
    for p in state.peds[:]:
        if (p.x - car.x) ** 2 + (p.y - car.y) ** 2 < 100 ** 2:
            state.peds.remove(p)
            state.blood.append([p.x, p.y, 6.0])
    for c in state.cops[:]:
        if (c.x - car.x) ** 2 + (c.y - car.y) ** 2 < 100 ** 2:
            state.cops.remove(c)
    for g in state.gangsters[:]:
        if (g.x - car.x) ** 2 + (g.y - car.y) ** 2 < 100 ** 2:
            state.gangsters.remove(g)
    if state.pimp is not None and (state.pimp.x - car.x) ** 2 + (state.pimp.y - car.y) ** 2 < 100 ** 2:
        state.pimp.hp -= 80
    for B in (state.boss, state.tank, state.heli):
        if B is not None and (B.x - car.x) ** 2 + (B.y - car.y) ** 2 < 100 ** 2:
            B.hp -= 80
    if state.player.in_car is car:
        damage_player(state, 70)
        state.shake = 1.0
        car.driver = None
        state.player.in_car = None
        state.player.x = car.x + random.randint(-60, 60)
        state.player.y = car.y + random.randint(-60, 60)
    elif not state.player.in_car:
        if (state.player.x - car.x) ** 2 + (state.player.y - car.y) ** 2 < 100 ** 2:
            damage_player(state, 40)
            state.shake = 0.9
    if car in state.cars:
        state.cars.remove(car)


def update(state, real_dt, actions):
    if state.game_over or state.show_help or state.confirm_exit:
        return
    dt = real_dt * state.time_scale
    world = state.world
    player = state.player

    for b in state.bullets[:]:
        b.x += math.cos(b.angle) * b.speed * dt
        b.y += math.sin(b.angle) * b.speed * dt
        b.life -= dt
        if b.life <= 0 or world.hits_building(b.x, b.y, 2):
            if b in state.bullets:
                state.bullets.remove(b)
            continue
        hit = False

        if b.owner not in ("pimp", "gangster"):
            for p in state.peds[:]:
                if (p.x - b.x) ** 2 + (p.y - b.y) ** 2 < (p.radius + 3) ** 2:
                    state.peds.remove(p)
                    state.blood.append([p.x, p.y, 5.0])
                    if random.random() < 0.05:
                        from utils import add_floater
                        add_floater(state.floaters, p.x, p.y - 30,
                                    "💀 HEADSHOT", (255, 60, 60), "small", 1.5)
                    if b.owner == "player":
                        state.wanted = min(15, state.wanted + 0.7)
                        state.wanted_cool = 4.0
                        player.money += 20
                        add_hit_marker(state.floaters, p.x, p.y, b.dmg)
                        witness_check(state, p.x, p.y)
                        if state.slowmo_t <= 0:
                            state.slowmo_t = 1.5
                    hit = True
                    break

        if not hit and b.owner in ("cop", "boss", "tank", "heli", "pimp", "gangster"):
            if (player.x - b.x) ** 2 + (player.y - b.y) ** 2 < (player.radius + 4) ** 2:
                damage_player(state, b.dmg)
                state.shake = max(state.shake, 0.3)
                hit = True

        if not hit and b.owner == "player":
            for c in state.cops[:]:
                if (c.x - b.x) ** 2 + (c.y - b.y) ** 2 < (c.radius + 4) ** 2:
                    c.hp -= b.dmg
                    add_hit_marker(state.floaters, c.x, c.y, b.dmg)
                    if c.hp <= 0:
                        state.cops.remove(c)
                        state.blood.append([c.x, c.y, 5.0])
                        state.wanted = min(15, state.wanted + 1.5)
                        state.wanted_cool = 5.0
                        player.money += 80
                        if state.slowmo_t <= 0:
                            state.slowmo_t = 1.2
                    hit = True
                    break
            if not hit:
                for g in state.gangsters[:]:
                    if (g.x - b.x) ** 2 + (g.y - b.y) ** 2 < (g.radius + 4) ** 2:
                        g.hp -= b.dmg
                        add_hit_marker(state.floaters, g.x, g.y, b.dmg)
                        if g.hp <= 0:
                            state.gangsters.remove(g)
                            state.blood.append([g.x, g.y, 5.0])
                            player.money += 120
                        hit = True
                        break
            if not hit and state.pimp is not None:
                if (state.pimp.x - b.x) ** 2 + (state.pimp.y - b.y) ** 2 < (state.pimp.radius + 4) ** 2:
                    state.pimp.hp -= b.dmg
                    add_hit_marker(state.floaters, state.pimp.x, state.pimp.y, b.dmg, crit=True)
                    hit = True
                    if state.pimp.hp <= 0:
                        state.pimp = None
                        player.money += 1000
                        state.banner, state.banner_t = "СУТЕНЁР УБИТ!  +$1000", 3.0
            if not hit:
                for name, B in (("boss", state.boss), ("tank", state.tank), ("heli", state.heli)):
                    if B is not None and (B.x - b.x) ** 2 + (B.y - b.y) ** 2 < (B.radius + 6) ** 2:
                        B.hp -= b.dmg
                        add_hit_marker(state.floaters, B.x, B.y, b.dmg, crit=True)
                        hit = True
                        if B.hp <= 0:
                            if name == "boss":
                                if not state.boss.on_foot:
                                    state.boss.on_foot = True
                                    state.boss.hp = 300
                                    state.boss.max_hp = 300
                                    state.boss.speed = 420
                                    state.boss.radius = 18
                                    state.boss.shoot_cool = 0.2
                                    state.boss.anim_t = 0.0
                                    state.boss.anim_frame = 0
                                    state.banner, state.banner_t = "SMORCH ВЫШЕЛ ИЗ МАШИНЫ!", 3.5
                                    for _ in range(10):
                                        state.explosions.append({
                                            "x": state.boss.x + random.randint(-40, 40),
                                            "y": state.boss.y + random.randint(-40, 40),
                                            "life": 1.0, "max": 1.0,
                                            "r": random.randint(25, 50)})
                                else:
                                    state.boss = None
                                    player.money += 5000
                                    state.banner, state.banner_t = "SMORCH УНИЧТОЖЕН!  +$5000", 4.0
                                    for _ in range(10):
                                        state.blood.append([
                                            player.x + random.randint(-60, 60),
                                            player.y + random.randint(-60, 60), 6.0])
                            elif name == "tank":
                                state.tank = None
                                player.money += 8000
                                state.banner, state.banner_t = "ВАСЬКА-2 ВЗОРВАН!  +$8000", 4.0
                            elif name == "heli":
                                state.heli = None
                                player.money += 6000
                                state.banner, state.banner_t = "ВЕРТОЛЁТ СБИТ!  +$6000", 4.0
                        break

        if not hit and b.owner == "cop":
            for g in state.gangsters[:]:
                if (g.x - b.x) ** 2 + (g.y - b.y) ** 2 < (g.radius + 4) ** 2:
                    g.hp -= b.dmg
                    if g.hp <= 0:
                        state.gangsters.remove(g)
                        state.blood.append([g.x, g.y, 5.0])
                    hit = True
                    break
            if not hit and state.pimp is not None:
                if (state.pimp.x - b.x) ** 2 + (state.pimp.y - b.y) ** 2 < (state.pimp.radius + 4) ** 2:
                    state.pimp.hp -= b.dmg
                    hit = True
                    if state.pimp.hp <= 0:
                        state.pimp = None

        if not hit:
            for cc in state.cop_cars[:]:
                if (cc.x - b.x) ** 2 + (cc.y - b.y) ** 2 < (cc.radius + 4) ** 2:
                    cc.hp -= b.dmg
                    add_hit_marker(state.floaters, cc.x, cc.y, b.dmg)
                    if cc.hp <= 0:
                        state.cop_cars.remove(cc)
                        for _ in range(8):
                            state.explosions.append({
                                "x": cc.x + random.randint(-25, 25),
                                "y": cc.y + random.randint(-25, 25),
                                "life": 1.0, "max": 1.0,
                                "r": random.randint(20, 40)})
                        if b.owner == "player":
                            state.wanted = min(15, state.wanted + 1.5)
                            state.wanted_cool = 5.0
                            player.money += 150
                    hit = True
                    break

        if not hit:
            for c in state.cars[:]:
                if c is player.in_car: continue
                if (c.x - b.x) ** 2 + (c.y - b.y) ** 2 < (c.radius + 4) ** 2:
                    damage_car(state, c, b.dmg)
                    add_hit_marker(state.floaters, c.x, c.y, b.dmg)
                    hit = True
                    break

        if hit and b in state.bullets:
            state.bullets.remove(b)

    # обновление кровяки
    for s in state.blood[:]:
        s[2] -= dt
        if s[2] <= 0:
            state.blood.remove(s)
