#!/usr/bin/env python3
import os
import matplotlib.pyplot as plt
import numpy as np
import json
import argparse
#from IPython import embed
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file", type=str, default="rssi.txt", help="json format rssi file path(default: rssi.txt)")
parser.add_argument("-s", "--save_file", type=str, default="rssi_heatmap.png",\
                    help="rssi heatmap to be saved(default: rssi_heatmap.png")

def visualize_heatmap(data, save_path):
    plt.imshow(data, cmap='hot', interpolation='bilinear')
    plt.savefig(save_path)


def load_data(path):
    with open(path, 'r') as f:
        data = f.readlines()
    data = [json.loads(i) for i in data if len(i) > 0]
    return data


def main():
    args = parser.parse_args()
    data = load_data(args.file)
    ssids = [i for i in list(data[0].keys()) if i != 'tag']
    ssid2rssi = np.zeros((4, 8))
    for d in data:
        x, y = d['tag'].split('-')
        x, y = int(x), int(y)
        for s in ssids:
            ssid2rssi[x][y] += np.mean(np.asarray(d[s]))

    visualize_heatmap(ssid2rssi, args.save_file)


if __name__ == "__main__":
    main()
