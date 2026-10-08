import pygame

pygame.init()
W, H = 1280, 720
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Clone City: Vice Edition — Psychopath Cut v11")
clock = pygame.time.Clock()

font       = pygame.font.SysFont("consolas", 18, bold=True)
small      = pygame.font.SysFont("consolas", 14, bold=True)
tiny       = pygame.font.SysFont("consolas", 12, bold=True)
big_font   = pygame.font.SysFont("consolas", 54, bold=True)
huge_font  = pygame.font.SysFont("consolas", 32, bold=True)
help_font  = pygame.font.SysFont("consolas", 15, bold=True)
help_title = pygame.font.SysFont("consolas", 30, bold=True)
