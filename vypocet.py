
import csv
import pandas as pd
import copy
import numpy as np

skolky = pd.read_csv('skolky.csv')
deti = pd.read_csv('deti.csv')

merged = pd.merge(deti, skolky[['id', 'mc']], left_on = 'spadova_skolka', right_on = 'id')
merged.reset_index(inplace = True)
merged.rename(columns={'Unnamed: 0': 'id_dite'}, inplace = True)
# merged.to_csv('vypocet.csv')


def calculate_points_one_child(id_child):
    copy_skolky = copy.deepcopy(skolky)
    copy_skolky['id_dite'] = id_child
    d = pd.merge(copy_skolky, merged, left_on ='id_dite', right_on = 'id_dite', how = 'left')
    d.rename(columns={'Unnamed: 0': 'id_skolka', 'mc_x': 'mc_skolka', 'mc_y': 'mc_dite'}, inplace = True)
    d.drop(['id_x', 'id_y', 'index'], axis = 1, inplace = True)
    d['body_spadovost'] = d.apply(lambda row: 250 if row['bydliste_brno'] == True else 0, axis = 1)
    d['body_spadovost'] = d.apply(lambda row: 500 if row['mc_skolka'] == row['mc_dite'] else row['body_spadovost'], axis = 1)
    d['body_spadovost'] = d.apply(lambda row: 750 if (row['id_skolka'] == row['spadova_skolka']) and (row['prioritni_vek'] == False) else row['body_spadovost'], axis = 1)
    d['body_spadovost'] = d.apply(lambda row: 1000 if (row['id_skolka'] == row['spadova_skolka']) and (row['prioritni_vek'] == True) else row['body_spadovost'], axis = 1)
    d['body_sourozenec'] = d.query('prioritni_vek == True and skolka_sourozence == id_skolka').apply(lambda x: 10, axis = 1)
    d['body_sourozenec'].fillna(0, inplace = True)

    # dve specialni skolky:
    d.loc[d['id_skolka'].isin([135, 136]), 'body_spadovost'] = d.loc[d['id_skolka'].isin([135, 136]), 'body_spadovost'].apply(lambda x: 1000)
    d.loc[d['id_skolka'].isin([135, 136]), 'body_sourozenec'] = d.loc[d['id_skolka'].isin([135, 136]), 'body_sourozenec'].apply(lambda x: 10)

    d['body_soucet'] = d['body_sourozenec'] + d['body_spadovost'] + d['body_za_vek']

    d_pivoted = d.pivot(index = 'id_dite', columns = 'id_skolka', values = 'body_soucet')
    return d_pivoted


points = calculate_points_one_child(0)

for i in range(len(merged)):
    one_child_pivoted_df = calculate_points_one_child(i)
    points = pd.concat([points, one_child_pivoted_df])

"""
pro citelnost tabulky lze jeste pridat sloupce jmeno ditete, datum narozeni, a druhy radek indexu: jmeno skolky
"""

# points.to_csv('points.csv')





























