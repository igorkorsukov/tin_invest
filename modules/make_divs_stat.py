import os
import statistics
import datetime
from dataclasses import dataclass
from dataclasses import field

from tinkoff.invest import Client

from . import divs_payments 
from . import divs_stat
from . import divs_blocked
from . import share_prices
from . import utils

def MakeStats(config):

    statsCsv = divs_stat.statCsvHeader(config.BEGIN_YEAR, config.END_YEAR, config.CSV_SEP)
    print(statsCsv)  
    statsCsv += '\n'

    blocked = divs_blocked.loadBlocked(config.BLOCKED_FILE, config.CSV_SEP)

    with Client(config.TOKEN) as client:
        # Get data
        allshares= client.instruments.shares()
        prices = share_prices.loadPrices(client)
        for ts in allshares.instruments:
            if not ts.buy_available_flag:
                continue

            if not ts.currency == 'rub':
                continue  

            if divs_blocked.isBlocked(blocked, ts.ticker):
                continue    

            # if not ts.ticker == 'LKOH':
            #     continue      

            # print(ts) 
            payments = divs_payments.payments(
                client = client, 
                figi = ts.figi, 
                fromY = config.BEGIN_YEAR, 
                toY = config.END_YEAR)

            if len(payments) == 0:
                continue    

            # for pay in payments:
            #     print(pay) 

            consolidated = divs_payments.consolidate(payments, config.BEGIN_YEAR, config.END_YEAR)  
            # print("consolidated") 
            # for cpay in consolidated:
            #     print(cpay) 

            # Calc stat 
            price = share_prices.findPrice(prices, ts.figi)
            if price < 0.00001: 
                print("not found price for", ts.ticker, ts.name)
                continue

            stat = divs_stat.makeStat(ts, consolidated, price)
            
            # Save csv file
            statCsv = divs_stat.statToCsv(stat, config.CSV_SEP) 
            print(statCsv)        
            statsCsv += statCsv
            statsCsv += '\n'
    

    with open(config.STATS_FILE, 'w') as statsFile:
        statsFile.write(statsCsv)