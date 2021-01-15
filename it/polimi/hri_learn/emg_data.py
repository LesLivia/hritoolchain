import sqlite3
from sqlite3 import Error, Cursor, OperationalError
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
    try:
        query = """
                    ALTER TABLE trial
                    ADD lambda_sick number;
                """
        sql.execute(query)
        query = """
                    ALTER TABLE trial
                    ADD mu_sick number;
                """
        sql.execute(query)
    except OperationalError:
        print('columns already created')


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


def filter_trials(sql: Cursor, clause: str):
    query = """SELECT * FROM trial t JOIN subject s
                ON t.sub_id=s.id
                WHERE {}""".format(clause)
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


def update_trial_sick(sql: Cursor, elem):
    query = 'UPDATE trial SET lambda_sick = ?, mu_sick = ? WHERE id = ? and sub_id = ?'
    sql.execute(query, elem)


def fix_rates(sql: Cursor):
    query = 'UPDATE trial SET mu = -lambda WHERE mode=\'r\''
    sql.execute(query)
    query = 'UPDATE trial SET mu_sick = -lambda_sick WHERE mode=\'r\''
    sql.execute(query)


def clear_trials(sql: Cursor):
    query = 'UPDATE trial SET lambda = ?, mu = ? WHERE id>0'
    sql.execute(query, (None, None))


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

# clear_trials(sql)
# conn.commit()

processed_trials = select_where(sql, 'trial', 'lambda<=0 or mu>=0 or mode=\'e\'')
processed_ids = [(t[0], t[1]) for t in processed_trials]

updated_trials = set()
index = 0
for trial in TRIALS:
    if (trial.trial_id, trial.group.to_char() + str(trial.sub_id)) not in processed_ids:
        try:
            trial = dryad_mgr.fill_emg_signals('resources/hrv_pg/dryad_data', [trial], dump=False)[0]
            est_rate = dryad_mgr.process_trial(trial, dump=False, cf=0.0001)
            to_update = (float(est_rate) if est_rate < 0 else None,
                         float(est_rate) if est_rate >= 0 else None, trial.trial_id,
                         trial.group.to_char() + str(trial.sub_id))
            update_trial(sql, to_update)
            conn.commit()
        except ValueError:
            print('trial could not be processed')
        index += 1
        print('{} processed'.format(index))

processed_trials = select_where(sql, 'trial', 'lambda_sick<=0 or mu_sick>=0 or mode=\'e\'')
processed_ids = [(t[0], t[1]) for t in processed_trials]

updated_trials = set()
index = 0
for trial in TRIALS[:100]:
    if (trial.trial_id, trial.group.to_char() + str(trial.sub_id)) not in processed_ids:
        try:
            trial = dryad_mgr.fill_emg_signals('resources/hrv_pg/dryad_data', [trial], dump=False)[0]
            est_rate = dryad_mgr.process_trial(trial, dump=False, cf=0.001)
            to_update = (float(est_rate) if est_rate < 0 else None,
                         float(est_rate) if est_rate >= 0 else None, trial.trial_id,
                         trial.group.to_char() + str(trial.sub_id))
            update_trial_sick(sql, to_update)
            conn.commit()
        except ValueError:
            print('trial could not be processed')
        index += 1
        print('{} processed'.format(index))

fix_rates(sql)
conn.commit()

processed_trials = select_where(sql, 'trial', '(lambda<=0 and lambda_sick<=0) or (mu>=0 and mu_sick>=0)')
print('{} available trials'.format(len(processed_trials)))

velocities = np.arange(1, 6)
COLORS = ['#CCCCCC', '#AAAAAA', '#999999', '#555555', '#000000']

