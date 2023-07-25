import pandas as pd
from bs4 import BeautifulSoup

"""
dava dobry vysledek, akorat chybi sloupec "Deti ze spadove oblasti"
"""

with open('input_full.txt') as file:
    tab = file.read()

def table_to_dataframe(table_html):
    soup = BeautifulSoup(table_html, 'html.parser')
    rows = soup.find_all('tr')

    headers = [header.text.strip() for header in rows[0].find_all('th') if header.text.strip() != "Průběžné výsledky"]
    prubezne = ["Děti ze spádové oblasti", "Podaných žádostí", "Přijatých žáků","Nepřijatých žáků", "Individuální docházka", "Přerušených řízení"]
    headers = headers + prubezne

    data = []
    for row in rows[1:]:
        values = [td.text.strip() for td in row.find_all('td')]
        prubezne_vysledky = [item.split(':')[-1].strip() for item in values[4].split('\n')]
        data.append(dict(zip(headers[:4] + headers[4:], values[:4] + prubezne_vysledky)))

    df = pd.DataFrame(data)
    return df

df = table_to_dataframe(tab)
print(df.info())
df.to_csv('skolky_seznam_zwebu.csv')
