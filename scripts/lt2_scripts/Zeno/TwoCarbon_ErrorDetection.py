"""
This script runs the Zeno experiment for an adjustable evolution time.
It is compromised of 2 qubit Initialization via swap and 2 qubit MBE.
a specified number of parity measurements,
and finally tomography of a certain expectation value.

NK 2015
"""

########################################
#                                   ####
####      UNDER CONSTRUCTION!!!!!   ####
#                                   ####
########################################


import numpy as np
import qt 

### reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD; reload(DD)
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



def Zeno(name, carbon_list   = [1,2],               
        
        carbon_init_list        = [2,1],
        carbon_init_states      = 2*['up'], 
        carbon_init_methods     = 2*['swap'], 
        carbon_init_thresholds  = 2*[0],  

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

    m = DD.Zeno_ErrDetection(name)
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
    m.params['2qb_logical_state']   = logic_state
    m.params['2C_RO_trigger_duration'] = 150e-6
    
    ###################################
    ### Parity measurement settings ###
    ###################################

    m.params['Nr_parity_msmts']     = number_of_zeno_msmnts ### in this experiment we exchange zeno with actual parity measurements.
    m.params['Parity_threshold']    = parity_msmnts_threshold
    m.params['Nr_Zeno_parity_msmts']     = number_of_zeno_msmnts


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
    c1ms0 = has been added for measuring the 'dip'. Changes the frequency with which we keep track of C1 if the electron is in ms=0.

    Output:

    last_check = the time the last check up has been performed
    breakstatement = True if the measurement has been aborted. Otherwise False
    """

    Evotime_slicer = evotime_slicer # == number of datapoints taken at once

    EvoTime_arr=array_slicer(Evotime_slicer,evotime_arr)

    # eRO_list = ['positive']
    eRO_list = ['positive','negative']

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

            for eRO in eRO_list:
                Zeno(SAMPLE +eRO+'_logicState_'+logic_state+'_'+str(msmts)+'msmt_'+'_ROBasis_'+RO_bases_dict[logic_state][0]+RO_bases_dict[logic_state][1], 
                    el_RO= eRO,
                    logic_state=logic_state,
                    Tomo_bases = RO_bases_dict[logic_state],
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

                        ssrocalibration(SAMPLE_CFG)
                        GreenAOM.set_power(15e-6)
                        counters.set_is_running(1)
                        optimiz0r.optimize(dims = ['x','y','z'])
                        stools.turn_off_all_lt2_lasers()
                        ssrocalibration(SAMPLE_CFG)

                        Zeno(SAMPLE +'positive'+'_'+str(1)+'msmts_TESTSTATE_'+RO_bases_dict['mX'][0]+RO_bases_dict['mX'][1], 
                                        el_RO= 'positive',
                                        logic_state='mX',
                                        Tomo_bases = RO_bases_dict['mX'],
                                        free_evolution_time=[10e-3],
                                        number_of_zeno_msmnts = 1,
                                        debug=False,Repetitions=1000)

                        Zeno(SAMPLE +'negative'+'_'+str(1)+'msmts_TESTSTATE_'+RO_bases_dict['mX'][0]+RO_bases_dict['mX'][1], 
                                        el_RO= 'negative',
                                        logic_state='mX',
                                        Tomo_bases = RO_bases_dict['mX'],
                                        free_evolution_time=[10e-3],
                                        number_of_zeno_msmnts = 1,
                                        debug=False,Repetitions=1000)

                        last_check=time.time()
                else: print 'time to next check: ', 2*60*60-time.time()+last_check
    return breakstatement, last_check

def check_magneticField(breakstatement=False):
    if not breakstatement:
        DESR_msmt.darkesr('magnet_' +  'msm1', ms = 'msm',
        range_MHz=range_fine, pts=pts_fine, reps=reps_fine, freq=f0m_temp*1e9,# - N_hyperfine,
        pulse_length = 8e-6, ssbmod_amplitude = 0.0025)


        DESR_msmt.darkesr('magnet_' +  'msp1', ms = 'msp',
        range_MHz=range_fine, pts=pts_fine, reps=reps_fine, freq=f0p_temp*1e9,# + N_hyperfine,
        pulse_length = 8e-6, ssbmod_amplitude = 0.006)


if __name__ == '__main__':

    logic_state_list=['X','mX','Y','mY','Z','mZ']

    #gives the necessary RO basis when decoding to carbon 5

    RO_bases_dict={'X':['Z','Z'],
    'mX':['Z','Z'],
    'Y':['Z','Y'],
    'mY':['Z','Y'],
    'Z':['I','X'],
    'mZ':['I','X']}

    breakst=False    
    last_check=time.time()


    # Measure a single point for a single state.
    teststate='Z'
    EvoTime_arr=[5e-3]#,10e-3,20e-3]
    msmts=1
    for RO in ['positive','negative']:
        Zeno(SAMPLE +RO+'_'+str(msmts)+'msmts_TESTSTATE_'+RO_bases_dict[teststate][0]+RO_bases_dict[teststate][1], 
                        el_RO= RO,
                        logic_state=teststate,
                        Tomo_bases = RO_bases_dict[teststate],
                        free_evolution_time=EvoTime_arr,
                        number_of_zeno_msmnts =msmts,
                        debug=False,Repetitions=500)



    # # #########################
    # # # 0 measurements        #
    # # ######################### Minimum evo time 0 ms and 9 data points per run (logical X)
    
    # EvoTime_arr=np.r_[np.linspace(0e-3,50e-3,14),60e-3,70e-3,80e-3,100e-3]
    # breakst, last_check=takeZenocurve(9,EvoTime_arr,0,
    #                                         logic_state_list,
    #                                         RO_bases_dict,
    #                                         debug=False,
    #                                         breakstatement=breakst,
    #                                         last_check=last_check)




    # # #########################
    # # # 1 measurement         #
    # # ######################### Minimum evo time 3.5 and 6 data points per run

    # EvoTime_arr=np.r_[0,np.linspace(3.5e-3,60e-3,14),80e-3,100e-3]
    # breakst,last_check=takeZenocurve(6,EvoTime_arr,1,
    #                                     logic_state_list,
    #                                     RO_bases_dict,
    #                                     debug=False,
    #                                     breakstatement=breakst,
    #                                     last_check=last_check)

    # check_magneticField(breakstatement=breakst)
    # # # ######################## 5 data points per run
    # # # #   2 measurements     # min length 9.4
    # # # ######################## estimated duration parity duration: 6.3 ms 2015-01-27

    # EvoTime_arr=np.r_[0,np.linspace(9.4e-3,60e-3,14),80e-3,100e-3]
    # breakst,last_check=takeZenocurve(5,EvoTime_arr,2,
    #                                         logic_state_list,
    #                                         RO_bases_dict,
    #                                         debug=False,
    #                                         breakstatement=breakst,
    #                                         last_check=last_check)

    # check_magneticField(breakstatement=breakst)

    # #  ######################### 4 data points per run
    # #  # 3 measurements        # min length 12.5
    # #  ######################### estimated duration parity duration: 9.4 ms 2015-01-27
    
    # EvoTime_arr=np.r_[0,np.linspace(12.5e-3,60e-3,14),80e-3,100e-3]
    # breakst,last_check=takeZenocurve(4,EvoTime_arr,3,
    #                                         logic_state_list,
    #                                         RO_bases_dict,
    #                                         debug=False,
    #                                         breakstatement=breakst,
    #                                         last_check=last_check)



    # check_magneticField(breakstatement=breakst)


