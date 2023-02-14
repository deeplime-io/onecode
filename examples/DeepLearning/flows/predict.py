
# This file is your entry point:
# - add you Python files and folder inside this 'flows' folder
# - add your imports
# - just don't change the name of the function 'run()' nor this filename ('deeplearning.py')
#   and everything is gonna be ok.
#
# Remember: everything is gonna be ok in the end: if it's not ok, it's not the end.
# Alternatively, contact us at support@deeplime.io
import os

import joblib
from tensorflow import keras

from onecode import Logger, Project, csv_output, csv_reader


def run():
    df = csv_reader('data_to_predict', 'winequality-red.csv')

    Logger.info('Loading dataset')
    with open(Project().get_output_path('columns.txt')) as f:
        input_cols = f.read().split('|')

    X = df[input_cols]

    Logger.info('Preparing dataset & Loading trained model')
    scaler_file = Project().get_output_path('scaler.bin')
    if os.path.exists(scaler_file):
        scaler = joblib.load(scaler_file)
        X = scaler.transform(X)

    model = keras.models.load_model(Project().get_output_path('saved_model'))

    Logger.info("Predicting...")
    y = model.predict(X)

    Logger.info("Done!")
    df['PREDICTED'] = y
    df.to_csv(csv_output('predicted', 'predicted.csv'))
