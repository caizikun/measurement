import numpy as np
import qt
import msvcrt
from analysis.scripts.QEC import carbon_ramsey_analysis as cr 
reload(cr)

execfile(qt.reload_current_setup)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

import measurement.lib.measurement2.adwin_ssro.DD_2 as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs; reload(funcs)


def NuclearRamseyWithInitialization_cal(name, 
        carbon_list           = [1],               
        carbon_init_state   = ['up'], 
        el_RO               = 'positive',
        detuning            = 0.5e3,
        evo_time            = 400e-6,
        el_state            = 1,
        electron_after_init = 0,
        debug               = False,
        C13_MBI_nr          =  1,
        free_evolution_time  = 400e-6 + np.linspace(0., 6.0e-3,44)):
    
    m = DD.NuclearRamseyWithInitializationModified(name)
    funcs.prepare(m)

    ### Some conditions must be met
    if len(carbon_init_state) != len(carbon_list):
        print 'Number of init states and carbons does not match! Aborting'
        return

    '''Set parameters'''
    ### Sweep parameters
    m.params['reps_per_ROsequence'] = 250
    m.params['C13_MBI_RO_state'] = el_state

    # Build init list or change this to ['swap']*(len(carbons)-1) + ['MBI']
    C13_init_method = []
    for i, c in enumerate(carbon_list):
        if c == C13_MBI_nr:
            C13_init_method.append('MBI')
        else:
            C13_init_method.append('swap')
    m.params['C13_init_method'] = C13_init_method

    print 'MBI carbon: ' + str(C13_MBI_nr)
    print 'All carbons: ' +str(carbon_list)
    print 'm.params[C13_init_method]: ' + str(C13_init_method)

    ####################################
    ### Option 1; Sweep waiting time ###
    ####################################

    ## '''1A - Rotating frame with detuning'''
    m.params['add_wait_gate'] = False
    if m.params['add_wait_gate'] == False:
        print 'Warning: Add_wait_gate = False'
    m.params['pts'] = len(free_evolution_time)
    m.params['free_evolution_time'] = free_evolution_time

    # m.params['free_evolution_time'] = 180e-6 + np.linspace(0e-6, 4*1./74e3,m.params['pts'])

    m.params['C'+str(C13_MBI_nr)+'_freq_0']  += detuning
    m.params['C'+str(C13_MBI_nr)+'_freq_1'+m.params['electron_transition']]  += detuning
    m.params['C_RO_phase'] =  np.ones(m.params['pts'] )*0  

    m.params['sweep_name'] = 'free_evolution_time'
    m.params['sweep_pts']  = m.params['free_evolution_time']


    ############################################
    ### Option 2; Sweep RO phase at set time ###
    ############################################
    # m.params['pts'] = 21
    # m.params['add_wait_gate'] = False
    # m.params['free_evolution_time'] = np.ones(m.params['pts'] )*evo_time
    # m.params['C_RO_phase'] = np.linspace(-20, 400,m.params['pts'])    

    # m.params['sweep_name'] = 'phase'
    # m.params['sweep_pts']  = m.params['C_RO_phase']

    '''Derived and fixed parameters'''

    m.params['electron_readout_orientation'] = el_RO
    m.params['carbon_list']                    = carbon_list
    m.params['C13_MBI_nr']                   = C13_MBI_nr
    m.params['init_state']                   = carbon_init_state
    m.params['C13_MBI_threshold_list']       = [0]*(len(carbon_list)-1)+[1]

  
    m.params['el_after_init'] = electron_after_init
    m.params['Nr_C13_init']       = len(carbon_list)
    m.params['Nr_MBE']            = 0
    m.params['Nr_parity_msmts']   = 0

    funcs.finish(m, upload =True, debug=debug)


def qstop(sleep=2):
    print '--------------------------------'
    print 'press q to stop measurement loop'
    print '--------------------------------'
    qt.msleep(sleep)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        return True

if __name__ == '__main__':

    ### parameter changes needed if init in ms=-1
    #qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['C13_MBI_RO_duration'] = 100
    #qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['SP_duration_after_C13'] = 100
    #qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['A_SP_amplitude_after_C13_MBI'] = 0*15e-9

    stopper = False

    detuning = 50e3

    # MBI carbon and the other carbons you would like to initialize
    C13_MBI_nr = 8
    carbons = [3] + [C13_MBI_nr]
    # Note put the MBI carbon last

    carbon_init_state = ['up','up']
    # zeros followed by one or 0
    #el_state is readout state. el_after_init gives a pi pulse if applied
    el_after_init = [0,0]

    NuclearRamseyWithInitialization_cal(SAMPLE_CFG+'_C'+str(C13_MBI_nr)+'_ms' + str(0) + '_' + 'positive', 
                        carbon_list           = carbons,               
                        carbon_init_state   = carbon_init_state, 
                        el_RO               = 'positive',
                        detuning            = detuning,
                        el_state            = 0,
                        electron_after_init = el_after_init,
                        debug               = False,
                        C13_MBI_nr          = C13_MBI_nr,
                        free_evolution_time = 100e-6 + np.linspace(0.,7.0*1./detuning,27))
    