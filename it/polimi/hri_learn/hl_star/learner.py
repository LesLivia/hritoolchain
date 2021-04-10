from typing import List, Tuple

EMPTY_STRING = '\u03B5'

MODEL_FORMATTER = 'f_{}'
DISTR_FORMATTER = 'N_{}'


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
            for tup in row:
                tuple_is_filled = tup[0] is not None and tup[1] is not None
                tuple_is_in_upper = tup in self.get_upper_observations()
                if tuple_is_filled and not tuple_is_in_upper:
                    return False
        else:
            return True

    def is_consistent(self):
        return True

    def print(self):
        HEADER = '\t|\t\t'
        for t_word in self.get_T():
            HEADER += t_word if t_word != '' else EMPTY_STRING
            HEADER += '\t\t|\t'
        print(HEADER)
        print('----+---------------+')
        for (i, s_word) in enumerate(self.get_S()):
            ROW = s_word if s_word != '' else EMPTY_STRING
            ROW += '\t|\t'
            for (j, t_word) in enumerate(self.get_T()):
                ROW += ObsTable.tuple_to_str(self.get_upper_observations()[i][j])
                ROW += '\t|'
            print(ROW)
        print('----+---------------+')
        for (i, s_word) in enumerate(self.get_low_S()):
            ROW = s_word if s_word != '' else EMPTY_STRING
            ROW += '\t|\t'
            for (j, t_word) in enumerate(self.get_T()):
                ROW += ObsTable.tuple_to_str(self.get_lower_observations()[i][j])
                ROW += '\t|'
            print(ROW)


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

    def fill_table(self):
        upp_obs: List[List[Tuple]] = self.get_table().get_upper_observations()
        for (i, s_word) in enumerate(self.get_table().get_S()):
            row: List[Tuple] = upp_obs[i].copy()
            for (j, t_word) in enumerate(self.get_table().get_T()):
                # if cell is yet to be filled,
                # asks teacher to answer queries
                # and fills cell with answers
                if upp_obs[i][j][0] is None:
                    identified_model = self.TEACHER.mf_query(s_word + t_word)
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
                if low_obs[i][j][0] is None and low_obs[i][j][1] is None:
                    identified_model = self.TEACHER.mf_query(s_word + t_word)
                    identified_distr = self.TEACHER.ht_query(s_word + t_word, identified_model)
                    cell = (identified_model, identified_distr)
                    row[j] = cell
            low_obs[i] = row.copy()
        self.get_table().set_lower_observations(low_obs)

    def make_closed(self):
        pass

    def make_consistent(self):
        pass

    def run_hl_star(self, debug_print=True):
        # Fill Observation Table with Answers to Queries (from TEACHER)
        self.fill_table()
        if debug_print:
            self.get_table().print()

        # Check if obs. table is closed
        while not (self.get_table().is_closed() and self.get_table().is_consistent()):
            if not self.get_table().is_closed():
                print('table not closed')
                # TODO: If not, make closed
                self.make_closed()

            # TODO: Check if obs. table is consistent
            if not self.get_table().is_consistent():
                print('table is not consistent')
                # TODO: If not, make consistent
                self.make_consistent()

        # TODO: Build Hypothesis Automaton

        # TODO: if counterexamples -> repeat
