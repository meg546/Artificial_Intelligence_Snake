import matplotlib.pyplot as plt

def plot(scores, mean_scores):
    plt.plot(scores, label='Score')
    plt.plot(mean_scores, label='Mean Score')
    plt.legend()
    plt.show()
