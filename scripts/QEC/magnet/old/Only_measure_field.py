"""
Script for coarse optimization of the magnet Z-position (using the ms=+1 resonance).
Coarse optimization starts with a large range scan and then zooms in
Important: choose the right domain for the range of positions in get_magnet_position in magnet tools!
"""
import numpy as np
import qt
import msvcrt
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt; reload(pulsar_msmt)

# import the dESR fit, magnet tools and master of magnet
from analysis.lib.fitting import dark_esr_auto_analysis; reload(dark_esr_auto_analysis)
from measurement.lib.tools import magnet_tools as mt; reload(mt)
mom = qt.instruments['master_of_magnet']; reload(mt)

execfile(qt.reload_current_setup)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']
nm_per_step = qt.exp_params['magnet']['nm_per_step']
current_f_msm1 = qt.exp_params['samples'][SAMPLE]['ms-1_cntr_frq']

def darkesr(name, range_MHz, pts, reps):

    m = pulsar_msmt.DarkESR_Switch(name)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])

    m.params['mw_frq'] = m.params['ms-1_cntr_frq']-43e6 #MW source frequency
    #m.params['mw_frq'] = 2*m.params['zero_field_splitting'] - m.params['ms-1_cntr_frq'] -43e6

    m.params['mw_power'] = 20
    m.params['repetitions'] = reps

    m.params['ssbmod_frq_start'] = 43e6 - range_MHz*1e6 ## first time we choose a quite large domain to find the three dips (15)
    m.params['ssbmod_frq_stop'] = 43e6 + range_MHz*1e6
    m.params['pts'] = pts
    m.params['pulse_length'] = 2e-6
    m.params['ssbmod_amplitude'] = 0.01

    m.autoconfig()
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()

######################
### Run experiment ###
######################

if __name__ == '__main__':

    ######################
    ## Input parameters ##
    ######################
    safemode=True
    maximum_magnet_step_size = 250
    opimization_target = 5     # target difference in kHz (or when 0 magnet steps are required)

    only_fine =  False

        ### for the first coarse step
    init_range   = 8     #Common: 10 MHz
    init_pts     = 121    #Common: 121
    init_reps    = 500   #Common: 500

        ### for the remainder of the steps
    repeat_range = 4.5
    repeat_pts   = 81
    repeat_reps  = 1000

    if only_fine == True:
        init_range   = repeat_range     #Common: 10 MHz
        init_pts     = repeat_pts    #Common: 121
        init_reps    = repeat_reps   #Common: 500

    ###########
    ## Start ##
    ###########
    
    #create the data lists
  
     #turn on magnet stepping in Z
    # mom.set_mode('Z_axis', 'stp')

    # start: define B-field and position by first ESR measurement
    darkesr('magnet_Zpos_optimize_coarse', range_MHz=init_range, pts=init_pts, reps=init_reps)


   