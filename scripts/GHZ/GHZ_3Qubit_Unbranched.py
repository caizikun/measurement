'This script runs the GHZ measurement, without branching out after each measurement and the corresponding result'


import numpy as np
import qt

### reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs; reload(funcs)
import analysis.lib.QEC.Tomo_dict as TD; reload(TD)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']


# import the DESR measurement, DESR fit, magnet tools and master of magnet
from measurement.scripts.QEC.magnet import DESR_msmt; reload(DESR_msmt)
from analysis.lib.fitting import dark_esr_auto_analysis; reload(dark_esr_auto_analysis)
from measurement.lib.tools import magnet_tools as mt; reload(mt)
mom = qt.instruments['master_of_magnet']; reload(mt)
ins_adwin = qt.instruments['adwin']
ins_counters = qt.instruments['counters']
ins_aom = qt.instruments['GreenAOM']

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro

import msvcrt

### reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs; reload(funcs)
import analysis.lib.QEC.Tomo_dict as TD; reload(TD)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro

def ssrocalibration(name,RO_power=None,SSRO_duration=None):
    m = ssro.AdwinSSRO('SSROCalibration_'+name)
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])

    if RO_power != None:
        m.params['Ex_RO_amplitude'] = RO_power
    if SSRO_duration != None:
        m.params['SSRO_duration'] = SSRO_duration

    # ms = 0 calibration
    m.params['Ex_SP_amplitude'] = 0
    m.run()
    m.save('ms0')

    # ms = 1 calibration
    m.params['SP_duration']     = 500
    m.params['A_SP_amplitude']  = 0.
    m.params['Ex_SP_amplitude'] = 15e-9
    m.run()
    m.save('ms1')

    m.finish()

