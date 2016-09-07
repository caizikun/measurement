"""
Script for fine optimization of the magnet XY-position (using the average ms=-1, ms=+1 freq).
Fine optimization measures only the center resonance
Important: choose the right domain for the range of positions in get_magnet_position in magnet tools!
"""

# import the DESR measurement, DESR fit, magnet tools and master of magnet
from measurement.scripts.QEC.magnet import DESR_msmt; reload(DESR_msmt)

execfile(qt.reload_current_setup)

f0p_temp = qt.exp_params['samples'][SAMPLE]['ms+1_cntr_frq']*1e-9
f0m_temp = qt.exp_params['samples'][SAMPLE]['ms-1_cntr_frq']*1e-9
N_hyperfine = qt.exp_params['samples'][SAMPLE]['N_HF_frq']

if __name__ == '__main__':
    
    ######################
    ## Input parameters ##
    ######################

    range_fine  = 0.40
    pts_fine    = 51   
    reps_fine   = 1500 #1000
        
    DESR_msmt.darkesr('magnet_' +  'msm1', ms = 'msm', 
            range_MHz=range_fine, pts=pts_fine, reps=reps_fine, freq=f0m_temp*1e9,# - N_hyperfine,
            pulse_length = 8e-6, ssbmod_amplitude = 0.0125)

    DESR_msmt.darkesr('magnet_' +  'msp1', ms = 'msp', 
            range_MHz=range_fine, pts=pts_fine, reps=reps_fine, freq=f0p_temp*1e9,# + N_hyperfine, 
            pulse_length = 8e-6, ssbmod_amplitude = 0.025)

