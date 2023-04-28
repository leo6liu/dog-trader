import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt


# https://www.tensorflow.org/tutorials/structured_data/time_series#data_windowing
class WindowGenerator:
    def __init__(self, input_width, label_width, shift, data, label_columns):
        # Store the raw data.
        self.data = data

        # Work out the label column indices.
        self.label_columns = label_columns
        self.label_columns_indices = {name: i for i, name in enumerate(label_columns)}

        self.column_indices = {name: i for i, name in enumerate(data.columns)}

        # Work out the window parameters.
        self.input_width = input_width
        self.label_width = label_width
        self.shift = shift

        self.total_window_size = input_width + shift

        self.input_slice = slice(0, input_width)
        self.input_indices = np.arange(self.total_window_size)[self.input_slice]

        self.label_start = self.total_window_size - self.label_width
        self.labels_slice = slice(self.label_start, None)
        self.label_indices = np.arange(self.total_window_size)[self.labels_slice]

    def __repr__(self):
        return "\n".join(
            [
                f"Total window size: {self.total_window_size}",
                f"Input indices: {self.input_indices}",
                f"Label indices: {self.label_indices}",
                f"Label column name(s): {self.label_columns}",
            ]
        )

    def split_windows(self, windows):
        """
        Parameters
        ----------
        windows : 3DArray
            [windows, minutes, columns]
        """
        inputs = windows[:, self.input_slice, :]
        labels = windows[:, self.labels_slice, :]

        labels = tf.stack(
            [labels[:, :, self.column_indices[name]] for name in self.label_columns],
            axis=-1,
        )

        # Slicing doesn't preserve static shape information, so set the shapes
        # manually. This way the `tf.data.Datasets` are easier to inspect.
        inputs.set_shape([None, self.input_width, None])
        labels.set_shape([None, self.label_width, None])

        return inputs, labels

    def plot(self, inputs, labels, plot_col, model=None, max_subplots=3):
        """
        Plots inputs and labels of a single column for each window.

        Parameters
        ----------
        inputs : 3DArray
            [windows, minutes, columns]
        labels : 3DArray
            [windows, minutes, columns]
        plot_col : str
            The name of the column to plot.
        """

        plt.figure(figsize=(8, 4))

        plot_col_index = self.column_indices[plot_col]

        # calculate number of windows to plot
        max_n = min(max_subplots, len(inputs))

        # plot each window
        for n in range(max_n):
            plt.subplot(max_n, 1, n + 1)
            plt.ylabel(f"{plot_col}")

            # plot input points
            plt.plot(
                self.input_indices,
                inputs[n, :, plot_col_index],
                label="Inputs",
                marker=".",
                zorder=-10,
            )

            # plot label point
            label_col_index = self.label_columns_indices.get(plot_col, None)
            plt.scatter(
                self.label_indices,
                labels[n, :, label_col_index],
                edgecolors="k",
                label="Labels",
                c="#2ca02c",
                s=64,
            )

            if model is not None:
                predictions = model(inputs)
                plt.scatter(
                    self.label_indices,
                    predictions[n, :, label_col_index],
                    marker="X",
                    edgecolors="k",
                    label="Predictions",
                    c="#ff7f0e",
                    s=64,
                )

            # show legend on first subplot
            if n == 0:
                plt.legend()

        # hard coded x-axis label
        plt.xlabel("Time (minutes)")

    def make_dataset(self, batch_size):
        data = np.array(self.data, dtype=np.float32)
        ds = tf.keras.utils.timeseries_dataset_from_array(
            data=data,
            targets=None,
            sequence_length=self.total_window_size,
            sequence_stride=1,
            shuffle=False,
            batch_size=batch_size,
        )

        ds = ds.map(self.split_windows)

        return ds
