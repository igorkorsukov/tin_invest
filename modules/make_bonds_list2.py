from dataclasses import dataclass

from tinkoff.invest import Client

import modules.bonds_ratings as bonds_ratings
import modules.bonds_coupons as bonds_coupons
import modules.bonds_prices as bonds_prices
import modules.bonds_profit as bonds_profit
import modules.bonds_blocked as bonds_blocked
import modules.bonds_allowed as bonds_allowed
import modules.bonds_stat as bonds_stat
import modules.utils as utils

import config as config

RATING = "BBB"
MATURITY = 12
CSV_SEP = '|'
BONDS_FILE = "bonds.csv"

@dataclass
class BondData:
    name: str = ""
    isin: str = ""
    rating: str = ""
    monthsToMaturity: int = 0
    monthsToOffer: int = 0
    nominalPrice: int = 0.0
    currentPrice: int = 0.0
    couponsCountPerYear: int = 0
    coupon: float = 0.0
    couponAmountPerYear: float = 0.0
    nominalProfitPerYear: float = 0.0
    nominalProfitDelta: float = 0.0     # Отклонение от среднего
    currentProfitPerYear: float = 0.0
    currentProfitDelta: float = 0.0     # Отклонение от среднего 
    maturityProfitPerYear: float = 0.0
    maturityProfitDelta: float = 0.0    # Отклонение от среднего 
    offerProfitPerYear: float = 0.0 

def tbondToBondData(tb):
     b = BondData()
     b.name = tb.name
     b.isin = tb.isin
     b.monthsToMaturity = utils.monthsCount(tb.maturity_date)
     b.nominalPrice = int(utils.moneyValueToReal(tb.nominal))
     b.couponsCountPerYear = tb.coupon_quantity_per_year
     return b

def precalcProfit(b, tb):
    b.couponAmountPerYear = bonds_profit.couponAmountPerYear(tb, b.coupon)
    b.nominalProfitPerYear = bonds_profit.nominalProfit(tb, b.coupon)
    b.currentProfitPerYear = bonds_profit.currentProfit(tb, b.coupon, b.currentPrice)
    b.maturityProfitPerYear = bonds_profit.maturityProfit(tb, b.coupon, b.currentPrice)

def bondsCsvHeader():
    h = "Название|ISIN|Рейтинг|Срок(м)|Оферта(м)|Номинал|Цена|Кол куп|% номл|d номл|% текщ|d текщ|% погш|d погш|% офер|d офер"
    return h

def bondToCsv(b):
    row = b.name+CSV_SEP+ \
        b.isin+CSV_SEP+ \
        b.rating+CSV_SEP+ \
        str(b.monthsToMaturity)+CSV_SEP+ \
        str(b.monthsToOffer)+CSV_SEP+ \
        str(b.nominalPrice)+CSV_SEP+ \
        str(b.currentPrice)+CSV_SEP+ \
        str(b.couponsCountPerYear)+CSV_SEP+ \
        utils.realToStr(b.nominalProfitPerYear)+CSV_SEP+ \
        utils.realToStr(b.nominalProfitDelta)+CSV_SEP+ \
        utils.realToStr(b.currentProfitPerYear)+CSV_SEP+ \
        utils.realToStr(b.currentProfitDelta)+CSV_SEP+ \
        utils.realToStr(b.maturityProfitPerYear)+CSV_SEP+ \
        utils.realToStr(b.maturityProfitDelta)+CSV_SEP+ \
        utils.realToStr(b.offerProfitPerYear)+CSV_SEP+ \
        utils.realToStr(0.0)

    return row 

def MakeList(config):

    with Client(config.TOKEN) as client:

        global RATING
        global MATURITY
        global CSV_SEP
        global BONDS_FILE

        RATING = config.RATING
        MATURITY = config.MATURITY
        CSV_SEP = config.CSV_SEP
        BONDS_FILE = config.BONDS_FILE

        bonds_ratings.init(config)
        bonds_coupons.init(config)
        bonds_profit.init(config)
        bonds_blocked.init(config)
        bonds_allowed.init(config)
        bonds_stat.init(config)

        bondsCsv = bondsCsvHeader()
        bondsCsv += '\n'

        prices = client.market_data.get_close_prices().close_prices
        
        # Load
        ratings = bonds_ratings.loadRatings()
        coupons = bonds_coupons.loadCoupons()
        blocked = bonds_blocked.loadBlocked()
        stats = bonds_stat.loadStats()

        allbonds = client.instruments.bonds()
        for tb in allbonds.instruments:

              if bonds_allowed.isBondAllowed(tb, blocked):
                rating = bonds_ratings.findRating(ratings, tb.isin)
                if bonds_ratings.isRatingLess(rating, RATING):
                    continue   

                myb = tbondToBondData(tb)
                myb.rating = rating
                c = bonds_coupons.getCoupon(coupons, client, tb)
                myb.coupon = c.value
                myb.monthsToOffer = c.months

                if myb.monthsToOffer < MATURITY:
                    continue
              
                myb.currentPrice = bonds_prices.currentPrice(prices, tb)

                precalcProfit(myb, tb)

                if not bonds_profit.isProfitAllow(myb):
                    continue    

                stat = bonds_stat.findStat(stats, rating)
                myb.nominalProfitDelta = round(myb.nominalProfitPerYear - stat.nominalProfit, 1)
                myb.currentProfitDelta = round(myb.currentProfitPerYear - stat.currentProfit, 1)    
                myb.maturityProfitDelta = round(myb.maturityProfitPerYear - stat.maturityProfit, 1)  

                if not bonds_stat.isDeltaAllowed(myb):
                    continue    

                bondCsv = bondToCsv(myb) 
                print(bondCsv)  
                
                bondsCsv += bondCsv
                bondsCsv += '\n'

        with open(BONDS_FILE, 'w') as bondsFile:
            bondsFile.write(bondsCsv)

if __name__ == "__main__":
    MakeList(config)                