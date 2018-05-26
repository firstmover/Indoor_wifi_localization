import numpy as np

def data_mean(data_lst):
    return [float(sum(data_lst)) / len(data_lst)]

def data_max(data_lst):
    return [max(data_lst)]

def data_min(data_lst):
    return [min(data_lst)]

def data_median(data_lst):
    return [np.median(data_lst)]

def data_std(data_lst):
    return [np.std(data_lst)]

