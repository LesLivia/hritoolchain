import math
from typing import List

import matplotlib.pyplot as plt
import numpy as np


def f1(time: List[float]):
    values = [t ** 2 for t in time]
    return values


def f2(time: List[float]):
    values = [2 * (t ** 2) for t in time]
    return values


def der(values: List[float]):
    increments = [v - values[i - 1] for (i, v) in enumerate(values) if i > 0]
    return increments


plt.figure()

time = np.arange(0, 100, 0.01)
values1 = f1(time)
values2 = f2(time)

plt.plot(time, values1, time, values2)
plt.show()

plt.figure()
plt.plot(time[1:], der(values1), time[1:], der(values2))
plt.show()
