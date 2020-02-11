import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import matplotlib
import matplotlib.pyplot as plt
import sys

import copy

folder = os.path.dirname(os.path.abspath(__file__))
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.arima_model import ARIMA

import warnings
import seaborn as sns


city = 'Frankfurt'

df = pd.read_csv('./'+city+'/'+city+'.csv')


df.rentals += np.random.random_sample(len(df.rentals)) / 10.0
df = df.rentals


r_m = df.rolling(100).mean()
r_m = r_m.values
r_m = r_m.astype('float32')

st = df.rolling(100).std()
st = st.values
st = st.astype('float32')

df = df.values
df = df.astype('float32')

x = range(745)
plt.plot(x,df, label='real')
plt.plot(x,r_m, label='rolling mean')
plt.plot(x,st, label='rolling std')

plt.title('Rolling Mean (1 week sliding window) - '+city)
plt.legend()

plt.savefig(city+'_rolling_stats.pdf')
plt.show()


print('end1')


