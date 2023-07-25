
import csv
import pandas as pd
import copy
import numpy as np



skolky = pd.read_csv('input_data/skolky.csv')
deti = pd.read_csv('deti.csv')

# skolky = pd.read_csv('input_data/test_skolky_input.csv', delimiter = ';')
# deti = pd.read_csv('test_deti.csv')

merged = pd.merge(deti, skolky[['id', 'mc']], left_on = 'spadova_skolka', right_on = 'id')   # diky tomu ziskame info o mestske casti ditete
merged.reset_index(inplace = True)
merged.drop(['Unnamed: 0'], axis = 1, inplace = True)

def calculate_points_one_child(id_child):
    copy_skolky = copy.deepcopy(skolky)
    copy_skolky['id_dite'] = id_child
    copy_skolky = copy_skolky[copy_skolky['volna_mista'] > 0]
    df_one_child = pd.merge(copy_skolky, merged, left_on ='id_dite', right_on = 'id_dite', how = 'left')
    df_one_child.rename(columns={'Unnamed: 0': 'id_skolka', 'mc_x': 'mc_skolka', 'mc_y': 'mc_dite'}, inplace = True)
    df_one_child.drop(['id_x', 'id_y', 'index'], axis = 1, inplace = True)
    df_one_child['body_spadovost'] = df_one_child.apply(lambda row: 250 if row['bydliste_brno'] == True else 0, axis = 1)
    df_one_child['body_spadovost'] = df_one_child.apply(lambda row: 500 if row['mc_skolka'] == row['mc_dite'] else row['body_spadovost'], axis = 1)
    df_one_child['body_spadovost'] = df_one_child.apply(lambda row: 750 if (row['id_skolka'] == row['spadova_skolka']) and (row['prioritni_vek'] == False) else row['body_spadovost'], axis = 1)
    df_one_child['body_spadovost'] = df_one_child.apply(lambda row: 1000 if (row['id_skolka'] == row['spadova_skolka']) and (row['prioritni_vek'] == True) else row['body_spadovost'], axis = 1)
    df_one_child['body_sourozenec'] = df_one_child.query('prioritni_vek == True and skolka_sourozence == id_skolka').apply(lambda x: 10, axis = 1)
    df_one_child['body_sourozenec'].fillna(0, inplace = True)

    # dve specialni skolky:
    df_one_child.loc[df_one_child['id_skolka'].isin([137, 138]), 'body_spadovost'] = df_one_child.loc[df_one_child['id_skolka'].isin([137, 138]), 'body_spadovost'].apply(lambda x: 1000)
    df_one_child.loc[df_one_child['id_skolka'].isin([137, 138]), 'body_sourozenec'] = df_one_child.loc[df_one_child['id_skolka'].isin([137, 138]), 'body_sourozenec'].apply(lambda x: 10)
    df_one_child['body_prodlouz_provoz'] = 0
    df_one_child.loc[df_one_child['id_skolka'].isin([137, 138]), 'body_prodlouz_provoz'] = df_one_child.loc[df_one_child['id_skolka'].isin([137, 138]), 'body_prodlouz_provoz'].apply(lambda x: 50 if 'prodlouzena_dochazka' == True else 0)

    # nezohledneni bodu za "Den věku dítěte v roce narození" v pripade spadovych skolek
    df_one_child.loc[df_one_child['spadova_skolka'] == df_one_child['id_skolka'], 'body_za_vek_dny'] = df_one_child.loc[df_one_child['spadova_skolka'] == df_one_child['id_skolka'], 'body_za_vek_dny'].apply(lambda x: 0)

    # soucet bodu
    df_one_child['body_soucet'] = df_one_child['body_sourozenec'] + df_one_child['body_spadovost'] + df_one_child['body_za_vek_roky'] + df_one_child['body_za_vek_dny'] + df_one_child['body_prodlouz_provoz']
    d_pivoted = df_one_child.pivot(index = 'id_dite', columns = 'id_skolka', values = 'body_soucet')
    d_pivoted = pd.merge(deti, d_pivoted, how = 'right', left_on = 'id_dite', right_on = 'id_dite')
    return d_pivoted
all_children_schools = calculate_points_one_child(0)

for i in range(1, len(merged)):
    one_child_pivoted_df = calculate_points_one_child(i)
    all_children_schools = pd.concat([all_children_schools, one_child_pivoted_df])


# all_children_schools.to_csv('test_all_children_schools.csv')

all_children_schools.to_csv('all_children_schools.csv')



































