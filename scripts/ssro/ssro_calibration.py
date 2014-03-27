"""
LT1/2 script for adwin ssro.
"""
import numpy as np
import qt
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro

# import the measurement parameters
SAMPLE_CFG = qt.cfgman['protocols']['current']

def ssrocalibration(name):
    m = ssro.AdwinSSRO('SSROCalibration_'+name)
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][SAMPLE_CFG]['AdwinSSRO'])

    # parameters
    m.params['SSRO_repetitions'] = 5000
    m.params['SSRO_duration']       = 100
    m.params['SSRO_stop_after_first_photon']= 0

   
    m.params['CR_preselect']    = 1000
    m.params['CR_repump']       = 1000
    m.params['CR_probe']        = 1000

    e_sp = m.params['Ex_SP_amplitude']

    
    # ms = 0 calibration
    m.params['SP_duration']=50
    m.params['Ex_SP_amplitude'] = 0.
    m.run()
    m.save('ms0')

    # ms = 1 calibration
    m.params['SP_duration']=250
    m.params['A_SP_amplitude'] = 0.
    m.params['Ex_SP_amplitude'] = e_sp
    m.run()
    m.save('ms1')

    m.finish()

if __name__ == '__main__':
    ssrocalibration(SAMPLE_CFG)

