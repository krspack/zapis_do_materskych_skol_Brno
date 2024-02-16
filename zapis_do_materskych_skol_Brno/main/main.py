#!/usr/bin/env python
# coding: utf-8


# Rozřazení
# Algoritmus funkce match() prochází seznam uchazečů a každého přiřadí do školky jeho první volby,
# pokud má tato školka ještě kapacitu. Toto přiřazení ale není finální,
# protože dříve nebo později přijde řada na dítě, jehož nejoblíbenější školka už je plná.
# V tomto okamžiku dojde na porovnávání počtu bodů.
# Pokud má dítě více bodů než poslední uchazeč "nad čarou", do školky se dostane, ale onen poslední z ní vypadává.
# Vyřazeného uchazeče se algoritmus následně pokusí stejným způsobem spárovat se školkou jeho druhé volby a tak stále dokola.
# Tímto způsobem algoritmus přepisuje seznamy dětí pro každou školku, dokud se nedostane do stabilního stavu,
# kdy nikdo nemůže vyřadit nikoho. Tento stav vrátí jako výsledek.
#



import csv
import pandas as pd
import copy
import numpy as np
import datetime
from dateutil.relativedelta import relativedelta
import sys
from matching.games import HospitalResident
import warnings
import subprocess

warnings.filterwarnings("ignore", category=DeprecationWarning)

script_name = sys.argv[0]
oznaceni_testu = str(sys.argv[1] if len(sys.argv) > 1 else 1)

# mezivýsledky uložené skriptem test.py. Pokud se main.py spouští samostatně (ne z testu), je nutné upravit cestu k souborům na "testy/{}_test/deti_test.csv"
deti = pd.read_csv("{}_test/deti_test.csv".format(oznaceni_testu), dtype = {
    'dite_id': 'string',
    'spadova_skolka': 'string',
    'skolka_sourozence': 'string'})

skolky = pd.read_csv("{}_test/skolky_test.csv".format(oznaceni_testu), dtype = {
    'skolka_id': 'string'})

prihlasky = pd.read_csv("{}_test/prihlasky_test.csv".format(oznaceni_testu), dtype = {
   'dite': 'string',
   'skolka': 'string'})

body = pd.read_csv("{}_test/body_test.csv".format(oznaceni_testu), dtype = {
    'dite_id': 'string',
    'spadova_skolka': 'string',
    'skolka_sourozence': 'string'})

# vstup pro funkci "match" c. 1: priority uchazecu
def get_priorities(tabulka_prihlasek):
    # Funkce vytvoří slovník uchazečů a jejich prioritních seznamů školek.
    prihlasky_groupedby_kids = tabulka_prihlasek.groupby('dite')['skolka'].agg(list)
    return prihlasky_groupedby_kids.to_dict()
priority = get_priorities(prihlasky)

"""
def get_priorities_names(priority_dict):
    priorities_names = {}
    for k, v in priority_dict.items():
        k = deti.loc[deti['dite_id'] == int(k), 'jmeno'].item()  + ' (' + k + ')'
        v = [(skolky.loc[skolky['skolka_id'] == int(i), 'nazev_kratky'].item()) + ' (' + i + ')' for i in v]
        priorities_names[k] = v
    return priorities_names
priority_jmena = get_priorities_names(priority)


print("Uchazeči a jejich vybrané školky v pořadí podle oblíbenosti:")
print()
for a, b in priority_jmena.items():
    print(a, b)
"""

# vstup pro funkci "match" c. 2: kapacity skolek
def get_volna_mista(df_skolky):
    # vyrobí slovník "školka: kapacita"
    volna_mista = df_skolky[['skolka_id', 'volna_mista']]
    volna_mista = skolky.set_index('skolka_id')['volna_mista'].to_dict()
    volna_mista = {str(k):v for k, v in volna_mista.items()}
    return volna_mista
volna_mista = get_volna_mista(skolky)

