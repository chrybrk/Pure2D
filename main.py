from engine import *
from engine import resource_manager as res
from engine import Vector as vec

game = Game()
game.set_window_clear_color(color.JetBlack.value)
game.create_scale_surface(50)
res.font.set_font_renderer("./assets/dogica.ttf", 16, color.White.value, 0)

res.input.set_key("left", K_a)
res.input.set_key("right", K_d)
res.input.set_key("up", K_w)
res.input.set_key("down", K_s)
res.input.set_key("jump", K_SPACE)

world_map = TileReader("./assets/test.csv", "./assets/pixel_art/test-player/final_player/tile/ground.png", nil, vec(32, 32))

player = Sprite(vec(50, 100), texture = "./assets/pixel_art/test-player/final_player/main/main_sprite.png")
res.camera.init_target_centered(player)

res.collision.add_mask(player, *world_map.sprites)

velocity = vec(0, 0)
jump_buffer = 0
movement = vec(0, 0)
jump_bonus = true

def player_movement(dt):
    global jump_buffer, movement, velocity, jump_bonus

    if res.input.is_key_held("left"): velocity.x = max(-6, velocity.x - 50 * dt)
    if res.input.is_key_held("right"): velocity.x = min(6, velocity.x + 50 * dt)
    if res.input.is_key_pressed("jump"): jump_buffer = 0.2
    if res.input.is_any_key_up():
        movement = vec(0, 0)

    if res.input.is_key_pressed_up("left") or res.input.is_key_pressed_up("right"): velocity.x = 0

    if not player.collision_bottom:
        velocity.y = min(10, velocity.y + 50 * dt)
        if jump_bonus and res.input.is_key_pressed("jump"):
            velocity.y = 0
            velocity.y -= 750 * dt
            jump_bonus = false
            jump_buffer = 0
    else:
        jump_bonus = true
        if jump_buffer > 0:
            velocity.y = 0
            velocity.y -= 900 * dt
            jump_buffer = 0

    jump_buffer = abs(jump_buffer - dt) if jump_buffer > 0 else 0

def function0(dt):
    player_movement(dt)
    frame_movement = movement + velocity
    player.move(frame_movement)

    offset = res.camera.get_offset()
    offset = vec(1/20*offset.x, 1/20*offset.y)
    if abs(offset.x) >= 1 or abs(offset.y) >= 1:
        player.position += offset
        world_map.update_offset(offset)

    res.renderer.add_drawable(player, *world_map.sprites)

res.scene.add_state("0", function0)
res.scene.set_state("0")

a = Light2D(500, (172, 172, 50), 0.5)
light_display = Light2D.global_light_display()
a.set_light_display(light_display)

def main_loop(dt):
    a.fill()
    Light2D.global_light(light_display, color = (200, 100, 100), intensity = 100)
    # a.locate_light(*player.position.value2())
    Light2D.render(light_display)

    res.font.draw(vec(0, 0), f"FPS:{int(clock.get_fps())}")
    res.font.draw(vec(0, 20), f"RND: { res.renderer.count }")
    res.scene.run()

game.set_function(main_loop)
game.run()
