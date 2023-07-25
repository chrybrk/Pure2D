from scripts.core import *

class Particle:
    def __init__(self, game, p_type, position, velocity = [0, 0], frame = 0):
        self.game = game
        self.type = p_type
        self.position = list(position)
        self.velocity = velocity
        self.frame = frame
        self.animation = self.game.assets.get('particle/' + p_type).copy()
        self.animation.frame = frame
    
    def update(self):
        kill = false
        if self.animation.done:
            kill = true

        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]

        self.animation.update()

        return kill

    def render(self, surface, offset=(0, 0)):
        image = self.animation.image()
        surface.blit(image, (self.position[0] - offset[0], self.position[1] - offset[1], self.position[0] - offset[0] - image.get_width() // 2, self.position[1] - offset[1] - image.get_height() // 2))
