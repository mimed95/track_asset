from time import sleep
import schedule
from src.track_asset import AssetTracker
from src.mailing import send_email
from datetime import datetime
import numpy as np


PERIOD = 15 # minutes
logfile = 'log.txt'

def check_asset_price(fileout=None):
    today = datetime.now()
    condition = (6 < today.hour < 22) & (np.is_busday(today.date()))

    if condition:
        track = AssetTracker()
        tick_value, recent_close, percent_down = track.compare_with_ohlc()
        print(tick_value, recent_close, today.strftime('%d.%m.%Y %H.%M.%S'),
        file=open(fileout, "a"))
        reduction = (recent_close - tick_value)/recent_close
        if reduction >= 0.02:
           send_email(recent_close, reduction)
    else:
        #print(
        #    "sleeping..",
        #    file=open(fileout, "a")
        #)
        pass


schedule.every(PERIOD).minutes.do(check_asset_price, logfile)

while True:
    schedule.run_pending()
    sleep(1)
