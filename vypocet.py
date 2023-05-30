
import csv
import pandas as pd
import copy
import numpy as np

skolky = pd.read_csv('skolky.csv')
deti = pd.read_csv('deti.csv')

"""
vypocitat body pro kazde dite pro kazdou skolku
ulozit do tabulky ("vysledkove") "body"
potom vyrobit u deti randomovy seznam priorit
ulozit do tabulky "prideleno"
"""


"""
# jinak
schools_ids = range(0, len(skolky))
schools_ids = [str(x) for x in schools_ids]
empty_df = pd.DataFrame(columns = schools_ids)
vypocet = pd.concat([deti, empty_df], axis = 1)
print(vypocet.head())
"""

# jeste jinak
# if vypocet['spadova_skolka'] == vypocet['skolka_sourozence']

vypocet = pd.merge(deti, skolky[['id', 'mc']], left_on = 'spadova_skolka', right_on = 'id')
vypocet.to_csv('vypocet.csv')

# for i in skolky['id']:
"""
def spocitej_body(i):
    body = vypocet['body_za_vek']
    if vypocet['spadova_skolka'] == i:
        body += 1000
    elif vypocet['mc'] == skolky.iloc[i].mc:
        body += 500
    elif vypocet['bydliste_brno'] == True:
        body += 250
    return body
"""
"""
def spocitej_body(spadova, mestska_cast, vekove_body):
    body = vekove_body
    if spadova == 6:
        body += 1000
    elif mestska_cast == skolky.iloc[6].mc:
        body += 500
    return body

result = spocitej_body(vypocet['spadova_skolka'], vypocet['mc'], vypocet['body_za_vek'])
print(result)
"""
""" verze 1, kde ale neni vyresene, jak se na konci bude prehledne videt, kdo ma u jake skolky jake body
novy sloupec: secti body za vek, body za brno a body za spadovost == udaj pro spadovou skolku
dalsi sloupec: secti body_za_vek, body jen za mc == udaj pro skolky ve stejne mc
dalsi: secti body_za_vek a body jen za brno if true == udaj pro skolky vsechny ostatni
dalsi: sourozenec
dalsi: skolky pro cele brno + u nich doklad o potrebe prodlouzeneho provozu
dalsi: vyresit neprioritni deti s hodne body

"""
""" verze 2, pocitat to jen pro jedno dite
az nakonec tabulku zpivotovat
a pak ji napojit na velkou gigatabulku
"""


d0 = vypocet.iloc[:2]
d0.to_csv('d0.csv')
d0 = d0.drop('id', axis = 1)
d0.rename(columns={'Unnamed: 0': 'id_dite'}, inplace = True)  # pozor, je duplicitni, holky a kluci
d0o = copy.deepcopy(skolky)
d0o['id_dite'] = 0   # do tabulky skolek pridam jen jedno dite. Pres tento sloupec tabulku napojim na tabulku Dite
d0o = pd.merge(d0o, d0, left_on ='id_dite', right_on = 'id_dite', how = 'left')
d0o.rename(columns={'Unnamed: 0': 'id_skolka', 'mc_x': 'mc_skolka', 'mc_y': 'mc_dite'}, inplace = True)

def is_priority(x, y, age):
    if (x == y) & np.greater(age, 3) & np.greater(6, age):
        return True
    return False

# d0o['prioritni_vek'] = is_priority(d0o['id_skolka'], d0o['spadova_skolka'], d0o['vek'])




"""
def vypocet(dite, skolka):
    body = dite.body_za_vek
    if skolka = dite.spadova_skola:
        body += 1000
    elif skolka.mc == dite.mc:
        body += 750
    else:
        body += 500



"""



















