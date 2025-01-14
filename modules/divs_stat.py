import math
from dataclasses import dataclass
from dataclasses import field

from . import divs_payments 
from . import utils

@dataclass
class Stat:
    ticker: str = ""
    name: str = ""
    payments: list[float] = field(default_factory=list)
    average: float = 0.0
    increase: float = 0.0
    averageAdj: float = 0.0
    price: float = 0.0
    profit: float = 0.0
    profitAdj: float = 0.0

def statCsvHeader(fromY, toY, sep):
    h = "Тикер"+sep+"Название"+sep
    for y in range(fromY, toY+1):
        h += str(y)+sep
    h += "Среднее"+sep
    h += "Рост"+sep
    h += "Среднее корр"+sep
    h += "Цена"+sep 
    h += "Доходность"+sep   
    h += "Доходность корр"+sep    
    return h

def statToCsv(s, sep):
    row = s.ticker+sep+s.name+sep
    for p in s.payments:
        row += utils.realToStr(p)+sep
        
    row += utils.realToStr(s.average)+sep    
    row += utils.realToStr(s.increase)+sep  
    row += utils.realToStr(s.averageAdj)+sep  
    row += utils.realToStr(s.price)+sep    
    row += utils.realToStr(s.profit)+sep  
    row += utils.realToStr(s.profitAdj)+sep
    return row       

def average(pays):
    val = 0.0
    for p in pays:
        val += p.value

    return round(val / len(pays), 4) 

def increase(pays):
    count = len(pays) 
    mid = math.ceil(count / 2)

    part1 = []
    for i in range(0, mid): 
        part1.append(pays[i])

    part2 = []
    for i in range(mid, count): 
        part2.append(pays[i])    

    avg1 = average(part1)  
    avg2 = average(part2) 

    if avg1 == 0.0:
        inc = 1
    elif avg2 == 0.0:
        inc = 0.5    
    else:
        inc = round(avg2 / avg1, 2)

    return inc

def makeStat(ts, payments, price):
    stat = Stat()
    stat.ticker = ts.ticker
    stat.name = ts.name 
    stat.payments = divs_payments.values(payments)
    stat.average = average(payments)
    stat.increase = increase(payments)
    stat.averageAdj = round(stat.average * stat.increase, 4)
    stat.price = price
    stat.profit = round(stat.average * 100.0 / stat.price, 2)
    stat.profitAdj = round(stat.averageAdj * 100.0 / stat.price, 2)

    # print(stat)

    return stat