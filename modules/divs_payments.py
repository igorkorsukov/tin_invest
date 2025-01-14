import datetime
from dataclasses import dataclass

from . import utils

@dataclass
class Payment:
    value: float = 0.0
    date: datetime.datetime=datetime.datetime(1900, 1, 1)

def payments(client, figi, fromY, toY):

    ret = client.instruments.get_dividends(
        figi = figi,
        from_= datetime.datetime(fromY, 1, 1),
        to = datetime.datetime(toY, 12, 31)
    )
    
    pays = []
    for d in ret.dividends:
        p = Payment()
        p.value = utils.moneyValueToReal(d.dividend_net)
        p.date = d.record_date
        pays.append(p)

    return pays

def consolidateByYear(pays, year):
    val = 0.0
    for p in pays:
        if p.date.year == year: 
            val += p.value
    return round(val, 4);         

def consolidate(pays, from_, to):
    consolidated = []

    for y in range(from_, to+1):
        cp = Payment()
        cp.date = datetime.datetime(y, 12, 31)
        cp.value = consolidateByYear(pays, y);   
        consolidated.append(cp)

    return consolidated    

def values(pays):
    vals = []
    for p in pays:
        vals.append(p.value)   

    return vals     