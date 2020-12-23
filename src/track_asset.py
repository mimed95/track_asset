from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np
import os
from typing import Optional, Union


def _get_date_string(date:datetime):
    return date.strftime('%d.%m.%Y')


class AssetTracker:
    def __init__(self, interval=1800, percent_down=2):
        self.start_date = datetime(2020,11,1)
        self.ticker_update_intervall = interval
        self.percent_down = percent_down
        self._download_ticker()
        self.update_ohlc()
    
    def _rename_cols(self, ohlc):
        ohlc_cols = ["date", "open", "close", "high", "low"]
        renamed_cols = {
            origin: new for origin, new in zip(ohlc.columns, ohlc_cols)
        }
        return ohlc.rename(columns=renamed_cols)
    
    @staticmethod
    def _check_if_today(timestamp:datetime):
        return timestamp.date() == datetime.today().date()
    
    def _check_exists(self, ohlc_name="hydro_cert_daily_ohlc"):
        if os.path.exists(f"data/{ohlc_name}.csv"):
            return True
        else:
            return False

    def _save_ohlc(self, df, ohlc_name="hydro_cert_daily_ohlc"):
        df.to_csv(f"data\{ohlc_name}.csv")

    def update_ohlc(self, ohlc_name="hydro_cert_daily_ohlc"):
        if not self._check_exists():
            df = self.download_ohlc_history()
        else:
            
            df = pd.read_csv(
                f"data/{ohlc_name}.csv",
                dayfirst=True,
                parse_dates=["date"]
            )
            if not AssetTracker._check_if_today(df.date.max()):
                df = self.download_ohlc_history()
        self.ohlc = df
    
    def download_ohlc_history(
        self,
        start:Optional[datetime]=None,
        end:Optional[Union[datetime, str]]='latest',
        onvista_id:Optional[int]=258725091
    ):
        if start is None:
            start_str = _get_date_string(self.start_date)
        else:
            start_str = _get_date_string(start)
        if end == 'latest':
            end_date = datetime.today() - timedelta(days=1)
        end_date_str = _get_date_string(end_date)

        csv_url = "https://www.onvista.de/derivative/snapshotHistoryCSV?" + \
        f"idNotation={onvista_id}&datetimeTzStartRange={start_str}" + \
        f"&datetimeTzLastRange={end_date_str}&codeResolution=1D"

        df = pd.read_csv(
            csv_url,
            sep=";",
            decimal=",",
            parse_dates=["Datum"],
            dayfirst=True
        )
        return self._rename_cols(df)

    def _download_ticker(self, onvista_id:Optional[int]=258725091):
        
        df = pd.read_csv(
            "https://www.onvista.de/derivative/factor/snapshot" + \
            f"TimesSalesCSV?idNotation={onvista_id}",
            skiprows=4,
            sep=";",
            decimal=",",
            parse_dates=["Zeit"],
            usecols=["Zeit", "Kurs"],
            dayfirst=True
            ).rename(columns={"Zeit":"time", "Kurs":"price"})
        self.ticker = df

    def _update_ticker(self, onvista_id:Optional[int]=258725091):

        dt = datetime.today() - self.ticker.iloc[0,0]
        if dt.seconds > self.ticker_update_intervall:
            self._download_ticker(onvista_id)

    def compare_with_ohlc(
        self,
        onvista_id:Optional[int]=258725091
    ):
        self._update_ticker(onvista_id)
        if self._check_exists("hydro_cert_ticker"):
            pass
            
        newest_date_idx = self.ohlc.date.idxmax()
        newest_close = self.ohlc.loc[newest_date_idx, "close"]
        #newest_low = self.ohlc.loc[newest_date_idx, "low"]
        #recent_val = np.mean((newest_close, newest_low))

        return self.ticker.iloc[0,1] , newest_close, (1-self.percent_down/100)

