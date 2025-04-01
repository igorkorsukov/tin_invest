import os
from dataclasses import dataclass

FAVS_FILE = "bonds_favs.csv"
CSV_SEP = '|'

@dataclass
class Fav:
    name: str = ""
    isin: str = ""
    comment: str = ""  

def init(config):
    global FAVS_FILE
    global CSV_SEP

    FAVS_FILE = config.FAVS_FILE
    CSV_SEP = config.CSV_SEP

def loadFavs():
    favs = []
    if not os.path.isfile(FAVS_FILE):
        return favs

    with open(FAVS_FILE) as file:
        for line in file:
            datas = line.rstrip().split(CSV_SEP)
            b = Fav()
            b.name = datas[0]
            b.isin = datas[1]
            b.comment = datas[2]
            favs.append(b)
    return favs 

def isAllowed(favs, isin):
    for b in favs:
        if b.isin == isin:
            return True
    return False  