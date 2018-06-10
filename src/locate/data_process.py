import platform
import sys
import numpy as np
import matplotlib.pyplot as plt

PLATFORM = platform.system()
# pity for windows
'''
if PLATFORM == "Windows":
    reload(sys)
    sys.setdefaultencoding('gbk')
elif PLATFORM == "Darwin":
    pass
else:
    reload(sys)
    sys.setdefaultencoding('utf-8')
'''


data_signal = {
    "mean": lambda x: [float(sum(x)) / len(x)],
    'max': lambda x: [max(x)],
    'min': lambda x: [min(x)],
    'median': lambda x: [np.median(x)],
    'std': lambda x: [np.std(x)]
}


def plot(pos, fig=None, color=None, mark=None):
    """
    plot data points according to the positon given
    pos: array/list of numpy array of shape (2,),
         every element stands for a position of coordinate (x, y)
    fig: predefined figure to draw on, None means to create a new fig using plt.figure
    color: any compatible with plt color specification
    mark: list of string, used as text marker of every position
          None means no marker
    return: the figure drawn
    """
    if fig is None:
        fig = plt.figure()
    ax = fig.add_subplot(111)
    x = np.array([p[0] for p in pos])
    y = np.array([p[1] for p in pos])
    plt.scatter(x, y, c=color)

    if mark is not None:
        for idx, p in enumerate(pos):
            text = mark[idx]
            ax.annotate(text, xy=tuple(p), xytext=tuple(p + .1),
                        arrowprops=dict(arrowstyle="->", connectionstyle="arc3"))
    return fig
