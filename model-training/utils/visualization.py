import matplotlib.pyplot as plt


def plot_predictions(labels, predictions, timestamps):
    """
    Plots the labels and predictions against timestamps.

    :param labels: numpy array containing true labels.
    :param predictions: numpy array containing predicted labels.
    :param timestamps: numpy array containing timestamps.
    """
    fig, ax = plt.subplots()
    ax.plot(timestamps, labels, label="True Labels")
    ax.plot(timestamps, predictions, "x", label="Predictions")
    ax.set_xlabel("Time")
    ax.set_ylabel("Close")
    ax.legend()
    plt.show()
