from pandas import DataFrame
from sklearn import datasets, linear_model, metrics

from random import randint

f = open('txstats.csv', 'r')

sizes = []
opcounts = []

for line in f:
    ls = line.split(",")
    size = int(ls[0])
    numops = int(ls[1])
    sizes.append([size])
    opcounts.append([numops])

lr = linear_model.LinearRegression().fit(opcounts, sizes)
prediction = lr.predict(opcounts)


print("coef = {}".format(lr.coef_))
print("intercept = {}".format(lr.intercept_))
print("mse = {}".format(metrics.mean_squared_error(sizes, prediction)))
