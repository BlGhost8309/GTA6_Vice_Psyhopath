from entities.player      import Player
from entities.vehicles    import Car
from entities.npcs        import Ped
import world as world_module


class GameState:
    """Единственный источник мутабельного состояния игры."""

    def __init__(self, world, assets):
        self.world  = world
        self.assets = assets
        self.running = True
        self.reset()

    def reset(self):
        w = self.world
        x, y = w.rand_free_pos(20)

        self.player = Player(x, y)

        # списки сущностей
        self.cars       = []
        self.peds       = []
        self.cops       = []
        self.cop_cars   = []
        self.bullets    = []
        self.blood      = []
        self.explosions = []
        self.floaters   = []
        self.rain       = []
        self.lasers     = []
        self.gangsters  = []

        # одиночки
        self.boss = None
        self.tank = None
        self.heli = None
        self.pimp = None

        # звёзды
        self.wanted       = 0.0
        self.wanted_cool  = 0.0
        self.stars_total  = 0

        # таймеры / мир
        self.time_of_day       = 0.35
        self.weather           = "clear"
        self.weather_t         = 30.0
        self.time_scale        = 1.0
        self.slowmo_t          = 0.0
        self.weather_disabled  = False
        self.time_disabled     = False

        # камера
        self.cam_x       = 0
        self.cam_y       = 0
        self.zoom_level  = 0.0
        self.zoom_target = 0.0
        self.shake       = 0.0

        # флаги
        self.game_over      = False
        self.inside         = None
        self.banner         = ""
        self.banner_t       = 0
        self.god_mode       = False
        self.show_help      = False
        self.confirm_exit   = False

        # буферы
        self.cheat_buffer       = ""
        self.cheat_timer        = 0.0
        self.j_count            = 0
        self.j_timer            = 0.0
        self.pimp_spawn_timer   = 0.0
        self.last_cheater_girl  = None
        self.cop_car_cd         = 3.0
        self.laser_cd           = 20.0
        self.radio              = 1
        self.radio_t            = 0.0
        self.flash              = 0.0

        # спавн стартовых сущностей
        from systems.spawning import seed_world
        seed_world(self)
