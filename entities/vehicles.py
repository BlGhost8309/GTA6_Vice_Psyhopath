import random


class Car:
    def __init__(self, x, y, angle=0, ai=False, color=None,
                 alarm=False, img=None):
        self.x, self.y = x, y
        self.angle = angle
        self.speed = 0.0
        self.radius = 22
        self.driver = None
        self.ai = ai
        self.ai_dir = 1
        self.target_axis = None
        self.hp = 100
        self.color = color or (random.randint(90, 220),
                               random.randint(60, 180),
                               random.randint(60, 200))
        self.alarm = alarm
        self.alarm_t = 0
        self.owner_angry = False
        self.img = img
        self.stuck_t = 0.0
        self.change_cd = 0.0


class CopCar:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.angle = 0
        self.speed = 0.0
        self.radius = 22
        self.hp = 80
        self.deploy_t = 1.5
        self.blink = 0.0
        self.deployed = 0
        self.max_deploy = 2
        self.stuck_t = 0.0
        self.change_cd = 0.0
        self.ai_dir = 1
        self.target_axis = None
