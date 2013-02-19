import os
import lofar.parmdb
import numpy as numpy
import lofar.expion.parmdbmain
import median_filter

def smoothparmdb(instrument_name,instrument_name_smoothed, half_window, threshold):
    print 'Smoothing with ', instrument_name, instrument_name_smoothed, half_window, threshold
    #print input_parmdb, output_parmdb
    #msname = 'L23145_SB030_TauA_avg_dem.MS'
    
    #instrument_name = input_parmdb # msname + '/' + 'instrument'
    #instrument_name_smoothed = output_parmdb  #
    
    #calibrate --key pCasA --clean --skip-sky-db --skip-instrument-db --instrument-name instrument_smoothed --cluster-desc ~/full.clusterdesc --db ldb001 --db-user postgres L23145_SB030_CasA_avg_dem.MS.gds bbs_CasA_smoothcal.parset ~/scripts/Ateam_LBA.skymodel $PWD
    # and L23145_SB030_CasA_avg_dem.MS/instrument_smoothed
    
    
    
    #half_window = 20
    #threshold   = 2.0
    
    
    pdb = lofar.parmdb.parmdb(instrument_name)
    parms = pdb.getValuesGrid("*")
    #print parms.keys()
    key_names = parms.keys()
    antenna_list = numpy.copy(key_names)
    pol_list = numpy.copy(key_names)
    sol_par  = numpy.copy(key_names)
    #print len(key_names)
    
    
    
    # create the antenna+polarizations list
    for ii in range(len(key_names)):
        #print 'ii', ii
        string_a = str(key_names[ii])
    
        split_a  = string_a.split( ":" )
        #print split_a[4]
        antenna_list[ii] = split_a[4]
        pol_list[ii]     = split_a[1] + ':' + split_a[2]
        sol_par[ii]      = split_a[3]
        gain             = split_a[0]
        #print antenna_list[ii] 
    
    antenna_list = numpy.unique(antenna_list)
    pol_list     = numpy.unique(pol_list)
    sol_par      =  numpy.unique(sol_par)
    print 'Stations available:', antenna_list
    print 'Polarizations:', pol_list, sol_par, gain
    
    
    
    
    if len(pol_list) == 4:
    
      for antenna in antenna_list:
          print 'smoothing (N_pol=4):', antenna
          real_val00 = parms[gain + ':0:0:Real:' + antenna]['values'][::]
          imag_val00 = parms[gain + ':0:0:Imag:' + antenna]['values'][::]
          ampl00   = numpy.sqrt(real_val00**2 + imag_val00**2)
          real_val01 = parms[gain + ':0:1:Real:' + antenna]['values'][::]
          imag_val01 = parms[gain + ':0:1:Imag:' + antenna]['values'][::]
          ampl01   = numpy.sqrt(real_val01**2 + imag_val01**2)
          real_val10 = parms[gain + ':1:0:Real:' + antenna]['values'][::]
          imag_val10 = parms[gain + ':1:0:Imag:' + antenna]['values'][::]
          ampl10   = numpy.sqrt(real_val10**2 + imag_val10**2)
          real_val11 = parms[gain + ':1:1:Real:' + antenna]['values'][::]
          imag_val11 = parms[gain + ':1:1:Imag:' + antenna]['values'][::]
          ampl11   = numpy.sqrt(real_val11**2 + imag_val11**2)
    
          #filter, medina smooth amplitudes 
          #ampl11_smoothed = (median_filter.median_filter(ampl11.squeeze(), half_window, threshold))
          #ampl11_smoothed = ampl11_smoothed.reshape(len(ampl11_smoothed),1)

          #ampl00_smoothed = (median_filter.median_filter(ampl00.squeeze(), half_window, threshold))
          #ampl00_smoothed = ampl00_smoothed.reshape(len(ampl00_smoothed),1)

          #ampl10_smoothed = (median_filter.median_filter(ampl10.squeeze(), half_window, threshold))
          #ampl10_smoothed = ampl10_smoothed.reshape(len(ampl10_smoothed),1)

          #ampl01_smoothed = (median_filter.median_filter(ampl01.squeeze(), half_window, threshold))
          #ampl01_smoothed = ampl01_smoothed.reshape(len(ampl01_smoothed),1)

          #filter, smooth amplitudes 
          ampl11_smoothed = (median_filter.my_solflag(ampl11.squeeze(), half_window, 5.0))
          ampl11_smoothed = ampl11_smoothed.reshape(len(ampl11_smoothed),1)
          ampl11_smoothed = (median_filter.my_solflag_inv(ampl11_smoothed.squeeze(), half_window, 5.0))
          ampl11_smoothed = ampl11_smoothed.reshape(len(ampl11_smoothed),1)
          # second pass
          ampl11_smoothed = (median_filter.my_solflag(ampl11_smoothed.squeeze(), 5, 2.0))
          ampl11_smoothed = ampl11_smoothed.reshape(len(ampl11_smoothed),1)
          ampl11_smoothed = (median_filter.my_solflag_inv(ampl11_smoothed.squeeze(), 5, 2.0))
          ampl11_smoothed = ampl11_smoothed.reshape(len(ampl11_smoothed),1)
          # third pass
          ampl11_smoothed = (median_filter.my_solflag(ampl11_smoothed.squeeze(), half_window, threshold))
          ampl11_smoothed = ampl11_smoothed.reshape(len(ampl11_smoothed),1)
          ampl11_smoothed = (median_filter.my_solflag_inv(ampl11_smoothed.squeeze(), half_window, threshold))
          ampl11_smoothed = ampl11_smoothed.reshape(len(ampl11_smoothed),1)
          # ---------------------------------------------------------------
        
          ampl00_smoothed = (median_filter.my_solflag(ampl00.squeeze(), half_window, 5.0))
          ampl00_smoothed = ampl00_smoothed.reshape(len(ampl00_smoothed),1)
          ampl00_smoothed = (median_filter.my_solflag_inv(ampl00_smoothed.squeeze(), half_window, 5.0))
          ampl00_smoothed = ampl00_smoothed.reshape(len(ampl00_smoothed),1)
          # second pass
          ampl00_smoothed = (median_filter.my_solflag(ampl00_smoothed.squeeze(), 5, 2.0))
          ampl00_smoothed = ampl00_smoothed.reshape(len(ampl00_smoothed),1)
          ampl00_smoothed = (median_filter.my_solflag_inv(ampl00_smoothed.squeeze(), 5, 2.0))
          ampl00_smoothed = ampl00_smoothed.reshape(len(ampl00_smoothed),1)
          # third pass
          ampl00_smoothed = (median_filter.my_solflag(ampl00_smoothed.squeeze(), half_window, threshold))
          ampl00_smoothed = ampl00_smoothed.reshape(len(ampl00_smoothed),1)
          ampl00_smoothed = (median_filter.my_solflag_inv(ampl00_smoothed.squeeze(), half_window, threshold))
          ampl00_smoothed = ampl00_smoothed.reshape(len(ampl00_smoothed),1)
          # ---------------------------------------------------------------
        
          ampl10_smoothed = (median_filter.my_solflag(ampl10.squeeze(), half_window*2, 4.0))
          ampl10_smoothed = ampl10_smoothed.reshape(len(ampl10_smoothed),1)
          ampl10_smoothed = (median_filter.my_solflag_inv(ampl10_smoothed.squeeze(), half_window*2, 4.0))
          ampl10_smoothed = ampl10_smoothed.reshape(len(ampl10_smoothed),1)
          # second pass
          ampl10_smoothed = (median_filter.my_solflag(ampl10_smoothed.squeeze(), 5, 2.0))
          ampl10_smoothed = ampl10_smoothed.reshape(len(ampl10_smoothed),1)
          ampl10_smoothed = (median_filter.my_solflag_inv(ampl10_smoothed.squeeze(), 5, 2.0))
          ampl10_smoothed = ampl10_smoothed.reshape(len(ampl10_smoothed),1)
          # third pass
          ampl10_smoothed = (median_filter.my_solflag(ampl10_smoothed.squeeze(), half_window, threshold))
          ampl10_smoothed = ampl10_smoothed.reshape(len(ampl10_smoothed),1)
          ampl10_smoothed = (median_filter.my_solflag_inv(ampl10_smoothed.squeeze(), half_window, threshold))
          ampl10_smoothed = ampl10_smoothed.reshape(len(ampl10_smoothed),1)      
          # ---------------------------------------------------------------
        
          ampl01_smoothed = (median_filter.my_solflag(ampl01.squeeze(), half_window*2, 4.0))
          ampl01_smoothed = ampl01_smoothed.reshape(len(ampl01_smoothed),1)
          ampl01_smoothed = (median_filter.my_solflag_inv(ampl01_smoothed.squeeze(), half_window*2, 4.0))
          ampl01_smoothed = ampl01_smoothed.reshape(len(ampl01_smoothed),1)
          #second pass
          ampl01_smoothed = (median_filter.my_solflag(ampl01_smoothed.squeeze(), 5, 2.0))
          ampl01_smoothed = ampl01_smoothed.reshape(len(ampl01_smoothed),1)
          ampl01_smoothed = (median_filter.my_solflag_inv(ampl01_smoothed.squeeze(), 5, 2.0))
          ampl01_smoothed = ampl01_smoothed.reshape(len(ampl01_smoothed),1)      
          # third pass      
          ampl01_smoothed = (median_filter.my_solflag(ampl01_smoothed.squeeze(), half_window, threshold))
          ampl01_smoothed = ampl01_smoothed.reshape(len(ampl01_smoothed),1)
          ampl01_smoothed = (median_filter.my_solflag_inv(ampl01_smoothed.squeeze(), half_window, threshold))
          ampl01_smoothed = ampl01_smoothed.reshape(len(ampl01_smoothed),1)            
          # ---------------------------------------------------------------

          factor11 = ampl11_smoothed/ampl11
          factor10 = ampl10_smoothed/ampl10
          factor01 = ampl01_smoothed/ampl01
          factor00 = ampl00_smoothed/ampl00
          factor11[~numpy.isfinite(factor11)] = 0.
          factor10[~numpy.isfinite(factor10)] = 0.
          factor01[~numpy.isfinite(factor01)] = 0.
          factor00[~numpy.isfinite(factor00)] = 0.
        
          parms['Gain:1:1:Imag:' + antenna]['values'][::] = parms['Gain:1:1:Imag:' + antenna]['values'][::]*factor11
          parms['Gain:1:1:Real:' + antenna]['values'][::] = parms['Gain:1:1:Real:' + antenna]['values'][::]*factor11
          parms['Gain:0:0:Imag:' + antenna]['values'][::] = parms['Gain:0:0:Imag:' + antenna]['values'][::]*factor00
          parms['Gain:0:0:Real:' + antenna]['values'][::] = parms['Gain:0:0:Real:' + antenna]['values'][::]*factor00
          parms['Gain:1:0:Imag:' + antenna]['values'][::] = parms['Gain:1:0:Imag:' + antenna]['values'][::]*factor10
          parms['Gain:1:0:Real:' + antenna]['values'][::] = parms['Gain:1:0:Real:' + antenna]['values'][::]*factor10
          parms['Gain:0:1:Imag:' + antenna]['values'][::] = parms['Gain:0:1:Imag:' + antenna]['values'][::]*factor01
          parms['Gain:0:1:Real:' + antenna]['values'][::] = parms['Gain:0:1:Real:' + antenna]['values'][::]*factor01
    
    if len(pol_list) == 2:
      for antenna in antenna_list:
          print 'smoothing (N_pol=2):', antenna
          real_val00 = parms[gain + ':0:0:Real:' + antenna]['values'][::]
          imag_val00 = parms[gain + ':0:0:Imag:' + antenna]['values'][::]
          ampl00   = numpy.sqrt(real_val00**2 + imag_val00**2)
    
          real_val11 = parms[gain + ':1:1:Real:' + antenna]['values'][::]
          imag_val11 = parms[gain + ':1:1:Imag:' + antenna]['values'][::]
          ampl11   = numpy.sqrt(real_val11**2 + imag_val11**2)
    
                    #filter, medina smooth amplitudes 
          #ampl11_smoothed = (median_filter.median_filter(ampl11.squeeze(), half_window, threshold))
          #ampl11_smoothed = ampl11_smoothed.reshape(len(ampl11_smoothed),1)

          #ampl00_smoothed = (median_filter.median_filter(ampl00.squeeze(), half_window, threshold))
          #ampl00_smoothed = ampl00_smoothed.reshape(len(ampl00_smoothed),1)

          #filter, smooth amplitudes 
          ampl11_smoothed = (median_filter.my_solflag(ampl11.squeeze(), half_window, 5.0))
          ampl11_smoothed = ampl11_smoothed.reshape(len(ampl11_smoothed),1)
          ampl11_smoothed = (median_filter.my_solflag_inv(ampl11_smoothed.squeeze(), half_window, 5.0))
          ampl11_smoothed = ampl11_smoothed.reshape(len(ampl11_smoothed),1)
          # second pass
          ampl11_smoothed = (median_filter.my_solflag(ampl11_smoothed.squeeze(), 5, 2.0))
          ampl11_smoothed = ampl11_smoothed.reshape(len(ampl11_smoothed),1)
          ampl11_smoothed = (median_filter.my_solflag_inv(ampl11_smoothed.squeeze(), 5, 2.0))
          ampl11_smoothed = ampl11_smoothed.reshape(len(ampl11_smoothed),1)
          # third pass
          ampl11_smoothed = (median_filter.my_solflag(ampl11_smoothed.squeeze(), half_window, threshold))
          ampl11_smoothed = ampl11_smoothed.reshape(len(ampl11_smoothed),1)
          ampl11_smoothed = (median_filter.my_solflag_inv(ampl11_smoothed.squeeze(), half_window, threshold))
          ampl11_smoothed = ampl11_smoothed.reshape(len(ampl11_smoothed),1)
          # ---------------------------------------------------------------

          ampl00_smoothed = (median_filter.my_solflag(ampl00.squeeze(), half_window, 5.0))
          ampl00_smoothed = ampl00_smoothed.reshape(len(ampl00_smoothed),1)
          ampl00_smoothed = (median_filter.my_solflag_inv(ampl00_smoothed.squeeze(), half_window, 5.0))
          ampl00_smoothed = ampl00_smoothed.reshape(len(ampl00_smoothed),1)
          # second pass
          ampl00_smoothed = (median_filter.my_solflag(ampl00_smoothed.squeeze(), 5, 2.0))
          ampl00_smoothed = ampl00_smoothed.reshape(len(ampl00_smoothed),1)
          ampl00_smoothed = (median_filter.my_solflag_inv(ampl00_smoothed.squeeze(), 5, 2.0))
          ampl00_smoothed = ampl00_smoothed.reshape(len(ampl00_smoothed),1)
          # third pass
          ampl00_smoothed = (median_filter.my_solflag(ampl00_smoothed.squeeze(), half_window, threshold))
          ampl00_smoothed = ampl00_smoothed.reshape(len(ampl00_smoothed),1)
          ampl00_smoothed = (median_filter.my_solflag_inv(ampl00_smoothed.squeeze(), half_window, threshold))
          ampl00_smoothed = ampl00_smoothed.reshape(len(ampl00_smoothed),1)
          # ---------------------------------------------------------------


          factor11 = ampl11_smoothed/ampl11
          factor00 = ampl00_smoothed/ampl00
          factor11[~numpy.isfinite(factor11)] = 0.
          factor00[~numpy.isfinite(factor00)] = 0.

          parms['Gain:1:1:Imag:' + antenna]['values'][::] = parms['Gain:1:1:Imag:' + antenna]['values'][::]*factor11
          parms['Gain:1:1:Real:' + antenna]['values'][::] = parms['Gain:1:1:Real:' + antenna]['values'][::]*factor11
          parms['Gain:0:0:Imag:' + antenna]['values'][::] = parms['Gain:0:0:Imag:' + antenna]['values'][::]*factor00
          parms['Gain:0:0:Real:' + antenna]['values'][::] = parms['Gain:0:0:Real:' + antenna]['values'][::]*factor00
    
    print 'writing the new database:', instrument_name_smoothed
    print 'check your results with: parmdbplot.py' , instrument_name_smoothed
    print 'compare with: parmdbplot.py', instrument_name

    lofar.expion.parmdbmain.store_parms(instrument_name_smoothed, parms, create_new = True)











