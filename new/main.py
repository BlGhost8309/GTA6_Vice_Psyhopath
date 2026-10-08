"""
Clone City: Psychopath Cut v11 — точка входа.
Здесь ТОЛЬКО цикл. Вся логика — в systems/, рендер — в render/.
"""
import pygame

from config import screen, clock, W, H, font
from assets import load_all
from world import World
from state import GameState
import systems
import systems.input as input_mod
import systems.cheats as cheats
import render


# ==============================================================
# ЗАСТАВКА
# ==============================================================
SPLASH_TIMEOUT = 3.0   # секунд максимум, если игрок ничего не нажал


def _show_splash():
    """Показывает assets/splash.png с надписью 'загрузка' внизу справа.
    Ждёт клик/клавишу или SPLASH_TIMEOUT секунд. Если картинки нет — тихо выходит."""
    from config import small

    try:
        raw = pygame.image.load("assets/splash.png")
    except Exception as e:
        print(f"[SPLASH] assets/splash.png не найден — пропуск заставки. ({e})")
        return

    raw = raw.convert()
    sw, sh = raw.get_size()

    # вписываем с сохранением пропорций (letterbox)
    scale = min(W / sw, H / sh)
    new_size = (max(1, int(sw * scale)), max(1, int(sh * scale)))
    splash = pygame.transform.smoothscale(raw, new_size)
    splash_rect = splash.get_rect(center=(W // 2, H // 2))

    # надпись "загрузка" внизу справа
    text_surf = small.render("загрузка", True, (255, 255, 255))
    text_rect = text_surf.get_rect()
    text_rect.bottomright = (W - 24, H - 18)

    # лёгкая тень под текстом, чтобы читался на любом фоне
    shadow = small.render("загрузка", True, (0, 0, 0))
    shadow_rect = shadow.get_rect()
    shadow_rect.bottomright = (text_rect.right + 2, text_rect.bottom + 2)

    t = 0.0
    waiting = True
    while waiting:
        real_dt = clock.tick(60) / 1000.0
        t += real_dt

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                waiting = False

        if t >= SPLASH_TIMEOUT:
            waiting = False

        screen.fill((0, 0, 0))
        screen.blit(splash, splash_rect)
        screen.blit(shadow, shadow_rect)
        screen.blit(text_surf, text_rect)
        pygame.display.flip()


# ==============================================================
# ЭКРАН ЗАГРУЗКИ СПРАЙТОВ (без текста — просто чёрный)
# ==============================================================
def _loading_screen():
    screen.fill((0, 0, 0))
    pygame.display.flip()
    pygame.event.pump()


# ==============================================================
# MAIN
# ==============================================================
def main():
    # 1. заставка
    _show_splash()

    # 2. спрайты
    _loading_screen()
    assets = load_all()
    world = World()

    state = GameState(world, assets)
    state.zoom_surf = pygame.Surface((int(W / 0.75), int(H / 0.75)))
    state.view_w_base = W
    state.world_w = 3200
    state.world_h = 2400
    state.zoom_surf_size = state.zoom_surf.get_size()

    # 3. игровой цикл
    while state.running:
        real_dt = min(clock.tick(60) / 1000.0, 0.05)

        actions = input_mod.poll(state)

        if actions.escape:
            if state.show_help:
                state.show_help = False
            else:
                state.confirm_exit = True

        if state.confirm_exit:
            if actions.quit:
                break
            if actions.confirm_no:
                state.confirm_exit = False
            render.frame(state, screen, real_dt)
            pygame.display.flip()
            continue

        if actions.quit:
            break

        cheats.process_chars(state, actions.unicode_chars)

        if state.cheat_timer <= 0:
            if actions.restart:
                state.reset()
            if actions.toggle_help:
                state.show_help = not state.show_help

        systems.interactions.update(state, real_dt, actions)

        if not state.game_over and not state.show_help:
            for system in systems.ORDER:
                system.update(state, real_dt, actions)

        render.frame(state, screen, real_dt)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()