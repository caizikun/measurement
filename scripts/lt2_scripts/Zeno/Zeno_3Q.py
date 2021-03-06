"""
This script runs the Zeno experiment for an adjustable evolution time.
It is compromised of 2 qubit Initialization via swap and 2 qubit MBE.
a specified number of parity measurements,
and finally tomography of a certain expectation value.

NK 2015
"""

import numpy as np
import qt 

### reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.scripts.lt2_scripts.Zeno.Zeno as Zen; reload(Zen)
import measurement.scripts.mbi.mbi_funcs as funcs; reload(funcs)
import time
import msvcrt

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']


#### Parameters and imports for DESR ####
from measurement.scripts.QEC.magnet import DESR_msmt; reload(DESR_msmt)
from analysis.lib.fitting import dark_esr_auto_analysis; reload(dark_esr_auto_analysis)

nm_per_step = qt.exp_params['magnet']['nm_per_step']
f0p_temp = qt.exp_params['samples'][SAMPLE]['ms+1_cntr_frq']*1e-9
f0m_temp = qt.exp_params['samples'][SAMPLE]['ms-1_cntr_frq']*1e-9
N_hyperfine = qt.exp_params['samples'][SAMPLE]['N_HF_frq']
ZFS = qt.exp_params['samples'][SAMPLE]['zero_field_splitting']

range_fine  = 0.40
pts_fine    = 51
reps_fine   = 1500 #1000
###############



def Zeno(name, carbon_list   = [1,2,5],               
        
        carbon_init_list        = [5,2,1],
        carbon_init_states      = 3*['up'],
        carbon_init_methods     = 3*['swap'],
        carbon_init_thresholds  = 3*[0],

        number_of_MBE_steps = 1,
        logic_state         ='X',
        mbe_bases           = ['Y','Y'],
        MBE_threshold       = 1,

        number_of_zeno_msmnts = 0,
        parity_msmnts_threshold = 1, 

        free_evolution_time = [0e-6],

        el_RO               = 'positive',
        debug               = False,
        Tomo_bases          = [],
        Repetitions         = 400):

    m = Zen.Zeno_ThreeQB(name)
    funcs.prepare(m)



    #############

    m.params['C13_MBI_threshold_list'] = carbon_init_thresholds

    ''' set experimental parameters '''

    m.params['reps_per_ROsequence'] = Repetitions

    ### Carbons to be used
    m.params['carbon_list']         = carbon_list

    ### Carbon Initialization settings 
    m.params['carbon_init_list']    = carbon_init_list
    m.params['init_method_list']    = carbon_init_methods    
    m.params['init_state_list']     = carbon_init_states    
    m.params['Nr_C13_init']         = len(carbon_init_list)

    ##################################
    ###         RO bases           ###
    ##################################

    m.params['Tomography Bases'] = Tomo_bases 
    
    ####################
    ### MBE settings ###
    ####################

    m.params['Nr_MBE']              = number_of_MBE_steps 
    m.params['MBE_bases']           = mbe_bases
    m.params['MBE_threshold']       = MBE_threshold
    m.params['3qb_state']           = logic_state
    m.params['2C_RO_trigger_duration'] = 150e-6
    
    ###################################
    ### Parity measurement settings ###
    ###################################

    m.params['Nr_parity_msmts']     = 0
    m.params['Parity_threshold']    = parity_msmnts_threshold
    m.params['Nr_Zeno_parity_msmts']     = number_of_zeno_msmnts
    m.params['Zeno_SP_A_power'] = 250e-9
    m.params['Repump_duration']= 30e-6 #how long the 'Zeno' beam is shined in.

    m.params['echo_like']=False # this is a bool to set the delay inbetween measurements.

    ### Derive other parameters
    m.params['free_evolution_time'] = free_evolution_time
    m.params['pts']                 = len(m.params['free_evolution_time'])
    m.params['sweep_name']          = 'free_evolution_time' 
    m.params['sweep_pts']           = [round(x*1e3,3) for x in m.params['free_evolution_time']]
    
    ### RO params
    m.params['electron_readout_orientation'] = el_RO



    ####################################
    ### waiting time and measurement ###
    ####################################
       
    m.params['free_evolution_time']=free_evolution_time


    funcs.finish(m, upload =True, debug=debug)

def array_slicer(Evotime_slicer,evotime_arr):
    """
    this function is used to slice up the free evolution times into a list of lists
    such that the sequence can be loaded into the AWG 
    """

    no_of_cycles=int(np.floor(len(evotime_arr)/Evotime_slicer))
    returnEvos = []
    for i in range(no_of_cycles):
        returnEvos.append(evotime_arr[i*Evotime_slicer:(i+1)*Evotime_slicer])

    if len(evotime_arr)%Evotime_slicer !=0 : #only add the remaining array if there are some elements left to add.
        (returnEvos.append(evotime_arr[no_of_cycles*Evotime_slicer:]))

    return returnEvos

