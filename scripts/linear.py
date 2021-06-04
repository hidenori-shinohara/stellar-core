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

# calculate the relative and absolute error

def relativeError(a, b):
    e = int(100 * abs(a - b) / a)
    return min(e, 100) # If off by more than 100%, just say 100%

def absoluteError(a, b):
    e = int(abs(a - b))
    return min(e, 400) # If off by more than 400 bytes, just say 400 bytes


relativeErrorCounts = [0] * 101
absoluteErrorCounts = [0] * 401

tot = 0
smaller = 0
for i in range(len(prediction)):
    p = prediction[i][0]
    s = sizes[i][0]
    relativeErrorCounts[relativeError(s, p)] += 1
    if s < 250:
        smaller += 1
    absoluteErrorCounts[absoluteError(p, s)] += 1
    tot += 1
print("{:.2f}% is smaller than 250 bytes".format(100 * smaller / tot))

runningTotal = 0
for i in range(101):
    cnt = relativeErrorCounts[i]
    runningTotal += cnt
    percent = 100 * runningTotal / tot
    print("{:.2f}% of all txns have <= {}% error".format(percent, i))

runningTotal = 0
for i in range(401):
    cnt = absoluteErrorCounts[i]
    runningTotal += cnt
    percent = 100 * runningTotal / tot
    if i % 4 == 0: # Print every 4 bytes
        print("{:.2f}% of all txns are off by <= {} bytes".format(percent, i))
