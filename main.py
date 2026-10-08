"""
Clone City: Psychopath Cut v11 — точка входа.
Здесь ТОЛЬКО цикл. Вся логика — в systems/, рендер — в render/.
"""
import threading
import pygame

from config import screen, clock, W, H, font, huge_font
from assets import load_all
from world import World
from state import GameState
from utils import resource_path
import systems
import systems.input as input_mod
import systems.cheats as cheats
import render


# ==============================================================
# ЗАСТАВКА + ПРОГРЕСС-БАР ЗАГРУЗКИ
# ==============================================================
_splash_cache = {"surf": None, "rect": None}


def _prepare_splash():
    """Загружает и масштабирует assets/splash.png один раз, кладёт в кэш."""
    try:
        raw = pygame.image.load(resource_path("assets/splash.png")).convert()
    except Exception as e:
        print(f"[SPLASH] assets/splash.png не найден — фон будет чёрным. ({e})")
        _splash_cache["surf"] = None
        _splash_cache["rect"] = None
        return

    Wc, Hc = screen.get_size()
    sw, sh = raw.get_size()
    scale = min(Wc / sw, Hc / sh)
    new_size = (max(1, int(sw * scale)), max(1, int(sh * scale)))
    splash = pygame.transform.smoothscale(raw, new_size)
    _splash_cache["surf"] = splash
    _splash_cache["rect"] = splash.get_rect(center=(Wc // 2, Hc // 2))


_OUTLINE_8 = [(-1, 0), (1, 0), (0, -1), (0, 1),
              (-1, -1), (1, 1), (1, -1), (-1, 1)]


def _draw_loading(fraction):
    """Рисует заставку + компактный прогресс-бар + слово 'загрузка' под ним."""
    Wc, Hc = screen.get_size()
    screen.fill((0, 0, 0))

    if _splash_cache["surf"] is not None:
        screen.blit(_splash_cache["surf"], _splash_cache["rect"])

    text_h = 28
    bar_w = max(160, Wc // 4)
    bar_h = max(8, Hc // 10)
    bar_x = (Wc - bar_w) // 2
    bar_y = Hc - text_h - 6 - bar_h
    text_y = Hc - text_h - 2

    fraction = max(0.0, min(1.0, fraction))

    pygame.draw.rect(screen, (25, 60, 160), (bar_x, bar_y, bar_w, bar_h))

    fill_w = int(bar_w * fraction)
    if fill_w > 0:
        pygame.draw.rect(screen, (40, 200, 70), (bar_x, bar_y, fill_w, bar_h))
        gloss_h = max(2, bar_h // 6)
        pygame.draw.rect(screen, (120, 240, 130),
                         (bar_x, bar_y, fill_w, gloss_h))

    pygame.draw.rect(screen, (220, 230, 255), (bar_x, bar_y, bar_w, bar_h), 2)

    pct_text = f"{int(fraction * 100)}%"
    pct = huge_font.render(pct_text, True, (255, 230, 60))
    pct_shadow = huge_font.render(pct_text, True, (0, 0, 0))
    px = Wc // 2 - pct.get_width() // 2
    py = bar_y + bar_h // 2 - pct.get_height() // 2
    for ox, oy in _OUTLINE_8:
        screen.blit(pct_shadow, (px + ox, py + oy))
    screen.blit(pct, (px, py))

    t = font.render("загрузка", True, (255, 255, 255))
    t_shadow = font.render("загрузка", True, (0, 0, 0))
    cx = Wc // 2 - t.get_width() // 2
    for ox, oy in _OUTLINE_8:
        screen.blit(t_shadow, (cx + ox, text_y + oy))
    screen.blit(t, (cx, text_y))

    pygame.display.flip()


def _load_assets_with_bar():
    """Грузит спрайты в фоне, рисует прогресс-бар, возвращает Assets."""
    progress = {"done": 0, "total": 1}
    result = {"assets": None, "exc": None}

    def worker():
        try:
            def cb(done, total):
                progress["done"] = done
                progress["total"] = total
            result["assets"] = load_all(progress_cb=cb)
        except Exception as e:
            result["exc"] = e

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()

    shown = 0.0
    clk = pygame.time.Clock()
    while thread.is_alive() or shown < 0.999:
        real_dt = clk.tick(60) / 1000.0

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

        target = progress["done"] / max(1, progress["total"])
        if not thread.is_alive():
            target = 1.0

        diff = target - shown
        if diff > 0:
            shown += diff * min(1.0, real_dt * 8.0)
            if target - shown < 0.003:
                shown = target
        else:
            shown = target

        _draw_loading(shown)

    if result["exc"]:
        raise result["exc"]
    return result["assets"]


# ==============================================================
# MAIN
# ==============================================================
def main():
    _prepare_splash()
    _draw_loading(0.0)

    assets = _load_assets_with_bar()
    world = World()

    state = GameState(world, assets)
    state.zoom_surf = pygame.Surface((int(W / 0.75), int(H / 0.75)))
    state.view_w_base = W
    state.world_w = 3200
    state.world_h = 2400
    state.zoom_surf_size = state.zoom_surf.get_size()

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

        if actions.restart:
            try:
                state.reset()
            except Exception:
                import traceback
                print("[RESET] Ошибка при рестарте:")
                traceback.print_exc()
            render.frame(state, screen, real_dt)
            pygame.display.flip()
            continue

        cheats.process_chars(state, actions.unicode_chars)

        if state.cheat_timer <= 0:
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
