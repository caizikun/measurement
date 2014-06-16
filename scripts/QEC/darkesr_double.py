"""
Script for e-spin manipulations using the pulsar sequencer
"""
import numpy as np
import qt

#reload all parameters and modules
execfile(qt.reload_current_setup)

#import measurement.lib.config.adwins as adwins_cfg
#import measurement.lib.measurement2.measurement as m2

# import the msmt class
#from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt

SAMPLE= qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def darkesrm1(name):

    m = pulsar_msmt.DarkESR(name)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])

    
    m.params['mw_mod_freq'] = 43e6
    m.params['SSRO_duration'] = 8    
    m.params['SP_duration'] = 50

    # m.params['mw_frq'] = m.params['ms-1_cntr_frq'] - m.params['mw_mod_freq'] #MW source frequency

    m.params['mw_frq'] = 2*m.params['zero_field_splitting'] - m.params['ms+1_cntr_frq'] - m.params['mw_mod_freq']

    m.params['mw_power'] = 20
    m.params['repetitions'] = 500

    m.params['ssbmod_frq_start'] = m.params['mw_mod_freq'] - 5e6
    m.params['ssbmod_frq_stop'] = m.params['mw_mod_freq'] + 5e6
    m.params['pts'] = 51
    m.params['pulse_length'] = 10e-6
    m.params['ssbmod_amplitude'] = 0.008

    m.autoconfig()
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()

def darkesrp1(name):

    m = pulsar_msmt.DarkESR(name)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])

    m.params['mw_mod_freq'] = 43e6
    m.params['SP_duration'] = 50
    # m.params['ms+1_cntr_frq'] =  3.725838e9
    m.params['mw_frq'] = m.params['ms+1_cntr_frq']-m.params['mw_mod_freq'] #MW source frequency
    # m.params['mw_frq'] = 2*m.params['zero_field_splitting'] - m.params['ms-1_cntr_frq'] - m.params['mw_mod_freq']


    m.params['mw_power'] = 20
    m.params['repetitions'] = 500

    m.params['ssbmod_frq_start'] = m.params['mw_mod_freq'] - 5e6
    m.params['ssbmod_frq_stop'] = m.params['mw_mod_freq'] + 5e6
    m.params['pts'] = 51
    m.params['pulse_length'] = 5e-6
    m.params['ssbmod_amplitude'] = 0.010

    m.autoconfig()
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()

if __name__ == '__main__':
    # darkesrm1(SAMPLE_CFG)
    darkesrp1(SAMPLE_CFG)
    cont = raw_input ('Do the fitting for ms=+1... Continue with ms=-1 y/n?')
    if cont =='y':
        darkesrm1(SAMPLE_CFG)

