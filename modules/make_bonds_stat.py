import os
import statistics
from dataclasses import dataclass
from dataclasses import field

from tinkoff.invest import Client

from . import bonds_ratings 
from . import bonds_blocked
from . import bonds_allowed
from . import bonds_coupons
from . import bonds_prices
from . import bonds_profit
from . import bonds_stat
from . import utils

TOKEN = os.environ["INVEST_TOKEN"]

NOMINAL_PROFIT = 10     # percent
CURRENT_PROFIT = 12     # percent
MATURITY_PROFIT = 12    # percent
CSV_SEP = '|'
STATS_FILE = "stats.csv" 

@dataclass
class StatData:
    nominalProfits: list[float] = field(default_factory=list)
    currentProfits: list[float] = field(default_factory=list)
    maturityProfits: list[float] = field(default_factory=list)

def MakeStats(config):

    # Init
    NOMINAL_PROFIT = config.NOMINAL_PROFIT
    CURRENT_PROFIT = config.CURRENT_PROFIT
    MATURITY_PROFIT = config.MATURITY_PROFIT
    CSV_SEP = config.CSV_SEP
    STATS_FILE = config.STATS_FILE

    bonds_ratings.init(config)
    bonds_blocked.init(config)
    bonds_allowed.init(config)

    # Load
    ratings = bonds_ratings.loadRatings()
    blocked = bonds_blocked.loadBlocked()
    coupons = bonds_coupons.loadCoupons()

    # Get Data
    data = {}
    with Client(TOKEN) as client:
        allbonds = client.instruments.bonds()
        prices = bonds_prices.loadPrices(client)
        for tb in allbonds.instruments:
            if bonds_allowed.isBondAllowed(tb, blocked):
                rating = bonds_ratings.findRating(ratings, tb.isin)
                rating = bonds_ratings.consolidate(rating)
                coupon = bonds_coupons.getCoupon(coupons, client, tb)

                # Nominal Profit
                nominalProfit = bonds_profit.nominalProfit(tb, coupon.value)
                if nominalProfit < NOMINAL_PROFIT:
                    continue

                # Current Profit
                currentPrice = bonds_prices.currentPrice(prices, tb)
                currentProfit = bonds_profit.currentProfit(tb, coupon.value, currentPrice)
                if currentProfit < CURRENT_PROFIT:
                    continue

                # Maturity Profit
                maturityProfit = bonds_profit.maturityProfit(tb, coupon.value, currentPrice)
                if maturityProfit < MATURITY_PROFIT:
                    continue   

                if rating not in data:
                    data[rating] = StatData()

                data[rating].nominalProfits.append(nominalProfit)
                data[rating].currentProfits.append(currentProfit)
                data[rating].maturityProfits.append(maturityProfit)

    # Calc stat
    stats = []
    for key, value in data.items():
        stat = bonds_stat.Stat()
        stat.rating = key
        stat.count = len(value.nominalProfits)
        stat.nominalProfit = round(statistics.mean(value.nominalProfits), 2)
        stat.currentProfit = round(statistics.mean(value.currentProfits), 2)
        stat.maturityProfit = round(statistics.mean(value.maturityProfits), 2)
        stats.append(stat)
   
    # Save csv file
    statsCsv = ""
    for stat in stats:
        statCsv = bonds_stat.statToCsv(stat) 
        print(statCsv)        
        statsCsv += statCsv
        statsCsv += '\n'

    with open(STATS_FILE, 'w') as statsFile:
        statsFile.write(statsCsv)