from scripts.core import *

class Tilemap:
    def __init__(self, game, tile_size = 16):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []

    def tiles_around(self, pos):
        tiles = []
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in NEIGHBOR_OFFSETS:
            check_loc = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])

        return tiles

    def extract(self, id_pairs, keep=false):
        matches = []
        for tile in self.offgrid_tiles.copy():
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                if not keep:
                    self.offgrid_tiles.remove(tile)
                    
        for loc in self.tilemap.copy():
            tile = self.tilemap[loc]
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                matches[-1]['position'] = matches[-1]['position'].copy()
                matches[-1]['position'][0] *= self.tile_size
                matches[-1]['position'][1] *= self.tile_size
                if not keep:
                    del self.tilemap[loc]

        return matches

    def save(self, path):
        f = open(path, 'w')
        json.dump({ 'tilemap': self.tilemap, 'tile_size': self.tile_size, 'offgrid': self.offgrid_tiles }, f)
        f.close()

    def load(self, path):
        f = open(path, 'r')
        map_data = json.load(f)
        f.close()

        self.tilemap = map_data['tilemap']
        self.tile_size = map_data['tile_size']
        self.offgrid_tiles = map_data['offgrid']

    def physics_rects_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            if tile['type'] in PHYSICS_TILES:
                rects.append(pygame.Rect(tile['position'][0] * self.tile_size, tile['position'][1] * self.tile_size, self.tile_size, self.tile_size))

        return rects

    def solid_check(self, position):
        tile_loc = str(int(position[0] // self.tile_size)) + ';' + str(int(position[1] // self.tile_size))
        if tile_loc in self.tilemap:
            if self.tilemap[tile_loc]['type'] in PHYSICS_TILES:
                return self.tilemap[tile_loc]

    def render(self, surface, offset = (0, 0)):
        for tile in self.offgrid_tiles:
            surface.blit(self.game.assets.get(tile['type'])[tile['variant']], (tile['position'][0] - offset[0], tile['position'][1] - offset[1]))

        for x in range(offset[0] // self.tile_size, (offset[0] + surface.get_width()) // self.tile_size + 1):
            for y in range(offset[1] // self.tile_size, (offset[1] + surface.get_height()) // self.tile_size + 1):
                loc = str(x) + ';' + str(y)
                if loc in self.tilemap:
                    tile = self.tilemap[loc]
                    surface.blit(self.game.assets.get(tile['type'])[tile['variant']], (tile['position'][0] * self.tile_size - offset[0], tile['position'][1] * self.tile_size - offset[1]))
