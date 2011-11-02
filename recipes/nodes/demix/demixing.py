import pyrap.tables
import sys
import time
import numpy
import os

def demixing (msname, mixingname, avg_msnames, N_channel_per_cell, N_time_per_cell,
              N_pol):
###########################################################################
#msname = 'L23145_SB000_HydA.MS'

# Name of the table containing the mixing matrix
#mixingname = 'L23145_SB000_mixing' # MODIFIED FROM VDTOL


#avg_msnames = ['L23145_SB000_HydA_avg.MS',
##               'L23145_SB000_CygA_avg.MS',
#               'L23145_SB000_CasA_avg.MS',
#               'L23145_SB000_TauA_avg.MS',
#               'L23145_SB000_VirA_avg.MS' ]


#N_channel_per_cell = 60
#N_time_per_cell = 10
#N_pol = 4
############################################################################


   N_dir = len(avg_msnames)

   t = pyrap.tables.table(msname)

   c = 299792458.0
   t_spw = pyrap.tables.table(t.getkeyword('SPECTRAL_WINDOW'))
   freqs = t_spw[0]['CHAN_FREQ']

   N_channel = len(freqs)
   if N_channel_per_cell > N_channel:
      N_channel_per_cell = N_channel

   print "Number of channels: %i" % N_channel

   wavelength = c / freqs


   t_ant = pyrap.tables.table(t.getkeyword('ANTENNA'))
   N_ant = len(t_ant)

