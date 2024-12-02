import pygame
import json
import os
from config.settings import * 
from src.ai.a_star import *
from src.ai.learning import DeepQLearningModel
from src.ai.ai_controller import * 
from src.game.snake import Snake
from src.game.food import Food
from src.game.board import Board
from src.ai.visualization import *

class Game:
    def __init__(self, automate=False, max_runs=1):
        pygame.init()
        self.window = pygame.display.set_mode((WIDTH + LOG_WIDTH, HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()

        # Automation setup
        self.automate = automate
        self.max_runs = max_runs
        self.current_run = 0
        
        self.learning_model = DeepQLearningModel(
            state_space_size=14,
            action_space_size=4,
            learning_rate=0.001,
            gamma=0.9
        )
        self.learning_model.load_model("model.pth")

        # Initialize score tracking for visualization graphing
        self.scores = []  # List to store scores for plotting
        self.mean_scores = []  # List to store mean scores

        self.epsilon = 1.0  # Initial exploration rate
        self.epsilon_decay = 0.999  # Decay rate for exploration
        self.min_epsilon = 0.1  # Minimum exploration rate

        # Initialize statistics and run data attributes
        self.normal_stats = {"runs": 0, "highest_score": 0, "total_score": 0, "last_score": 0}
        self.a_star_stats = {"runs": 0, "highest_score": 0, "total_score": 0, "last_score": 0}
        self.learning_stats = {"runs": 0, "highest_score": 0, "total_score": 0, "last_score": 0}
        self.run_data = {NORMAL_MODE: [], A_STAR_MODE: [], LEARNING_MODE: []}

        # Load data from files
        self.load_statistics()
        self.load_run_data()

        # Mode selection
        self.mode = LEARNING_MODE if self.automate else select_mode(self.window)

        # Initialize game state
        self.running = True
        self.paused = not self.automate
        self.game_over = False
        self.font = pygame.font.SysFont("Arial", 18)
        self.logs = []
        self.position_message = ""
        self.goal_text = ""

        if self.automate:
            reset_automation_data()  # Reset the file


        # Initialize game components
        self.reset_game()
        print("Game initialized successfully.")

    # -----------------
    # Data Management
    # -----------------
    def log_training_data(self, rewards, scores):
        with open("training_log.csv", "a") as log_file:
            log_file.write(f"{rewards},{scores}\n")

    def update_position_message(self):
        """Update the message showing the snake's current head position."""
        head_pos_x, head_pos_y = self.snake.head_position()
        self.position_message = f"Snake Position: ({head_pos_x // TILE_SIZE}, {head_pos_y // TILE_SIZE})"

    def update_goal_position(self):
        """Update the message showing the current food's position."""
        fruit_x, fruit_y = self.food.position
        self.goal_text = f"Goal Position: ({fruit_x // TILE_SIZE}, {fruit_y // TILE_SIZE})"

    def load_statistics(self):
        """Load statistics for each mode from separate JSON files in the data directory."""
        for mode in [NORMAL_MODE, A_STAR_MODE, LEARNING_MODE]:
            filename = f"data/{mode}_stats.json"
            try:
                with open(filename, "r") as file:
                    if mode == NORMAL_MODE:
                        self.normal_stats = json.load(file)
                    elif mode == A_STAR_MODE:
                        self.a_star_stats = json.load(file)
                    elif mode == LEARNING_MODE:
                        self.learning_stats = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError):
                print(f"{filename} not found or corrupted, using default values.")

    def save_statistics(self):
        """Save statistics for each mode to separate JSON files in the data directory."""
        stats_files = {
            NORMAL_MODE: "data/normal_stats.json",
            A_STAR_MODE: "data/a_star_stats.json",
            LEARNING_MODE: "data/learning_stats.json"
        }

        for mode, filename in stats_files.items():
            data = (
                self.normal_stats if mode == NORMAL_MODE else
                self.a_star_stats if mode == A_STAR_MODE else
                self.learning_stats
            )
            with open(filename, "w") as file:
                json.dump(data, file, indent=4)
        print("Statistics saved to separate files in data directory.")

    def load_run_data(self):
        """Load run data for each mode from separate JSON files in the data directory."""
        for mode in [NORMAL_MODE, A_STAR_MODE, LEARNING_MODE]:
            filename = f"data/{mode}_run_data.json"
            try:
                with open(filename, "r") as file:
                    self.run_data[mode] = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError):
                self.run_data[mode] = []

    def save_run_data(self):
        """Save run data for each mode to separate JSON files in the data directory."""
        for mode, data in self.run_data.items():
            filename = f"data/{mode}_run_data.json"
            with open(filename, "w") as file:
                json.dump(data, file, indent=4)
        print("Run data saved to separate files in data directory.")

    # -----------------
    # Game Logic
    # -----------------

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.paused:
                    if self.game_over:
                        self.reset_game()
                    else:
                        self.paused = False
                elif self.mode == NORMAL_MODE:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.snake.change_direction("UP")
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.snake.change_direction("DOWN")
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        self.snake.change_direction("LEFT")
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.snake.change_direction("RIGHT")

    def reset_game(self):
        print("Resetting game...")
        self.board = Board(WIDTH, HEIGHT, TILE_SIZE)
        initial_position = (self.board.grid_width // 2 * TILE_SIZE, self.board.grid_height // 2 * TILE_SIZE)
        self.snake = Snake(initial_position, TILE_SIZE)
        self.snake.direction = None
        self.food = Food(self.board, self.snake, TILE_SIZE)
        self.running = True
        self.paused = not self.automate
        self.game_over = False
        self.score = 0
        self.position_message = ""
        self.goal_text = ""
        print("Game reset successfully.")


    def end_game(self):
        print(f"Ending game #{self.current_run + 1}.")
        stats = (
            self.normal_stats if self.mode == NORMAL_MODE else
            self.a_star_stats if self.mode == A_STAR_MODE else
            self.learning_stats
        )
        stats["runs"] += 1
        stats["last_score"] = self.score
        stats["total_score"] += self.score
        stats["highest_score"] = max(stats["highest_score"], self.score)

        # Append the score to the scores list for the current automation
        self.scores.append(self.score)

        if self.mode == LEARNING_MODE:
            mean_score = sum(self.scores[-100:]) / min(len(self.scores), 100)
            self.mean_scores.append(mean_score)
            self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)
            print(f"Epsilon decayed to {self.epsilon:.4f}")

        # Log current automation data
        log_current_automation_data(self.current_run, self.score)

        # Log run data (run number and score)
        run_info = {"run": stats["runs"], "score": self.score}
        self.run_data[self.mode].append(run_info)
        self.save_run_data()
        self.save_statistics()

        # Save the learning model for every 100 runs
        if self.mode == LEARNING_MODE and self.current_run == self.max_runs - 1:  # At the end of automation
            plot(
                self.scores,
                self.mean_scores,
                save_path="final_learning_plot.png",
                title="Learning Model Progress"
            )
            print("Automation completed. Learning plot saved.")

        if self.automate:
            self.current_run += 1
            if self.current_run < self.max_runs:
                self.reset_game()
            else:
                print(f"[AUTOMATION] Completed {self.max_runs} runs. Displaying graph.")
                # Automation finished, plot the graph
                if self.mode == A_STAR_MODE:
                    # Load scores from JSON for A* plotting
                    with open("data/current_automation_data.json", "r") as file:
                        automation_data = json.load(file)
                    scores = [run["score"] for run in automation_data["runs"]]
                    plot(
                        scores,
                        save_path="astar_plot.png",
                        title="A* Algorithm Progress"
                    )
                elif self.mode == LEARNING_MODE:
                    plot(
                        self.scores,
                        self.mean_scores,
                        save_path="learning_plot.png",
                        title="Learning Model Progress"
                    )
                self.running = False
        else:
            self.game_over = True
            self.paused = True

    def update(self):
        if self.paused or self.game_over:
            return

        if self.mode == LEARNING_MODE:
            # Get current state
            current_state = self.learning_model.get_state(self.snake, self.food, self.board)

            # Choose an action using the learning model
            action = self.learning_model.choose_action(current_state, self.epsilon)
            self.snake.change_direction(["UP", "DOWN", "LEFT", "RIGHT"][action])
            self.snake.move()

            # Compute reward and next state
            reward = self.learning_model.get_reward(self.snake, self.food, self.board)
            next_state = self.learning_model.get_state(self.snake, self.food, self.board)

            # Train the model
            self.learning_model.train_short_memory(current_state, action, reward, next_state, self.game_over)

            # Remember for long-term memory
            self.learning_model.remember(current_state, action, reward, next_state, self.game_over)

            if reward == -10:  # Game over
                self.end_game()
            elif reward == 10:  # Food eaten
                self.score += 1
                self.snake.grow()
                self.food.position = self.food.spawn(self.snake.body)

        elif self.mode == A_STAR_MODE:
            a_star_move(self.snake, self.food, self.board)

        else:  # NORMAL_MODE
            self.snake.move()

        # Update display messages
        self.update_position_message()
        self.update_goal_position()

        # Collision and food handling for all modes
        if self.snake.head_position() == self.food.position:
            self.score += 1
            self.snake.grow()
            self.food.position = self.food.spawn(self.snake.body)
        elif not self.board.is_within_bounds(self.snake.head_position()) or self.snake.has_collision():
            self.end_game()

    def render(self):
        """Render the game state and statistics to the window."""
        # Draw the game board
        for row in range(0, HEIGHT, TILE_SIZE):
            for col in range(0, WIDTH, TILE_SIZE):
                color = COLOR_LIGHT if (row // TILE_SIZE + col // TILE_SIZE) % 2 == 0 else COLOR_DARK
                pygame.draw.rect(self.window, color, (col, row, TILE_SIZE, TILE_SIZE))

        # Draw the snake and food
        self.snake.draw(self.window)
        self.food.draw(self.window)

        # Draw the side log area
        pygame.draw.rect(self.window, COLOR_BACKGROUND, (WIDTH, 0, LOG_WIDTH, HEIGHT))

        # Display score
        score_text = self.font.render(f"Score: {self.score}", True, COLOR_TEXT)
        self.window.blit(score_text, (WIDTH + 10, 10))

        # Display position and goal messages
        position_text = self.font.render(self.position_message, True, COLOR_TEXT)
        self.window.blit(position_text, (WIDTH + 10, 40))

        goal_text = self.font.render(self.goal_text, True, COLOR_TEXT)
        self.window.blit(goal_text, (WIDTH + 10, 60))

        # Display statistics
        stats = (
            self.normal_stats if self.mode == NORMAL_MODE else
            self.a_star_stats if self.mode == A_STAR_MODE else
            self.learning_stats
        )
        average_score = stats["total_score"] / stats["runs"] if stats["runs"] > 0 else 0

        runs_text = self.font.render(f"Runs: {stats['runs']}", True, COLOR_TEXT)
        highest_score_text = self.font.render(f"Highest Score: {stats['highest_score']}", True, COLOR_TEXT)
        last_score_text = self.font.render(f"Last Score: {stats['last_score']}", True, COLOR_TEXT)
        average_score_text = self.font.render(f"Average Score: {average_score:.2f}", True, COLOR_TEXT)

        self.window.blit(runs_text, (WIDTH + 10, 80))
        self.window.blit(highest_score_text, (WIDTH + 10, 100))
        self.window.blit(last_score_text, (WIDTH + 10, 120))
        self.window.blit(average_score_text, (WIDTH + 10, 140))

        # Display the event log
        y_offset = 160
        for log in self.logs:
            log_text = self.font.render(log, True, COLOR_TEXT)
            self.window.blit(log_text, (WIDTH + 10, y_offset))
            y_offset += 20

        # Display pause messages
        if self.paused:
            pause_text = (
                self.font.render("Press any key to restart", True, COLOR_TEXT)
                if self.game_over else
                self.font.render("Use W A S D or Arrow Keys to start", True, COLOR_TEXT)
            )
            self.window.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2))

        # Update the display
        pygame.display.flip()

    def run(self):
        print("Starting game loop...")
        try:
            while self.running:
                self.handle_input()
                self.update()
                self.render()

                if self.mode == LEARNING_MODE and self.game_over:
                    self.end_game()

                self.clock.tick(SNAKE_SPEED)

            # Wait for user input before closing
            if (self.automate):
                print("Automation completed. Press any key or click to close.")
                self.wait_for_close()

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            pygame.quit()
            if self.mode == LEARNING_MODE:
                self.learning_model.save_model()

    def wait_for_close(self):
        """Wait for the user to press a key or click before closing."""
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                elif event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
                    waiting = False
            self.render()

