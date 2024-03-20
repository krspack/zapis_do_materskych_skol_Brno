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


import sys
import warnings
import csv
import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import copy
from matching.games import HospitalResident


warnings.filterwarnings("ignore", category=DeprecationWarning)

script_name = sys.argv[0]
OZNACENI_TESTU = str(sys.argv[1] if len(sys.argv) > 1 else 1)

# mezivýsledky uložené skriptem test.py se ctou z nasledujicich souboru.
# Pokud se main.py spouští samostatně (ne z testu pres subcommand), je nutné upravit cestu k souborům na "testy/{}_test/deti_test.csv"
deti = pd.read_csv(
    "{}_test/deti_test.csv".format(OZNACENI_TESTU),
    dtype={
        "dite_id": "string",
        "spadova_skolka": "string",
        "skolka_sourozence": "string",
    },
)
deti = deti.sample(frac = 1)

skolky = pd.read_csv(
    "{}_test/skolky_test.csv".format(OZNACENI_TESTU), dtype={"skolka_id": "string"}
)

prihlasky = pd.read_csv(
    "{}_test/prihlasky_test.csv".format(OZNACENI_TESTU),
    dtype={"dite": "string", "skolka": "string"},
)

# vypocet bodu pro jednotlive uchazece podle kritérií popsaných zde: https://zapisdoms.brno.cz/kriteria-rizeni
def get_mestska_cast(deti_df: pd.DataFrame, skolky_df: pd.DataFrame) -> pd.DataFrame:
    # Funkce rozšíří tabulku dětí o sloupec "mestska_cast", převzatý od spádové školky, za účelem obodování.
    deti_df = pd.merge(
        deti_df,
        skolky_df[["skolka_id", "mc"]],
        left_on="spadova_skolka",
        right_on="skolka_id",
    )
    deti_df.drop("skolka_id", axis=1, inplace=True)
    return deti_df
deti = get_mestska_cast(deti, skolky)


def get_age(birthday: datetime.date) -> tuple[int, int]:
    # Z data narození vypočte věk v letech a dnech k letošnímu 31. srpnu.
    today = datetime.date.today()
    current_year = today.year
    schoolyear_start = datetime.date(birthday.year, 8, 31)
    difference = (
        schoolyear_start - birthday
    )  # stavajici vypocet na webu zapisdoms.brno.cz jeste odecita jednicku (tj. relativedelta(days = 1)), tj. deti narozene 31.8. by mely o rok mene.

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
body.to_csv("{}_test/body_test.csv".format(OZNACENI_TESTU))

print("Všichni uchazeči vs. všechny školky: přidělené body")
print()
seznam_id_skolek = list(skolky.skolka_id)
print(body[["dite_id", "jmeno"] + seznam_id_skolek])


# vstup pro funkci "match" c. 1: priority uchazecu
def get_priorities(tabulka_prihlasek: pd.DataFrame) -> dict:
    # Funkce vytvoří slovník uchazečů a jejich prioritních seznamů školek.
    prihlasky_groupedby_kids = tabulka_prihlasek.groupby("dite")["skolka"].agg(list)
    return prihlasky_groupedby_kids.to_dict()
priority = get_priorities(prihlasky)

