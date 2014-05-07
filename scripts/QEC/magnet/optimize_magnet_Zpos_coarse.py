"""
Script for coarse optimization of the magnet Z-position (using the ms=+1 resonance).
Coarse optimization starts with a large range scan and then zooms in
Important: choose the right domain for the range of positions in get_magnet_position in magnet tools!
"""
import numpy as np
import qt
import msvcrt
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt

# import the dESR fit, magnet tools and master of magnet
from analysis.lib.fitting import dark_esr_auto_analysis; reload(dark_esr_auto_analysis)
from measurement.lib.tools import magnet_tools as mt; reload(mt)
mom = qt.instruments['master_of_magnet']; reload(mt)

execfile(qt.reload_current_setup)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']
nm_per_step = qt.exp_params['magnet']['nm_per_step']
current_f_msp1 = qt.exp_params['samples'][SAMPLE]['ms+1_cntr_frq']

def darkesr(name, range_MHz, pts, reps):

    m = pulsar_msmt.DarkESR(name)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])

    m.params['mw_frq'] = m.params['ms+1_cntr_frq']-43e6 #MW source frequency
    #m.params['mw_frq'] = 2*m.params['zero_field_splitting'] - m.params['ms-1_cntr_frq'] -43e6

    m.params['mw_power'] = 20
    m.params['repetitions'] = reps

    m.params['ssbmod_frq_start'] = 43e6 - range_MHz*1e6 ## first time we choose a quite large domain to find the three dips (15)
    m.params['ssbmod_frq_stop'] = 43e6 + range_MHz*1e6
    m.params['pts'] = pts
    m.params['pulse_length'] = 2e-6
    m.params['ssbmod_amplitude'] = 0.03

    m.autoconfig()
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()

######################
### Run experiment ###
######################

if __name__ == '__main__':

    ######################
    ## Input parameters ##
    ######################
    maximum_magnet_step_size = 250
    opimization_target = 5     # target difference in kHz (or when 0 magnet steps are required)

        ### for the first coarse step
    init_range   = 4.5     #Common: 10 MHz
    init_pts     = 91    #Common: 121
    init_reps    = 750   #Common: 500
        ### for the remainder of the steps
    repeat_range = 4.5
    repeat_pts   = 81
    repeat_reps  = 1000

    ###########
    ## Start ##
    ###########
    
    #create the data lists
    d_steps = []; f0 = []; u_f0 = []; delta_f0 =[];iterations_list =[]
  
     #turn on magnet stepping in Z
    mom.set_mode('Z_axis', 'stp')

    # start: define B-field and position by first ESR measurement
    darkesr('magnet_Zpos_optimize_coarse', range_MHz=init_range, pts=init_pts, reps=init_reps)
    # do the fitting, returns in MHz, input in GHz
    f0_temp, u_f0_temp = dark_esr_auto_analysis.analyze_dark_esr(current_f_msp1*1e-9, qt.exp_params['samples'][SAMPLE]['N_HF_frq']*1e-9)
    delta_f0_temp = f0_temp*1e6-current_f_msp1*1e-3

    # start to list all the measured values
    iterations = 0
    f0.append(f0_temp)
    u_f0.append(u_f0_temp)
    delta_f0.append(delta_f0_temp)

    print 'Measured frequency = ' + str(f0_temp) + ' GHz +/- ' + str(u_f0_temp*1e6) + ' kHz'
    print 'Difference = ' + str(delta_f0_temp) + ' kHz'
    
    while abs(delta_f0_temp) > opimization_target:
        d_steps.append(int(round(mt.steps_to_frequency(freq=f0_temp*1e9,freq_id=current_f_msp1, ms = 'plus'))))
        print 'move magnet in Z with '+ str(d_steps[iterations]) + ' steps'

        if abs(d_steps[iterations]) > maximum_magnet_step_size:
            print 'd_steps>+/-00, step only 250 steps!'
            if d_steps[iterations] > 0:
                mom.step('Z_axis',maximum_magnet_step_size)
                d_steps[iterations] = maximum_magnet_step_size
            if d_steps[iterations] < 0:
                mom.step('Z_axis',-1*maximum_magnet_step_size)
                d_steps[iterations] = -1*maximum_magnet_step_size
        elif d_steps[iterations]==0:
            print 'Steps = 0 optimization converted'
            break
        else:
            mom.step('Z_axis',d_steps[iterations])

        qt.msleep(1)
        stools.turn_off_all_lt2_lasers()
        GreenAOM.set_power(5e-6)
        optimiz0r.optimize(dims=['x','y','z'])
        
        
        darkesr(SAMPLE_CFG, range_MHz=repeat_range, pts=repeat_pts, reps=repeat_reps)
        
        #Determine frequency and B-field --> this fit programme returns in MHz, needs input GHz
        f0_temp,u_f0_temp = dark_esr_auto_analysis.analyze_dark_esr(current_f_msp1*1e-9,qt.exp_params['samples'][SAMPLE]['N_HF_frq']*1e-9 )
        delta_f0_temp = f0_temp*1e6-current_f_msp1*1e-3

        f0.append(f0_temp)
        u_f0.append(u_f0_temp)
        delta_f0.append(delta_f0_temp)
        iterations_list.append(iterations)
        
        print 'Measured frequency = ' + str(f0_temp) + ' GHz +/- ' + str(u_f0_temp*1e6) + ' kHz'
        print 'Difference = ' + str(abs(f0_temp*1e6-current_f_msp1*1e-3)) + ' kHz'
    
        # To cleanly exit the optimization
        print '--------------------------------'
        print 'press q to stop measurement loop'
        print '--------------------------------'
        qt.msleep(2)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')) or d_steps[iterations]==abs(1):
            break

        iterations += 1

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
    d.add_data_point(iterations_list, f0,u_f0,delta_f0,d_steps)
    d.close_file()

    print 'Z position coarse optimization finished, stepped the magnet '+ str(total_d_steps) + ' in '+str(iterations+1) +' iterations'


