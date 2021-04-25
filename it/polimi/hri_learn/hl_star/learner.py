from typing import List, Tuple

from domain.hafeatures import HybridAutomaton, Location, Edge
from hri_learn.hl_star.logger import Logger

EMPTY_STRING = '\u03B5'

MODEL_FORMATTER = 'f_{}'
DISTR_FORMATTER = 'N_{}'
LOCATION_FORMATTER = 'q_{}'
LOGGER = Logger()


class ObsTable:
    def __init__(self, s: List[str], t: List[str], low_s: List[str]):
        self.__S = s
        self.__low_S = low_s
        self.__T = t
        self.__upp_obs: List[List[Tuple]] = [[(None, None)] * len(t)] * len(s)
        self.__low_obs: List[List[Tuple]] = [[(None, None)] * len(t)] * len(low_s)

    def get_S(self):
        return self.__S

    def add_S(self, word: str):
        self.__S.append(word)

    def get_T(self):
        return self.__T

    def add_T(self, word: str):
        self.__T.append(word)

    def get_low_S(self):
        return self.__low_S

    def add_low_S(self, word: str):
        self.__low_S.append(word)

    def del_low_S(self, index: int):
        self.get_low_S().pop(index)

    def get_upper_observations(self):
        return self.__upp_obs

    def set_upper_observations(self, obs_table: List[List[Tuple]]):
        self.__upp_obs = obs_table

    def get_lower_observations(self):
        return self.__low_obs

    def set_lower_observations(self, obs_table: List[List[Tuple]]):
        self.__low_obs = obs_table

    @staticmethod
    def tuple_to_str(tup):
        if tup[0] is None and tup[1] is None:
            return '(∅, ∅)\t'
        else:
            return '({}, {})'.format(MODEL_FORMATTER.format(tup[0]), DISTR_FORMATTER.format(tup[1]))

    def is_closed(self):
        for row in self.get_lower_observations():
            row_is_filled = True
            for tup in row:
                if tup[0] is None or tup[1] is None:
                    row_is_filled = False
            row_is_in_upper = row in self.get_upper_observations()
            if row_is_filled and not row_is_in_upper:
                return False
        else:
            return True

    def is_consistent(self, symbols):
        upp_obs = self.get_upper_observations()
        pairs: List[Tuple] = []
        # FIXME: each pair shows up twice, duplicates should be cleared
        for (index, row) in enumerate(upp_obs):
            equal_rows = [i for (i, r) in enumerate(upp_obs) if index != i and r == row]
            equal_pairs = [(self.get_S()[index], self.get_S()[equal_i]) for equal_i in equal_rows]
            pairs += equal_pairs
        if len(pairs) == 0:
            return True, None
        else:
            for pair in pairs:
                for symbol in symbols.keys():
                    try:
                        new_pair_1 = self.get_S().index(pair[0] + symbol)
                        new_row_1 = self.get_upper_observations()[new_pair_1]
                    except ValueError:
                        new_pair_1 = self.get_low_S().index(pair[0] + symbol)
                        new_row_1 = self.get_lower_observations()[new_pair_1]

                    try:
                        new_pair_2 = self.get_S().index(pair[1] + symbol)
                        new_row_2 = self.get_upper_observations()[new_pair_2]
                    except ValueError:
                        new_pair_2 = self.get_low_S().index(pair[1] + symbol)
                        new_row_2 = self.get_lower_observations()[new_pair_2]

                    new_1_populated = all([new_row_1[i][0] is not None and new_row_1[i][1] is not None
                                           for i in range(len(self.get_T()))])
                    new_2_populated = all([new_row_2[i][0] is not None and new_row_2[i][1] is not None
                                           for i in range(len(self.get_T()))])

                    if new_1_populated and new_2_populated and new_row_1 != new_row_2:
                        return False, symbol
            else:
                return True, None

    def print(self, filter_empty=False):
        max_s = max(len(word) / 3 for word in self.get_S())
        max_low_s = max(len(word) / 3 for word in self.get_low_S())
        max_tabs = int(max(max_s, max_low_s))

        HEADER = '\t' * max_tabs + '|\t\t'
        for t_word in self.get_T():
            HEADER += t_word if t_word != '' else EMPTY_STRING
            HEADER += '\t\t|\t\t'
        print(HEADER)

        SEPARATOR = '----' * max_tabs + '+' + '---------------+' * len(self.get_T())

        print(SEPARATOR)
        for (i, s_word) in enumerate(self.get_S()):
            ROW = s_word if s_word != '' else EMPTY_STRING
            len_word = int(len(s_word) / 3) if s_word != '' else 1
            ROW += '\t' * (max_tabs + 1 - len_word) + '|\t'
            for (j, t_word) in enumerate(self.get_T()):
                ROW += ObsTable.tuple_to_str(self.get_upper_observations()[i][j])
                ROW += '\t|\t'
            print(ROW)
        print(SEPARATOR)
        for (i, s_word) in enumerate(self.get_low_S()):
            row = self.get_lower_observations()[i]
            row_is_populated = any([row[j][0] is not None and row[j][1] is not None for j in range(len(self.get_T()))])
            if filter_empty and not row_is_populated:
                pass
            else:
                ROW = s_word if s_word != '' else EMPTY_STRING
                ROW += '\t' * (max_tabs + 1 - int(len(s_word) / 3)) + '|\t'
                for (j, t_word) in enumerate(self.get_T()):
                    ROW += ObsTable.tuple_to_str(self.get_lower_observations()[i][j])
                    ROW += '\t|\t'
                print(ROW)
        print(SEPARATOR)


