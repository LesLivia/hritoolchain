from typing import Tuple, List

import matplotlib.pyplot as plt

from domain.sigfeatures import SignalPoint
from hri_learn.hl_star.evt_id import EventFactory, DEFAULT_DISTR, DEFAULT_MODEL, DRIVER_SIGNAL, MODEL_TO_DISTR_MAP
from hri_learn.hl_star.logger import Logger
from functools import reduce

LOGGER = Logger()


class Teacher:
    def __init__(self, models, distributions: List[Tuple]):
        # System-Dependent Attributes
        self.symbols = None
        self.models = models
        self.distributions = distributions
        self.evt_factory = EventFactory(None, None, None)

        # Trace-Dependent Attributes
        # (to be cleared when trace changes)
        self.chg_pts = None
        self.events = None
        self.signals: List[List[SignalPoint]] = []

    def clear(self):
        self.events = None
        self.chg_pts = None
        self.signals: List[List[SignalPoint]] = []
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
        self.chg_pts = chg_pts

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

    def add_signal(self, signal: List[SignalPoint]):
        self.signals.append(signal)
        self.evt_factory.add_signal(signal)

    # EVENTS
    def set_events(self, events):
        self.events = events

    def get_events(self):
        return self.events

    def identify_events(self):
        events = {}

        for pt in self.get_chg_pts():
            events[pt] = self.evt_factory.label_event(pt)

        self.set_events(events)

    def plot_trace(self, title=None, xlabel=None, ylabel=None):
        plt.figure(figsize=(10, 5))

        if title is not None:
            plt.title(title, fontsize=18)
        if xlabel is not None:
            plt.xlabel(xlabel, fontsize=18)
        if ylabel is not None:
            plt.ylabel(ylabel, fontsize=18)

        t = [x.timestamp for x in self.get_signals()[0]]
        v = [x.value for x in self.get_signals()[0]]

        plt.xlim(min(t) - 5, max(t) + 5)
        plt.ylim(0, max(v) + .05)
        plt.plot(t, v, 'k', linewidth=.5)

        x = list(self.get_events().keys())
        plt.vlines(x, [0] * len(x), [max(v)] * len(x), 'b', '--')
        for (index, e) in enumerate(self.get_events().values()):
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
        trace_events = reduce(lambda x, y: x + y, list(self.get_events().values()))
        if word not in trace_events:
            return None
        main_sig = self.get_signals()[DRIVER_SIGNAL]
        events_in_word = []
        for i in range(0, len(word), 3):
            events_in_word.append(word[i:i + 3])

        last_event = events_in_word[-1]
        for (index, event) in enumerate(self.get_events().values()):
            if event == last_event:
                start_timestamp = list(self.get_events().keys())[index]
                end_timestamp: float
                if index < len(self.get_events()) - 1:
                    end_timestamp = list(self.get_events().keys())[index + 1]
                else:
                    end_timestamp = main_sig[-1].timestamp
                return list(filter(lambda pt: start_timestamp <= pt.timestamp <= end_timestamp, main_sig))
        else:
            return None

    def mf_query(self, word: str):
        if word == '':
            return DEFAULT_MODEL
        else:
            segment = self.cut_segment(word)
            if segment is not None:
                min_distance = 10000
                best_fit = None
                for (m_i, model) in enumerate(self.get_models()):
                    interval = [pt.timestamp for pt in segment]
                    ideal_model = model(interval, segment[0].value)
                    real_behavior = [pt.value for pt in segment]
                    # plt.figure()
                    # plt.plot(interval, ideal_model, 'b', interval, real_behavior, 'r')
                    # plt.show()
                    distances = [abs(i - real_behavior[index]) for (index, i) in enumerate(ideal_model)]
                    avg_distance = sum(distances) / len(distances)
                    avg_ideal_dts = sum([v - ideal_model[i - 1] for (i, v) in enumerate(ideal_model) if i > 0]) / len(
                        ideal_model)
                    avg_real_dts = sum(
                        [v - real_behavior[i - 1] for (i, v) in enumerate(real_behavior) if i > 0]) / len(
                        real_behavior)
                    if avg_distance < min_distance and avg_ideal_dts * avg_real_dts > 0:
                        min_distance = avg_distance
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
                metric = self.evt_factory.get_ht_metric(segment)
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
