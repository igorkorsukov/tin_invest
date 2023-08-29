import os
from dataclasses import dataclass

BLOCKED_FILE = "blocked.csv"
CSV_SEP = '|'

@dataclass
class Blocked:
    name: str = ""
    isin: str = ""
    comment: str = ""  

def init(config):
    global BLOCKED_FILE
    global CSV_SEP

    BLOCKED_FILE = config.BLOCKED_FILE
    CSV_SEP = config.CSV_SEP

def loadBlocked():
    blocked = []
    if not os.path.isfile(BLOCKED_FILE):
        return blocked

    with open(BLOCKED_FILE) as file:
        for line in file:
            datas = line.rstrip().split(CSV_SEP)
            b = Blocked()
            b.name = datas[0]
            b.isin = datas[1]
            b.comment = datas[2]
            blocked.append(b)
    return blocked 

def isBlocked(blocked, isin):
    for b in blocked:
        if b.isin == isin:
            return True
    return False  