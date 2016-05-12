'''
Test measurements such as non_local adwin communication etc.
'''

import numpy as np
import qt 
import purify_slave; reload(purify_slave)
import msvcrt
import sweep_purification
name = qt.exp_params['protocols']['current']

def show_stopper():
    print '-----------------------------------'            
    print 'press q to stop measurement cleanly'
    print '-----------------------------------'
    qt.msleep(1)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        return True
    else: return False

def test_adwin_communication(name,debug = False,upload_only=False):
    """
    Initializes the electron in ms = -1 
    and sweeps the repump duration at the beginning of LDE_1
    """

    m = purify_slave.purify_single_setup(name)
    sweep_purification.prepare(m)

    ### general params
    pts = 5
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500

    sweep_purification.turn_all_sequence_elements_off(m)

    ### sequence specific parameters
    m.params['is_two_setup_experiment'] = 1
    m.params['MW_before_LDE1'] = 0 # allows for init in -1 before LDE
    m.params['LDE_1_is_init']  = 1
    m.params['input_el_state'] = 'mZ'
    m.params['MW_during_LDE'] = 0
    m.joint_params['opt_pi_pulses'] = 0
    m.joint_params['LDE_attempts'] = 1

    # m.params['Hermite_pi_amp'] = 0
    ### prepare sweep
    m.params['do_general_sweep']    = True
    m.params['general_sweep_name'] = 'LDE_SP_duration'
    print 'sweeping the', m.params['general_sweep_name']
    m.params['general_sweep_pts'] = np.linspace(0.0,2.e-6,pts)
    m.params['sweep_name'] = m.params['general_sweep_name'] 
    m.params['sweep_pts'] = m.params['general_sweep_pts']*1e9

    ### upload and run

    sweep_purification.run_sweep(m,debug = debug,upload_only = upload_only)



if __name__ == '__main__':

    test_adwin_communication(name+'_test_adwin_communication',upload_only=False)