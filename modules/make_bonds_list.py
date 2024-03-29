import os
import datetime
import time
from dataclasses import dataclass
import argparse

from tinkoff.invest import Client

from . import bonds_stat

TOKEN = os.environ["INVEST_TOKEN"]

RATING = "BBB"
CURRENT_PROFIT = 11     # percent
MATURITY_PROFIT = 11    # percent
MATURITY = 10           # month
MONTH_TO_OFFER = 6
AMORTIZATION = True
FLOATING_COUPON = False
CSV_SEP = '|'
CURRENCY = "rub"

BONDS_FILE = "bonds.csv"
RATINGS_FILE = "ratings.csv"
COUPONS_FILE = "coupons.csv"
BLOCKED_FILE = "blocked.csv"

RATING_TO_NUM = {
    'D': 0,
    'C-': 1,
    'C': 2,
    'C+': 3,
    'CC-': 4,
    'CC': 5,
    'CC+': 6,
    'CCC-': 7,
    'CCC': 8,
    'CCC+': 9,
    'B-': 10,
    'B': 11,
    'B+': 12,
    'BB-': 13,
    'BB': 14,
    'BB+': 15,
    'BBB-': 16,
    'BBB': 17,
    'BBB+': 18,
    'A-': 19,
    'A': 20,
    'A+': 21,
    'AA-': 22,
    'AA': 23,
    'AA+': 24,
    'AAA-': 25,
    'AAA': 26,
    'AAA+': 27,
    '-': 30
}

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

@dataclass
class Rating:    
    name: str = ""
    isin: str = ""
    rating: str = ""

@dataclass
class Coupon:
    name: str = ""
    isin: str = ""
    coupon: float = 0.0
    months: int = 0     

@dataclass
class Blocked:
    name: str = ""
    isin: str = ""
    comment: str = ""      

def monthsCount(dt):
    today = datetime.datetime.now()
    naive = dt.replace(tzinfo=None)
    time_diff = naive - today
    return round(time_diff.days / 365 * 12)

def moneyValueToReal(mv):
    return round(mv.units + (mv.nano / 1000000000.0), 2)

def realToStr(v):
    return str(v).replace('.',',')   

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
        realToStr(b.nominalProfitPerYear)+CSV_SEP+ \
        realToStr(b.nominalProfitDelta)+CSV_SEP+ \
        realToStr(b.currentProfitPerYear)+CSV_SEP+ \
        realToStr(b.currentProfitDelta)+CSV_SEP+ \
        realToStr(b.maturityProfitPerYear)+CSV_SEP+ \
        realToStr(b.maturityProfitDelta)+CSV_SEP+ \
        realToStr(b.offerProfitPerYear)+CSV_SEP+ \
        realToStr(0.0)

    return row    
        

def tbondToBondData(tb):
     b = BondData()
     b.name = tb.name
     b.isin = tb.isin
     b.monthsToMaturity = monthsCount(tb.maturity_date)
     b.nominalPrice = int(moneyValueToReal(tb.nominal))
     b.couponsCountPerYear = tb.coupon_quantity_per_year
     return b

def precalcProfit(b):
    b.couponAmountPerYear = round(b.coupon * b.couponsCountPerYear, 2)
    if b.nominalPrice > 0:
        b.nominalProfitPerYear = round(b.couponAmountPerYear * 100 / b.nominalPrice, 2)
    if b.currentPrice > 0:
        b.currentProfitPerYear = round(b.couponAmountPerYear * 100 / b.currentPrice, 2)

    if b.nominalPrice > 0 and b.currentPrice > 0:
        couponAmount = b.couponAmountPerYear / 12 * b.monthsToMaturity
        totalAmount = couponAmount - (b.currentPrice - b.nominalPrice)
        amountByYear = totalAmount / b.monthsToMaturity * 12
        b.maturityProfitPerYear = round(amountByYear / b.currentPrice * 100, 2)

    if b.nominalPrice > 0 and b.currentPrice > 0 and b.monthsToOffer > 0:
        couponAmount = b.couponAmountPerYear / 12 * b.monthsToOffer
        totalAmount = couponAmount - (b.currentPrice - b.nominalPrice)
        amountByYear = totalAmount / b.monthsToOffer * 12
        b.offerProfitPerYear = round(amountByYear / b.currentPrice * 100, 2)

def loadCoupons():
    coupons = []
    if not os.path.isfile(COUPONS_FILE):
        return coupons

    with open(COUPONS_FILE) as file:
        for line in file:
            datas = line.rstrip().split('|')
            c = Coupon()
            c.name = datas[0]
            c.isin = datas[1]
            c.coupon = float(datas[2])
            c.months = int(datas[3])
            coupons.append(c)
    return coupons 

def addCouponToFile(c):
    row = c.name+CSV_SEP+c.isin+CSV_SEP+str(c.coupon)+CSV_SEP+str(c.months)+'\n'
    with open(COUPONS_FILE, 'a') as f:
        f.write(row)    

def findCoupon(coupons, isin):
    for c in coupons:
        if c.isin == isin:
            return c
    return Coupon()  
    
