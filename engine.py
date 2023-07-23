#############################################################
#                           Imports                         #
#############################################################
import pygame, sys, math, random, time
import numpy as np
from pygame.locals import *
from enum import Enum
from PIL import Image

#############################################
#       TODO        FIXME       NOTE        #
#############################################

# TODO: [x] - Game
# TODO: [x] - Display
# TODO: [x] - Scene
# TODO: [x] - Input
# TODO: [x] - Font
# TODO: [x] - Config Manager
# TODO: [x] - Texture
# TODO: [x] - Sprite - textured | rect
# TODO: [x] - Light2D
# TODO: [x] - Tile Reader
# TODO: [x] - Camera - Target Centered, Fixed, Box Centered
# TODO: [x] - Collision
# TODO: [ ] - Animation
# TODO: [ ] - Particle
# TODO: [ ] - Different Layer Of Map | Parallax

#############################################################
#                     Global Constants                      #
#############################################################

true = True; false = False; nil = None
clock = pygame.time.Clock()

#############################################################
#                       Global Classes                      #
#############################################################
class ResourceManager:
    def __init__(self):
        self.event = nil
        self.window = nil
        self.config = nil
        self.font = nil
        self.scene = nil
        self.input = nil
        self.camera = nil
        self.renderer = nil
        self.collision = nil

class SpriteType:
    COLLISION = 0
    LIGHT = 1
    DAMAGE = 2

class color(Enum):
    Black = (0, 0, 0)
    MidnightBlack = (40, 40, 43)
    Charcoal = (54, 69, 79)
    JetBlack = (52, 52, 52)
    DarkSlateGray = (47, 79, 79)
    SlateGray = (112, 128, 144)
    LightSlateGray = (119, 136, 153)
    White = (255, 255, 255)

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

#############################################################
#                       Global Funtions                     #
#############################################################
def fpsLock(fps): return clock.tick(fps)

def err(msg):
    print(msg)
    exit(1)

def sine_wave(time, period, amplitude, midpoint):
    return math.sin(time * 2 * math.pi / period) * amplitude + midpoint

def sine_between(time, period, minimum, maximum):
    mid = minimum / maximum
    amp = maximum - mid
    return sine_wave(time, period, amp, mid)

#############################################################
#                      Global Variables                     #
#############################################################
resource_manager = ResourceManager()

#############################################################
#                   Independent Classes                     #
#############################################################

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

    def global_light_display(global_light_color = (255, 255, 255), global_light_intensity = 0):
        light_display = pygame.Surface(resource_manager.window.get_surface().get_size())

        dark = pygame.Surface(resource_manager.window.get_surface().get_size()).convert_alpha()
        dark.fill((*global_light_color, global_light_intensity))

        light_display.blit(dark, (0, 0))

        return light_display

    def global_light(light_display, color = (255, 255, 255), intensity = 0):
        dark = pygame.Surface(resource_manager.window.get_surface().get_size()).convert_alpha()
        dark.fill((*color, intensity))
        light_display.blit(dark, (0, 0))

    def render(light_display): resource_manager.window.get_surface().blit(light_display, (0, 0), special_flags=BLEND_RGBA_MULT)

    def set_light_display(self, light_display): self.light_display = light_display

    def fill(self):
        self.light_display.fill((0, 0, 0))

        self.render_surface.fill((0, 0, 0))
        self.render_surface.blit(self.pixel_shader_surface, (0, 0))

    def locate_light(self, x, y): self.light_display.blit(self.render_surface, (x - self.radius, y - self.radius), special_flags=BLEND_RGBA_ADD)

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


class Animation:
    def __init__(self):
        ...

