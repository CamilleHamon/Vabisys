# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 13:12:38 2020

@author: camilleha
"""


import scipy.io as sio
from scipy.spatial import cKDTree
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

data_folder = 'Data/'

def get_duration_curve(df,col,rows=None):
    df_new = df[col].copy().sort_values(ascending=False).reset_index(drop=True)
    if rows:
        df_new = df_new.iloc[rows]
    return df_new

def load_svk_scenarios(filename, columns):
    svk_file = sio.loadmat(data_folder+filename)
    df = pd.DataFrame(svk_file['M_Price'], columns=columns)
    df = pd.DataFrame(np.reshape(df['FI'].values, (8736,31)), 
                             columns=['Scenario {}'.format(i) for i in range(1,32)])
    return df

svk_2030_file = sio.loadmat(data_folder+'m_price_2030')
svk_2040ref_file = sio.loadmat(data_folder+'m_price_2040ref')
svk_2040low_file = sio.loadmat(data_folder+'m_price_2040low')
svk_2040high_file = sio.loadmat(data_folder+'m_price_2040high')

columns = ['SE{}'.format(i) for i in range(1,5)]+['NO{}'.format(i) for i in range(1,6)] + ['FI'] + ['DK2']
prices_2030_svk = pd.DataFrame(svk_2030_file['M_Price'], columns=columns)
prices_FI_vtt = pd.read_csv(data_folder+'VTT_Finland_elprices_2030.csv')
prices_FI_svk = pd.DataFrame(np.reshape(prices_2030_svk['FI'].values, (8736,31)), 
                             columns=['Scenario {}'.format(i) for i in range(1,32)])
prices_2040ref_svk = load_svk_scenarios('m_price_2040ref',columns)
prices_2040low_svk = load_svk_scenarios('m_price_2040low',columns)
prices_2040high_svk = load_svk_scenarios('m_price_2040high',columns)

nb_hours = 8736
# To be consistent with Svk way of modelling, we only keep 52 weeks per year 
# i.e. 364 days or 8736 hours (8735 = 8736-1 because of indexing from zero)
prices_FI_vtt = prices_FI_vtt.loc[:nb_hours-1,:].copy()


# All together
fig=plt.figure()
all_prices = pd.concat([prices_FI_vtt, prices_FI_svk], axis=1)
ax = sns.boxplot(x='variable', y='value', data=pd.melt(all_prices))
ax.set_xticklabels(ax.get_xticklabels(),rotation=90)
ax.set_ylabel('Price FI (SEK/MWh)')
ax.set_xlabel('')

# Plot Svk's 31 scenarios and VTT's 3 scenarios on the same graph
linestyles = ['-','--','-.']
fig=plt.figure()
ax = prices_FI_svk.plot(color='lightgray', legend=None)
prices_FI_vtt.plot(ax=ax, style=linestyles, color='k', zorder=2)
plt.ylabel('Price FI [SEK/MWh]')

# Duration curves
fig=plt.figure()
for col in prices_FI_svk:
    to_plot = prices_FI_svk[col].copy().sort_values(ascending=False).reset_index(drop=True)
    to_plot.plot(color='lightgray', label='_')
for col in prices_FI_vtt:
    to_plot = prices_FI_vtt[col].copy().sort_values(ascending=False).reset_index(drop=True)
    to_plot.plot(label=col)
plt.ylabel('Price FI (SEK/MWh)')
plt.xlabel('Hours')
plt.title('Duration curves')
plt.legend()

# And two close-ups on the tails
fig=plt.figure()
for col in prices_FI_svk:
    to_plot = get_duration_curve(prices_FI_svk, col, rows=range(500))
    to_plot.plot(color='lightgray', label='_')
for col in prices_FI_vtt:
    to_plot = get_duration_curve(prices_FI_vtt, col, range(500))
    to_plot.plot(label=col)
plt.legend()
plt.ylabel('Price FI (SEK/MWh)')
plt.title('Duration curves - Close-up ')
plt.xlabel('Hours')

fig=plt.figure()
for col in prices_FI_svk:
    to_plot = get_duration_curve(prices_FI_svk, col, range(7000,nb_hours))
    to_plot.plot(color='lightgray', label='_')
for col in prices_FI_vtt:
    to_plot = get_duration_curve(prices_FI_vtt, col, range(7000,nb_hours))
    to_plot.plot(label=col)
plt.legend()
plt.ylabel('Price FI (SEK/MWh)')
plt.title('Duration curves - Close-up ')
plt.xlabel('Hours')

# Finding the closer Svk scenarios
stats = all_prices.describe()
# remove the row count
stats = stats.iloc[1:]

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