class Bullet:
    def __init__(self, x, y, angle, owner, dmg=22):
        self.x, self.y = x, y
        self.angle = angle
        self.speed = 950
        self.owner = owner
        self.life = 1.2
        self.dmg = dmg


class Laser:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.t = 1.4
        self.max_t = 1.4
        self.radius = 90
        self.fired = False
