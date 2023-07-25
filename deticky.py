
# script generates a dataframe with 3200 fake identities aged 2-7

"""
radek 94 a dal / preskladat
rozdelit generator hodnot a vypocet hodnot:
melo by byt mozne zadat nove dite s polozkami jmeno, datum narozeni, mc, spadova_skolka, bydliste_brno, prodlouzena_dochazka, skolka_sourozence
zvysit pocet deti mimobrnenskych

zjistit ty body za prodlouzenou dochazku a pak upravit v sekci Vypocet - dve specialni skolky
"""

import csv
import datetime
from dateutil.relativedelta import relativedelta
import random
import pandas as pd
import copy

random.seed(11)

schools_mc = 135  # 3 # to test
schools_all = 137  # 3 # to test

first_names_0 = []
surnames_0 = []
with open('divky.csv', newline='') as file:
    fi = csv.reader(file, delimiter=';')
    for line in fi:
        first_names_0.append(line[0])
        surnames_0.append(line[1])

girls = []
for i in first_names_0:
    for ii in surnames_0:
        girls.append(i + ' ' + ii)
girls = [{'jmeno': i} for i in girls]

first_names_1 = []
surnames_1 = []
with open('hosi.csv', newline='') as file:
    f = csv.reader(file, delimiter=';')
    for line in f:
        first_names_1.append(line[0])
        surnames_1.append(line[1])

boys = []
for i in first_names_1:
    for ii in surnames_1:
        boys.append(i + ' ' + ii)
boys = [{'jmeno': i} for i in boys]

def get_random_birthday():    # vymyslet korekci - zvysit pocet 3 a 4 letych na ukor starsich - ti uz v nejake skolce jsou z vetsiny...
    today = datetime.date.today()
    current_year = today.year
    birthday_range = datetime.date(current_year-2, 8, 30) - datetime.date(current_year-7, 5, 31)    # (current_year-7, 5, 31) je vysledkem odhadu
    random_integer = random.randint(0, birthday_range.days)
    random_birthday = datetime.date(current_year-2, 8, 30) - relativedelta(days = random_integer)
    return random_birthday
random_birthday = get_random_birthday()

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

def get_random_school(number):
    spadova_skolka = random.randint(0, schools_mc)   # randomizace zajisti rovnomerne rozmisteni 'deti' do spadovych oblasti skolek
    if number%10 == 0:                          # pocet sourozencu ve skolkach je vysledkem odhadu
        skolka_sourozence = spadova_skolka
    if number%20 == 0:
        skolka_sourozence = random.randint(1, schools_all)  # dtto
    else:
        skolka_sourozence = None                 # dtto
    return spadova_skolka, skolka_sourozence

get_points_days = lambda x: 0 if x < 0 else x*0.02
get_bydliste = lambda x: False if x%21 == 0 else True    # randomizace, staoveny pomer deti z Brna a mimobrnenskych je vysledkem odhadu
je_prioritni_vek = lambda x: True if 3 <= x <= 6 else False
je_prodlouzena_dochazka = lambda x: True if x%33 == 0 else False   # randomizace, pocet deti s pozadavkem prodlouzene dochazky je vysledkem odhadu


for i in boys:
    i['pohlavi'] = 'M'
for i in girls:
    i['pohlavi'] = 'F'

children = boys + girls

for i in children:
    i['datum_narozeni'] = get_random_birthday()
    i['vek'] = get_age(i['datum_narozeni'])[0]
    i['vek_dny_srpen31'] = get_age(i['datum_narozeni'])[1]
    i['body_za_vek_roky'] = get_points_years(i['vek'], i['vek_dny_srpen31'])
    i['body_za_vek_dny'] = get_points_days(i['vek_dny_srpen31'])
    i['spadova_skolka'] = get_random_school(i['vek_dny_srpen31'])
    i['skolka_sourozence'] = i['spadova_skolka'][1]
    i['spadova_skolka'] = i['spadova_skolka'][0]
    i['bydliste_brno'] = get_bydliste(i['vek_dny_srpen31'])
    i['prioritni_vek'] = je_prioritni_vek(i['vek'])
    i['prodlouzena_dochazka'] = je_prodlouzena_dochazka(i['vek_dny_srpen31'])


children_df = pd.DataFrame(children)
new_col = children_df.index
children_df.insert(0, 'id_dite', new_col)
children_df.to_csv('deti.csv')

"""
children_test = children_df[:20]
children_test.to_csv('test_deti.csv')
"""





















