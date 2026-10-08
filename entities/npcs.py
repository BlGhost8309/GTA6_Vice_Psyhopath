import math
import random


class Ped:
    def __init__(self, x, y, kind="ped"):
        self.x, self.y = x, y
        self.angle = random.random() * math.tau
        self.speed = 65 if kind == "ped" else 40
        self.radius = 10
        self.timer = random.uniform(0.8, 3.0)
        self.kind = kind
        self.color = (255, 60, 160) if kind == "prostitute" else (235, 195, 160)
        self.witness_cd = 0
        self.headless = False
        self.anim_t = random.random() * 0.15
        self.anim_frame = random.randint(0, 3)


class Cop:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.angle = 0
        self.speed = 145
        self.radius = 12
        self.hp = 60
        self.shoot_cool = 0.6
        self.anim_t = random.random() * 0.15
        self.anim_frame = random.randint(0, 3)


class Gangster:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.angle = 0
        self.speed = 160
        self.radius = 12
        self.hp = 70
        self.shoot_cool = 0.7
        self.anim_t = random.random() * 0.15
        self.anim_frame = random.randint(0, 3)


class Pimp:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.angle = 0
        self.speed = 190
        self.radius = 15
        self.hp = 150
        self.max_hp = 150
        self.shoot_cool = 0.5
        self.insult_cool = 1.5
        self.anim_t = 0.0
        self.anim_frame = 0
