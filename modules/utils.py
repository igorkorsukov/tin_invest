import datetime

def monthsCount(dt):
    today = datetime.datetime.now()
    naive = dt.replace(tzinfo=None)
    time_diff = naive - today
    return round(time_diff.days / 365 * 12)

def moneyValueToReal(mv):
    return round(mv.units + (mv.nano / 1000000000.0), 2)    

def realToStr(v):
    return str(v).replace('.',',')       