def takeZenocurve(evotime_slicer,evotime_arr,msmts,logic_state_list,RO_bases_dict,debug=False,breakstatement=False,last_check=time.time()):
    ### this function runs a measurement loop  
    ### after two hours of measurement we run check ups: SSRO + optimize the NV position + generation of Teststates.
    ### Parameters:
    """
    Input:
    evotime_slicer = tells the function array slicer the maximum length of sweep points (evolution times)
    evotim_arr = all evolution times we sweep over.
    msmts = number of zeno measurements
    logic_state_list = a list of strings, i.e. logic input carbon_init_states
    RO_bases_dict = is a dictionary which contains a read-out basis for each logical input state (key)
    breakstatement = if True then we don't do anything
    last_check = the time when the check of the magnetic field has been performed
    
    Output:

    last_check = the time the last check up has been performed
    breakstatement = True if the measurement has been aborted. Otherwise False
    """

    Evotime_slicer = evotime_slicer # == number of datapoints taken at once

    EvoTime_arr=array_slicer(Evotime_slicer,evotime_arr)

    eRO_list = ['positive','negative']

    last_magnet_check = last_check

    for logic_state in logic_state_list:

        if breakstatement:
            break

        for EvoTime in EvoTime_arr:
            print EvoTime
            print '-----------------------------------'            
            print 'press q to stop measurement cleanly'
            print '-----------------------------------'
            qt.msleep(2)
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                breakstatement=True
                break
            for RO_base in RO_bases_dict[logic_state]:
                print '-----------------------------------'            
                print 'press q to stop measurement cleanly'
                print '-----------------------------------'
                qt.msleep(1)
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                    breakstatement=True
                    break
                for eRO in eRO_list:
                    print '-----------------------------------'            
                    print 'press q to stop measurement cleanly'
                    print '-----------------------------------'
                    qt.msleep(1)
                    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                        breakstatement=True
                        break


                    Zeno(SAMPLE +eRO+'_logicState_'+logic_state+'_'+str(msmts)+'msmt_'+'_ROBasis_'+RO_base[0]+RO_base[1]+RO_base[2], 
                        el_RO= eRO,
                        logic_state=logic_state,
                        Tomo_bases = RO_base,
                        free_evolution_time=EvoTime,
                        number_of_zeno_msmnts = msmts,
                        debug=debug)

                    if time.time()-last_check>2*60*60: #perform a consistency check every two hours
                        if not debug and not breakstatement:

                            print '-----------------------------------'            
                            print 'press q to stop measurement cleanly'
                            print '-----------------------------------'
                            qt.msleep(2)
                            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                                breakstatement=True
                                break

                            # execfile(r'D:\measuring\measurement\scripts\QEC\QEC_ssro_calibration.py')
                            GreenAOM.set_power(15e-6)
                            counters.set_is_running(1)
                            optimiz0r.optimize(dims = ['x','y','z'])
                            optimiz0r.optimize(dims = ['z','y','x'])
                            stools.turn_off_all_lt2_lasers()
                            # execfile(r'D:\measuring\measurement\scripts\QEC\QEC_ssro_calibration.py')

                            Zeno(SAMPLE +'positive'+'_'+str(1)+'msmts_TESTSTATE_'+'XXX', 
                                            el_RO= 'positive',
                                            logic_state='00',
                                            Tomo_bases = ['X','X','X'],
                                            free_evolution_time=[10e-3],
                                            number_of_zeno_msmnts = 1,
                                            debug=False,Repetitions=1000)

                            Zeno(SAMPLE +'negative'+'_'+str(1)+'msmts_TESTSTATE_'+'XXX', 
                                            el_RO= 'negative',
                                            logic_state='00',
                                            Tomo_bases = ['X','X','X'],
                                            free_evolution_time=[10e-3],
                                            number_of_zeno_msmnts = 1,
                                            debug=False,Repetitions=1000)

                            last_check=time.time()

                    ### check the magnetic field every hour.
                    elif time.time()-last_magnet_check>1*60*60 and not breakstatement and not debug:
                        check_magneticField()
                        last_magnet_check = time.time()

                else: print 'time to next check: ', 2*60*60-time.time()+last_check
    return breakstatement, last_check

def check_magneticField(breakstatement=False):
    if not breakstatement:
        DESR_msmt.darkesr('magnet_' +  'msm1', ms = 'msm',
        range_MHz=range_fine, pts=pts_fine, reps=reps_fine, freq=f0m_temp*1e9,# - N_hyperfine,
        pulse_length = 8e-6, ssbmod_amplitude = 0.0025,mw_switch = True)




