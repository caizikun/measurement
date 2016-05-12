import numpy as np
import qt
import msvcrt
from analysis.scripts.QEC import carbon_ramsey_analysis as cr 
reload(cr)

execfile(qt.reload_current_setup)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

import measurement.lib.measurement2.adwin_ssro.DD_2 as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs;reload(funcs)


def NuclearRamseyWithInitialization_cal(name, 
        carbon_nr           = 1,               
        carbon_init_state   = 'up', 
        el_RO               = 'positive',
        detuning            = 0.5e3,
        evo_time            = 400e-6,
        el_state            = 1,
        debug               = False,
        free_evolution_time  = 400e-6 + np.linspace(0., 6.0e-3,44)):
    
    m = DD.NuclearRamseyWithInitialization(name)
    funcs.prepare(m)


    '''Set parameters'''

    ### Sweep parameters
    m.params['reps_per_ROsequence'] = 250
    m.params['C13_MBI_RO_state'] = 0
    ### overwritten from msmnt params

    ####################################
    ### Option 1; Sweep waiting time ###
    ####################################

    ## '''1A - Rotating frame with detuning'''
    m.params['add_wait_gate'] = True
    m.params['pts'] = len(free_evolution_time)
    m.params['free_evolution_time'] = free_evolution_time

    # m.params['free_evolution_time'] = 180e-6 + np.linspace(0e-6, 4*1./74e3,m.params['pts'])


    m.params['C'+str(carbon_nr)+'_freq_0']  += detuning
    m.params['C'+str(carbon_nr)+'_freq_1'+m.params['electron_transition']]  += detuning
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
    m.params['carbon_nr']                    = carbon_nr
    m.params['init_state']                   = carbon_init_state  
    m.params['electron_after_init'] = str(el_state)
    m.params['Nr_C13_init']       = 1
    m.params['Nr_MBE']            = 0
    m.params['Nr_parity_msmts']   = 0

    funcs.finish(m, upload =True, debug=debug)


    # print '--------------------------------'
    # print 'press q to stop measurement loop'
    # print '--------------------------------'
    # qt.msleep(sleep)
    # if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
    #     return True

if __name__ == '__main__':



    ### parameter changes needed if init in ms=-1
    #qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['C13_MBI_RO_duration'] = 100
    #qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['SP_duration_after_C13'] = 100
    #qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['A_SP_amplitude_after_C13_MBI'] = 0*15e-9
  

    stopper = False

    detuning = 5000
    NuclearRamseyWithInitialization_cal(SAMPLE_CFG+'_C'+str(4)+'_ms' + str(1) + '_' + 'positive', 
                        carbon_nr           = 1,               
                        carbon_init_state   = 'up', 
                        el_RO               = 'positive',
                        detuning            = detuning,
                        el_state            = 1,
                        debug               = True,
                        free_evolution_time = 400e-6 + np.linspace(0.,2.8*1./detuning,1))
    



    ### more elaborate sweep for several carbons.



    # detuning_basic = 0.200e3
    # detuning_dict = {
    # '1' : detuning_basic*1.5,
    # '2' : detuning_basic*1.5,
    # '3' : detuning_basic*3.,
    # '5' : detuning_basic,
    # '6' : detuning_basic*4.}
    #
    # for carbon in [6,3,5,2,1]:
    #     FET = 400e-6 + np.linspace(0., 6.0*1./detuning_dict[str(carbon)],60)
    #     if stopper:
    #         break
    #     for el_state in [0,1]:
    #         if el_state == 0:
    #             qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['C13_MBI_RO_duration'] = 60
    #             qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['SP_duration_after_C13'] = 250
    #             qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['A_SP_amplitude_after_C13_MBI'] = 15e-9
    #         else:
    #             qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['C13_MBI_RO_duration'] = 100
    #             qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['SP_duration_after_C13'] = 100
    #             qt.exp_params['protocols']['111_1_sil18']['AdwinSSRO+C13']['A_SP_amplitude_after_C13_MBI'] = 0*15e-9
    #         if stopper:
    #             break
    #         GreenAOM.set_power(20e-6)
    #         adwin.start_set_dio(dio_no=4,dio_val=0)
    #         optimiz0r.optimize(dims=['x','y','z','x','y'], int_time=120)
    #         for el_RO in ['positive','negative']:
    #             if stopper:
    #                 break
    #             for ii in range(3):
    #                 if qstop(5):
    #                     stopper=True
    #                     break
    #                 NuclearRamseyWithInitialization_cal('C'+str(carbon)+'_ms' + str(el_state) + '_' + el_RO +'_part' + str(ii+1), 
    #                     carbon_nr           = carbon,               
    #                     carbon_init_state   = 'up', 
    #                     el_RO               = el_RO,
    #                     detuning            = detuning_dict[str(carbon)],
    #                     el_state            = el_state,
    #                     debug               = False,
    #                     free_evolution_time = FET[ii*20:(ii+1)*20])


    # NuclearRamseyWithInitialization_cal('C1_ms1_phasesweep_19ms', 
    #         carbon_nr           = 1,               
    #         carbon_init_state   = 'up', 
    #         el_RO               = 'positive',
    #         detuning            = 0.1e3,
    #         el_state            = 1,
    #         evo_time     = 19.2e-3,
    #         debug               = False)

    # NuclearRamseyWithInitialization_cal('C1_ms1_phasesweep_34ms', 
    #         carbon_nr           = 1,               
    #         carbon_init_state   = 'up', 
    #         el_RO               = 'positive',
    #         detuning            = 0.1e3,
    #         el_state            = 1,
    #         evo_time     = 34.6e-3,
    #         debug               = False)

    # NuclearRamseyWithInitialization_cal('C5_ms1_phasesweep_27ms', 
    #         carbon_nr           = 5,               
    #         carbon_init_state   = 'up', 
    #         el_RO               = 'positive',
    #         detuning            = 0.1e3,
    #         el_state            = 1,
    #         evo_time     = 26.9e-3,
    #         debug               = False)

    