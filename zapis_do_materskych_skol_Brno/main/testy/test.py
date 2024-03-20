#!/usr/bin/env python
# coding: utf-8

import sys
import warnings
import subprocess
import random
import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import copy


warnings.filterwarnings("ignore", category=DeprecationWarning)

# vstupni data
## fiktivni uchazeci - viz vyroba_testovacich_dat.py
deti = pd.read_csv(
    "deti.csv",
    dtype={
        "dite_id": "string",
        "spadova_skolka": "string",
        "skolka_sourozence": "int64",
    },
)

## skutecne skolky
skolky = pd.read_csv("skolky.csv", dtype={"skolka_id": "string"})


# parametry testu ctene z prikazove radky
script_name = sys.argv[0]
pocet_deti = int(sys.argv[1] if len(sys.argv) > 1 else 4488)
pocet_skolek = int(sys.argv[2] if len(sys.argv) > 2 else len(skolky))
random_seed = int(sys.argv[3] if len(sys.argv) > 3 else 42)
cislo_testu = str(sys.argv[4] if len(sys.argv) > 4 else 1)
kapacita_jedne_skolky = int(
    sys.argv[5] if len(sys.argv) > 5 else -1
)  # defaultne: skutecne kapacity.


random.seed(random_seed)


def vyrob_adresar(test_number: str):
    # pokud je cislo testu jine nez 1, vyrobi adresar, kam se ulozi mezivysledky a vysledek testu
    if test_number not in [1, "1"]:
        nazev_adresare = str(test_number) + "_test"
        vyrob_novy_adresar = ["mkdir", nazev_adresare]
        subprocess.run(vyrob_novy_adresar)


vyrob_adresar(cislo_testu)


def get_kapacity_skolek(kapacity_input: int, skolky_df: pd.DataFrame):
    # pokud je zadana kapacita skolek, prepise v datasetu 'skolky' defaultni kapacitu skolek
    if kapacity_input > 0:
        skolky_df["volna_mista"] = kapacity_input


get_kapacity_skolek(kapacita_jedne_skolky, skolky)


def get_random_rows_skolky(dataframe: pd.DataFrame, num_rows: int) -> pd.DataFrame:
    # vybere nahodne skolky z datasetu 'skolky' v poctu pocet_skolek
    random_rows = dataframe.sample(n=num_rows)
    random_rows.reset_index()
    return random_rows


skolky = get_random_rows_skolky(skolky, pocet_skolek)

skolky.to_csv("{}_test/skolky_test.csv".format(cislo_testu))
"""


"""
def get_random_rows_deti(dataframe: pd.DataFrame, num_rows: int) -> pd.DataFrame:
    # Vybere nahodne uchazece z datasetu 'deti' v poctu pocet_uchazecu
    random_rows = dataframe.sample(n=num_rows)
    random_rows["spadova_skolka"] = [
        random.choice(list(skolky.skolka_id)) for _ in range(num_rows)
    ]
    random_rows["skolka_sourozence"] = [
        int(random.choice(list(skolky.skolka_id)))
        if original_value >= 0
        else original_value
        for original_value in random_rows["skolka_sourozence"]
    ]
    random_rows.reset_index()
    return random_rows


deti = get_random_rows_deti(deti, pocet_deti)

deti.to_csv("{}_test/deti_test.csv".format(cislo_testu))

# vyroba prihlasek:
def get_prihlasky(deti_df: pd.DataFrame, skolky_df: pd.DataFrame) -> pd.DataFrame:
    # Fuknce simuluje výběr oblíbených školek. Počet položek je náhodný.
    # Funkce při "výběru" oblíbených školek zohledňuje spádovost a školku sourozence.
    data: dict[str, list] = {"dite": [], "jmeno": [], "skolka": [], "poradi": []}
    for idx, row in deti_df.iterrows():
        vybrane_skolky = set()
        pocet_prihlasek = random.randint(1, len(skolky_df))
        dostupne_skolky = list(skolky_df.skolka_id)
        dostupne_skolky = [int(_) for _ in dostupne_skolky]
        for i in range(pocet_prihlasek):
            if i == 0:
                choice = int(row["spadova_skolka"])
                vybrane_skolky.add(choice)
                dostupne_skolky = [_ for _ in dostupne_skolky if _ != choice]
            elif i == 1 and row["skolka_sourozence"] >= 0:
                choice = int(row["skolka_sourozence"])
                vybrane_skolky.add(choice)
                dostupne_skolky = [_ for _ in dostupne_skolky if _ != choice]
            else:
                random.shuffle(dostupne_skolky)
                choice = dostupne_skolky[0]
                vybrane_skolky.add(choice)
                dostupne_skolky = [_ for _ in dostupne_skolky if _ != choice]

        vybrane_skolky_list = list(vybrane_skolky)
        vybrane_skolky_list = [str(_) for _ in vybrane_skolky]

        for index, value in enumerate(vybrane_skolky_list):
            data["dite"].append(str(row["dite_id"]))
            data["jmeno"].append(row["jmeno"])
            data["skolka"].append(value)
            data["poradi"].append(index + 1)

    df = pd.DataFrame(data)
    return df

prihlasky = get_prihlasky(deti, skolky)
prihlasky.to_csv("{}_test/prihlasky_test.csv".format(cislo_testu))


print("Vstupní data pro rozřazení (vybrané sloupce, prvních 10 řádek): ")
print()
print("Uchazeči:")
print(deti[["dite_id", "jmeno", "datum_narozeni", "spadova_skolka"]].head(10))
print()
print("Školky:")
print(skolky[["skolka_id", "nazev_kratky", "volna_mista"]].head(10))
print()
print("Priority uchazečů:")
# print(prihlasky)

# -------------------------------------------------

# spusteni skriptu main.py:
spustit_main = ["python", "../main.py", cislo_testu]
subprocess.run(spustit_main)

