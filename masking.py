from pure.pure import *
from pure.pure import Vector as vec
from pure.pure import sharedresource as res
import numpy as np
import random
import math as meth

# init
game = Game()
game.set_window_clear_color(color.JetBlack.value)
game.create_surface_with_keeping_ratio(40)
res.font.set_font_renderer("./assets/dogica.ttf", 8, color.White.value, 0)

class LIGHT:
    def __init__(self, size, pixel_shader):
        self.size = size
        self.radius = size * 0.5
        self.render_surface = pygame.Surface((size, size))
        self.pixel_shader_surf = pixel_shader.copy()
        self.baked_pixel_shader_surf = pixel_shader.copy()
        self.render_surface.set_colorkey((0,0,0))

    def main(self, tiles, display, x, y):
        self.render_surface.fill((0,0,0))
        self.render_surface.blit(self.baked_pixel_shader_surf, (0, 0))
        display.blit(self.render_surface, (x - self.radius, y - self.radius), special_flags=BLEND_RGBA_ADD)

        return display

def global_light(size, intensity):
    dark = pygame.Surface(size).convert_alpha()
    dark.fill((255, 255, 255, intensity))
    return dark

def pixel_shader(size, color, intensity, point, angle=0, angle_width=360):
    final_array = np.full((size, size, 3), color, dtype=np.uint16)
    radius = size*0.5

    for x in range(len(final_array)):
        
        for y in range(len(final_array[x])):

            #radial -----
            distance = meth.sqrt((x - radius)**2 + (y - radius)**2)
    
            radial_falloff = (radius - distance) * (1 / radius)

            if radial_falloff <= 0:
                radial_falloff = 0
            #-----

            #angular -----
            if not point:
                angular_falloff = 1
                
            else:
                point_angle = (180 / meth.pi) * -meth.atan2((radius - x), (radius - y)) + 180
                diff_anlge = abs(((angle - point_angle) + 180) % 360 - 180)
                
                angular_falloff = ((angle_width / 2) - diff_anlge) * (1 / angle_width)

                if angular_falloff <= 0:
                    angular_falloff = 0
            #-----
    
            final_intensity = radial_falloff * angular_falloff * intensity
            final_array[x][y] = final_array[x][y] * final_intensity

    return pygame.surfarray.make_surface(final_array)

light0 = LIGHT(500, pixel_shader(500, (255, 100, 100), 1, 0))
light1 = LIGHT(500, pixel_shader(500, (255, 100, 100), 1, 0))
lights_display = pygame.Surface((res.window.get_surface().get_size()))

shadow_objects = []

input_system = Input()
input_system.set_key("left", K_a)
input_system.set_key("right", K_d)
input_system.set_key("up", K_w)
input_system.set_key("down", K_s)
input_system.set_key("jump", K_SPACE)

pos = Vector(0, 0)

light = Light2D(500, (255, 100, 100), 0.5)

def main_loop(dt):
    if input_system.is_key_pressed("left"): pos.x -= 10
    if input_system.is_key_pressed("right"): pos.x += 10
    if input_system.is_key_pressed("up"): pos.y += 10
    if input_system.is_key_pressed("down"): pos.y -= 10

    light.render(10, 10, 40)

    # lights_display.fill((0, 0, 0))
    # lights_display.blit(global_light((200, 200), 10), (0,0))
    # light0.main(shadow_objects, lights_display, 10, 10)
    # light0.main(shadow_objects, lights_display, 300, 200)

    # res.window.get_surface().blit(lights_display, (0,0), special_flags=BLEND_RGBA_MULT)

    res.font.draw(vec(0, 0), f"FPS:{int(clock.get_fps())}")

game.set_main_game_function(main_loop)
game.run()
