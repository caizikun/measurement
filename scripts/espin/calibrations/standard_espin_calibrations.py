"""
Work in progress :)
Anais
"""

import numpy as np
import qt
#reload all parameters and modules
execfile(qt.reload_current_setup)


# from adwin_ssro import ssro and pulsar as pulsar_msmt
from measurement.scripts.espin import espin_funcs as funcs
reload(funcs)

SAMPLE_CFG = qt.exp_params['protocols']['current']






### called at stage 2.5
def dark_esr(name):
    '''
    dark ESR on the 0 <-> -1 transition
    '''

    m = pulsar_msmt.DarkESR(name)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])


    m.params['ssmod_detuning'] = 43e6
    m.params['mw_frq']       = m.params['ms-1_cntr_frq'] - m.params['ssmod_detuning'] #MW source frequency, detuned from the target
    m.params['repetitions']  = 2000
    m.params['range']        = 4e6
    m.params['pts'] = 131
    m.params['pulse_length'] = 1.6e-6
    m.params['ssbmod_amplitude'] = 0.05
    
    m.params['Ex_SP_amplitude']=0



    m.params['ssbmod_frq_start'] = m.params['ssmod_detuning'] - m.params['range']
    m.params['ssbmod_frq_stop']  = m.params['ssmod_detuning'] + m.params['range']

    debug=True

    m.autoconfig()
    m.generate_sequence(upload=True)
    m.run(debug=debug)
    m.save()
    m.finish()




### master function
def run_calibrations(stage): 
    if stage == 0 :
        print "Firstly measure the resonance frequency with a continuous ESR\
         : execfile(r'D:/measuring/scripts/espin/esr.py')"
        print "Analysis suggestion : execfile(r'D:/measuring/analysis/scripts/espin/simple_esr_fit.py')"

    if stage == 1 :
        print "execute SSRO calibration : execfile(r'D:/measuring/scripts/ssro/ssro_calibration.py')"

    if stage == 2.5 :
        print "Starting a dark ESR spectrum"
        dark_esr(SAMPLE_CFG)
        print "Analysis suggestion : execfile(r'D:/measuring/analysis/scripts/espin/dark_esr_analysis.py')"
 


    if stage == 1:
        print 'Cal CORPSE pi'
        cal_CORPSE_pi(name, multiplicity=11)
    if stage == 1.5:
        print 'Cal CORPSE pi/2'
        cal_CORPSE_pi2(name)
    if stage == 2:
        dd_calibrate_C13_revival(name)
    if stage == 3:
        dd_sweep_LDE_spin_echo_time(name)
    if stage == 4:
        dd_sweep_LDE_DD_XYX_t_between_pulse(name)





if __name__ == '__main__':
    run_calibration(0)
    """
    stage 0 : continuous ESR
            --> central resonance frequency to put in 'f_msm1_cntr' in qt.exp_params 

    stage 1 : SSRO calibration

    stage 2 : : Rabi oscillations
                --> if CORPSE rabi oscillations for 'CORPSE_rabi_frequency' in qt.exp_params
            CAUTION, a factor 1/2 remains between the definition of the Rabi frequency 
            that is used in the script and its standard definition
            (eg. f_Rabi = pi/pi_pulse_duration)
    stage 2.5 : eventually perfom a dark ESR
            --> central resonance frequency to put in 'f_msm1_cntr' in qt.exp_params 

    stage 3.0 : coarse calibration of the pi CORPSE pulse 
        sweep of the pulse amplitude
            - choice between 
                - normal CORPSE pulse
                - with IQ modulation
                - with I modulation ?
    stage 3.5 : fine calibration of the pi CORPSE pulse
    		- with multiplicity != 1
    		--> 'CORPSE_pi_amp' in qt.exp_params
    stage 4.0 : coarse calibration of the pi/2 CORPSE pulse
    """
