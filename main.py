from src.game.game import Game

if __name__ == "__main__":
    game = Game(automate=True, max_runs=20)
    game.run()
