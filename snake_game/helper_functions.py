import random

def random_square(surface_width, surface_height, tile_width, tile_height):
    horizontal_tiles = surface_width // tile_width
    vertical_tiles = surface_height // tile_height

    return (random.randint(0, horizontal_tiles) * tile_width, random.randint(0, vertical_tiles) * tile_height)


# for _ in range(10):
#     print(random_square(100, 100, 50, 50))