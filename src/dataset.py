import sys
import copy
import numpy as np
from data_process import *
from utils import str2dict, dict2str

def dicts2ndarray(data_dicts):
    """
    convert list of dicts to ndarray of type np.float32
    """
    data_len = 0
    # NEVER make any assumption about the order of .keys() return
    aps = data_dicts[0].keys()
    aps.remove("tag")
    aps.sort()
    data_num = len(data_dicts)
    data_len = len(data_dicts[0][aps[0]])

    ndary = np.zeros([data_num, len(aps), data_len], dtype=np.float32)
    for idx, d in enumerate(data_dicts):
        for aidx, ap in enumerate(aps):
            ndary[idx, aidx, :] = d[ap]

    return ndary

class Dataset():
    """
    class for storing data points
    """
    def __init__(self, raw_data):
        """
        raw data: list of json string read from raw file
        """
        self.data_dicts = map(str2dict, raw_data)
        self.aps = self.data_dicts[0].keys()
        self.aps.remove("tag")
        self.aps.sort()
        self.ap_num = len(self.aps)
        self.tags = map(lambda x:x['tag'], self.data_dicts)

        # 2-d coordinates (x, y)
        self.pos = np.zeros([len(self.tags), 2], dtype=np.float32)
        for idx, tag in enumerate(self.tags):
            self.pos[idx] = map(float, tag.split("-"))
        self.pos_num = self.tag_num = len(self.tags)

        # length of RSSIs of every ap
        # NOTE: it's ok to have different RSSIs length for different ap,
        # but all RSSIs of the same ap should keep the same length
        self.data_len = {}
        self.total_data_len = 0
        for ap in self.aps:
            self.data_len[ap] = len(self.data_dicts[0][ap])
            self.total_data_len += self.data_len[ap]
        self.ndary = dicts2ndarray(self.data_dicts)

    def process(self, method):
        """
        process raw data according to method given
        return: Dataset with processed data as internal data
        method: function takes list of data(rssi) and output a list of processed data
        """
        process_dicts = []
        for d in self.data_dicts:
            dd = copy.deepcopy(d)
            for ap in self.aps:
                dd[ap] = method(d[ap])
            process_dicts.append(dict2str(dd))

        #print(process_dicts)
        #print(type(process_dicts[0]))
        return Dataset(process_dicts)     
    
    # some instances of process
    def mean(self):
        return self.process(data_mean)

    def max(self):
        return self.process(data_max)

    def min(self):
        return self.process(data_min)

    def median(self):
        return self.process(data_median)

    def std(self):
        return self.process(data_std)

if __name__ == "__main__":
    # test, DO NOT run this
    assert len(sys.argv) == 2
    with open(sys.argv[1], "r") as f:
        lines = [l.strip() for l in f.readlines()]
    ds = Dataset(lines).median()
    print(lines)
    print(ds.data_dicts)
    print(ds.aps)
    print(ds.tags)
    print(ds.pos)
    print(ds.ndary)


    




