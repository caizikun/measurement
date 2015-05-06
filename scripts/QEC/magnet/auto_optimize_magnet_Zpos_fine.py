"""
Script for coarse optimization of the magnet Z-position (using the ms=+1 resonance).
Coarse optimization starts with a large range scan and then zooms in
Important: choose the right domain for the range of positions in get_magnet_position in magnet tools!
"""
import numpy as np
import qt
import msvcrt
from analysis.lib.fitting import fit, common; reload(common)
from matplotlib import pyplot as plt
from analysis.lib.tools import toolbox

# import the DESR measurement, DESR fit, magnet tools and master of magnet
from measurement.scripts.QEC.magnet import DESR_msmt; reload(DESR_msmt)
from analysis.lib.fitting import dark_esr_auto_analysis; reload(dark_esr_auto_analysis)
from measurement.lib.tools import magnet_tools as mt; reload(mt)
mom = qt.instruments['master_of_magnet']; reload(mt)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']
nm_per_step = qt.exp_params['magnet']['nm_per_step']
f0_temp = qt.exp_params['samples'][SAMPLE]['ms-1_cntr_frq']*1e-9
f0p_temp = qt.exp_params['samples'][SAMPLE]['ms+1_cntr_frq']*1e-9
current_f_msm1 = qt.exp_params['samples'][SAMPLE]['ms-1_cntr_frq']

######################
### Run experiment ###
######################

def auto_z_magnet_optimize():

    ######################
    ## Input parameters ##
    ######################
    safemode=False
    maximum_magnet_step_size = 50
    opimization_target = 10     # target difference in kHz (or when 0 magnet steps are required)


    ### for the remainder of the steps
    range_fine = 0.4
    pts_fine   = 51
    reps_fine  = 100

    ###########
    ## Start ##
    ###########
    
    #create the data lists
    d_steps = [0]; f0 = [0]; u_f0 = [0]; delta_f0 =[0];iterations_list =[0]
  
     #turn on magnet stepping in Z
    mom.set_mode('Z_axis', 'stp')

    # start: define B-field and position by first ESR measurement
    DESR_msmt.darkesr('magnet_' + 'Z_axis_' + 'msm1', ms = 'msm', 
            range_MHz=range_fine, pts=pts_fine, reps=reps_fine, freq=f0_temp*1e9,# - N_hyperfine,
            pulse_length = 8e-6, ssbmod_amplitude = 0.0025)
    f0_temp, u_f0_temp = dark_esr_auto_analysis.analyze_dark_esr_double(do_ROC = False,do_plot = False)
    f0_temp = f0_temp# + N_hyperfine*1e-9
    delta_f0_temp = f0_temp*1e6-current_f_msm1*1e-3

    # start to list all the measured values
    iterations = 0
    iterations_list.append(iterations)
    f0.append(f0_temp)
    u_f0.append(u_f0_temp)
    delta_f0.append(delta_f0_temp)
    d_steps.append(int(round(mt.steps_to_frequency(freq=f0_temp*1e9,
            freq_id=current_f_msm1, ms = 'plus'))))

    print 'Measured frequency = ' + str(f0_temp) + ' GHz +/- ' + str(u_f0_temp*1e6) + ' kHz'
    print 'Difference = ' + str(delta_f0_temp) + ' kHz'
    
    while abs(delta_f0_temp) > opimization_target:
        iterations += 1
        print 'move magnet in Z with '+ str(d_steps[iterations]) + ' steps'

        if abs(d_steps[iterations]) > maximum_magnet_step_size:
            print 'd_steps>+/-00, step only 50 steps!'
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
 
        
        DESR_msmt.darkesr('fine_optimize_magnet_' + 'Z_axis_' + 'msm1', ms = 'msm', 
                range_MHz=range_fine, pts=pts_fine, reps=reps_fine, freq=f0_temp*1e9,# - N_hyperfine,
                pulse_length = 8e-6, ssbmod_amplitude = 0.0025)
        
        f0_temp, u_f0_temp, folder = dark_esr_auto_analysis.analyze_dark_esr_double(do_ROC = False,ret_folder = True,do_plot = False)
        f0_temp = f0_temp# + N_hyperfine*1e-9
        delta_f0_temp = f0_temp*1e6-current_f_msm1*1e-3

        d_steps.append(int(round(mt.steps_to_frequency(freq=f0_temp*1e9,
                freq_id=current_f_msm1, ms = 'plus'))))

        f0.append(f0_temp)
        u_f0.append(u_f0_temp)
        delta_f0.append(delta_f0_temp)
        
        print 'Measured frequency = ' + str(f0_temp) + ' GHz +/- ' + str(u_f0_temp*1e6) + ' kHz'
        print 'Difference = ' + str(f0_temp*1e6-current_f_msm1*1e-3) + ' kHz'
    
        iterations_list.append(iterations)




    total_d_steps = np.sum(d_steps)

    #create a file to save data to --> what is a good way to save this?
    d = qt.Data(name='magnet_auto_Z_optimization_overview')
    d.add_coordinate('iteration')
    d.add_value('frequency [GHz]')
    d.add_value('frequency error [GHz]')
    d.add_value('frequency difference [GHz]')
    d.add_value('number of steps')
    d.create_file()
    filename=d.get_filepath()[:-4]
    print iterations_list
    print f0
    print u_f0
    print delta_f0
    print d_steps
    d.add_data_point(iterations_list, f0,u_f0,delta_f0,d_steps)
    d.close_file()


    print 'Z position fine optimization finished, stepped the magnet '+ str(total_d_steps) + ' in '+str(iterations+1) +' iterations'

