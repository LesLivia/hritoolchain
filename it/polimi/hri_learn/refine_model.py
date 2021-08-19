import math
import sys
import warnings
from typing import List
from datetime import datetime
from graphviz import Source

import pltr.ha_pltr as ha_pltr
from hri_learn.hl_star.learner import Learner
from hri_learn.hl_star.logger import Logger
from hri_learn.hl_star.teacher import Teacher

# LEARNING PROCEDURE SETUP
warnings.filterwarnings('ignore')
startTime = datetime.now()

CS_VERSION = sys.argv[2]
N_0 = (0.003, 0.0001, 100)
N_1 = (0.004, 0.0004, 100)

# N_0 = (0.0005, 0.00028, 100)
# N_1 = (0.00059, 0.00037, 100)

LOGGER = Logger()
# PROB_DISTR = [N_0, N_1, N_2, N_3, N_4, N_5, N_6, N_7, N_8, N_9]
PROB_DISTR = [N_0, N_1]

UNCONTR_EVTS = {}
if CS_VERSION == 'b':
    UNCONTR_EVTS = {'w': 'in_waiting_room'}  # , 'o': 'in_office'}
elif CS_VERSION == 'c':
    UNCONTR_EVTS = {'w': 'in_waiting_room', 'o': 'in_office'}
elif CS_VERSION == 'x':
    UNCONTR_EVTS = {'s': 'sat', 'r': 'ran', 'h': 'harsh_env', 'l': 'load', 'a': 'assisted_walk'}

CONTR_EVTS = {'u': 'start_moving', 'd': 'stop_moving'}


def idle_model(interval: List[float], F_0: float):
    return [F_0 * math.exp(-N_0[0] * (t - interval[0])) for t in interval]


def busy_model(interval: List[float], F_0: float):
    return [1 - (1 - F_0) * math.exp(-N_1[0] * (t - interval[0])) for t in interval]


MODELS = [idle_model, busy_model]

TEACHER = Teacher(MODELS, PROB_DISTR)
TEACHER.compute_symbols(list(UNCONTR_EVTS.keys()), list(CONTR_EVTS.keys()))
for sym in TEACHER.get_symbols().keys():
    print('{}: {}'.format(sym, TEACHER.get_symbols()[sym]))

LEARNER = Learner(TEACHER)

# RUN LEARNING ALGORITHM:
LEARNED_HA = LEARNER.run_hl_star(filter_empty=True)
ha_pltr.plot_ha(LEARNED_HA, 'H_{}_{}{}'.format(sys.argv[1], CS_VERSION, sys.argv[3]), view=True)
TEACHER.plot_distributions()
print(datetime.now() - startTime)

temp = "/Users/lestingi/Desktop/phd-workspace/_papers/RA-L_IROS21/journal_version/IEEETransactions_LaTeX/IEEEtran/figs/exp/upp/"
source = """
digraph hybrid_automaton {
	edge [arrowsize=0.5]
	rankdir=LR size=2
	node [shape=circle]
	node [fontname=helvetica]
	node [penwidth=0.5]
	edge [fontname=helvetica]
	edge [penwidth=0.5]
	q_0 [label=<<FONT  POINT-SIZE="8" COLOR="black">q_0</FONT><br/><FONT  POINT-SIZE="6" COLOR="#8b54a1"><br/><b>f_0, N_0</b></FONT>>]
	q_1 [label=<<FONT  POINT-SIZE="8" COLOR="black">q_1</FONT><br/><FONT  POINT-SIZE="6" COLOR="#8b54a1"><br/><b>f_1, N_1</b></FONT>>]
	q_2 [label=<<FONT  POINT-SIZE="8" COLOR="black">q_2</FONT><br/><FONT  POINT-SIZE="6" COLOR="#8b54a1"><br/><b>f_1, N_2</b></FONT>>]
	q_3 [label=<<FONT  POINT-SIZE="8" COLOR="black">q_3</FONT><br/><FONT  POINT-SIZE="6" COLOR="#8b54a1"><br/><b>f_0, N_3</b></FONT>>]
	q_4 [label=<<FONT  POINT-SIZE="8" COLOR="black">q_4</FONT>>]
	q_0 -> q_0 [label=<<FONT  POINT-SIZE="8" COLOR="#cc2b23">ε</FONT>>]
	q_0 -> q_1 [label=<<FONT  POINT-SIZE="8" COLOR="#179900">!run</FONT><br/><FONT  POINT-SIZE="8" COLOR="#cc2b23">start?</FONT>>]
	q_1 -> q_0 [label=<<FONT  POINT-SIZE="8" COLOR="#179900">!sit</FONT><br/><FONT  POINT-SIZE="8" COLOR="#cc2b23">stop?</FONT>>]
	q_1 -> q_3 [label=<<FONT  POINT-SIZE="8" COLOR="#179900">sit</FONT><br/><FONT  POINT-SIZE="8" COLOR="#cc2b23">stop?</FONT>>]
	q_3 -> q_1 [label=<<FONT  POINT-SIZE="8" COLOR="#179900">!run</FONT><br/><FONT  POINT-SIZE="8" COLOR="#cc2b23">start?</FONT>>]
	q_0 -> q_2 [label=<<FONT  POINT-SIZE="8" COLOR="#179900">run</FONT><br/><FONT  POINT-SIZE="8" COLOR="#cc2b23">start?</FONT>>]
	q_2 -> q_0 [label=<<FONT  POINT-SIZE="8" COLOR="#179900">!sit</FONT><br/><FONT  POINT-SIZE="8" COLOR="#cc2b23">stop?</FONT>>]
	q_2 -> q_3 [label=<<FONT  POINT-SIZE="8" COLOR="#179900">sit</FONT><br/><FONT  POINT-SIZE="8" COLOR="#cc2b23">stop?</FONT>>]
	q_1 -> q_4 [label=<<FONT  POINT-SIZE="8" COLOR="#179900">F&gt;=1</FONT>>]
    q_2 -> q_4 [label=<<FONT  POINT-SIZE="8" COLOR="#179900">F&gt;=1</FONT>>]
}
"""
#s = Source(source, filename=temp+"hri_c", format="pdf")
#s.view()