class Sprite:
    def __init__(self, position, size = nil, hit_box_size = nil, color = nil, sp_type = nil, texture = nil):
        self.position = position
        self.size = size
        self.hit_box_size = hit_box_size
        self.color = color
        self.texture_object = nil
        self.texture = nil
        self.fixed_function = nil

        self.collision_top = false
        self.collision_left = false
        self.collision_bottom = false
        self.collision_right = false

        if texture:
            if isinstance(texture, str):
                self.texture_object = Texture(texture)
                self.texture = self.texture_object.texture
            elif isinstance(texture, Texture):
                self.texture_object = texture
                self.texture = self.texture_object.texture
            else:
                self.texture_object = texture
                self.texture = self.texture_object

            self.size = Vector(*self.texture.get_size())
        elif not self.size: err("Sprite :: err => str, Texture required not `None`")

        if not hit_box_size: self.hit_box_size = self.size

        if sp_type: resource_manager.scene.update_sprite(self, sp_type)

    def get_rect(self): return pygame.Rect(self.position.x, self.position.y, self.size.x, self.size.y)

    def get_hit_box(self): return pygame.Rect(self.position.x, self.position.y, self.hit_box_size.x, self.hit_box_size.y)

    def move(self, movement):
        self.collision_top = false
        self.collision_left = false
        self.collision_bottom = false
        self.collision_right = false

        clm = min(self.hit_box_size.x, self.hit_box_size.y)

        self.position.x += movement.x
        a = self.get_hit_box()
        for tile in resource_manager.collision.get_collision(self):
            b = tile.get_hit_box()

            if movement.x < 0:
                a.left = b.right
                self.collision_left = true

            if movement.x > 0:
                a.right = b.left
                self.collision_right = true

            self.position.x = a.x

        self.position.y += movement.y
        hit = resource_manager.collision.get_collision(self)
        a = self.get_hit_box()
        for tile in hit:
            if movement.y > 0 and abs(tile.get_hit_box().top - a.bottom) < clm:
                a.bottom = tile.get_hit_box().top
                self.collision_bottom = true
            if movement.y < 0 and abs(tile.get_hit_box().bottom - a.top) < clm:
                a.top = tile.get_hit_box().bottom
                self.collision_top = true

            self.position.y = a.y

    def draw(self, offset = Vector(0, 0)):
        self.position += offset
        if self.texture:
            resource_manager.window.get_surface().blit(self.texture, self.position.value2())
        else:
            surf = pygame.Surface((self.size.x, self.size.y)).convert_alpha()
            surf.fill(self.color)
            resource_manager.window.get_surface().blit(surf, self.position.value2())
            # pygame.draw.rect(resource_manager.window.get_surface(), self.color, self.get_rect())

        pygame.draw.rect(resource_manager.window.get_surface(), color.Black.value, (*self.position.value2(), *self.hit_box_size.value2()))

class Texture:
    def __init__(self, texture_path: str = nil, scale: Vector = nil) -> nil:
        self.texture_path = texture_path
        self.texture = pygame.image.load(texture_path).convert_alpha() if self.texture_path else nil
        if scale: self.texture = pygame.transform.scale(self.texture, scale.value2())
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

