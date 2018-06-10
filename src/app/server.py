import os
import sys
sys.path.insert(0, "../locate")

import socket
import json
import numpy as np
import time
import argparse

from dataset import prepare_dataset
from method import CNN, kNN
from data_process import data_signal

#from IPython import embed
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--train", type=str, default="../../data/train.txt", \
                    help="training json format file path(default: ../../data/train.txt)")
parser.add_argument("-m", "--method", type=str, default="4NN", help="matching algorithm, only support kNN now,\
                    give xNN(x is a integer) indicates using kNN(k=x)(default: 4NN)")
parser.add_argument("-s", "--signal", type=str, default="median", help="signal type used for matching,\
                    should be median/mean/std/min/max(default: median)")
parser.add_argument("--ip", type=str, default="127.0.0.1", help="server ip address(default: 127.0.0.1)")
parser.add_argument("--port", type=int, default=12138, help="server port(default: 12138)")


class Server:
    def __init__(self, train_ds_path, method, signal, addr, model_path=None):
        # prepare training dataset
        self.train_ds = prepare_dataset(train_ds_path, signal)

        self.signal = signal

        # locater
        if method == "CNN":
            if model_path is None:
                raise ValueError("CNN model path should be provided.")
            self.locater = CNN(self.train_ds, model_path)
        elif method.find("NN"):
            self.locater = kNN(int(method[0:-2]), self.train_ds)
        else:
            raise ValueError("invalid method.")

        self.addr = addr

        self.ap_position = {
            "Xiaomi_8334": [0.5, 0],
            "Xiaomi_3336": [1, 0.5],
            "Xiaomi_B84D": [0.5, 1],
            "Xiaomi_8334_5G": [0.5, 0],
            "Xiaomi_3336_5G": [1, 0.5],
            "Xiaomi_B84D_5G": [0.5, 1],

            }
        print("Server starting at {} with udp...".format(self.addr))
        

    def listen_and_response(self):
        # server listening to request.

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(self.addr)

        while True:
            data, addr = s.recvfrom(2048)
            data = json.loads(data.decode()) 
            print("recieved {}: {}".format(addr, data))
            # client require ap names ans positions. 
            if len(list(data.keys())) == 1:
                time.sleep(5)
                s.sendto(json.dumps(self.ap_position).encode(), addr)
                print("sending ap positions.")
            else:
                vec = [data[ap] for ap in self.train_ds.aps]
                match_len = True
                for i in vec:
                    if len(i) != len(vec[0]):
                        match_len = False
                if not match_len:
                    s.sendto(json.dumps({'x': 0, 'y': 0}).encode(), addr)
                    continue 
                vec = np.asarray(vec)
                vec = vec.reshape((1, vec.shape[0], vec.shape[1]))
                pred_pos = self.locater(vec)[0]
                ret_dict = {'x': float(pred_pos[0]) / 3.0, 'y': float(pred_pos[1]) / 8.0}
                print("sending {}: {}".format(addr, ret_dict))
                s.sendto(json.dumps(ret_dict).encode(), addr)

        s.close()

def main():
    # server = Server("../data/train.txt", "CNN", 'raw', "../cnn_data/ckpt/euclid_loss/model_epoch5000.ckpt")
    args = parser.parse_args()
    server = Server(args.train, args.method, args.signal, (args.ip, args.port))
    server.listen_and_response()
    return
    from dataset import prepare_dataset
    from method import kNN
    train_ds = prepare_dataset("../data/train.txt", 'median')
    test_ds = prepare_dataset("../data/val.txt", 'median')
    locater = kNN(4, train_ds)
    print("result: {}".format(locater(test_ds.ndary)))


if __name__ == "__main__":
    main()
