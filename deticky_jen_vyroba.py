
# script generates a dataframe with 3200 fake identities aged 2-7


import csv
import datetime
from dateutil.relativedelta import relativedelta
import random
import pandas as pd
import copy

random.seed(11)

schools_mc = 4 # 135  # 4 # to test
schools_all = 4 # 137  # 4 # to test

first_names_0 = []
surnames_0 = []
with open('dummy_input_data/divky.csv', newline='') as file:
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
with open('dummy_input_data/hosi.csv', newline='') as file:
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

def get_random_school():
    spadova_skolka = random.randint(0, schools_mc-1)   # randomizace zajisti rovnomerne rozmisteni 'deti' do spadovych oblasti skolek
    random_number = random.randint(1, 1000)
    if random_number%10 == 0:                          # pocet sourozencu ve skolkach je vysledkem odhadu
        skolka_sourozence = spadova_skolka
    if random_number%20 == 0:
        skolka_sourozence = random.randint(1, schools_all-1)  #  dtto
    else:
        skolka_sourozence = None                 # dtto
    return spadova_skolka, skolka_sourozence

je_bydliste_Brno = lambda x: False if x%21 == 0 else True    # stanoveny pomer deti z Brna a mimobrnenskych je vysledkem odhadu
je_prodlouzena_dochazka = lambda x: True if x%33 == 0 else False   # pocet deti s pozadavkem prodlouzene dochazky je vysledkem odhadu


for i in boys:
    i['pohlavi'] = 'M'
for i in girls:
    i['pohlavi'] = 'F'

children = boys + girls

for i in children:
    i['datum_narozeni'] = get_random_birthday()
    i['spadova_skolka'] = get_random_school()[0]
    i['skolka_sourozence'] = get_random_school()[1]
    i['bydliste_brno'] = je_bydliste_Brno(random.randint(1, 1000))
    i['prodlouzena_dochazka'] = je_prodlouzena_dochazka(random.randint(1, 1000))


# vytvor pro kazde dite nejaky random list vysnenych skolek, s prihlednutim ke spadove a skolce, kde je sourozenec
def get_priorities(deti_list, pocet_skolek):   # spojit tuto a nasledujici fci do jedne. Ve skriptu Vypocet pak otevrit csv prihlasky jako vstup do funkce get_schools_longlists
    with open('prihlasky_test.csv', 'w') as file:
        writer = csv.DictWriter(file, fieldnames = ['dite', 'skolka', 'poradi'])
        writer.writeheader()
        for _ in range(len(deti_list)):
            vybrane_skolky = set()    # set: nejde vybrat skolku dvakrat. Spadova neni vzdy prvni. Poradi se priradi nahodne - pro random generator je to ok.
            pocet_prihlasek = random.randint(1, pocet_skolek)    # lze libovolne menit
            for i in range(pocet_prihlasek):
                if i == 0:
                    vybrane_skolky.add(str(deti_list[_]['spadova_skolka']))
                if (i == 1 and deti_list[_]['skolka_sourozence'] != None):
                    vybrane_skolky.add(str(deti_list[_]['skolka_sourozence']))
                else:
                    vybrane_skolky.add(str(random.randint(0, pocet_skolek-1)))
            vybrane_skolky = list(vybrane_skolky)   # Poradi se priradi nahodne - pro random generator je to ok.
            for index, value in enumerate(vybrane_skolky):
                d = {'dite': str(_), 'skolka': value, 'poradi': index + 1}
                writer.writerow(d)
        # return vybrane_skolky
print(get_priorities(children[:20], schools_all))






children_df = pd.DataFrame(children)
new_col = children_df.index
children_df.insert(0, 'id_dite', new_col)
# children_df.to_csv('deti.csv')


children_test = children_df[:20]
# children_test.to_csv('deti_test.csv')






