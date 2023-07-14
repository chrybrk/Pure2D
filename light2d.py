from pure.pure import *
from pure.pure import Vector as vec
from pure.pure import sharedresource as res

import math, random

# init
game = Game()
game.set_window_clear_color(color.JetBlack.value)
game.create_surface_with_keeping_ratio(40)
res.font.set_font_renderer("./assets/dogica.ttf", 8, color.White.value, 0)

light=pygame.image.load('circle.png')

def main_loop(dt):
    global light
    light = pygame.transform.scale(light, (200, 200))
    filter = pygame.surface.Surface(res.window.get_surface().get_size())
    filter.fill(pygame.color.Color('Grey'))
    filter.blit(light, (100, 100))
    res.window.get_surface().blit(filter, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

    res.font.draw(vec(0, 0), f"FPS:{int(clock.get_fps())}")

game.set_main_game_function(main_loop)
game.run()
