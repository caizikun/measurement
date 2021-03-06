'''
Notes

Initialize via ms = 0 and then a MW pulse instead of pumping on E' (which does + and -1 at the same time)
'''

"""
LT2 script for adwin ssro.
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
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['Magnetometry'])
    # parameters
    m.params['SSRO_repetitions'] = 5000
    m.params['SSRO_duration']       = 100
    m.params['SSRO_stop_after_first_photon']= 0


    m.params['CR_preselect']    = 1000
    m.params['CR_repump']       = 1000
    m.params['CR_probe']        = 1000

    e_sp = 18e-9
    a_sp=  m.params['A_SP_amplitude']

    #m.params['green_rempump_duration']=150
    #m.params['green_repump_amplitude'] = 30e-6
    print m.params['Ex_CR_amplitude']

    ''' remains unchanged '''
    # ms = 0 calibration
    m.params['SP_duration']=200
    m.params['Ex_SP_amplitude'] = 0.
    m.params['A_SP_amplitude'] = a_sp
    m.run()
    m.save('ms0')

    ''' init via MW '''
    # ms = 1 calibration
    m.params['SP_duration']=300
    m.params['Ex_SP_amplitude'] = 0
    #init into ms = 0
    m.params['A_SP_amplitude'] = a_so
    
    # MW parameters
    m.run()
    m.save('ms1')

    m.finish()

if __name__ == '__main__':
    ssrocalibration(SAMPLE_CFG)
