import scipy.special as sci


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


P_0 = 0.05
N = 500

print("at least {} failures out of {} segments".format(get_theta_th(P_0, N), N))
