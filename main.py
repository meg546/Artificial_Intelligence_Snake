from src.game.game import Game
from config.settings import *
import pygame

if __name__ == "__main__":
    try:
        max_runs = 1000  # Specify the number of runs for automation
        automate = True  # Enable automation
        game = Game(automate=automate, max_runs=max_runs)

        # Force learning mode
        game.mode = A_STAR_MODE

        game.run()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        pygame.quit()
