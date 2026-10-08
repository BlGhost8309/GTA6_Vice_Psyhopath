import math
import pygame
from config import W, H, font, small, tiny, huge_font
from data import WEAPONS, GANG_COLORS, GANG_NAMES, RADIO_STATIONS


def draw(screen, state):
    player = state.player

    # HP
    if state.god_mode:
        pygame.draw.rect(screen, (60, 40, 0), (20, 20, 220, 22))
        pygame.draw.rect(screen, (255, 215, 0), (22, 22, 216, 18))
        screen.blit(font.render("HP ∞   GOD MODE", True, (60, 40, 0)), (26, 22))
    else:
        pygame.draw.rect(screen, (30, 30, 30), (20, 20, 220, 22))
        hp_w = int(216 * max(0, player.hp) / 100)
        hp_color = (60, 200, 60) if player.hp > 40 else (220, 60, 60)
        pygame.draw.rect(screen, hp_color, (22, 22, hp_w, 18))
        screen.blit(font.render(f"HP {int(max(0, player.hp))}", True, (255, 255, 255)),
                    (26, 22))

    # энергия
    pygame.draw.rect(screen, (20, 30, 40), (20, 48, 220, 16))
    en_w = int(216 * max(0, player.energy) / 100)
    if player.energy > 60:
        en_color = (0, 220, 255)
    elif player.energy > 25:
        en_color = (255, 200, 60)
    else:
        en_color = (220, 60, 60)
    pygame.draw.rect(screen, en_color, (22, 50, en_w, 12))
    screen.blit(tiny.render(f"ЭНЕРГИЯ {int(player.energy)}", True, (255, 255, 255)),
                (26, 49))

    if player.girl_cd > 0:
        screen.blit(tiny.render(f"GIRL CD: {int(player.girl_cd)}s",
                                True, (255, 120, 200)), (250, 50))

    # деньги
    screen.blit(huge_font.render(f"${player.money}", True, (0, 255, 120)),
                (W - 200, 16))

    # оружие
    wcol = WEAPONS[player.weapon]["color"]
    pygame.draw.rect(screen, (30, 30, 30), (W - 200, 60, 180, 26))
    pygame.draw.rect(screen, wcol, (W - 198, 62, 176, 22), 2)
    screen.blit(font.render(f"🔫 {player.weapon.upper()}", True, wcol),
                (W - 195, 63))
    inv_str = " ".join(w[:3].upper() for w in player.weapons)
    screen.blit(tiny.render(inv_str, True, (180, 180, 180)), (W - 200, 88))

    # звёзды
    stars = int(math.ceil(state.wanted))
    for i in range(min(stars, 15)):
        cx, cy = 32 + i * 26, 74
        pts = []
        for k in range(10):
            ang = -math.pi / 2 + k * math.pi / 5
            r = 11 if k % 2 == 0 else 5
            pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
        col = (255, 215, 0) if i < 7 else ((255, 120, 60) if i < 12 else (255, 40, 40))
        pygame.draw.polygon(screen, col, pts)

    # скорость/радио
    if player.in_car:
        sp = int(abs(player.in_car.speed) * 0.45)
        screen.blit(font.render(f"Скорость: {sp} км/ч", True, (255, 255, 255)),
                    (W - 200, 110))
        screen.blit(font.render(f"♪ {RADIO_STATIONS[state.radio]}",
                                True, (255, 200, 60)), (W - 200, 135))

    # время / погода
    hour = int(state.time_of_day * 24)
    minute = int((state.time_of_day * 24 - hour) * 60)
    wx = {"clear": "ЯСНО", "rain": "ДОЖДЬ", "storm": "ГРОЗА"}[state.weather]
    screen.blit(small.render(f"{hour:02d}:{minute:02d}  {wx}",
                             True, (200, 220, 255)), (W - 200, 160))

    # район
    g = state.world.zone_at(player.x, player.y)
    screen.blit(small.render(f"РАЙОН: {GANG_NAMES[g]}", True, GANG_COLORS[g]),
                (W - 200, 180))

    if state.cop_cars:
        screen.blit(small.render(f"ПАТРУЛЕЙ: {len(state.cop_cars)}",
                                 True, (100, 150, 255)), (W - 200, 200))
    if state.pimp is not None:
        screen.blit(small.render(f"СУТЕНЁР: {int(state.pimp.hp)} HP  |  БАНДА: {len(state.gangsters)}",
                                 True, (255, 100, 220)), (W - 260, 220))
    if state.boss is not None and state.boss.on_foot:
        screen.blit(small.render(f"SMORCH ФАЗА 2: {int(state.boss.hp)} HP",
                                 True, (255, 80, 80)), (W - 260, 240))

    # сообщение игрока
    if player.msg_t > 0:
        t = font.render(player.msg, True, (255, 255, 120))
        screen.blit(t, (W // 2 - t.get_width() // 2, H - 90))

    # баннер
    if state.banner_t > 0:
        t = huge_font.render(state.banner, True, (255, 40, 40))
        bg = pygame.Surface((t.get_width() + 40, t.get_height() + 20),
                            pygame.SRCALPHA)
        bg.fill((0, 0, 0, 170))
        screen.blit(bg, (W // 2 - bg.get_width() // 2, 180))
        screen.blit(t, (W // 2 - t.get_width() // 2, 190))

    # строка подсказок внизу
    screen.blit(small.render(
        "H — помощь   F — действие   J — кидок/сброс×7   Q — оружие   R — рестарт",
        True, (220, 220, 220)), (20, H - 28))
