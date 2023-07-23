from scripts.core import *

class Cloud:
    def __init__(self, position, image, speed, depth):
        self.position = list(position)
        self.image = image
        self.speed = speed
        self.depth = depth

    def update(self):
        self.position[0] += self.speed
        self.position[1] += self.speed

    def render(self, surface, offset=(0, 0)):
        render_position = (self.position[0] - offset[0] * self.depth, self.position[1] - offset[1] * self.depth)
        surface.blit(self.image, (render_position[0] % (surface.get_width() + self.image.get_width()) - self.image.get_width(), render_position[1] % (surface.get_height() + self.image.get_height()) - self.image.get_height()))

class Clouds:
    def __init__(self, cloud_images, count = 16):
        self.clouds = []

        for i in range(count):
            self.clouds.append(Cloud((random.random() * 99999, random.random() * 99999), random.choice(cloud_images), random.random() * 0.05 + 0.05, random.random() * 0.6 + 0.2))

        self.clouds.sort(key=lambda x: x.depth)

    def update(self):
        for cloud in self.clouds: cloud.update()

    def render(self, surface, offset=(0, 0)):
        for cloud in self.clouds: cloud.render(surface, offset)
