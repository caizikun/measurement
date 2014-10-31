"""
Script for optimizing the magnet position in Z-direction.
Important: choose the right domain for the range of positions in get_magnet_position in magnet tools!

"""
import numpy as np
import qt
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
import msvcrt

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt

# import the dESR fit
from analysis.lib.fitting import dark_esr_auto_analysis

# import magnet tools and master of magnet
from measurement.lib.tools import magnet_tools as mt
from measurement.instruments import Master_of_magnet

execfile(qt.reload_current_setup)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

nm_per_step = qt.exp_params['magnet']['nm_per_step']

B_step_per_msmt = 10 

def darkesr(name, center_frequency = f_msp1_cntr):

    m = pulsar_msmt.DarkESR(name)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])


    #m.params['mw_frq'] = m.params['ms+1_cntr_frq']-43e6 #MW source frequency
    m.params['mw_frq'] = 2*m.params['zero_field_splitting'] - center_frequency -43e6

    m.params['mw_power'] = 20
    m.params['repetitions'] = 3000

    m.params['ssbmod_frq_start'] = 43e6 - 15e6 ## fist time we choose a quite large domain to find the three dips
    m.params['ssbmod_frq_stop'] = 43e6 + 15e6
    m.params['pts'] = 101
    m.params['pulse_length'] = 2e-6
    m.params['ssbmod_amplitude'] = 0.05

    m.autoconfig()
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()

if __name__ == '__main__':

    # start: define B-field and position by first ESR measurement

    darkesr(SAMPLE_CFG+'step_magnet_'+str(0))

    # do the fitting  --> this fit programme returns in MHz, needs input GHz
    f0_temp,u_f0_temp = dark_esr_auto_analysis.analyze_dark_esr(m.params['ms+1_cntr_frq']*1e-9,
        m.params['N_HF_frq']*1e-9 )
    
    # start to list all the measured values
    iterations = 0
    B_field_measured  =mt.convert_f_to_Bz(freq=f0_temp*1e6)

    print 'Measured frequency = ' +str(f0_temp*1e-3)+' GHz'
    print 'Measured B-field = '+str(B_field_measured)+' G'
    distance = mt.get_magnet_position(msm1_freq=f0_temp*1e-6, ms = 'plus',solve_by = 'list')
    print 'Distance between magnet and NV centre = '+str(distance) + ' mm'

    for ii in range(0):#(1,9):

        B_field = B_field_measured + B_step_per_msmt
        steps_for_msmt = steps_to_field(B_field,frequency = f0_temp)

        print 'To move from B = ' +str(B_field_measured) + 'G to B = ' + str(B_field)+' G, we move \
        the magnet '+ str (steps_for_msmt)+' steps in Z'

        #Master_of_magnet.step('Z_axis',steps_for_msmt)
       
        qt.msleep(5) # because QTlab does not know that the magnet is still stepping (this should be enough, can also set with freq)

        stools.turn_off_all_lt2_lasers()
        GreenAOM.set_power(5e-6) 
        optimiz0r.optimize(dims=['x','y','z','x','y'])
        
        # Make sure you can always stop the optimization process --> keep an eye on the optimization because this
        # can cause crosstalk
        print 'press q to stop measurement loop (check if optimize worked!)'
        qt.msleep(2)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            break

        # determine the expected new centre frequency for the ESR msmt
        #center_frequency = mt.convert_Bz_to_f(B_field)
        
        # perform the dark ESR measurement
        darkesr(SAMPLE_CFG+'step_magnet_'+str(ii), center_frequency = center_frequency)
        
        # do the fitting  --> this fit programme returns in MHz, needs input GHz
        f0_temp,u_f0_temp = dark_esr_auto_analysis.analyze_dark_esr(m.params['ms+1_cntr_frq']*1e-9,
            m.params['N_HF_frq']*1e-9 )

        print 'Measured frequency = ' +str(f0_temp*1e-3)+' GHz'
        print 'Measured B-field = '+str(B_field_measured[iterations])+' G'
        distance = mt.get_magnet_position(msm1_freq=f0_temp*1e-6, ms = 'plus',solve_by = 'list')
        print 'Distance between magnet and NV centre = '+str(distance) + ' mm'