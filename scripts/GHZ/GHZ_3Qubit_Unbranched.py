'This script runs the GHZ measurement, without branching out after each measurement and the corresponding result'


import numpy as np
import itertools
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

def feedforward_flips(tomo_list):
    ###this defines which outcomes to flip, for a ppp (positive-positive-positive) readout
    ###the reference (never flipped) is the 111 readout, corresponding to a 'basic' GHZ state.
    if tomo_list == ['X','X','X']:
        flips = ['000','011','101','110']
    elif tomo_list == ['X','Y','Y']:
        flips = ['000','001','010','011']
    elif tomo_list == ['Y','X','Y']:
        flips = ['000','001','100','101']
    elif tomo_list == ['Y','Y','X']:
        flips = ['000','010','100','110']
    elif tomo_list == ['Z','Z','I']:
        flips = ['010','011','100','101']
    elif tomo_list == ['Z','I','Z']:
        flips = ['001','011','100','110']
    elif tomo_list == ['I','Z','Z']:
        flips = ['001','010','101','110']
    else:
        flips = []

    return(flips)

def calc_inv_RO_list(RO_basis_list, carbon_list, inv_carbon_list):
    inv_RO_basis_list = ['I' for i in RO_basis_list]
    for ii,inv_c in enumerate(inv_carbon_list):
        for jj,c in enumerate(carbon_list):
            if inv_c == c:
                inv_RO_basis_list[ii] = RO_basis_list[jj]
    print 'RO_basis_list', RO_basis_list
    print 'inv_RO_basis_list', inv_RO_basis_list
    return(inv_RO_basis_list)

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
    carbon_list = [5,1,2],
    inv_carbon_list = [5,1,2],
    xyy_list = ['X','Y','Y'],
    yxy_list = ['Y','X','Y'],
    yyx_list = ['Y','Y','X'],
    tomo_list = ['X','X','X'],
    feedforward = False,
    debug = False,
    parity_orientations = ['positive','positive','positive','positive'],
    final_phases = [0,0,0],
    initialize_carbons = False,
    init_carbon_list = [5,1,2],
    init_carbon_states = 3*['up'],
    init_carbon_methods = 3*['swap'],
    init_carbon_thresholds = [0,0,0],
    tomo_carbons = [5,1,2],
    electron_RO = False,
    composite_pi = False,
    ):

    m = DD.GHZ_ThreeQB_Unbranched(name)
    funcs.prepare(m)

    if debug:
        print 'DEBUG MODE'

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

    m.params['Use_composite_pi'] = composite_pi

    ###### parity yxy and invert yxy ########
    m.params['Parity_xyy_do_init_pi2'] = True
    m.params['Parity_xyy_carbon_list'] = carbon_list
    m.params['Parity_xyy_RO_list'] = xyy_list
    m.params['Parity_xyy_RO_orientation'] = parity_orientations[0]
    m.params['Invert_xyy_carbon_list'] = inv_carbon_list
    m.params['Invert_xyy_RO_list'] = calc_inv_RO_list(xyy_list,carbon_list,inv_carbon_list)
    m.params['Invert_xyy_do_final_pi2'] = False

    ###### parity yxy and invert yxy ########
    m.params['Parity_yxy_do_init_pi2'] = False
    m.params['Parity_yxy_carbon_list'] = carbon_list
    m.params['Parity_yxy_RO_list'] = yxy_list
    m.params['Parity_yxy_RO_orientation'] = parity_orientations[1]
    m.params['Invert_yxy_carbon_list'] = inv_carbon_list
    m.params['Invert_yxy_RO_list'] = calc_inv_RO_list(yxy_list,carbon_list,inv_carbon_list) 
    m.params['Invert_yxy_do_final_pi2'] = False

    ###### parity yyx and invert yyx ######
    m.params['Parity_yyx_do_init_pi2'] = False
    m.params['Parity_yyx_carbon_list'] = carbon_list
    m.params['Parity_yyx_RO_list'] = yyx_list
    m.params['Parity_yyx_RO_orientation'] = parity_orientations[2]
    m.params['Invert_yyx_carbon_list'] = inv_carbon_list
    m.params['Invert_yyx_RO_list'] = calc_inv_RO_list(yyx_list,carbon_list,inv_carbon_list)
    m.params['Invert_yyx_do_final_pi2'] = False    
    
    ###### RO TOMO params ################
    m.params['RO_electron'] = electron_RO
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
        print 'WARNING: YOU CANNOT DO FEEDFORWARD FOR THE UNBRANCHED SITUATION'
        # flip_states = feedforward_flips(tomo_list)
        # print('flipping before orientation correction:')
        # print(flip_states)

        # ###correct for the orientations when determining which outcomes have to be flipped.
        # for j in np.arange(3):
        #     if parity_orientations[j] == 'negative':
        #         for k,state in enumerate(flip_states):
        #             outcome = state[j]
        #             outcome_n = np.mod(int(state[j])+1,2)
        #             state = state[:j] + str(outcome_n) + state[(j+1):]
        #             flip_states[k] = state
        # print('flipping after orientation correction:')
        # print(flip_states)

        # if '000' in flip_states:
        #     m.params['flip_000'] = True
        # if '001' in flip_states:
        #     m.params['flip_001'] = True
        # if '010' in flip_states:
        #     m.params['flip_010'] = True
        # if '011' in flip_states:
        #     m.params['flip_011'] = True
        # if '100' in flip_states:
        #     m.params['flip_100'] = True
        # if '101' in flip_states:
        #     m.params['flip_101'] = True
        # if '110' in flip_states:
        #     m.params['flip_110'] = True
        # if '111' in flip_states:
        #     m.params['flip_111'] = True

    funcs.finish(m, upload =True, debug=debug)

