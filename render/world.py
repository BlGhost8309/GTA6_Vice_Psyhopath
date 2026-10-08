import pygame
from data import GRASS, ASPHALT, ROAD_LINE, BUILDING_EDGE, WORLD_W, WORLD_H


def draw(state, screen, cam):
    cam_x, cam_y = cam["cam_x"], cam["cam_y"]
    # ВАЖНО: это размер ИМЕННО поверхности, куда рисуем (zoom_surf).
    # Раньше тут брали W, H из config — и вся правая/нижняя часть
    # обрезалась отсечением, обнажая зелёную траву.
    SW, SH = screen.get_size()

    screen.fill(GRASS)

    for r in state.world.roads_v:
        rr = r.move(-cam_x, -cam_y)
        if rr.right >= 0 and rr.left <= SW:
            pygame.draw.rect(screen, ASPHALT, rr)
    for r in state.world.roads_h:
        rr = r.move(-cam_x, -cam_y)
        if rr.bottom >= 0 and rr.top <= SH:
            pygame.draw.rect(screen, ASPHALT, rr)

    for r in state.world.roads_v:
        x = r.centerx - cam_x
        if -10 <= x <= SW + 10:
            for y in range(0, WORLD_H, 90):
                sy = y - cam_y
                if -50 < sy < SH + 50:
                    pygame.draw.rect(screen, ROAD_LINE, (x - 2, sy, 4, 45))
    for r in state.world.roads_h:
        y = r.centery - cam_y
        if -10 <= y <= SH + 10:
            for x in range(0, WORLD_W, 90):
                sx = x - cam_x
                if -50 < sx < SW + 50:
                    pygame.draw.rect(screen, ROAD_LINE, (sx, y - 2, 45, 4))

    for b in state.world.buildings:
        rect = b["rect"]
        rr = rect.move(-cam_x, -cam_y)
        if rr.right < 0 or rr.left > SW or rr.bottom < 0 or rr.top > SH:
            continue
        pygame.draw.rect(screen, b["color"], rr)
        pygame.draw.rect(screen, BUILDING_EDGE, rr, 3)
        for wx in range(rr.left + 14, rr.right - 20, 34):
            for wy in range(rr.top + 14, rr.bottom - 30, 34):
                pygame.draw.rect(screen, (max(0, b["color"][0] - 25),
                                          max(0, b["color"][1] - 25),
                                          max(0, b["color"][2] - 25)),
                                 (wx, wy, 20, 20))
        dr = b["door"].move(-cam_x, -cam_y)
        pygame.draw.rect(screen, (200, 170, 90), dr)
        pygame.draw.rect(screen, (90, 70, 30), dr, 2)
        pygame.draw.circle(screen, (255, 230, 120), (dr.centerx, dr.centery), 2)
