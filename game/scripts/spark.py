from scripts.core import *

class Spark:
    def __init__(self, position, angle, speed):
        self.position = list(position)
        self.angle = angle
        self.speed = speed

    def update(self):
        self.position[0] += math.cos(self.angle) * self.speed
        self.position[1] += math.sin(self.angle) * self.speed

        self.speed = max(0, self.speed - 0.1)

        return not self.speed

    def render(self, surface, offset = (0, 0)):
        render_points = [
            (self.position[0] + math.cos(self.angle) * self.speed * 3 - offset[0], self.position[1] + math.sin(self.angle) * self.speed * 3 - offset[1]),
            (self.position[0] + math.cos(self.angle + math.pi * 0.5) * self.speed * 0.5 - offset[0], self.position[1] + math.sin(self.angle + math.pi * 0.5) * self.speed * 0.5 - offset[1]),
            (self.position[0] + math.cos(self.angle + math.pi) * self.speed * 3 - offset[0], self.position[1] + math.sin(self.angle + math.pi) * self.speed * 3 - offset[1]),
            (self.position[0] + math.cos(self.angle - math.pi) * self.speed * 0.5 - offset[0], self.position[1] + math.sin(self.angle - math.pi) * self.speed * 0.5 - offset[1])
        ]
        pygame.draw.polygon(surface, (255, 255, 255), render_points)
