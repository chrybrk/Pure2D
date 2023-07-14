import pygame, sys, math, random
import numpy as np
from pygame.locals import *
from enum import Enum
from PIL import Image

# TODO: Camera
# TODO: Light
# TODO: Verlet Integration

# constants
true = True; false = False; nil = None
clock = pygame.time.Clock()

# some specified funtions
def fpsLock(fps): return clock.tick(fps)

def clamp(x, mn, mx):
    if x < mn: return mn
    elif x > mx: return mx
    return x

# Shared Class
class SharedResource(object):
    def __init__(self) -> nil:
        self.window = nil
        self.config = nil
        self.event = nil
        self.renderer = nil
        self.font = nil
        self.scene = nil

sharedresource = SharedResource()

# Enum
class color(Enum):
    Black = (0, 0, 0)
    MidnightBlack = (40, 40, 43)
    Charcoal = (54, 69, 79)
    JetBlack = (52, 52, 52)
    DarkSlateGray = (47, 79, 79)
    SlateGray = (112, 128, 144)
    LightSlateGray = (119, 136, 153)
    White = (255, 255, 255)

# Physics
class Vector(object):
    def __init__(self, x: int = 0, y: int = 0, z: int = 0) -> nil:
        self.x: int = x
        self.y: int = y
        self.z: int = z

    def __add__(self, vec2: object) -> object:  return Vector(self.x + vec2.x, self.y + vec2.y, self.z + vec2.z)
    def __sub__(self, vec2: object) -> object:  return Vector(self.x - vec2.x, self.y - vec2.y, self.z - vec2.z)
    def __mul__(self, vec2: object) -> object:  return Vector(self.x * vec2.x, self.y * vec2.y, self.z * vec2.z)
    def dot(self, vec2: object) -> object:      return Vector(self.x * vec2.x, self.y * vec2.y, self.z * vec2.z)
    def cross(self, vec2: object) -> object:    return Vector((self.y * vec2.z + vec2.y * self.z), (self.x * vec2.z + vec2.x * self.z), (self.x * vec2.y + vec2.x * self.y))
    def scalar(self, value: int) -> object:     return Vector(self.x * value, self.y * value)
    def value2(self) -> tuple[int, int]:        return (self.x, self.y)
    def lerp(a, b, t) -> object:                return a.scalar(t) + b.scalar((1.0 - t))
    def magnitude(self) -> int:                 return math.sqrt(self.x * self.x + self.y * self.y)
    def normalize(self) -> object:
        m = self.magnitude()
        return Vector(self.x / m, self.y / m, self.z / m)

    def __repr__(self) -> str: return f"Vector({self.x}, {self.y}, {self.z})"

