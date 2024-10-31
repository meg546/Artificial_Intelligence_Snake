# src/game/food.py

import pygame
import random

class Food:
    def __init__(self, board, snake, tile_size):
        self.board = board
        self.snake = snake
        self.tile_size = tile_size
        self.position = self.spawn(snake.body)

    def spawn(self, snake_body):
        # Spawns the food, somewhere random where the snake is not 
        empty_positions = [
            (x * self.tile_size, y * self.tile_size)
            for x in range(self.board.grid_width)
            for y in range(self.board.grid_height)
            if (x * self.tile_size, y * self.tile_size) not in snake_body
        ]
        
        # Select a random empty position
        return random.choice(empty_positions) if empty_positions else None

    # Function to draw food randomly on board
    def draw(self, surface):
        if self.position:
            x, y = self.position
            pygame.draw.rect(surface, (255, 0, 0), (x, y, self.tile_size, self.tile_size))
