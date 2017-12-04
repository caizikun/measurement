"""
Script which performs an electron ramsey experiment after initializing a carbon in the vicinity
"""

import qt
import numpy as np
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD
import measurement.scripts.mbi.mbi_funcs as funcs

reload(DD)



SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']


def electronramsey_WithNuclearInit(name,
    Addressed_Carbon=1,
    C_13_init_state='up',
    el_RO_result=0,
    electron_RO='positive',
    no_carbon_init = False):

    m = DD.ElectronRamseyWithNuclearInit(name)

    funcs.prepare(m)

    pts = 32
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000

    m.params['wait_times'] = np.linspace(0,300000e-9,pts)

    # MW pulses
    m.params['detuning']  = 0 #0.5e6

    m.params['pi2_phases1'] = np.ones(pts) * 0
    m.params['pi2_phases2'] = np.ones(pts) * 360 * m.params['wait_times'] * m.params['detuning']
    m.params['pi2_lengths'] = np.ones(pts) * 16e-9


    # for the autoanalysis
    m.params['sweep_name'] = 'evolution time (ns)'
    m.params['sweep_pts'] = m.params['wait_times']/1e-9

    #define everything carbon related
    m.params['Addressed_Carbon']             = Addressed_Carbon
    m.params['C13_init_state']               = C_13_init_state
    m.params['electron_readout_orientation'] = electron_RO
    m.params['C13_MBI_RO_state']             = el_RO_result


    m.params['no_carbon_init']=no_carbon_init # if True, this flag circumvents any carbon initialization. (does not work yet)

    
    #This part of the script does not yet work with the current adwin script. Causes adwin to crash....
    if no_carbon_init:
        m.params['Nr_C13_init']                  = 0
        m.params['C13_MBI_threshold_list']      = []
    else:
        m.params['Nr_C13_init']                  = 1
        m.params['C13_MBI_threshold_list']      = [0]


    ### MBE settings
    m.params['Nr_MBE']              = 0
    m.params['Nr_parity_msmts']     = 0

    ##########
    # Overwrite certain params to test their influence on the sequence. 
        

    funcs.finish(m, upload=True, debug=False)


if __name__ == '__main__':


    for ii in range(1):

        electronramsey_WithNuclearInit(SAMPLE+'_C1_up',
        Addressed_Carbon=1,
        C_13_init_state='up',
        el_RO_result=0,
        electron_RO='positive', no_carbon_init=False)

        electronramsey_WithNuclearInit(SAMPLE+'_C1_down',
        Addressed_Carbon=1,
        C_13_init_state='down',
        el_RO_result=0,
        electron_RO='positive', no_carbon_init=False)

        # electronramsey_WithNuclearInit(SAMPLE+'_C1_noInit',
        # Addressed_Carbon=1,
        # C_13_init_state='down',
        # el_RO_result=0,
        # electron_RO='positive', no_carbon_init=True)

        # ssrocalibration(SAMPLE_CFG)    

