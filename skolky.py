
import csv
import pandas as pd

with open('seznam_skolek_jednoduchy.csv') as file:
    seznam_skolek = csv.DictReader(file)
    seznam = list(seznam_skolek)

skolky = pd.DataFrame(seznam)
skolky.rename(columns = {'Název školy': 'nazev_skoly', '': 'adresa', 'mc': 'mc'}, inplace = True)
skolky['nazev_skoly'] = skolky['nazev_skoly'].str.replace('Brno', '')
skolky['nazev_skoly'] = skolky['nazev_skoly'].str.replace('Mateřská škola', 'MŠ')
skolky['nazev_skoly'] = skolky['nazev_skoly'] + " " + skolky['adresa']
skolky['nazev_skoly'] = skolky['nazev_skoly'].str.replace("  ", " ")
skolky = skolky.drop('adresa', axis = 1)


skolky_celobrno = pd.DataFrame([["MŠ Štolcova 51", "Brno"], ["MŠ Veslařská 256", "Brno"]], columns = ['nazev_skoly', 'mc'])
skolky = pd.concat([skolky, skolky_celobrno]).reset_index(drop = True)
skolky['id'] = skolky.index


skolky.to_csv('skolky.csv')

mestske_casti = skolky.groupby(['mc']).nazev_skoly.unique()