if __name__ == '__main__':



    logic_state_list=['00','00p10','00p11']


    logic_state_list=['00p10']


    ### preservation of the XXX subspace.
    ### read-out the expectation values for the two logical qubits. This is a dictionary of lists. 
    ### We then loop over the RO-bases list according to the key.
    ### states: 00 --> |X1,X2,X3>
    ###         00p10 --> |X1>(|X2,X3>+ |-X2,-X3>)
    ###         00p11 --> (|X1,X2> + |-X1,-X2>)|X3>
    ### for the entangled state you want to read-out three expectation values to map the two qubit state fidelity out.


    ### take the expectation values for he fidelity with the full two qubit state.
    RO_bases_dict={'00':[['X','X','I'],['X','I','X'],['I','X','X'],['X','X','X']],
        '00p10':[['I','Z','Z'],['I','Y','Y'],['I','X','X'],['X','X','X']],
        '00p11':[['X','X','I'],['Y','Y','I'],['Z','Z','I'],['X','X','X']]}

    
    ### take the additional expectation values for he fidelity with the full two qubit state.
    # RO_bases_dict={'00':[['X','X','I']],
    #     '00p10':[['I','Y','Y']],
    #     '00p11':[['X','X','I'],['Y','Y','I'],['Z','Z','I'],['X','X','X']]}


    breakst=False    
    last_check=time.time()


    # Measure a single point for a single state.
    teststate='00p11'
    msmts = 0
    EvoTime_arr = [0e-3]
    for RO in ['positive','negative']:
        Zeno(SAMPLE +RO+'_'+str(msmts)+'msmts_TESTSTATE_XXX', 
                                        el_RO= RO,
                                        logic_state=teststate,
                                        Tomo_bases = ['X','X','X'],
                                        free_evolution_time=EvoTime_arr,
                                        number_of_zeno_msmnts =msmts,
                                        debug=False,Repetitions=700)
    # EvoTime_arr=[0e-3]
    # msmts=1
    # for state in logic_state_list:
    #     print state
    #     if breakst:
    #         break
    #     for Basis in RO_bases_dict[state]:
    #         print Basis
    #         for RO in ['positive','negative']:
    #             print '-----------------------------------'            
    #             print 'press q to stop measurement cleanly'
    #             print '-----------------------------------'
    #             qt.msleep(1)
    #             if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
    #                 breakst=True
    #                 break
    #             Zeno(SAMPLE +RO+'_'+str(msmts)+'msmts_' + state + '_'+Basis[0]+Basis[1]+Basis[2], 
    #                             el_RO= RO,
    #                             logic_state=state,
    #                             Tomo_bases = Basis,
    #                             free_evolution_time=EvoTime_arr,
    #                             number_of_zeno_msmnts =msmts,
    #                             debug=False,Repetitions=500)
    #             GreenAOM.set_power(15e-6)
    #             counters.set_is_running(1)
    #             optimiz0r.optimize(dims = ['x','y','z'])



    #########################
    # 1 measurement         #
    ######################### Minimum evo time 5.3 and 4 data points per run

    # EvoTime_arr=np.r_[0,np.linspace(5.3e-3,35e-3,14),40e-3,50e-3,60e-3,70e-3,80e-3,100e-3]
    # breakst,last_check=takeZenocurve(4,EvoTime_arr,1,
    #                                     logic_state_list,
    #                                     RO_bases_dict,
    #                                     debug=False,
    #                                     breakstatement=breakst,
    #                                     last_check=last_check)



    #########################
    # 4 measurements        #
    ######################### Minimum evo time 22.5 ms and 2 data points per run
    # EvoTime_arr=np.r_[0,np.linspace(22.9e-3,45e-3,9),50e-3,60e-3,70e-3,80e-3,90e-3]
    
    ### testing purposes
    # RO_bases_dict={'00p10':[['I','Z','Z'],['I','Y','Y']]}
    # EvoTime_arr = [0,22.9e-3]


    # breakst,last_check=takeZenocurve(2,EvoTime_arr,4,
    #                                    logic_state_list,
    #                                    RO_bases_dict,
    #                                    debug=False,
    #                                    breakstatement=breakst,
    #                                    last_check=last_check)

    #########################
    # 2 measurement         #
    ######################### Minimum evo time 12.5 and 3 data points per run


    # EvoTime_arr=np.r_[0,np.linspace(12.9e-3,35e-3,9),40e-3,50e-3,60e-3,70e-3,80e-3]
    # breakst,last_check=takeZenocurve(3,EvoTime_arr,2,
    #                                     logic_state_list,
    #                                     RO_bases_dict,
    #                                     debug=False,
    #                                     breakstatement=breakst,
    #                                     last_check=last_check)




    #########################
    # 0 measurements        #
    ######################### Minimum evo time 0 ms and 7 data points per run (logical X)
    
    # EvoTime_arr=np.r_[np.linspace(0e-3,30e-3,14),40e-3,50e-3,60e-3,70e-3]
    # breakst, last_check=takeZenocurve(7,EvoTime_arr,0,
    #                                         logic_state_list,
    #                                         RO_bases_dict,
    #                                         debug=False,
    #                                         breakstatement=breakst,
    #                                         last_check=last_check)



