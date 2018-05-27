import os
import sys
import json
import argparse
import numpy as np
from dataset import *
from method import *
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description="localization algorithm")
parser.add_argument("--train", type=str, required=True, help="training data list, NOTE the file format must be json string, one sample per line,\
                                                              see data/train.txt and data/test.txt for reference")
parser.add_argument("--test", type=str, required=True, help="testing data list, NOTE as above")
parser.add_argument("--method", type=str, default="1NN", help="matching method/algorithm selection(default: 1NN)\
                    \n\txNN: nearest-neighbour using mean rssi, x is a integer indicating k in kNN\n\tTBD")
parser.add_argument("--signal", type=str, default="mean", help="signal type used for matching(default: mean)\
                    \n\tmean: average value of RSSI sequence\n\tmedian: median value of RSSI sequence\
                    \n\tmax: max value of RSSI sequence\n\tmin: min value of RSSI sequence\
                    \n\tstd: standard deviation value of RSSI sequence\n\traw: raw RSSI sequence")

def main():
    args = parser.parse_args()
    f = open(args.train, "r")
    train_lines = [l.strip() for l in f.readlines()]
    f.close()
    f = open(args.test, "r")
    test_lines = [l.strip() for l in f.readlines()]
    f.close()

    train_ds = Dataset(train_lines)
    test_ds = Dataset(test_lines)
    if args.signal == "mean":
        train_ds = train_ds.mean()
        test_ds = test_ds.mean()
    elif args.signal == "median":
        train_ds = train_ds.median()
        test_ds = test_ds.median()
    elif args.signal == "max":
        train_ds = train_ds.max()
        test_ds = test_ds.max()
    elif args.signal == "min":
        train_ds = train_ds.min()
        test_ds = test_ds.min()
    elif args.signal == "std":
        train_ds = train_ds.std()
        test_ds = test_ds.std()
    elif args.siganl == "raw":
        pass
    else:
        raise Exception("unknown signal {}, use -h for details".format(args.signal))
        sys.exit()

    if args.method.find("NN"):
        # kNN
        k = int(args.method[0:-2])
        locater = kNN(k, train_ds)
    else:
        raise Exception("unknown method {}, use -h for details".format(args.method))
        sys.exit()

    true_coords = test_ds.pos
    coords = locater(test_ds)
    print("True coords")
    print(true_coords)
    print("Pred coords")
    print(coords)
    fig = plot_pred(train_ds, test_ds, coords, "data points prediciton using {}".format(args.method))
    fig.show()
    while 1:
        c = raw_input("save or not?[Y/N]")
        if c == "Y":
            fig.savefig("tem.png")
            break
        elif c == "N":
            break
        else:
            print("invalid input {}".format(c))

if __name__ == "__main__":
    main()

    




