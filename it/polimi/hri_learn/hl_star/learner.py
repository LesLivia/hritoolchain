from typing import List, Tuple
from domain.hafeatures import HybridAutomaton, Location, Edge
from hri_learn.hl_star.logger import Logger
import pltr.ha_pltr as ha_pltr

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
        S = self.get_table().get_S()
        upp_obs: List[List[Tuple]] = self.get_table().get_upper_observations()
        low_S = self.get_table().get_low_S()
        low_obs: List[List[Tuple]] = self.get_table().get_lower_observations()
        for (index, row) in enumerate(low_obs):
            row_is_populated = all([cell[0] is not None and cell[1] is not None for cell in row])
            if row_is_populated and row not in upp_obs:
                upp_obs.append(row)
                self.get_table().add_S(low_S[index])
                low_obs.pop(index)
                self.get_table().del_low_S(index)
        self.get_table().set_upper_observations(upp_obs)
        self.get_table().set_lower_observations(low_obs)

    def make_consistent(self):
        pass

    def build_hyp_aut(self, show=True):
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

        hyp_ha = HybridAutomaton(locations, edges)
        if show:
            ha_pltr.plot_ha(hyp_ha, 'hyp_ha', view=True)

        return HybridAutomaton(locations, edges)

    def run_hl_star(self, debug_print=True, show=True):
        # Fill Observation Table with Answers to Queries (from TEACHER)
        self.fill_table()
        if debug_print:
            LOGGER.info('OBSERVATION TABLE')
            self.get_table().print()

        # Check if obs. table is closed
        while not (self.get_table().is_closed() and self.get_table().is_consistent()):
            if not self.get_table().is_closed():
                LOGGER.warn('TABLE IS NOT CLOSED')
                # If not, make closed
                self.make_closed()
                LOGGER.info('CLOSED OBSERVATION TABLE')
                self.get_table().print()

            # TODO: Check if obs. table is consistent
            if not self.get_table().is_consistent():
                print('table is not consistent')
                # TODO: If not, make consistent
                self.make_consistent()

        # Build Hypothesis Automaton
        LOGGER.info('BUILDING HYP. AUTOMATON...')
        return self.build_hyp_aut(show)

        # TODO: if counterexamples -> repeat
