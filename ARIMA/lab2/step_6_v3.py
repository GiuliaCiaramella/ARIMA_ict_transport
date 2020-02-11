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

# prendi df da css:
cities = ['Milano', 'New York City', 'Frankfurt']

for city in cities:
  df = pd.read_csv('./'+city+'/'+city+'.csv')


  df.rentals += np.random.random_sample(len(df.rentals)) / 10.0
  df = df.rentals
  df = df.values
  df = df.astype('float32')


  warnings.filterwarnings("ignore") # to remove the possible warning in output

  training_size = 24*7*3 # 3 weeks
  test_len = 24 * 7

  p=4
  q=2
  d = 0
  order = (p, d, q)

  best_mse, best_order = float("inf"), None
  result_temp = []

  slide_train = df[0: training_size]
  slide_test = df[training_size: training_size + test_len]
  past_data = copy.deepcopy(slide_train).tolist()

  prediction = list()

  for instants_to_test in range(0, test_len):
      model = ARIMA(past_data, order=order)
      model_fit = model.fit(disp=0, maxiter=500, method='css')

      output = model_fit.forecast()[0][0]
      prediction.append(output)
      past_data.append(slide_test[instants_to_test])
      #past_data = past_data[1:]
  model_fit.plot_predict(dynamic=False)
  plt.title('ARIMA('+str(p)+','+str(d)+','+str(q)+') - '+city)
  plt.savefig(city+'_model_fit.pdf')
  plt.legend('forecast', 'real data')
  plt.xlabel('hrs')
  plt.ylabel('rentals')
  plt.show()
  mse = mean_squared_error(slide_test, prediction)
  print(city, mse)

  error = pd.DataFrame(model_fit.resid)

  fig2 = error.plot(kind='kde').get_figure()
  plt.title('Error distribution - ' + city)
  fig2.savefig(city + '_error_distribution.pdf')
  # fig2 = error.plot().get_figure()
  # plt.title('Residual - ' + city)
  # fig2.savefig(city + '_error.pdf')

# results:
# Milano 2615.938668155933
# New York City 349.00958005098767
# Frankfurt 120.20703550154629