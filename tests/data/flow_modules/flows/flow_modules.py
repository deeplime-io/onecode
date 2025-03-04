import onecode
import time

import pandas as pd
import sklearn
import matplotlib.pyplot as plt


def run():
    onecode.Logger.info(f"Current time: {time.time()}")
    pd.read_csv("blabla.csv")
    plt.show()
