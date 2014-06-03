"""
Work in progress :)
Anais
"""

import qt
#reload all parameters and modules
execfile(qt.reload_current_setup)




if __name__ == '__main__':
    run_calibration(0)
    """
    stage 0 : SSRO calibration
    stage 1 : ESR (simple esr or dark esr)
            --> central resonance frequency to put in 'f_msm1_cntr' in qt.exp_params 
    stage 2 : Rabi oscillations
            --> if CORPSE rabi oscillations for 'CORPSE_rabi_frequency' in qt.exp_params
            CAUTION, a factor 1/2 remains between the definition of the Rabi frequency 
            that is used in the script and its standard definition
            (eg. f_Rabi = pi/pi_pulse_duration)
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
