
import csv
import pandas as pd
import random
from collections import defaultdict
from matching.games import HospitalResident  # https://matching.readthedocs.io/en/latest/py-modindex.html
import json
import sys


random.seed(11)

""" # some test input
skolky = pd.read_csv('input_data/test_skolky_nizke_kapacity.csv')
skolky = skolky[skolky['volna_mista'] > 0]

deti = pd.read_csv('test_deti.csv')
points = pd.read_csv('test_all_children_schools.csv')

"""
skolky = pd.read_csv('input_data/skolky.csv')
skolky = skolky[skolky['volna_mista'] > 0]
deti = pd.read_csv('deti.csv')
points = pd.read_csv('all_children_schools.csv')


schools_capacities = skolky[['id', 'volna_mista']]
schools_capacities = schools_capacities.to_dict('dict')['volna_mista']
schools_capacities = {str(k):v for k, v in schools_capacities.items()}

def get_priorities(deti_list, skolky_list):
    priorities = {}
    for _ in range(len(deti_list)):
        vybrane_skolky = set()    # set, aby neslo vybrat jednu skolku jednim ditetem opakovane
        pocet_prihlasek = random.randint(1, len(skolky))    # lze libovolne menit
        for i in range(pocet_prihlasek):
            vybrane_skolky.add(str(random.choice(list(skolky['id']))))
        priorities[str(_)] = tuple(vybrane_skolky)  # tuple, aby vysledkem bylo poradi
    return priorities
priorities = get_priorities(deti, skolky)

def flip_priorities(priorities_dict):
    chosen = defaultdict(set)
    for child, chosen_schools in priorities_dict.items():
        for school in chosen_schools:
            chosen[school].add(child)
    return chosen
schools_chosen_by_applicants = flip_priorities(priorities)

def get_schools_longlists(points_df, chosen_schools):
    """
    Kazda skolka si oboduje vsechny deti, ktere se na ni hlasi. Vysledkem je poradi.
    """
    chosen_schools_int = {}   # pretypovani pro ucely teto funkce
    for k, v in chosen_schools.items():
        vv = {int(x) for x in v}
        chosen_schools_int[k] = vv

    longlists = {}
    # schools = points_df.columns[-(len(skolky)):]
    schools = chosen_schools_int.keys()
    for s in schools:
        df = points_df[['id_dite', s]]   # vyrobi tabulku jen s dvema sloupci: vsechny deti a jejich skore pro skolu s
        df = df[df['id_dite'].isin(chosen_schools_int[s])]  # vyfiltruje deti, ktere se hlasi na skolu s
        df.sort_values(by=s, ascending=False, inplace=True)  # seradi je od tech, co maji nejvic bodu
        df.reset_index(inplace = True, drop = True)
        sorted_longlist = tuple(df['id_dite'])
        longlists[s] = tuple(str(x) for x in sorted_longlist)  # vysledkem je slovnikove heslo {skola: serazene vsechny deti, co se na ni hlasi}
    return longlists
schools_longlists = get_schools_longlists(points, schools_chosen_by_applicants)


sys.setrecursionlimit(10000)
game = HospitalResident.create_from_dictionaries(priorities, schools_longlists, schools_capacities)
schools_shortlists = game.solve(optimal="resident")
print(schools_shortlists)










