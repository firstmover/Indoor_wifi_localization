import platform
PLATFORM = platform.system()
import sys
reload(sys)
# pity for windows
if PLATFORM == "Windows":
    sys.setdefaultencoding('gbk')
else:
    sys.setdefaultencoding('utf-8')

import numpy as np
from data_process import plot
import matplotlib.pyplot as plt

def plot_pred(train_ds, test_ds, pred, title=None):
    fig = plot(train_ds.pos, color="b")
    gt_mark = ["gt{0}_({1:.2f},{2:.2f})".format(i, test_ds.pos[i][0], test_ds.pos[i][1]) \
                                  for i in range(len(test_ds.pos))]
    pred_mark = ["pred{0}_({1:.2f},{2:.2f})".format(i, pred[i][0], pred[i][1]) \
                                    for i in range(len(pred))]
    fig = plot(test_ds.pos, fig=fig, color="y", mark=gt_mark) 
    fig = plot(pred, fig=fig, color="r", mark=pred_mark) 
    if not title is None:
        plt.title(title)
    plt.xlabel("x")
    plt.ylabel("y")
    return fig

class kNN(object):
    """
    k nearest-neighbour matching algorithm 
    """
    def __init__(self, k, train_ds):
        self.k = k
        self.train_ds = train_ds

    def __call__(self, test_ds):
        coords = np.zeros([test_ds.pos_num, 2], dtype=np.float32)
        for idx, vector in enumerate(test_ds.ndary):
            coords[idx] = self._locate(vector)
        
        return coords

    def _locate(self, vector):
        """
        internal locating function for one vector
        """
        ndary = self.train_ds.ndary
        dis_lst = [(np.linalg.norm(vector - ndary[i]), i) for i in range(self.train_ds.pos_num)]
        # sort using distance
        dis_lst.sort(key=lambda tup: tup[0])
        # NOTE: weight proportional to 1/distance
        kweight = map(lambda tup: 1./(tup[0]+10e-5), dis_lst[0:self.k])
        kidx = map(lambda tup: tup[1], dis_lst[0:self.k])
        kcoords = map(lambda idx: self.train_ds.pos[idx], kidx)
        # calculate the coordinates (x, y) using weighted sum
        weight_sum = sum(kweight)
        kweight = map(lambda weight: weight / weight_sum, kweight)
        coord = np.zeros([2], dtype=np.float32)
        for i in range(self.k):
            coord = coord + kcoords[i] * kweight[i]

        return coord
        
if __name__ == "__main__":
    # test, DO NOT run this
    assert len(sys.argv) == 3
    from dataset import Dataset
    with open(sys.argv[1], "r") as f:
        lines = [l.strip() for l in f.readlines()]
    ds = Dataset(lines)
    locater = kNN(int(sys.argv[2]), ds)
    print(locater(ds))
    
                
        

                
        
    
