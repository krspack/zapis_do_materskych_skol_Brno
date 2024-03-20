Spuštění skriptu s testovacími daty: 

1. v terminálu se pomocí příkazu cd dostat do složky /main/testy

2. spustit test:

a. bez parametrů: příkazem python test.py
Test se spustí s testovacími daty odpovídajícími situaci v Brně, bude se tedy rozdělovat 4488 uchazečů mezi 139 školek na základě jejich skutečné kapacity. Test může běžet několik desítek minut. Výsledek (a mezivýsledky) se uloží do složky /main/testy/1_test pod nazvem vysledek.csv, respektive už je tam uložen.

b. s parametry v následujícím pořadí:

pocet_deti: maximálně 4608 

pocet_skolek: maximálně len(skolky), tj. 136

random_seed: nahodně vybrané číslo (prvek náhody se uplatní např. při „vybírání“ školek fiktivními uchazeči)

cislo_testu: mezivýsledky a výsledky testu se uloží do složky cislo_testu_test namísto defaultní složky 1_test. Pokud parametr zůstane nevyplněn, přepíše se 1_test.

kapacita_jedne_skolky: pro verzi testu, kde mají všechny školky shodnou kapacitu. Defaultně se uplatní skutečná kapacita školek.




Příklady testovacích scénářů a jejich spuštění z příkazové řádky:

python test.py (Do nově vytvořené složky 1_test uloží rozřazení 4488 dětí do všech brněnských školek.)

python test.py 20 5 42 2 3 (Do nově vytvořené složky 2_test se uloží rozřazení 20 dětí mezi 5 školek, kde každá má 3 volná místa.)

python test.py 1000 40 42 3 (Do nově vytvořené složky 3_test se uloží rozřazení 1000 dětí do 40 školek. Bude se počítat s reálnou kapacitou školek.)




Skript test.py nevytváří při každém spuštění nové fiktivní uchazeče pro rozdělení, pouze je vybírá z již předvyrobeného datasetu /main/testy/deti.csv. Pro úpravu tohoto datasetu (např. zvýšení maximálního počtu uchazečů nebo změna jejich věkového složení) je nutné upravit skript testy/výroba_testovacich_dat/vyroba_testovacich_dat.py. 


