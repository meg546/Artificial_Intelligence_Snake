import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import json

def plot(scores, mean_scores=None, save_path="plot.png", title="Progress", window_size=10, show_ci=True):
    plt.figure(figsize=(10, 5))

    # Calculate rolling statistics
    rolling_mean = [np.mean(scores[max(0, i - window_size):i + 1]) for i in range(len(scores))]
    rolling_std = [np.std(scores[max(0, i - window_size):i + 1]) for i in range(len(scores))]
    rolling_se = [std / np.sqrt(min(i + 1, window_size)) for i, std in enumerate(rolling_std)]

    # Plot raw scores
    plt.plot(scores, label="Score", color="blue", alpha=0.7)

    # Plot rolling mean
    plt.plot(rolling_mean, label="Rolling Mean", color="red", linewidth=2)

    # Add confidence intervals or error bars
    if show_ci:
        ci_upper = [m + 1.96 * se for m, se in zip(rolling_mean, rolling_se)]
        ci_lower = [m - 1.96 * se for m, se in zip(rolling_mean, rolling_se)]
        plt.fill_between(range(len(scores)), ci_lower, ci_upper, color="red", alpha=0.2, label="95% CI")
    else:
        plt.errorbar(
            range(len(scores)), rolling_mean, yerr=rolling_std, fmt='o', color="gray", alpha=0.5, label="Error Bars"
        )

    # Add labels, title, legend, and grid
    plt.xlabel("Games")
    plt.ylabel("Score")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Save and display the plot
    plt.savefig(save_path)
    print(f"Plot saved as {save_path}.")
    plt.show()


def plot_data(json_file, title, save_path="output_plot.png", window_size=100, show_ci=True):
    # Load data from JSON file
    with open(json_file, 'r') as f:
        data = json.load(f)

    df = pd.DataFrame(data)

    # Calculate rolling statistics
    df["rolling_mean_score"] = df["score"].rolling(window=window_size).mean()
    df["rolling_std"] = df["score"].rolling(window=window_size).std()
    df["rolling_se"] = df["rolling_std"] / np.sqrt(window_size)

    # Calculate confidence intervals
    df["ci_upper"] = df["rolling_mean_score"] + 1.96 * df["rolling_se"]
    df["ci_lower"] = df["rolling_mean_score"] - 1.96 * df["rolling_se"]

    # Plot raw scores
    plt.figure(figsize=(12, 8))
    plt.scatter(df["run"], df["score"], label="Raw Scores", color="blue", alpha=0.7, s=5)

    # Plot rolling mean
    plt.plot(df["run"], df["rolling_mean_score"], label="Rolling Avg (100 runs)", color="red", linewidth=2)

    # Add confidence intervals or error bars
    if show_ci:
        plt.fill_between(
            df["run"], df["ci_lower"], df["ci_upper"], color="red", alpha=0.2, label="95% CI"
        )
    else:
        plt.errorbar(
            df["run"], df["rolling_mean_score"], yerr=df["rolling_std"], fmt='o', color="gray", alpha=0.5, label="Error Bars"
        )

    # Add the median line
    median_score = df["score"].median()
    plt.axhline(median_score, color="orange", linestyle="--", label=f"Median Score ({median_score})")

    # Add labels, title, and legend
    plt.xlabel("Run")
    plt.ylabel("Score")
    plt.title(title)
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.7)

    # Save and display the plot
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
        print(f"Plot saved as {save_path}")
    plt.show()


def reset_automation_data():
    """Resets the JSON file to store data for the current automation."""
    current_automation_data = {"runs": []}  # Clear data structure
    with open("data/current_automation_data.json", "w") as file:
        json.dump(current_automation_data, file, indent=4)
    print("Automation data reset.")

def log_current_automation_data(current_run, score):
    """Log scores and run data for the current automation."""
    filename = "data/current_automation_data.json"
    try:
        # Load existing data
        with open(filename, "r") as file:
            current_automation_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Create new structure if file doesn't exist
        current_automation_data = {"runs": []}

    # Append the new run data
    run_info = {"run": current_run + 1, "score": score}
    current_automation_data["runs"].append(run_info)

    # Save updated data to the file
    with open(filename, "w") as file:
        json.dump(current_automation_data, file, indent=4)
    print(f"Logged run data for run #{current_run + 1}.")




if __name__ == "__main__":

    data = "data/normal_run_data.json"
    title = "Human Performance"
    save_path="data/Human_performance.png"
    window_size = 100
    ci = True

    plot_data(data, title, save_path, window_size, ci);
