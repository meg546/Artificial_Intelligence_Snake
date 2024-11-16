import pygame

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

    # check for if the snake has a collsion
    def has_collision(self):
        return self.head_position() in self.body[1:]

    # draw the snake on the board
    def draw(self, surface):
        for segment in self.body:
            x, y = segment
            pygame.draw.rect(surface, (0, 255, 0), (x, y, self.tile_size, self.tile_size))

    def get_next_head_position(self):
        """
        Returns the position of the snake's head after it moves in its current direction.
        """
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

