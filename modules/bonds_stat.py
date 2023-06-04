import os
from dataclasses import dataclass

from . import bonds_ratings 

STATS_FILE = "stats.csv"
CSV_SEP = '|'

@dataclass
class Stat:
    rating: str = ""
    count: int = 0
    nominalProfit: float = 0.0
    currentProfit: float = 0.0
    maturityProfit: float = 0.0

def init(config):
    STATS_FILE = config.STATS_FILE
    CSV_SEP = config.CSV_SEP

def loadStats():
    stats = []
    if not os.path.isfile(STATS_FILE):
        return stats

    with open(STATS_FILE) as file:
        for line in file:
            datas = line.rstrip().split(CSV_SEP)
            s = Stat()
            s.rating = datas[0]
            s.count = int(datas[1])
            s.nominalProfit = float(datas[2])
            s.currentProfit = float(datas[3])
            s.maturityProfit = float(datas[4])
            stats.append(s)
    return stats 

def findStat(stats, rating):
    r = bonds_ratings.consolidate(rating)
    for s in stats:
        if s.rating == r:
            return s
    return Stat() 

def statToCsv(s):
    row = s.rating+CSV_SEP+ \
        str(s.count)+CSV_SEP+ \
        str(s.nominalProfit)+CSV_SEP+ \
        str(s.currentProfit)+CSV_SEP+ \
        str(s.maturityProfit)

    return row      