from . import bonds_blocked
from . import utils

MATURITY = 12           # month
AMORTIZATION = True
FLOATING_COUPON = False
CURRENCY = "rub"

def init(config):
    global FLOATING_COUPON
    global AMORTIZATION
    global MATURITY
    global CURRENCY

    FLOATING_COUPON = config.FLOATING_COUPON
    AMORTIZATION = config.AMORTIZATION
    MATURITY = config.MATURITY
    CURRENCY = config.CURRENCY

def isBondAllowed(tb, blocked):
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

    if utils.monthsCount(tb.maturity_date) < MATURITY:
        return False

    if tb.currency != CURRENCY:
        return False

    if bonds_blocked.isBlocked(blocked, tb.isin):
        return False   

    return True           
