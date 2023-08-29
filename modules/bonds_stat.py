import os
from dataclasses import dataclass

from . import bonds_ratings 

NOMINAL_DELTA_MIN = -10 
CURRENT_DELTA_MIN = -10 
MATURITY_DELTA_MIN = -10 
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
    global NOMINAL_DELTA_MIN
    global CURRENT_DELTA_MIN
    global MATURITY_DELTA_MIN
    global STATS_FILE
    global CSV_SEP

    NOMINAL_DELTA_MIN = config.NOMINAL_DELTA_MIN
    CURRENT_DELTA_MIN = config.CURRENT_DELTA_MIN
    MATURITY_DELTA_MIN = config.MATURITY_DELTA_MIN
    STATS_FILE = config.STATS_FILE
    CSV_SEP = config.CSV_SEP

def isDeltaAllowed(myb):
    if myb.nominalProfitDelta < NOMINAL_DELTA_MIN:
        return False
    if myb.currentProfitDelta < CURRENT_DELTA_MIN:
        return False   
    if myb.maturityProfitDelta < MATURITY_DELTA_MIN:
        return False
    
    return True

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