def requestCoupon(client, fig):
    #time.sleep(10)
    today = datetime.datetime.now()
    coupons = client.instruments.get_bond_coupons(
        figi = fig,
        from_= today,
        to = today + datetime.timedelta(days=365))

    if len(coupons.events) == 0:
        return Coupon()

    pay = 0.0
    if len(coupons.events) == 1:    
        pay = coupons.events[-1].pay_one_bond
    else:
        pay = coupons.events[-2].pay_one_bond    

    c = Coupon()
    c.coupon = moneyValueToReal(pay)
    
    lastDate = datetime.datetime.now()
    for e in reversed(coupons.events):
        if (e.pay_one_bond.units == 0):
            break
        lastDate = e.coupon_date

    c.months = monthsCount(lastDate) 
    if (c.months < 1):
        c.months = 1

    return c       

def getCoupon(coupons, client, tb):

    c = findCoupon(coupons, tb.isin)  
    if c.coupon > 0: 
        return c

    c = requestCoupon(client, tb.figi)  
    if c.coupon > 0:
        c.name = tb.name
        c.isin = tb.isin
        coupons.append(c)
        addCouponToFile(c)

    return c    

def findCurrentPrice(prices, figi, nominal):
    for p in prices:
        if p.figi == figi:
            perc = moneyValueToReal(p.price) 
            return round(perc / 100.0 * nominal)
    return 0.0  

def loadRatings():
    ratings = []
    with open(RATINGS_FILE) as file:
        for line in file:
            datas = line.rstrip().split('|')
            r = Rating()
            r.name = datas[0]
            r.isin = datas[1]
            r.rating = datas[2]
            ratings.append(r)
    return ratings    

def findRating(ratings, isin):
    for r in ratings:
        if r.isin == isin:
            return r.rating
    return "-"

def loadBlocked():
    blocked = []
    if not os.path.isfile(BLOCKED_FILE):
        return blocked

    with open(BLOCKED_FILE) as file:
        for line in file:
            datas = line.rstrip().split('|')
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

def isAllowBond(tb, blocked):
    if not tb.buy_available_flag:
        return False
    if not tb.sell_available_flag:
        return False

    if tb.perpetual_flag:
        return False    

    if tb.for_qual_investor_flag:
        return False    

    if not FLOATING_COUPON and tb.floating_coupon_flag:
        return False

    if not AMORTIZATION and tb.amortization_flag:
        return False 

    if monthsCount(tb.maturity_date) < MATURITY:
        return False

    if tb.currency != CURRENCY:
        return False

    if isBlocked(blocked, tb.isin):
        return False   

    return True           

def isRatingLess(r1, r2):
    return RATING_TO_NUM[r1] < RATING_TO_NUM[r2]  

def isProfitAllow(b):
    if b.nominalProfitPerYear == 0:
        return True    

    if b.currentProfitPerYear >= CURRENT_PROFIT and b.maturityProfitPerYear >= MATURITY_PROFIT:
        return True   

    return False 

def isNew(b):
    if b.rating == "":
        return True 
    return False   

def MakeList():
    # parser = argparse.ArgumentParser(description='Tinkoff bonds')
    # parser.add_argument('--only_new', action='store_true', help='Only new bonds')
    # args = parser.parse_args()

    with Client(TOKEN) as client:

        bondsCsv = bondsCsvHeader()
        bondsCsv += '\n'

        prices = client.market_data.get_close_prices().close_prices
        ratings = loadRatings()
        coupons = loadCoupons()
        blocked = loadBlocked()
        stats = bonds_stat.loadStats()

        allbonds = client.instruments.bonds()
        for tb in allbonds.instruments:

              if isAllowBond(tb, blocked):
                rating = findRating(ratings, tb.isin)
                if isRatingLess(rating, RATING):
                    continue   

                myb = tbondToBondData(tb)
                myb.rating = rating
                c = getCoupon(coupons, client, tb)
                myb.coupon = c.coupon
                myb.monthsToOffer = c.months
                myb.currentPrice = findCurrentPrice(prices, tb.figi, myb.nominalPrice)

                if myb.monthsToOffer < MONTH_TO_OFFER:
                    continue

                precalcProfit(myb)

                if not isProfitAllow(myb):
                    continue    

                stat = bonds_stat.findStat(stats, rating)
                myb.nominalProfitDelta = round(myb.nominalProfitPerYear - stat.nominalProfit, 1)
                myb.currentProfitDelta = round(myb.currentProfitPerYear - stat.currentProfit, 1)    
                myb.maturityProfitDelta = round(myb.maturityProfitPerYear - stat.maturityProfit, 1)  

                # if args.only_new and not isNew(myb):
                #     continue

                bondCsv = bondToCsv(myb) 
                print(bondCsv)  
                
                bondsCsv += bondCsv
                bondsCsv += '\n'

        with open(BONDS_FILE, 'w') as bondsFile:
            bondsFile.write(bondsCsv)

def main():
    makeList()

if __name__ == "__main__":
    main()
