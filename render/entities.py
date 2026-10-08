import math
import pygame
from config import small
from .sprites import draw_npc_sprite, draw_rotated_image, draw_player_sprite


def draw_world_entities(state, screen, cam):
    cam_x, cam_y = cam["cam_x"], cam["cam_y"]
    SW, SH = screen.get_size()
    a = state.assets

    # пули
    for b in state.bullets:
        sx, sy = int(b.x - cam_x), int(b.y - cam_y)
        if -10 < sx < SW + 10 and -10 < sy < SH + 10:
            colors = {"player": (255, 230, 120), "cop": (255, 120, 80),
                      "boss": (255, 60, 60), "tank": (255, 160, 30),
                      "heli": (255, 200, 60), "pimp": (255, 60, 200),
                      "gangster": (255, 140, 60)}
            pygame.draw.circle(screen, colors.get(b.owner, (255, 255, 255)),
                               (sx, sy), 3)

    # педы
    for p in state.peds:
        sx, sy = int(p.x - cam_x), int(p.y - cam_y)
        if -30 < sx < SW + 30 and -30 < sy < SH + 30:
            frames = a.prostitute if p.kind == "prostitute" else a.ped
            if not draw_npc_sprite(screen, frames, sx, sy, p.angle, p.anim_frame, p.radius * 3):
                pygame.draw.circle(screen, p.color, (sx, sy), p.radius)
                ex = sx + math.cos(p.angle) * p.radius
                ey = sy + math.sin(p.angle) * p.radius
                pygame.draw.line(screen, (60, 40, 30), (sx, sy), (ex, ey), 2)

    # копы
    for c in state.cops:
        sx, sy = int(c.x - cam_x), int(c.y - cam_y)
        if -30 < sx < SW + 30 and -30 < sy < SH + 30:
            if not draw_npc_sprite(screen, a.cop, sx, sy, c.angle, c.anim_frame, c.radius * 3):
                pygame.draw.circle(screen, (60, 80, 220), (sx, sy), c.radius)
                pygame.draw.circle(screen, (255, 255, 255), (sx, sy), c.radius, 2)

    # гангстеры
    for g in state.gangsters:
        sx, sy = int(g.x - cam_x), int(g.y - cam_y)
        if -30 < sx < SW + 30 and -30 < sy < SH + 30:
            if not draw_npc_sprite(screen, a.gangster, sx, sy, g.angle, g.anim_frame, g.radius * 3):
                pygame.draw.circle(screen, (120, 40, 160), (sx, sy), g.radius)

    # машины
    for c in state.cars:
        sx, sy = int(c.x - cam_x), int(c.y - cam_y)
        if sx < -70 or sx > SW + 70 or sy < -70 or sy > SH + 70:
            continue
        if not draw_rotated_image(screen, c.img, sx, sy, c.angle, target_w=80):
            surf = pygame.Surface((54, 28), pygame.SRCALPHA)
            surf.fill(c.color)
            pygame.draw.rect(surf, (30, 30, 30), surf.get_rect(), 2)
            rot = pygame.transform.rotate(surf, -math.degrees(c.angle))
            screen.blit(rot, rot.get_rect(center=(sx, sy)))
        if c.hp < 100:
            bw = 44
            pygame.draw.rect(screen, (40, 0, 0), (sx - bw // 2, sy - 34, bw, 5))
            pygame.draw.rect(screen, (220, 60, 60),
                             (sx - bw // 2, sy - 34,
                              int(bw * max(0, c.hp) / 100), 5))

    # патрули
    for cc in state.cop_cars:
        sx, sy = int(cc.x - cam_x), int(cc.y - cam_y)
        if sx < -80 or sx > SW + 80 or sy < -80 or sy > SH + 80:
            continue
        if not draw_rotated_image(screen, a.cop_car, sx, sy, cc.angle, target_w=85):
            surf = pygame.Surface((54, 28), pygame.SRCALPHA)
            surf.fill((30, 50, 140))
            pygame.draw.rect(surf, (255, 255, 255), (2, 8, 50, 4))
            pygame.draw.rect(surf, (30, 30, 30), surf.get_rect(), 2)
            rot = pygame.transform.rotate(surf, -math.degrees(cc.angle))
            screen.blit(rot, rot.get_rect(center=(sx, sy)))
        if int(cc.blink) % 2 == 0:
            pygame.draw.circle(screen, (255, 30, 30), (sx - 12, sy), 5)
            pygame.draw.circle(screen, (30, 100, 255), (sx + 12, sy), 5)
        else:
            pygame.draw.circle(screen, (30, 100, 255), (sx - 12, sy), 5)
            pygame.draw.circle(screen, (255, 30, 30), (sx + 12, sy), 5)

    # пимп
    if state.pimp is not None:
        pimp = state.pimp
        sx, sy = int(pimp.x - cam_x), int(pimp.y - cam_y)
        if not draw_npc_sprite(screen, a.pimp, sx, sy, pimp.angle, pimp.anim_frame, pimp.radius * 3):
            pygame.draw.circle(screen, (200, 40, 140), (sx, sy), pimp.radius)
        bw = 120
        pygame.draw.rect(screen, (40, 0, 40), (sx - bw // 2, sy - 44, bw, 8))
        pygame.draw.rect(screen, (255, 60, 200),
                         (sx - bw // 2, sy - 44,
                          int(bw * pimp.hp / pimp.max_hp), 8))
        t = small.render("PIMP", True, (255, 100, 220))
        screen.blit(t, (sx - t.get_width() // 2, sy - 62))

    # босс
    if state.boss is not None:
        boss = state.boss
        sx, sy = int(boss.x - cam_x), int(boss.y - cam_y)
        if boss.on_foot:
            if not draw_npc_sprite(screen, a.boss, sx, sy, boss.angle, boss.anim_frame, boss.radius * 3):
                pygame.draw.circle(screen, (255, 60, 60), (sx, sy), boss.radius)
            label = "SMORCH ФАЗА 2"
            col = (255, 40, 40)
        else:
            if not draw_rotated_image(screen, a.boss_car, sx, sy, boss.angle, target_w=100):
                pygame.draw.circle(screen, (20, 20, 24), (sx, sy), boss.radius)
            label = "SMORCH"
            col = (220, 30, 30)
        bw = 140
        pygame.draw.rect(screen, (40, 0, 0), (sx - bw // 2, sy - 44, bw, 8))
        pygame.draw.rect(screen, col, (sx - bw // 2, sy - 44,
                                       int(bw * boss.hp / boss.max_hp), 8))
        t = small.render(label, True, (255, 100, 100))
        screen.blit(t, (sx - t.get_width() // 2, sy - 62))

    # танк
    if state.tank is not None:
        tank = state.tank
        sx, sy = int(tank.x - cam_x), int(tank.y - cam_y)
        if not draw_rotated_image(screen, a.tank, sx, sy, tank.angle, target_w=120):
            pygame.draw.circle(screen, (40, 60, 40), (sx, sy), 42)
        bw = 140
        pygame.draw.rect(screen, (40, 0, 0), (sx - bw // 2, sy - 66, bw, 8))
        pygame.draw.rect(screen, (255, 120, 30),
                         (sx - bw // 2, sy - 66,
                          int(bw * tank.hp / tank.max_hp), 8))
        t = small.render("VASYA-2", True, (255, 160, 60))
        screen.blit(t, (sx - t.get_width() // 2, sy - 84))

    # вертолёт
    if state.heli is not None:
        heli = state.heli
        sx = int(heli.x - cam_x)
        sy = int(heli.y - cam_y + math.sin(heli.bob) * 6)
        drew = False
        if a.heli:
            frame = a.heli[int(heli.bob * 2) % len(a.heli)]
            from assets import scale_to_width
            scaled = scale_to_width(frame, 90)
            if scaled:
                rot = pygame.transform.rotate(scaled, -math.degrees(heli.angle))
                screen.blit(rot, rot.get_rect(center=(sx, sy)))
                drew = True
        if not drew:
            pygame.draw.circle(screen, (60, 60, 70), (sx, sy), 20)
        bw = 100
        pygame.draw.rect(screen, (40, 0, 0), (sx - bw // 2, sy - 44, bw, 6))
        pygame.draw.rect(screen, (255, 200, 60),
                         (sx - bw // 2, sy - 44,
                          int(bw * heli.hp / heli.max_hp), 6))
        t = small.render("HELI", True, (255, 220, 80))
        screen.blit(t, (sx - t.get_width() // 2, sy - 62))

    # лазер-метки
    for L in state.lasers:
        sx, sy = int(L.x - cam_x), int(L.y - cam_y)
        t = 1 - L.t / L.max_t
        pygame.draw.circle(screen, (255, 0, 0), (sx, sy), int(L.radius * t), 4)
        pygame.draw.circle(screen, (255, 100, 100), (sx, sy), int(L.radius * t * 0.5), 3)
        if L.t < 0.3:
            pygame.draw.circle(screen, (255, 255, 200), (sx, sy), L.radius, 3)

    # игрок поверх всего
    if not state.player.in_car:
        sx, sy = int(state.player.x - cam_x), int(state.player.y - cam_y)
        draw_player_sprite(screen, state, sx, sy)
