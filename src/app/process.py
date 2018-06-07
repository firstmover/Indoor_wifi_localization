import sys
import numpy as np

def data_mean(data_lst):
    if len(data_lst) == 0:
        return []
    return [float(sum(data_lst)) / len(data_lst)]

def data_max(data_lst):
    if len(data_lst) == 0:
        return []
    return [max(data_lst)]

def data_min(data_lst):
    if len(data_lst) == 0:
        return []
    return [min(data_lst)]

def data_median(data_lst):
    if len(data_lst) == 0:
        return []
    return [np.median(data_lst)]

def data_std(data_lst):
    if len(data_lst) == 0:
        return []
    return [np.std(data_lst)]
