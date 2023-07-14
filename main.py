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
platform = Sprite(vec(0, 200), tex = platform_tex)
platform.sprite_filling(2, 50)

player_tex = texture.load_texture_from_tilesheet(vec(400, 0), vec(16, 16))
player = Sprite(vec(200, 100), tex = "./assets/pixel_art/player.png")
player.init_physics()
player.physics.add_collision(platform)

enemy_tex = texture.load_texture_from_tilesheet(vec(416, 0), vec(16, 16))
enemy0 = Sprite(vec(230, 100), tex = enemy_tex)
enemy1 = Sprite(vec(50, 50), tex = enemy_tex)

game_over = false

bounce = 0.0
gravity = 0.9
gravity_back = 0.5
friction = 0.999
jump_height = 6
max_jump = 8
max_speed = 8
mid_air = false

old_position = vec(player.position.x, player.position.y)

def player_movement():
    global old_position, mid_air

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
        new_position = vec.lerp(old_position, player.position, 0.85)
        old_position.x = new_position.x

    if player.physics.is_on_floor() or mid_air:
        if input_system.is_key_held("jump"):
            mid_air = true
            if abs(player.position.y - old_position.y) < max_jump: old_position.y += jump_height
            else: mid_air = false
        else:
            mid_air = false
    else: old_position.y -= gravity_back

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


player.update_fix_function(player_movement)

def level0(dt):
    global game_over
    enemy0.position = Vector.lerp(player.position, enemy0.position, 0.03)
    enemy1.position = Vector.lerp(player.position, enemy1.position, 0.01)

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

a = Light2D(500, (167, 203, 143), 0.3)

def main_loop(dt):
    a.render(player.position.x, player.position.y, (178, 143, 203), 20)

    res.font.draw(vec(0, 0), f"FPS:{int(clock.get_fps())}")
    if game_over: res.scene.set_state("gameover")
    res.scene.run()

game.set_main_game_function(main_loop)
game.run()
