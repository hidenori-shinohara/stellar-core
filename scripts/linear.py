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

# calculate the relative error

def relativeError(a, b):
    return int(100 * abs(a - b) / max(a, b))

relativeErrorCounts = [0] * 100

tot = 0
for i in range(len(prediction)):
    p = prediction[i][0]
    s = sizes[i][0]
    relativeErrorCounts[relativeError(p, s)] += 1
    tot += 1

runningTotal = 0
for i in range(100):
    cnt = relativeErrorCounts[i]
    runningTotal += cnt
    percent = 100 * runningTotal / tot
    print("{:.2f}% of all txns have <= {}% error".format(percent, i))
