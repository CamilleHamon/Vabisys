# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 14:40:31 2020

@author: camilleha
"""

from utils import load_svk_scenarios
import pandas as pd

create_price_scenarios = False

if create_price_scenarios:
    columns = ['SE{}'.format(i) for i in range(1,5)]+['NO{}'.format(i) for i in range(1,6)] + ['FI'] + ['DK2']
    area = 'SE3'
    eur_to_sek = 10.47 # today's exchange rate
    wy=1
    # Importing all scenarios
    prices_scenarios = ['m_price_2030','m_price_2040ref','m_price_2040low','m_price_2040high']
    create_df = lambda n: eur_to_sek*load_svk_scenarios(n, columns, area=area, wy=wy).rename('ElPrice-SEK')
    prices = [create_df(n) for n in prices_scenarios]
    
    # export the scenarios
    for p, n in zip(prices, prices_scenarios):
        n = n[2:] # get rid of the leading m_
        p.to_csv('Data/CreatedScenarios/DAprice-scenarios/'+n+'.csv', index_label='Timestamp')
