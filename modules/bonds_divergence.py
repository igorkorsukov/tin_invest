import datetime
from dataclasses import dataclass

from tinkoff.invest import CandleInterval, InstrumentClosePriceRequest

from . import utils

BOND_1 = "SU26244RMFS2"
BOND_2 = "SU26243RMFS4"
NOMINAL = 1000
REF_DATETIME = datetime.datetime(2023, 11, 3, 16, 0)

BOND_1_REF_PRICE = 0
BOND_2_REF_PRICE = 0

@dataclass
class DivergenceInfo:
    bond1: str = ""
    bond2: str = ""
    delta1: float = 0.0
    delta2: float = 0.0
    divergence: float = 0.0

def init(config):
    global BOND_1
    global BOND_2
    global REF_DATETIME

    # BOND_1 = config.BOND_1    
    # BOND_2 = config.BOND_2
    # REF_DATETIME = config.REF_DATETIME

def getIntrumentUid(client, q):
    return client.instruments.find_instrument(query = q).instruments[0].uid

def bondValueToPrice(q, nominal):
    perc = utils.moneyValueToReal(q) 
    return round(perc / 100.0 * nominal)

def getPrice(client, intrument_uid, dt):
    response = client.market_data.get_candles(
        instrument_id = intrument_uid,
        from_ = dt,
        to = dt + datetime.timedelta(minutes=5),
        interval = CandleInterval.CANDLE_INTERVAL_1_MIN
        )
    
    if len(response.candles) == 0:
        return 0

    candel = response.candles[0]
    # print(candel)
    return bondValueToPrice(candel.close, NOMINAL)

def getLastPrice(client, intrument_uid):
    response = client.market_data.get_last_prices(instrument_id = intrument_uid)
    # print(response)

    p = bondValueToPrice(response.last_prices[0].price, NOMINAL) 
    if p != 0:
        return p
    
    response = client.market_data.get_close_prices(instruments = [InstrumentClosePriceRequest(instrument_id = intrument_uid)])
    # print(response)
    
    return bondValueToPrice(response.close_prices[0].price, NOMINAL) 

def divergence(client):
    
    global BOND_1_REF_PRICE
    global BOND_2_REF_PRICE

    bondUid1 = getIntrumentUid(client, BOND_1)
    bondUid2 = getIntrumentUid(client, BOND_2)

    if BOND_1_REF_PRICE == 0:
        BOND_1_REF_PRICE = getPrice(client, bondUid1, REF_DATETIME)

    if BOND_2_REF_PRICE == 0:
        BOND_2_REF_PRICE = getPrice(client, bondUid2, REF_DATETIME)    

    lastPrice1 = getLastPrice(client, bondUid1)
    lastPrice2 = getLastPrice(client, bondUid2)

    info = DivergenceInfo()
    info.bond1 = BOND_1
    info.bond2 = BOND_2

    info.delta1 = round(lastPrice1 / BOND_1_REF_PRICE * 100 - 100, 2)
    info.delta2 = round(lastPrice2 / BOND_2_REF_PRICE * 100 - 100, 2)

    info.divergence = round(info.delta1 - info.delta2, 2)
    return info