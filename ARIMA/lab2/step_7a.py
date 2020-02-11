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


# ----------------------GRID SEARCH---------------------------
warnings.filterwarnings("ignore") # to remove the possible warning in output
# 6) modello + predizione

training_size = 24*7*3 # 3 weeks
test_len = 24 * 7

possible_values_p = [3,4,6,8] # lag number
possible_values_q = range(0,4)
d = 0



for city in cities:
  df = pd.read_csv('lab2/'+city+'/'+city+'.csv')
  df.rentals += np.random.random_sample(len(df.rentals)) / 10.0
  df = df.rentals
  df = df.values
  df = df.astype('float32')

  best_mse, best_order = float("inf"), None
  result_temp = []
  aa = np.zeros((len(possible_values_p), len(possible_values_q)))

  for p in possible_values_p:
      for q in possible_values_q:
          order = (p, d, q)
          try:
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

              mse = mean_squared_error(slide_test, prediction)
              result_temp.append({'p': p, 'q': q, 'mse': mse})
              aa[p,q] = mse
              # print('ARIMA%s MSE=%.3f' % (order, mse))
              if mse < best_mse:
                  best_mse, best_order = mse, order
          except Exception:
              continue

  print('Best ARIMA%s MSE=%.3f' % (best_order, best_mse))
  result = pd.DataFrame.from_dict(result_temp)

  ax = result.pivot(index='p', columns='q', values='mse')

  show = sns.heatmap(ax, annot=True, fmt='g', cmap='viridis',  linewidth=0.5)
  plt.title('Expanding Window - MSE for different p and q - '+city)
  plt.plot()
  #plt.savefig(folder + '/'+city+"/exp_training3w_test1w.pdf")
  plt.savefig('lab2/'+city+'_exp_3tr_1test.pdf')

  plt.show()
print('end')