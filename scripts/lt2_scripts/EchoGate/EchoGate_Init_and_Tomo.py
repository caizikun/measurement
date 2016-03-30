"""
This script uses the Echo_gate to initialze a carbon along z and perform tomography afterwards.
AR & NK 2015
"""
import numpy as np
import qt 

#reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD
import measurement.scripts.mbi.mbi_funcs as funcs

reload(DD)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def Echo_gate(name, carbon_nr = 5,C13_init_state='up',e_RO='positive'):

    m = DD.EchoGateInit(name)
    funcs.prepare(m)

    '''set experimental parameters'''
    
    m.params['Carbon_nr'] = carbon_nr    
    
    m.params['reps_per_ROsequence'] = 1000
    m.params['C13_init_state']      = C13_init_state
    m.params['sweep_name']          = 'waiting time (us)'
    m.params['electron_readout_orientation']    = e_RO

    f0=m.params['C'+str(carbon_nr)+'_freq_0']
    f1=m.params['C'+str(carbon_nr)+'_freq_1'+m.params['electron_transition']]
    Waittime=2*(1/np.abs(f1-f0))/4. ### Half waittime multiplied by 2.
#     ### Sweep parameters
    # m.params['waiting_times']=[round(x,9) for x in np.linspace(Waittime-2e-6,HalfWaittime+2e-6,11)]
    m.params['waiting_times']=[31.1e-6]
    m.params['pts'] = len(m.params['waiting_times']) 

    m.params['sweep_pts'] = [round(x*10**6,9) for x in m.params['waiting_times']] ## rescale to microseconds!

    m.params['Nr_C13_init']     = 1
    m.params['Nr_MBE']          = 0
    m.params['Nr_parity_msmts'] = 0

    ### Bools

    m.params['use_Echo_gate_RO'] = True ### uses Ren gates for the carbon tomography.
    
    funcs.finish(m, upload =True, debug=False)


if __name__ == '__main__':
    Echo_gate(SAMPLE + 'positive_C3_init_tomo',carbon_nr = 3,C13_init_state='up')
    Echo_gate(SAMPLE + 'negative_C3_init_tomo',carbon_nr = 3,C13_init_state='up',e_RO='negative')
       






