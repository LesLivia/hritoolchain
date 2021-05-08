import math
from functools import reduce
from typing import Tuple, List

import matplotlib.pyplot as plt
import numpy as np
import scipy.special as sci
import scipy.stats as stats
from tqdm import tqdm

from domain.sigfeatures import SignalPoint
from hri_learn.hl_star.evt_id import EventFactory, DEFAULT_DISTR, DEFAULT_MODEL, DRIVER_SIGNAL, MODEL_TO_DISTR_MAP
from hri_learn.hl_star.learner import ObsTable
from hri_learn.hl_star.logger import Logger

LOGGER = Logger()


class Teacher:
    def __init__(self, models, distributions: List[Tuple]):
        # System-Dependent Attributes
        self.symbols = None
        self.models = models
        self.distributions = distributions
        self.evt_factory = EventFactory(None, None, None)

        # Trace-Dependent Attributes
        self.chg_pts: List[List[float]] = []
        self.events = []
        self.signals: List[List[List[SignalPoint]]] = []

    def clear(self):
        self.signals.append([])
        self.evt_factory.clear()

    # SYMBOLS
    def set_symbols(self, symbols):
        self.symbols = symbols
        self.evt_factory.set_symbols(symbols)

    def get_symbols(self):
        return self.symbols

    def compute_symbols(self, guards: List[str], syncs: List[str]):
        symbols = {}
        self.evt_factory.set_guards(guards)
        self.evt_factory.set_channels(syncs)

        # Compute all guards combinations
        guards_comb = [''] * 2 ** len(guards)
        for (i, g) in enumerate(guards):
            pref = ''
            for j in range(2 ** len(guards)):
                guards_comb[j] += pref + g
                if (j + 1) % ((2 ** len(guards)) / (2 ** (i + 1))) == 0:
                    pref = '!' if pref == '' else ''

        # Combine all guards with channels
        for chn in syncs:
            for (index, g) in enumerate(guards_comb):
                symbols[chn + '_' + str(index + 1)] = g + ' and ' + chn

        self.set_symbols(symbols)
        self.evt_factory.set_symbols(symbols)

    # CHANGE POINTS
    def set_chg_pts(self, chg_pts: List[float]):
        self.chg_pts.append(chg_pts)

    def get_chg_pts(self):
        return self.chg_pts

    def find_chg_pts(self, timestamps: List[float], values: List[float]):
        chg_pts: List[float] = []

        # IDENTIFY CHANGE PTS IN DRIVER OVERLAY
        prev = values[0]
        for i in range(1, len(values)):
            curr = values[i]
            if curr != prev:
                chg_pts.append(timestamps[i])
            prev = curr

        self.set_chg_pts(chg_pts)

    # SIGNALS
    def get_signals(self):
        return self.signals

    def add_signal(self, signal: List[SignalPoint], trace: int):
        self.signals[trace].append(signal)
        self.evt_factory.add_signal(signal, trace)

    # EVENTS
    def set_events(self, events):
        self.events.append(events)

    def get_events(self):
        return self.events

    def identify_events(self, trace):
        events = {}

        for pt in self.get_chg_pts()[trace]:
            events[pt] = self.evt_factory.label_event(pt, trace)

        self.set_events(events)

    def plot_trace(self, trace: int, title=None, xlabel=None, ylabel=None):
        plt.figure(figsize=(10, 5))

        if title is not None:
            plt.title(title, fontsize=18)
        if xlabel is not None:
            plt.xlabel(xlabel, fontsize=18)
        if ylabel is not None:
            plt.ylabel(ylabel, fontsize=18)

        t = [x.timestamp for x in self.get_signals()[trace][0]]
        v = [x.value for x in self.get_signals()[trace][0]]

        plt.xlim(min(t) - 5, max(t) + 5)
        plt.ylim(0, max(v) + .05)
        plt.plot(t, v, 'k', linewidth=.5)

        x = list(self.events[trace].keys())
        plt.vlines(x, [0] * len(x), [max(v)] * len(x), 'b', '--')
        for (index, e) in enumerate(self.get_events()[trace].values()):
            plt.text(x[index] - 7, max(v) + .01, e, fontsize=18, color='blue')

        plt.show()

    # QUERIES
    def set_models(self, models):
        self.models = models

    def get_models(self):
        return self.models

    def set_distributions(self, distributions):
        self.distributions = distributions

    def get_distributions(self):
        return self.distributions

    def plot_distributions(self):
        for (i_m, m) in enumerate(self.get_models()):
            plt.figure()
            plt.title("Distributions for f_{}".format(i_m))
            related_distributions = list(filter(lambda k: MODEL_TO_DISTR_MAP[k] == i_m, MODEL_TO_DISTR_MAP.keys()))
            for d in related_distributions:
                distr: Tuple = self.get_distributions()[d]
                mu: float = distr[0]
                sigma: float = distr[1]
                x = np.linspace(mu - 3 * sigma, mu + 3 * sigma, 200)
                plt.plot(x, stats.norm.pdf(x, mu, sigma), label='N_{}({:.3f}, {:.3f})'.format(d, mu, sigma))
            plt.legend()
            plt.show()

    def get_segments(self, word: str):
        trace_events: List[str] = []
        for trace in range(len(self.get_events())):
            trace_events.append(reduce(lambda x, y: x + y, list(self.get_events()[trace].values())))
        traces = []
        for (i, event_str) in enumerate(trace_events):
            if event_str.startswith(word):
                traces.append(i)
        if len(traces) == 0:
            return []

        segments = []
        for trace in traces:
            main_sig = self.get_signals()[trace][DRIVER_SIGNAL]
            events_in_word = []
            for i in range(0, len(word), 3):
                events_in_word.append(word[i:i + 3])

            start_timestamp = list(self.get_events()[trace].keys())[len(events_in_word) - 1]
            if len(events_in_word) < len(self.get_events()[trace]):
                end_timestamp = list(self.get_events()[trace].keys())[len(events_in_word)]
            else:
                end_timestamp = main_sig[-1].timestamp

            segment = list(filter(lambda pt: start_timestamp <= pt.timestamp <= end_timestamp, main_sig))
            segments.append(segment)
        else:
            return segments

    @staticmethod
    def derivative(t: List[float], values: List[float]):
        increments = []
        try:
            increments = [(v - values[i - 1]) / (t[i] - t[i - 1]) for (i, v) in enumerate(values) if i > 0]
        except ZeroDivisionError:
            avg_dt = sum([x - t[i - 1] for (i, x) in enumerate(t) if i > 0]) / (len(t) - 1)
            increments = [(v - values[i - 1]) / avg_dt for (i, v) in enumerate(values) if i > 0]
        finally:
            return increments

    def mi_query(self, word: str):
        if word == '':
            return DEFAULT_MODEL
        else:
            segments = self.get_segments(word)
            if len(segments) > 0:
                fits = []
                for segment in segments:
                    if len(segment) < 10:
                        continue
                    interval = [pt.timestamp for pt in segment]
                    real_behavior = [pt.value for pt in segment]
                    real_der = self.derivative(interval, real_behavior)
                    min_distance = 10000
                    min_der_distance = 10000
                    best_fit = None

                    for (m_i, model) in enumerate(self.get_models()):
                        ideal_model = model(interval, segment[0].value)
                        distances = [abs(i - real_behavior[index]) for (index, i) in enumerate(ideal_model)]
                        avg_distance = sum(distances) / len(distances)

                        ideal_der = self.derivative(interval, ideal_model)
                        der_distances = [abs(i - real_der[index]) for (index, i) in enumerate(ideal_der)]
                        avg_der_distance = sum(der_distances) / len(der_distances)

                        dist_is_closer = avg_distance < min_distance
                        der_is_closer = avg_der_distance < min_der_distance
                        der_same_sign = sum([v * ideal_der[i] for (i, v) in enumerate(real_der)]) / len(real_der) > 0

                        if dist_is_closer and der_is_closer and der_same_sign:
                            min_distance = avg_distance
                            min_der_distance = avg_der_distance
                            best_fit = m_i
                    else:
                        fits.append(best_fit)

                unique_fits = set(fits)
                freq = -1
                best_fit = None
                for f in unique_fits:
                    matches = sum([x == f for x in fits]) / len(fits)
                    if matches > freq:
                        freq = matches
                        best_fit = f
                if freq > 0.9:
                    return best_fit
                else:
                    return None
            else:
                return None

    @staticmethod
    def get_theta_th(P_0: float, N: int, alpha: float = 0.05):
        for theta in range(0, N, 1):
            alpha_th = 0
            for K in range(theta, N, 1):
                binom = sci.binom(N, K)
                alpha_th += binom * (P_0 ** K) * ((1 - P_0) ** (N - K))
            if alpha_th <= alpha:
                return theta
        return None

    def ht_query(self, word: str, model=DEFAULT_MODEL, save=True):
        if model is None:
            return None

        if word == '':
            return DEFAULT_DISTR
        else:
            segments = self.get_segments(word)
            if len(segments) > 0:
                successes = []

                distributions = self.get_distributions()
                eligible_distributions = [k for k in MODEL_TO_DISTR_MAP.keys() if
                                          MODEL_TO_DISTR_MAP[k] == model]
                for d in eligible_distributions:
                    successes.append([])

                metrics = []
                for segment in segments:
                    metric = self.evt_factory.get_ht_metric(segment, word)
                    metrics.append(metric)
                    if metric is not None:
                        LOGGER.info('EST. RATE for {}: {}'.format(word, metric))
                        # performs hyp. testing on all eligible distributions
                        for (i, d) in enumerate(eligible_distributions):
                            distr: tuple = distributions[d]
                            minus_sigma = max(distr[0] - 2 * distr[1], 0)
                            plus_sigma = distr[0] + 2 * distr[1]
                            successes[i].append(minus_sigma <= metric <= plus_sigma)

                p_value = [0] * len(eligible_distributions)
                for (i, d) in enumerate(eligible_distributions):
                    for x in successes[i]:
                        if not x:
                            p_value[i] += 1
                    p_value[i] /= len(successes[i])

                metrics = list(filter(lambda m: m is not None, metrics))
                min_Y = None
                best_D = None
                for (i, d) in enumerate(eligible_distributions):
                    if min_Y is None or p_value[i] < min_Y:
                        best_D = d
                        min_Y = p_value[i]

                theta_z = None
                alpha = 0.00
                while theta_z is None:
                    alpha += 0.05
                    theta_z = self.get_theta_th(0.05, len(metrics), alpha)
                    if alpha > 0.1:
                        return None

                if min_Y is not None and min_Y * len(metrics) <= theta_z:
                    LOGGER.debug(
                        "Accepting N_{} with Y: {:.0f}({}), confidence: {}".format(best_D, min_Y * len(metrics),
                                                                                   len(metrics), 1 - alpha))
                    return best_D
                else:
                    LOGGER.debug(
                        "Rejecting H_0 with Y: {:.0f}({}), confidence: {}".format(
                            min_Y * len(metrics) if min_Y is not None else 0,
                            len(metrics), 1 - alpha))
                    if save:
                        # if no distribution is found that passes the hyp. test,
                        # a new distribution is created...
                        avg_metrics = sum(metrics) / len(metrics)
                        var_metrics = sum([(m - avg_metrics) ** 2 for m in metrics]) / len(metrics)
                        std_dev_metrics = math.sqrt(var_metrics) if var_metrics != 0 else avg_metrics / 10
                        self.get_distributions().append((avg_metrics, std_dev_metrics, len(metrics)))
                        # and added to the map of eligible distr. for the selected model
                        new_distr_index = len(self.get_distributions()) - 1
                        MODEL_TO_DISTR_MAP[new_distr_index] = model
                    else:
                        new_distr_index = len(self.get_distributions()) + 1

                    return new_distr_index
            else:
                return None

    def eqr_query(self, row1: List[Tuple], row2: List[Tuple], strict=False):
        if strict:
            return row1 == row2

        match = True
        for (c_i, cell) in enumerate(row1):
            cell_is_filled = cell[0] is not None and cell[1] is not None
            cell2_is_filled = row2[c_i][0] is not None and row2[c_i][1] is not None
            if cell_is_filled and cell2_is_filled and cell != row2[c_i]:
                match = False
        return match

    def get_counterexample(self, table: ObsTable):
        S = table.get_S()
        low_S = table.get_low_S()

        trace_events: List[str] = []
        for trace in range(len(self.get_events())):
            trace_events.append(reduce(lambda x, y: x + y, list(self.get_events()[trace].values())))

        max_events = int(max([len(t) for t in trace_events]))

        unique_seq = []
        for (s_i, s_word) in enumerate(S):
            row = table.get_upper_observations()[s_i]
            row_is_filled = any([t[0] is not None and t[1] is not None for t in row])
            if row_is_filled and row not in unique_seq:
                unique_seq.append(row)

        for (i, event_str) in tqdm(enumerate(trace_events), total=len(trace_events)):
            for j in range(3, max_events + 1, 3):
                if event_str[:j] not in S and event_str[:j] not in low_S:
                    new_row = []
                    for (e_i, e_word) in enumerate(table.get_E()):
                        word = event_str[:j] + e_word
                        id_model = self.mi_query(word)
                        id_distr = self.ht_query(word, id_model, save=False)
                        if id_model is not None and id_distr is not None:
                            new_row.append((id_model, id_distr))
                        else:
                            new_row.append((None, None))
                    new_row_is_filled = any([t[0] is not None and t[1] is not None for t in new_row])
                    if new_row_is_filled:
                        new_row_is_present = any([self.eqr_query(new_row, row2) for row2 in unique_seq])
                        if new_row and not new_row_is_present:
                            for a in self.get_symbols():
                                id_model = self.mi_query(event_str[:j] + a)
                                id_distr = self.ht_query(event_str[:j] + a, id_model, save=False)
                                if id_model is not None and id_distr is not None:
                                    return event_str[:j]
                        else:
                            for (s_i, s_word) in enumerate(S):
                                old_row = table.get_upper_observations()[s_i] if s_i < len(S) else \
                                    table.get_lower_observations()[s_i - len(S)]
                                if self.eqr_query(old_row, new_row):
                                    for a in self.get_symbols():
                                        id_model_1 = self.mi_query(s_word + a)
                                        id_distr_1 = self.ht_query(s_word + a, id_model_1, save=False)
                                        one_is_filled = id_model_1 is not None and id_distr_1 is not None
                                        id_model_2 = self.mi_query(event_str[:j] + a)
                                        id_distr_2 = self.ht_query(event_str[:j] + a, id_model_2, save=False)
                                        two_is_filled = id_model_2 is not None and id_distr_2 is not None
                                        if one_is_filled and two_is_filled and \
                                                (id_model_1 != id_model_2 or id_distr_1 != id_distr_2):
                                            return event_str[:j]
        else:
            return None
