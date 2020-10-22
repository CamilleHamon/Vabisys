# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 13:12:38 2020

@author: camilleha
"""

from scipy.spatial import cKDTree
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from utils import load_svk_scenarios, get_duration_curve

data_folder = 'Data/'
include_vtt = False
columns = ['SE{}'.format(i) for i in range(1,5)]+['NO{}'.format(i) for i in range(1,6)] + ['FI'] + ['DK2']

if include_vtt:
    prices_FI_vtt = pd.read_csv(data_folder+'VTT_Finland_elprices_2030.csv')
    area = 'FI'
else:
    area = 'SE3'

prices_2030_svk = load_svk_scenarios('m_price_2030', columns, area=area)
prices_2040ref_svk = load_svk_scenarios('m_price_2040ref', columns, area=area)
prices_2040low_svk = load_svk_scenarios('m_price_2040low', columns, area=area)
prices_2040high_svk = load_svk_scenarios('m_price_2040high', columns, area=area)

# Compare 2040 scenarios
comparison_df = pd.concat([prices_2040high_svk.describe()['Scenario 1'], prices_2040low_svk.describe()['Scenario 1']], keys=['2040high','2040low'], names=['Scenario'])
comparison_df = comparison_df.unstack(level=[0]).drop('count')
comparison_withoumax = comparison_df.drop('max')
fig = plt.figure()
comparison_withoumax.plot.bar()
fig = plt.figure()
ax = comparison_df.loc['max',:].plot.bar()
ax.set_ylabel('Max value')

nb_hours = 8736
# To be consistent with Svk way of modelling, we only keep 52 weeks per year 
# i.e. 364 days or 8736 hours (8735 = 8736-1 because of indexing from zero)
if include_vtt:
    prices_FI_vtt = prices_FI_vtt.loc[:nb_hours-1,:].copy()
    all_prices = pd.concat([prices_FI_vtt, prices_2030_svk], axis=1)
else:
    all_prices = prices_2030_svk

# All together
fig=plt.figure()
ax = sns.boxplot(x='variable', y='value', data=pd.melt(all_prices))
ax.set_xticklabels(ax.get_xticklabels(),rotation=90)
ax.set_ylabel('Price {} (SEK/MWh)'.format(area))
ax.set_xlabel('')

# Plot Svk's 31 scenarios and VTT's 3 scenarios on the same graph
linestyles = ['-','--','-.']
fig=plt.figure()
ax = prices_2030_svk.plot(color='lightgray', legend=None)
if include_vtt:
    prices_FI_vtt.plot(ax=ax, style=linestyles, color='k', zorder=2)
plt.ylabel('Price {} [SEK/MWh]'.format(area))

# Duration curves
fig=plt.figure()
for col in prices_2030_svk:
    to_plot = prices_2030_svk[col].copy().sort_values(ascending=False).reset_index(drop=True)
    to_plot.plot(color='lightgray', label='_')
if include_vtt:
    for col in prices_FI_vtt:
        to_plot = prices_FI_vtt[col].copy().sort_values(ascending=False).reset_index(drop=True)
        to_plot.plot(label=col)
plt.ylabel('Price {} (SEK/MWh)'.format(area))
plt.xlabel('Hours')
plt.title('Duration curves')
plt.legend()

# And two close-ups on the tails
fig=plt.figure()
for col in prices_2030_svk:
    to_plot = get_duration_curve(prices_2030_svk, col, rows=range(500))
    to_plot.plot(color='lightgray', label='_')
if include_vtt:
    for col in prices_FI_vtt:
        to_plot = get_duration_curve(prices_FI_vtt, col, range(500))
        to_plot.plot(label=col)
plt.legend()
plt.ylabel('Price {} (SEK/MWh)'.format(area))
plt.title('Duration curves - Close-up ')
plt.xlabel('Hours')

fig=plt.figure()
for col in prices_2030_svk:
    to_plot = get_duration_curve(prices_2030_svk, col, range(7000,nb_hours))
    to_plot.plot(color='lightgray', label='_')
if include_vtt:
    for col in prices_FI_vtt:
        to_plot = get_duration_curve(prices_FI_vtt, col, range(7000,nb_hours))
        to_plot.plot(label=col)
plt.legend()
plt.ylabel('Price {} (SEK/MWh)'.format(area))
plt.title('Duration curves - Close-up ')
plt.xlabel('Hours')

# Finding the closer Svk scenarios
stats = all_prices.describe()
# remove the row count
stats = stats.iloc[1:]

if not include_vtt:
    stats.plot.bar(legend=False)
    plt.ylabel('Price {} [SEK/MWh]'.format(area))
else:
    svk_idx = 3
    vtt_stats = stats.transpose().iloc[0:3,:].copy()
    svk_stats = stats.transpose().iloc[3:,:].copy()
    vtt_idx_find = 0
    tree = cKDTree(svk_stats)
    distances, indices = tree.query(vtt_stats.iloc[vtt_idx_find,:],k=2)
    print(svk_stats.iloc[indices,:])
    # Comparing the statistics of the closest scenarios
    scenarios_to_plot = ['Ref'] + ['Scenario {}'.format(i+1) for i in indices]
    stats[scenarios_to_plot].plot.bar()
    plt.ylabel('Price FI [SEK/MWh]')
    # Plotting the prices in the scenarios close by, divide the year in four plots
    
    period = nb_hours//4
    for i in range(4):
        plt.figure()
        all_prices.iloc[i*period:(i+1)*period][scenarios_to_plot].plot(linewidth=0.5)
        plt.ylabel('Price FI [SEK/MWh]')
        plt.title('Quarter {}'.format(i+1))