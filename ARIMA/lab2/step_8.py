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

# prendi df da css:
df = pd.read_csv('Milano.csv')

df.rentals += np.random.random_sample(len(df.rentals)) / 10.0
df = df.rentals
df = df.values
df = df.astype('float32')


# ----------------------GRID SEARCH---------------------------
warnings.filterwarnings("ignore") # to remove the possible warning in output
# 6) modello + predizione

training_size = 24*7 # one week
test_len = 24 * 3

Training_possible_size = [24*7*1, 2*24*7, 3*24*7] # 1week 2weeks 3weeks

p = 4
q = 2
d = 0
order = (p, d, q)

result_temp_mono = []
for training_size_ in Training_possible_size:
    try:
        slide_train = df[0: training_size_]
        slide_test = df[training_size_: training_size_ + test_len]
        past_data = copy.deepcopy(slide_train).tolist()

        prediction = list()

        model = ARIMA(past_data, order=order)
        model_fit = model.fit(disp=0, maxiter=500, method='css')

        output = model_fit.forecast(steps=test_len)[0]

        mse = mean_squared_error(slide_test, output)
        result_temp_mono.append({'Traning size': int(training_size_ / 24 / 7), 'mse': mse})

        fig1 = plt.figure()
        plt.plot(np.arange(test_len), slide_test, label="Dataset")
        plt.plot(np.arange(test_len), output, label="Predict")
        plt.title('Real Vs Prediction (training size : ' + str(int(training_size_ / 24 / 7)) + ' weeks)')
        plt.legend()
        fig1.savefig('RealVsPrediction_training'+ str(int(training_size_ / 24 / 7)) + '.pdf')
        plt.show()
        print('Erroe of ARIMA model with model for each prediction: %s' % mse)
    except Exception:
        print("error")

result_mono = pd.DataFrame.from_dict(result_temp_mono)

fig = plt.figure()
plt.close()
array_ = ['1w', '2w', '3w']
plt.plot(array_, result_mono['mse'].values,label='Mono model')
plt.xlim(1, 3)
plt.xlabel('Weeks')
plt.ylabel('MSE')
plt.xticks(array_)
plt.title('Training window size w.r.t. multi models or mono')

result_temp_multi = []
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
        print('Erroe of ARIMA model with model for each prediction: %s' % mse)
        result_temp_multi.append({'Traning size': int(training_size_ / 24 / 7), 'mse': mse})
    except Exception:
        continue

result_multi = pd.DataFrame.from_dict(result_temp_multi)

plt.plot(array_, result_multi['mse'].values,label='Multi Model')
plt.xlim(1, 3)
plt.xlabel('Weeks')
plt.ylabel('MSE')
plt.xticks(array_)
plt.title('Training window size w.r.t. multi models or Mono')

plt.legend()
fig.savefig('Training window size w.r.t. multi models or Mono.pdf')
plt.show()