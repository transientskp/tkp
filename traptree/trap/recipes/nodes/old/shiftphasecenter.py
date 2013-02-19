import pyrap.tables
import sys
import time
import numpy

def shiftphasecenter (msname, targets, N_channel_per_cell, N_time_per_cell):
################## edit the paramers below ####################

    #msname = 'L23145_SB040_HydA.MS'

    targetdirs = { 'CasA': (6.123487680622104,  1.0265153995604648),
                   'CygA': (5.233686575770755,  0.7109409582180791),
                   'TauA': (1.4596748493730913, 0.38422502335921294),
                   'VirA': (3.276086511413598,  0.21626589533567378),
                   'HerA': (4.4119087330382163, 0.087135562905816893),
                   'HydA': (2.4351466,         -0.21110706),
                   'PerA': (0.87180363,         0.72451580)}
                  #'Sun':  (5.0546192 , -0.38024905))            



    #N_channel_per_cell = 60
    #N_time_per_cell = 10

############# edit the parameters above ###################


    # Here's some string juggling magic. Below, when we loop over the given
    # `targets`, we want to replace the last part of `msname` (delimited by
    # underscores, up to but not including the first dot) with the name of
    # the target. Everything after the dot is considered to be part of the
    # filename's extension and should be left untouched.
    basename = (msname.rsplit('_',1)[0] +
                '_%s.' +
                msname.rsplit('_',1)[1].split('.',1)[1])

    t = pyrap.tables.table(msname)
    c = 299792458.0
    t_spw = pyrap.tables.table(t.getkeyword('SPECTRAL_WINDOW'))
    freqs = t_spw[0]['CHAN_FREQ']

    N_channel = len(freqs)

    print "Number of channels: %i" % N_channel

    wavelength = c / freqs

    t_field = pyrap.tables.table(t.getkeyword('FIELD'))
    ra, dec = t_field[0]['DELAY_DIR'][0,:]

    t_ant = pyrap.tables.table(t.getkeyword('ANTENNA'))
    N_ant = len(t_ant)

# Number of baselines including zero length (autocorrelation) baselines 

    N_baselines = (N_ant * (N_ant + 1)) / 2

    chunksize = 100


    for target in targets:
   
        msname1 = basename % target

        ra1, dec1 = targetdirs[target]


        t.copy(msname1)
        t1 = pyrap.tables.table(msname1, readonly = False)

        t_field1 = pyrap.tables.table(t1.getkeyword('FIELD'), readonly = False)
        t_field1.putcol('PHASE_DIR', numpy.array([[[ra1, dec1]]]))
        t_field1.putcol('REFERENCE_DIR', numpy.array([[[ra1, dec1]]]))
        t_field1.putcol('DELAY_DIR', numpy.array([[[ra1, dec1]]]))

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

        x1 = numpy.sin(ra1)*numpy.cos(dec1)
        y1 = numpy.cos(ra1)*numpy.cos(dec1)
        z1 = numpy.sin(dec1)
        w1 = numpy.array([[x1,y1,z1]]).T

        x1 = -numpy.sin(ra1)*numpy.sin(dec1)
        y1 = -numpy.cos(ra1)*numpy.sin(dec1)
        z1 = numpy.cos(dec1)
        v1 = numpy.array([[x1,y1,z1]]).T

        x1 = numpy.cos(ra1)
        y1 = -numpy.sin(ra1)
        z1 = 0
        u1 = numpy.array([[x1,y1,z1]]).T

        T1 = numpy.concatenate([u1,v1,w1], axis = -1 )
        TT = numpy.dot(T1.T, T)

        N_cell_per_chunk_in_freq = N_channel / N_channel_per_cell
        N_cell_per_chunk_in_time = chunksize / N_time_per_cell


        for pos in range(0, len(t), chunksize * N_baselines) :
            time_start = time.time()
            uvw = t.getcol('UVW', pos, chunksize * N_baselines)
            data = t.getcol('DATA', pos, chunksize * N_baselines)
            f = numpy.dot(numpy.dot((w-w1).T, T) , uvw.T)
            f = numpy.exp(numpy.dot(1.0 / wavelength.reshape(-1,1) * 2 * numpy.pi * 1j, f))
            uvw1 = numpy.dot(uvw, TT.T)
            data1 = data * numpy.resize(f, data.shape[::-1]).T
            t1.putcol('UVW', uvw1, pos, uvw1.shape[0])
            t1.putcol('DATA', data1, pos, data1.shape[0])
            time_stop = time.time()
            #print time_stop - time_start
            #sys.stdout.flush()
      
        t1.close()
    t.close()
    t_field1.close()
