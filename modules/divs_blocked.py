import os
from dataclasses import dataclass

@dataclass
class Blocked:
    ticker: str = ""
    name: str = ""
    comment: str = ""  

def loadBlocked(fileName, sep):
    blocked = []
    if not os.path.isfile(fileName):
        return blocked

    with open(fileName) as file:
        for line in file:
            datas = line.rstrip().split(sep)
            b = Blocked()
            b.ticker = datas[0]
            b.name = datas[1]
            b.comment = datas[2]
            blocked.append(b)
    return blocked 

def isBlocked(blocked, ticker):
    for b in blocked:
        if b.ticker == ticker:
            return True
    return False  