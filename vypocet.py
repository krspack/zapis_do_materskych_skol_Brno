
import csv
import pandas as pd
import copy
import numpy as np
import datetime
from dateutil.relativedelta import relativedelta
import sys
from matching.games import HospitalResident

"""

jednoduche testy:
pocet deti na vstupu a na vystupu je stejny (tech, co se nekam dostaly, a tech, co se nikam nedostaly)
deti neskonci ve skolce, co si samy nevybraly
kapacity skolek jsou naplneny

slozitejsi testy:
skript mimo generuje sady dummy dat a ty se prohaneji algoritmem
u tech dummy dat musi byt jasne patrne, kde maji skoncit - napriklad se jmenuji podle veku a mestske casti apod
pak je mozne proverit pouhym prehlednutim vysledku, ze to matchuje dobre

vymyslet ruzne testovaci scenare na mensich sadach dat. Napriklad:
1. vsichni chteji na skolku 1 nebo 2. Je to tak, ze kdo vezme na milost i skolku 3, ten tam skonci, protoze jini tam nechteji? Ne.
2.
"""



# skolky = pd.read_csv('input_data/skolky.csv')
# deti = pd.read_csv('deti.csv')

skolky = pd.read_csv('input_data/skolky_test.csv', delimiter = ',')
deti = pd.read_csv('deti_test.csv')
prihlasky = pd.read_csv('prihlasky_test.csv')

# vyrob input c. 1 pro funkci rozrazeni deti: slovnik typu "dite a seznam skolek, kam se hlasi"
def get_priorities(prihlasky_df):
    prihlasky_copy = prihlasky_df.copy()
    prihlasky_copy['dite'] = prihlasky_copy['dite'].astype('str')
    prihlasky_copy['skolka'] = prihlasky_copy['skolka'].astype('str')
    prihlasky_groupedby_kids = prihlasky_copy.groupby('dite')['skolka'].agg(list)
    return prihlasky_groupedby_kids.to_dict()
priorities = get_priorities(prihlasky)


# spocitej pro vsechny deti body na vsechny skolky:
merged = pd.merge(deti, skolky[['skolka_id', 'mc']], left_on = 'spadova_skolka', right_on = 'skolka_id')   # diky tomu ziskame info o mestske casti ditete
merged.reset_index(inplace = True)
merged.drop(['Unnamed: 0'], axis = 1, inplace = True)

def get_age(birthday):
    today = datetime.date.today()
    current_year = today.year
    schoolyear_start = datetime.date(birthday.year, 8, 31)
    difference = schoolyear_start - birthday - relativedelta(days = 1)   # prizpusobeni webu zapisdoms.brno.cz

    schoolyear_start_current = datetime.date(current_year, 8, 31)
    age_in_years = int(round((schoolyear_start_current - schoolyear_start).days/365, 0))
    if difference.days < 0:
        age_in_years -= 1
    return age_in_years, difference.days

def get_points_years(age, age_difference_days):
    options = {7: 2160, 6: 2120, 5: 2080, 4: 2040, 3: 2000, 2: 0, 1: 0}
    calculate_points = lambda x: 1000 if (x == 2 and age_difference_days < 0) else options[x]
    points_years = calculate_points(age)
    return points_years

def calculate_points_one_child(id_child):
    copy_skolky = copy.deepcopy(skolky)
    copy_skolky['id_dite'] = id_child
    copy_skolky = copy_skolky[copy_skolky['volna_mista'] > 0]
    df_one_child = pd.merge(copy_skolky, merged, left_on ='id_dite', right_on = 'id_dite', how = 'left')
    df_one_child.rename(columns={'Unnamed: 0': 'id_skolka', 'mc_x': 'mc_skolka', 'mc_y': 'mc_dite'}, inplace = True)
    df_one_child.drop(['skolka_id_x', 'skolka_id_y', 'index'], axis = 1, inplace = True)

    df_one_child['datum_narozeni'] = pd.to_datetime(df_one_child['datum_narozeni']).dt.date
    df_one_child['vek'] = df_one_child['datum_narozeni'].apply(lambda x: pd.Series(get_age(x)))[0]
    df_one_child['vek_dny_srpen31'] = df_one_child['datum_narozeni'].apply(lambda x: pd.Series(get_age(x)))[1]
    df_one_child['body_za_vek_roky'] = df_one_child.apply(lambda row: get_points_years(row['vek'], row['vek_dny_srpen31']), axis=1)
    df_one_child['body_za_vek_dny'] = df_one_child.apply(lambda row: 0 if (row['vek_dny_srpen31'] < 0) else row['vek_dny_srpen31']*0.02, axis = 1)
    df_one_child['prioritni_vek'] = df_one_child.apply(lambda row: True if (3 <= row['vek'] <= 6) else False, axis = 1)

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
all_points = calculate_points_one_child(0)

for i in range(1, len(deti)):
    one_child_pivoted_df = calculate_points_one_child(i)
    all_points = pd.concat([all_points, one_child_pivoted_df])

all_points.to_csv('test_all_points.csv')

# z bodu vytvor input c. 2 pro rozrazeni deti: slovniky typu "skolka a k ni vsechny deti, co se na ni hlasi, obodovane pro danou skolku"
def get_schools_longlists(points_df, prihlasky_df):
    prihlasky_groupedby_schools = prihlasky_df.groupby('skolka')['dite'].agg(list)
    prihlasky_groupedby_schools = prihlasky_groupedby_schools.to_dict()

    longlists = {}
    schools = prihlasky_groupedby_schools.keys()
    for s in schools:
        all_kids_one_school = points_df[['id_dite', s]].copy()  # Use copy here

        kids_applyint_to_one_school = all_kids_one_school.loc[all_kids_one_school['id_dite'].isin(prihlasky_groupedby_schools[s])].copy()

        kids_applyint_to_one_school.sort_values(by=s, ascending=False, inplace=True)
        kids_applyint_to_one_school.reset_index(inplace=True, drop=True)
        sorted_longlist = tuple(kids_applyint_to_one_school['id_dite'])
        longlists[str(s)] = [str(x) for x in sorted_longlist]
    return longlists

schools_longlists = get_schools_longlists(all_points, prihlasky)

# vytvor input c. 3 pro rozrazeni deti: slovnik skolek s jejich volnymi misty
schools_capacities = skolky[['skolka_id', 'volna_mista']]
schools_capacities = schools_capacities.to_dict('dict')['volna_mista']
schools_capacities = {str(k):v for k, v in schools_capacities.items()}

print('priorities: ', priorities)
print('schools_longlists: ', schools_longlists)
print('schools_capacities: ', schools_capacities)

# finale: rozrazeni deti do skol
sys.setrecursionlimit(10000)
game = HospitalResident.create_from_dictionaries(priorities, schools_longlists, schools_capacities)
schools_shortlists = game.solve(optimal="resident")
print(schools_shortlists)


def save_schools_shortlists(shortlists):
    with open('prijeti_test.csv', 'w') as file:
        writer = csv.DictWriter(file, fieldnames = ['dite', 'skolka', 'poradi'])
        writer.writeheader()
        for school, shortlist in shortlists.items():
            for index, person in enumerate(shortlist):
                d = {'skolka': school, 'poradi': index + 1, 'dite': person}
                writer.writerow(d)
    return
save_schools_shortlists(schools_shortlists)







































