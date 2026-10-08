from data import WEAPON_ORDER, is_cheat_prefix
from entities.bosses import Boss
from utils import add_floater


def process_chars(state, chars):
    """Вызывается из main при появлении новых символов."""
    if not chars:
        return
    player = state.player
    for ch in chars:
        state.cheat_buffer = (state.cheat_buffer + ch)[-12:]
        if is_cheat_prefix(state.cheat_buffer):
            state.cheat_timer = 0.6

        if state.cheat_buffer.endswith("god"):
            state.god_mode = True
            state.cheat_buffer = ""
            state.cheat_timer = 0.6
            add_floater(state.floaters, player.x, player.y - 50,
                        "GOD MODE ON", (255, 215, 0), "huge", 2.5)
        elif state.cheat_buffer.endswith("mortal"):
            state.god_mode = False
            state.cheat_buffer = ""
            state.cheat_timer = 0.6
            add_floater(state.floaters, player.x, player.y - 50,
                        "GOD MODE OFF", (255, 80, 80), "huge", 2.5)
        elif state.cheat_buffer.endswith("weapons"):
            player.weapons = WEAPON_ORDER[:]
            player.weapon = "ak47"
            state.cheat_buffer = ""
            state.cheat_timer = 0.6
            add_floater(state.floaters, player.x, player.y - 50,
                        "ВСЁ ОРУЖИЕ ВЫДАНО", (255, 200, 60), "big", 2.0)
        elif state.cheat_buffer.endswith("vice"):
            state.cheat_buffer = ""
            state.cheat_timer = 0.6
            from entities.vehicles import Car
            from systems.spawning import pick_car_img
            c = Car(player.x + 80, player.y, 0, color=(255, 105, 180),
                    img=pick_car_img(state))
            state.cars.append(c)
            add_floater(state.floaters, player.x, player.y - 50,
                        "VICE CAR", (255, 105, 180), "big", 2.0)
        elif state.cheat_buffer.endswith("smorch"):
            state.cheat_buffer = ""
            state.cheat_timer = 0.6
            import random, math
            ang = random.random() * math.tau
            state.boss = Boss(player.x + math.cos(ang) * 500,
                              player.y + math.sin(ang) * 500)
            state.banner_t = 0
            add_floater(state.floaters, player.x, player.y - 80,
                        "SMORCH ЗДЕСЬ!", (255, 60, 60), "huge", 2.5)
        elif state.cheat_buffer.endswith("noweather"):
            state.weather_disabled = not state.weather_disabled
            state.cheat_buffer = ""
            state.cheat_timer = 0.6
            add_floater(state.floaters, player.x, player.y - 50,
                        "ПОГОДА ОТКЛ" if state.weather_disabled else "ПОГОДА ВКЛ",
                        (120, 200, 255), "huge", 2.5)
        elif state.cheat_buffer.endswith("notime"):
            state.time_disabled = not state.time_disabled
            state.cheat_buffer = ""
            state.cheat_timer = 0.6
            add_floater(state.floaters, player.x, player.y - 50,
                        "ВРЕМЯ ОТКЛ" if state.time_disabled else "ВРЕМЯ ВКЛ",
                        (120, 200, 255), "huge", 2.5)
