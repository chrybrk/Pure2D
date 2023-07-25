from scripts.core import *
from scripts.config import ConfigurationManager
from scripts.assets import Assets, Animation
from scripts.entities import Entity, Player, Enemy
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.font import Font
from scripts.particle import Particle
from scripts.spark import Spark

# NOTE: timestamp @ 4:14:22
# TODO: Enemy [done]
# TODO: Sparks [done]
# TODO: Level Transition
# TODO: Silhouette

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

        self.assets = Assets()
        self.tilemap = Tilemap(self, tile_size = 16)
        self.font = Font()
        self.font.set_font_renderer("./assets/font/dogica.ttf", 8, (255, 255, 255), 0)

        self.game_data()

    def game_data(self):
        self.assets.load_images("grass", "./assets/new_assets/grass", (0, 0, 0))
        self.assets.load_images("stone", "./assets/images/tiles/stone", (0, 0, 0))
        self.assets.load_images("decor", "./assets/images/tiles/decor", (0, 0, 0))
        self.assets.load_images("large_decor", "./assets/images/tiles/large_decor", (0, 0, 0))
        self.assets.load_images("spwaners", "./assets/images/tiles/spawners", (0, 0, 0))
        self.assets.load_images("clouds", "./assets/images/clouds", (0, 0, 0))
        self.assets.load_image("player", "./assets/images/entities/player.png")
        self.assets.create_animation("enemy/idle", "./assets/images/entities/enemy/idle", image_duration = 6, color_key = (0, 0, 0))
        self.assets.create_animation("enemy/run", "./assets/images/entities/enemy/run", image_duration = 6, color_key = (0, 0, 0))
        self.assets.create_animation("player/idle", "./assets/new_assets/entities/player/idle", image_duration = 12, color_key = (0, 0, 0))
        self.assets.create_animation("player/run", "./assets/new_assets/entities/player/run", image_duration = 8, color_key = (0, 0, 0))
        self.assets.create_animation("player/jump", "./assets/new_assets/entities/player/jump", image_duration = 4, color_key = (0, 0, 0))
        self.assets.create_animation("player/wall_slide", "./assets/new_assets/entities/player/wall_slide", image_duration = 4, color_key = (0, 0, 0))
        self.assets.create_animation("particle/leaf", "./assets/images/particles/leaf", image_duration = 20, color_key = (0, 0, 0), loop = false)
        self.assets.create_animation("particle/particle", "./assets/images/particles/particle", image_duration = 12, color_key = (0, 0, 0), loop = false)
        self.assets.load_image("gun", "./assets/images/gun.png", color_key = (0, 0, 0))
        self.assets.load_image("projectile", "./assets/images/projectile.png", color_key = (0, 0, 0))

        self.clouds = Clouds(self.assets.get("clouds"))

        self.player = Player(self, (100, 10), (4, 14))
        self.movement = [false, false]

        self.screenshake = 0
        self.screenshake_amount = 50

        self.level = 0
        self.load_level(self.level)

    def load_level(self, map_id):
        self.tilemap.load('./assets/maps/' + str(map_id) + '.json')

        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep = true):
            # dim for tree, FIXME
            self.leaf_spawners.append(pygame.Rect(4 + tree['position'][0], 4 + tree['position'][1], 23, 13))

        self.enemies = []
        for spawner in self.tilemap.extract([('spwaners', 0), ('spwaners', 1)]):
            if spawner['variant'] == 0:
                self.player.position = spawner['position']
                self.player.air_time = 0
            else:
                self.enemies.append(Enemy(self, spawner['position'], (8, 15)))

        self.particles = []
        self.projectiles = []
        self.sparks = []

        self.scroll = [0, 0]
        self.dead = 0
        self.transition = -30

    def update(self, dt):
        self.font.draw(self.surface, (0, 0), f"FPS: { int(clock.get_fps()) }")

        self.screenshake = max(0, self.screenshake - 1)

        if not len(self.enemies):
            self.transition += 1
            if self.transition > 30:
                self.level = min(self.level + 1, len(os.listdir("./assets/maps")) - 1)
                self.load_level(self.level)
        if self.transition < 0:
            self.transition += 1

        if self.dead:
            self.dead += 1
            if self.dead >= 10:
                self.transition = min(30, self.transition + 1)
            if self.dead > 40:
                self.load_level(self.level)

        self.scroll[0] += (self.player.rect().centerx - self.surface.get_width() / 2 - self.scroll[0]) / 30
        self.scroll[1] += (self.player.rect().centery - self.surface.get_height() / 2 - self.scroll[1]) / 30
        render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
        
        for rect in self.leaf_spawners:
            if random.random() * 49999 < rect.width * rect.height:
                position = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                self.particles.append(Particle(self, 'leaf', position, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))

        self.clouds.update()
        self.clouds.render(self.surface, render_scroll)

        self.tilemap.render(self.surface, offset = render_scroll)

        for enemy in self.enemies.copy():
            kill = enemy.update(self.tilemap, (0, 0))
            enemy.render(self.surface, render_scroll)
            if kill:
                self.enemies.remove(enemy)


        if not self.dead:
            self.player.update(self.tilemap, ((self.movement[1] - self.movement[0]), 0))
            self.player.render(self.surface, offset = render_scroll)

        for projectile in self.projectiles.copy():
            projectile[0][0] += projectile[1]
            projectile[2] += 1
            image = self.assets.get("projectile")
            self.surface.blit(image, (projectile[0][0] - image.get_width() / 2 - render_scroll[0], projectile[0][1] - image.get_height() / 2 - render_scroll[1]))
            if self.tilemap.solid_check(projectile[0]):
                self.projectiles.remove(projectile)
                for i in range(4): self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))
            elif projectile[2] > 360:
                self.projectiles.remove(projectile)
            elif abs(self.player.dashing) < 50:
                if self.player.rect().collidepoint(projectile[0]):
                    self.projectiles.remove(projectile)
                    self.dead += 1
                    self.screenshake = max(self.screenshake_amount, self.screenshake)
                    for i in range(30):
                        angle = random.random() * math.pi * 2
                        speed = random.random() * 5
                        self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                        self.particles.append(Particle(self, 'particle', self.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame = random.randint(0, 7)))

        for spark in self.sparks.copy():
            kill = spark.update()
            spark.render(self.surface, offset = render_scroll)
            if kill:
                self.sparks.remove(spark)

        for particle in self.particles.copy():
            kill = particle.update()
            particle.render(self.surface, render_scroll)
            if particle.type == 'leaf':
                particle.position[0] += math.sin(particle.animation.frame * 0.035) * 0.3
            if kill:
                self.particles.remove(self.particles[0])

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
                    if event.key == pygame.K_SPACE: self.player.jump()
                    if event.key == pygame.K_LSHIFT: self.player.dash()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a: self.movement[0] = false
                    if event.key == pygame.K_d: self.movement[1] = false

            self.update(self.dt)

            if self.transition:
                transition_surface = pygame.Surface(self.surface.get_size())
                pygame.draw.circle(transition_surface, (255, 255, 255), (self.surface.get_width() // 2, self.surface.get_height() // 2), (30 - abs(self.transition)) * 8)
                transition_surface.set_colorkey((255, 255, 255))
                self.surface.blit(transition_surface, (0, 0))

            screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)
            self.window.blit(pygame.transform.scale(self.surface, (self.width, self.height)), screenshake_offset)

            pygame.display.update()
            fpsLock(self.fps)

        pygame.quit()
        sys.exit()

Game().run()
