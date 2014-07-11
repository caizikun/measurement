"""
Script for fine optimization of the magnet Z-position (using the ms=+1 resonance).
Fine optimization measures only the center resonance
Important: choose the right domain for the range of positions in get_magnet_position in magnet tools!
"""

import numpy as np
import qt
import msvcrt
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt

# import the DESR measurement, DESR fit, magnet tools and master of magnet
from measurement.scripts.QEC.magnet import DESR_msmt; reload(DESR_msmt)
from analysis.lib.fitting import dark_esr_auto_analysis; reload(dark_esr_auto_analysis)
from measurement.lib.tools import magnet_tools as mt; reload(mt)
mom = qt.instruments['master_of_magnet']; reload(mt)

execfile(qt.reload_current_setup)


nm_per_step = qt.exp_params['magnet']['nm_per_step']
current_f_msp1 = qt.exp_params['samples'][SAMPLE]['ms+1_cntr_frq']

if __name__ == '__main__':

    ######################
    ## Input parameters ##
    ######################
    safemode = False
    maximum_magnet_step_size = 250
    opimization_target = 5     # target difference in kHz (or when 0 magnet steps are required)

    DESR_range = 5       # MHz (ful range = 2*DESR_range)
    pts   = 121
    reps  = 1000

    ###########
    ## Start ##
    ###########
    
    #create the data lists
    d_steps = []; f0 = []; u_f0 = []; delta_f0 =[];
    #turn on magnet stepping in Z
    mom.set_mode('Z_axis', 'stp')

    # start: define B-field and position by first ESR measurement
    DESR_msmt.darkesr('magnet_Zpos_optimize_fine', ms = 'msp', 
            range_MHz=DESR_range, pts=pts, reps=reps)
    # do the fitting, returns in MHz, input in GHz
    f0_temp, u_f0_temp = dark_esr_auto_analysis.analyze_dark_esr(current_f_msp1*1e-9, 
            qt.exp_params['samples'][SAMPLE]['N_HF_frq']*1e-9)
    delta_f0_temp = f0_temp*1e6-current_f_msp1*1e-3

    # start to list all the measured values
    iterations = 0
    f0.append(f0_temp)
    u_f0.append(u_f0_temp)
    delta_f0.append(delta_f0_temp)

    print 'Measured frequency = ' + str(f0_temp) + ' GHz +/- ' + str(u_f0_temp*1e6) + ' kHz'
    print 'Difference = ' + str(delta_f0_temp) + ' kHz'
    
    while abs(delta_f0_temp) > opimization_target:
        
        # To cleanly exit the optimization
        print '--------------------------------'
        print 'press q to stop measurement loop'
        print '--------------------------------'
        qt.msleep(2)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            break


        d_steps.append(int(round(mt.steps_to_frequency(freq=f0_temp*1e9,
                freq_id=current_f_msp1, ms = 'plus'))))
        print 'move magnet in Z with '+ str(d_steps[iterations]) + ' steps'

        if abs(d_steps[iterations]) > maximum_magnet_step_size:
            print 'd_steps>+/-00, step only 250 steps!'
            if d_steps[iterations] > 0:
                d_steps[iterations] = maximum_magnet_step_size
            if d_steps[iterations] < 0:
                d_steps[iterations] = -1*maximum_magnet_step_size
        elif d_steps[iterations]==0:
            print 'Steps = 0 optimization converted'
            break
        if safemode == True: 
            ri = raw_input ('move magnet? (y/n)')
            if str(ri) == 'y': 
                mom.step('Z_axis',d_steps[iterations])
            else :
                break 
        else: 
            mom.step('Z_axis',d_steps[iterations])

        qt.msleep(1)
        stools.turn_off_all_lt2_lasers()
        GreenAOM.set_power(5e-6)
        optimiz0r.optimize(dims=['x','y','z'])
        iterations += 1
        
        DESR_msmt.darkesr('magnet_Zpos_optimize_fine', ms = 'msp', 
                range_MHz=DESR_range, pts=pts, reps=reps)
        #do the fitting, returns in MHz, input in GHz
        f0_temp, u_f0_temp = dark_esr_auto_analysis.analyze_dark_esr(current_f_msp1*1e-9, 
                qt.exp_params['samples'][SAMPLE]['N_HF_frq']*1e-9,min_dip_depth = 0.85)
        delta_f0_temp = f0_temp*1e6-current_f_msp1*1e-3

        f0.append(f0_temp)
        u_f0.append(u_f0_temp)
        delta_f0.append(delta_f0_temp)
        
        print 'Measured frequency = ' + str(f0_temp) + ' GHz +/- ' + str(u_f0_temp*1e6) + ' kHz'
        print 'Difference = ' + str(abs(f0_temp*1e6-current_f_msp1*1e-3)) + ' kHz'
    


    total_d_steps = np.sum(d_steps)

    #create a file to save data to --> what is a good way to save this?
    d = qt.Data(name='magnet_coarseZ_optimization_overview')
    d.add_coordinate('iteration')
    d.add_value('frequency [GHz]')
    d.add_value('frequency error [GHz]')
    d.add_value('frequency difference [GHz]')
    d.add_value('number of steps')
    d.create_file()
    filename=d.get_filepath()[:-4]
    d.add_data_point(iterations, f0,u_f0,delta_f0,d_steps)
    d.close_file()

    print 'Z position coarse optimization finished, stepped the magnet '+ str(total_d_steps) + ' in '+str(iterations) +' iterations'


