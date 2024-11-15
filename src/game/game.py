import pygame

from config.settings import * 
from src.ai.a_star import *
from src.ai.ai_controller import * 

from src.game.snake import Snake
from src.game.food import Food
from src.game.board import Board

import json
import os


class Game:

    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((WIDTH + LOG_WIDTH, HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()

        # Initialize mode-specific statistics
        self.normal_stats = {"runs": 0, "highest_score": 0, "total_score": 0, "last_score": 0}
        self.a_star_stats = {"runs": 0, "highest_score": 0, "total_score": 0, "last_score": 0}
        self.learning_stats = {"runs": 0, "highest_score": 0, "total_score": 0, "last_score": 0}

        # Load statistics from file
        self.load_statistics()
        
        # Pass self.window to select_mode
        self.mode = select_mode(self.window)
        
        self.running = True
        self.paused = True
        self.game_over = False
        self.font = pygame.font.SysFont(None, 24)
        self.logs = []
        self.position_message = ""

        # Initialize game components
        self.reset_game()

        # Initialize additional variables
        self.font = pygame.font.SysFont("Arial", 18)
        self.logs = []
        self.position_message = ""
        self.goal_text = ""


    def load_statistics(self):
        """Load statistics for each mode from a JSON file."""
        try:
            with open("game_stats.json", "r") as file:
                stats = json.load(file)
                self.normal_stats = stats.get("normal", self.normal_stats)
                self.a_star_stats = stats.get("a_star", self.a_star_stats)
                self.learning_stats = stats.get("learning", self.learning_stats)
        except (FileNotFoundError, json.JSONDecodeError):
            # Set defaults if the file does not exist or is corrupted
            self.normal_stats = {"runs": 0, "highest_score": 0, "total_score": 0, "last_score": 0}
            self.a_star_stats = {"runs": 0, "highest_score": 0, "total_score": 0, "last_score": 0}
            self.learning_stats = {"runs": 0, "highest_score": 0, "total_score": 0, "last_score": 0}


    def save_statistics(self):
        """Save statistics for each mode to a JSON file."""
        stats = {
            "normal": self.normal_stats,
            "a_star": self.a_star_stats,
            "learning": self.learning_stats
        }
        with open("game_stats.json", "w") as file:
            json.dump(stats, file)


    def end_game(self):
        # Update statistics for the current mode
        if self.mode == NORMAL_MODE:
            stats = self.normal_stats
        elif self.mode == A_STAR_MODE:
            stats = self.a_star_stats
        elif self.mode == LEARNING_MODE:
            stats = self.learning_stats

        stats["runs"] += 1
        stats["last_score"] = self.score
        stats["total_score"] += self.score
        stats["highest_score"] = max(stats["highest_score"], self.score)
        self.save_statistics()  # Save stats to file

        # Reset game status flags
        self.game_over = True
        self.paused = True

    def reset_game(self):
        # Reinitialize the board and snake
        self.board = Board(WIDTH, HEIGHT, TILE_SIZE)
        # start snake in middle of board
        initial_position = (self.board.grid_width // 2 * TILE_SIZE, self.board.grid_height // 2 * TILE_SIZE)
        self.snake = Snake(initial_position, TILE_SIZE)
        self.snake.direction = None

        # Reinitialize food
        self.food = Food(self.board, self.snake, TILE_SIZE)

        # Reset game state flags and score
        self.running = True
        self.paused = True  # Start paused until the player presses a key
        self.game_over = False
        self.score = 0
        self.position_message = ""  # Clear the position message


    def log(self, message):
        if VERBOSE:
            # Logs event during the game
            self.logs.append(message)
            # Limit number of displayed logs
            if len(self.logs) > 10:  
                self.logs.pop(0)
    

    # Constantly update the position of the snake to be displayed in the log section
    def update_position_message(self):
        head_pos_x, head_pos_y = self.snake.head_position()
        self.position_message = f"Snake Position: {head_pos_x // TILE_SIZE, head_pos_y // TILE_SIZE}"


    def update_goal_position(self):
        fruit_x, fruit_y = self.food.position
        self.goal_text = f"Goal Position: {fruit_x // TILE_SIZE, fruit_y // TILE_SIZE}"


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
                        # self.log("Direction Move: UP")
                    # DOWN
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.snake.change_direction("DOWN")
                        # self.log("Direction Move: DOWN")
                    # LEFT
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        self.snake.change_direction("LEFT")
                        # self.log("Direction Move: LEFT")
                    # RIGHT
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.snake.change_direction("RIGHT")
                        # self.log("Direction Move: RIGHT")


    def update(self):
        if self.paused or self.game_over:
            return

        # Use A* mode if the game is in A* mode; otherwise, allow normal movement
        if self.mode == A_STAR_MODE:
            a_star_move(self.snake, self.food, self.board)  # Use A* algorithm to move the snake
        else:
            self.snake.move()  # Regular player-controlled movement

        # Constantly update the position of the snake display in the log
        self.update_position_message()
        self.update_goal_position()

        # Logic for eating a fruit
        if self.snake.head_position() == self.food.position:
            fruit_x, fruit_y = self.food.position
            self.log(f"Goal Reached: {fruit_x // TILE_SIZE, fruit_y // TILE_SIZE}")
            # Increase score
            self.score += 1
            # Grow the snake
            self.snake.grow()
            self.food.position = self.food.spawn(self.snake.body)

        # Check for snake hitting the wall
        if not self.board.is_within_bounds(self.snake.head_position()):
            self.log("Snake hit the boundary.")
            self.game_over = True
            self.paused = True
            self.end_game()

        # Check for snake hitting itself
        elif self.snake.has_collision():
            self.log("Snake collided with itself.")
            self.game_over = True
            self.paused = True
            self.end_game()

    def render(self):
        # Render the board
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

        # Render position text in the LOG section
        position_text = self.font.render(self.position_message, True, COLOR_TEXT)
        self.window.blit(position_text, (WIDTH + 10, 40))

        goal_text = self.font.render(self.goal_text, True, COLOR_TEXT)
        self.window.blit(goal_text, (WIDTH + 10, 60))

        # Determine which stats to display based on the current mode
        if self.mode == NORMAL_MODE:
            stats = self.normal_stats
        elif self.mode == A_STAR_MODE:
            stats = self.a_star_stats
        elif self.mode == LEARNING_MODE:
            stats = self.learning_stats

        # Calculate the average score safely (avoid division by zero)
        average_score = stats["total_score"] / stats["runs"] if stats["runs"] > 0 else 0

        # Render mode-specific statistics
        runs_text = self.font.render(f"Runs: {stats['runs']}", True, COLOR_TEXT)
        highest_score_text = self.font.render(f"Highest Score: {stats['highest_score']}", True, COLOR_TEXT)
        last_score_text = self.font.render(f"Last Score: {stats['last_score']}", True, COLOR_TEXT)
        average_score_text = self.font.render(f"Average Score: {average_score:.2f}", True, COLOR_TEXT)

        # Position each text line
        self.window.blit(runs_text, (WIDTH + 10, 80))
        self.window.blit(highest_score_text, (WIDTH + 10, 100))
        self.window.blit(last_score_text, (WIDTH + 10, 120))
        self.window.blit(average_score_text, (WIDTH + 10, 140))

        # Render log messages
        y_offset = 160
        for log in self.logs:
            log_text = self.font.render(log, True, COLOR_TEXT)
            self.window.blit(log_text, (WIDTH + 10, y_offset))
            y_offset += 20

        # Logic for game restarting/Starting
        if self.paused:
            # Game needs to be restarted 
            if self.game_over:
                pause_text = self.font.render("Press any key to restart", True, COLOR_TEXT)
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
