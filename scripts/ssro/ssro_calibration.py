"""
LT2 script for adwin ssro.
"""
import qt
#reload all parameters and modules
execfile(qt.reload_current_setup)

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro

SAMPLE_CFG = qt.exp_params['protocols']['current']

def ssrocalibration(name, **additional_params):
    m = ssro.AdwinSSRO('SSROCalibration_'+name)

    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(additional_params)

    # ms = 0 calibration
    m.params['SP_duration'] = m.params['SP_duration_ms0']
    m.params['Ex_SP_amplitude'] = 0.
    m.params['A_SP_amplitude'] = m.params['A_SP_amplitude']
    if m.run():
        m.save('ms0')

        # ms = 1 calibration
        m.params['SP_duration'] = m.params['SP_duration_ms1']
        m.params['A_SP_amplitude'] = 0.
        m.params['Ex_SP_amplitude'] = m.params['Ex_SP_calib_amplitude']
        m.run()
        m.save('ms1')

    m.finish()

if __name__ == '__main__':
    stools.turn_off_all_lasers()
    ssrocalibration(SAMPLE_CFG)
    
