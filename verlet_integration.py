# TODO: Constrains
# TODO: Forms
# TODO: Rag doll

from pure.pure import *
from pure.pure import Vector as vec
from pure.pure import sharedresource as res

import math, random

# init
game = Game()
game.set_window_clear_color(color.JetBlack.value)
game.create_surface_with_keeping_ratio(40)
res.font.set_font_renderer("./assets/dogica.ttf", 8, color.White.value, 0)

class Point:
    def __init__(self, position, old_position):
        self.position = position
        self.old_position = old_position

class Stick:
    def __init__(self, p0, p1):
        self.p0 = p0
        self.p1 = p1

        dx = p1.position.x - p0.position.x
        dy = p1.position.y - p0.position.y
        self.distance = math.sqrt(dx * dx + dy * dy)

points = []
sticks = []
bounce = 0.5
gravity = 0.1
friction = 0.995

# points
x_diff = [i for i in range(-5, 5)]
y_diff = [i for i in range(-10, 10)]
for i in range(0, random.choice([i for i in range(100, res.window.get_surface().get_size()[0] - 100, 100)]), 1):
    points.append(Point(vec(i, 100), vec(i + random.choice(x_diff), 100 + random.choice(y_diff))))

# sticks
for i in range(len(points) - 1): sticks.append(Stick(points[i], points[i + 1]))

def update_points(points):
    for i in range(len(points)):
        p = points[i]
        vx = (p.position.x - p.old_position.x) * friction
        vy = (p.position.y - p.old_position.y) * friction
        p.old_position.x = p.position.x
        p.old_position.y = p.position.y
        p.position.x += vx
        p.position.y += vy
        p.position.y += gravity

        if (p.position.x > res.window.get_surface().get_size()[0]):
            p.position.x = res.window.get_surface().get_size()[0]
            p.old_position.x = p.position.x + vx * bounce
        elif (p.position.x < 0):
            p.position.x = 0
            p.old_position.x = p.position.x + vx * bounce

        if (p.position.y > res.window.get_surface().get_size()[1] - 5):
            p.position.y = res.window.get_surface().get_size()[1] - 5
            p.old_position.y = p.position.y + vy * bounce
        elif (p.position.y < 0):
            p.position.y = 0
            p.old_position.y = p.position.y + vy * bounce

def update_sticks(sticks):
    for i in range(len(sticks)):
        s = sticks[i]
        dx = s.p1.position.x - s.p0.position.x
        dy = s.p1.position.y - s.p0.position.y
        distance = math.sqrt(dx * dx + dy * dy)
        difference = s.distance - distance
        percent = difference / distance / 2
        offsetX = dx * percent
        offsetY = dy * percent

        s.p0.position.x -= offsetX
        s.p0.position.y -= offsetY
        s.p1.position.x += offsetX
        s.p1.position.y += offsetY

def render_points(points):
    for i in range(len(points)):
        p = points[i]
        pygame.draw.circle(res.window.get_surface(), color.White.value, (p.position.x, p.position.y), 0, 0)

def render_sticks(sticks):
    for i in range(len(sticks)):
        s = sticks[i]
        pygame.draw.line(res.window.get_surface(), color.White.value, (s.p0.position.x, s.p0.position.y), (s.p1.position.x, s.p1.position.y), 1)

def main_loop(dt):
    update_points(points)
    update_sticks(sticks)
    render_points(points)
    render_sticks(sticks)
    res.font.draw(vec(0, 0), f"FPS:{int(clock.get_fps())}")

game.set_main_game_function(main_loop)
game.run()
