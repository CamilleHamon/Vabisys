# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 14:40:31 2020

@author: camilleha
"""

from utils import load_svk_scenarios, get_hourly_time_index
import pandas as pd
from pathlib import Path
import numpy as np

create_price_scenarios = True
create_heat_scenarios = True

if create_price_scenarios:
    columns = ['SE{}'.format(i) for i in range(1,5)]+['NO{}'.format(i) for i in range(1,6)] + ['FI'] + ['DK2']
    area = 'SE3'
    eur_to_sek = 10.47 # today's exchange rate
    wy=1
    # Importing all scenarios
    prices_scenarios = ['m_price_2030','m_price_2040ref','m_price_2040low','m_price_2040high']
    create_df = lambda n: eur_to_sek*load_svk_scenarios(n, columns, area=area, wy=wy).rename('ElPrice-SEK')
    prices = [create_df(n) for n in prices_scenarios]
    
    # export the scenarios for 2030 and 2040
    for p, n in zip(prices, prices_scenarios):
        n = n[2:] # get rid of the leading m_
        p.to_csv('Data/CreatedScenarios/DAprice-scenarios/'+n+'.csv', index_label='Timestamp')
        
    # create scnarios for the period 2020-2025 from the 2018 prices
    year_to_use = '2018'
    folder = Path('Data/') / 'RawData'
    prices = pd.read_csv(folder / "electricity_prices.csv", parse_dates=['Timestamp'], index_col=['Timestamp']).loc[year_to_use,:]
    # look for the first monday
    weekdays = prices.index.weekday.values
    mondays = np.where(weekdays==0)[0]
    first_monday = mondays[0]
    last_idx = first_monday+8736
    prices = prices.iloc[first_monday:last_idx,]
    # export the corresponding dataframe
    new_index = get_hourly_time_index(2020)
    prices.index = new_index
    prices.to_csv('Data/CreatedScenarios/DAprice-scenarios/price_{}.csv'.format(2020), index_label='Timestamp')

if create_heat_scenarios:
    folder = Path('Data/') / 'RawData' / 'Boras'
    year_to_use = '2017'
    # Load data for the year to use
    heat_demand_ts = pd.read_csv(folder / "heat_demand.csv", parse_dates=['Timestamp'], index_col=['Timestamp']).loc[year_to_use,:]
    # look for the first monday
    weekdays = heat_demand_ts.index.weekday.values
    mondays = np.where(weekdays==0)[0]
    first_monday = mondays[0]
    last_idx = first_monday+8736
    heat_demand = heat_demand_ts.iloc[first_monday:last_idx,]
    for year in [2030,2040]:
        new_index = get_hourly_time_index(year)
        heat_demand.index = new_index
        heat_demand.to_csv('Data/CreatedScenarios/BORAS-scenarios/heat_demand_{}.csv'.format(year), index_label='Timestamp')