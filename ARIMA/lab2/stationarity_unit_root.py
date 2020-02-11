#define function for ADF test
from statsmodels.tsa.stattools import adfuller
import pandas as pd


def adf_test(timeseries):
    #Perform Dickey-Fuller test:
    print ('Results of Dickey-Fuller Test:')
    dftest = adfuller(timeseries, autolag='AIC')
    dfoutput = pd.Series(dftest[0:4], index=['Test Statistic','p-value','#Lags Used','Number of Observations Used'])
    for key,value in dftest[4].items():
       dfoutput['Critical Value (%s)'%key] = value
    print (dfoutput)

#apply adf test on the series
city = 'New York City'
# prendi df da css:
df = pd.read_csv('./'+city+'/'+city+'.csv')

adf_test(df['rentals'])

from statsmodels.tsa.stattools import kpss
#define KPSS
def kpss_test(timeseries):
    print ('Results of KPSS Test:')
    kpsstest = kpss(timeseries, regression='c')
    kpss_output = pd.Series(kpsstest[0:3], index=['Test Statistic','p-value','Lags Used'])
    for key,value in kpsstest[3].items():
        kpss_output['Critical Value (%s)' %key] = value
    print ('\n', kpss_output)

kpss_test(df['rentals'])

'''Statistical test

Instead of going for the visual test, we can use statistical tests like the unit root stationary tests.
 Unit root indicates that the statistical properties of a given series are not constant with time, 
 which is the condition for stationary time series. Here is the mathematics explanation of the same :
Suppose we have a time series :
yt = a*yt-1 + ε t

where yt is the value at the time instant t and ε t is the error term. In order to calculate yt we
 need the value of yt-1, which is :

yt-1 = a*yt-2 + ε t-1
If we do that for all observations, the value of yt will come out to be:
yt = an*yt-n + Σεt-i*ai
If the value of a is 1 (unit) in the above equation, then the predictions will be equal to the yt-n 
and sum of all errors from t-n to t, which means that the variance will increase with time. This is
 knows as unit root in a time series. We know that for a stationary time series, the variance must not
  be a function of time. The unit root tests check the presence of unit root in the series by checking 
  if value of a=1. Below are the two of the most commonly used unit root stationary tests:'''


'''Test for stationarity: If the test statistic is greater than the critical value, 
we reject the null hypothesis (series is not stationary). If the test statistic is less than 
the critical value, if fail to reject the null hypothesis (series is stationary). For the air 
passenger data, the value of the test statistic is greater than the critical value at all 
confidence intervals, and hence we can say that the series is not stationary.

I usually perform both the statistical tests before I prepare a model for my time series data. 
It once happened that both the tests showed contradictory results. One of the tests showed that 
the series is stationary while the other showed that the series is not! I got stuck at this part 
for hours, trying to figure out how is this possible. As it turns out, there are more than one type 
of stationarity.
So in summary, the ADF test has an alternate hypothesis of linear or difference stationary, 
while the KPSS test identifies trend-stationarity in a series.


    Case 1: Both tests conclude that the series is not stationary -> series is not stationary
    Case 2: Both tests conclude that the series is stationary -> series is stationary
    Case 3: KPSS = stationary and ADF = not stationary  -> trend stationary, remove the trend to make series strict stationary
    Case 4: KPSS = not stationary and ADF = stationary -> difference stationary, use differencing to make series stationary



'''