import os

from dataset import Dataset
from method import CNN, kNN
from data_process import data_signal


class Server:
    def __init__(self, train_ds_path, method, model_path=None):
        # prepare training dataset
        with open(train_ds_path, 'r') as f:
            lines = [l.strip() for l in f.readlines()]
        train_ds = Dataset(lines).get_signal('mean')

        # locater
        if method == "CNN":
            if model_path is None:
                raise ValueError("CNN model path should be provided.")
            self.locater = CNN(train_ds, model_path)
        elif method.find("NN"):
            self.locater = kNN(int(method[0:-2]), train_ds)
        else:
            raise ValueError("invalid method.")

    def get_pred_coord(self, x):
        return self.locater(data_signal['mean'](x))

    def listen_and_response(self):
        # server listening to request.
        pass


def main():
    pass


if __name__ == "__main__":
    main()
