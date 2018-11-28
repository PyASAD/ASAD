import sys

age = float(sys.argv[1])
fname = sys.argv[2]

f = open(fname)
ages = list(map(float, f.readline().strip('#').strip().split(',')))
index = None
try:
  index = ages.index(age)
except:
  print 'Age not found'
  sys.exit(1)

lines = f.readlines()
data = []
for line in lines:
    if len(line.strip()) == 0:
        continue
    dat = list(map(float, line.split()[1:]))
    data.append(dat)

M = len(data)
N = len(data[0])
flux = N * [M * [0]]

for i in range(M):
    for j in range(N):
        flux[j][i] = data[i][j]

column = flux[index]
for x in column:
    print x