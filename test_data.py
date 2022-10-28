#Written by Patrick Naylor
#Generate day data with semirandom cycling
#Generate 6 other variables with varying levels of corrilation to test data
#Generate Me data based on test data
#Turn into pandas dataframe then test_data[n].db

import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
import math
from scipy.optimize import curve_fit

x = np.arange(500) *((2*math.pi)/49) * (500/(365/12))
r = (np.random.random_sample(500)/2) + .75
Day = ((np.sin(x*r)+1)/2)

p = np.arange(0, .05, .0001)

y = []
means = []
for i in list(np.arange(0, .05, .0001)):
	rtest = (np.random.random_sample(500)*(2*i)) + (1-i)
	vartest = ((np.sin(x*r*rtest)+1)/2)
	y.append(np.corrcoef(Day, vartest)[0,1])


def func(x, a, b, c):
	return a * np.exp(-b *x) + c
popt, pcov = curve_fit(func, p, y, [20, 2130, .1], maxfev=10000)
print(popt)
plt.plot(p, y)


y_fit = func(p, *popt)
coeffs = [.8, .6, .6, .4, .3, .2]
coeffs_x = []
for c in coeffs:
	diff_array = np.absolute(y_fit - c)
	coeffs_x.append(p[np.argmin(diff_array)])
print(coeffs_x)

data_arrays = []
for c_x in coeffs_x:
	r1 = (np.random.random_sample(500)*(2*c_x)) + (1-c_x)
	var = ((np.sin(x*r*r1)+1)/2)
	print(np.corrcoef(Day, var)[0,1])
	data_arrays.append(var)