for g in dryad_mgr.Group:
    lambdas_mean = []
    lambdas_std = []
    mus_mean = []
    mus_std = []
    lambdas_sick_mean = []
    lambdas_sick_std = []
    mus_sick_mean = []
    mus_sick_std = []

    for v in velocities:
        clause = '((lambda<=0 and lambda_sick<=0) or (mu>=0 and mu_sick>=0)) and s.sub_group=\'{}\' and vel={}'.format(
            g.to_char(), v)
        _trials = filter_trials(sql, clause)

        train_perc = 0.8
        print('{}/{} trials for training...'.format(int(train_perc * len(_trials)), len(_trials)))
        lambdas = [t[4] for t in _trials[:int(train_perc * len(_trials))] if t[3] == 'w']
        lambdas_mean.append(np.mean(lambdas))
        lambdas_std.append(np.std(lambdas))
        lambdas_sick = [t[6] for t in _trials[:int(train_perc * len(_trials))] if t[3] == 'w']
        lambdas_sick_mean.append(np.mean(lambdas_sick))
        lambdas_sick_std.append(np.std(lambdas_sick))

        mus = [t[5] for t in _trials[:int(train_perc * len(_trials))] if t[3] == 'r']
        mus_mean.append(np.mean(mus))
        mus_std.append(np.std(mus))
        mus_sick = [t[7] for t in _trials[:int(train_perc * len(_trials))] if t[3] == 'r']
        mus_sick_mean.append(np.mean(mus_sick))
        mus_sick_std.append(np.std(mus_sick))

    z_score = 2

    plt.figure(figsize=(10, 5))
    plt.title('Fatigue Rate Distribution, {} healthy group'.format(g.to_char()))
    for (index, rate) in enumerate(lambdas_mean):
        x = np.linspace(rate - z_score * lambdas_std[index], rate + z_score * lambdas_std[index], 1000)
        label = 'v.{}, mean:{:.6f}, sigma:{:.6f}'.format(velocities[index], rate, lambdas_std[index])
        plt.plot(x, stats.norm.pdf(x, rate, lambdas_std[index]), label=label, color=COLORS[index], linewidth=1)
    plt.legend()
    plt.show()

    plt.figure(figsize=(10, 5))
    plt.title('Resting Rate Distribution, {} healthy group'.format(g.to_char()))
    for (index, rate) in enumerate(mus_mean):
        x = np.linspace(rate - z_score * mus_std[index], rate + z_score * mus_std[index], 1000)
        label = 'v.{}, mean:{:.6f}, sigma:{:.6f}'.format(velocities[index], rate, mus_std[index])
        plt.plot(x, stats.norm.pdf(x, rate, mus_std[index]), label=label, color=COLORS[index], linewidth=1)
    plt.legend()
    plt.show()

    plt.figure(figsize=(10, 5))
    plt.title('Fatigue Rate Distribution, {} sick group'.format(g.to_char()))
    for (index, rate) in enumerate(lambdas_sick_mean):
        x = np.linspace(rate - z_score * lambdas_sick_std[index], rate + z_score * lambdas_sick_std[index], 1000)
        label = 'v.{}, mean:{:.6f}, sigma:{:.6f}'.format(velocities[index], rate, lambdas_sick_std[index])
        plt.plot(x, stats.norm.pdf(x, rate, lambdas_sick_std[index]), label=label, color=COLORS[index], linewidth=1)
    plt.legend()
    plt.show()

    plt.figure(figsize=(10, 5))
    plt.title('Resting Rate Distribution, {} sick group'.format(g.to_char()))
    for (index, rate) in enumerate(mus_sick_mean):
        x = np.linspace(rate - z_score * mus_sick_std[index], rate + z_score * mus_sick_std[index], 1000)
        label = 'v.{}, mean:{:.6f}, sigma:{:.6f}'.format(velocities[index], rate, mus_sick_std[index])
        plt.plot(x, stats.norm.pdf(x, rate, mus_sick_std[index]), label=label, color=COLORS[index], linewidth=1)
    plt.legend()
    plt.show()

sql.close()
conn.close()