def GHZ_3mmts(name, 
    carbon_list = [5,1],
    inv_carbon_list = [5,1],
    A_list = ['X','Y','Y'],
    B_list = ['Y','X','Y'],
    tomo_list = ['X','X','X'],
    feedforward = False,
    debug = False,
    parity_orientations = ['positive','positive','positive'],
    final_phases = [0,0],
    initialize_carbons = False,
    init_carbon_list = [5,1,2],
    init_carbon_states = 3*['up'],
    init_carbon_methods = 3*['swap'],
    init_carbon_thresholds = [0,0,0],
    tomo_carbons = [5,1],
    electron_RO = False,
    composite_pi = False,
    ):

    m = DD.GHZ_3mmts_Unbranched(name)
    funcs.prepare(m)

    if debug:
        print 'DEBUG MODE'

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
    m.params['Nr_parity_msmts']     = 2
    m.params['add_wait_gate'] = False
    m.params['wait_in_msm1']  = False

    ##### general RO params
    m.params['RO_trigger_duration'] = 150e-6
    m.params['Tomo_RO_trigger_duration'] = 10e-6

    m.params['Use_composite_pi'] = composite_pi

    ###### parity yxy and invert yxy ########
    m.params['Parity_A_do_init_pi2'] = True
    m.params['Parity_A_carbon_list'] = carbon_list
    m.params['Parity_A_RO_list'] = A_list
    m.params['Parity_A_RO_orientation'] = parity_orientations[0]
    m.params['Invert_A_carbon_list'] = inv_carbon_list
    m.params['Invert_A_RO_list'] = calc_inv_RO_list(A_list,carbon_list,inv_carbon_list)
    m.params['Invert_A_do_final_pi2'] = False

    ###### parity yxy and invert yxy ########
    m.params['Parity_B_do_init_pi2'] = False
    m.params['Parity_B_carbon_list'] = carbon_list
    m.params['Parity_B_RO_list'] = B_list
    m.params['Parity_B_RO_orientation'] = parity_orientations[1]
    m.params['Invert_B_carbon_list'] = inv_carbon_list
    m.params['Invert_B_RO_list'] = calc_inv_RO_list(B_list,carbon_list,inv_carbon_list) 
    m.params['Invert_B_do_final_pi2'] = False

    ###### RO TOMO params ################
    m.params['RO_electron'] = electron_RO
    m.params['Tomo_do_init_pi2'] = False

    if electron_RO:
        m.params['Invert_B_do_final_pi2'] = True
        m.params['Tomo_do_init_pi2'] = False

    for s in tomo_list:
        if 'Z' in s:
            print 'tomography contains Z; doing pi/2 between invertRO and RO'
            m.params['Invert_B_do_final_pi2'] = True
            m.params['Tomo_do_init_pi2'] = True
    m.params['Tomo_carbon_list'] = tomo_carbons
    m.params['Tomo_RO_orientation'] = parity_orientations[2]
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
        print 'WARNING: YOU CANNOT DO FEEDFORWARD FOR THE UNBRANCHED SITUATION'
        # flip_states = feedforward_flips(tomo_list)
        # print('flipping before orientation correction:')
        # print(flip_states)

        # ###correct for the orientations when determining which outcomes have to be flipped.
        # for j in np.arange(3):
        #     if parity_orientations[j] == 'negative':
        #         for k,state in enumerate(flip_states):
        #             outcome = state[j]
        #             outcome_n = np.mod(int(state[j])+1,2)
        #             state = state[:j] + str(outcome_n) + state[(j+1):]
        #             flip_states[k] = state
        # print('flipping after orientation correction:')
        # print(flip_states)

        # if '000' in flip_states:
        #     m.params['flip_000'] = True
        # if '001' in flip_states:
        #     m.params['flip_001'] = True
        # if '010' in flip_states:
        #     m.params['flip_010'] = True
        # if '011' in flip_states:
        #     m.params['flip_011'] = True
        # if '100' in flip_states:
        #     m.params['flip_100'] = True
        # if '101' in flip_states:
        #     m.params['flip_101'] = True
        # if '110' in flip_states:
        #     m.params['flip_110'] = True
        # if '111' in flip_states:
        #     m.params['flip_111'] = True

    funcs.finish(m, upload =True, debug=debug)

