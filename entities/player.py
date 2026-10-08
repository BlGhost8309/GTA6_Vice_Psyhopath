import math


class Player:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.angle = 0
        self.speed = 235
        self.radius = 12
        self.hp = 100
        self.in_car = None
        self.shoot_cool = 0
        self.money = 500
        self.msg, self.msg_t = "", 0
        self.weapons = ["pistol"]
        self.weapon = "pistol"
        self.energy = 100.0
        self.anim_t = 0.0
        self.anim_frame = 0
        self.facing_row = 0
        self.moving = False
        self.girl_cd = 0.0

    def say(self, text):
        self.msg, self.msg_t = text, 2.2
