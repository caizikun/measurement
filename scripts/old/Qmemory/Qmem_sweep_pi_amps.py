"""
Initializes a carbon via SWAP into |Z>
Repeptitively goes through an LDE element.
Perofrms tomogrpahy on the carbon.
We vary the timing of the sequence in order to detect spurious resonances.

NK 2015
"""

import numpy as np
import qt 

### reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.scripts.Qmemory.QMemory as QM; reload(QM) ## get the measurement class
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



def QMem(name, carbon_list   = [5],               
        
        carbon_init_list        = [5],
        carbon_init_states      = ['up'], 
        carbon_init_methods     = ['MBI'], 
        carbon_init_thresholds  = [1],

        number_of_MBE_steps = 0,
        mbe_bases           = ['Y','Y'],
        MBE_threshold       = 1,

        el_RO               = 'positive',
        debug               = True,
        tomo_list			= ['X'],
        Repetitions         = 500):



    m = DD.QMemory_repumping(name)
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

    m.params['el_after_init']       = '0'

    ##################################
    ###         RO bases           ###
    ##################################

    ## not necessary
    
    ####################
    ### MBE settings ###
    ####################
    """these parameters will be used later on"""

    m.params['Nr_MBE']              = number_of_MBE_steps 
    m.params['MBE_bases']           = []# should be mbe_bases as soon as mbe is implemented
    m.params['MBE_threshold']       = MBE_threshold
    # m.params['2qb_logical_state']   = logic_state
    # m.params['2C_RO_trigger_duration'] = 150e-6
    
    ###################################
    ### Parity measurement settings ###
    ###################################

    m.params['Nr_parity_msmts']     = 0
    m.params['Parity_threshold']    = 1

    ###################################
    ###	   LDE element settings		###
    ###################################

    pts = 11

    f_larmor = (m.params['ms+1_cntr_frq']-m.params['zero_field_splitting'])*m.params['g_factor_C13']/m.params['g_factor']
    tau_larmor = round(1/f_larmor,9)

    m.params['repump_wait'] =  [tau_larmor]*pts # time between pi pulse and beginning of the repumper
    m.params['average_repump_time'] = pts*[190e-9] #this parameter has to be estimated from calivbration curves, goes into phase calculation
    m.params['fast_repump_repetitions'] = [150]*pts
    m.params['do_pi'] = True
    

    centre = 0.8346
    rng = 0.1
    m.params['pi_amps'] = np.linspace(centre-rng,centre+rng,pts)

    m.params['fast_repump_duration'] = pts*[3.5e-6] #how long the 'Zeno' beam is shined in.

    m.params['fast_repump_power'] = 700e-9


    ### For the Autoanalysis
    m.params['pts']                 = pts
    m.params['sweep_name']          = 'MW pulse amplitude' 
    m.params['sweep_pts']           =  m.params['pi_amps']
    
    ### RO params
    m.params['electron_readout_orientation'] = el_RO
    m.params['Tomo_bases'] = tomo_list

    funcs.finish(m, upload =True, debug=debug)


def show_stopper():
    print '-----------------------------------'            
    print 'press q to stop measurement cleanly'
    print '-----------------------------------'
    qt.msleep(1)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        return True
    else: return False

def optimize():
    GreenAOM.set_power(10e-6)
    counters.set_is_running(1)
    optimiz0r.optimize(dims = ['x','y','z','y','x'])

if __name__ == '__main__':

    # logic_state_list=['X','mX','Y','mY','Z','mZ'] doesn't do anything at the moment

    breakst=False    
    last_check=time.time()

    # QMem('C5_positive_tomo_Y',debug=True,tomo_list = ['Y'])
    n = 1
    if n == 1:
        for c in [2]:
            if breakst:
                break
            for tomo in ['X','Y']:
                optimize()
                if breakst:
                    break
                for ro in ['positive','negative']:
                    breakst = show_stopper()
                    if breakst:
                        break
                    QMem('sweep_pi_amps_'+ro+'_Tomo_'+tomo+'_C'+str(c),
                                                                        debug=False,
                                                                        tomo_list = [tomo], 
                                                                        el_RO = ro,
                                                                        carbon_list   = [c],               
                                                                        carbon_init_list        = [c])