import pygame
from config.settings import WIDTH, HEIGHT, TILE_SIZE, LOG_WIDTH, COLOR_BACKGROUND, COLOR_TEXT, SNAKE_SPEED, COLOR_LIGHT, COLOR_DARK
from src.game.snake import Snake
from src.game.food import Food
from src.game.board import Board

class Game:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((WIDTH + LOG_WIDTH, HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()

        # Initialize game components
        self.reset_game()

        # Game State
        self.font = pygame.font.SysFont(None, 24)
        self.logs = []
        self.position_message = ""

    def reset_game(self):

        # Reinitialize the board and snake
        self.board = Board(WIDTH, HEIGHT, TILE_SIZE)
        initial_position = (self.board.grid_width // 2 * TILE_SIZE, self.board.grid_height // 2 * TILE_SIZE)
        self.snake = Snake(initial_position, TILE_SIZE)
        self.snake.direction = None  # Reset direction to None for a fresh start

        # Reinitialize food
        self.food = Food(self.board, self.snake, TILE_SIZE)

        # Reset game state flags and score
        self.running = True
        self.paused = True  # Start paused until the player presses a key
        self.game_over = False
        self.score = 0
        self.position_message = ""  # Clear the position message

    def log(self, message):
        # Logs event during the game
        self.logs.append(message)
        # Limit number of displayed logs
        if len(self.logs) > 10:  
            self.logs.pop(0)
    
    # Constantly update the position of the snake to be displayed in the log section
    def update_position_message(self):
        head_pos = self.snake.head_position()
        self.position_message = f"Snake Position: {head_pos}"

    def handle_input(self):
        # Watches for input at start of game, and constantly throughout the game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.paused:
                    if self.game_over:
                        # Restart the game on key press after game over
                        self.reset_game()
                        self.log("New game started.")

                    else:
                        # Set initial direction to unpause and start the game
                        # UP
                        if event.key in (pygame.K_UP, pygame.K_w):
                            self.snake.change_direction("UP")
                            self.paused = False
                            self.log("Initial direction: UP")
                        # DOWN
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            self.snake.change_direction("DOWN")
                            self.paused = False
                            self.log("Initial direction: DOWN")
                        # LEFT
                        elif event.key in (pygame.K_LEFT, pygame.K_a):
                            self.snake.change_direction("LEFT")
                            self.paused = False
                            self.log("Initial direction: LEFT")
                        # RIGHT
                        elif event.key in (pygame.K_RIGHT, pygame.K_d):
                            self.snake.change_direction("RIGHT")
                            self.paused = False
                            self.log("Initial direction: RIGHT")

                # Allow changing direction only if the game is running
                elif not self.paused:

                    # UP 
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.snake.change_direction("UP")
                    # DOWN
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.snake.change_direction("DOWN")
                    # LEFT
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        self.snake.change_direction("LEFT")
                    # RIGHT
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.snake.change_direction("RIGHT")


    def update(self):
        if self.paused or self.game_over:
            return

        # Constantly be moving the snkae
        self.snake.move()
        # Constantly be updating the position of the snake display in log 
        self.update_position_message()

        # Logic for eating a fruit
        if self.snake.head_position() == self.food.position:
            # increase score
            self.score += 1
            # set the food_position to display in log 
            food_position = self.food.position
            # grow the snake
            self.snake.grow()
            self.food.position = self.food.spawn(self.snake.body)
            # Log the position
            self.log(f"Snake ate food at: {food_position}")

        # Check for snake hitting the wall
        if not self.board.is_within_bounds(self.snake.head_position()):
            self.log("Snake hit the boundary.")
            self.game_over = True
            self.paused = True

        # Check for snake hitting itself
        elif self.snake.has_collision():
            self.log("Snake collided with itself.")
            self.game_over = True
            self.paused = True

    def render(self):
        # Render the baord
        for row in range(0, HEIGHT, TILE_SIZE):
            for col in range(0, WIDTH, TILE_SIZE):
                color = COLOR_LIGHT if (row // TILE_SIZE + col // TILE_SIZE) % 2 == 0 else COLOR_DARK
                pygame.draw.rect(self.window, color, (col, row, TILE_SIZE, TILE_SIZE))

        # Draw the snake and food
        self.snake.draw(self.window)
        self.food.draw(self.window)

        # Render LOG Section
        pygame.draw.rect(self.window, COLOR_BACKGROUND, (WIDTH, 0, LOG_WIDTH, HEIGHT))
        score_text = self.font.render(f"Score: {self.score}", True, COLOR_TEXT)
        self.window.blit(score_text, (WIDTH + 10, 10))

        # Render LOG Section position text
        position_text = self.font.render(self.position_message, True, COLOR_TEXT)
        self.window.blit(position_text, (WIDTH + 10, 40))

        # Render LOG Section text
        y_offset = 80
        for log in self.logs:
            log_text = self.font.render(log, True, COLOR_TEXT)
            self.window.blit(log_text, (WIDTH + 10, y_offset))
            y_offset += 20

        # Logic for game restarting/Starting
        if self.paused:
            
            # Game needs to be restarted 
            if self.game_over:
                pause_text = self.font.render("Press any key to restart", True, COLOR_TEXT)
             # Game needs to be started
            else:
                pause_text = self.font.render("Use W A S D or Arrow Keys to start", True, COLOR_TEXT)
            self.window.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2))

        pygame.display.flip()

    def run(self):
        try:
            while self.running:
                self.handle_input()
                self.update()
                self.render()
                self.clock.tick(SNAKE_SPEED)
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            pygame.quit()