def GHZ_branched(name, 
    carbon_list = [5,1,2],
    inv_carbon_list = [5,1,2],
    xyy_list = ['X','Y','Y'],
    yxy_list = ['Y','X','Y'],
    yyx_list = ['Y','Y','X'],
    tomo_list = ['X','X','X'],
    feedforward = False,
    debug = False,
    parity_orientations = ['positive','positive','positive','positive'],
    final_phases = [0,0,0],
    initialize_carbons = False,
    init_carbon_list = [5,1,2],
    init_carbon_states = 3*['up'],
    init_carbon_methods = 3*['swap'],
    init_carbon_thresholds = [0,0,0],
    tomo_carbons = [5,1,2],
    electron_RO = False
    ):

    m = DD.GHZ_ThreeQB(name)
    funcs.prepare(m)

    if debug:
        print 'DEBUG MODE'

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

    ###### parity yxy and invert yxy ########
    m.params['Parity_xyy_do_init_pi2'] = True
    m.params['Parity_xyy_carbon_list'] = carbon_list
    m.params['Parity_xyy_RO_list'] = xyy_list
    m.params['Parity_xyy_RO_orientation'] = parity_orientations[0]
    m.params['Invert_xyy_carbon_list'] = inv_carbon_list
    m.params['Invert_xyy_RO_list'] = calc_inv_RO_list(xyy_list,carbon_list,inv_carbon_list)
    m.params['Invert_xyy_do_final_pi2'] = False

    ###### parity yxy and invert yxy ########
    m.params['Parity_yxy_do_init_pi2'] = False
    m.params['Parity_yxy_carbon_list'] = carbon_list
    m.params['Parity_yxy_RO_list'] = yxy_list
    m.params['Parity_yxy_RO_orientation'] = parity_orientations[1]
    m.params['Invert_yxy_carbon_list'] = inv_carbon_list
    m.params['Invert_yxy_RO_list'] = calc_inv_RO_list(yxy_list,carbon_list,inv_carbon_list) 
    m.params['Invert_yxy_do_final_pi2'] = False

    ###### parity yyx and invert yyx ######
    m.params['Parity_yyx_do_init_pi2'] = False
    m.params['Parity_yyx_carbon_list'] = carbon_list
    m.params['Parity_yyx_RO_list'] = yyx_list
    m.params['Parity_yyx_RO_orientation'] = parity_orientations[2]
    m.params['Invert_yyx_carbon_list'] = inv_carbon_list
    m.params['Invert_yyx_RO_list'] = calc_inv_RO_list(yyx_list,carbon_list,inv_carbon_list)
    m.params['Invert_yyx_do_final_pi2'] = False    

    ###### RO TOMO params
    m.params['RO_electron'] = electron_RO

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

    debug = False

    context3mmt_test = False
    unbranched_GHZ=True
    GHZ_permute_carbons =False
    unbranched_GHZ_test_permuted=False
    test_unbranched_GHZ_with_init=False
    test_X_X_X_tomo=False
    unbranched_GHZ_contextuality_test=False

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

    threemmt_orientations_list=[
        ['positive','positive','positive'],
        ['positive','positive','negative'],
        ['positive','negative','positive'],
        ['positive','negative','negative'],
        ['negative','positive','positive'],
        ['negative','positive','negative'],
        ['negative','negative','positive'],
        ['negative','negative','negative']
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
        # ['Z','Z','I'],
        # ['Z','I','Z'],
        # ['I','Z','Z'],
        # ['X','Y','Y'],
        # ['Y','X','Y'],
        # ['Y','Y','X']
        ]

    full_tomo_lists = [
        ['X','X','X'],
        ['X','Y','Y'],
        ['Y','X','Y'],
        ['Y','Y','X'],
        # ['X','I','I'],['Y','I','I'],['Z','I','I'],
        # ['I','X','I'],['I','Y','I'],['I','Z','I'],
        # ['I','I','X'],['I','I','Y'],['I','I','Z'],

        # ['X','X','I'],['X','Y','I'],['X','Z','I'],
        # ['Y','X','I'],['Y','Y','I'],['Y','Z','I'],
        # ['Z','X','I'],['Z','Y','I'],['Z','Z','I'],

        # ['X','I','X'],['Y','I','X'],
        # ['Z','I','X'],
        # ['X','I','Y'],['Y','I','Y'],['Z','I','Y'],
        # ['X','I','Z'],['Y','I','Z'],['Z','I','Z'],

        # ['I','X','X'],['I','Y','X'],['I','Z','X'],
        # ['I','X','Y'],['I','Y','Y'],['I','Z','Y'],
        # ['I','X','Z'],['I','Y','Z'],['I','Z','Z'],

        # ['X','X','X'],
        ['X','Y','X'],#['X','Z','X'],
        ['Y','X','X'],#['Y','Y','X'],
        # ['Y','Z','X'],
        # ['Z','X','X'],
        # ['Z','Y','X']
        # ['Z','Z','X'],

         ['X','X','Y'],#['X','Y','Y'],
        # ['X','Z','Y'],
        # ['Y','X','Y'],
         ['Y','Y','Y'],#['Y','Z','Y'],
        # ['Z','X','Y'],['Z','Y','Y'],['Z','Z','Y'],

        # ['X','X','Z'],['X','Y','Z'],
        # ['X','Z','Z'],
        # ['Y','X','Z'],
        # ['Y','Y','Z'],
        # ['Y','Z','Z'],
        # ['Z','X','Z'],['Z','Y','Z'],['Z','Z','Z']
        ['Z','Z','I'],
        ['Z','I','Z'],
        ['I','Z','Z'],
        ]
        


    if unbranched_GHZ:

        for jj,tomo_list in enumerate(full_tomo_lists):
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
            
            tomo_name = ''.join([a for a in tomo_list])
            if tomo_name == 'XZZ' or tomo_name == 'YZZ' or tomo_name == 'ZXZ' or tomo_name == 'ZYZ' or tomo_name == 'ZZZ':
                branched = False
            else:
                branched = False

            for kk,orientations in enumerate(orientations_list):
                print '-----------------------------------'
                print 'press q to stop measurement cleanly'
                print '-----------------------------------'
                qt.msleep(2)
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                    break


                orientations_name = ''.join([o[0] for o in orientations])
                print tomo_name
                print orientations_name

                GHZ(SAMPLE+'GHZ_C512_unbranched_composite_pi_tomo_'+tomo_name+'_'+orientations_name,  
                    tomo_list = tomo_list, composite_pi=True,
                    parity_orientations = orientations, initialize_carbons = False,feedforward=False, debug=False)
                # GHZ(SAMPLE+'GHZ_C512_unbranched_tomo_'+tomo_name+'_'+orientations_name,feedforward=False,
                #     tomo_list = tomo_list, parity_orientations = orientations, 
                #     initialize_carbons = False, debug=False)
                if branched:
                    print '-----------------------------------'
                    print 'press q to stop measurement cleanly'
                    print '-----------------------------------'
                    qt.msleep(2)
                    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                        break

                    GHZ_branched(SAMPLE+'GHZ_C512_branched_tomo_'+tomo_name+'_'+orientations_name,feedforward=False, 
                        tomo_list = tomo_list, parity_orientations = orientations, 
                        initialize_carbons = False, debug=False)

    if GHZ_permute_carbons:
        carbon_lists = [[1,5,2],[5,1,2]]#
        inv_carbon_lists = list(itertools.permutations([1,2,5]))

        for jj,carbon_list in enumerate(carbon_lists):
            print '-----------------------------------'
            print 'press q to stop measurement cleanly'
            print '-----------------------------------'
            qt.msleep(2)
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                break

            for jj,inv_carbon_list in enumerate(inv_carbon_lists):
                print '-----------------------------------'
                print 'press q to stop measurement cleanly'
                print '-----------------------------------'
                qt.msleep(2)
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                    break

                if not debug:
                    GreenAOM.set_power(25e-6)
                    ins_counters.set_is_running(0)
                    optimiz0r.optimize(dims=['x','y','z'])

                    ssrocalibration(SAMPLE_CFG)

                ro_carbon_list_name = ''.join([str(a) for a in carbon_list])
                inv_carbon_list_name = ''.join([str(a) for a in inv_carbon_list])

                branched = False

                for kk,orientations in enumerate(orientations_list):
                    print '-----------------------------------'
                    print 'press q to stop measurement cleanly'
                    print '-----------------------------------'
                    qt.msleep(2)
                    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                        break

                    orientations_name = ''.join([o[0] for o in orientations])
                    print ro_carbon_list_name
                    print inv_carbon_list_name
                    print orientations_name

                    GHZ(SAMPLE+'GHZ_C125_unbranched_carbon_list_ro_'+ro_carbon_list_name+'_inv_'+inv_carbon_list_name+'_'+orientations_name,
                        feedforward=False, carbon_list = carbon_list, tomo_carbons = carbon_list, inv_carbon_list = inv_carbon_list, 
                        parity_orientations = orientations, 
                        initialize_carbons = False, debug=debug)
                    if branched:
                        print '-----------------------------------'
                        print 'press q to stop measurement cleanly'
                        print '-----------------------------------'
                        qt.msleep(2)
                        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                            break

                        GHZ_branched(SAMPLE+'GHZ_C125_branched_carbon_list_ro_'+ro_carbon_list_name+'_inv_'+inv_carbon_list_name+'_'+orientations_name,
                            feedforward=False, carbon_list = carbon_list, tomo_carbons = carbon_list,
                            parity_orientations = orientations, 
                            initialize_carbons = False, debug=debug)


    if unbranched_GHZ_contextuality_test:
        mmt_lists = [#[['X','I','I'],['X','I','I'],['X','I','I'],['X','I','I']],
                     # [['X','I','I'],['X','I','I'],['X','I','I'],['Y','I','I']],
                     # [['X','I','I'],['X','I','I'],['X','I','I'],['Z','I','I']],
                     [['I','X','I'],['I','X','I'],['I','X','I'],['I','X','I']],
                     [['I','X','I'],['I','X','I'],['I','X','I'],['I','Y','I']],
                     # [['I','X','I'],['I','X','I'],['I','X','I'],['I','Z','I']],
                     [['I','I','X'],['I','I','X'],['I','I','X'],['I','I','X']],
                     [['I','I','X'],['I','I','X'],['I','I','X'],['I','I','Y']],
                     # [['I','I','X'],['I','I','X'],['I','I','X'],['I','I','Z']]
                    #[[['X','Y','Y'],['Y','X','Y'],['Y','Y','X'],['X','X','X']],
                    # [['X','I','I'],['I','X','I'],['I','I','X'],['X','X','X']],
                    # [['X','I','I'],['I','Y','I'],['I','I','Y'],['X','Y','Y']],
                    # [['Y','I','I'],['I','X','I'],['I','I','Y'],['Y','X','Y']],
                    # [['Y','I','I'],['I','Y','I'],['I','I','X'],['Y','Y','X']]
                    ]

        for mmt_list in mmt_lists:
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

            xyy_list = mmt_list[0]
            yxy_list = mmt_list[1]
            yyx_list = mmt_list[2]
            tomo_list = mmt_list[3]
            xyy_list_name = ''.join([a for a in xyy_list])                
            yxy_list_name = ''.join([a for a in yxy_list])                
            yyx_list_name = ''.join([a for a in yyx_list])
            tomo_name = ''.join([a for a in tomo_list])

            for kk,orientations in enumerate(orientations_list):
                print '-----------------------------------'
                print 'press q to stop measurement cleanly'
                print '-----------------------------------'
                qt.msleep(2)
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                    break

                orientations_name = ''.join([o[0] for o in orientations])

                print xyy_list_name, yxy_list_name, yyx_list_name, tomo_name
                print orientations_name

                GHZ(SAMPLE+'GHZ_C512_unbranched_composite_pi_'+'_'+xyy_list_name+'_'+yxy_list_name+'_'+yyx_list_name+'_'+tomo_name+'_'+orientations_name,  
                    xyy_list = xyy_list, yxy_list = yxy_list, yyx_list = yyx_list, tomo_list = tomo_list, composite_pi=True,
                    parity_orientations = orientations, initialize_carbons = False,feedforward=False, debug=False)
                # GHZ(SAMPLE+'GHZ_C512_unbranched_contextuality_'+'_'+xyy_list_name+'_'+yxy_list_name+'_'+yyx_list_name+'_'+tomo_name+'_'+orientations_name, 
                #     xyy_list = xyy_list, yxy_list = yxy_list, yyx_list = yyx_list, tomo_list = tomo_list, 
                #     parity_orientations = orientations, initialize_carbons = False,feedforward=False, debug=False)
                # GHZ_branched(SAMPLE+'GHZ_C512_branched_contextuality_'+'_'+xyy_list_name+'_'+yxy_list_name+'_'+yyx_list_name+'_'+tomo_name+'_'+orientations_name,
                #     xyy_list = xyy_list, yxy_list = yxy_list, yyx_list = yyx_list, tomo_list = tomo_list, 
                #     parity_orientations = orientations, initialize_carbons = False,feedforward=False, debug=False)


    if context3mmt_test:
        mmt_lists = [[['I','X','I'],['X','I','I'],['I','X','I']],
                    [['I','X','I'],['X','I','I'],['I','Y','I']],
                    [['I','X','I'],['I','I','X'],['I','X','I']],
                    [['I','X','I'],['I','I','X'],['I','Y','I']]
                    # [['I','Y','I'],['X','I','I'],['I','Y','I']],
                    # [['I','Y','I'],['X','I','I'],['I','X','I']],
                    # [['I','Y','I'],['I','I','X'],['I','Y','I']],
                    # [['I','Y','I'],['I','I','X'],['I','X','I']]                    
                    #[[['X','I'],['I','Y'],['X','Y']],
                    #[['I','X'],['Y','I'],['Y','X']]
                    #[['Y','I'],['I','X'],['Y','Y']],
                    #[['Y','I'],['I','X'],['X','Y']],
                    #[['Y','I'],['I','X'],['X','X']],
                    #[['X','I'],['I','Y'],['X','Y']],
                    #[['Y','Y'],['X','X'],['Z','Z']],
                    #[['Y','Y'],['X','X'],['X','Z']],
                    #[['Y','Y'],['X','X'],['Y','Z']],
                    #[['Y','Y'],['X','X'],['Z','X']],
                    #[['Y','Y'],['X','X'],['Z','Y']],
                    #[['Y','Y'],['X','X'],['Y','X']],
                    #[['Y','Y'],['X','X'],['X','Y']],
                    #[['Y','I'],['I','Y'],['Y','Y']],
                    #[['X','I'],['I','X'],['X','X']],
                    #[['Y','X'],['X','Y'],['Z','Z']]
                    ]


        for mmt_list in mmt_lists:
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

            A_list = mmt_list[0]
            B_list = mmt_list[1]
            tomo_list = mmt_list[2]
            A_list_name = ''.join([a for a in A_list])                
            B_list_name = ''.join([a for a in B_list])                
            tomo_name = ''.join([a for a in tomo_list])

            for kk,orientations in enumerate(threemmt_orientations_list):
                print '-----------------------------------'
                print 'press q to stop measurement cleanly'
                print '-----------------------------------'
                qt.msleep(2)
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                    break

                orientations_name = ''.join([o[0] for o in orientations])

                print A_list_name, B_list_name, tomo_name
                print orientations_name

                GHZ_3mmts(SAMPLE+'GHZ_C512_unbranched_composite_pi_'+'_'+A_list_name+'_'+B_list_name+'_'+tomo_name+'_'+orientations_name,  
                    A_list = A_list, B_list = B_list, tomo_list = tomo_list, carbon_list =[5,1,2], inv_carbon_list=[5,1,2],tomo_carbons=[5,1,2],
                    composite_pi=True,
                    parity_orientations = orientations, initialize_carbons = False,feedforward=False, debug=False)


    if unbranched_GHZ_test_permuted:
        mmt_lists_1 = list(itertools.permutations([['X','Y','Y'],['Y','X','Y'],['Y','Y','X'],['X','X','X']]))
        mmt_lists_2 = list(itertools.permutations([['X','I','I'],['I','X','I'],['I','I','X'],['X','X','X']]))
        mmt_lists_3 = list(itertools.permutations([['X','I','I'],['I','Y','I'],['I','I','Y'],['X','Y','Y']]))
        mmt_lists_4 = list(itertools.permutations([['Y','I','I'],['I','X','I'],['I','I','Y'],['Y','X','Y']]))
        mmt_lists_5 = list(itertools.permutations([['Y','I','I'],['I','Y','I'],['I','I','X'],['Y','Y','X']]))
        mmt_lists = mmt_lists_2+mmt_lists_3+mmt_lists_4+mmt_lists_5
        for mmt_list in mmt_lists:
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
            xyy_list = mmt_list[0]
            yxy_list = mmt_list[1]
            yyx_list = mmt_list[2]
            tomo_list = mmt_list[3]
            xyy_list_name = ''.join([a for a in xyy_list])                
            yxy_list_name = ''.join([a for a in yxy_list])                
            yyx_list_name = ''.join([a for a in yyx_list])
            tomo_name = ''.join([a for a in tomo_list])
            for kk,orientations in enumerate(orientations_list):
                print '-----------------------------------'
                print 'press q to stop measurement cleanly'
                print '-----------------------------------'
                qt.msleep(2)
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                    break

                orientations_name = ''.join([o[0] for o in orientations])
                print xyy_list_name, yxy_list_name, yyx_list_name, tomo_name
                print orientations_name
                GHZ(SAMPLE+'GHZ_C125_unbranched_tomo_'+xyy_list_name+'_'+yxy_list_name+'_'+yyx_list_name+'_'+tomo_name+'_'+orientations_name, carbon_list = [1,2,5], 
                    xyy_list = xyy_list, yxy_list = yxy_list, yyx_list = yyx_list, tomo_list = tomo_list, 
                    parity_orientations = orientations, initialize_carbons = False,feedforward=False, debug=False)


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

                tomo_name = ''.join([a for a in tomo_list])
                orientations_name = ''.join([o[0] for o in orientations])
                print tomo_name
                print orientations_name

                GHZ(SAMPLE+'GHZ_C125_unbranched_tomo_'+tomo_name+'_'+orientations_name,feedforward=False, carbon_list = [1,2,5], 
                    tomo_list = tomo_list, parity_orientations = orientations, 
                    initialize_carbons = True, init_carbon_list = [1,2,5], init_carbon_states = 3*['up'], init_carbon_methods = 3*['swap'],
                    init_carbon_thresholds = 3*[0], debug=False)

    if test_X_X_X_tomo:
        tomo_lists = [['X'],['Y'],['Z']]

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
                tomo_name = ''.join([a for a in tomo_list])
                orientations_name = ''.join([o[0] for o in orientations])

                print 'tomo: '+tomo_name
                print orientations_name

                GHZ(SAMPLE+'GHZ_C1_unbranched_X_X_X_tomo_'+tomo_name+'_'+orientations_name, feedforward=False,carbon_list = [1], 
                    xyy_list = ['X'],yxy_list=['X'],yyx_list=['X'],tomo_list = tomo_list, tomo_carbons=[1],parity_orientations = orientations, 
                    initialize_carbons=False,debug=False)

