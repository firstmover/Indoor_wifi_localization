import os
import socket
import json
import numpy as np

from dataset import prepare_dataset
from method import CNN, kNN
from data_process import data_signal


class Server:
    def __init__(self, train_ds_path, method, model_path=None):
        # prepare training dataset
        self.train_ds = prepare_dataset(train_ds_path, 'median')

        # locater
        if method == "CNN":
            if model_path is None:
                raise ValueError("CNN model path should be provided.")
            self.locater = CNN(self.train_ds, model_path)
        elif method.find("NN"):
            self.locater = kNN(int(method[0:-2]), self.train_ds)
        else:
            raise ValueError("invalid method.")

        self.addr = ('127.0.0.1', 31500)

    def get_pred_coord(self, x):
        # get pred pos, x include one vector.
        pred_pos = self.locater(data_signal['median']([x]))[0]
        return pred_pos

    def listen_and_response(self):
        # server listening to request.

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(self.addr)

        while True:
            data, addr = s.recvfrom(2048)
            print("recieved {}: {}".format(addr, data))
            data = json.loads(data.decode())
            vec = np.asarray([data[ap] for ap in self.train_ds.aps])
            # pred_pos = self.get_pred_coord(vec)
            print("vec: {}".format(vec))
            vec = vec.reshape((1, vec.shape[0], 1))
            pred_pos = self.locater(vec)[0]
            ret_dict = {'x': float(pred_pos[0]), 'y': float(pred_pos[1])}
            print("send {}: {}".format(addr, ret_dict))
            s.sendto(json.dumps(ret_dict).encode(), addr)

        s.close()


def pseudo_client():
    test_ds = prepare_dataset("../data/val.txt", 'median')

    address = ('127.0.0.1', 31500)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    for test_sample, pos in zip(test_ds.ndary, test_ds.pos):
        data_dict = {}
        for idx, ap in enumerate(test_ds.aps):
            data_dict[ap] = float(test_sample[idx][0])
        data_dict['tag'] = 'test'
        print("send {}: {}".format(address, data_dict))
        s.sendto(json.dumps(data_dict).encode(), address)
        rec_pos, addr = s.recvfrom(2048)
        print("recieved {}: {}".format(addr, rec_pos))
        rec_pos = rec_pos.decode()
        print("rec_pos: {}".format(rec_pos))

    s.close()


def main():
    server = Server("../data/train.txt", "4NN")
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
