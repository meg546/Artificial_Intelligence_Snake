from src.game.game import Game
from config.settings import *
import pygame

if __name__ == "__main__":
    try:
        testing = False  # Set to True to enable testing mode
        max_runs = 100   # Specify # runs
        automate = False  # Set to True to run max_runs automatically
        num_walls = 0 # # of walls in the scene

        game = Game(automate=automate, max_runs=max_runs, testing=testing, num_walls=num_walls)
        
        if automate:
            game.mode = A_STAR_MODE

        game.run()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        pygame.quit()

