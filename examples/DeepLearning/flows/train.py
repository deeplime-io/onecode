
# This file is your entry point:
# - add you Python files and folder inside this 'flows' folder
# - add your imports
# - just don't change the name of the function 'run()' nor this filename ('train.py')
#   and everything is gonna be ok.
#
# Remember: everything is gonna be ok in the end: if it's not ok, it's not the end.
# Alternatively, contact us at support@deeplime.io

import os

import joblib
import matplotlib.pyplot as plt
import numpy as np
from onecode_ext import neural_net_input
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow import keras

from onecode import (
    Logger,
    checkbox,
    csv_reader,
    dropdown,
    file_output,
    image_output,
    number_input,
    slider,
    text_output
)


class LogHistory(keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs={}):
        Logger.info(f"Epoch {epoch} - loss: {logs.get('loss')} | val loss: {logs.get('loss')}")


def run():
    df = csv_reader('dataset', 'winequality-red.csv')

    input_cols = dropdown(
        'input_cols',
        [
            "fixed acidity",
            "volatile acidity",
            "citric acid",
            "residual sugar",
            "chlorides",
            "free sulfur dioxide",
            "total sulfur dioxide",
            "density",
            "pH",
            "sulphates",
            "alcohol"
        ],
        options='$dataset$.columns',
        multiple=True
    )
    output_col = dropdown('output_col', "quality", options='$dataset$.columns')

    normalize = checkbox('Normalize?', True)
    categorical = checkbox('Is output categorical?', False)
    train_split = slider('train/test split', 0.7)

    number_input('n layers', 4, min=1, max=7, step=1)
    nn = neural_net_input(
        'Neural Net',
        [
            {"neurons": 32, "activation": "relu", "dropout": 0.2},
            {"neurons": 16, "activation": "tanh", "dropout": 0.1},
            {"neurons": 32, "activation": "relu", "dropout": 0.2},
            {"neurons": 16, "activation": "tanh", "dropout": 0.1},
        ],
        count='$n_layers$'
    )

    X = df[input_cols]
    y = df[output_col]

    scaler_file = file_output('scaler', 'scaler.bin')
    if os.path.exists(scaler_file):
        os.remove(scaler_file)

    if normalize:
        scaler = StandardScaler()
        X = scaler.fit_transform(X)
        Logger.info('Scaling...')
        Logger.info(f'Mean: {scaler.mean_}')
        joblib.dump(scaler, scaler_file, compress=True)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        train_size=train_split,
        random_state=4096,
        shuffle=True
    )

    layers = []
    for i, layer in enumerate(nn):
        # first layer must specify input shape
        extra_params = {"input_shape": (X_train.shape[-1],)} if i == 0 else {}

        layers.append(
            keras.layers.Dense(
                layer.get('neurons', 8),
                activation=layer.get('activation', 'relu'),
                **extra_params
            )
        )

        dropout = layer.get('dropout', 0.)
        if dropout > 0:
            layers.append(keras.layers.Dropout(dropout))

    n_out = int(np.max(y_train) + 1) if categorical else 1
    loss = keras.losses.SparseCategoricalCrossentropy(from_logits=True) if categorical else 'mse'
    metrics = 'accuracy' if categorical else 'mse'

    layers.append(keras.layers.Dense(n_out))

    model = keras.Sequential(layers)
    print(model.summary())

    model.compile(
        optimizer='adam',
        loss=loss,
        metrics=[metrics]
    )

    epochs = int(slider('Epochs', 55, min=10, max=100, step=1))

    Logger.info('Training...')
    history = model.fit(
        X_train,
        y_train,
        batch_size=2048,
        epochs=epochs,
        verbose=0,
        validation_data=(X_test, y_test),
        callbacks=[LogHistory()]
    )

    Logger.info('Training Done!')
    Logger.info('Saving data...')

    # summarize history for loss
    plt.figure()
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.savefig(image_output('loss', 'loss.png'))

    model.save(file_output('model', 'saved_model', tags=['Keras', 'Binary', 'Model']))

    with open(text_output('columns', 'columns.txt', label='Columns used for training'), 'w') as f:
        f.write('|'.join(input_cols))
