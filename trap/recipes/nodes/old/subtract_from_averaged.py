import pyrap.tables
import sys
import time
import numpy
import os

def subtract_from_averaged (msname, mixingname, mspredictnames, msnameout):
######################################################
# The averaged data, including the contribution of other sources
#msname = 'L23145_SB000_HydA_avg.MS'

# Name of the table containing the mixing matrix
#mixingname = 'L23145_SB000_mixing'

# Names of the measurement sets with predicted data in the MODEL_DATA column
# The predicted data is going to be subtracted from the averaged data
#mspredictnames = ('L23145_SB000_CygA_avg_dem.MS',
#                  'L23145_SB000_CasA_avg_dem.MS',
#                  'L23145_SB000_TauA_avg_dem.MS',
#                  'L23145_SB000_VirA_avg_dem.MS' )

# Output measurment set
#msnameout = 'L23145_SB000_HydA_avg_sub2.MS'
#######################################################

   t_mix = pyrap.tables.table(mixingname)
   N_dir = t_mix.getcoldesc('MIXING')['shape'][-1]

   avg_msnames = []
   for i in range(N_dir):
      avg_msnames.append( t_mix.getcolkeyword('MIXING', 'avg_msname%i' % i ) )

   avg_dem_msnames = []
   for i in range(N_dir):
      avg_dem_msnames.append( t_mix.getcolkeyword('MIXING', 'avg_dem_msname%i' % i ) )

   target_idx = avg_msnames.index(msname)
   predict_idx = [avg_dem_msnames.index(mspredictname) for mspredictname in mspredictnames]

   print target_idx
   print predict_idx

   t = pyrap.tables.table(msname)
   t.copy(msnameout)
   t.close()

   t = pyrap.tables.table(msnameout, readonly = False)

   t_predict_list = []
   for mspredictname in mspredictnames:
      t_predict = pyrap.tables.table(mspredictname)
      t_predict_list.append(t_predict)

   for i in range(len(t)):
      data = t.getcol('DATA', i, 1)
      mixing = t_mix.getcol('MIXING', i, 1)
      for t_predict, idx in zip(t_predict_list, predict_idx):
         modeldata = t_predict.getcol('MODEL_DATA', i, 1)
         for channel in range(data.shape[1]) :
            for pol in range(data.shape[2]):
               data[0, channel, pol] -= mixing[0, channel, pol, idx, target_idx]*modeldata[0, channel, pol]
      t.putcol('DATA', data, i, 1)

