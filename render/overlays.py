import pygame
from config import W, H, font, huge_font, big_font, help_font, help_title


def draw(screen, state):
    if state.show_help:
        _help(screen, state)
    if state.confirm_exit:
        _confirm(screen)
    if state.game_over:
        _game_over(screen)


def _help(screen, state):
    ov = pygame.Surface((W, H), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 225))
    screen.blit(ov, (0, 0))
    title = help_title.render("CLONE CITY: PSYCHOPATH CUT v11 — ПОМОЩЬ",
                              True, (255, 100, 200))
    screen.blit(title, (W // 2 - title.get_width() // 2, 20))
    lines = [
        "",
        "УПРАВЛЕНИЕ:",
        "  WASD / стрелки  —  ходьба и вождение",
        "  F               —  дом / машина / снять девушку (50$) / подобрать ствол",
        "  J               —  КИДОК проститутки (не платишь)",
        "  J ×7 быстро     —  сброс всех звёзд, все боссы убегают",
        "  Q               —  сменить оружие (только из подобранных)",
        "  ЛКМ             —  стрелять",
        "  1 2 3 4         —  радио в машине",
        "  H               —  эта справка",
        "  Esc             —  закрыть справку / выход с подтверждением",
        "  R               —  рестарт",
        "",
        "ЧИТ-КОДЫ (набирай прямо в игре):",
        "  god       —  РЕЖИМ БОГА (неубиваемый)",
        "  mortal    —  выключить режим бога",
        "  weapons   —  выдать ВСЁ оружие сразу",
        "  vice      —  спавн розовой тачки рядом",
        "  noweather —  вкл/выкл погоду (дождь, гроза)",
        "  notime    —  вкл/выкл смену дня и ночи",
        "",
        "НОВОЕ В v11:",
        "  • ПАТРУЛИ ЕДУТ ПО ДОРОГАМ — ищут тебя через перекрёстки",
        "  • Если застряли 2 сек — принудительный поворот на перекрёстке",
        "  • ПУЛИ ПОПАДАЮТ В ПАТРУЛИ: урон, взрыв, +1.5★, +$150",
        "",
        "H или Esc — закрыть",
    ]
    y = 74
    for line in lines:
        col = (255, 255, 255)
        if line.endswith(":") or line.startswith(("ЧИТ", "НОВОЕ", "СТАРОЕ")):
            col = (120, 220, 255)
        if "ЧИТ-КОДЫ" in line:
            col = (255, 200, 60)
        if ("НОВОЕ В v11" in line or "ПАТРУЛИ ЕДУТ" in line
                or "ПУЛИ ПОПАДАЮТ" in line or "застряли" in line):
            col = (0, 255, 200)
        t = help_font.render(line, True, col)
        screen.blit(t, (70, y))
        y += 21


def _confirm(screen):
    ov = pygame.Surface((W, H), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 200))
    screen.blit(ov, (0, 0))
    t1 = huge_font.render("ВЫЙТИ ИЗ ИГРЫ?", True, (255, 200, 60))
    screen.blit(t1, (W // 2 - t1.get_width() // 2, H // 2 - 60))
    t2 = font.render("Y / Enter — выйти    N / Esc — отмена", True, (255, 255, 255))
    screen.blit(t2, (W // 2 - t2.get_width() // 2, H // 2 + 10))


def _game_over(screen):
    txt = big_font.render("ПОТРАЧЕНО", True, (220, 30, 30))
    screen.blit(txt, (W // 2 - txt.get_width() // 2, H // 2 - 40))
    sub = font.render("Нажми R для рестарта", True, (255, 255, 255))
    screen.blit(sub, (W // 2 - sub.get_width() // 2, H // 2 + 30))
