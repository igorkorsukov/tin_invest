import os
import datetime
from dataclasses import dataclass

import modules.utils as utils

COUPONS_FILE = "coupons.csv"
CSV_SEP = '|'

@dataclass
class Coupon:
    name: str = ""
    isin: str = ""
    value: float = 0.0
    months: int = 0   

def init(config):
    global COUPONS_FILE
    global CSV_SEP

    COUPONS_FILE = config.COUPONS_FILE
    CSV_SEP = config.CSV_SEP

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
            c.value = float(datas[2])
            c.months = int(datas[3])
            coupons.append(c)
    return coupons     

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
        to = today + datetime.timedelta(days=365*10))

    if len(coupons.events) == 0:
        return Coupon()

    pay = 0.0
    if len(coupons.events) == 1:    
        pay = coupons.events[0].pay_one_bond
    else:
        pay = coupons.events[1].pay_one_bond 

    c = Coupon()
    c.value = utils.moneyValueToReal(pay)
    
    lastDate = today
    for e in coupons.events:
        if (e.pay_one_bond.units == 0):
            break
        lastDate = e.coupon_date

    c.months = utils.monthsCount(lastDate) 
    if (c.months < 1):
        c.months = 1

    return c       

def getCoupon(coupons, client, tb):

    c = findCoupon(coupons, tb.isin)  
    if c.value > 0: 
        return c

    c = requestCoupon(client, tb.figi)  
    if c.value > 0:
        c.name = tb.name
        c.isin = tb.isin
        coupons.append(c)
        addCouponToFile(c)

    return c 

def addCouponToFile(c):
    row = c.name+CSV_SEP+c.isin+CSV_SEP+str(c.value)+CSV_SEP+str(c.months)+'\n'
    with open(COUPONS_FILE, 'a') as f:
        f.write(row)        

def clearFile():
    open(COUPONS_FILE, 'w').close()    