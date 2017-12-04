import numpy as np
import qt
import msvcrt
from analysis.scripts.QEC import carbon_ramsey_analysis as cr 
reload(cr)

execfile(qt.reload_current_setup)

ins_adwin = qt.instruments['adwin']
ins_counters = qt.instruments['counters']
ins_aom = qt.instruments['GreenAOM']

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

import measurement.lib.measurement2.adwin_ssro.Simulate_dynamicaldecoupling as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs
# import measurement.scripts.QEC.carbon_calibration_routine as CCR

def NuclearRamseyWithInitialization_cal(name, 
        carbon_nr           = 8,               
        carbon_init_state   = 'up', 
        el_RO               = 'positive',
        detuning            = 0.5e3,
        evo_time            = 400e-6,
        el_state            = 1,
        debug               = True,
        free_evolution_time = 400e-6 + np.linspace(0., 6.0*1./0.5,44)):
    
    m = DD.NuclearRamseyWithInitialization_v2(name)
    # m = DD.ClusterRamseyWithInitialization(name)
    funcs.prepare(m)

    '''Set parameters'''

    ### Sweep parameters
    m.params['reps_per_ROsequence'] = 300
    m.params['C13_MBI_RO_state'] = el_state
    ### overwritten from msmnt params
           
    ####################################
    ### Option 1; Sweep waiting time ###
    ####################################
    
        # 1A - Rotating frame with detuning
    m.params['add_wait_gate'] = True
    m.params['pts'] = len(free_evolution_time)
    m.params['free_evolution_time'] = free_evolution_time

    # m.params['free_evolution_time'] = 180e-6 + np.linspace(0e-6, 4*1./74e3,m.params['pts'])
    

    m.params['C'+str(carbon_nr)+'_freq_0']  += detuning
    m.params['C'+str(carbon_nr)+'_freq_1'+m.params['electron_transition']]  += detuning
    m.params['C_RO_phase'] =  np.ones(m.params['pts'] )*0  

    m.params['sweep_name'] = 'free_volution_time'
    m.params['sweep_pts']  = m.params['free_evolution_time']


    ############################################
    ### Option 2; Sweep RO phase at set time ###
    ############################################
    # m.params['pts'] = 21
    # m.params['add_wait_gate'] = True
    # m.params['free_evolution_time'] = np.ones(m.params['pts'] )*evo_time
    # m.params['C_RO_phase'] = np.linspace(-20, 800,m.params['pts'])    

    # m.params['sweep_name'] = 'phase'
    # m.params['sweep_pts']  = m.params['C_RO_phase']

    '''Derived and fixed parameters'''
 
    m.params['electron_readout_orientation'] = el_RO
    m.params['carbon_nr']                    = carbon_nr
    m.params['init_state']                   = carbon_init_state  
    m.params['electron_after_init'] = str(el_state) #str(el_state)
    m.params['Nr_C13_init']       = 1
    m.params['Nr_MBE']            = 0
    m.params['Nr_parity_msmts']   = 0
    print m.params['MBI_threshold']


    funcs.finish(m, upload =True, debug=debug)


def qstop(sleep=2):
    print '--------------------------------'
    print 'press q to stop measurement loop'
    print '--------------------------------'
    qt.msleep(sleep)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        return True

if __name__ == '__main__':

    ## parameter changes needed if init in ms=-1
    # qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['C13_MBI_RO_duration'] = 100
    # qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['SP_duration_after_C13'] = 100
    # qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['A_SP_amplitude_after_C13_MBI'] = 0*15e-9

    detune = -469076.2
    el_state = 1
    el_RO = 'positive'

    NuclearRamseyWithInitialization_cal('C'+str(1)+'_ms' + str(el_state) + '_' + el_RO, 
        carbon_nr           = 1,               
        carbon_init_state   = 'up', 
        el_RO               = 'positive',
        detuning            = detune,#detuning_dict[str(1)],
        el_state            = el_state,
        debug               = True,
        free_evolution_time = 300e-6 + np.linspace(0e-6,8e-6,1))

