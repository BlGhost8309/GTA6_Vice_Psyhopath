import math
import pygame
from config import font, big_font, tiny


def draw_world_effects(state, screen, cam):
    cam_x, cam_y = cam["cam_x"], cam["cam_y"]
    SW, SH = screen.get_size()

    # кровь
    for s in state.blood:
        sx, sy = int(s[0] - cam_x), int(s[1] - cam_y)
        a = min(1.0, s[2] / 4.0)
        if -40 < sx < SW + 40 and -40 < sy < SH + 40:
            pygame.draw.circle(screen, (int(150 * a), 0, 0), (sx, sy), 14)

    # взрывы
    for ex in state.explosions:
        t = ex["life"] / ex["max"]
        sx, sy = int(ex["x"] - cam_x), int(ex["y"] - cam_y)
        r = int(ex["r"] * (1.4 - t * 0.4))
        if -80 < sx < SW + 80 and -80 < sy < SH + 80:
            pygame.draw.circle(screen, (int(255 * t), int(120 * t), 0), (sx, sy), r)
            pygame.draw.circle(screen, (255, int(220 * t), int(80 * t)),
                               (sx, sy), r // 2)

    # флоатеры
    for f in state.floaters:
        sx, sy = int(f["x"] - cam_x), int(f["y"] - cam_y)
        t = min(1.0, f["life"] / f["max"])
        alpha = int(255 * t)
        if f["size"] == "huge":
            s_txt = big_font.render(f["text"], True, f["color"])
            s_out = big_font.render(f["text"], True, (0, 0, 0))
        elif f["size"] == "small":
            s_txt = tiny.render(f["text"], True, f["color"])
            s_out = tiny.render(f["text"], True, (0, 0, 0))
        else:
            s_txt = font.render(f["text"], True, f["color"])
            s_out = font.render(f["text"], True, (0, 0, 0))
        s_txt.set_alpha(alpha)
        s_out.set_alpha(alpha)
        for ox, oy in [(-3, 0), (3, 0), (0, -3), (0, 3),
                       (-2, -2), (2, 2), (2, -2), (-2, 2)]:
            screen.blit(s_out, (sx - s_out.get_width() // 2 + ox,
                                sy - s_out.get_height() // 2 + oy))
        screen.blit(s_txt, (sx - s_txt.get_width() // 2,
                            sy - s_txt.get_height() // 2))

    # подсказки у игрока
    if not state.player.in_car:
        hint = None
        player = state.player
        for b in state.world.buildings:
            if math.hypot(b["door"].centerx - player.x, b["door"].centery - player.y) < 48:
                hint = "F — войти в дом"; break
        if hint is None:
            for c in state.cars:
                if math.hypot(c.x - player.x, c.y - player.y) < 62:
                    hint = "F — сесть в машину" + (" (СИГНАЛИЗАЦИЯ!)" if c.alarm else "")
                    break
        if hint is None:
            for p in state.peds:
                if p.kind == "prostitute" and math.hypot(p.x - player.x, p.y - player.y) < 46:
                    hint = "F — снять (50$)   J — кинуть"; break
        if hint:
            sx, sy = int(player.x - cam_x), int(player.y - cam_y)
            t = font.render(hint, True, (255, 255, 255))
            bg = pygame.Surface((t.get_width() + 14, t.get_height() + 8), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 160))
            screen.blit(bg, (sx - t.get_width() // 2 - 7, sy - 62))
            screen.blit(t, (sx - t.get_width() // 2, sy - 58))

    # затемнение по времени суток
    hour = state.time_of_day * 24
    if 6 <= hour <= 20:
        dark = max(0, min(180, int((abs(hour - 13) / 7) * 120)))
    else:
        dark = 180
    if dark > 0:
        overlay = pygame.Surface((SW, SH), pygame.SRCALPHA)
        overlay.fill((0, 0, 20, dark))
        screen.blit(overlay, (0, 0))


def draw_screen_effects(state, screen):
    SW, SH = screen.get_size()

    # дождь поверх
    for r in state.rain:
        pygame.draw.line(screen, (180, 200, 240),
                         (r[0], r[1]), (r[0] - 2, r[1] + 10), 2)

    if state.flash > 0:
        ov = pygame.Surface((SW, SH), pygame.SRCALPHA)
        ov.fill((255, 255, 255, int(120 * state.flash)))
        screen.blit(ov, (0, 0))
