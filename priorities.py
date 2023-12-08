
import csv
import pandas as pd
import random
from collections import defaultdict
from matching.games import HospitalResident  # https://matching.readthedocs.io/en/latest/py-modindex.html
import json
import sys

"""
neslo by to randomizovane prilepit rovnou k tabulce deti? slo
pokracuju v myslence oddelit random vstup a vypocet
"""

random.seed(11)

"""
myslenka: nakonec zbydou volna mista v nekterych skolkach a zaroven nektere deti se nikam nedostanou. To je ale ok: pokud nepozadali o misto v te skolce vubec,
asi nechteji tak daleko jezdit. Nedostanou se tedy nikam...  Ale udelat druhe kolo: mit verejnou informaci, ktere skolky jeste maji volna mista a prostrednictvim
stejneho webu o ne soutezit.

"""

"""
skolky = pd.read_csv('input_data/test_skolky_nizke_kapacity.csv')
skolky = skolky[skolky['volna_mista'] > 0]

deti = pd.read_csv('test_deti.csv')
points = pd.read_csv('test_all_children_schools.csv')

"""
with open('input_data/skolky_test.csv', 'r') as s:
    skolky = pd.read_csv(s)
    skolky = skolky[skolky['volna_mista'] > 0]

with open('dummy_input_data/deti_test.csv', 'r') as d:
    deti = pd.read_csv(d)

with open('test_all_children_schools.csv', 'r') as p:
    points = pd.read_csv(p)


schools_capacities = skolky[['skolka_id', 'volna_mista']]
schools_capacities = schools_capacities.to_dict('dict')['volna_mista']
schools_capacities = {str(k):v for k, v in schools_capacities.items()}

def flip_priorities(priorities_dict):
    chosen = defaultdict(set)
    for child, chosen_schools in priorities_dict.items():
        for school in chosen_schools:
            chosen[school].add(child)
    return chosen
schools_chosen_by_applicants = flip_priorities(priorities)

def get_schools_longlists(points_df, chosen_schools):
    """
    Kazda skolka si oboduje ty deti, ktere se na ni hlasi. Vysledkem je poradi.
    """
    chosen_schools_int = {}   # pretypovani pro ucely teto funkce
    for k, v in chosen_schools.items():
        vv = {int(x) for x in v}
        chosen_schools_int[k] = vv

    longlists = {}
    longlists_with_points = {}
    schools = chosen_schools_int.keys()
    for s in schools:
        df = points_df[['id_dite', s]]   # vyrobi tabulku jen s dvema sloupci: vsechny deti a jejich body pro skolu s
        df = df[df['id_dite'].isin(chosen_schools_int[s])]  # vyfiltruje deti, ktere se hlasi na skolu s
        df.sort_values(by=s, ascending=False, inplace=True)  # seradi je od tech, co maji nejvic bodu
        df.reset_index(inplace = True, drop = True)
        sorted_longlist = tuple(df['id_dite'])
        longlists[s] = [str(x) for x in sorted_longlist]  # vysledkem je slovnikove heslo {skola: serazene vsechny deti, co se na ni hlasi}.
    return longlists
schools_longlists = get_schools_longlists(points, schools_chosen_by_applicants)

print(schools_longlists)


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












