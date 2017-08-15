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
        fid_transition      = 'm1',
        free_evolution_time  = 400e-6 + np.linspace(0., 6.0e-3,44),
        dyn_dec_wait=False):
    
    m = DD.NuclearRamseyWithInitialization_v2(name)
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
    m.params['dyn_dec_wait']=dyn_dec_wait

    if ~dyn_dec_wait:    
        if fid_transition != '0':
            m.params['C'+str(carbon_nr)+'_freq_1'+fid_transition]  += detuning
        else:
            m.params['C'+str(carbon_nr)+'_freq_0']  += detuning
    elif dyn_dec_wait:
        if fid_transition == '0':
            print 'please select a transition to dyn decouple'
        if fid_transition != '0':
            m.params['C'+str(carbon_nr)+'_freq'+fid_transition]  += detuning

    m.params['fid_transition'] = fid_transition
    m.params['C_RO_phase'] =  np.ones(m.params['pts'] )*0  

    m.params['sweep_name'] = 'free_evolution_time'
    m.params['sweep_pts']  = m.params['free_evolution_time']


    ###########################################
    ## Option 2; Sweep RO phase at set time ###
    # ###########################################
    # if ~dyn_dec_wait:    
    #     if fid_transition != '0':
    #         m.params['C'+str(carbon_nr)+'_freq_1'+fid_transition]  += detuning
    #     else:
    #         m.params['C'+str(carbon_nr)+'_freq_0']  += detuning
    # elif dyn_dec_wait:
    #     if fid_transition == '0':
    #         print 'please select a transition to dyn decouple'
    #     if fid_transition != '0':
    #         m.params['C'+str(carbon_nr)+'_freq'+fid_transition]  += detuning
            

    # m.params['fid_transition'] = fid_transition

    # m.params['pts'] = 11
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

def NuclearRamseyWithInitialization_DD_cal(name, 
        carbon_nr           = 1,               
        carbon_init_state   = 'up', 
        el_RO               = 'positive',
        detuning            = 0.5e3,
        evo_time            = 400e-6,
        el_state            = 1,
        debug               = False,
        fid_transition      = 'm1',
        free_evolution_time  = np.linspace(4.5e3,10.5e3,20).astype(int)*1e-9):
    
    m = DD.NuclearRamseyWithInitialization_v2_DD(name)
    funcs.prepare(m)


    '''Set parameters'''

    ### Sweep parameters
    m.params['reps_per_ROsequence'] = 1000
    m.params['C13_MBI_RO_state'] = 0
    ### overwritten from msmnt params

    ####################################
    ### Option 1; Sweep waiting time ###
    ####################################

    ## '''1A - Rotating frame with no detuning'''
    m.params['add_wait_gate'] = True
    m.params['pts'] = len(free_evolution_time)
    m.params['free_evolution_time'] = free_evolution_time
    
    # m.params['free_evolution_time'] = 180e-6 + np.linspace(0e-6, 4*1./74e3,m.params['pts'])
    m.params['C'+str(carbon_nr)+'_freq'+fid_transition]=m.params['C'+str(carbon_nr)+'_freq'+fid_transition] 

    m.params['fid_transition'] = fid_transition
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


def qstop(sleep=3):
    print '--------------------------------'
    print 'press q to stop measurement loop'
    print '--------------------------------'
    qt.msleep(sleep)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        return True

if __name__ == '__main__':

    do_DD = True
    stopper = True
    
    for c in [1]:
        for detuning in [500]:
            for el in ['_m1','0','_p1']:
                qstop()
                NuclearRamseyWithInitialization_cal(SAMPLE_CFG+'_C'+str(c)+'_ms' + el + '_' + 'positive', 
                                carbon_nr           = c,               
                                carbon_init_state   = 'up', 
                                el_RO               = 'positive',
                                detuning            = detuning,
                                el_state            = el,
                                debug               = True,
                                free_evolution_time = 400e-6 + np.linspace(0.,3.0*1./detuning,1),
                               fid_transition = el )
    # # if ~do_DD:
    #     for c in [4]:
    #         #GreenAOM.set_power(80e-6)
    #         #optimiz0r.optimize(dims=['x','y','z'],cycles=1)
    #         for detuning in [20000]:
    #             for el_trans,el in [['_m1','0']]:
                    
    #                 qstop(sleep=3)
    #                 NuclearRamseyWithInitialization_cal(SAMPLE_CFG+'_C'+str(c)+'_ms' + el_trans + '_' + 'positive', 
    #                             carbon_nr           = c,               
    #                             carbon_init_state   = 'up', 
    #                             el_RO               = 'positive',
    #                             detuning            = detuning,
    #                             el_state            = el,
    #                             debug               = False,
    #                  xq           free_evolution_time = 400e-6 + np.linspace(0.,2.8*1./detuning,22),
    #                            fid_transition = el_trans,
    # #                            dyn_dec_wait = True)
    # # NuclearRamseyWithInitialization_DD_cal(SAMPLE + '_evo_times_1' + '_C' +str(1)+'_m1', 
    # #                         carbon_nr           = 1,               
    # #                         carbon_init_state   = 'up', 
    # #                         el_RO               = 'negative',
    # #                         debug               = True,
    # #                         el_state            = '0',
    # #                         free_evolution_time = np.linspace(4.5e3,12.5e3,5).astype(int)*1e-9,
    #                         fid_transition = '_m1')
    if do_DD:
        for c in [4]:
            # GreenAOM.turn_on()
            # optimiz0r.optimize(dims=['x','y','z'],cycles=1)
            for el_trans in ['_m1','_p1']:
                print '###########################'
                print'Doing DD'
                print '###########################'
                evolution_times1 = np.linspace(4.5e3,12.5e3,1).astype(int)*1e-9
                evolution_times2 = np.linspace(15e3,23e3,1).astype(int)*1e-9
                evolution_times3 = np.linspace(28e3,36e3,1).astype(int)*1e-9
            
   
                
                qstop()
                NuclearRamseyWithInitialization_DD_cal(SAMPLE + '_evo_times_1' + '_C' +str(c)+el_trans, 
                            carbon_nr           = c,               
                            carbon_init_state   = 'up', 
                            el_RO               = 'negative',
                            debug               = True,
                            el_state            = '0',
                            free_evolution_time = evolution_times1,
                            fid_transition = el_trans)
                qstop()
                NuclearRamseyWithInitialization_DD_cal(SAMPLE + '_evo_times_2' + '_C' +str(c)+el_trans, 
                            carbon_nr           = c,               
                            carbon_init_state   = 'up', 
                            el_RO               = 'negative',
                            debug               = True,
                            el_state            = '0',
                            free_evolution_time = evolution_times2,
                            fid_transition = el_trans)
                qstop()                        
                NuclearRamseyWithInitialization_DD_cal(SAMPLE + '_evo_times_3' + '_C' +str(c)+el_trans, 
                            carbon_nr           = c,               
                            carbon_init_state   = 'up', 
                            el_RO               = 'negative',
                            debug               = True,
                            el_state            = '0',
                            free_evolution_time = evolution_times3,
                            fid_transition = el_trans)


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

    