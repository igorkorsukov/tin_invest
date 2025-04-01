import os
import time

from tinkoff.invest import Client

import modules.bonds_coupons as bonds_coupons
import modules.bonds_allowed as bonds_allowed
import modules.bonds_blocked as bonds_blocked

import bonds_config as config

TOKEN = os.environ["INVEST_TOKEN"]

def MakeCoupons(config):

    bonds_allowed.init(config)
    bonds_blocked.init(config)

    blocked = bonds_blocked.loadBlocked()

    bonds_coupons.clearFile()

    with Client(TOKEN) as client:
        allbonds = client.instruments.bonds()

        for tb in allbonds.instruments:
            if not bonds_allowed.isBondAllowed(tb, blocked):
                continue

            time.sleep(1)        
            c = bonds_coupons.requestCoupon(client, tb.figi)  
            c.name = tb.name
            c.isin = tb.isin
            print(c)
            bonds_coupons.addCouponToFile(c)

if __name__ == "__main__":
    MakeCoupons(config)            