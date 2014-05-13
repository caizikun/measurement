"""
Script for optimizing the magnet position in Z-direction.
Important: choose the right domain for the range of positions in get_magnet_position in magnet tools!
At the moment this only optimizes the Z position on the ms=+1 transition
"""
import numpy as np
import qt
import msvcrt

#import measurement.lib.config.adwins as adwins_cfg
#import measurement.lib.measurement2.measurement as m2

# import the msmt class
#from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt

# import the dESR fit
from analysis.lib.fitting import dark_esr_auto_analysis; reload(dark_esr_auto_analysis)

# import magnet tools and master of magnet
from measurement.lib.tools import magnet_tools as mt; reload(mt)
mom = qt.instruments['master_of_magnet']
reload(mt)

execfile(qt.reload_current_setup)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']
nm_per_step = qt.exp_params['magnet']['nm_per_step']
current_f_msp1 = qt.exp_params['samples'][SAMPLE]['ms+1_cntr_frq']

# Define the wanted magnet position
B_field_ideal = mt.convert_f_to_Bz(freq=current_f_msp1)
position_ideal = mt.get_magnet_position(msp1_freq=current_f_msp1,ms = 'plus',solve_by = 'list')
B_error_range = 2e-3 # allowed error in B_field (it was 7mG in RT experiment, can be changed)

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

    ## Input parameters ##
    init_range   = 6     #Common: 10 MHz
    init_pts     = 81    #Common: 121
    init_reps    = 500   #Common: 500

    repeat_range = 6
    repeat_pts   = 81
    repeat_reps  = 1000

    #create the lists to save the data to
    d_steps = []
    f0 = []
    u_f0 = []
    B_field_measured = []

    #turn on magnet stepping in Z
    mom.set_mode('Z_axis', 'stp')

    # start: define B-field and position by first ESR measurement
    darkesr(SAMPLE_CFG+'_magnet_optimization', range_MHz=init_range, pts=init_pts, reps=init_reps)

    # do the fitting  --> this fit programme returns in MHz, needs input GHz ! guess center freq can be gone!
    f0_temp, u_f0_temp = dark_esr_auto_analysis.analyze_dark_esr(current_f_msp1*1e-9, qt.exp_params['samples'][SAMPLE]['N_HF_frq']*1e-9)

    # start to list all the measured values
    iterations = 0
    f0.append(f0_temp)
    u_f0.append(u_f0_temp)
    B_field_measured.append(mt.convert_f_to_Bz(freq=f0_temp*1e9))

    print 'Measured frequency = ' +str(f0_temp)+' GHz, so '+str(abs(f0_temp*1e6-current_f_msp1*1e-3))+' kHz away from wanted frequency'
    print 'Measured B-field = '+str(B_field_measured[iterations])+' G, , so '+str(abs(B_field_measured[iterations]-B_field_ideal))+' G away from wanted frequency'

    print B_error_range
    print B_field_ideal
    print B_field_measured

    # start loop to optimize the field if field is out of set range
    while abs(B_field_measured[iterations]-B_field_ideal) > B_error_range:

        # Step the magnet
        d_steps.append(int(round(mt.steps_to_frequency(freq=f0_temp*1e9,freq_id=current_f_msp1, ms = 'plus'))))
        print 'move magnet in Z with '+ str(d_steps[iterations]) + ' steps'

        if abs(d_steps[iterations]) > 250:
            print 'd_steps>+/-100, step only 250 steps!'
            if d_steps[iterations] > 0:
                mom.step('Z_axis',250)
                d_steps[iterations] = 250
            if d_steps[iterations] < 0:
                mom.step('Z_axis',-250)
                d_steps[iterations] = -250
        elif d_steps[iterations]==0:
            print 'Steps = 0 optimization converted'
            break
        else:
            mom.step('Z_axis',d_steps[iterations])

        qt.msleep(1)
        stools.turn_off_all_lt2_lasers()
        GreenAOM.set_power(5e-6)
        optimiz0r.optimize(dims=['x','y','z'])

        # To cleanly exit the optimization
        print 'press q to stop measurement loop (check if optimize worked!)'
        qt.msleep(2)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            break

        iterations += 1
        #do dESR
        darkesr(SAMPLE_CFG, range_MHz=repeat_range, pts=repeat_pts, reps=repeat_reps)
        
        #Determine frequency and B-field --> this fit programme returns in MHz, needs input GHz
        f0_temp,u_f0_temp = dark_esr_auto_analysis.analyze_dark_esr(current_f_msp1*1e-9,qt.exp_params['samples'][SAMPLE]['N_HF_frq']*1e-9 )
        f0.append(f0_temp)
        u_f0.append(u_f0_temp)
        B_field_measured.append(mt.convert_f_to_Bz(freq=f0_temp*1e9))

        print 'Measured frequency = ' +str(f0_temp)+' GHz, so '+str(abs(f0_temp*1e6-current_f_msp1*1e-3))+' kHz away from wanted frequency'
        print 'Measured B-field = '+str(B_field_measured[iterations])+' G, , so '+str(abs(B_field_measured[iterations]-B_field_ideal))+' G away from wanted frequency'

        


    total_d_steps = np.sum(d_steps)
    #create a file to save data to --> what is a good way to save this?
    d = qt.Data(name='magnet_optimization_overview')
    d.add_coordinate('iteration')
    d.add_value('frequency [GHz]')
    d.add_value('frequency error [GHz]')
    d.add_value('Bfield [G]')
    d.add_value('number of steps')
    d.create_file()
    filename=d.get_filepath()[:-4]
    d.add_data_point(iterations, f0,u_f0,B_field_measured,d_steps)
    d.close_file()

    print 'Bz field optimized, stepped the magnet '+ str(total_d_steps) + ' in '+str(iterations) +' iterations in Z direction'

