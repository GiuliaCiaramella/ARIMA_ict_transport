import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
folder = os.path.dirname(os.path.abspath(__file__))
from statsmodels.tsa.arima_model import ARIMA
from sklearn.metrics import mean_squared_error
import copy

# read data:
city = 'New York City'
df = pd.read_csv('lab2/'+city+'/'+city+'.csv')

# city = city.replace(' ', '')
print(city)

# convert in float
df.rentals += np.random.random_sample(len(df.rentals))/10.0
#  we just need rentals..
df = df.rentals

p = 2
q = 2
d = 0


model = ARIMA(df, order=(p, d, q))
model_fit = model.fit(disp=False)

fig =plt.figure()
plt.plot(df, label='Dataset')
plt.plot(model_fit.fittedvalues, label='ARIMA('+str(p)+','+str(d)+','+str(q)+')')
plt.legend()
plt.xlabel('Hours, October 2017')
plt.ylabel('# rentals')
plt.title('ARIMA('+str(p)+','+str(d)+','+str(q)+') fitting dataset')
#fig.savefig(folder + '/'+city+'/ARIMA('+str(p)+','+str(d)+','+str(q)+')_'+city+'.pdf')
plt.savefig(city+'ARIMA('+str(p)+','+str(d)+','+str(q)+')')


error = pd.DataFrame(model_fit.resid)

# compute the error
error = pd.DataFrame(model_fit.resid)
print(error.describe())

# errors for each value


fig2= error.plot().get_figure()
plt.title('error vs hour, '+city)
fig2.savefig(folder + '/'+city+'/ARIMA('+str(p)+','+str(d)+','+str(q)+')_error_vs_hour_'+city+'.pdf')

# curve with low std dev is the better

fig3= error.plot(kind='kde').get_figure()
plt.grid(which= 'minor')
plt.title('ARIMA('+str(p)+','+str(d)+','+str(q)+') residual in '+city)
fig3.savefig(folder + '/'+city+'/ARIMA('+str(p)+','+str(d)+','+str(q)+')_residual_'+city+'.pdf')


plt.show()
