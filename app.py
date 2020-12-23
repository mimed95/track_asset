from sched import scheduler
from src.track_asset import AssetTracker
from src.mailing import send_email
from datetime import datetime


def check_asset_price():
    if 6 < datetime.today().hour < 23:
        track = AssetTracker()
        tick_value, recent_close, percent_down = track.compare_with_ohlc()
        print(tick_value, recent_close)
        reduction = (recent_close - tick_value)/recent_close
        if reduction >= 0.02:
            send_email(recent_close, reduction)
        s.enter(900, 1, check_asset_price)
    

if __name__ == "__main__":
    s = scheduler()
    s.enter(10, 1, check_asset_price)
    s.run()