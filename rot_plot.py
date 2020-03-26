import matplotlib.pyplot as plt
import numpy as np
import csv

d = []
with open('log.txt', newline='\n') as f:
	reader = csv.reader(f, 'excel-tab')
	for row in reader:
		if len(row) == 4:
			r = [float(n) for n in row]
			d.append(r)

d = np.asarray(d)		

print(d.shape)

x = d[:,0]
plt.scatter(x, d[:,1], label='roll')
plt.scatter(x, d[:,2], label='pitch')
plt.scatter(x, d[:,3], label='yaw')
plt.legend()
plt.show()
		