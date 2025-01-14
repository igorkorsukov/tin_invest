from . import utils

def loadPrices(client):
    return client.market_data.get_close_prices().close_prices

def findPrice(prices, figi):
    for p in prices:
        if p.figi == figi:
            return round(utils.moneyValueToReal(p.price), 4)
    return 0.0      