def GHZ(name, 
    carbon_list = [1,2,5],
    xyy_list = ['X','Y','Y'],
    yxy_list = ['Y','X','Y'],
    yyx_list = ['Y','Y','X'],
    tomo_list = ['X','X','X'],
    feedforward = False,
    debug = False,
    parity_orientations = ['positive','positive','positive','positive'],
    final_phases = [0,0,0],
    initialize_carbons = False,
    init_carbon_list = [1,2,5],
    init_carbon_states = 3*['up'],
    init_carbon_methods = 3*['swap'],
    init_carbon_thresholds = [0,0,0],
    tomo_carbons = [1,2,5],
    electron_RO = False,
    mmtA_electron_RO = False,
    ):

    m = DD.GHZ_ThreeQB_Unbranched(name)
    funcs.prepare(m)

    m.params['reps_per_ROsequence'] = 3000
    m.params['pts'] = 1

    ##### Carbon initializations params
    m.params['initialize_carbons'] = initialize_carbons
    if initialize_carbons:
        m.params['Nr_C13_init'] = len(init_carbon_list)
        m.params['carbon_init_list']        = init_carbon_list
        m.params['init_state_list']         = init_carbon_states
        m.params['init_method_list']        = init_carbon_methods
        m.params['C13_MBI_threshold_list']  = init_carbon_thresholds
    else:
        m.params['Nr_C13_init'] = 0
        m.params['carbon_init_list']        = []
        m.params['init_state_list']         = []
        m.params['init_method_list']        = []
        m.params['C13_MBI_threshold_list']  = []
    

    m.params['Nr_MBE']              = 0 
    #m.params['MBE_bases']           = []
    #m.params['MBE_threshold']       = 1
    m.params['Nr_parity_msmts']     = 3
    m.params['add_wait_gate'] = False
    m.params['wait_in_msm1']  = False

    ##### general RO params
    m.params['RO_trigger_duration'] = 150e-6
    m.params['Tomo_RO_trigger_duration'] = 10e-6

    ###### RO xyy params
    m.params['Parity_xyy_do_RO_electron'] = mmtA_electron_RO
    if mmtA_electron_RO:
        m.params['Parity_xyy_do_init_pi2'] = False
        m.params['Invert_Parity_xyy_carbon_list'] = carbon_list
        m.params['Invert_Parity_xyy_RO_list'] = ['I','I','X']
        m.params['Parity_xyy_carbon_list'] = []
        m.params['Parity_xyy_RO_list'] = []
    else:
        m.params['Parity_xyy_do_init_pi2'] = True
        m.params['Invert_Parity_xyy_carbon_list'] = carbon_list
        m.params['Invert_Parity_xyy_RO_list'] = xyy_list
        m.params['Parity_xyy_carbon_list'] = carbon_list
        m.params['Parity_xyy_RO_list'] = xyy_list
    m.params['Parity_xyy_RO_orientation'] = parity_orientations[0]

    m.params['Invert_xyy_do_final_pi2'] = False
    m.params['Parity_yxy_do_init_pi2'] = False
    m.params['Parity_yxy_carbon_list'] = carbon_list
    m.params['Parity_yxy_RO_list'] = yxy_list
    m.params['Parity_yxy_RO_orientation'] = parity_orientations[1]

    ###### invert yxy and RO yyx params
    m.params['Invert_yxy_do_final_pi2'] = False
    m.params['Parity_yyx_do_init_pi2'] = False
    m.params['Parity_yyx_carbon_list'] = carbon_list
    m.params['Parity_yyx_RO_list'] = yyx_list
    m.params['Parity_yyx_RO_orientation'] = parity_orientations[2]
    
    ###### invert yyx and RO TOMO params
    m.params['RO_electron'] = electron_RO

    m.params['Invert_yyx_do_final_pi2'] = False
    m.params['Tomo_do_init_pi2'] = False

    if electron_RO:
        m.params['Invert_yyx_do_final_pi2'] = True
        m.params['Tomo_do_init_pi2'] = False

    for s in tomo_list:
        if 'Z' in s:
            print 'tomography contains Z; doing pi/2 between invertRO and RO'
            m.params['Invert_yyx_do_final_pi2'] = True
            m.params['Tomo_do_init_pi2'] = True
    m.params['Tomo_carbon_list'] = tomo_carbons
    m.params['Tomo_RO_orientation'] = parity_orientations[3]
    m.params['final_phases'] = final_phases

    m.params['Tomo_RO_list'] = tomo_list

    m.params['flip_000'] = False
    m.params['flip_001'] = False
    m.params['flip_010'] = False
    m.params['flip_011'] = False
    m.params['flip_100'] = False
    m.params['flip_101'] = False
    m.params['flip_110'] = False
    m.params['flip_111'] = False

    if feedforward:
        flip_states = feedforward_flips(tomo_list)
        print('flipping before orientation correction:')
        print(flip_states)

        ###correct for the orientations when determining which outcomes have to be flipped.
        for j in np.arange(3):
            if parity_orientations[j] == 'negative':
                for k,state in enumerate(flip_states):
                    outcome = state[j]
                    outcome_n = np.mod(int(state[j])+1,2)
                    state = state[:j] + str(outcome_n) + state[(j+1):]
                    flip_states[k] = state
        print('flipping after orientation correction:')
        print(flip_states)

        if '000' in flip_states:
            m.params['flip_000'] = True
        if '001' in flip_states:
            m.params['flip_001'] = True 
        if '010' in flip_states:
            m.params['flip_010'] = True
        if '011' in flip_states:
            m.params['flip_011'] = True
        if '100' in flip_states:
            m.params['flip_100'] = True
        if '101' in flip_states:
            m.params['flip_101'] = True
        if '110' in flip_states:
            m.params['flip_110'] = True
        if '111' in flip_states:
            m.params['flip_111'] = True

    funcs.finish(m, upload =True, debug=debug)

