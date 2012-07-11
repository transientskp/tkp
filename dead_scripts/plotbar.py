#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt

N = 5
x = (20, 35, 30, 35, 27)
menStd =   (2, 3, 4, 1, 2)
bins = (-2,-1,0,1,2)

width = 1./len(x)       # the width of the bars
ind = np.arange(0,1,width)  # the x locations for the groups
print ind

plt.subplot(111)
rects1 = plt.bar(ind, x, width, color='r')

print rects1[0]

# add some
plt.ylabel('Scores')
plt.title('Distribution')
plt.xticks(ind+width/2., bins )

#plt.legend( (rects1[0], rects2[0]), ('Men', 'Women') )

# attach some text labels
#height = rects1[0].get_height()
#plt.text(rects1[0].get_x()+rects1[0].get_width()/2., 1.05*height, '%d'%int(height),ha='center', va='bottom')

plt.show()

