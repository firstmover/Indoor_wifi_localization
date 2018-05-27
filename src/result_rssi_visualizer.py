#!/usr/bin/env python3
import os 
import matplotlib.pyplot as plt
import numpy as np
import json 
from IPython import embed 

def visualize_heatmap(data, save_path):
    plt.imshow(data, cmap='hot', interpolation='bilinear')
    plt.savefig(save_path)

def load_data(path):
    with open(path, 'r') as f:
        data = f.readlines()
    data = [json.loads(i) for i in data if len(i) > 0]
    return data

def main():
    data = load_data('../data/result.txt')
    ssids = [i for i in list(data[0].keys()) if i != 'tag']
    ssid2rssi = {key:np.zeros((4, 8)) for key in ssids}
    for d in data:
        if d['tag'] == 'test' or len(d['tag'].split('-')) != 2:
            continue 
        x, y = d['tag'].split('-')
        x, y = int(x), int(y)
        for s in ssids:
            rssi = d[s]
            ssid2rssi[s][x][y] = np.mean(np.asarray(d[s]))

    for k, v in ssid2rssi.items():
        visualize_heatmap(v, os.path.join('../figures', "rssi_heatmap_{}.png".format(k)))

if __name__ == "__main__":
    main()

