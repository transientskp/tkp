import pyrap.tables as pt
import pyrap.quanta as qa
import pyrap.measures as pm
from numpy import pi

"""
Provides getAteamList, a function that returns a comma-separated list of the Ateam sources that have to be demixed.

Inputs:
* MSname (the measurement set name)
* innerDistance is the minimum distance (degrees) between the target and an Ateam source. It is frequency dependent, see refFreq
* outerDistance is the maximum distance (degrees) between the target and an Ateam source. It will be multiplied by 2 for CasA and CygA, because they are brighter than the others. It is also frequency dependent, see refFreq
* refFreq is the frequency in MHz that the innerDistance and outerDistance will be scaled relative to
* elLimit is the elevation limit in degrees
* verbose, if enabled, will print out separation and elevation information

v0.1, 1 July 2011 by G. Heald
based on some code from ~weeren/scripts/plot_Ateam_elevation.py
"""

def getAteamList(MSname, innerDistance=21., outerDistance=35.,refFreq=58.,elLimit=20.,verbose=False):
        
        # Here are the Ateam sources to check, with RA,Dec in rad
        targets = [ {'name' : 'CasA', 'ra' : 6.123487680622104,  'dec' : 1.0265153995604648},
            {'name' : 'CygA', 'ra' : 5.233686575770755,  'dec' : 0.7109409582180791},
            {'name' : 'TauA', 'ra' : 1.4596748493730913, 'dec' : 0.38422502335921294},
            #{'name' : 'HerA', 'ra' : 4.4119087330382163, 'dec' : 0.087135562905816893},
            {'name' : 'VirA', 'ra' : 3.276086511413598,  'dec' : 0.21626589533567378}]#,
            #{'name' : 'HydA', 'ra' : 2.4351466,        'dec' : -0.21110706},
            #{'name' : 'PerA', 'ra' : 0.87180363,         'dec' : 0.72451580},
            #{'name' : 'SUN'},
            #{'name' : 'JUPITER'}]

        # Need a measure object
        me = pm.measures()

        # Open the ms and get the reference time and frequency
        ms = pt.table(MSname,ack=False)
        refTime = ms.getcell('TIME',0)
        freq_table = pt.table(ms.getkeyword('SPECTRAL_WINDOW'),ack=False)
        msFreq = freq_table.getcell('REF_FREQUENCY',0)

        # correct the inner and outer distances for frequency
        freqFactor = (refFreq*1.e6)/msFreq
        innerDistance *= freqFactor
        outerDistance *= freqFactor
        if verbose:
                print 'At frequency %f MHz:'%(msFreq/1.e6)
                print 'Frequency-corrected inner radius: %f'%innerDistance
                print 'Frequency-corrected outer radius: %f'%outerDistance
                print '  (or %f for CasA,CygA)'%(outerDistance*2.)
                print ''
        
        # Get location of the first station
        ant_table = pt.table(ms.getkeyword('ANTENNA'),ack=False)
        ant_no = 0
        pos = ant_table.getcol('POSITION')
        x = qa.quantity( pos[ant_no,0], 'm' )
        y = qa.quantity( pos[ant_no,1], 'm' )
        z = qa.quantity( pos[ant_no,2], 'm' )
        position =  me.position( 'wgs84', x, y, z )
        me.doframe(position)
        #print position
        ant_table.close()

        # Get pointing direction of the MS
        field_table = pt.table(ms.getkeyword('FIELD'),ack=False)
        field_no = 0
        direction = field_table.getcol('PHASE_DIR')
        ra = direction[ ant_no, field_no, 0 ]
        dec = direction[ ant_no, field_no, 1 ]
        targets.insert(0, {'name' : 'Pointing', 'ra' : ra, 'dec' : dec})
        field_table.close()

        # set up the target pointing direction
        ra_qa  = qa.quantity( targets[0]['ra'], 'rad' )
        dec_qa = qa.quantity( targets[0]['dec'], 'rad' )
        pointing =  me.direction('j2000', ra_qa, dec_qa)

        # this will be the list of sources to demix
        aTeamList = []

        # For each source, we have to calculate
        # a) distance to target field
        # b) elevation
        for target in targets[1:]:
                t = qa.quantity(refTime,'s')
                t1 = me.epoch('utc',t)
                me.doframe(t1)

                # calculate the sun and jupiter positions specially
                if 'ra' in target.keys():
                        ra_qa  = qa.quantity( target['ra'], 'rad' )
                        dec_qa = qa.quantity( target['dec'], 'rad' )
                        direction =  me.direction('j2000', ra_qa, dec_qa)
                else :
                        direction =  me.direction(target['name'])
                
                # Now the separation between the target and the Ateam source
                aTeamDistance = me.separation(pointing,direction).get_value()

                # Now the elevation of the Ateam source at the reference time
                a = me.measure(direction, 'azel')
                elevation = a['m1']
                elDeg = elevation['value']/pi*180.

                # print if verbose
                if verbose:
                        print 'Source: %s' % target['name']
                        print 'Separation: %f' % aTeamDistance
                        print 'Elevation: %f' % elDeg
                
                # Does it need to be demixed?
                if target['name'] == 'CygA' or target['name'] == 'CasA':
                        odFact = 2.
                else:
                        odFact = 1.
                if aTeamDistance > innerDistance and aTeamDistance < outerDistance*odFact and elDeg > elLimit:
                        aTeamList.append(target['name'])
                        if verbose: print 'DEMIX\n'
                elif verbose: print 'DO NOT DEMIX\n'

        return aTeamList

