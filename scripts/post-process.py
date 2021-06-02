f = open("txstats.csv", "r")

cnt = dict()

total = 0

for line in f:
    if line not in cnt:
        cnt[line] = 0
    cnt[line] += 1
    total += 1

# Print the output from the most common class
for key in sorted(cnt, key=cnt.get, reverse=True):
    ls = key.split(",")
    size = int(ls[0])
    numOps = int(ls[1])
    avgOpSize = int(ls[2])
    percentage = 100 * cnt[key] / total
    formattedNumOps = str(numOps) if numOps <= 10 else "[{}, {}]".format(numOps - 9, numOps)
    template = "There are {} txns ({:.2f} % of all txns) " + \
               "such that it is [{},{}] bytes, " + \
               "it contains {} ops and " + \
               "the avg size of the ops in it is [{},{}] bytes"
    print(template.format(cnt[key], percentage,
                          size - 99, size,
                          formattedNumOps,
                          avgOpSize - 19, avgOpSize))
