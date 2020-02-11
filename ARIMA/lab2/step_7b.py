# abbiamo fatto  data cleaning  quindi ora abbiamo i dati filtrati.
# ottobre non ha missing data (da controll manuale, fai controllo iterativo)
# quinid procediamo con il modello
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_squared_error
from mpl_toolkits.mplot3d import Axes3D

from sklearn.metrics import mean_absolute_error as mae
from math import sqrt
import copy
folder = os.path.dirname(os.path.abspath(__file__))
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from statsmodels.tsa.stattools import acf, pacf
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.graphics.tsaplots import plot_pacf, plot_acf  # Per il plot dei correlogrammi
from statsmodels.graphics.gofplots import qqplot  # Per il qqplot
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings
import seaborn as sns

city = 'New York City'
df = pd.read_csv('./'+city+'/'+city+'.csv')

df.rentals += np.random.random_sample(len(df.rentals)) / 10.0
df = df.rentals
df = df.values
df = df.astype('float32')


# ----------------------GRID SEARCH---------------------------
warnings.filterwarnings("ignore") # to remove the possible warning in output
# 6) modello + predizione

training_size = 24*7 # one week
test_len = 24 * 1

Training_possible_size = [24*7*1, 2*24*7, 3*24*7] # 1week 2weeks 3weeks

p = 4
q = 2
d = 0
order = (p, d, q)

# plot distribution of error
model = ARIMA(df, order=(p, d, q))
model_fit = model.fit(disp=True)
fig =plt.figure()

plt.plot(df, label='Dataset')
plt.plot(model_fit.fittedvalues, label='ARIMA('+str(p)+','+str(d)+','+str(q)+')')
plt.legend()
plt.xlabel('Hours, October 2017')
plt.ylabel('# rentals')
plt.title('ARIMA('+str(p)+','+str(d)+','+str(q)+') best model fitting dataset')
plt.show()
fig.savefig(folder + '/'+city+'/ARIMA('+str(p)+','+str(d)+','+str(q)+')_best_model_'+city+'.pdf')

fig2 =plt.figure()
# compute the error
error = pd.DataFrame(model_fit.resid)
# errors for each value
error.plot()
plt.title('error vs hour, '+ city)
fig2.savefig(folder + '/'+city+'/ARIMA('+str(p)+','+str(d)+','+str(q)+')_error_vs_hour_'+city+'.pdf')

fig3 =plt.figure()
# curve with low std dev is the better
error.plot(kind='kde')
plt.grid(which= 'minor')
title = 'ARIMA('+str(p)+','+str(d)+','+str(q)+') residuals in'+city
plt.title(title)
fig3.savefig(folder + '/'+city+'/distribution_in_'+city+'.pdf')

plt.show()

# p_fix = 3 # reasonable choice by looking at the PACF
best_mse, best_order = float("inf"), None
result_temp_expanding = []

for training_size_ in Training_possible_size:

    try:
        slide_train = df[0: training_size_]
        slide_test = df[training_size_: training_size_ + test_len]
        past_data = copy.deepcopy(slide_train).tolist()

        prediction = list()

        for instants_to_test in range(0, test_len):
            model = ARIMA(past_data, order=order)
            model_fit = model.fit(disp=0, maxiter=500, method='css')

            output = model_fit.forecast()[0][0]
            prediction.append(output)
            past_data.append(slide_test[instants_to_test])
            # past_data = past_data[1:]

        mse = mean_squared_error(slide_test, prediction)
        result_temp_expanding.append({'Traning size': int(training_size_/24/7), 'mse': mse})
        if mse < best_mse:
            best_mse, best_size = mse, training_size_/24/7
    except Exception:
        continue
result_expanding = pd.DataFrame.from_dict(result_temp_expanding)

fig = plt.figure()
array_ = ['1w', '2w','3w']
plt.plot(array_, result_expanding['mse'].values,label='expanding window')
plt.scatter(array_, result_expanding['mse'].values)
z = 0
for i in result_expanding['mse']:
    plt.annotate(int(i), (array_[z], i))
    z+=1

plt.xlim(1, 3)
plt.xlabel('Weeks')
plt.ylabel('MSE')
plt.xticks(array_)

plt.title('MSE vs learning strategy and window size - ' + city)

print('Best ARIMA%s MSE=%.3f' % (best_order, best_mse))
print(result_expanding)


result_temp_sliding = []

for training_size_ in Training_possible_size:

    try:
        slide_train = df[0: training_size_]
        slide_test = df[training_size_: training_size_ + test_len]
        past_data = copy.deepcopy(slide_train).tolist()

        prediction = list()

        for instants_to_test in range(0, test_len):
            model = ARIMA(past_data, order=order)
            model_fit = model.fit(disp=0, maxiter=500, method='css')

            output = model_fit.forecast()[0][0]
            prediction.append(output)
            past_data.append(slide_test[instants_to_test])
            past_data = past_data[1:]

        mse = mean_squared_error(slide_test, prediction)
        result_temp_sliding.append({'Traning size': int(training_size_/24/7), 'mse': mse})
        if mse < best_mse:
            best_mse, best_size = mse, training_size_/24/7
    except Exception:
        #result_temp_sliding.append({'Traning size': int(training_size_/24/7), 'mse': 220.3752})
        continue
result_sliding = pd.DataFrame.from_dict(result_temp_sliding)

array_2 = ['2w', '3w']
plt.plot(array_2, result_sliding['mse'].values,label='sliding window')
plt.scatter(array_2, result_sliding['mse'].values)

plt.xlim(1, 2)
plt.xlabel('Training size [weeks]')
plt.ylabel('MSE')
plt.title('MSE vs learning strategy and window size - ' + city)
plt.legend()
plt.xticks(array_)
#plt.text()

z = 0
for i in result_sliding['mse']:
    plt.annotate(int(i), (array_[z+1], i))
    z+=1

fig.savefig(folder + '/'+city+'/'+city+"_7b_sliding_vs_expanding.pdf")
plt.show()
