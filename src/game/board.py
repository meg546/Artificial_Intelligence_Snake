import random
import pygame

class Board:
    def __init__(self, width, height, tile_size, num_walls=0):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.grid_width = width // tile_size
        self.grid_height = height // tile_size
        self.num_walls = num_walls
        self.walls = self.generate_walls(num_walls)
    
    # check bounds on the board
    def is_within_bounds(self, position):
        x, y = position
        return 0 <= x < self.width and 0 <= y < self.height
    
    def generate_walls(self, num_walls):
        walls = set()
        while len(walls) < self.num_walls:
            wall_x = random.randint(0, self.grid_width - 1) * self.tile_size
            wall_y = random.randint(0, self.grid_height - 1) * self.tile_size
            walls.add((wall_x, wall_y))
        return walls

    def is_wall(self, position):
        return position in self.walls

    def draw(self, surface):
        for wall in self.walls:
            pygame.draw.rect(surface, (128, 128, 128), (*wall, self.tile_size, self.tile_size))
