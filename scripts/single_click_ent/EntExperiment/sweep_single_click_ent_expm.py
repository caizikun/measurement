'''
Allows for sweeps of general parameters within the purification sequence.
Only supports single setup experiments with one specific adwin script
NK 2016
'''

import numpy as np
import qt 
import single_click_ent_expm; reload(single_click_ent_expm)
import msvcrt
name = qt.exp_params['protocols']['current']

def show_stopper():
    print '-----------------------------------'            
    print 'press q to stop measurement cleanly'
    print '-----------------------------------'
    qt.msleep(1)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        return True
    else: return False
    
def print_adwin_stuff(m):
    print m.params['cycle_duration']
    print m.params['SP_duration']
    print m.params['wait_after_pulse_duration']
    print m.params['MBI_attempts_before_CR']
    print m.params['Dynamical_stop_ssro_threshold']
    print m.params['Dynamical_stop_ssro_duration']
    print m.params['is_master']
    print m.params['is_two_setup_experiment'] 
    print m.params['do_carbon_init'] # goes to mbi sequence, ends with tomography
    print m.params['do_C_init_SWAP_wo_SSRO']
    print m.params['do_swap_onto_carbon']
    print m.params['do_SSRO_after_electron_carbon_SWAP']
    print m.params['do_LDE_2']
    print m.params['do_phase_correction'             ]
    print m.params['do_purifying_gate'               ]
    print m.params['do_carbon_readout'               ]
    print m.params['wait_for_awg_done_timeout_cycles'] 
    print m.params['adwin_comm_safety_cycles'        ] 
    print m.params['adwin_comm_timeout_cycles'       ] 
    print m.params['remote_awg_trigger_channel'      ]
    print m.params['invalid_data_marker_do_channel'  ]  


def prepare(m, setup=qt.current_setup,name=qt.exp_params['protocols']['current']):
    '''
    loads all necessary msmt parameters
    '''
    m.params['setup']=setup
    sample_name = qt.exp_params['samples']['current']
    name = qt.exp_params['protocols']['current']
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+MBI'])
    m.params.from_dict(qt.exp_params['protocols'][name]['AdwinSSRO+C13'])
    m.params.from_dict(qt.exp_params['protocols'][name]['AdwinSSRO+MBI'])
    m.params.from_dict(qt.exp_params['protocols'][name]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][name]['pulses'])
    m.params.from_dict(qt.exp_params['samples'][sample_name])

    ### soon not necessary anymore.
    m.params['Nr_C13_init']     = 0 # Not necessary (only for adwin: C13 MBI)
    m.params['Nr_MBE']          = 0 # Not necessary (only for adwin: C13 MBI)
    m.params['Nr_parity_msmts'] = 0 # Not necessary (only for adwin: C13 MBI)

    if setup == 'lt4' :
        import single_click_ent_expm_params_lt4 as params_lt4
        reload(params_lt4)
        m.AWG_RO_AOM = qt.instruments['PulseAOM']
        for k in params_lt4.params_lt4:
            m.params[k] = params_lt4.params_lt4[k]

    elif setup == 'lt3' :
         import single_click_ent_expm_params_lt3 as params_lt3
         reload(params_lt3)
         m.AWG_RO_AOM = qt.instruments['PulseAOM']
         for k in params_lt3.params_lt3:
             m.params[k] = params_lt3.params_lt3[k]

    else:
        print 'Sweep_purification.py: invalid setup:', setup

    if not(hasattr(m,'joint_params')):
        m.joint_params = {}
    import single_click_ent_expm_joint_params as joint_params
    reload(joint_params)
    for k in joint_params.joint_params:
        m.joint_params[k] = joint_params.joint_params[k]

    if setup == m.joint_params['master_setup']:
        m.params['is_master'] = 1
    else:
        m.params['is_master'] = 0

    m.params['send_AWG_start'] = 1
    m.params['sync_during_LDE'] = 1
    m.params['wait_for_AWG_done'] = 0
    m.params['do_general_sweep']= 1
    m.params['trigger_wait'] = 1


def run_sweep(m,debug=True, upload_only=True,save_name='',multiple_msmts=False,autoconfig = True):

    if autoconfig:
        m.autoconfig()    

    m.generate_sequence()
    m.dump_AWG_seq()
    
    if upload_only:
        return



    m.setup(debug=debug)

    if not debug:
        m.run(autoconfig=False, setup=False)

        if save_name != '':
            m.save(save_name)
        else:
            m.save()

        if multiple_msmts:
            return

        m.finish()


def turn_all_sequence_elements_off(m):
    """
    turns all parts of the AWG sequence off. except for do_LDE_1
    running this function before sequence generation will generate 
    Barrett & Kok like sequences
    """

    m.params['is_two_setup_experiment'] = 0
    m.params['MW_before_LDE']          = 0
    m.params['MW_pi_during_LDE']        = 1 # we always do this... has to be explicitly switched off
    m.params['do_N_MBI']                = 0 # we never do this (or might actually do this... depends)
    m.params['LDE_is_init']           = 0
    m.params['PLU_during_LDE']          = 0
    m.params['is_TPQI']                 = 0
    m.params['force_LDE_attempts_before_init'] = 0
    m.params['no_repump_after_LDE']     = 1
    m.params['do_general_sweep']        = 0
    m.params['do_phase_stabilisation']  = 0
    m.params['only_meas_phase']         = 0
    m.params['do_dynamical_decoupling'] = 0 
    
    
def turn_all_sequence_elements_on(m):
    """
    turns all parts of the AWG sequence on. except for do_LDE_1
    Running this function before generating the sequence
    creates the full purification sequence (no special sequences such as TPQI etc.)
    """

    m.params['is_two_setup_experiment'] = 1
    m.params['MW_before_LDE']          = 0
    m.params['MW_pi_during_LDE']        = 1
    m.params['do_N_MBI']                = 0 # we never do this (or might actually do this... depends)
    m.params['LDE_is_init']           = 0
    m.params['PLU_during_LDE']          = 1
    m.params['is_TPQI']                 = 0
    m.params['force_LDE_attempts_before_init'] = 0
    m.params['no_repump_after_LDE']    = 1
    m.params['do_general_sweep']        = 0
    m.params['do_phase_stabilisation']  = 1
    m.params['only_meas_phase']         = 0
    m.params['do_dynamical_decoupling'] = 0 # Not doing this yet (PH) 
    

def calibrate_theta(name):
    pass


if __name__ == '__main__':
    pass