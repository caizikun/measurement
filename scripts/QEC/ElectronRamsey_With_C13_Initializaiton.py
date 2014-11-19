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
    electron_RO='positive'):
    m = DD.ElectronRamseyWithNuclearInit(name)

    funcs.prepare(m)

    # m.params.from_dict(qt.cfgman.get('samples/'+SAMPLE))
    # m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    # m.params.from_dict(qt.cfgman['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    # m.params.from_dict(qt.cfgman['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    # m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO+espin'])
    # m.params['Ex_SP_amplitude']=0
    # m.params['AWG_to_adwin_ttl_trigger_duration']=2e-6
    # m.params['wait_for_AWG_done']=1
    # m.params['sequence_wait_time']=1

    pts = 3
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500

    #m.params['wait_for_AWG_done']=1
    #m.params['evolution_times'] = np.linspace(0,0.25*(pts-1)*1/m.params['N_HF_frq'],pts)

    m.params['wait_times'] = np.linspace(0,3000e-9,pts)

    # MW pulses
    m.params['detuning']  = 1.0e6

    m.params['pi2_phases1'] = np.ones(pts) * 0
    m.params['pi2_phases2'] = np.ones(pts) * 360 * m.params['wait_times'] * m.params['detuning']
    m.params['pi2_lengths'] = np.ones(pts) * 16e-9
    #m.params['pi2_lengths'] = np.linspace(15,30,pts)*1e-9

    # for the autoanalysis
    m.params['sweep_name'] = 'evolution time (ns)'
    m.params['sweep_pts'] = m.params['wait_times']/1e-9

    #define everything carbon related
    m.params['Addressed_Carbon']             = Addressed_Carbon
    m.params['C13_init_state']               = C_13_init_state
    m.params['electron_readout_orientation'] = electron_RO
    m.params['C13_MBI_RO_state']             = el_RO_result

    m.params['Nr_C13_init']                  = 1
        ### MBE settings
    m.params['Nr_MBE']              = 0
    m.params['Nr_parity_msmts']     = 0

    ##########
    # Overwrite certain params to test their influence on the sequence.
    m.params['C13_MBI_threshold_list']      = [0]
    m.params['C13_MBI_RO_duration']         = 100
    m.params['SP_duration_after_C13']       = 250
        

    funcs.finish(m, upload=True, debug=False)

if __name__ == '__main__':
    electronramsey_WithNuclearInit(SAMPLE+'_',
    Addressed_Carbon=1,
    C_13_init_state='up',
    el_RO_result=0,
    electron_RO='positive')