if __name__ == '__main__':


    test_unbranched_GHZ=False
    test_unbranched_GHZ_with_init=True

    orientations_list=[
        ['positive','positive','positive','positive'],
        ['positive','positive','positive','negative'],
        ['positive','positive','negative','positive'],
        ['positive','positive','negative','negative'],
        ['positive','negative','positive','positive'],
        ['positive','negative','positive','negative'],
        ['positive','negative','negative','positive'],
        ['positive','negative','negative','negative'],
        ['negative','positive','positive','positive'],
        ['negative','positive','positive','negative'],
        ['negative','positive','negative','positive'],
        ['negative','positive','negative','negative'],
        ['negative','negative','positive','positive'],
        ['negative','negative','positive','negative'],
        ['negative','negative','negative','positive'],
        ['negative','negative','negative','negative']
        ]

    fast_orientations_list=[
        ['positive','positive','positive','positive'],
        ['negative','negative','negative','negative']
        ]

    debug_orientations_list=[
        ['positive','positive'],
        ['positive','negative'],
        ['negative','positive'],
        ['negative','negative'],
        ]        

    tomo_lists = [
        ['X','X','X'],
        ['Z','Z','I'],
        ['Z','I','Z'],
        ['I','Z','Z'],
        ['X','Y','Y'],
        ['Y','X','Y'],
        ['Y','Y','X']
        ]

    if test_unbranched_GHZ:

        for jj,tomo_list in enumerate(tomo_lists):
            print '-----------------------------------'
            print 'press q to stop measurement cleanly'
            print '-----------------------------------'
            qt.msleep(2)
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                break

            GreenAOM.set_power(25e-6)
            ins_counters.set_is_running(0)
            optimiz0r.optimize(dims=['x','y','z'])

            ssrocalibration(SAMPLE_CFG)

            for kk,orientations in enumerate(orientations_list):
                print '-----------------------------------'
                print 'press q to stop measurement cleanly'
                print '-----------------------------------'
                qt.msleep(2)
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                    break

                orientations_name = orientations[0][0]+ orientations[1][0]+ orientations[2][0] +orientations[3][0]
                tomo_name = tomo_list[0]+tomo_list[1]+tomo_list[2]
                print tomo_name
                print orientations_name

                GHZ(SAMPLE+'GHZ_C125_unbranched_tomo_'+tomo_name+'_'+orientations_name,feedforward=False, carbon_list = [1,2,5], 
                    tomo_list = tomo_list, parity_orientations = orientations, 
                    initialize_carbons = False, init_carbon_list = [3], init_carbon_states =['up'], init_carbon_methods = ['swap'],
                    init_carbon_thresholds = [0], debug=False)

    if test_unbranched_GHZ_with_init:

        for jj,tomo_list in enumerate(tomo_lists):
            print '-----------------------------------'
            print 'press q to stop measurement cleanly'
            print '-----------------------------------'
            qt.msleep(2)
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                break

            GreenAOM.set_power(25e-6)
            ins_counters.set_is_running(0)
            optimiz0r.optimize(dims=['x','y','z'])

            ssrocalibration(SAMPLE_CFG)

            for kk,orientations in enumerate(fast_orientations_list):
                print '-----------------------------------'
                print 'press q to stop measurement cleanly'
                print '-----------------------------------'
                qt.msleep(2)
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                    break

                orientations_name = orientations[0][0]+ orientations[1][0]+ orientations[2][0] +orientations[3][0]
                tomo_name = tomo_list[0]+tomo_list[1]+tomo_list[2]
                print tomo_name
                print orientations_name

                GHZ(SAMPLE+'GHZ_C125_unbranched_tomo_'+tomo_name+'_'+orientations_name,feedforward=False, carbon_list = [1,2,5], 
                    tomo_list = tomo_list, parity_orientations = orientations, 
                    initialize_carbons = True, init_carbon_list = [1,2,5], init_carbon_states = 3*['up'], init_carbon_methods = 3*['swap'],
                    init_carbon_thresholds = 3*[0], debug=False)