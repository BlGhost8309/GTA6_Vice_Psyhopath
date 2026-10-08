import pygame
from data import is_cheat_prefix


class Actions:
    """Что игрок сделал в этом кадре. Не мутирует state."""
    def __init__(self):
        self.quit = False
        self.restart = False
        self.toggle_help = False
        self.interact = False
        self.throw = False          # J
        self.next_weapon = False    # Q
        self.radio_key = 0          # 1-4
        self.escape = False
        self.confirm_yes = False
        self.confirm_no = False
        self.unicode_chars = []     # для чит-кодов
        self.keys = None            # pygame.key.get_pressed()
        self.mouse = None
        self.mouse_pos = (0, 0)


def poll(state):
    a = Actions()
    a.keys = pygame.key.get_pressed()
    a.mouse = pygame.mouse.get_pressed()
    a.mouse_pos = pygame.mouse.get_pos()

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            a.quit = True
            continue
        if e.type != pygame.KEYDOWN:
            continue

        # режим подтверждения выхода
        if state.confirm_exit:
            if e.key in (pygame.K_y, pygame.K_RETURN):
                a.quit = True
            elif e.key in (pygame.K_n, pygame.K_ESCAPE):
                a.confirm_no = True
            continue

        # буфер чит-кодов (обрабатывается в systems/cheats.py)
        if e.unicode and len(e.unicode) == 1 and e.unicode.isprintable():
            a.unicode_chars.append(e.unicode.lower())

        # Esc — приоритетная клавиша
        if e.key == pygame.K_ESCAPE:
            a.escape = True
            continue

        # R — работает ВСЕГДА, кроме случая, когда R сам является
        # частью набираемого чит-кода (буква 'r' есть только в "smorch").
        if e.key == pygame.K_r:
            prospective = (state.cheat_buffer + 'r')[-12:]
            if not is_cheat_prefix(prospective):
                a.restart = True
            continue

        # остальные клавиши не срабатывают во время активного набора чита
        if state.cheat_timer > 0:
            continue

        if e.key == pygame.K_h:
            a.toggle_help = True
        elif e.key == pygame.K_q:
            a.next_weapon = True
        elif e.key == pygame.K_f:
            a.interact = True
        elif e.key == pygame.K_j:
            a.throw = True
        elif e.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
            a.radio_key = e.key - pygame.K_0

    return a