"""
def get_priorities_names(priority_dict):
    # funkce vytiskne slovnik 'priority' se jmeny uchazecu namisto cisel
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
def get_volna_mista(df_skolky: pd.DataFrame) -> dict[str, int]:
    # vyrobí slovník "školka: kapacita"
    volna_mista_dict = df_skolky.set_index("skolka_id")["volna_mista"].to_dict()
    volna_mista_dict = {str(k): v for k, v in volna_mista_dict.items()}
    return volna_mista_dict


volna_mista = get_volna_mista(skolky)


# vstup pro funkci "match" c. 3: priority skolek, vyjadrene poradim obodovanych uchazecu o kazdou skolku
def get_schools_longlists(
    body_df: pd.DataFrame, prihlasky_df: pd.DataFrame
) -> dict[str, list[str]]:
    # Z tabulky body_df vybere jen relevantni udaje podle toho, kdo se kam hlásí.
    # výstup je slovnik typu "skolka a k ni vsechny deti, co se na ni hlasi, seřazené podle počtu bodů"
    prihlasky_groupedby_schools = prihlasky_df.groupby("skolka")["dite"].agg(list)
    prihlasky_groupedby_schools_dict = prihlasky_groupedby_schools.to_dict()
    longlists = {}
    schools = prihlasky_groupedby_schools_dict.keys()
    for s in schools:
        all_kids_one_school = body_df[["dite_id", str(s)]].copy()
        all_kids_one_school["dite_id"] = all_kids_one_school["dite_id"].astype(str)
        kids_applyint_to_one_school = all_kids_one_school.loc[
            all_kids_one_school["dite_id"].isin(
                prihlasky_groupedby_schools_dict[str(s)]
            )
        ].copy()
        kids_applyint_to_one_school.sort_values(
            by=str(s), ascending=False, inplace=True
        )
        kids_applyint_to_one_school.reset_index(inplace=True, drop=True)
        sorted_longlist = tuple(kids_applyint_to_one_school["dite_id"])
        longlists[str(s)] = [str(x) for x in sorted_longlist]
    return longlists

serazeni_uchazeci = get_schools_longlists(body, prihlasky)

"""
def get_longlists_names(longlists_dict):
    # funkce vytiskne slovnik "serazeni_uchazeci" se jmeny namisto cisel
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


def match(
    priority_zaku: dict[str, list[str]],
    priority_skolek: dict[str, list[str]],
    kapacity_skolek: dict[str, int],
):
    # rozřadí uchazeče do školek
    game = HospitalResident.create_from_dictionaries(
        priority_zaku, priority_skolek, kapacity_skolek
    )
    schools_shortlists = game.solve(optimal="resident")
    return schools_shortlists


rozrazeni = match(priority, serazeni_uchazeci, volna_mista)


def save_results(results: dict[str, list[str]], test_number: str):
    nazev_adresare = str(test_number) + "_test"
    with open("{}/vysledek.csv".format(nazev_adresare), "w", encoding = 'utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["dite", "skolka", "poradi"])
        writer.writeheader()
        for school, shortlist in results.items():
            for index, person in enumerate(shortlist):
                d = {"skolka": school, "poradi": index + 1, "dite": person}
                writer.writerow(d)



save_results(rozrazeni, OZNACENI_TESTU)


def get_vysledek_se_jmeny(vysledek, deti_df: pd.DataFrame) -> dict[str, list[str]]:
    names = {}
    for k, v in vysledek.items():
        k_nazev = skolky.loc[skolky["skolka_id"] == k.name, "nazev_kratky"].item()
        v_jmeno = [i.name for i in v]
        v_jmeno = [
            (
                deti_df.loc[deti_df["dite_id"] == i, "jmeno"].item()
                + " ("
                + (deti_df.loc[deti_df["dite_id"] == i, "dite_id"].item())
                + ")"
            )
            for i in v_jmeno
        ]
        names[k_nazev + " (" + k.name + ")"] = v_jmeno
    return names


vysledek_se_jmeny = get_vysledek_se_jmeny(rozrazeni, deti)

print()
print("Výsledky - kdo se dostal kam: ")
print()
for k, v in vysledek_se_jmeny.items():
    print(k, v)
    print()


def kdo_se_nedostal(vysledek, deti_df: pd.DataFrame) -> dict[str, str]:
    uspesni_uchazeci = []
    for v in vysledek.values():
        uspesni_uchazeci.extend(v)
    uspesni_uchazeci = [_.name for _ in uspesni_uchazeci]

    neuspesni = {}
    for _ in deti_df["dite_id"]:
        if _ not in uspesni_uchazeci:
            neuspesni[_] = deti_df.loc[deti_df["dite_id"] == _, "jmeno"].item()
    return neuspesni
neuspesni = kdo_se_nedostal(rozrazeni, deti)

print()
print()
print("Neúspěšní uchazeči:")
print()
for k, v in neuspesni.items():
    print(v + " (" + k + ")")