# Graphic - Specific
class Light2D:
    def __init__(self, size: int, color: tuple, intensity: int, point: int = 0, angle: float = 0, angle_width: float = 360):
        self.size = size
        self.color = color
        self.intensity = intensity
        self.point = point
        self.angle = angle
        self.angle_width = angle_width
        self.radius = size * 0.5
        self.render_surface = pygame.Surface((size, size))
        self.render_surface.set_colorkey((0, 0, 0))
        self.pixel_shader_surface = self.pixel_shader()
        self.display = pygame.Surface(sharedresource.window.get_surface().get_size())
        self.dark = pygame.Surface(sharedresource.window.get_surface().get_size()).convert_alpha()

    def render(self, x, y, global_light_color = (255, 255, 255), global_light_intensity = 0):
        self.display.fill((0, 0, 0))

        self.dark.fill((*global_light_color, global_light_intensity))
        self.display.blit(self.dark, (0, 0))

        self.render_surface.fill((0, 0, 0))
        self.render_surface.blit(self.pixel_shader_surface, (0, 0))

        self.display.blit(self.render_surface, (x - self.radius, y - self.radius), special_flags=BLEND_RGBA_ADD)
        sharedresource.window.get_surface().blit(self.display, (0, 0), special_flags=BLEND_RGBA_MULT)

    def pixel_shader(self):
        array = np.full((self.size, self.size, 3), self.color, dtype=np.uint16)

        for x in range(len(array)):
            for y in range(len(array[x])):
                distance = math.sqrt((x - self.radius) ** 2 + (y - self.radius) ** 2)
                radial_falloff = (self.radius - distance) * (1 / self.radius)

                if radial_falloff <= 0: radial_falloff = 0

                if not self.point: angular_falloff = 1
                else:
                    point_angle = (180 / math.pi) * -math.atan2((self.radius - x), (self.radius - y)) + 180
                    diff_anlge = abs(((self.angle - point_angle) + 180) % 360 - 180)

                    angular_falloff = ((self.angle_width / 2) - diff_anlge) * (1 / self.angle_width)

                    if angular_falloff <= 0: angular_falloff = 0

                intensity = radial_falloff * angular_falloff * self.intensity
                array[x][y] = array[x][y] * intensity

        return pygame.surfarray.make_surface(array)

    def create_pixel_shader(size, color, intensity, point, angle = 0, angle_width = 360):
        radius = size * 0.5
        array = np.full((size, size, 3), color, dtype=np.uint16)

        for x in range(len(array)):
            for y in range(len(array[x])):
                distance = math.sqrt((x - radius) ** 2 + (y - radius) ** 2)
                radial_falloff = (radius - distance) * (1 / radius)

                if radial_falloff <= 0: radial_falloff = 0

                if not point: angular_falloff = 1
                else:
                    point_angle = (180 / math.pi) * -math.atan2((radius - x), (radius - y)) + 180
                    diff_anlge = abs(((angle - point_angle) + 180) % 360 - 180)

                    angular_falloff = ((angle_width / 2) - diff_anlge) * (1 / angle_width)

                    if angular_falloff <= 0: angular_falloff = 0

                intensity = radial_falloff * angular_falloff * intensity
                array[x][y] = array[x][y] * intensity

        return pygame.surfarray.make_surface(array)


