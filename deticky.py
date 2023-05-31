
# script generates a dataframe with 3200 fake identities aged 2-7

import csv
import datetime
from dateutil.relativedelta import relativedelta
import random
import pandas as pd
import copy


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
    difference = schoolyear_start - birthday - relativedelta(days = 1)   # correction to get the same result as zapisdoms.brno.cz

    schoolyear_start_current = datetime.date(current_year, 8, 31)
    age_in_years = int(round((schoolyear_start_current - schoolyear_start).days/365, 0))
    if difference.days < 0:
        age_in_years -= 1
    return age_in_years, difference.days

def calculate_points_age(age, age_difference_days):
    options = {7: 2160, 6: 2120, 5: 2080, 4: 2040, 3: 2000, 2: 0, 1: 0}
    get_points_years = lambda x: 1000 if (x == 2 and age_difference_days < 0) else options[x]
    points_years = get_points_years(age)
    get_points_days = lambda x: 0 if age_difference_days < 0 else age_difference_days*0.02
    points_days = get_points_days(age_difference_days)
    return points_years + points_days

def get_random_school(number):
    spadova_skolka = random.randint(0, 135)   # randomizace zajisti rovnomerne rozmisteni 'deti' do spadovych oblasti skolek
    if number%10 == 0:                          # pocet sourozencu ve skolkach je vysledkem odhadu
        skolka_sourozence = spadova_skolka
    if number%20 == 0:
        skolka_sourozence = random.randint(1, 137)  # dtto
    else:
        skolka_sourozence = None                 # dtto
    return spadova_skolka, skolka_sourozence

get_bydliste = lambda x: False if x%101 == 0 else True    # randomizace, stamoveny pomer True a False je vysledkem odhadu
je_prioritni_vek = lambda x: True if 3 <= x <= 6 else False
je_prodlouzena_dochazka = lambda x: True if x%33 == 0 else False   # randomizace, stamoveny pomer True a False je vysledkem odhadu

for i in boys:
    i['pohlavi'] = 'M'
    i['datum_narozeni'] = get_random_birthday()
    i['vek'] = get_age(i['datum_narozeni'])[0]
    i['vek_dny_srpen31'] = get_age(i['datum_narozeni'])[1]
    i['body_za_vek'] = calculate_points_age(i['vek'], i['vek_dny_srpen31'])
    i['spadova_skolka'] = get_random_school(i['vek_dny_srpen31'])
    i['skolka_sourozence'] = i['spadova_skolka'][1]
    i['spadova_skolka'] = i['spadova_skolka'][0]
    i['bydliste_brno'] = get_bydliste(i['vek_dny_srpen31'])
    i['prioritni_vek'] = je_prioritni_vek(i['vek'])
    i['prodlouzena_dochazka'] = je_prodlouzena_dochazka(i['vek_dny_srpen31'])

for i in girls:
    i['pohlavi'] = 'F'
    i['datum_narozeni'] = get_random_birthday()
    i['vek'] = get_age(i['datum_narozeni'])[0]
    i['vek_dny_srpen31'] = get_age(i['datum_narozeni'])[1]
    i['body_za_vek'] = calculate_points_age(i['vek'], i['vek_dny_srpen31'])
    i['spadova_skolka'] = get_random_school(i['vek_dny_srpen31'])
    i['skolka_sourozence'] = i['spadova_skolka'][1]
    i['spadova_skolka'] = i['spadova_skolka'][0]
    i['bydliste_brno'] = get_bydliste(i['vek_dny_srpen31'])
    i['prioritni_vek'] = je_prioritni_vek(i['vek'])
    i['prodlouzena_dochazka'] = je_prodlouzena_dochazka(i['vek_dny_srpen31'])      # toto bude nutne zohlednit v rozhodovani o prijeti

boys_df = pd.DataFrame(boys)
girls_df = pd.DataFrame(girls)
children = pd.concat([boys_df, girls_df]).reset_index(drop = True)


children.to_csv('deti.csv')



















