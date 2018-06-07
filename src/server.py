import os
import socket
import json

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
            data = json.loads(data)
            vec = [data[ap] for ap in self.train_ds.aps]
            pred_pos = self.get_pred_coord(vec)
            ret_dict = {'x': pred_pos[0], 'y': pred_pos[1]}
            s.sendto(json.dumps(ret_dict), addr)

        s.close()


def pseudo_client():
    address = ('127.0.0.1', 31500)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    test_ds = prepare_dataset("../data/val.txt", 'median')
    data_dict = []

    while True:
        s.sendto(data_dict, address)

    s.close()


def main():
    server = Server("../data/train.txt", "4NN")
    server.listen_and_response()


if __name__ == "__main__":
    main()