# vstup pro funkci "match" c. 3: priority skolek, vyjadrene poradim obodovanych uchazecu o kazdou skolku
def get_schools_longlists(body_df, prihlasky_df):
    # Z tabulky body_df vybere jen relevantni udaje podle toho, kdo se kam hlásí.
    # výstup je slovnik typu "skolka a k ni vsechny deti, co se na ni hlasi, seřazené podle počtu bodů"
    prihlasky_groupedby_schools = prihlasky_df.groupby('skolka')['dite'].agg(list)
    prihlasky_groupedby_schools = prihlasky_groupedby_schools.to_dict()
    longlists = {}
    schools = prihlasky_groupedby_schools.keys()
    for s in schools:
        all_kids_one_school = body_df[['dite_id', str(s)]].copy()
        all_kids_one_school['dite_id'] = all_kids_one_school['dite_id'].astype(str)
        kids_applyint_to_one_school = all_kids_one_school.loc[all_kids_one_school['dite_id'].isin(prihlasky_groupedby_schools[str(s)])].copy()
        kids_applyint_to_one_school.sort_values(by=str(s), ascending=False, inplace=True)
        kids_applyint_to_one_school.reset_index(inplace=True, drop=True)
        sorted_longlist = tuple(kids_applyint_to_one_school['dite_id'])
        longlists[str(s)] = [str(x) for x in sorted_longlist]
    return longlists

serazeni_uchazeci = get_schools_longlists(body, prihlasky)

"""
def get_longlists_names(longlists_dict):
    longlists_names = {}
    for k, v in longlists_dict.items():
        k = skolky.loc[skolky['skolka_id'] == int(k),'nazev_kratky'].item()
        v = [(deti.loc[deti['dite_id'] == int(i), 'jmeno'].item()) for i in v]
        longlists_names[k] = v
    return longlists_names
serazeni_uchazeci_jmena = get_longlists_names(serazeni_uchazeci)
print()
for k,v in serazeni_uchazeci_jmena.items():
    print(k,v)
    print()
"""

"""
print('priority uchazečů: ', priority)
print('uchazeči o každou školu, seřazení podle bodů: ', serazeni_uchazeci)
print('školky a jejich kapacity: ', volna_mista)
"""

# ------------------------------------------------------------------------------------
sys.setrecursionlimit(10000)
def match(priority_zaku, priority_skolek, kapacity_skolek):
    game = HospitalResident.create_from_dictionaries(priority_zaku, priority_skolek, kapacity_skolek)
    schools_shortlists = game.solve(optimal="resident")
    return schools_shortlists
rozrazeni = match(priority, serazeni_uchazeci, volna_mista)

def save_results(results, test_number):
    nazev_adresare = test_number + '_test'
    with open('{}/vysledek.csv'.format(nazev_adresare), 'w') as file:
        writer = csv.DictWriter(file, fieldnames = ['dite', 'skolka', 'poradi'])
        writer.writeheader()
        for school, shortlist in results.items():
            for index, person in enumerate(shortlist):
                d = {'skolka': school, 'poradi': index + 1, 'dite': person}
                writer.writerow(d)
    return
save_results(rozrazeni, oznaceni_testu)

def get_vysledek_se_jmeny(vysledek, deti_df):
    names = {}
    for k, v in vysledek.items():
        k_nazev = skolky.loc[skolky['skolka_id'] == k.name,'nazev_kratky'].item()
        v_jmeno = [(deti_df.loc[deti_df['dite_id'] == i.name, 'jmeno'].item() + ' (' + i.name + ')') for i in v]
        names[k_nazev + ' (' + k.name + ')'] = v_jmeno
    return names
vysledek_se_jmeny = get_vysledek_se_jmeny(rozrazeni, deti)
print('Výsledky - kdo se dostal kam: ')
print()
for k,v in vysledek_se_jmeny.items():
    print(k,v)
    print()

def kdo_se_nedostal(vysledek, deti_df):
    uspesni_uchazeci = []
    for v in vysledek.values():
        uspesni_uchazeci += v
    uspesni_uchazeci = [_.name for _ in uspesni_uchazeci]

    neuspesni = {}
    for _ in deti_df['dite_id']:
        if _ not in uspesni_uchazeci:
            neuspesni[_] = deti_df.loc[deti_df['dite_id'] == _, 'jmeno'].item()
    return neuspesni
print()
print()
print('Neúspěšní uchazeči:')
print()
for k, v in kdo_se_nedostal(rozrazeni, deti).items():
    print (v + ' (' + str(k) + ')')







