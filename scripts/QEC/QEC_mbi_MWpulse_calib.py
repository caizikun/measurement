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

import measurement.scripts.mbi.mbi_funcs as funcs
reload(funcs)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def erabi(name):
    m = pulsar_msmt.ElectronRabi(name)
    funcs.prepare(m) 

    # NOTE: Replaced all the m.params.from_dict statements with funcs.prepare(m) 
    # m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    # m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    # m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    # m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    # m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    # m.params.from_dict(qt.exp_params['protocols'][SAMPLE]['pulses'])


    m.params['pts'] = 31
    pts = m.params['pts']
    m.params['repetitions'] = 1000

    m.params['MW_pulse_frequency'] = m.params['mw_mod_freq'] 

    if 0:
        m.params['MW_pulse_durations'] =  np.ones(pts)*m.params['AWG_MBI_MW_pulse_duration']
        m.params['MW_pulse_amplitudes'] = np.linspace(0,0.04,pts)
        m.params['sweep_name'] = 'MW_pulse_amplitudes (V)'
        m.params['sweep_pts'] = m.params['MW_pulse_amplitudes']

    elif 1:
        m.params['MW_pulse_durations'] =  np.linspace(0,10e-6,pts)
        m.params['MW_pulse_amplitudes'] = np.ones(pts)*m.params['AWG_MBI_MW_pulse_amp']
        m.params['sweep_name'] = 'MW_pulse_durations (us)'
        m.params['sweep_pts'] = m.params['MW_pulse_durations']*1e6

    m.autoconfig() #Redundant because executed in m.run()? Tim
    m.generate_sequence(upload=True)
    m.run(autoconfig=False)
    m.save()
    m.finish()

if __name__ == '__main__':
    erabi(SAMPLE+'_'+'rabi')