class Learner:
    def __init__(self, teacher, table: ObsTable = None):
        self.symbols = teacher.get_symbols()
        self.TEACHER = teacher
        self.obs_table = table if table is not None else ObsTable([''], [''], list(self.symbols.keys()))

    def set_symbols(self, symbols):
        self.symbols = symbols

    def get_symbols(self):
        return self.symbols

    def set_table(self, table: ObsTable):
        self.obs_table = table

    def get_table(self):
        return self.obs_table

    def fill_table(self, initial_low_s_words: List[str]):
        upp_obs: List[List[Tuple]] = self.get_table().get_upper_observations()
        for (i, s_word) in enumerate(self.get_table().get_S()):
            row: List[Tuple] = upp_obs[i].copy()
            for (j, t_word) in enumerate(self.get_table().get_T()):
                # if cell is yet to be filled,
                # asks teacher to answer queries
                # and fills cell with answers
                if upp_obs[i][j][0] is None:
                    identified_model = self.TEACHER.mi_query(s_word + t_word)
                    identified_distr = self.TEACHER.ht_query(s_word + t_word, identified_model)
                    cell = (identified_model, identified_distr)
                    row[j] = cell
            upp_obs[i] = row.copy()
        self.get_table().set_upper_observations(upp_obs)

        low_obs: List[List[Tuple]] = self.get_table().get_lower_observations()
        for (i, s_word) in enumerate(self.get_table().get_low_S()):
            row: List[Tuple] = low_obs[i].copy()
            for (j, t_word) in enumerate(self.get_table().get_T()):
                # if cell is yet to be filled,
                # asks teacher to answer queries
                # and fills cell with answers
                if low_obs[i][j][0] is None and low_obs[i][j][1] is None and s_word not in initial_low_s_words:
                    identified_model = self.TEACHER.mi_query(s_word + t_word)
                    identified_distr = self.TEACHER.ht_query(s_word + t_word, identified_model)
                    cell = (identified_model, identified_distr)
                    row[j] = cell
            low_obs[i] = row.copy()
        self.get_table().set_lower_observations(low_obs)

    def make_closed(self, initial_low_s_words: List[str]):
        upp_obs: List[List[Tuple]] = self.get_table().get_upper_observations()
        low_S = self.get_table().get_low_S()
        low_obs: List[List[Tuple]] = self.get_table().get_lower_observations()
        for (index, row) in enumerate(low_obs):
            row_is_populated = all([cell[0] is not None and cell[1] is not None for cell in row])
            # if there is a populated row in lower portion that is not in the upper portion
            # the corresponding word is added to the S word set
            if row_is_populated and row not in upp_obs:
                upp_obs.append(row)
                new_s_word = low_S[index]
                self.get_table().add_S(new_s_word)
                low_obs.pop(index)
                self.get_table().del_low_S(index)
                # lower portion is then updated with all combinations of
                # new S word and all possible symbols
                for symbol in self.get_symbols():
                    self.get_table().add_low_S(new_s_word + symbol)
                    new_row: List[Tuple] = [(None, None)] * len(self.get_table().get_T())
                    low_obs.append(new_row)
        self.get_table().set_upper_observations(upp_obs)
        self.get_table().set_lower_observations(low_obs)
        self.fill_table(initial_low_s_words)

    def make_consistent(self, discr_sym: str, initial_low_s_words: List[str]):
        self.get_table().add_T(discr_sym)
        upp_obs = self.get_table().get_upper_observations()
        low_obs = self.get_table().get_lower_observations()
        for s_i in range(len(upp_obs)):
            upp_obs[s_i].append((None, None))
        for s_i in range(len(low_obs)):
            low_obs[s_i].append((None, None))
        self.fill_table(initial_low_s_words)

    def get_counterexamples(self, init_words: List[str]):
        upp_obs = self.get_table().get_upper_observations()
        low_obs = self.get_table().get_lower_observations()
        for (s_i, s_word) in enumerate(init_words):
            new_row: List[Tuple] = []
            for (t_i, t_word) in enumerate(self.get_table().get_T()):
                identified_model = self.TEACHER.mi_query(s_word + t_word)
                identified_distr = self.TEACHER.ht_query(s_word + t_word, identified_model)
                LOGGER.debug('QUERY RESULTS FOR {}: ({}, {})'.format(s_word + t_word,
                                                                     MODEL_FORMATTER.format(identified_model),
                                                                     DISTR_FORMATTER.format(identified_distr)))
                new_row.append((identified_model, identified_distr))
            existing_row = low_obs[s_i]
            ex_row_populated = all([existing_row[t_i][0] is not None and existing_row[t_i][1] is not None
                                    for s_i in range(len(init_words)) for t_i in range(len(self.get_table().get_T()))])
            new_row_populated = all([new_row[t_i][0] is not None and new_row[t_i][1] is not None
                                     for s_i in range(len(init_words)) for t_i in range(len(self.get_table().get_T()))])
            if new_row_populated and new_row != low_obs[s_i]:
                if not ex_row_populated:
                    upp_obs.append(new_row)
                    self.get_table().add_S(s_word)
                    self.get_table().del_low_S(s_i)
                    low_obs.pop(s_i)
                    # lower portion is then updated with all combinations of
                    # new S word and all possible symbols
                    for symbol in self.get_symbols():
                        self.get_table().add_low_S(s_word + symbol)
                        new_row: List[Tuple] = [(None, None)] * len(self.get_table().get_T())
                        low_obs.append(new_row)
                    return s_word
                else:
                    LOGGER.warn('CONFLICT DETECTED FOR {}'.format(s_word))
        else:
            return None

    def build_hyp_aut(self):
        locations: List[Location] = []
        upp_obs = self.get_table().get_upper_observations()
        unique_sequences: List[List[Tuple]] = []
        for row in upp_obs:
            if row not in unique_sequences:
                unique_sequences.append(row)
        for (index, seq) in enumerate(unique_sequences):
            new_name = LOCATION_FORMATTER.format(index)
            new_flow = MODEL_FORMATTER.format(seq[0][0]) + ', ' + DISTR_FORMATTER.format(seq[0][1])
            locations.append(Location(new_name, new_flow))

        edges: List[Edge] = []
        for (s_i, s_word) in enumerate(self.get_table().get_S()):
            for (t_i, t_word) in enumerate(self.get_table().get_T()):
                if upp_obs[s_i][t_i][0] is not None and upp_obs[s_i][t_i][1] is not None:
                    word: str = s_word + t_word
                    entry_word = word[:-3] if t_word != '' else s_word[:-3]
                    start_row_index = self.get_table().get_S().index(entry_word)
                    start_row = unique_sequences.index(upp_obs[start_row_index])
                    start_loc = locations[start_row]
                    if t_word == '':
                        dest_row = unique_sequences.index(upp_obs[s_i])
                        dest_loc = locations[dest_row]
                    else:
                        dest_row = [obs[0] for obs in unique_sequences].index(upp_obs[s_i][t_i])
                        dest_loc = locations[dest_row]
                    # labels = self.get_symbols()[word[-3:]].split(' and ') if word != '' else ['', EMPTY_STRING]
                    labels = word[-3:] if word != '' else EMPTY_STRING
                    new_edge = Edge(start_loc, dest_loc, sync=labels)  # , sync=labels[1])
                    if new_edge not in edges:
                        edges.append(new_edge)

        low_obs: List[List[Tuple]] = self.get_table().get_lower_observations()
        for (s_i, s_word) in enumerate(self.get_table().get_low_S()):
            for (t_i, t_word) in enumerate(self.get_table().get_T()):
                if low_obs[s_i][t_i][0] is not None and low_obs[s_i][t_i][1] is not None:
                    word = s_word + t_word
                    entry_word = word[:-3]
                    start_row_index = self.get_table().get_S().index(entry_word)
                    start_row = unique_sequences.index(upp_obs[start_row_index])
                    start_loc = locations[start_row]
                    dest_row = [obs[0] for obs in upp_obs].index(low_obs[s_i][t_i])
                    dest_loc = locations[dest_row]
                    if word != '':
                        # labels = self.get_symbols()[word.replace(entry_word, '')].split(' and ')
                        labels = word.replace(entry_word, '')
                    else:
                        # labels = ['', EMPTY_STRING]
                        labels = EMPTY_STRING
                    new_edge = Edge(start_loc, dest_loc, sync=labels)  # [0], sync=labels[1])
                    if new_edge not in edges:
                        edges.append(new_edge)

        return HybridAutomaton(locations, edges)

    def run_hl_star(self, debug_print=True, filter_empty=False):
        initial_low_s_words = self.get_table().get_low_S().copy()
        # Fill Observation Table with Answers to Queries (from TEACHER)
        counterexample = self.get_counterexamples(initial_low_s_words)
        while counterexample is not None:
            LOGGER.warn('FOUND COUNTEREXAMPLE: {}'.format(counterexample))
            initial_low_s_words.remove(counterexample)
            self.fill_table(initial_low_s_words)

            if debug_print:
                LOGGER.info('OBSERVATION TABLE')
                self.get_table().print(filter_empty)

            # Check if obs. table is closed
            closedness_check = self.get_table().is_closed()
            consistency_check, discriminating_symbol = self.get_table().is_consistent(self.get_symbols())
            while not (closedness_check and consistency_check):
                if not closedness_check:
                    LOGGER.warn('!!TABLE IS NOT CLOSED!!')
                    # If not, make closed
                    self.make_closed(initial_low_s_words)
                    LOGGER.msg('CLOSED OBSERVATION TABLE')
                    self.get_table().print(filter_empty)
                closedness_check = self.get_table().is_closed()

                # Check if obs. table is consistent
                if not consistency_check:
                    LOGGER.warn('!!TABLE IS NOT CONSISTENT!!')
                    # If not, make consistent
                    self.make_consistent(discriminating_symbol, initial_low_s_words)
                    LOGGER.msg('CONSISTENT OBSERVATION TABLE')
                    self.get_table().print(filter_empty)

                consistency_check, discriminating_symbol = self.get_table().is_consistent(self.get_symbols())

            [initial_low_s_words.remove(s_word) for s_word in self.get_table().get_S() if s_word in initial_low_s_words]
            counterexample = self.get_counterexamples(initial_low_s_words)

        if debug_print:
            LOGGER.msg('FINAL OBSERVATION TABLE')
            self.get_table().print(filter_empty)
        # Build Hypothesis Automaton
        LOGGER.info('BUILDING HYP. AUTOMATON...')
        return self.build_hyp_aut()
