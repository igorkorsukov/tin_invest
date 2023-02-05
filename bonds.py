import os
import datetime
import time
from dataclasses import dataclass

from tinkoff.invest import Client

TOKEN = os.environ["INVEST_TOKEN"]

RATING = "BB+"
CURRENT_PROFIT = 12     # percent
MATURITY_PROFIT = 11    # percent
MATURITY = 12           # month
AMORTIZATION = True
FLOATING_COUPON = False
CSV_SEP = '|'
CURRENCY = "rub"

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
    nominalPrice: int = 0.0
    currentPrice: int = 0.0
    couponsCountPerYear: int = 0
    coupon: float = 0.0
    couponAmountPerYear: float = 0.0
    nominalProfitPerYear: float = 0.0
    currentProfitPerYear: float = 0.0
    maturityProfitPerYear: float = 0.0

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
    return mv.units + (mv.nano / 1000000000.0)

def realToStr(v):
    return str(v).replace('.',',')   

def bondsCsvHeader():
    h = "Название|ISIN|Рейтинг|Срок(м)|Номинал|Цена|Кол куп|Сумма куп|% номинал|% текущ|% к погош"
    return h

def bondToCsv(b):
    row = b.name+CSV_SEP+ \
        b.isin+CSV_SEP+ \
        b.rating+CSV_SEP+ \
        str(b.monthsToMaturity)+CSV_SEP+ \
        str(b.nominalPrice)+CSV_SEP+ \
        str(b.currentPrice)+CSV_SEP+ \
        str(b.couponsCountPerYear)+CSV_SEP+ \
        realToStr(b.couponAmountPerYear)+CSV_SEP+ \
        realToStr(b.nominalProfitPerYear)+CSV_SEP+ \
        realToStr(b.currentProfitPerYear)+CSV_SEP+ \
        realToStr(b.maturityProfitPerYear)
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
            coupons.append(c)
    return coupons 

def addCouponToFile(c):
    row = c.name+CSV_SEP+c.isin+CSV_SEP+str(c.coupon)+'\n'
    with open(COUPONS_FILE, 'a') as f:
        f.write(row)    

def findCoupon(coupons, isin):
    for c in coupons:
        if c.isin == isin:
            return c.coupon
    return -1  
    
def requestCoupon(client, fig):
    #time.sleep(10)
    today = datetime.datetime.now()
    coupons = client.instruments.get_bond_coupons(
        figi = fig,
        from_= today,
        to = today + datetime.timedelta(days=365))

    if len(coupons.events) == 0:
        return 0.0
        
    pay = coupons.events[-1].pay_one_bond
    return moneyValueToReal(pay)

def getCoupon(coupons, client, tb):

    cv = findCoupon(coupons, tb.isin)  
    if cv > 0: 
        return cv

    cv = requestCoupon(client, tb.figi)  
    if cv > 0:
        c = Coupon()
        c.name = tb.name
        c.isin = tb.isin
        c.coupon = cv
        coupons.append(c)
        addCouponToFile(c)

    return cv    

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

def main():
    with Client(TOKEN) as client:

        bondsCsv = bondsCsvHeader()
        bondsCsv += '\n'

        prices = client.market_data.get_close_prices().close_prices
        ratings = loadRatings()
        coupons = loadCoupons()
        blocked = loadBlocked()

        allbonds = client.instruments.bonds()
        for tb in allbonds.instruments:
              if isAllowBond(tb, blocked):
                rating = findRating(ratings, tb.isin)
                if isRatingLess(rating, RATING):
                    continue

                myb = tbondToBondData(tb)
                myb.rating = rating
                myb.coupon = getCoupon(coupons, client, tb)
                myb.currentPrice = findCurrentPrice(prices, tb.figi, myb.nominalPrice)

                precalcProfit(myb)

                if not isProfitAllow(myb):
                    continue

                bondCsv = bondToCsv(myb) 
                print(bondCsv)  
                
                bondsCsv += bondCsv
                bondsCsv += '\n'

        with open("bonds.csv", 'w') as bondsFile:
            bondsFile.write(bondsCsv)


if __name__ == "__main__":
    main()
