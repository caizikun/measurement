"""
Initializes a carbon via MBi into |x>
Repeptitively goes through an LDE element.
Perofrms tomogrpahy on the carbon.
We vary the power of the repumper at the end of the LDE.

NK 2015
"""

import numpy as np
import qt 

### reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs; reload(funcs)
import time
import msvcrt
import analysis.lib.Qmemory.CarbonDephasing as CD
reload (CD)

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



def QMem(name, carbon_list   = [5],               
        
        carbon_init_list        = [5],
        carbon_init_states      = ['up'], 
        carbon_init_methods     = ['MBI'], 
        carbon_init_thresholds  = [1],  

        number_of_MBE_steps = 0,
        mbe_bases           = ['Y','Y'],
        MBE_threshold       = 1,
        logic_state         = 'X',

        el_RO               = 'positive',
        debug               = True,
        tomo_list           = ['X'],
        Repetitions         = 500):



    m = DD.QMemory_repumping(name)
    funcs.prepare(m)



    #############

    m.params['C13_MBI_threshold_list'] = carbon_init_thresholds*len(carbon_init_list)

    ''' set experimental parameters '''

    m.params['reps_per_ROsequence'] = Repetitions

    ### Carbons to be used
    m.params['carbon_list']         = carbon_list

    ### Carbon Initialization settings 
    m.params['carbon_init_list']    = carbon_init_list
    m.params['init_method_list']    = carbon_init_methods*len(carbon_init_list)
    m.params['init_state_list']     = carbon_init_states*len(carbon_init_list)    
    m.params['Nr_C13_init']         = len(carbon_init_list)

    m.params['el_after_init']       = '0'

    ##################################
    ###         RO bases           ###
    ##################################

    ## not necessary
    
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

    m.params['Nr_parity_msmts']     = 0
    m.params['Parity_threshold']    = 1

    ###################################
    ###    LDE element settings     ###
    ###################################

    ### determine sweep parameters

    pts = 12
    step = 22

    minReps = 0 # minimum number of LDE reps
    maxReps = pts
    # maxReps =1701 # max number of LDe reps. this number is going to be rounded
    

    maxReps = minReps + step*pts


    f_larmor = (m.params['ms+1_cntr_frq']-m.params['zero_field_splitting'])*m.params['g_factor_C13']/m.params['g_factor']
    tau_larmor = round(1/f_larmor,9)

    # tau_larmor = 500e-9
    m.params['repump_wait'] = pts*[2e-6]#tau_larmor] #pts*[2e-6] # time between pi pulse and beginning of the repumper
    m.params['average_repump_time'] = pts*[180e-9] #this parameter has to be estimated from calibration curves, goes into phase calculation
    m.params['fast_repump_repetitions'] = np.arange(minReps,maxReps,step)


    m.params['fast_repump_duration'] = pts*[3.5e-6] #how long the beam is shined in.

    m.params['fast_repump_power'] = 900e-9
    m.params['do_pi'] = False ### does a regular pi pulse
    m.params['do_BB1'] = True ### does a BB1 pi pulse NOTE: both bools should not be true at the same time.
    m.params['pi_amps'] = pts*[m.params['fast_pi_amp']]


    ### For the Autoanalysis
    m.params['pts']                 = pts
    m.params['sweep_name']          = 'repump repetitions' 
    m.params['sweep_pts']           =  m.params['fast_repump_repetitions']
    
    ### RO params
    m.params['electron_readout_orientation'] = el_RO
    m.params['Tomo_bases'] = tomo_list


    #### rmeove any phase calibration from the msmt params
    m.params['Carbon_LDE_phase_correction_list'] = np.array([0.0]*10)
    m.params['Carbon_LDE_init_phase_correction_list'] = np.array([0.0]*10)

    funcs.finish(m, upload =True, debug=debug)


def show_stopper():
    print '-----------------------------------'            
    print 'press q to stop measurement cleanly'
    print '-----------------------------------'
    qt.msleep(1)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        return True
    else: return False

def optimize(breakst):
    if not breakst:
        GreenAOM.set_power(15e-6)
        counters.set_is_running(1)
        optimiz0r.optimize(dims = ['x','y','z','y','x'])

if __name__ == '__main__':

    last_check = time.time() ### time reference for long mesaurement loops

    breakst=False    
    debug = False


    #########################
    ### single qubit loop ###
    #########################

    # freq_dict = {'1': 1/20., '2':1/30.,'3':1/30.,'5':1/30.,'6':1/30.}

    c_list = [2]
    n = 0### turn measurement on/off
    if n == 1:
        for c in c_list:
            if breakst:
                break
            for tomo in ['X']:
                optimize(breakst or debug)
                if breakst:
                    break
                for ro in ['positive','negative']:
                    breakst = show_stopper()
                    if breakst:
                        break
                    QMem('NoOf_Repetitions_'+ro+'_Tomo_X_C'+str(c),
                                                                        debug=debug,
                                                                        tomo_list = [tomo], 
                                                                        el_RO = ro,
                                                                        carbon_list   = [c],               
                                                                        carbon_init_list        = [c],
                                                                        carbon_init_thresholds  = [1],
                                                                        carbon_init_methods     = ['MBI'])

    ### analysis
    if not debug and not breakst:
        for c in c_list:
            fit_result = CD.Osci_period(carbon = str(c),fit_results = True,auto_analysis = True,fixed = [],show_guess = True,freq = 0.000,decay=89)
            try:
                print 'Phsaeshift for carbon {}: {} +- {:2.2}'.format(c,fit_result['params_dict']['f']*180/0.5,180*fit_result['error_dict']['f']/0.5)
                print 'Phase shift after 1 repetition {} +- {:2.2}'.format(fit_result['params_dict']['phi'],fit_result['error_dict']['phi'])
            except KeyError:
                print 'frequency could not be determined'
