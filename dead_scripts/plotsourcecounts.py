#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt

s = np.arange(0.10, 10000.0, 0.01)
y=[]

# log x and y axis
a = [0.841,0.540,0.364,-0.063,-0.107,0.052,-0.007]

for i in range(len(s)):
    logy = 0
    for j in range(len(a)):
        logy = logy + a[j] * np.power(np.log10(s[i]), j)
    y.append(np.power(10,logy))
plt.loglog(s,y)
plt.grid(True)
plt.title('Source counts')

plt.show()

