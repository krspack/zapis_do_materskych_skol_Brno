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
print(prihlasky)


# vypocet bodu pro jednotlive uchazece podle kritérií popsaných zde: https://zapisdoms.brno.cz/kriteria-rizeni


def get_mestska_cast(deti_df: pd.DataFrame) -> pd.DataFrame:
    # Funkce rozšíří tabulku dětí o sloupec "mestska_cast", převzatý od spádové školky, za účelem obodování.
    deti_df = pd.merge(
        deti_df,
        skolky[["skolka_id", "mc"]],
        left_on="spadova_skolka",
        right_on="skolka_id",
    )
    deti_df.drop("skolka_id", axis=1, inplace=True)
    return deti_df


deti = get_mestska_cast(deti)


def get_age(birthday: datetime.date) -> tuple[int, int]:
    # Z data narození vypočte věk v letech a dnech k letošnímu 31. srpnu.
    today = datetime.date.today()
    current_year = today.year
    schoolyear_start = datetime.date(birthday.year, 8, 31)
    difference = (
        schoolyear_start - birthday - relativedelta(days=1)
    )  # prizpusobeni vypoctu webu zapisdoms.brno.cz

    schoolyear_start_current = datetime.date(current_year, 8, 31)
    age_in_years = int(
        round((schoolyear_start_current - schoolyear_start).days / 365, 0)
    )
    if difference.days < 0:
        age_in_years -= 1
    return age_in_years, difference.days


def get_points_years(age: int, age_difference_days: int) -> int:
    # Přidelí body za věk.
    options = {7: 2160, 6: 2120, 5: 2080, 4: 2040, 3: 2000, 2: 0, 1: 0}
    calculate_points = (
        lambda x: 1000 if (x == 2 and age_difference_days < 0) else options[x]
    )
    points_years = calculate_points(age)
    return points_years


