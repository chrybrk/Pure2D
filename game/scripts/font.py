from scripts.core import *

class Font:
    def __init__(self) -> nil:
        self.font = nil
        self.color = nil
        self.smooth = 1

    def set_font_renderer(self, font_family: str, font_size: int, color: tuple, smooth: int = 1) -> nil:
        self.font = pygame.font.Font(font_family, font_size)
        self.font_size = font_size
        self.color = color
        self.smooth = smooth

    def draw(self, surface, position, text: str) -> nil:
        fdr = self.font.render(text, self.smooth, self.color)
        surface.blit(fdr, (position[0], position[1]))
        del fdr
