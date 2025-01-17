import pygame
from src.game.board import *

class Snake:
    def __init__(self, initial_position, tile_size):
        self.tile_size = tile_size
        self.body = [initial_position]
        self.direction = None  # Start with no direction
        self.growing = False

    def change_direction(self, new_direction):
        if self.direction is None:
            self.direction = new_direction
        else:
            # Prevent the snake from reversing
            opposite_directions = {
                'UP': 'DOWN',
                'DOWN': 'UP',
                'LEFT': 'RIGHT',
                'RIGHT': 'LEFT'
            }
            if new_direction != opposite_directions[self.direction]:
                self.direction = new_direction

    # move the snake
    def move(self):
        # Do not move until a direction is set
        if self.direction is None:
            return  

        head_x, head_y = self.body[0]

        # what direction the snake is moving
        if self.direction == 'UP':
            new_head = (head_x, head_y - self.tile_size)
        elif self.direction == 'DOWN':
            new_head = (head_x, head_y + self.tile_size)
        elif self.direction == 'LEFT':
            new_head = (head_x - self.tile_size, head_y)
        elif self.direction == 'RIGHT':
            new_head = (head_x + self.tile_size, head_y)

        # move the head forward one
        self.body.insert(0, new_head)

        # pop the last segment of its body 
        if not self.growing:
            self.body.pop()
        else:
            self.growing = False

    # grow the snake
    def grow(self):
        self.growing = True

    # get head position of snake
    def head_position(self):
        return self.body[0]

    def has_collision(self, board):
        # Check for self-collision
        if self.head_position() in self.body[1:]:
            return True

        # Check for wall collision
        if board.is_wall(self.head_position()):
            return True

    # draw the snake on the board
    def draw(self, surface):
        for segment in self.body:
            x, y = segment
            pygame.draw.rect(surface, (0, 255, 0), (x, y, self.tile_size, self.tile_size))

    def get_next_head_position(self):
        head_x, head_y = self.head_position()

        if self.direction == "UP":
            return head_x, head_y - self.tile_size
        elif self.direction == "DOWN":
            return head_x, head_y + self.tile_size
        elif self.direction == "LEFT":
            return head_x - self.tile_size, head_y
        elif self.direction == "RIGHT":
            return head_x + self.tile_size, head_y

        # If no direction is set, return the current head position
        return head_x, head_y

    def will_collide(self, direction, board_width, board_height, walls):
        
        head_x, head_y = self.head_position()

        if direction == "UP":
            new_head = (head_x, head_y - self.tile_size)
        elif direction == "DOWN":
            new_head = (head_x, head_y + self.tile_size)
        elif direction == "LEFT":
            new_head = (head_x - self.tile_size, head_y)
        elif direction == "RIGHT":
            new_head = (head_x + self.tile_size, head_y)
        else:
            return False

        # Check board boundaries
        if not (0 <= new_head[0] < board_width and 0 <= new_head[1] < board_height):
            return True

        # Check collision with the snake's body
        if new_head in self.body:
            return True

        # Check collision with walls
        if new_head in walls:
            return True

        return False

    
    def turn_left(self):
        turn_map = {
            "UP": "LEFT",
            "DOWN": "RIGHT",
            "LEFT": "DOWN",
            "RIGHT": "UP"
        }
        return turn_map[self.direction] if self.direction else None

    def turn_right(self):
        turn_map = {
            "UP": "RIGHT",
            "DOWN": "LEFT",
            "LEFT": "UP",
            "RIGHT": "DOWN"
        }
        return turn_map[self.direction] if self.direction else None