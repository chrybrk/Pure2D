from scripts.core import *

class Entity:
    def __init__(self, game, e_type, position, size):
        self.game = game
        self.type = e_type
        self.position = list(position)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = { 'up': false, 'down': false, 'right': false, 'left': false }

        self.action = ''
        self.anim_offset = (-3, -3)
        self.flip = false
        self.set_action('idle')

    def rect(self): return pygame.Rect(*self.position, *self.size)

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets.get(self.type + '/' + self.action).copy()

    def update(self, tilemap, movement):
        self.collisions = { 'top': false, 'bottom': false, 'right': false, 'left': false }

        frame_movement = (movement[0] + self.velocity[0] * self.game.dt, movement[1] + self.velocity[1] * self.game.dt)

        self.position[0] += frame_movement[0]
        er = self.rect()
        for rect in tilemap.physics_rects_around(self.position):
            if er.colliderect(rect):
                if frame_movement[0] > 0:
                    er.right = rect.left
                    self.collisions['right'] = true
                if frame_movement[0] < 0:
                    er.left = rect.right
                    self.collisions['left'] = true

                self.position[0] = er.x

        self.position[1] += frame_movement[1]
        er = self.rect()
        for rect in tilemap.physics_rects_around(self.position):
            if er.colliderect(rect):
                if frame_movement[1] > 0:
                    er.bottom = rect.top
                    self.collisions['bottom'] = true
                if frame_movement[1] < 0:
                    er.top = rect.bottom
                    self.collisions['top'] = true

                self.position[1] = er.y

        self.velocity[1] = min(5, self.velocity[1] + 0.1)
        if self.collisions['bottom'] or self.collisions['top']: self.velocity[1] = 0

        if movement[0] > 0: self.flip = false
        if movement[0] < 0: self.flip = true

        self.animation.update()

    def render(self, surface, offset = (0, 0)):
        surface.blit(pygame.transform.flip(self.animation.image(), self.flip, false), (self.position[0] - offset[0] + self.anim_offset[0], self.position[1] - offset[1] + self.anim_offset[1]))

class Player(Entity):
    def __init__(self, game, position, size):
        super().__init__(game, 'player', position, size)
        self.air_time = 0

    def update(self, tilemap, movement):
        super().update(tilemap, movement)

        self.air_time += 1
        if self.collisions['bottom']: self.air_time = 0

        if self.air_time > 4: self.set_action('jump')
        elif movement[0] != 0: self.set_action('run')
        else: self.set_action('idle')
