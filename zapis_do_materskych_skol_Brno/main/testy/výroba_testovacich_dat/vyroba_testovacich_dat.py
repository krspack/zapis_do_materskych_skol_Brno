#!/usr/bin/env python
# coding: utf-8

# In[1]:


"""
Skript vygeneruje 5000 fiktivních uchazečů ve věku 2 až 7 let 
s náhodným datem narození, spádovou školkou a dalšími atributy 
převzatými z reálného přihlašovacího formuláře z webu zapisdoms.brno.cz. 
Data ulozi do souboru deti.csv a skolky.csv.
"""
import csv
import pandas as pd
import random
import copy
import numpy as np
import datetime
from dateutil.relativedelta import relativedelta
import sys
from matching.games import HospitalResident
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

random.seed(11)

# Seznam školek stažený z webu, mínus školky s nulovou kapacitou
skolky = pd.read_csv('../data/skolky_scrap_2023_12_12.csv')
skolky = skolky[skolky['volna_mista'] != 0]
skolky_spadove = skolky[skolky['mc'] != "brno"] # 2 skolky maji spadovou oblast cele Brno
skolky.to_csv('skolky.csv')

# výroba fiktivních uchazečů
def get_random_birthday(deti_df):    
    # Fuknce generuje náhodná data narození dětí ve věku 2 až 7 let. 
    today = datetime.date.today()
    current_year = today.year
    birthday_range = datetime.date(current_year-2, 8, 30) - datetime.date(current_year-7, 5, 31)    # (current_year-7, 5, 31) je vysledkem odhadu
    def get_birthday():
        random_integer = random.randint(0, birthday_range.days)
        random_birthday = datetime.date(current_year-2, 8, 30) - relativedelta(days = random_integer)
        return random_birthday
    deti_df['datum_narozeni'] = None
    deti_df['datum_narozeni'] = deti_df['datum_narozeni'].apply(lambda x: get_birthday())
    return 

def get_random_schools(skolky_df, skolky_spadove_df, deti_df):
    def get_random_number():
        return random.randint(1, 1000)
        
    def get_random_choice(schools_list):
        try:
            choice = random.choice(schools_list)
            schools_list.remove(choice)  
            return choice
        except:
            return -1  
            
    spadovost = []
    for index, row in skolky_spadove_df.iterrows():
        for i in range(row['spadove_deti']):
            spadovost.append(str(row['skolka_id']))
 
    deti_df['spadova_skolka'] = deti_df.apply(lambda row: get_random_choice(spadovost), axis = 1)
    deti_df['skolka_sourozence'] = deti_df.apply(lambda row: row['spadova_skolka'] if get_random_number() % 23 == 0 else (get_random_choice(list(skolky_df.skolka_id)) if (get_random_number() % 24 == 0) else -1), axis = 1)
    return

def je_bydliste_brno(deti_df):
    # U deti bez spadove skolky funkce doplni, ze maji stale bydliste mimo Brno. (Kauzalita je ale opacna.)
    deti_df['bydliste_brno'] = deti_df.apply(lambda row: False if (int(row['spadova_skolka']) < 0) else True, axis = 1)
    return

def je_prodlouzena_dochazka(deti_df):
    # Funkce u většiny dětí zvolí, že nepožadují prodlouženou docházku. Počet je opět odhadu. 
    def get_random_number(): 
        return random.randint(1, 1000)
    deti_df['prodlouzena_dochazka'] = deti_df.apply(lambda row: True if (get_random_number() % 33 == 0) else False, axis = 1)

def get_names(jmena_divky, jmena_hosi):
    # vyrobi jména fiktivním uchazečům. Vstupem jsou nejběžnější česká a slovenská křestní jména a příjmení.
    first_names_0, surnames_0 = [], []
    with open(jmena_divky, newline='') as file:
        fi = csv.reader(file, delimiter=';')
        for line in fi:
            first_names_0.append(line[0])
            surnames_0.append(line[1])
    divky = [{'jmeno': i + ' Test ' + ii} for i in first_names_0 for ii in surnames_0]

    first_names_1, surnames_1 = [], []
    with open(jmena_hosi, newline='') as file:
        f = csv.reader(file, delimiter=';')
        for line in f:
            first_names_1.append(line[0])
            surnames_1.append(line[1])
    hosi = [{'jmeno': i + ' Test ' + ii} for i in first_names_1 for ii in surnames_1]

    return divky, hosi
    
divky, hosi = get_names('divky.csv', 'hosi.csv')

for i in hosi:
    i['pohlavi'] = 'M'
for i in divky:
    i['pohlavi'] = 'F'

deti = hosi + divky
deti = pd.DataFrame(deti)
new_col = deti.index
deti.insert(0, 'dite_id', new_col)
deti = deti.sample(frac = 1) 

get_random_birthday(deti)
get_random_schools(skolky, skolky_spadove, deti)
je_bydliste_brno(deti)
je_prodlouzena_dochazka(deti)

# deti.to_csv('deti.csv')


# In[ ]:





# In[ ]:




