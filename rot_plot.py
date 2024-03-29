import matplotlib.pyplot as plt
import numpy as np
import csv

d = []
with open('log.txt', newline='\n') as f:
    reader = csv.reader(f, 'excel-tab')
    try:
        for row in reader:
            if len(row) == 4:
                r = [float(n) for n in row]
                d.append(r)
    except:
        pass

d = np.asarray(d)
x = d[:,0]
plt.scatter(x, d[:,1], label='roll')
plt.scatter(x, d[:,2], label='pitch')
plt.scatter(x, d[:,3], label='yaw')
plt.legend()
plt.show()

# plt.plot(x, d[:,1], label='roll')
# plt.plot(x, d[:,2], label='pitch')
# plt.plot(x, d[:,3], label='yaw')
# plt.legend()
# plt.show()
