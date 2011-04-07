import sys
from pylab import *

"""
Run as:

%> python source_counts.py 15 0.516 263
                           freq[MHz], flux_low[Jy], FoV[deg^2]
"""


a=[0.841,0.540,0.364,-0.063,-0.107,0.052,-0.007]

S_min = 50E-06
S_hi = 2.

"""
nu = float(sys.argv[1])
Snu_lo = float(sys.argv[2])
FoV = float(sys.argv[3])
"""

"""
freq=[15,30,45,60,75,120,150,180,210,240]
FieldOfView=[1676,419,186,105,67,16.2,10.3,7.18,5.28,4.04]
sig = [5.,30.]
S2N = [[5.9,1.9,0.59,0.19,0.059],\
       [1.1,0.35,0.11,0.035,0.011],\
       [0.59,0.19,0.059,0.019,0.0059],\
       [0.39,0.12,0.039,0.012,0.0039],\
       [0.63,0.20,0.063,0.020,0.0063],\
       [0.032,0.010,0.0032,0.001,0.00032],\
       [0.025,0.0078,0.0025,0.00078,0.00025],\
       [0.028,0.0089,0.0028,0.00089,0.00028],\
       [0.032,0.010,0.0032,0.001,0.00032],\
       [0.036,0.011,0.0036,0.0011,0.00036]]
"""
freq=[60,150]
FieldOfView=[105,18.4]
sig = [5.,30.]
#sig = [5.]
S2N = [[0.013],[0.0011]]


for k in range(len(freq)):
    nu = freq[k]
    FoV = FieldOfView[k]
    print "\nIntegrating for", nu, " MHz"
    print "+------ start integration -------------------+"

    for n in range(len(S2N[k])):
        for m in range(len(sig)):
            Snu_lo = sig[m] * S2N[k][n]
            S_lo = Snu_lo * pow((nu / 1400.), 0.7)
            print "|                                            |"
            print "|      sig = ", sig[m]
            print "|      S/N = ", S2N[k][n], " [Jy] "
            print "|      S_lo = ", S_lo, " [Jy]     "
            if (S_lo < S_min):
                sys.exit('Value lower than 50 microJy')
            N = 0.
            S = S_lo
            dS = 1E-06
            j=0
            while (S < S_hi):
                S = S + dS
                sum = 0.
                for i in range(len(a)):
                    fac2 = a[i] * pow(log10(S * 1000), i)
                    sum = sum + fac2
                N += pow(S, -2.5) * pow(10, sum) * dS
                j+=1
                #if (j < 10 or j%100000==0):
                if (j%100000==0):
                    print "j=",j,"S=",S, "N=", N, "sr^{-1}, N=", N/pow((180/pi),2), "deg^{-2}"
                
            # System.out.println("last: " + dSnu + "\t" + mdSnu + "\t" + dN + "\t" + N);
            print "------- end   integration --------------------"
            print "Number of sources: ", N, " sr^{-1}"
            print "Number of sources: ", str(N/pow((180/pi),2)), " deg^{-2}"
            print "Number of sources: ", str(FoV * N/(1000*pow((180/pi),2))), " x 10^3 FoV^{-1}"
            print "----------------------------------------------"

"""
>>> ns=[226,343,574,815,1138,1737,2437,3280,4805,6246,8035,11071,14371]
>>> len(ns)
13
>>> t_int=[10000,5000,2000,1000,500,200,100,50,20,10,5,2,1]
>>> len(t_int)
13
>>> sum=0
>>> for i in range(len(ns)):
...     sum+=ns[i]*t_int[i]
... 
>>> sum

"""
