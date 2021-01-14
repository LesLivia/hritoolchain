import sqlite3
from sqlite3 import Error, Cursor
from typing import Set, Tuple, List

import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats

import mgrs.dryad_mgr as dryad_mgr


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        return conn


def create_tables(sql: Cursor):
    query = """
                CREATE TABLE IF NOT EXISTS subject (
	                id text PRIMARY KEY,
	                sub_group char NOT NULL,
	                sub_num integer NOT NULL
                );
            """
    sql.execute(query)
    query = """
                    CREATE TABLE IF NOT EXISTS trial (
    	                id integer,
    	                sub_id text NOT NULL,
    	                vel integer NOT NULL,
                        mode char,
                        lambda number,
                        mu number,
    	                FOREIGN KEY (sub_id) REFERENCES subject(id),    
    	                PRIMARY KEY (id, sub_id)        
    	             );
                """
    sql.execute(query)


def select_all(sql: Cursor, table: str, orderBy=None):
    if orderBy is None:
        query = 'SELECT *  FROM {};'.format(table)
    else:
        query = 'SELECT *  FROM {} ORDER BY {};'.format(table, orderBy)
    sql.execute(query)
    return sql.fetchall()


def select_where(sql: Cursor, table: str, clause: str):
    query = 'SELECT * from {} WHERE {}'.format(table, clause)
    sql.execute(query)
    return sql.fetchall()


def populate_subjects(sql: Cursor, elems):
    query = 'INSERT INTO subject(id, sub_group, sub_num) VALUES(?,?,?)'
    for elem in elems:
        sql.execute(query, elem)


def populate_trials(sql: Cursor, elems):
    query = 'INSERT INTO trial(id, sub_id, vel, mode) VALUES(?, ?, ?, ?)'
    for elem in elems:
        sql.execute(query, elem)


def update_trial(sql: Cursor, elem):
    query = 'UPDATE trial SET lambda = ?, mu = ? WHERE id = ? and sub_id = ?'
    sql.execute(query, elem)


conn = create_connection('resources/hrv_pg/dryad_data/subjects.db')
sql = conn.cursor()
create_tables(sql)
conn.commit()

SPEEDS_PATH = 'resources/hrv_pg/dryad_data/walking_speeds.txt'
TRIALS = dryad_mgr.acquire_trials_list(SPEEDS_PATH)

all_trials = select_all(sql, 'trial', 'sub_id')
if len(all_trials) == 0:
    subjects: Set[Tuple] = set()
    trials: List[Tuple] = []
    for trial in TRIALS:
        sub = (trial.group.to_char() + str(trial.sub_id), trial.group.to_char(), trial.sub_id)
        subjects.add(sub)
        t = (trial.trial_id, trial.group.to_char() + str(trial.sub_id), trial.vel, trial.mode.to_char())
        trials.append(t)
    populate_subjects(sql, subjects)
    populate_trials(sql, trials)
    conn.commit()

processed_trials = select_where(sql, 'trial', 'lambda<=0 or mu>=0 or mode=\'e\'')
processed_ids = [(t[0], t[1]) for t in processed_trials]
print(len(processed_ids))

updated_trials = set()
index = 0
for trial in TRIALS:
    if (trial.trial_id, trial.group.to_char() + str(trial.sub_id)) not in processed_ids:
        try:
            trial = dryad_mgr.fill_emg_signals('resources/hrv_pg/dryad_data', [trial], dump=False)[0]
            est_rate = dryad_mgr.process_trial(trial, dump=False)
            to_update = (float(est_rate) if est_rate < 0 else None,
                         float(est_rate) if est_rate >= 0 else None, trial.trial_id,
                         trial.group.to_char() + str(trial.sub_id))
            update_trial(sql, to_update)
            conn.commit()
        except ValueError:
            print('trial could not be processed')
        index += 1
        print('{} processed'.format(index))

processed_trials = select_where(sql, 'trial', 'lambda<=0 or mu >=0')
print(len(processed_trials))

lambdas = [t[4] for t in processed_trials if t[4] is not None]
avg_lambda = np.mean(lambdas)
std_dev_lambda = np.std(lambdas)
print(avg_lambda)
print(std_dev_lambda)

x = np.linspace(avg_lambda - 3 * std_dev_lambda, avg_lambda + 3 * std_dev_lambda, 1000)
plt.plot(x, stats.norm.pdf(x, avg_lambda, std_dev_lambda))

plt.show()

mus = [t[5] for t in processed_trials if t[5] is not None]
avg_mu = np.mean(mus)
std_dev_mu = np.std(mus)
print(avg_mu)
print(std_dev_mu)

x = np.linspace(avg_mu - 3 * std_dev_mu, avg_mu + 3 * std_dev_mu, 1000)
plt.plot(x, stats.norm.pdf(x, avg_mu, std_dev_mu))
plt.show()

sql.close()
conn.close()
