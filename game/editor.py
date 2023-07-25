from scripts.core import *
from scripts.config import ConfigurationManager
from scripts.assets import Assets, Animation
from scripts.tilemap import Tilemap
from scripts.font import Font

RENDER_SCALE = 2.5

class Editor:
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
        self.tilemap = Tilemap(self)
        self.tilemap.load('./map.json')

        self.font = Font()
        self.font.set_font_renderer("./assets/font/dogica.ttf", 8, (255, 255, 255), 0)

        self.game_data()

    def game_data(self):
        self.assets.load_images("grass", "./assets/new_assets/grass", (0, 0, 0))
        self.assets.load_images("stone", "./assets/images/tiles/stone", (0, 0, 0))
        self.assets.load_images("decor", "./assets/images/tiles/decor", (0, 0, 0))
        self.assets.load_images("large_decor", "./assets/images/tiles/large_decor", (0, 0, 0))
        self.assets.load_images("spwaners", "./assets/images/tiles/spawners", (0, 0, 0))

        self.movement = [false, false, false, false]

        self.tile_list = list(self.assets.assets)
        self.tile_group = 0
        self.tile_variant = 0

        self.clicking = false
        self.right_clicking = false
        self.shift = false
        self.ongrid = true

    def update(self, dt):
        self.font.draw(self.surface, (0, 0), f"FPS: { int(clock.get_fps()) }")

        self.tile_asset = self.assets.get(self.tile_list[self.tile_group])
        current_tile_image = self.tile_asset[self.tile_variant].copy()
        current_tile_image.set_alpha(100)

        self.surface.blit(current_tile_image, (self.surface.get_width() - current_tile_image.get_width() - 5, self.surface.get_height() - current_tile_image.get_height() - 5))

        self.scroll[0] += (self.movement[1] - self.movement[0]) * 2 * self.dt
        self.scroll[1] += (self.movement[3] - self.movement[2]) * 2 * self.dt
        render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

        self.tilemap.render(self.surface, render_scroll)

        self.mouse_position = pygame.mouse.get_pos()
        self.mouse_position = (self.mouse_position[0] / RENDER_SCALE, self.mouse_position[1] / RENDER_SCALE)
        tile_position = (int((self.mouse_position[0] + self.scroll[0]) // self.tilemap.tile_size), int((self.mouse_position[1] + self.scroll[1]) // self.tilemap.tile_size))
        self.font.draw(self.surface, (0, 10), f"X: {tile_position[0]}, Y: {tile_position[1]}")

        if self.ongrid:
            self.surface.blit(current_tile_image, (tile_position[0] * self.tilemap.tile_size - self.scroll[0], tile_position[1] * self.tilemap.tile_size - self.scroll[1]))
        else:
            self.surface.blit(current_tile_image, self.mouse_position)

        if self.clicking and self.ongrid:
            self.tilemap.tilemap[str(tile_position[0]) + ';' + str(tile_position[1])] = { 'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'position': tile_position }
        if self.right_clicking:
            tile_loc = str(tile_position[0]) + ';' + str(tile_position[1])
            if tile_loc in self.tilemap.tilemap:
                del self.tilemap.tilemap[tile_loc]

            for tile in self.tilemap.offgrid_tiles.copy():
                tile_image = self.assets.get(tile['type'])[tile['variant']]
                tr = pygame.Rect(tile['position'][0] - self.scroll[0], tile['position'][1] - self.scroll[1], tile_image.get_width(), tile_image.get_height())
                if tr.collidepoint(self.mouse_position):
                    self.tilemap.offgrid_tiles.remove(tile)

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

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = true
                        if not self.ongrid:
                            self.tilemap.offgrid_tiles.append({'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'position': (self.mouse_position[0] + self.scroll[0], self.mouse_position[1] + self.scroll[1])})
                    if event.button == 3:
                        self.right_clicking = true
                    if self.shift:
                        if event.button == 4:
                            self.tile_variant = (self.tile_variant - 1) % len(self.tile_asset)
                        if event.button == 5:
                            self.tile_variant = (self.tile_variant + 1) % len(self.tile_asset)
                    else:
                        if event.button == 4:
                            self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                            self.tile_variant = 0
                        if event.button == 5:
                            self.tile_group = (self.tile_group + 1) % len(self.tile_list)
                            self.tile_variant = 0

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = false
                    if event.button == 3:
                        self.right_clicking = false

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a: self.movement[0] = true
                    if event.key == pygame.K_d: self.movement[1] = true
                    if event.key == pygame.K_w: self.movement[2] = true
                    if event.key == pygame.K_s: self.movement[3] = true
                    if event.key == pygame.K_LSHIFT: self.shift = true
                    if event.key == pygame.K_g: self.ongrid = not self.ongrid
                    if event.key == pygame.K_o: self.tilemap.save('map.json')

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a: self.movement[0] = false
                    if event.key == pygame.K_d: self.movement[1] = false
                    if event.key == pygame.K_w: self.movement[2] = false
                    if event.key == pygame.K_s: self.movement[3] = false
                    if event.key == pygame.K_LSHIFT: self.shift = false

            self.update(self.dt)

            self.window.blit(pygame.transform.scale(self.surface, (self.width, self.height)), (0, 0))

            pygame.display.update()
            fpsLock(self.fps)

        pygame.quit()
        opt = input("do you wanna save the file? ")
        if opt == 'y': self.tilemap.save('map.json')
        sys.exit()

Editor().run()
