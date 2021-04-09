from typing import List, Tuple

EMPTY_STRING = '\u03B5'


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
        return '({}, {})'.format(tup[0], tup[1])

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
            row: List[Tuple] = upp_obs[i]
            for (j, t_word) in enumerate(self.get_table().get_T()):
                if upp_obs[i][j][0] is None:
                    cell = ('f_0', 'N_0')
                    row[j] = cell
            upp_obs[i] = row
        self.get_table().set_upper_observations(upp_obs)

        low_obs: List[List[Tuple]] = self.get_table().get_lower_observations()
        for (i, s_word) in enumerate(self.get_table().get_low_S()):
            row: List[Tuple] = low_obs[i]
            for (j, t_word) in enumerate(self.get_table().get_T()):
                if low_obs[i][j][0] is None:
                    cell = ('f_0', 'N_0')
                    row[j] = cell
            low_obs[i] = row
        self.get_table().set_upper_observations(upp_obs)

    def run_hl_star(self):
        # Fill Observation Table with Answers to Queries (from TEACHER)
        self.fill_table()
        self.get_table().print()
