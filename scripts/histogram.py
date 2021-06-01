f = open("txstats.csv", "r")

cnt = dict()

# Remember the maximum size
maxSize = 0

for line in f:
    size = int(line)
    if size not in cnt:
        cnt[size] = 0
        maxSize = max(maxSize, size)
    cnt[size] += 1

# Print the size from 0, 4, 8, ...
# We want to print 0 when there's none
# to make the histogram more readable.
for size in range(maxSize + 1):
    if size % 4 != 0:
        continue
    print("{},{}".format(size, cnt[size] if size in cnt else 0))
