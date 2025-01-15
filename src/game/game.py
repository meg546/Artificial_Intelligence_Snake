import pygame
import json
from config.settings import * 
from src.ai.a_star import *
from src.ai.learning import DeepQLearningModel
from src.ai.ai_controller import * 
from src.game.snake import Snake
from src.game.food import Food
from src.game.board import Board
from src.ai.visualization import *

class Game:
    def __init__(self, automate=False, max_runs=1, testing=False, num_walls=0):
        pygame.init()
        self.window = pygame.display.set_mode((WIDTH + LOG_WIDTH, HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()

        # Automation setup
        self.automate = automate
        self.max_runs = max_runs
        self.testing = testing
        self.current_run = 0
        self.num_walls = num_walls

        self.idle_timer = 0
        self.max_idle_ticks = 2000  # Maximum ticks before ending the round due to inactivity
        
        self.learning_model = DeepQLearningModel(
            state_space_size=11,
            action_space_size=4,
            learning_rate=0.002,
            gamma=0.9
        )
        self.learning_model.load_model("model.pth")

        # Initialize score tracking for visualization graphing
        self.scores = []  # List to store scores for plotting
        self.mean_scores = []  # List to store mean scores

        # Initialize statistics and run data attributes
        self.normal_stats = {"runs": 0, "highest_score": 0, "total_score": 0, "last_score": 0}
        self.a_star_stats = {"runs": 0, "highest_score": 0, "total_score": 0, "last_score": 0}
        self.learning_stats = {"runs": 0, "highest_score": 0, "total_score": 0, "last_score": 0}
        self.testing_stats = {"runs": 0, "highest_score": 0, "total_score": 0, "last_score": 0}
        self.current_automation_stats = []  # List to store run and score for current automation
        self.run_data = {NORMAL_MODE: [], A_STAR_MODE: [], LEARNING_MODE: [], TESTING_MODE: []}

        # Load data from files
        self.load_statistics()
        self.load_run_data()

        # Set mode
        if self.testing:
            self.mode = TESTING_MODE
            print("Testing mode enabled.")
            self.automate = True  # Enable automation for testing
        else:
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

    def update_position_message(self):
        #Update the message showing the snake's current head position.
        head_pos_x, head_pos_y = self.snake.head_position()
        self.position_message = f"Snake Position: ({head_pos_x // TILE_SIZE}, {head_pos_y // TILE_SIZE})"

    def update_goal_position(self):
        #Update the message showing the current food's position.
        fruit_x, fruit_y = self.food.position
        self.goal_text = f"Goal Position: ({fruit_x // TILE_SIZE}, {fruit_y // TILE_SIZE})"

    def load_statistics(self):
        #Load statistics for each mode from separate JSON files in the data directory.
        for mode in [NORMAL_MODE, A_STAR_MODE, LEARNING_MODE, TESTING_MODE]:
            filename = f"data/{mode}_stats.json"
            try:
                with open(filename, "r") as file:
                    if mode == NORMAL_MODE:
                        self.normal_stats = json.load(file)
                    elif mode == A_STAR_MODE:
                        self.a_star_stats = json.load(file)
                    elif mode == LEARNING_MODE:
                        self.learning_stats = json.load(file)
                    elif mode == TESTING_MODE:
                        self.testing_stats = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError):
                print(f"{filename} not found or corrupted, using default values.")

    def save_statistics(self):
        #Save statistics for each mode to separate JSON files in the data directory.
        stats_files = {
            NORMAL_MODE: "data/normal_stats.json",
            A_STAR_MODE: "data/a_star_stats.json",
            LEARNING_MODE: "data/learning_stats.json",
            TESTING_MODE: "data/testing_stats.json",
        }

        for mode, filename in stats_files.items():
            data = (
                self.normal_stats if mode == NORMAL_MODE else
                self.a_star_stats if mode == A_STAR_MODE else
                self.learning_stats if mode == LEARNING_MODE else
                self.testing_stats
            )
            with open(filename, "w") as file:
                json.dump(data, file, indent=4)
        print("Statistics saved to separate files in data directory.")

    def load_run_data(self):
        #Load run data for each mode from separate JSON files in the data directory.
        for mode in [NORMAL_MODE, A_STAR_MODE, LEARNING_MODE]:
            filename = f"data/{mode}_run_data.json"
            try:
                with open(filename, "r") as file:
                    self.run_data[mode] = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError):
                print(f"{filename} not found or corrupted. Resetting run data for {mode}.")
                self.run_data[mode] = []

    def save_run_data(self):
        #Save run data for the active mode to its JSON file.
        filename = f"data/{self.mode}_run_data.json"
        try:
            with open(filename, "w") as file:
                json.dump(self.run_data[self.mode], file, indent=4)
            print(f"Run data saved to {filename}.")
        except Exception as e:
            print(f"Error saving run data to {filename}: {e}")

    def save_current_automation_stats(self):
        if self.mode == LEARNING_MODE:
            return  # Do not save current stats for learning mode

        filename = f"data/{self.mode}_current_automation.json"
        try:
            with open(filename, "w") as file:
                json.dump(self.current_automation_stats, file, indent=4)
            print(f"Current automation stats saved to {filename}.")
        except Exception as e:
            print(f"Error saving current automation stats: {e}")




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
        self.idle_timer = 0  # Reset idle timer
        self.board = Board(WIDTH, HEIGHT, TILE_SIZE, num_walls=self.num_walls)
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
        if self.game_over:  # If already game over, skip
            return
        
        print(f"Ending game #{self.current_run + 1}.")
        
        # Determine the stats based on the mode
        stats = (
            self.normal_stats if self.mode == NORMAL_MODE else
            self.a_star_stats if self.mode == A_STAR_MODE else
            self.learning_stats
        )
        
        # Update overall stats
        if stats:
            stats["runs"] += 1
            stats["last_score"] = self.score
            stats["total_score"] += self.score
            stats["highest_score"] = max(stats["highest_score"], self.score)

            # Update current automation stats (exclude learning mode)
            if self.mode != LEARNING_MODE and self.automate:
                self.current_automation_stats.append({
                    "run": self.current_run + 1,
                    "score": self.score
                })

        # Append the score to the scores list for the current automation
        self.scores.append(self.score)

        if self.mode == LEARNING_MODE and self.automate:
            self.learning_model.n_games += 1
            # Update mean score
            mean_score = sum(self.scores[-100:]) / min(len(self.scores), 100)
            self.mean_scores.append(mean_score)

            # Decay epsilon
            self.learning_model.decay_epsilon()
            print(f"Epsilon decayed to {self.learning_model.epsilon:.4f}")
        
        elif self.mode == TESTING_MODE:
            # Log testing progress
            print(f"Testing mode: Game {self.current_run + 1} completed with score: {self.score}")

        # Log run data (run number and score)
        run_info = {"run": stats["runs"], "score": self.score}
        self.run_data[self.mode].append(run_info)
        self.save_run_data()
        self.save_statistics()

        if self.automate:
            self.current_run += 1
            if self.current_run < self.max_runs:
                self.reset_game()
            else:
                print(f"[AUTOMATION] Completed {self.max_runs} runs.")
                self.save_current_automation_stats()
                if self.mode == LEARNING_MODE:
                    plot(
                        self.scores,
                        self.mean_scores,
                        save_path="learning_plot.png",
                        title="Learning Model Progress"
                    )
                self.running = False
        else:
            # Non-automated behavior: Pause and wait for user input
            self.game_over = True
            self.paused = True
            print("Game over. Press any key to restart.")


    def update(self):
        # Prevent any updates if the game is over or paused
        if self.paused or self.game_over:
            return
        
        self.idle_timer += 1

        if self.idle_timer > self.max_idle_ticks:
            print(f"Ending game due to inactivity. Idle timer exceeded {self.max_idle_ticks} ticks.")
            self.end_game()
            return

        if self.mode == LEARNING_MODE:
            if self.automate:
                # Automated learning logic
                current_state = self.learning_model.get_state(self.snake, self.food, self.board)
                action = self.learning_model.choose_action(current_state)
                self.snake.change_direction(["UP", "DOWN", "LEFT", "RIGHT"][action])
                self.snake.move()

                reward = self.learning_model.get_reward(self.snake, self.food, self.board)
                next_state = self.learning_model.get_state(self.snake, self.food, self.board)

                self.learning_model.train_step([current_state], [action], [reward], [next_state], [self.game_over])
                self.learning_model.remember(current_state, action, reward, next_state, self.game_over)

                if self.snake.head_position() == self.food.position:
                    self.score += 1
                    self.snake.grow()
                    self.food.position = self.food.spawn(self.snake.body)
                elif not self.board.is_within_bounds(self.snake.head_position()) or self.snake.has_collision(self.board):
                    self.end_game()

            else:
                # Non-automated behavior
                current_state = self.learning_model.get_state(self.snake, self.food, self.board)
                action = self.learning_model.choose_action(current_state, epsilon=0.0)  # Exploit only
                self.snake.change_direction(["UP", "DOWN", "LEFT", "RIGHT"][action])
                self.snake.move()

                if not self.board.is_within_bounds(self.snake.head_position()) or self.snake.has_collision(self.board):
                    if not self.game_over:  # Avoid multiple calls
                        self.end_game()
                elif self.snake.head_position() == self.food.position:
                    self.score += 1
                    self.snake.grow()
                    self.food.position = self.food.spawn(self.snake.body)
                    self.idle_timer = 0

        elif self.mode == A_STAR_MODE:
            a_star_move(self.snake, self.food, self.board)

        elif self.mode == TESTING_MODE:
            current_state = self.learning_model.get_state(self.snake, self.food, self.board)
            action = self.learning_model.choose_action(current_state, epsilon=0.0)  # No exploration
            self.snake.change_direction(["UP", "DOWN", "LEFT", "RIGHT"][action])
            self.snake.move()

            if not self.board.is_within_bounds(self.snake.head_position()) or self.snake.has_collision(self.board):
                self.end_game()
            if self.snake.head_position() == self.food.position:
                self.score += 1
                self.snake.grow()
                self.food.position = self.food.spawn(self.snake.body)

        else:  # NORMAL_MODE
            self.snake.move()

        # Update display messages
        self.update_position_message()
        self.update_goal_position()

        # Collision handling for all modes
        if self.snake.head_position() == self.food.position:
            self.score += 1
            self.snake.grow()
            self.food.position = self.food.spawn(self.snake.body)
        elif not self.board.is_within_bounds(self.snake.head_position()) or self.snake.has_collision(self.board):
            self.end_game()


    def render(self):
        # Draw the game board
        for row in range(0, HEIGHT, TILE_SIZE):
            for col in range(0, WIDTH, TILE_SIZE):
                color = COLOR_LIGHT if (row // TILE_SIZE + col // TILE_SIZE) % 2 == 0 else COLOR_DARK
                pygame.draw.rect(self.window, color, (col, row, TILE_SIZE, TILE_SIZE))
        
        #draw walls
        self.board.draw(self.window)

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
        #Wait for the user to press a key or click before closing.
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                elif event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
                    waiting = False
            self.render()

    def test_model(self, test_runs=100):
        print(f"Starting testing phase with {test_runs} runs...")

        # Switch the model to evaluation mode
        self.learning_model.model.eval()

        # Disable exploration (epsilon = 0)
        test_epsilon = 0.0

        # Initialize metrics
        total_score = 0
        max_score = 0
        scores = []

        for test_run in range(test_runs):
            print(f"Testing game #{test_run + 1}...")
            self.reset_game()

            while not self.game_over:
                # Get the current state
                current_state = self.learning_model.get_state(self.snake, self.food, self.board)
                # Choose the best action (exploit)
                action = self.learning_model.choose_action(current_state, epsilon=test_epsilon)
                # Perform the action
                self.snake.change_direction(["UP", "DOWN", "LEFT", "RIGHT"][action])
                self.snake.move()

                # Check collisions or food
                if not self.board.is_within_bounds(self.snake.head_position()) or self.snake.has_collision(self.board):
                    break  # Game over
                if self.snake.head_position() == self.food.position:
                    self.score += 1
                    self.snake.grow()
                    self.food.position = self.food.spawn(self.snake.body)

            # Update metrics
            total_score += self.score
            max_score = max(max_score, self.score)
            scores.append(self.score)

            print(f"Game #{test_run + 1} ended with score: {self.score}")

        # Final metrics
        average_score = total_score / test_runs
        print(f"Testing completed. Average Score: {average_score:.2f}, Max Score: {max_score}")

        return {
            "average_score": average_score,
            "max_score": max_score,
            "scores": scores
        }

