import numpy as np


def percent_round_int(percent, x):
    return np.round(percent * x).astype(int)
