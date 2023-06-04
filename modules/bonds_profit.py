from . import bonds_prices
from . import utils

def couponAmountPerYear(tb, coupon):
    couponsCountPerYear = tb.coupon_quantity_per_year
    couponAmountPerYear = round(coupon * couponsCountPerYear, 2)
    return couponAmountPerYear

def nominalProfit(tb, coupon):
    nominalPrice = bonds_prices.nominalPrice(tb)
    if nominalPrice <= 0:
        return 0.0

    return round(couponAmountPerYear(tb, coupon) * 100 / nominalPrice, 2)

def currentProfit(tb, coupon, currentPrice):
    if currentPrice <= 0.0:
        return 0.0

    return round(couponAmountPerYear(tb, coupon) * 100 / currentPrice, 2)    

def maturityProfit(tb, coupon, currentPrice):
    nominalPrice = bonds_prices.nominalPrice(tb)
    if nominalPrice > 0 and currentPrice > 0:
        monthsToMaturity = utils.monthsCount(tb.maturity_date)
        couponAmount = couponAmountPerYear(tb, coupon) / 12 * monthsToMaturity
        totalAmount = couponAmount - (currentPrice - nominalPrice)
        amountByYear = totalAmount / monthsToMaturity * 12
        maturityProfitPerYear = round(amountByYear / currentPrice * 100, 2)   
        return maturityProfitPerYear