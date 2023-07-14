from pure.pure import *
from pure.pure import Vector as vec
from pure.pure import sharedresource as res

game = Game()
game.set_window_clear_color(color.JetBlack.value)

def main_loop(dt): pass

game.set_main_game_function(main_loop)
game.run()
