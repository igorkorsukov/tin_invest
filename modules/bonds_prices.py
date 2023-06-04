from . import utils

def loadPrices(client):
    return client.market_data.get_close_prices().close_prices

def findPrice(prices, tb):
    for p in prices:
        if p.figi == tb.figi:
            perc = utils.moneyValueToReal(p.price) 
            return round(perc / 100.0 * nominalPrice(tb))
    return 0.0     

def nominalPrice(tb):
    return int(utils.moneyValueToReal(tb.nominal))    

def currentPrice(prices, tb):
    return findPrice(prices, tb)        