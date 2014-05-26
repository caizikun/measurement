"""
script for adwin ssro calibration.
"""
import qt
#reload all parameters and modules
execfile(qt.reload_current_setup)

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro

SAMPLE_CFG = qt.exp_params['protocols']['current']

def ssrocalibration(name):
    m = ssro.AdwinSSRO('SSROCalibration_'+name)
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])


    m.params['SSRO_duration']   =  50
    m.params['Ex_RO_amplitude'] =  2e-9 
    
    m.params['SSRO_stop_after_first_photon']=1
    m.run()
    m.save('ms0')

    # ms = 1 calibration
    m.params['SP_duration']     = 250
    m.params['A_SP_amplitude']  = 0.
    m.params['Ex_SP_amplitude'] = 20e-9
    m.run()
    m.save('ms1')

    m.finish()

if __name__ == '__main__':
    ssrocalibration(SAMPLE_CFG)
