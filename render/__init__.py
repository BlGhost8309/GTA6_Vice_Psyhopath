"""Единая точка рендера. Чистая функция: не мутирует state."""
from . import camera, world, entities, effects, hud, overlays
from .sprites import draw_npc_sprite, draw_rotated_image, draw_player_sprite


def frame(state, screen, real_dt):
    cam = camera.update(state, real_dt)

    # фоновый зум-суффейс
    view_w = cam["view_w"]
    view_h = cam["view_h"]
    zoom_surf = state.zoom_surf

    # ---------- внутренняя сцена ----------
    if state.inside is not None:
        _render_inside(state, zoom_surf)
    else:
        world.draw(state, zoom_surf, cam)
        entities.draw_world_entities(state, zoom_surf, cam)

    if not state.inside:
        effects.draw_world_effects(state, zoom_surf, cam)

    # ---------- масштабирование и вывод ----------
    sub = zoom_surf.subsurface((cam["off_x"], cam["off_y"], view_w, view_h))
    import pygame
    from config import W as RW, H as RH
    scaled = pygame.transform.smoothscale(sub, (RW, RH))
    screen.blit(scaled, (0, 0))

    if state.inside is None:
        effects.draw_screen_effects(state, screen)

    # ---------- HUD + оверлеи ----------
    hud.draw(screen, state)
    overlays.draw(screen, state)


def _render_inside(state, surf):
    import pygame
    from data import ROOM_W, ROOM_H, WEAPONS, WEAPON_ORDER
    from config import small, font
    from assets import scale_to_width

    surf.fill((28, 24, 32))
    pygame.draw.rect(surf, (72, 62, 58), (20, 20, ROOM_W - 40, ROOM_H - 40))
    pygame.draw.rect(surf, (40, 34, 32), (20, 20, ROOM_W - 40, ROOM_H - 40), 6)
    for fx in range(60, ROOM_W - 60, 80):
        pygame.draw.line(surf, (60, 52, 50), (fx, 30), (fx, ROOM_H - 30), 1)
    pygame.draw.rect(surf, (90, 60, 40), (90, 90, 160, 80))
    pygame.draw.rect(surf, (60, 90, 120), (ROOM_W - 250, 90, 150, 90))
    pygame.draw.rect(surf, (120, 100, 70),
                     (ROOM_W // 2 - 70, ROOM_H // 2 - 40, 140, 70))

    w = state.inside.get("weapon")
    if w and not w["taken"]:
        wx, wy = int(w["x"]), int(w["y"])
        idx = WEAPON_ORDER.index(w["type"])
        drew = False
        frames = state.assets.weapons
        if frames and idx < len(frames):
            wf = frames[idx]
            scaled = scale_to_width(wf, 50)
            if scaled:
                surf.blit(scaled, scaled.get_rect(center=(wx, wy)))
                drew = True
        if not drew:
            pygame.draw.rect(surf, (40, 40, 40), (wx - 18, wy - 8, 36, 16))
            pygame.draw.rect(surf, (120, 80, 40), (wx - 18, wy - 8, 36, 16), 2)
            col = WEAPONS[w["type"]]["color"]
            pygame.draw.rect(surf, col, (wx - 10, wy - 12, 20, 8))
            pygame.draw.rect(surf, (0, 0, 0), (wx - 10, wy - 12, 20, 8), 1)
        t = small.render(w["type"].upper(), True, (255, 220, 100))
        surf.blit(t, (wx - t.get_width() // 2, wy - 38))

    door = pygame.Rect(ROOM_W // 2 - 34, ROOM_H - 30, 68, 26)
    pygame.draw.rect(surf, (200, 170, 90), door)
    pygame.draw.rect(surf, (110, 90, 40), door, 3)
    surf.blit(small.render("ВЫХОД", True, (40, 30, 10)), (door.x + 10, door.y + 5))

    px, py = int(state.player.x), int(state.player.y)
    draw_player_sprite(surf, state, px, py)

    if w and not w["taken"]:
        import math
        if math.hypot(state.player.x - w["x"], state.player.y - w["y"]) < 55:
            t = font.render(f"F — подобрать {w['type'].upper()}", True, (255, 220, 100))
            surf.blit(t, (w["x"] - t.get_width() // 2, w["y"] - 70))
    import math
    if math.hypot(state.player.x - door.centerx, state.player.y - door.centery) < 55:
        t = font.render("F — выйти", True, (255, 255, 255))
        surf.blit(t, (door.centerx - t.get_width() // 2, door.y - 32))
