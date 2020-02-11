import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
folder = os.path.dirname(os.path.abspath(__file__))
from statsmodels.tsa.arima_model import ARIMA
from sklearn.metrics import mean_squared_error
import copy

# read data:
city = 'Milano'
df = pd.read_csv('lab2/'+city+'/'+city+'.csv')
df.rentals += np.random.random_sample(len(df.rentals))/10.0


#  we just need rentals..
df = df.rentals

p = 2
q = 2
d = 0
N = 3*7*24
training_dataset = df[0: N]

df = training_dataset

model = ARIMA(df, order=(p, d, q))
model_fit = model.fit(disp=False)

fig =plt.figure()
plt.plot(df, label='Dataset')
plt.plot(model_fit.fittedvalues, label='ARIMA('+str(p)+','+str(d)+','+str(q)+')')
plt.legend()
plt.xlabel('Hours, 1st-21st October 2017')
plt.ylabel('# rentals')
plt.title('ARIMA('+str(p)+','+str(d)+','+str(q)+') fitting dataset - '+city)
#fig.savefig(folder + '/'+city+'/ARIMA('+str(p)+','+str(d)+','+str(q)+')_'+city+'.pdf')
plt.savefig(city+'ARIMA('+str(p)+','+str(d)+','+str(q)+').pdf')

# Actual vs Fitted
model_fit.plot_predict(dynamic=False)
plt.savefig('real_vs_predict.pdf')
plt.show()

# compute the error. 
error = pd.DataFrame(model_fit.resid)

print(error.describe())
fig2= error.plot().get_figure()
plt.title('error vs hour, '+city)
#fig2.savefig(folder + '/'+city+'/ARIMA('+str(p)+','+str(d)+','+str(q)+')_error_vs_hour_'+city+'.pdf')
plt.savefig(city+'_error.pdf')

# curve with low std dev is the better
# we get a density plot of the residual error values, suggesting the errors are Gaussian, but may not be centered on zero.
fig3= error.plot(kind='kde').get_figure()
plt.grid(which= 'minor')
plt.title('ARIMA('+str(p)+','+str(d)+','+str(q)+') residual in '+city)
#fig3.savefig(folder + '/'+city+'/ARIMA('+str(p)+','+str(d)+','+str(q)+')_residual_'+city+'.pdf')
plt.savefig(city+'_density_error.pdf')
plt.show()


# Accuracy metrics
def fit_accuracy(fit, actual):
   
    mpe = np.mean((fit - actual)/actual)   # MPE
    rmse = np.mean((fit - actual)**2)**.5  # RMSE
   
    print('mpe', mpe)

fit_accuracy(model_fit.fittedvalues, df)
# fit_accuracy(error, df)


# mpe milano: 1.29
# mpe nyc: 3.37
# frankfurt: 7.17
