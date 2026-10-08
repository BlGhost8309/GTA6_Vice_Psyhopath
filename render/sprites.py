import math
import pygame
from assets import get_scaled, scale_to_width
from utils import get_facing_row


def draw_npc_sprite(screen, frames, sx, sy, angle, anim_frame, size):
    if not frames:
        return False
    row = get_facing_row(angle)
    frame = frames[row][anim_frame % 4]
    scaled = get_scaled(frame, size)
    screen.blit(scaled, scaled.get_rect(center=(sx, sy)))
    return True


def draw_rotated_image(screen, img, sx, sy, angle, target_w=None):
    if not img:
        return False
    s = scale_to_width(img, target_w) if target_w else img
    rot = pygame.transform.rotate(s, -math.degrees(angle))
    screen.blit(rot, rot.get_rect(center=(sx, sy)))
    return True


def draw_player_sprite(screen, state, sx, sy):
    player = state.player
    frames = state.assets.player
    if frames:
        frame = frames[player.facing_row][player.anim_frame]
        size = player.radius * 3
        scaled = pygame.transform.scale(frame, (size, size))
        screen.blit(scaled, scaled.get_rect(center=(sx, sy)))
    else:
        pygame.draw.circle(screen, (90, 200, 255), (sx, sy), player.radius)
        pygame.draw.circle(screen, (20, 60, 90), (sx, sy), player.radius, 2)
        ex = sx + math.cos(player.angle) * player.radius
        ey = sy + math.sin(player.angle) * player.radius
        pygame.draw.line(screen, (255, 255, 255), (sx, sy), (ex, ey), 2)
