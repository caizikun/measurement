"""
Script for a carbon Hahn echo sequence.
Initialization:
- Initializes in the +/- X state using C13 MBI
- Can set the electron state by setting the MBI succes condition

Hahn echo
- Sweeps same wait time between initialization and pi pulse and between pi pulse and RO
- Applies a pi pulse
"""
import numpy as np
import qt 

#reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.DD_2 as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def NuclearHahnWithInitialization(name, 
        carbon_nr             = 5,               
        carbon_init_state     = 'up', 
        el_RO                 = 'positive',
        debug                 = False,
        C13_init_method       = 'MBI', 
        C13_MBI_RO_state       = 0,
        el_after_init = 1):

    m = DD.NuclearHahnEchoWithInitialization(name)
    funcs.prepare(m)

    '''Set parameters'''

    ### Sweep parameters
    
    m.params['C13_MBI_RO_state']        = C13_MBI_RO_state     # Initalize in ms_=-1 to decouple nuclear spins
    m.params['C13_MBI_threshold_list']  = [1] 

    m.params['el_after_init'] = el_after_init 
        # m.params['C13_MBI_RO_duration']     = 100   #Chaning readout laser duration to ensure m_s=-1 
        # m.params['SP_duration_after_C13']   = 20
        # m.params['A_SP_amplitude_after_C13_MBI'] = 0*15e-9

    ### overwritten from msmnt params
           
    ####################################
    ### Option 1; Sweep waiting time ###
    ####################################
              
    ### 1B - Lab frame
    m.params['add_wait_gate'] = True

    if el_after_init == 0:
        m.params['reps_per_ROsequence'] = 200
        m.params['free_evolution_time'] = np.linspace(2e-3,60e-3,5) #np.arange(2e-3, 60e-3, 4e-3)
        m.params['pts'] = len(m.params['free_evolution_time'])
    if el_after_init == 1:
        # m.params['free_evolution_time'] = np.r_[4e-3,25e-3, 50e-3,100e-3, 200e-3, 350e-3, 600e-3, 1.]
        m.params['reps_per_ROsequence'] = 200
        m.params['free_evolution_time'] = np.linspace(2e-3,60e-3,5)
        m.params['pts'] = len(m.params['free_evolution_time'])
        
    

    m.params['C_RO_phase'] = m.params['pts']*['X']        

    m.params['sweep_name'] = 'Total_free_evolution_time'
    m.params['sweep_pts']  = m.params['free_evolution_time']*2
    
    ############################################
    ### Option 2; Sweep RO phase at set time ###
    ############################################
    # m.params['pts'] = 21
    # m.params['add_wait_gate'] = False
    # m.params['free_evolution_time'] = np.ones(m.params['pts'] )*360e-6
    # m.params['C_RO_phase'] = np.linspace(-20, 400,m.params['pts'])    

    # m.params['sweep_name'] = 'phase'
    # m.params['sweep_pts']  = m.params['C_RO_phase']

    '''Derived and fixed parameters'''

    m.params['C13_init_method'] = C13_init_method

    m.params['electron_readout_orientation'] = el_RO
    m.params['carbon_nr']                    = carbon_nr
    m.params['init_state']                   = carbon_init_state  

    m.params['Nr_C13_init']       = 1
    m.params['Nr_MBE']            = 0
    m.params['Nr_parity_msmts']   = 0

  
    funcs.finish(m, upload =True, debug=debug)


if __name__ == '__main__':


    # NuclearHahnWithInitialization(SAMPLE + '_C5_el1_positive', carbon_nr=5, el_RO= 'positive', C13_MBI_RO_state =1, debug=False)
    # NuclearHahnWithInitialization(SAMPLE + '_C5_el0_positive', carbon_nr=5, el_RO= 'positive', C13_MBI_RO_state =)
    # NuclearHahnWithInitialization(SAMPLE + '_C5_el0_negative', carbon_nr=5, el_RO= 'negative', C13_MBI_RO_state =0)


    # carbon_list = [1,2,5]
    # el_RO_list = ['positive','negative']
    # el_after_init_list = [1,0,1]
    # shutter_list = [True, False, False]

    carbon_list = [1]
    el_RO_list = ['positive']
    el_after_init_list = [0,1]

    for carbon in carbon_list:
        for ii, el_after_init in enumerate(el_after_init_list):
            for el_RO in el_RO_list:
                print '--------------------------------'
                print 'press q to stop measurement loop'
                print '--------------------------------'
                qt.msleep(5)
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                    break

                msmtstring =  '_C'+str(carbon)+'_el'+str(el_after_init)+'_'+el_RO
                #adwin.start_set_dio(dio_no=4,dio_val=0)
                #ssrocalibration(SAMPLE)
                #GreenAOM.set_power(10e-6)
                #adwin.start_set_dio(dio_no=4,dio_val=0)
                #optimiz0r.optimize(dims=['x','y','z','x','y'])
                #adwin.start_set_dio(dio_no=4,dio_val=0)
                # ssrocalibration(SAMPLE)
                # adwin.start_set_dio(dio_no=4,dio_val=0)
                # MBE(SAMPLE + '_C'+str(carbon)+'_el'+str(el_after_init)+'_'+ el_RO + '_MBI', el_RO= el_RO, carbon = carbon, carbon_init_list = [carbon],
                #                          carbon_init_methods = ['MBI'], carbon_init_thresholds = [1])
                NuclearHahnWithInitialization(SAMPLE + msmtstring, carbon_nr=carbon, el_RO= el_RO, C13_MBI_RO_state =0, el_after_init=el_after_init)

    # execfile(r'D:\measuring\measurement\scripts\QEC\NuclearT1_2.py')
