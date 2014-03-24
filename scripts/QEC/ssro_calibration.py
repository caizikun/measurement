"""
LT2 script for adwin ssro.
"""
import qt

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro

# reload the msmt_params
execfile("lt2_scripts/setup/msmt_params.py")
SAMPLE_CFG = qt.cfgman['protocols']['current']

def ssrocalibration(name):
    m = ssro.AdwinSSRO('SSROCalibration_'+name)
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols'][SAMPLE_CFG]['AdwinSSRO'])

    # ms = 0 calibration
    m.autoconfig()
    m.setup()
    m.run()
    m.save('ms0')

    # ms = 1 calibration
    m.params['SP_duration'] = 300
    m.params['A_SP_amplitude'] = 0.
    m.params['Ex_SP_amplitude'] = 10e-9

    m.run()
    m.save('ms1')
    m.finish()

if __name__ == '__main__':
    ssrocalibration(SAMPLE_CFG)