def calculate_points_one_child(id_child: int) -> pd.DataFrame:
    # Sečte body za všechna bodovaná kritéria.

    # vytvořit tabulku "1 uchazeč, všechny školky"
    copy_skolky = copy.deepcopy(skolky)
    copy_skolky["dite_id"] = id_child
    df_one_child = pd.merge(
        copy_skolky, deti, left_on="dite_id", right_on="dite_id", how="left"
    )
    df_one_child.rename(columns={"mc_x": "mc_skolka", "mc_y": "mc_dite"}, inplace=True)

    # body za věk
    df_one_child["datum_narozeni"] = pd.to_datetime(
        df_one_child["datum_narozeni"]
    ).dt.date
    df_one_child["vek"] = df_one_child["datum_narozeni"].apply(
        lambda x: pd.Series(get_age(x))
    )[0]
    df_one_child["vek_dny_srpen31"] = df_one_child["datum_narozeni"].apply(
        lambda x: pd.Series(get_age(x))
    )[1]
    df_one_child["body_za_vek_roky"] = df_one_child.apply(
        lambda row: get_points_years(row["vek"], row["vek_dny_srpen31"]), axis=1
    )
    df_one_child["body_za_vek_dny"] = df_one_child.apply(
        lambda row: 0
        if (row["vek_dny_srpen31"] < 0)
        else row["vek_dny_srpen31"] * 0.02,
        axis=1,
    )
    df_one_child["prioritni_vek"] = df_one_child.apply(
        lambda row: True if (3 <= row["vek"] <= 6) else False, axis=1
    )

    # body za bydliště
    df_one_child["body_spadovost"] = df_one_child.apply(
        lambda row: 250 if row["bydliste_brno"] == True else 0, axis=1
    )
    df_one_child["body_spadovost"] = df_one_child.apply(
        lambda row: 500
        if row["mc_skolka"] == row["mc_dite"]
        else row["body_spadovost"],
        axis=1,
    )
    df_one_child["body_spadovost"] = df_one_child.apply(
        lambda row: 750
        if (row["skolka_id"] == row["spadova_skolka"])
        and (row["prioritni_vek"] == False)
        else row["body_spadovost"],
        axis=1,
    )
    df_one_child["body_spadovost"] = df_one_child.apply(
        lambda row: 1000
        if (row["skolka_id"] == row["spadova_skolka"])
        and (row["prioritni_vek"] == True)
        else row["body_spadovost"],
        axis=1,
    )

    # body za sourozence ve školce
    df_one_child["skolka_sourozence"] = pd.to_numeric(
        df_one_child["skolka_sourozence"], errors="coerce"
    )  # nutne kvuli df.query nize
    df_one_child["skolka_id"] = pd.to_numeric(
        df_one_child["skolka_id"], errors="coerce"
    )
    df_one_child["body_sourozenec"] = df_one_child.query(
        "prioritni_vek == True and skolka_sourozence == skolka_id"
    ).apply(lambda x: 10, axis=1)
    df_one_child["body_sourozenec"].fillna(0, inplace=True)
    df_one_child["skolka_sourozence"] = df_one_child["skolka_sourozence"].astype(str)
    df_one_child["skolka_id"] = df_one_child["skolka_id"].astype(str)

    # dve specialni skolky, které mají jako spádovou oblast celé Brno a nabízejí prodloužený provoz
    # body navíc, pokud uchazeč doloží potřebu prodlouženého provozu
    # zapisdoms.brno.cz nespecifikuje počet bodů navíc >>> arbitrárně stanoveno 50 bodů
    df_one_child.loc[
        df_one_child["mc_skolka"] == "brno", "body_spadovost"
    ] = df_one_child.loc[df_one_child["mc_skolka"] == "brno", "body_spadovost"].apply(
        lambda x: 1000
    )
    df_one_child.loc[
        df_one_child["mc_skolka"] == "brno", "body_sourozenec"
    ] = df_one_child.loc[df_one_child["mc_skolka"] == "brno", "body_sourozenec"].apply(
        lambda x: 10
    )
    df_one_child["body_prodlouz_provoz"] = 0
    df_one_child.loc[
        df_one_child["mc_skolka"] == "brno", "body_prodlouz_provoz"
    ] = df_one_child.loc[
        df_one_child["mc_skolka"] == "brno", "body_prodlouz_provoz"
    ].apply(
        lambda x: 50 if "prodlouzena_dochazka" == True else 0
    )

    # nezohledneni bodů za "Den věku dítěte v roce narození" v případě spádových školek
    df_one_child.loc[
        df_one_child["spadova_skolka"] == df_one_child["skolka_id"], "body_za_vek_dny"
    ] = df_one_child.loc[
        df_one_child["spadova_skolka"] == df_one_child["skolka_id"], "body_za_vek_dny"
    ].apply(
        lambda x: 0
    )

    # součet bodů
    df_one_child["body_soucet"] = (
        df_one_child["body_sourozenec"]
        + df_one_child["body_spadovost"]
        + df_one_child["body_za_vek_roky"]
        + df_one_child["body_za_vek_dny"]
        + df_one_child["body_prodlouz_provoz"]
    )
    d_pivoted = df_one_child.pivot(
        index="dite_id", columns="skolka_id", values="body_soucet"
    )
    d_pivoted = pd.merge(
        deti, d_pivoted, how="right", left_on="dite_id", right_on="dite_id"
    )
    return d_pivoted


# výstup pro prvního uchazeče:
body = calculate_points_one_child(deti.iloc[0]["dite_id"])

# výstup pro všechny uchazeče:
for i in range(1, len(deti)):
    one_child_pivoted_df = calculate_points_one_child(deti.iloc[i]["dite_id"])
    body = pd.concat([body, one_child_pivoted_df])
body[["dite_id", "spadova_skolka", "skolka_sourozence"]] = body[
    ["dite_id", "spadova_skolka", "skolka_sourozence"]
].astype("str")
body.to_csv("{}_test/body_test.csv".format(cislo_testu))

print("Všichni uchazeči vs. všechny školky: přidělené body")
print()
seznam_id_skolek = list(skolky.skolka_id)
print(body[["dite_id", "jmeno"] + seznam_id_skolek])

# -------------------------------------------------

# spusteni skriptu main.py:
spustit_main = ["python", "../main.py", cislo_testu]
subprocess.run(spustit_main)
