"""
Script to sweep the magnet and determine the field. This script does not do fits 
(i.e. it is not for automatic optimization).
by THT and Julia
"""
import numpy as np
import qt
import msvcrt
# import the msmt class
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt
# import magnet tools and master of magnet
from measurement.lib.tools import magnet_tools as mt; reload(mt)
mom = qt.instruments['master_of_magnet']

execfile(qt.reload_current_setup)

ins_adwin = qt.instruments['adwin']
ins_counters = qt.instruments['counters']
ins_aom = qt.instruments['GreenAOM']

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

nm_per_step = qt.exp_params['magnet']['nm_per_step']
current_f_msp1 = qt.exp_params['samples'][SAMPLE]['ms+1_cntr_frq']
current_f_msm1 = qt.exp_params['samples'][SAMPLE]['ms-1_cntr_frq']
ZFS = qt.exp_params['samples'][SAMPLE]['zero_field_splitting']

def darkesr(name, ms):
    ''' simple DESR fucntion'''
    
    if ms == 'msp':
        m.params['mw_frq'] = m.params['ms+1_cntr_frq']-43e6 #MW source frequency
    elif ms == 'msm':
        m.params['mw_frq'] = m.params['ms-1_cntr_frq']-43e6 #MW source frequency
    
    m.params['ssbmod_frq_start'] = 43e6 - 8e6
    m.params['ssbmod_frq_stop'] = 43e6 + 8e6
    m.params['pts'] = 101
    m.params['pulse_length'] = 2e-6
    m.params['ssbmod_amplitude'] = 0.03

    m.autoconfig()
    m.generate_sequence()
    m.run()
    m.save(name)
    
if __name__ == '__main__':

    ### Set input parameters ###
    axis = 'x_axis'
    scan_range = 20            #from -scan rage to +scan range  
    no_of_steps = 3            #with a total of .. measurment points
    maximum_magnet_step = 10


    stepsize = scan_range/(no_of_steps-1) 
    steps = [0] + (no_of_steps-1)/2*[stepsize] + (no_of_steps-1)*[-stepsize] + (no_of_steps-1)/2*[stepsize] 
    print steps
    
    ### Create the measurement ###
    m = pulsar_msmt.DarkESR(SAMPLE_CFG + '_magnet_sweep')
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params['mw_power'] = 20
    m.params['repetitions'] = 1000
    pos = 0
    for k in range(len(steps)):
        step = steps[k]
        pos += step 
        print 'stepping by ' + str(step) + 'to_pos = ' + str(pos)  
        
        if step == 0:
            print 'made 0 steps'
        else:
            for i in range(abs(step)/maximum_magnet_step):
                print 'step by ' + str(np.sign(step)*maximum_magnet_step)
                mom.step('X_axis',np.sign(step)*maximum_magnet_step)
                print 'magnet stepped by ' + str((i+1)*np.sign(step)*maximum_magnet_step) + ' out of ' + str(step)
                qt.msleep(1)
                GreenAOM.set_power(5e-6)
                ins_counters.set_is_running(0)
                counter = 1
                int_time = 1000 
                cnts = ins_adwin.measure_counts(int_time)[counter-1]
                print 'counts = '+str(cnts)
                if cnts < 1e4:
                    optimiz0r.optimize(dims=['x','y','z','x','y'])
                print 'press q to stop magnet movement'
                qt.msleep(5)
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                    break    

        print 'press q to stop measurement cleanly'
        qt.msleep(5)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            break    
              
        GreenAOM.set_power(5e-6)
        optimiz0r.optimize(dims=['x','y','z','x','y'])

        ### start the  DESR measurement ### 
        darkesr('measurmemt_msp_' + str(k), ms = 'msp')
        qt.msleep(1)
        darkesr('measurmemt_msm' + str(k), ms = 'msm')
        print 'press q to stop measurement cleanly'
        
    ### Finish the measurement ###
    m.finish()

