from typing import List

import matplotlib.pyplot as plt

import mgrs.sig_mgr as sig_mgr
from domain.sigfeatures import SignalPoint, ChangePoint, Labels, TimeInterval


def plot_sig(entries: List[SignalPoint], chg_pts: List[ChangePoint], with_pred=False):
    plt.figure(figsize=(20, 10))
    plt.xlabel('t [s]', fontsize=24)
    plt.ylabel('F [%]', fontsize=24)
    plt.xticks(fontsize=23)
    plt.yticks(fontsize=23)
    plt.grid(linestyle="--")
    x = list(map(lambda e: e.timestamp, entries))
    y_max = list(map(lambda e: e.value, entries))
    y_min = [0] * len(y_max)
    plt.plot(x, y_max, 'k.', label='sensor readings')
    plt.vlines(x, y_min, y_max, 'lightgray')

    colors = ['turquoise', 'tomato']
    labels = []
    for (index, pt) in enumerate(chg_pts):
        color = colors[0] if pt.event == Labels.STARTED else colors[1]
        items = list(filter(lambda e: pt.dt.t_min <= e.timestamp <= pt.dt.t_max, entries))
        x = list(map(lambda i: i.timestamp, items))
        y = list(map(lambda i: i.value, items))
        if pt.event not in labels:
            plt.vlines(x, [0] * len(y), [max(y)] * len(y), color=color, label=pt.event)
            labels.append(pt.event)
        else:
            plt.vlines(x, [0] * len(y), [max(y)] * len(y), color=color)
    plt.legend(fontsize=15)
    plt.show()
