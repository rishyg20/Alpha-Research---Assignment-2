from datetime import datetime
import os
import pandas as pd

from sip.alpha import *
from sip.alpha import data, util

fred = data.api.fred()

SERIES = [
    'VIXCLS', # cboe volatility index
    'DGS3MO', # 3 month treasury yield
    'T10Y2Y', # 10 year treasury yield minus 2 year treasury yield
    'DTWEXBGS', # trade weighted dollar index: broad goods
    'DCOILWTICO', # wti crude oil price
    'BAMLH0A0HYM2', # ICE BofA US High Yield Index Option-Adjusted Spread
    'SOFR', # secured overnight financing rate  
    'EFFR',   # effective federal funds rate
    'UNRATE', # unemployment rate
    'PAYEMS', # payroll employment: total nonfarm
    'CPIAUCSL', # consumer price index for all urban consumers: all items
    'GDPC1', # real gross domestic product
    'M2SL', # M2 money stock
    'PCEPI', # personal consumption expenditures: price index
    'PCECC96', # real personal consumption expenditures
]

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "sip", "alpha", "fred"))

START_DATE = '2019-01-01'

@timer
def info(refresh=False):
    path = os.path.abspath(os.path.join(DATA_DIR, "fred_series_info.csv"))
    if not refresh and os.path.exists(path):
        logger.info(f"Loading series info from {path}...")
        return pd.read_csv(path, index_col=0)
    else:
        logger.warning(f"Series info not found at {path}. Initiating download...")
        df = pd.concat([fred.get_series_info(i) for i in SERIES], axis=1).T
        df.set_index('id', inplace=True)
        df.to_csv(path)
        logger.info("Data successfully cached.")
        return info()
    
@timer
def releases(refresh=False):
    path = os.path.abspath(os.path.join(DATA_DIR, "fred_releases.csv"))
    if not refresh and os.path.exists(path):
        logger.info(f"Loading releases from {path}...")
        return pd.read_csv(path, index_col=0, parse_dates=['date', 'realtime_start'])
    else:
        logger.warning(f"Releases not found at {path}. Initiating download...")
        data = []
        for s in SERIES:
            logger.info(f"Downloading releases for series {s}...")
            r = fred.get_series_all_releases(s, realtime_start=START_DATE, realtime_end=util.est_today())
            r = r[r['value'].notna()]
            r['id'] = s
            data.append(r)
        df = pd.concat(data).set_index('id')
        df.to_csv(path)
        logger.info("Data successfully cached.")
        return releases()
    
def point_in_time(date = util.est_today(), refresh=False):
    path = os.path.abspath(os.path.join(DATA_DIR, f"fred_point_in_time_{date}.csv"))
    if not refresh and os.path.exists(path):
        logger.info(f"Loading point-in-time data for {date} from {path}...")
        df = pd.read_csv(path, parse_dates=['date'])
        return df.set_index('date')
    else:
        logger.warning(f"Point-in-time data for {date} not found at {path}. Initiating download...")
        releases_data = releases()
        df = pd.DataFrame()
        df['date'] = pd.date_range(START_DATE, date, freq = util.us_business_day)
        df.set_index('date', inplace=True)
        for s in SERIES:
            logger.info(f"Processing series {s}...")
            r = releases_data.loc[s].reset_index()
            # recent release for ech date
            latest_revisions = r.loc[r.groupby('date')['realtime_start'].idxmax()].reset_index(drop=True)
            latest_revisions = latest_revisions.sort_values('date').reset_index(drop=True)
            dates_df = pd.DataFrame({'date': df.index}).sort_values('date').reset_index(drop=True)
            # carry forward if nothing is published
            merged = pd.merge_asof(
                dates_df, 
                latest_revisions[['date', 'value']].rename(columns={'date': 'source_date'}),
                left_on='date',
                right_on='source_date', 
                direction='backward'
            )
            df[s] = merged['value'].values
            df[f'{s}_date'] = merged['source_date'].values
        df.to_csv(path)
        logger.info("Data successfully cached.")
        return point_in_time(date)
