import numpy as np

def directional_accuracy_rate(inputs, labels, predictions):
    """
    Calculates the rate at which the prediction and labels are in the same direction relative to inputs.

    Parameters
    ----------
    inputs : numpy array containing inputs
    labels : numpy array containing true labels.
    predictions : numpy array containing predicted labels.

    Returns
    -------
    - Rate at which the prediction and labels are in the same direction relative to inputs.
    """
    input_diff = labels - inputs
    pred_diff = predictions - inputs
    same_direction_count = np.sum(np.sign(input_diff) == np.sign(pred_diff))

    return same_direction_count / len(inputs)
