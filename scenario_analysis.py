# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 13:12:38 2020

@author: camilleha
"""


import scipy.io as sio
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

data_folder = 'Data/'

mat_contents = sio.loadmat(data_folder+'m_price_2030')

columns = ['SE{}'.format(i) for i in range(1,5)]+['NO{}'.format(i) for i in range(1,6)] + ['FI'] + ['DK2']
prices_2030_svk = pd.DataFrame(mat_contents['M_Price'], columns=columns)
prices_FI_vtt = pd.read_csv(data_folder+'VTT_Finland_elprices_2030.csv')
prices_FI_svk = pd.DataFrame(np.reshape(prices_2030_svk['FI'].values, (8736,31)), 
                             columns=['Scenario {}'.format(i) for i in range(1,32)])

# To be consistent with Svk way of modelling, we only keep 52 weeks per year 
# i.e. 364 days or 8736 hours (8735 = 8736-1 because of indexing from zero)
prices_FI_vtt = prices_FI_vtt.loc[:8735,:].copy()

# All together
fig=plt.figure()
all_prices = pd.concat([prices_FI_vtt, prices_FI_svk], axis=1)
ax = sns.boxplot(x='variable', y='value', data=pd.melt(all_prices))
ax.set_xticklabels(ax.get_xticklabels(),rotation=90)

# Plot Svk's 31 scenarios and VTT's 3 scenarios on the same graph
linestyles = ['-','--','-.']
fig=plt.figure()
ax = prices_FI_svk.plot(color='lightgray', legend=None)
prices_FI_vtt.plot(ax=ax, style=linestyles, color='k', zorder=2)


fig=plt.figure()
for col in prices_FI_svk:
    to_plot = prices_FI_svk[col].copy().sort_values(ascending=False).reset_index(drop=True)
    to_plot.plot(color='lightgray', label='_')
for col in prices_FI_vtt:
    to_plot = prices_FI_vtt[col].copy().sort_values(ascending=False).reset_index(drop=True)
    to_plot.plot(label=col)
plt.legend()

