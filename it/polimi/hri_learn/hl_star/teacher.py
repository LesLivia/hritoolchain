from functools import reduce
from typing import Tuple, List

import matplotlib.pyplot as plt

from domain.sigfeatures import SignalPoint
from hri_learn.hl_star.evt_id import EventFactory, DEFAULT_DISTR, DEFAULT_MODEL, DRIVER_SIGNAL, MODEL_TO_DISTR_MAP
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
        # self.events = None
        # self.chg_pts = None
        # self.signals: List[List[List[SignalPoint]]] = []
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

    def cut_segment(self, word: str):
        trace_events: List[str] = []
        for trace in range(len(self.get_events())):
            trace_events.append(reduce(lambda x, y: x + y, list(self.get_events()[trace].values())))
        trace = None
        for (i, event_str) in enumerate(trace_events):
            if word in event_str:
                trace = i
        if trace is None:
            return None

        main_sig = self.get_signals()[trace][DRIVER_SIGNAL]
        events_in_word = []
        for i in range(0, len(word), 3):
            events_in_word.append(word[i:i + 3])

        last_event = events_in_word[-1]
        for (index, event) in enumerate(self.get_events()[trace].values()):
            if event == last_event:
                start_timestamp = list(self.get_events()[trace].keys())[index]
                end_timestamp: float
                if index < len(self.get_events()[trace]) - 1:
                    end_timestamp = list(self.get_events()[trace].keys())[index + 1]
                else:
                    end_timestamp = main_sig[-1].timestamp
                return list(filter(lambda pt: start_timestamp <= pt.timestamp <= end_timestamp, main_sig))
        else:
            return None

    @staticmethod
    def derivative(t: List[float], values: List[float]):
        try:
            increments = [(v - values[i - 1]) / (t[i] - t[i - 1]) for (i, v) in enumerate(values) if i > 0]
        except ZeroDivisionError:
            avg_dt = sum([x - t[i - 1] for (i, x) in enumerate(t) if i > 0]) / (len(t) - 1)
            increments = [(v - values[i - 1]) / avg_dt for (i, v) in enumerate(values) if i > 0]
        finally:
            return increments

    def mf_query(self, word: str):
        if word == '':
            return DEFAULT_MODEL
        else:
            segment = self.cut_segment(word)
            if segment is not None:
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
                    return best_fit
            else:
                return None

    def ht_query(self, word: str, model=DEFAULT_MODEL):
        if model is None:
            return None

        if word == '':
            return DEFAULT_DISTR
        else:
            segment = self.cut_segment(word)
            if segment is not None:
                metric = self.evt_factory.get_ht_metric(segment, word)
                if metric is not None:
                    LOGGER.debug('EST. RATE for {}: {}'.format(word, metric))
                    distributions = self.get_distributions()
                    eligible_distributions = [k for k in MODEL_TO_DISTR_MAP.keys() if MODEL_TO_DISTR_MAP[k] == model]
                    # performs hyp. testing on all eligible distributions
                    for index in eligible_distributions:
                        distr: tuple = distributions[index]
                        minus_sigma = max(distr[0] - 3 * distr[1], 0)
                        plus_sigma = distr[0] + 3 * distr[1]
                        if minus_sigma <= metric <= plus_sigma:
                            return index
                    else:
                        # if no distribution is found that passes the hyp. test,
                        # a new distribution is created...
                        self.get_distributions().append((metric, metric / 10))
                        # and added to the map of eligible distr. for the selected model
                        new_distr_index = len(self.get_distributions()) - 1
                        MODEL_TO_DISTR_MAP[new_distr_index] = model
                        return new_distr_index
                else:
                    return None
            else:
                return None
