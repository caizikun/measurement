''' 
Script to initialize one carbon via another using their hyperfine interaction


Gate scheme, assuming decent C1 control:
|C1 MBI| - |wait time: beating freq*2 = pi| - |M C1 X|(require X) - |C1 MBI|
'''

import numpy as np
import qt 
import analysis.lib.QEC.Tomo_dict as TD; reload(TD)
import msvcrt

### reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.DD_2 as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs; reload(funcs)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']
print SAMPLE_CFG
EL_TRANS = qt.exp_params['samples'][SAMPLE]['electron_transition']

def show_stopper():
    print '-----------------------------------'            
    print 'press q to stop measurement cleanly'
    print '-----------------------------------'
    qt.msleep(1)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        return True
    else: return False

def NuclearRamseyWithRemoteInitialization(name, 
        carbon_nr           = 5,               
        carbon_init_state   = 'up', 
        el_RO               = 'positive',
        detuning            = 0.5e3,
        el_state            = 0,
        beating_wait_time   = 1e-6,
        free_evolution_time  = 400e-6 + np.linspace(0., 6.0e-3,44),
        debug               = False):
    
    m = DD.NuclearRamseyWithRemoteInitialization(name)
    funcs.prepare(m)

    '''Set parameters'''
    m.params['C13_MBI_RO_state'] = 0
    m.params['C13_MBI_threshold_list'] = [1,1]

    m.params['beating_wait_time'] = beating_wait_time - ((m.params['C13_MBI_RO_duration']+m.params['SP_duration_after_C13'])*1e-6+20e-6)
    m.params['add_wait_gate'] = True #could be removed, does the beating wait gate and ramsey times

    m.params['reps_per_ROsequence'] = 250


    ### Sweep parameters
    m.params['pts'] = len(free_evolution_time)
    m.params['free_evolution_time'] = free_evolution_time
    m.params['sweep_name'] = 'free_evolution_time'
    m.params['sweep_pts']  = m.params['free_evolution_time']

    m.params['C'+str(carbon_nr)+'_freq_0']  += detuning
    m.params['C'+str(carbon_nr)+'_freq_1'+m.params['electron_transition']]  += detuning

    m.params['C_RO_phase'] =  np.ones(m.params['pts'] )*0  




    '''Derived and fixed parameters'''
    m.params['electron_readout_orientation'] = el_RO
    m.params['carbon_nr']                    = carbon_nr
    m.params['init_state']                   = carbon_init_state  
    m.params['electron_after_init'] = str(el_state)
    m.params['Nr_C13_init']       = 2
    m.params['Nr_MBE']            = 0
    m.params['Nr_parity_msmts']   = 0

    funcs.finish(m, upload =True, debug=debug)
    
if __name__ == '__main__':
    carbon = 2
    debug = False
    breakst = False
    beating_wait_time = 3.1e-3
    detuning = 1e3

    NuclearRamseyWithRemoteInitialization(SAMPLE_CFG+'Remote_ms' + EL_TRANS[-2:] +str(carbon),
     carbon_nr= carbon,
     beating_wait_time = beating_wait_time, 
     el_state = 1,
     debug = debug,
     detuning = detuning,
     free_evolution_time = 100e-6 + np.linspace(0.,4.0*1./detuning,25))#36
    
