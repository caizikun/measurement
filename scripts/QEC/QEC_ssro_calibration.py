"""
script for adwin ssro calibration.
"""
import qt
#reload all parameters and modules
execfile(qt.reload_current_setup)

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro

SAMPLE_CFG = qt.exp_params['protocols']['current']

def ssrocalibration(name,RO_power=None,SSRO_duration=None):
    m = ssro.AdwinSSRO('SSROCalibration_'+name)
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    if RO_power != None: 
        m.params['Ex_RO_amplitude'] = RO_power
    if SSRO_duration != None: 
        m.params['SSRO_duration'] = SSRO_duration

    m.run()
    m.save('ms0')

    # ms = 1 calibration
    m.params['SP_duration']     = 500
    m.params['A_SP_amplitude']  = 0.
    m.params['Ex_SP_amplitude'] = 15e-9#20e-9
    m.run()
    m.save('ms1')

    m.finish()

if __name__ == '__main__':
    ssrocalibration(SAMPLE_CFG)
    #ssrocalibration(SAMPLE_CFG, RO_power = 0.5e-9,SSRO_duration = 100)

    # RO_powers = [0.2e-9,0.5e-9,1e-9,2e-9,5e-9]
    # for RO_power in RO_powers: 
    #     print 'RO_power = %s W' %RO_power 
    #     ssrocalibration(SAMPLE_CFG,RO_power = RO_power,SSRO_duration = 50)
    #     ri = raw_input ('Do Fitting. Press c to continue. \n')
    #     if str(ri) != 'c':
    #         break
    #  NOTE: If you want to measure make sure you analyse a normal ssro as last 
    # TODO: Make a simple SSRO analysis script that does not edit the config. 
