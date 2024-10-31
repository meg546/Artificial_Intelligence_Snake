import random

class Board:
    def __init__(self, width, height, tile_size):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.grid_width = width // tile_size
        self.grid_height = height // tile_size
    
    # check bounds on the board
    def is_within_bounds(self, position):
        x, y = position
        return 0 <= x < self.width and 0 <= y < self.height
    
    # Check if the head collides with any other part of the body
    def has_collision(self):
        collision = self.head_position() in self.body[1:]
        print(f"Checking for collision. Head position: {self.head_position()}, Collision: {collision}")
        return collision
