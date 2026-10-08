import math
import random

from data import GIRL_INSULTS


def try_interact(state):
    player = state.player
    world = state.world

    if player.in_car:
        car = player.in_car
        car.driver = None
        car.ai = False
        car.speed = 0
        for ang in (math.pi / 2, -math.pi / 2, math.pi, 0):
            px = car.x + math.cos(car.angle + ang) * 46
            py = car.y + math.sin(car.angle + ang) * 46
            if not world.hits_building(px, py, player.radius):
                player.x, player.y = px, py
                break
        else:
            player.x, player.y = car.x, car.y
        player.in_car = None
        return

    if state.inside is not None:
        w = state.inside.get("weapon")
        if w and not w["taken"]:
            if math.hypot(player.x - w["x"], player.y - w["y"]) < 55:
                give_weapon(state, w["type"])
                w["taken"] = True
                return
        door = state.inside["door"]
        player.x, player.y = door.centerx, door.centery + 46
        state.inside = None
        return

    best, bd = None, 1e9
    for c in state.cars:
        d = math.hypot(c.x - player.x, c.y - player.y)
        if d < 62 and d < bd:
            bd, best = d, ("car", c)
    for b in world.buildings:
        d = math.hypot(b["door"].centerx - player.x, b["door"].centery - player.y)
        if d < 48 and d < bd:
            bd, best = d, ("door", b)
    for p in state.peds:
        if p.kind != "prostitute": continue
        d = math.hypot(p.x - player.x, p.y - player.y)
        if d < 46 and d < bd:
            bd, best = d, ("girl", p)

    if best is None:
        return
    kind, obj = best

    if kind == "car":
        if obj.alarm and obj.driver is None and not obj.owner_angry:
            obj.alarm_t = 3.0
            obj.owner_angry = True
            state.wanted = min(15, state.wanted + 1.0)
            state.wanted_cool = 5.0
            from utils import add_floater
            add_floater(state.floaters, obj.x, obj.y - 40,
                        "СИГНАЛИЗАЦИЯ!  +1★", (255, 80, 80), "big", 2.5)
        obj.driver = player
        obj.ai = False
        obj.speed = 0
        obj.owner_angry = False
        player.in_car = obj
    elif kind == "door":
        state.inside = obj
        player.x, player.y = 760 / 2, 480 - 130
    elif kind == "girl":
        if player.girl_cd > 0:
            player.say(f"Подожди {int(player.girl_cd) + 1} сек...")
            return
        if player.money >= 50:
            player.money -= 50
            player.hp = min(100, player.hp + 45)
            player.energy = min(100, player.energy + 50)
            player.girl_cd = 30.0
            from utils import add_floater
            add_floater(state.floaters, player.x, player.y - 40,
                        "Fuck yeeeeeh", (255, 60, 200), "huge", 3.0)
            add_floater(state.floaters, player.x, player.y - 80,
                        "+50 ЭНЕРГИИ", (0, 255, 200), "big", 2.0)
            player.say("- $50   + HP   + ЭНЕРГИЯ")
        else:
            player.say("Нет денег, братан")


def give_weapon(state, wtype):
    from data import WEAPONS
    from utils import add_floater
    player = state.player
    if wtype not in player.weapons:
        player.weapons.append(wtype)
        add_floater(state.floaters, player.x, player.y - 40,
                    f"+{wtype.upper()}", (255, 200, 60), "big", 2.0)
    else:
        add_floater(state.floaters, player.x, player.y - 40,
                    wtype.upper(), (255, 200, 60), "small", 1.2)
    player.weapon = wtype


def try_throw(state):
    """J — кидок проститутки либо ×7 — сброс звёзд."""
    player = state.player
    near_girl = None
    if player.in_car is None and state.inside is None:
        for p in state.peds:
            if p.kind == "prostitute":
                if math.hypot(p.x - player.x, p.y - player.y) < 46:
                    near_girl = p
                    break
    if near_girl is not None:
        if player.girl_cd > 0:
            player.say(f"Подожди {int(player.girl_cd) + 1} сек...")
            return
        player.hp = min(100, player.hp + 45)
        player.energy = min(100, player.energy + 40)
        player.girl_cd = 30.0
        from utils import add_floater
        add_floater(state.floaters, near_girl.x, near_girl.y - 45,
                    random.choice(GIRL_INSULTS), (255, 80, 80), "huge", 2.5)
        player.say("Ты кинул её на 50$...")
        state.last_cheater_girl = near_girl
        state.pimp_spawn_timer = 3.0
        state.j_count = 0
        state.j_timer = 0
    else:
        if state.j_timer <= 0:
            state.j_count = 0
        state.j_count += 1
        state.j_timer = 0.6
        if state.j_count >= 7:
            for B in (state.boss, state.tank, state.heli):
                if B is not None:
                    from utils import add_floater
                    add_floater(state.floaters, B.x, B.y - 50,
                                "УБЕГАЮ!", (255, 255, 100), "big", 2.5)
            state.boss = None
            state.tank = None
            state.heli = None
            state.cops.clear()
            state.cop_cars.clear()
            state.wanted = 0.0
            state.wanted_cool = 0.0
            state.j_count = 0
            state.banner = "ЗВЁЗДЫ СБРОШЕНЫ. ВСЕ БОССЫ УБЕГАЛИ."
            state.banner_t = 3.0


def update(state, real_dt, actions):
    """Реагирует на действия из input, если игра активна."""
    if state.game_over or state.show_help or state.confirm_exit:
        return
    if actions.interact:
        try_interact(state)
    if actions.throw:
        try_throw(state)
    if actions.next_weapon and not state.show_help and not state.game_over:
        player = state.player
        if len(player.weapons) > 1:
            idx = player.weapons.index(player.weapon)
            player.weapon = player.weapons[(idx + 1) % len(player.weapons)]
            from utils import add_floater
            add_floater(state.floaters, player.x, player.y - 40,
                        player.weapon.upper(), (255, 200, 60), "small", 1.2)
        else:
            from utils import add_floater
            add_floater(state.floaters, player.x, player.y - 40,
                        "ТОЛЬКО ПИСТОЛЕТ", (200, 200, 200), "small", 1.2)
    if actions.radio_key:
        state.radio = actions.radio_key
        state.radio_t = 0
