class Boss:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.angle = 0
        self.speed = 340
        self.radius = 26
        self.hp = 500
        self.max_hp = 500
        self.shoot_cool = 0.35
        self.life_timer = 0
        self.anim_t = 0.0
        self.anim_frame = 0
        self.on_foot = False


class TankBoss:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.angle = 0
        self.speed = 130
        self.radius = 40
        self.hp = 900
        self.max_hp = 900
        self.shoot_cool = 1.2


class Heli:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.angle = 0
        self.speed = 260
        self.radius = 34
        self.hp = 350
        self.max_hp = 350
        self.shoot_cool = 0.5
        self.bob = 0.0
