"""
LT2 script for adwin ssro.
"""
import qt
#reload all parameters and modules
execfile(qt.reload_current_setup)

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro

SAMPLE_CFG = qt.exp_params['protocols']['current']

def ssrocalibration(name, params = None):
    m = ssro.AdwinSSRO('SSROCalibration_'+name)
    print 'test2'
    
    if params == None:
        m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
        m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    else :
        print 'test'
        m.params.from_dict(params)

    
    # parameters
    e_sp = m.params['Ex_SP_amplitude'] 
    a_sp =  m.params['A_SP_amplitude']

    print m.params['Ex_CR_amplitude']


    # ms = 0 calibration
    m.params['SP_duration'] = m.params['SP_duration_ms0']
    m.params['Ex_SP_amplitude'] = 0.
    m.params['A_SP_amplitude'] = a_sp
    m.run()
    m.save('ms0')

    # ms = 1 calibration
    m.params['SP_duration'] = m.params['SP_duration_ms1']
    m.params['A_SP_amplitude'] = 0
    m.params['Ex_SP_amplitude'] = e_sp
    m.run()
    m.save('ms1')

    m.finish()

if __name__ == '__main__':
    ssrocalibration(SAMPLE_CFG)