class TileReader:
    def __init__(self, csv_path: str, tilesheet_path: str, sprite_type: dict, tile_size: Vector, scale: Vector = nil):
        self.csv_path = csv_path

        self.tilesheet_path = tilesheet_path
        self.scale = scale
        self.tile_size = tile_size if not self.scale else self.scale
        self.texture = Texture()
        self.texture.load_tilesheet(self.tilesheet_path)

        self.file = open(self.csv_path, "r")
        self.map = []
        for line in self.file.readlines():
            clms = []
            for element in line.split(","):
                clms.append(int(element))

            self.map.append(clms)

        self.unq = []
        self.sprites = []
        self.textures = {}
        for i in range(len(self.map)):
            for j in range(len(self.map[i])):
                if self.map[i][j] not in self.unq and self.map[i][j] != -1:

                    self.unq.append(self.map[i][j])

                    e = self.unq[::-1][0]
                    w = self.texture.image.size[0] // self.tile_size.x
                    h = self.texture.image.size[1] // self.tile_size.y
                    pos = Vector((e % w) * self.tile_size.x, (e // w) * tile_size.y)
                    self.textures[e] = self.texture.load_texture_from_tilesheet(pos, self.tile_size)
                    if self.scale: self.textures[e] = pygame.transform.scale(self.textures[e], self.scale.value2())

                if self.map[i][j] != -1:
                    self.sprites.append(Sprite(Vector(j * self.tile_size.x, i * self.tile_size.y), texture = self.textures[self.map[i][j]]))
                    self.sprites[len(self.sprites) - 1].hit_box_size = Vector(self.sprites[len(self.sprites) - 1].size.x + 20, self.sprites[len(self.sprites) - 1].size.y + 20)

    def update_offset(self, offset):
        for sprite in self.sprites: sprite.position += offset

    def draw(self, wdn = 0, offset = Vector(0, 0)):
        for i in range(len(self.sprites)):
            self.sprites[i].position += offset
            self.sprites[i].draw()

class Collision:
    def __init__(self):
        self.mask = {}

    def add_mask(self, target, *mask):
        self.mask[target] = mask
    
    def get_collision(self, target):
        if target not in self.mask.keys(): return []

        hit = []
        for item in self.mask[target]:
            if target.get_hit_box().colliderect(item.get_hit_box()): hit.append(item)

        return hit

#############################################################
#                    Game Specific Classes                  #
#############################################################

class ConfigurationManager:
    def __init__(self, path = nil):
        self.config_path = path if path else "./config.pconf"
        self.config_text = open(self.config_path, "r+")
        self.config = {}

    def change_path(self, new_path):
        self.config_path = new_path
        self.load_config()

    def load_config(self):
        context = nil
        for i in self.config_text.readlines():
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

    def dump_config(self, head, body, context): ...

    def get_config(self, head, body, dt): return dt(self.config[head][body])

class Camera:
    def __init__(self):
        self.type = nil
        self.box_size = nil
        self.target = nil
        self.speed = 0
        self.offset = Vector(0, 0)

    def init_target_centered(self, target):
        self.target = target
        self.type = 0 # target_centered

    def get_offset(self):
        match self.type:
            case 0: # target_centered
                x, y = resource_manager.window.get_surface().get_size()
                cx, cy = x / 2, y / 2
                self.offset = Vector(cx, cy) - self.target.position

        return self.offset

class Input:
    def __init__(self):
        self.input_keys = {}

    def set_key(self, name: str, key: int) -> nil: self.input_keys[name] = key
    def get_key(self, name: str) -> int: return self.input_keys[name]
    def get_keys(self) -> dict: return self.input_keys

    def is_any_key_down(self):
        for event in resource_manager.event:
            if event.type == pygame.KEYDOWN: return true
        
        return false

    def is_any_key_up(self):
        for event in resource_manager.event:
            if event.type == pygame.KEYUP: return true
        
        return false

    def is_key_pressed(self, name: str) -> bool:
        for event in resource_manager.event:
            if event.type == KEYDOWN and event.key == self.get_keys()[name]: return true

        return false

    def is_key_pressed_up(self, name: str) -> bool:
        for event in resource_manager.event:
            if event.type == KEYUP and event.key == self.get_keys()[name]: return true

        return false
    
    def is_key_held(self, name: str) -> bool: return pygame.key.get_pressed()[self.get_keys()[name]]

class Scene:
    def __init__(self):
        self.state = nil
        self.layers = {}

    def add_state(self, state, function):
        self.layers[state] = function

    def set_state(self, state): self.state = state

    def run(self): self.layers[self.state](fpsLock(resource_manager.window.fps) / 1000)

class Font:
    def __init__(self) -> nil:
        self.font = nil
        self.color = nil
        self.smooth = 1

    def set_font_renderer(self, font_family: str, font_size: int, color: tuple, smooth: int = 1) -> nil:
        self.font = pygame.font.Font(font_family, font_size)
        self.font_size = font_size
        self.color = color
        self.smooth = smooth

    def draw(self, position, text: str) -> nil:
        fdr = self.font.render(text, self.smooth, self.color)
        resource_manager.window.get_surface().blit(fdr, position.value2())
        del fdr

class Window:
    def __init__(self, title, width, height, fps):
        self.title = title
        self.width = width
        self.height = height
        self.fps = fps
        self.color = (255, 255, 255)
        self.alive = true
        self.window = pygame.display.set_mode((width, height))
        self.surface = nil
        pygame.display.set_caption(title)

    def clear(self):
        self.get_surface().fill(self.color)

    def update(self) -> nil:
        self.update_event()
        if self.surface: self.window.blit(pygame.transform.scale(self.surface, self.get_size().value2()), (0, 0))
        pygame.display.update()
        fpsLock(self.fps)

    def get_surface(self) -> object: return self.surface if self.surface else self.window

    def update_event(self) -> nil:
        for lookup in resource_manager.event:
            if lookup.type == 32779: # window resize event handler
                self.width = lookup.x
                self.height = lookup.y

    def get_size(self: object) -> Vector: return Vector(self.width, self.height)

    def is_alive(self) -> bool: return self.alive

class Renderer:
    def __init__(self):
        self.objects = []

    def add_drawable(self, *objects): self.objects += objects

    def render(self):
        count = 0
        for element in self.objects:
            x, y = resource_manager.window.get_surface().get_size()

            size_w, size_h = element.size.value2() if isinstance(element.size, Vector) else (element.size, element.size)
            if (element.position.x <= x and element.position.x + size_w >= 0) and (element.position.y <= y and element.position.y + size_h >= 0):
                element.draw()
                count += 1

        self.count = count

        self.objects = []

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()

        resource_manager.config = ConfigurationManager()
        resource_manager.config.load_config()

        title = resource_manager.config.get_config("DISPLAY", "title", str)
        width = resource_manager.config.get_config("DISPLAY", "width", int)
        height = resource_manager.config.get_config("DISPLAY", "height", int)
        fps = resource_manager.config.get_config("DISPLAY", "fps", int)

        resource_manager.window = Window(title, width, height, fps)
        resource_manager.font = Font()
        resource_manager.scene = Scene()
        resource_manager.input = Input()
        resource_manager.camera = Camera()
        resource_manager.renderer = Renderer()
        resource_manager.collision = Collision()

        self.function = nil
        self.last_time = time.time()

    def create_scale_surface(self, x: int) -> nil:
        resource_manager.window.surface = pygame.Surface((x * resource_manager.window.get_size().x / 100, x * resource_manager.window.get_size().y / 100))

    def set_window_clear_color(self, color): resource_manager.window.color = color

    def set_function(self, function): self.function = function

    def run(self) -> nil:
        while resource_manager.window.is_alive():
            dt = time.time() - self.last_time
            dt *= resource_manager.window.fps
            self.last_time = time.time()

            resource_manager.window.clear()

            shared_event = pygame.event.get()
            resource_manager.event = shared_event

            for event in shared_event:
                if event.type == pygame.QUIT: resource_manager.window.alive = false

            resource_manager.renderer.render()

            self.function(dt)
            resource_manager.window.update()
