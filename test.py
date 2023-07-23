from pure.pure import *
from pure.pure import Vector as vec
from pure.pure import sharedresource as res

# init
game = Game()
game.set_window_clear_color(color.JetBlack.value)
game.create_surface_with_keeping_ratio(40)
res.font.set_font_renderer("./assets/dogica.ttf", 8, color.White.value, 0)

tile_editor = TileEditor("./assets/lvl0_map.csv", "./assets/monochrome-transparent_packed.png", vec(16, 16))

input_system = Input()
input_system.set_key("left", K_a)
input_system.set_key("right", K_d)
input_system.set_key("up", K_w)
input_system.set_key("down", K_s)
input_system.set_key("change_light", K_l)
input_system.set_key("jump", K_SPACE)

texture = Texture()
texture.load_tilesheet("./assets/monochrome-transparent_packed.png")

platform_tex = texture.load_texture_from_tilesheet(vec(160, 272), vec(16, 16))
platform = Sprite(vec(0, 250), tex = platform_tex)
platform.sprite_filling(2, 50)


idle = Texture("./assets/pixel_art/test-player/main.png")
player_sprites = [ Texture(f"./assets/pixel_art/test-player/idle{str(i)}.png") for i in range(0, 13) ]

player_tex = texture.load_texture_from_tilesheet(vec(400, 0), vec(16, 16))
player = Sprite(vec(200, 100), tex = idle)
player.init_physics()
player.physics.add_collision(platform)

enemy_tex = texture.load_texture_from_tilesheet(vec(416, 0), vec(16, 16))
enemy0 = Sprite(vec(230, 100), tex = enemy_tex)
enemy1 = Sprite(vec(50, 50), tex = enemy_tex)

game_over = false

bounce = 0.0
gravity = 0.9
gravity_back = 1
friction = 0.999
jump_height = 4
max_jump = 8
max_speed = 4
mid_air = false
walk = 0

old_position = vec(player.position.x, player.position.y)

def player_movement():
    global old_position, mid_air, walk

    if walk >= len(player_sprites): walk = 0

    dt = fpsLock(res.window.fps) / 1000

    if input_system.is_key_held("right"):
        player.unflip()
        if player.position.x - old_position.x < 0: old_position.x = player.position.x
        old_position.x = old_position.x - 0.5 if abs(player.position.x - old_position.x) < max_speed else player.position.x - max_speed
    elif input_system.is_key_held("left"):
        player.flip()
        if player.position.x - old_position.x > 0: old_position.x = player.position.x
        old_position.x = old_position.x + 0.5 if abs(player.position.x - old_position.x) < max_speed else player.position.x + max_speed
    else:
        if player.flipped: player.tex = player.texture_object.flip_x
        new_position = vec.lerp(old_position, player.position, 0.85)
        old_position.x = new_position.x

    for event in res.event:
        if event.type == KEYDOWN and event.key == K_SPACE and player.physics.is_on_floor():
            old_position.y += 12
            mid_air = true
        else:
            mid_air = false

    if mid_air:
        old_position.y -= 2

    vx = (player.position.x - old_position.x) * friction
    vy = (player.position.y - old_position.y) * friction

    old_position.x = player.position.x
    old_position.y = player.position.y

    player.position.x += vx
    player.position.y += vy
    player.position.y += gravity

    if (player.position.y > platform.position.y - player.size.y):
        player.position.y = platform.position.y - player.size.y
        old_position.y = player.position.y + vy * bounce
    elif (player.position.y < 0):
        player.position.y = 0
        old_position.y = player.position.y + vy * bounce


# player.update_fix_function(player_movement)

def level0(dt):
    global game_over
    enemy0.position = Vector.lerp(player.position, enemy0.position, 0.03)
    enemy1.position = Vector.lerp(player.position, enemy1.position, 0.01)

    player.physics.movement(2, 3.0, 3.0, 0.999, 5, 12)

    # if player.physics.collision.check_collisions(player, enemy0, enemy1): game_over = true
    res.renderer.add_drawable(player, enemy0, enemy1, platform)

def gameover(dt):
    text = "Game Over"
    res.font.draw(vec(res.window.get_surface().get_size()[0] / 2 - (len(text) * 4), res.window.get_surface().get_size()[1] / 2), text)

def testing(dt):
    tile_editor.draw()

res.scene.add_state("level0", level0)
res.scene.add_state("testing", testing)
res.scene.add_state("gameover", gameover)
res.scene.set_state("level0")

a = Light2D(500, (172, 172, 50), 0.2)
b = Light2D(500, (202, 71, 71), 1, 1, 0, 120)

light_display = Light2D.global_light_display()

a.set_light_display(light_display)
b.set_light_display(light_display)

def main_loop(dt):
    b.fill()
    a.fill()

    Light2D.global_light(light_display, intensity = 50)

    b.locate_light(100, 50)
    b.locate_light(250, 50)
    b.locate_light(400, 50)

    Light2D.render(light_display)

    res.font.draw(vec(0, 0), f"FPS:{int(clock.get_fps())}")
    if game_over: res.scene.set_state("gameover")
    res.scene.run()

game.set_main_game_function(main_loop)
game.run()
