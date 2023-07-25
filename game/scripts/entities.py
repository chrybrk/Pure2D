from scripts.core import *
from scripts.particle import Particle
from scripts.spark import Spark

class Entity:
    def __init__(self, game, e_type, position, size):
        self.game = game
        self.type = e_type
        self.position = list(position)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = { 'top': false, 'bottom': false, 'right': false, 'left': false }

        self.action = ''
        self.anim_offset = (-3, -3)
        self.flip = false
        self.set_action('idle')

        self.last_movement = [0, 0]

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

        self.last_movement = movement

        self.animation.update()

    def render(self, surface, offset = (0, 0)):
        surface.blit(pygame.transform.flip(self.animation.image(), self.flip, false), (self.position[0] - offset[0] + self.anim_offset[0], self.position[1] - offset[1] + self.anim_offset[1]))

class Player(Entity):
    def __init__(self, game, position, size):
        super().__init__(game, 'player', position, size)
        self.air_time = 0
        self.jumps = 2
        self.wall_slide = false
        self.dashing = false

    def update(self, tilemap, movement):
        super().update(tilemap, movement)

        self.air_time += 1
        if self.air_time > 180:
            self.game.dead += 1
            self.game.screenshake = max(self.game.screenshake_amount, self.game.screenshake)

        if self.collisions['bottom']:
            self.air_time = 0
            self.jumps = 2

        self.wall_slide = false
        if (self.collisions['right'] or self.collisions['left']) and self.air_time > 5:
            self.air_time = 10
            self.wall_slide = true
            self.velocity[1] = min(self.velocity[1], 0.2)
            if self.collisions['right']:
                self.flip = false
            if self.collisions['left']:
                self.flip = true
            self.set_action('wall_slide')

        if not self.wall_slide:
            if self.air_time > 5:
                self.set_action('jump')
            elif movement[0] != 0:
                self.set_action('run')
            else:
                self.set_action('idle')

        if abs(self.dashing) in {60, 50}:
            for i in range(20):
                angle = random.random() * math.pi * 2
                speed = random.random() * 0.5 + 0.5
                p_vel = [math.cos(angle) * speed, math.sin(angle) * speed]
                self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity = p_vel, frame = random.randint(0, 7)))

        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)

        if abs(self.dashing) > 50:
            self.velocity[0] = abs(self.dashing) / self.dashing * 8
            if abs(self.dashing) == 51:
                self.velocity[0] *= 0.1

                p_vel = [abs(self.dashing) / self.dashing * random.random() * 3, 0]
                self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity = p_vel, frame = random.randint(0, 7)))

        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)

    def jump(self):
        if self.wall_slide:
            if self.flip and self.last_movement[0] < 0:
                self.velocity[0] = 3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)

                return true

            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)

                return true

        elif self.jumps:
            self.velocity[1] = -2
            self.jumps -= 1
            self.air_time = 5

            return true

    def dash(self):
        if not self.dashing:
            if self.flip:
                self.dashing = -60
            else:
                self.dashing =  60

    def render(self, surface, offset=(0, 0)):
        if abs(self.dashing) <= 50:
            super().render(surface, offset)

class Enemy(Entity):
    def __init__(self, game, position, size):
        super().__init__(game, "enemy", position, size)

        self.walking = 0

    def update(self, tilemap, movement):
        if self.walking:
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.position[1] + 23)):
                if (self.collisions['right'] or self.collisions['left']):
                    self.flip = not self.flip
                else:
                    movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
            else:
                self.flip = not self.flip

            self.walking = max(0, self.walking - 1)

            if not self.walking:
                dis = (self.game.player.position[0] - self.position[0], self.game.player.position[1] - self.position[1])
                if abs(dis[1]) < 16:
                    if self.flip and dis[0] < 0:
                        self.game.projectiles.append([[self.rect().centerx - 7, self.rect().centery], -1.5, 0])
                        for i in range(4): self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5 + math.pi, 2 + random.random()))
                    if not self.flip and dis[0] > 0:
                        self.game.projectiles.append([[self.rect().centerx + 7, self.rect().centery],  1.5, 0])
                        for i in range(4): self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5, 2 + random.random()))

        elif random.random() < 0.01:
            self.walking = random.randint(30, 120)

        super().update(tilemap, movement)

        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')

        if abs(self.game.player.dashing) >= 50:
            if self.rect().colliderect(self.game.player.rect()):
                self.game.screenshake = max(self.game.screenshake_amount, self.game.screenshake)
                for i in range(30):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.sparks.append(Spark(self.game.player.rect().center, angle, 2 + random.random()))
                    self.game.particles.append(Particle(self.game, 'particle', self.game.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame = random.randint(0, 7)))

                self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))

                return true

        return false

    def render(self, surface, offset=(0, 0)):
        super().render(surface, offset = offset)

        if self.flip:
            surface.blit(pygame.transform.flip(self.game.assets.get("gun"), true, false), (self.rect().centerx - 2 - self.game.assets.get("gun").get_width() - offset[0], self.rect().centery - offset[1]))
        else:
            surface.blit(self.game.assets.get("gun"), (self.rect().centerx + 2 - offset[0], self.rect().centery - offset[1]))
