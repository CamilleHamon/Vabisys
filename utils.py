# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 14:18:10 2020

@author: camilleha
"""

import scipy.io as sio
import pandas as pd
import numpy as np
from datetime import timedelta, datetime
from pathlib import Path

def get_hourly_time_index(year):
    start_date = datetime.strptime('{}-01-01'.format(year),'%Y-%m-%d')
    stop_date = start_date+timedelta(hours=8735) # 52 weeks => 8736 in Svks scenarios => first hour + 8735 other hours
    return pd.date_range(start_date, stop_date, freq='H')

def load_svk_scenarios(filename, columns, data_folder='Data/RawData/',area='SE3', weather_year=None):
    svk_file = sio.loadmat(data_folder+filename)
    if '2030' in filename:
        index = get_hourly_time_index(2030)
    elif '2040' in filename:
        index = get_hourly_time_index(2040)
    df = pd.DataFrame(svk_file['M_Price'], columns=columns)
    df = pd.DataFrame(np.reshape(df[area].values, (8736,31)), index=index,
                             columns=['Scenario {}'.format(i) for i in range(1,32)])
    if weather_year is not None:
        # only one scenario
        s = 'Scenario {}'.format(weather_year)
        df = df.loc[:,s]
    return df

def get_duration_curve(df,col,rows=None):
    df_new = df[col].copy().sort_values(ascending=False).reset_index(drop=True)
    if rows:
        df_new = df_new.iloc[rows]
    return df_new

