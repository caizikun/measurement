"""
Script for e-spin manipulations using the pulsar sequencer
"""
import numpy as np
import qt

#reload all parameters and modules
execfile(qt.reload_current_setup)

import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
from measurement.lib.measurement2.adwin_ssro import pulse_select as ps
import time
#reload(funcs)
SAMPLE= qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def darkesr(name):
    '''dark ESR on the 0 <-> -1 transition
    '''

    m = pulsar_msmt.DarkESR(name)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    # m.params['ssmod_detuning'] = 250e6#m.params['MW_modulation_frequency']
    m.params['mw_frq'] = m.params['ms-1_cntr_frq']-43e6 #MW source frequency
    m.params['repetitions']  = 2000
    m.params['range']        = 1.e6
    m.params['pts'] = 81
    m.params['pulse_length'] = m.params['DESR_pulse_duration'] # was 2.e-6 changed to msmt params # NK 2015-05 27
    m.params['ssbmod_amplitude'] = m.params['DESR_pulse_amplitude'] #0.03 changed to msmt params # NK 2015-05-27
    m.params['mw_power'] = 20
    m.params['Ex_SP_amplitude']=0

    m.params['ssbmod_frq_start'] = 43e6 - m.params['range']  
    m.params['ssbmod_frq_stop'] = 43e6 + m.params['range'] 
    list_swp_pts =np.linspace(m.params['ssbmod_frq_start'],m.params['ssbmod_frq_stop'], m.params['pts'])
    m.params['sweep_pts'] = (np.array(list_swp_pts) +  m.params['mw_frq'])*1e-9
    m.autoconfig()
    #m.params['sweep_pts']=m.params['pts']
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()

def darkesrp1(name):
    '''dark ESR on the 0 <-> +1 transition
    '''

    m = pulsar_msmt.DarkESR(name)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])
    # m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['Magnetometry'])


    # m.params['ssmod_detuning'] = m.params['MW_modulation_frequency']
    m.params['mw_frq']         = m.params['ms+1_cntr_frq']-43e6# - m.params['ssmod_detuning'] # MW source frequency, detuned from the target
    m.params['mw_power'] = 20
    m.params['repetitions'] = 1000
    m.params['range']        = 5e6
    m.params['pts'] = 81
    m.params['pulse_length'] = m.params['DESR_pulse_duration'] #2.1e-6 changed to msmt params # NK 2015-05 27
    m.params['ssbmod_amplitude'] = m.params['DESR_pulse_amplitude'] #0.03 changed to msmt params # NK 2015-05-27

    m.params['ssbmod_frq_start'] = 43e6 - m.params['range']  
    m.params['ssbmod_frq_stop'] = 43e6 + m.params['range'] 
    list_swp_pts =np.linspace(m.params['ssbmod_frq_start'],m.params['ssbmod_frq_stop'], m.params['pts'])
    m.params['sweep_pts'] =(np.array(list_swp_pts) + m.params['mw_frq'])*1e-9
    m.autoconfig()
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()


def show_stopper():
    print '-----------------------------------'            
    print 'press q to stop measurement cleanly'
    print '-----------------------------------'
    qt.msleep(2)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        return True
    else: return False

def optimize_NV(cycles = 1):
    qt.msleep(2)
    # AWG.clear_visa()
    stools.turn_off_all_lasers()
    qt.msleep(1)
    GreenAOM.set_power(12e-6)
    optimiz0r.optimize(dims=['x','y','z','x','y'], cycles = cycles)
    stools.turn_off_all_lasers()


if __name__ == '__main__':


    breakstatement = False

    start_time = time.time()


    while abs(time.time()- start_time) < 12*60*60: ### 12 hours of measurement. HOOORAY!
        #some info
        print 'Time until I stop', 12*60*60 - (time.time()- start_time)

        ### stop experiment? Press q.
        breakstatement = show_stopper()
        if breakstatement: break

    ### run experiment
        darkesr(SAMPLE_CFG)

        optimize_NV()

        # print 'last optimize', 0.5*60*60 - (time.time()-last_optimize)
        # if abs(time.time()-last_optimize) > 0.5*60*60:
        #     optimize()
        #     last_optimize = time.time()