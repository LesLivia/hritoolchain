from typing import List

import scipy.special as sci
import math
import numpy as np
import scipy.stats as stats
import random
import matplotlib.pyplot as plt


def get_theta_th(P_0: float, N: int, alpha: float = 0.05):
    for theta in range(0, N, 1):
        alpha_th = 0
        for K in range(theta, N, 1):
            binom = sci.binom(N, K)
            alpha_th += binom * (P_0 ** K) * ((1 - P_0) ** (N - K))
        if alpha_th <= alpha:
            print(alpha_th)
            return theta
    return None


def get_likelihood_ratio(x: List[float], y: List[float]):
    avg_x = sum(x) / len(x)
    avg_y = sum(y) / len(y)
    u = sum(x + y) / (len(x) + len(y))
    n = len(x)
    m = len(y)
    std_x = sum([(x_i - avg_x) ** 2 for x_i in x]) / n
    std_y = sum([(y_i - avg_y) ** 2 for y_i in y]) / m
    std_xu = sum([(x_i - u) ** 2 for x_i in x])
    std_yu = sum([(y_i - u) ** 2 for y_i in y])
    std_u = ((std_xu + std_yu) / (n + m)) ** ((n + m) / 2)

    lambda_mn = (std_x ** (n / 2) * std_y ** (m / 2)) / std_u
    return lambda_mn


P_0 = 0.05
N = 500

print("at least {} failures out of {} segments".format(get_theta_th(P_0, N), N))

# x = [361, 447, 401, 375, 434, 403, 393, 426, 406, 318, 467, 407, 427, 420, 477, 392, 430, 339, 410, 326]
# y = [380, 321, 366, 356, 283, 349, 402, 462, 356, 410, 329, 399, 350, 384, 316, 272, 345, 455, 360, 431]

# x = [4.23, 4.35, 4.05, 3.75, 4.41, 4.37, 4.01, 4.06, 4.15, 4.19, 4.52, 4.21, 4.29]
# y = [4.14, 4.26, 4.05, 4.11, 4.31, 4.12, 4.17, 4.35, 4.25, 4.21, 4.05, 4.28, 4.15, 4.20, 4.32, 4.25, 4.02, 4.14]

x = [12.207, 16.869, 25.050, 22.429, 8.456, 20.589]
y = [11.074, 9.686, 12.064, 9.351, 8.182, 6.642]

res = stats.ks_2samp(x, y)

# lambda_mn = get_likelihood_ratio(x, y)
# print(math.log(lambda_mn))

x = [0.49643668348989334, 0.5204945527768525, 0.5022882605012919, 0.4854124321919, 0.506474861573235, 0.508189537328311,
     0.5066933245401024, 0.4979527264104132, 0.5027634985285513, 0.5059324954226768, 0.49546887208115736,
     0.49936293158738687, 0.5045489202475874, 0.5088884376027852, 0.517780661582751, 0.48699494070960775,
     0.50405660590934, 0.49705554847943645, 0.4977383050756809, 0.4939443308281121, 0.48503475559078124,
     0.4853664311208055, 0.5099253501612471, 0.492698321456103, 0.5187970753451057, 0.5034421759591856,
     0.4937725948657988, 0.5131635782287127, 0.5252880346546878, 0.5066026555450915, 0.4971726998624839,
     0.49913192680264507, 0.4998011164725981, 0.49385039189840463, 0.5256657615408434, 0.4990250689764847,
     0.4997790746494164, 0.4984837928692656]

x = [0.2952546980893941, 0.3060883810453331, 0.2920790992376668, 0.30679811986059524, 0.2981305325098274,
     0.3043967384888962, 0.2831780991917597, 0.29514431068884134, 0.28647061223553544, 0.31918540447312177,
     0.30328335597111833, 0.2976488324663345, 0.297040213279498, 0.30277123407942175, 0.2932300214793147,
     0.2928271372352233, 0.2960994549396225, 0.28859471242299506, 0.48893628237316145, 0.2885064347890733,
     0.2970928813619796, 0.2943976635147367, 0.3079276499597793, 0.296154669842278, 0.29786185866764747,
     0.3064191197904143, 0.3161679854701696, 0.3005573770831573, 0.31041152231864205, 0.29548529349830155,
     0.3001077824554474, 0.3003762378736939]

x = [101.4738561407058, 100.56600725348282, 98.12851158557834, 99.18911660623495, 98.86537652986976, 98.47771769391221,
     98.74278772879404, 98.91780356068489, 98.25979219972547, 99.6746639307771, 100.82795888149668, 100.44590092490289,
     98.74359689465383]

m = len(x)
scs = 0
alpha = 0.05
for i in range(100):
    y = list(np.random.normal(100, 1.0, np.random.randint(m / 2, m + m / 2)))
    n = len(y)
    res = stats.ks_2samp(x, y)
    if res.pvalue > alpha:
        scs += 1
print(scs)

N_0 = (0.05, 0.00028, 100)
N_1 = (0.059, 0.0037, 100)


def idle_model(interval: List[float], F_0: float, rate=N_0[0]):
    #return [F_0 * math.exp(-rate * (t - interval[0])) for t in interval]
    return [F_0 for t in interval]


def busy_model(interval: List[float], F_0: float, rate=N_1[0]):
    #return [1 - (1 - F_0) * math.exp(-rate * (t - interval[0])) for t in interval]
    return [F_0 + rate*math.cos(t) for t in interval]


def der(X: List[float]):
    return [((x - X[i - 1]) + (X[i + 1] - X[i - 1]) / 2) / 2 for (i, x) in enumerate(X) if 0 < i < len(X) - 1]


models = [idle_model, busy_model]

rate = np.random.normal(N_1[0], N_1[1])
F_0 = 0.4
t = list(np.arange(0, 10, 0.1))
X = busy_model(t, F_0, rate)
m_p_1 = busy_model(t, F_0/2)
m_p_2 = idle_model(t, F_0)

dist_1 = sum([(x - m_p_1[i]) ** 2 for i, x in enumerate(X)])/len(X)
dist_2 = sum([(x - m_p_2[i]) ** 2 for i, x in enumerate(X)])/len(X)

der_dist_1 = sum([(x - der(m_p_1)[i]) ** 2 for i, x in enumerate(der(X))])/len(X)
der_dist_2 = sum([(x - der(m_p_2)[i]) ** 2 for i, x in enumerate(der(X))])/len(X)

print('euclidean distance {:.6f}'.format(dist_1))
print('euclidean distance {:.6f}'.format(dist_2))
print('der distance {:.8f}'.format(der_dist_1))
print('der distance {:.8f}'.format(der_dist_2))
print('comb distance {:.8f}'.format(dist_1*der_dist_1))
print('comb distance {:.8f}'.format(dist_2*der_dist_2))

plt.figure(figsize=[10, 5])
plt.plot(t, X, color='orange', label='sample')
plt.plot(t, m_p_1, color='blue', label='ideal_1')
plt.plot(t, m_p_2, color='green', label='ideal_2')
plt.legend()
plt.show()
