"""
LT2 script for adwin ssro.
"""
import qt
#reload all parameters and modules
execfile(qt.reload_current_setup)

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro
#from measurement.lib.measurement2.adwin_ssro import pulsar_measurement as pulsar_msmnt

SAMPLE_CFG = qt.exp_params['protocols']['current']

def ssrocalibration(name):
    m = ssro.AdwinSSRO('SSROCalibration_'+name)
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['Magnetometry'])
    stools.turn_off_all_lasers()
    # parameters
    m.params['SSRO_repetitions'] = 5000
    m.params['SSRO_duration']       = 100
    m.params['SSRO_stop_after_first_photon']= 0


    m.params['CR_preselect']    = 1000
    m.params['CR_repump']       = 1000
    m.params['CR_probe']        = 1000

    e_sp = m.params['Ex_SP_calib_amplitude']
    a_sp=  m.params['A_SP_amplitude']

    #m.params['green_rempump_duration']=150
    #m.params['green_repump_amplitude'] = 30e-6
    #print m.params['Ex_CR_amplitude']


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


def ssrocalibration_ms_0_p1(name):
    m = ssro.AdwinSSRO('SSROCalibration_'+name)
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['Magnetometry'])
    stools.turn_off_all_lasers()
    # parameters
    m.params['SSRO_repetitions'] = 5000
    m.params['SSRO_duration']       = 100
    m.params['SSRO_stop_after_first_photon']= 0


    m.params['CR_preselect']    = 1000
    m.params['CR_repump']       = 1000
    m.params['CR_probe']        = 1000

    e_sp = 5e-9
    a_sp=  m.params['A_SP_amplitude']

    #m.params['green_rempump_duration']=150
    #m.params['green_repump_amplitude'] = 30e-6
    #print m.params['Ex_CR_amplitude']


    # ms = 0 calibration
    m.params['SP_duration']=50
    m.params['Ex_SP_amplitude'] = 0.
    m.params['A_SP_amplitude'] = a_sp
    m.run()
    m.save('ms0')

    # ms = 1 calibration
    
    m.params['SP_duration']=300
    m.params['A_SP_amplitude'] = 0
    m.params['Ex_SP_amplitude'] = e_sp
    m.run()
    m.save('ms1')

    m.finish()


if __name__ == '__main__':
    ssrocalibration(SAMPLE_CFG)
