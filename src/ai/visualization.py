import matplotlib.pyplot as plt

def plot(scores, mean_scores, save_path="learning_plot.png"):
    plt.figure(figsize=(10, 5))
    plt.plot(scores, label="Score")
    plt.plot(mean_scores, label="Mean Score")
    plt.xlabel("Games")
    plt.ylabel("Score")
    plt.title("Learning Progress")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(save_path)  # Save the plot to a file
    print(f"Plot saved as {save_path}.")
