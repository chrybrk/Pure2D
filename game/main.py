from scripts.core import *
from scripts.config import ConfigurationManager
from scripts.assets import Assets, Animation
from scripts.entities import Entity, Player
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.font import Font

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()

        self.configuration_manager = ConfigurationManager()
        self.configuration_manager.load_config()

        self.width = self.configuration_manager.get_config("DISPLAY", "width", int)
        self.height = self.configuration_manager.get_config("DISPLAY", "height", int)
        self.title = self.configuration_manager.get_config("DISPLAY", "title", str)
        self.fps = self.configuration_manager.get_config("DISPLAY", "fps", int)
        self.scale = self.configuration_manager.get_config("DISPLAY", "scale", int)

        self.window = pygame.display.set_mode((self.width, self.height))
        self.surface = pygame.Surface((self.scale * self.window.get_size()[0] / 100, self.scale * self.window.get_size()[1] / 100))
        pygame.display.set_caption(self.title)

        self.alive = true

        self.dt = 0
        self.last_time = time.time()

        self.clear_color = (25, 25, 25)

        self.scroll = [0, 0]

        self.assets = Assets()
        self.tilemap = Tilemap(self, tile_size = 32); self.tilemap.load('./map.json')
        self.font = Font()
        self.font.set_font_renderer("./assets/font/dogica.ttf", 8, (255, 255, 255), 0)

        self.game_data()

    def game_data(self):
        # self.assets.load_images("grass", "./assets/images/tiles/grass")
        # self.assets.load_images("stone", "./assets/images/tiles/stone")
        self.assets.load_images("clouds", "./assets/images/clouds", (0, 0, 0))
        self.assets.load_images("floor", "./assets/new_assets/floor", (0, 0, 0))
        self.assets.load_image("player", "./assets/images/entities/player.png")
        self.assets.create_animation("player/idle", "./assets/images/entities/player/idle", image_duration = 6, color_key = (0, 0, 0))
        self.assets.create_animation("player/run", "./assets/images/entities/player/run", image_duration = 8, color_key = (0, 0, 0))
        self.assets.create_animation("player/jump", "./assets/images/entities/player/jump", image_duration = 4, color_key = (0, 0, 0))

        self.clouds = Clouds(self.assets.get("clouds"))

        self.player = Player(self, (100, 10), (10, 16))
        self.movement = [false, false]

    def update(self, dt):
        self.font.draw(self.surface, (0, 0), f"FPS: { int(clock.get_fps()) }")

        self.scroll[0] += (self.player.rect().centerx - self.surface.get_width() / 2 - self.scroll[0]) / 30
        self.scroll[1] += (self.player.rect().centery - self.surface.get_height() / 2 - self.scroll[1]) / 30
        render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

        self.clouds.update()
        self.clouds.render(self.surface, render_scroll)

        self.tilemap.render(self.surface, offset = render_scroll)

        self.player.update(self.tilemap, ((self.movement[1] - self.movement[0]), 0))
        self.player.render(self.surface, offset = render_scroll)

    def run(self):
        while self.alive:
            self.dt = time.time() - self.last_time
            self.dt *= self.fps
            self.last_time = time.time()

            self.surface.fill(self.clear_color)

            for event in pygame.event.get():
                # exit event
                if event.type == pygame.QUIT: self.alive = false
                
                # window resize event
                if event.type == 32779:
                    self.width = event.x
                    self.height = event.y

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a: self.movement[0] = true
                    if event.key == pygame.K_d: self.movement[1] = true
                    if event.key == pygame.K_SPACE: self.player.velocity[1] = -3

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a: self.movement[0] = false
                    if event.key == pygame.K_d: self.movement[1] = false

            self.update(self.dt)

            self.window.blit(pygame.transform.scale(self.surface, (self.width, self.height)), (0, 0))

            pygame.display.update()
            fpsLock(self.fps)

        pygame.quit()
        sys.exit()

Game().run()
