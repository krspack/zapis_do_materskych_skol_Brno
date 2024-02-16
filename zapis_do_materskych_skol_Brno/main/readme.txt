Spuštění skriptu s testovacími daty: 

1. v terminálu se pomocí příkazu cd dostat do složky /main/testy

2. spustit test:

a. bez parametrů: příkazem python test.py
Test se spustí s testovacími daty odpovídajícími situaci v Brně, bude se tedy rozdělovat 4488 uchazečů mezi 139 školek na základě jejich skutečné kapacity. Test může běžet několik desítek minut. Výsledek (a mezivýsledky) se uloží do složky /main/testy/1_test pod nazvem vysledek.csv, respektive už je tam uložen.

b. s parametry v následujícím pořadí:

pocet_deti: maximálně 4608 

pocet_skolek: maximálně len(skolky), tj. 136

random_seed: nahodně vybrané číslo (prvek náhody se uplatní např. při „vybírání“ školek fiktivními uchazeči)

kapacita_jedne_skolky: pro verzi testu, kde mají všechny školky shodnou kapacitu. Defaultně se uplatní skutečná kapacita školek.

cislo_testu: mezivýsledky a výsledky testu se uloží do složky cislo_testu_test namísto defaultní složky 1_test. Pokud parametr zůstane nevyplněn, přepíše se 1_test.

Skript test.py nevytváří při každém spuštění nové fiktivní uchazeče pro rozdělení, pouze je vybírá z již předvyrobeného datasetu /main/testy/deti.csv. Pro úpravu tohoto datasetu (např. zvýšení maximálního počtu uchazečů nebo změna jejich věkového složení) je nutné upravit skript testy/výroba_testovacich_dat/vyroba_testovacich_dat.py. 


