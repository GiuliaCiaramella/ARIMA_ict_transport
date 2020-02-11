
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
folder = os.path.dirname(os.path.abspath(__file__))
from statsmodels.graphics.tsaplots import plot_pacf, plot_acf   # Per il plot dei correlogrammi



city = 'Milano'
# prendi df da css:
df = pd.read_csv('lab2/'+city+'/'+city+'.csv')

city = city.replace(' ', '')

# 1) prendi i valori di rentals e trasformali da integer a float, per motivi pratici
df.rentals += np.random.random_sample(len(df.rentals))/10.0
# 2) ti interessano solo i rental, quindi:
df = df.rentals
fig =plt.figure()
pd.plotting.autocorrelation_plot(df)
plt.title('ACF '+ city)
plt.savefig(city+'_ACF_.pdf')
plt.show()



fig1, ax1 = plt.subplots( 1, 1 )
plot_acf( df, ax = ax1, lags = 50 )
plt.title('ACF zoom '+city)

plt.savefig(city+'_ACF_zoom.pdf') # quello strano

# # PACF
fig2, ax2 = plt.subplots( 1, 1)
plot_pacf( df, ax = ax2, lags = 50 )

#[ax2.axvline(lag, color = "blue", lw = 10, alpha = 0.2) for lag in range(3)]
#[ax2.axvline(lag, color = "red", lw = 10, alpha = 0.2) for lag in range(23,24,1)]
plt.title('PACF '+city)
plt.savefig(city+'_PACF_.pdf')
plt.show()

print('end')