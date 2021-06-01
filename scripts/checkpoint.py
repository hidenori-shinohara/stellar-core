import subprocess


def checkpointNumber(n):
    while (n + 1) % 64 != 0:
        n -= 1
    return n


def getFileName(n):
    s = hex(n)[2:]
    while len(s) < 8:
        s = "0" + s
    return "transactions-{}.xdr".format(s)


ledger = 35370879
days = 7  # number of days to go back

ledger = checkpointNumber(ledger)
numCheckpoints = days * 24 * 60 // 5

f = open("txstats.csv", "w")

for checkpoint in range(numCheckpoints):
    cmd = "stellar-core dump-xdr --txstats " + getFileName(ledger)
    print("Running {}".format(cmd))
    output = subprocess.check_output(cmd.split()).decode("utf-8")
    f.write(output)
    ledger -= 64

f.close()
