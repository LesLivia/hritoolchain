from typing import List

import matplotlib.pyplot as plt

from domain.hafeatures import SignalPoint, ChangePoint, Labels


def plot_sig(entries: List[SignalPoint], chg_pts: List[ChangePoint]):
    fig = plt.figure(figsize=(20, 10))
    plt.xlabel('t [s]', fontsize=24)
    plt.ylabel('F [%]', fontsize=24)
    plt.xticks(fontsize=23)
    plt.yticks(fontsize=23)
    plt.grid(linestyle="--")
    x = list(map(lambda e: e.timestamp, entries))
    y_max = list(map(lambda e: e.value, entries))
    y_min = [0] * len(y_max)
    plt.plot(x, y_max, 'k.', label='sensor readings')
    plt.vlines(x, y_min, y_max, 'gray')

    colors = ['tomato', 'turquoise']
    labels = []
    for pt in chg_pts:
        color = colors[0] if pt.event == Labels.STARTED else colors[1]
        items = list(filter(lambda e: pt.dt.t_min <= e.timestamp <= pt.dt.t_max, entries))
        x = list(map(lambda i: i.timestamp, items))
        y = list(map(lambda i: i.value, items))
        if pt.event not in labels:
            plt.vlines(x, [0] * len(y), [1.0] * len(y), color=color, label=pt.event)
            labels.append(pt.event)
        else:
            plt.vlines(x, [0] * len(y), [1.0] * len(y), color=color)

    plt.legend(fontsize=15)
    plt.show()