# Number of baselines including zero length (autocorrelation) baselines 

   N_baselines = (N_ant * (N_ant + 1)) / 2

   t_field = pyrap.tables.table(t.getkeyword('FIELD'))
   ra, dec = t_field[0]['DELAY_DIR'][0,:]

   x = numpy.sin(ra)*numpy.cos(dec)
   y = numpy.cos(ra)*numpy.cos(dec)
   z = numpy.sin(dec)
   w = numpy.array([[x,y,z]]).T

   x = -numpy.sin(ra)*numpy.sin(dec)
   y = -numpy.cos(ra)*numpy.sin(dec)
   z = numpy.cos(dec)
   v = numpy.array([[x,y,z]]).T

   x = numpy.cos(ra)
   y = -numpy.sin(ra)
   z = 0
   u = numpy.array([[x,y,z]]).T

   T = numpy.concatenate([u,v,w], axis = -1 )


   avg_dem_msnames = []
   avg_tables = []
   avg_dem_tables = []
   w_list =[]

   for avg_msname in avg_msnames :
      avg_dem_msname = avg_msname.replace('.MS', '_dem.MS')
      avg_dem_msnames.append(avg_dem_msname)
      avg_table = pyrap.tables.table(avg_msname)
      avg_tables.append(avg_table)
      avg_table.copy(avg_dem_msname)
      avg_dem_table = pyrap.tables.table(avg_dem_msname, readonly = False)
      avg_dem_tables.append(avg_dem_table)
   
      t_field1 = pyrap.tables.table(avg_dem_table.getkeyword('FIELD'))
      ra1, dec1 = t_field1[0]['DELAY_DIR'][0,:]

      x1 = numpy.sin(ra1)*numpy.cos(dec1)
      y1 = numpy.cos(ra1)*numpy.cos(dec1)
      z1 = numpy.sin(dec1)
      w1 = numpy.array([[x1,y1,z1]]).T
      w_list.append(w1)

   N_cell_in_freq = N_channel / N_channel_per_cell

   tabledesc = {'MIXING': {'_c_order': True,                                                                
                'comment': 'The mixing matrix column',                                              
                'dataManagerGroup': 'mixing',                                                 
                'dataManagerType': 'TiledColumnStMan',                                           
                'maxlen': 0,                                                                     
                'ndim': 4,                                                                       
                'option': 4,                                                                     
                'shape': numpy.array([N_cell_in_freq, N_pol, N_dir, N_dir], dtype=numpy.int32),                                             
                'valueType': 'complex'}}
   t_mix = pyrap.tables.table(mixingname, tabledesc, nrow = len(avg_tables[0]))

   for avg_msname, i in zip(avg_msnames, range(len(avg_msnames))) :
      t_mix.putcolkeywords('MIXING', {'avg_msname%i' % i :avg_msname})
   
   for avg_dem_msname, i in zip(avg_dem_msnames, range(len(avg_dem_msnames))) :
      t_mix.putcolkeywords('MIXING', {'avg_dem_msname%i' % i: avg_dem_msname})
   

   A = numpy.zeros((N_dir, N_dir, N_pol, N_cell_in_freq, N_baselines), dtype=numpy.complex128)
   Ainv = numpy.zeros((N_dir, N_dir, N_pol, N_cell_in_freq, N_baselines), dtype=numpy.complex128)
   data = numpy.zeros((N_dir, N_pol, N_cell_in_freq, N_baselines), dtype=numpy.complex128)

   for pos in range(0, len(t), N_time_per_cell * N_baselines) :
      time_start = time.time()
      uvw = t.getcol('UVW', pos, N_time_per_cell * N_baselines)
      for d in range(N_dir):
         data[d, :,:,:] = avg_dem_tables[d].getcol('DATA', pos/N_time_per_cell, N_baselines).T
      N_time_in_this_cell = uvw.shape[0] / N_baselines
      flags = t.getcol('FLAG', pos, N_time_per_cell * N_baselines)
      weight = t.getcol('WEIGHT_SPECTRUM', pos, N_time_per_cell * N_baselines)
      weight = weight * ~flags
      weight = weight.T.reshape(N_pol, N_cell_in_freq, N_channel_per_cell, N_time_in_this_cell, N_baselines)
      weight_sum = weight.sum(axis = 3).sum(axis = 2)
      for w_idx in range(0, N_dir) :
         A[w_idx, w_idx, :, :, :] = 1.0
         w = w_list[w_idx]
         for w1_idx in range(w_idx+1, N_dir) :
            w1 = w_list[w1_idx]
            f = numpy.dot(numpy.dot((w-w1).T, T) , uvw.T)
            f = numpy.exp(numpy.dot(1.0 / wavelength.reshape(-1,1) * 2 * numpy.pi * 1j, f))
            f = numpy.resize( f, (N_pol, N_cell_in_freq, N_channel_per_cell, N_time_in_this_cell, N_baselines))
            f = f * weight
            f = f.sum(axis = 3)
            f = f.sum(axis = 2)
            f = f / weight_sum
            A[w_idx, w1_idx, :, :, :] = numpy.conj(f)
            A[w1_idx, w_idx, :, :, :] = f
      newdata = numpy.zeros((N_dir, N_pol, N_cell_in_freq, N_baselines), dtype=numpy.complex128)
      newweight = numpy.zeros((N_dir, N_pol, N_cell_in_freq, N_baselines))
      for f_idx in range(N_cell_in_freq) :
         for baseline in range(N_baselines) :
            for pol in range(N_pol) :
               try:
                  Ainv[:,:,pol,f_idx,baseline] = numpy.linalg.inv(A[:,:,pol,f_idx,baseline])
                  v = data[:,pol,f_idx,baseline].reshape((N_dir,1))
                  newdata[:,pol,f_idx,baseline] = numpy.dot(Ainv[:,:,pol,f_idx,baseline],v)[:,0]
                  newweight[:,pol,f_idx,baseline] = 1/numpy.diag(Ainv[:,:,pol,f_idx,baseline])
               #print numpy.diag(Ainv[:,:,f_idx,baseline])
               except numpy.linalg.linalg.LinAlgError:
                  pass
   # set flags
      newweight = newweight * weight_sum
      newweight[numpy.nonzero(numpy.isnan(newweight))] = 0
      for d in range(N_dir):
         avg_dem_tables[d].putcol('DATA', newdata[d, :,:,:].T, pos/N_time_per_cell, N_baselines)
         avg_dem_tables[d].putcol('WEIGHT_SPECTRUM', newweight[d, :,:,:].T, pos/N_time_per_cell, N_baselines)
         avg_dem_tables[d].putcol('FLAG', newweight[d, :,:,:].T == 0, pos/N_time_per_cell, N_baselines)
      t_mix.putcol('MIXING', A.T, pos/N_time_per_cell, N_baselines)
      time_stop = time.time()
      #print time_stop - time_start
      #sys.stdout.flush()


# MODIFIED FROM VDTOL
   for d in range(N_dir):   
      avg_dem_tables[d].unlock()

   t_mix.close()
   t.close()
