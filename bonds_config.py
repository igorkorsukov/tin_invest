import os

TOKEN = os.environ["INVEST_TOKEN"]

RATING = "BBB-"
NOMINAL_PROFIT = 8      # percent
CURRENT_PROFIT = 12     # percent
MATURITY_PROFIT = 12    # percent
MATURITY = 8            # month
NOMINAL_DELTA_MIN = -100 
CURRENT_DELTA_MIN = -100 
MATURITY_DELTA_MIN = -100 
AMORTIZATION = True
FLOATING_COUPON = False
CSV_SEP = '|'
CURRENCY = "rub"

BONDS_FILE = "bonds.csv"
RATINGS_FILE = "ratings.csv"
COUPONS_FILE = "coupons.csv"
BLOCKED_FILE = "bonds_blocked.csv"
FAVS_FILE = "bonds_favs.csv"
STATS_FILE = "stats.csv"