class Texture:
    def __init__(self, texture_path: str = nil) -> nil:
        self.texture_path = texture_path
        self.texture = pygame.image.load(texture_path).convert_alpha() if self.texture_path else nil
        self.flip_x = pygame.transform.flip(self.texture, true, false) if self.texture else nil
        self.flip_y = pygame.transform.flip(self.texture, false, true) if self.texture else nil
        self.tilesheet_path = nil
        self.image = nil
        self.tiles = []

    def load_tilesheet(self, tilesheet_path: str) -> nil:
        self.tilesheet_path = tilesheet_path
        self.image = Image.open(self.tilesheet_path).convert("RGBA")

    def load_texture_from_tilesheet(self, position: Vector, size: Vector) -> pygame.image:
        cprd = self.image.crop((position.x, position.y, position.x + size.x, position.y + size.y))
        self.texture = pygame.image.fromstring(cprd.tobytes(), cprd.size, cprd.mode)

        return self.texture

    def load_tile_from_tilesheet(self, tile_size: Vector) -> nil:
        for i in range(self.image.size[1] // tile_size.y):
            elements = []
            for j in range(self.image.size[0] // tile_size.x):
                cprd = self.image.crop((tile_size.y * j, tile_size.x * i, tile_size.y * (j + 1), tile_size.x * (i + 1)))
                tile = pygame.image.fromstring(cprd.tobytes(), cprd.size, cprd.mode)
                elements.append(tile)
            self.tiles.append(elements)

class TileEditor:
    def __init__(self, csv_path: str, tilesheet_path: str, tile_size: Vector):
        self.csv_path = csv_path

        self.tilesheet_path = tilesheet_path
        self.tile_size = tile_size
        self.texture = Texture()
        self.texture.load_tilesheet(self.tilesheet_path)

        self.file = open(self.csv_path, "r")
        self.unq = []
        self.map = []
        for line in self.file.readlines():
            clms = []
            for element in line.split(","):
                clms.append(int(element))

            self.map.append(clms)

        for i in range(len(self.map)):
            for j in range(len(self.map[i])):
                if self.map[i][j] not in self.unq: self.unq.append(self.map[i][j])

        self.unq.pop(self.unq.index(-1))

        self.textures = {}
        for e in self.unq:
            w = self.texture.image.size[0] // self.tile_size.x
            h = self.texture.image.size[1] // self.tile_size.y
            pos = Vector((e % w) * self.tile_size.x, (e // w) * tile_size.y)
            self.textures[e] = self.texture.load_texture_from_tilesheet(pos, self.tile_size)


        for i in range(len(self.map)):
            for j in range(len(self.map[i])):
                print("%4d" % (self.map[i][j]), end=" ")
            print()

        self.sprites = []
    def draw(self, wdn = 2):
        for i in range(len(self.map)):
            for j in range(len(self.map[i])):
                if self.map[i][j] != -1:
                    sharedresource.window.get_surface().blit(self.textures[self.map[i][j]], (j * (self.tile_size.x - wdn), i * (self.tile_size.y - wdn)))

class Collision:
    def __init__(self, mask) -> nil:
        self.top = false
        self.left = false
        self.bottom = false
        self.right = false
        self.collide = false

        self.mask = mask

    def check_collision(self, a, b, additive: Vector = nil):
        if additive: a.position += additive
        return b.position.x - a.size.x <= a.position.x <= b.position.x + b.size.x and b.position.y - a.size.y <= a.position.y <= b.position.y + b.size.y

    def check_collisions(self, a, *bs):
        for b in bs:
            if self.check_collision(a, b): return true
        return false

    def aabb(self, a):
        self.top = false
        self.left = false
        self.bottom = false
        self.right = false

        who_hit_target = []
        self.lock_distance = 50

        for b in self.mask:
            if self.check_collision(a, b): who_hit_target.append(b)

        self.collide = true if len(who_hit_target) > 0 else false

        for b in who_hit_target:
            top = abs((b.position.y + b.size.y) - a.position.y)
            left = abs(b.position.x - (a.position.x + a.size.x))
            bottom = abs(b.position.y - (a.position.y + a.size.y))
            right = abs((b.position.x + b.size.x) - a.position.x)

            self.top = true if top <= self.lock_distance else false
            self.left = true if left <= self.lock_distance else false
            self.bottom = true if bottom <= self.lock_distance else false
            self.right = true if right <= self.lock_distance else false

            if self.bottom: a.position.y = b.position.y - a.size.y

class Physics:
    def __init__(self) -> nil:

        # properties
        self.velocity = Vector(0, 0)

        self.bounce = 0.0
        self.gravity = 0.0
        self.gravity_back = 0.0
        self.friction = 0.0
        self.jump_height = 0
        self.max_jump = 0
        self.max_speed = 0
        self.mid_air = false

        # objects
        self.collision = Collision(nil)

        # flags
        self.g_flag = false
        self.c_flag = false
        self.r_flag = false

    def add_gravity(self, gravity: int) -> nil:
        self.g_flag = true
        self.gravity = gravity

    def add_friction(self, friction): self.friction = friction

    def add_collision(self, *mask: object) -> nil:
        self.c_flag = true
        self.collision = Collision(mask)

    def is_on_floor(self) -> int: return self.collision.bottom

    def apply(self, sprite) -> nil:
        # TODO: Celeste run movement
        if self.g_flag:
            dt = fpsLock(sharedresource.window.fps) / 1000
            sprite.position.y = sprite.position.y + dt * self.velocity.y
            self.velocity.y = self.velocity.y + dt * self.gravity

        if self.c_flag:
            self.collision.aabb(sprite)
            if self.collision.bottom: self.velocity = Vector(0, 0)

# Verlet Integration
class Point: pass
class Stick: pass
class Forms: pass

class Sprite:
    def __init__(self, position: Vector, size: Vector = nil, color: tuple = color.Black.value, tex: object = nil) -> nil:
        self.position = position
        self.color = color
        self.texture_object = Texture(tex) if isinstance(tex, str) else tex
        self.tex = self.texture_object.texture if isinstance(self.texture_object, Texture) else self.texture_object
        self.size = size if size else Vector(self.tex.get_size()[0], self.tex.get_size()[1])
        self.physics = nil
        self.animation = nil
        self.fixed_function = nil
        self.flipped = false

    def flip(self):
        if not self.flipped:
            self.flipped = true
            self.tex = self.texture_object.flip_x

    def unflip(self):
        if self.flipped:
            self.flipped = false
            self.tex = self.texture_object.texture

    def update_fix_function(self, function): self.fixed_function = function

    def init_physics(self) -> nil: self.physics = Physics()

    def sprite_filling(self, rows: int, cols: int):
        self.size = Vector(self.tex.get_size()[0] * cols, self.tex.get_size()[1] * rows)

    def draw(self):
        if self.physics: self.physics.apply(self)
        if self.fixed_function: self.fixed_function()

        px, py = int(self.position.x), int(self.position.y)
        px_w, py_h = px + self.size.x, py + self.size.y
        w, h = self.tex.get_size()
        wdn = 2
        for i in range(px, px_w - wdn, w - wdn):
            for j in range(py, py_h - wdn, h - wdn):
                sharedresource.window.get_surface().blit(self.tex, (i, j))

# Game - Specific
class Display:
    def __init__(self, width: int, height: int, title: str, color: Vector, fps: int) -> nil:
        self.width: int             = width
        self.height: int            = height
        self.title: str             = title
        self.color: Vector          = color
        self.fps: int               = fps
        self.alive: int             = true
        self.is_resized: int        = false
        self.window: pygame.display = pygame.display.set_mode((self.width, self.height))
        self.surface = nil
        pygame.display.set_caption(self.title)

    def clear(self) -> nil:
        if self.surface: self.surface.fill(self.color)
        else: self.window.fill(self.color)

    def update(self) -> nil:
        self.update_event()
        if self.surface: self.window.blit(pygame.transform.scale(self.surface, self.get_size().value2()), (0, 0))
        pygame.display.update()
        fpsLock(self.fps)

    def get_surface(self) -> object: return self.surface if self.surface else self.window

    def update_event(self) -> nil:
        for lookup in sharedresource.event:
            if lookup.type == 32779: # window resize event handler
                self.width = lookup.x
                self.height = lookup.y
                self.is_resized = true

    def get_size(self: object) -> Vector: return Vector(self.width, self.height)

    def is_alive(self) -> bool: return self.alive

class Input:
    def __init__(self):
        self.input_keys = {}

    def set_key(self, name: str, key: int) -> nil: self.input_keys[name] = key
    def get_key(self, name: str) -> int: return self.input_keys[name]
    def get_keys(self) -> dict: return self.input_keys

    def is_key_pressed(self, name: str) -> bool:
        for event in sharedresource.event:
            if event.type == KEYUP and event.key == self.get_keys()[name]: return true

        return false
    
    def is_key_held(self, name: str) -> bool: return pygame.key.get_pressed()[self.get_keys()[name]]

    def on_key_press_move(self, name: str, sprite: Sprite, position: Vector, speed: Vector) -> nil:
        if self.is_key_held(name):
            new_position = position * speed
            new_position = new_position.scalar(fpsLock(sharedresource.window.fps) / 1000)
            sprite.position += new_position

class LoadConfig:
    def __init__(self) -> nil:
        self.config_path = "./config.pconf"
        self.config_string = open(self.config_path, "r+")
        self.config = {}

        self.re_evaluate()

    def change_path(self, new_path: str) -> nil:
        self.config_path = new_path
        self.config_string = open(self.config_path, "r+")
        self.re_evaluate()

    def re_evaluate(self) -> nil:
        context = nil
        for i in self.config_string.readlines():
            if "[" in i:
                context = i[1:len(i) - 2]
                self.config[context] = {}
                continue
            
            if i not in ['\n', '\t', ' ']:
                endln = 0
                context_value = ""
                context_value_data = ""

                for j in range(len(i)):
                    if i[j] == ' ':
                        endln = j
                        break
                    context_value += i[j]

                for j in range(endln, len(i)):
                    if i[j] == '\n': continue
                    context_value_data += i[j]

                self.config[context][context_value] = context_value_data

class Font:
    def __init__(self) -> nil:
        self.font = nil
        self.color = nil
        self.smooth = 1

    def set_font_renderer(self, font_family: str, font_size: int, color: tuple, smooth: int = 1) -> nil:
        # self.font = pygame.font.SysFont(font_family, font_size) if ".tff" not in font_family else pygame.font.font(font_family, font_size)
        self.font = pygame.font.Font(font_family, font_size)
        self.font_size = font_size
        self.color = color
        self.smooth = smooth

    def draw(self, position, text: str) -> nil:
        fdr = self.font.render(text, self.smooth, self.color)
        sharedresource.window.get_surface().blit(fdr, position.value2())
        del fdr

class Scene:
    def __init__(self):
        self.state = nil
        self.layers = {}

    def add_state(self, state, function): self.layers[state] = function

    def set_state(self, state): self.state = state

    def run(self): self.layers[self.state](fpsLock(sharedresource.window.fps) / 1000)

class Renderer:
    def __init__(self):
        self.camera = nil
        self.objects = []

    def update_camera(self, camera): self.camera = camera

    def add_drawable(self, *objects): self.objects += objects

    def render(self):
        for element in self.objects:
            x, y = sharedresource.window.get_surface().get_size()

            if isinstance(element, TileEditor): element.draw()
            else:
                size_w, size_h = element.size.value2() if isinstance(element.size, Vector) else (element.size, element.size)
                if (element.position.x <= x and element.position.x + size_w >= 0) and (element.position.y <= y and element.position.y + size_h >= 0):
                    element.draw()

                # FIXME: performance draw
                elif isinstance(element, Sprite) and element.physics: element.physics.apply(element)

        self.objects = []

class Game:
    def __init__(self) -> nil:
        pygame.init()
        pygame.font.init()

        self.main_game_function = nil
        self.load_config = LoadConfig()
        sharedresource.window = Display(
                    int(self.load_config.config["DISPLAY"]["width"]),
                    int(self.load_config.config["DISPLAY"]["height"]),
                    self.load_config.config["DISPLAY"]["title"],
                    color.White.value,
                    int(self.load_config.config["DISPLAY"]["fps"])
                )

        sharedresource.renderer = Renderer()
        sharedresource.config = self.load_config
        sharedresource.font = Font()
        sharedresource.scene = Scene()

    def create_surface(self, size: Vector) -> nil: sharedresource.window.surface = pygame.Surface(size.value2())

    def create_surface_with_keeping_ratio(self, x: int) -> nil:
        if sharedresource.window.surface:
            print("You cannot re-define surface, with new size.")
            exit(1)
        else:
            sharedresource.window.surface = pygame.Surface((x * sharedresource.window.get_size().x / 100, x * sharedresource.window.get_size().y / 100))

    def set_window_clear_color(self, color): sharedresource.window.color = color

    def set_main_game_function(self, function): self.main_game_function = function

    def run(self) -> nil:
        while sharedresource.window.is_alive():
            sharedresource.window.clear()

            shared_event = pygame.event.get()
            sharedresource.event = shared_event

            for event in shared_event:
                if event.type == pygame.QUIT: sharedresource.window.alive = false

            sharedresource.renderer.render()

            self.main_game_function(fpsLock(sharedresource.window.fps) / 1000)
            sharedresource.window.update()
