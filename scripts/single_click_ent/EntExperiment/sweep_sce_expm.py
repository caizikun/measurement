'''
Allows for sweeps of general parameters within the purification sequence.
Only supports single setup experiments with one specific adwin script
NK 2016
'''

import numpy as np
import qt 
import sce_expm; reload(sce_expm)
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
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
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
        import sce_expm_params_lt4 as params_lt4
        reload(params_lt4)
        m.AWG_RO_AOM = qt.instruments['PulseAOM']
        for k in params_lt4.params_lt4:
            m.params[k] = params_lt4.params_lt4[k]

    elif setup == 'lt3' :
         import sce_expm_params_lt3 as params_lt3
         reload(params_lt3)
         m.AWG_RO_AOM = qt.instruments['PulseAOM']
         for k in params_lt3.params_lt3:
             m.params[k] = params_lt3.params_lt3[k]

    else:
        print 'Sweep_purification.py: invalid setup:', setup

    if not(hasattr(m,'joint_params')):
        m.joint_params = {}
    import sce_expm_joint_params as joint_params
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


def run_sweep(m,debug=True, upload_only=True,save_name='',multiple_msmts=False,autoconfig = True,**kw):

    if autoconfig:
        m.autoconfig()    

    m.generate_sequence()
    m.dump_AWG_seq()
    
    if upload_only:
        return



    m.setup(debug=debug)

    if not debug:
        m.run(autoconfig=False, setup=False,**kw)

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
    m.params['do_only_opt_pi']          = 0
    m.params['do_yellow_with_AWG']      = 0
    
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
    m.params['do_only_opt_pi']          = 0 # for single setup testing!
    m.params['do_yellow_with_AWG']      = 0
    

def calibrate_theta(name, debug = False, upload_only = False):
    """
    See espin/calibrate_mw_pulses.
    """
    from measurement.scripts.espin.calibrate_mw_pulses import calibrate_theta_pulse

    calibrate_theta_pulse(SAMPLE_CFG + 'theta',rng = 0.05,debug=debug,upload_only=upload_only)


def lastpi2_measure_delay(name, debug = False, upload_only = False):
    """
    There is a finite timing offset between LDE element and the last pi/2 pulse that we do upon success.
    This measurement sweeps the timing of the last pi/2 to determine the best position.
    """
    m = sce_expm.SingleClickEntExpm(name)
    prepare(m)

    ### general params
    pts = 21
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500

    turn_all_sequence_elements_off(m)

    ### sequence specific parameters
    m.params['MW_during_LDE'] = 1
    m.joint_params['opt_pi_pulses'] = 0
    m.joint_params['LDE_attempts'] = 1
    m.joint_params['do_final_mw_LDE'] = 1
    m.params['first_mw_pulse_is_pi2'] = True
    ### prepare sweep
    m.params['do_general_sweep']    = True
    m.params['general_sweep_name'] = 'MW_final_delay_offset'
    print 'sweeping the', m.params['general_sweep_name']
    m.params['general_sweep_pts'] = np.linspace(-0.1e-6,0.1e-6,pts)
    m.params['sweep_name'] = m.params['general_sweep_name'] 
    m.params['sweep_pts'] = m.params['general_sweep_pts']*1e9

    ### upload and run

    run_sweep(m,debug = debug,upload_only = upload_only)


def lastpi2_phase_vs_amplitude(name, debug = False, upload_only = False):
    """
    This measurement sweeps the phase of the last pi/2 pulse while keeping the amplitude constant.
    Is used as a sanity check --> are all our pi/2 pulses actually pi/2 pulses?
    """
    m = sce_expm.SingleClickEntExpm(name)
    prepare(m)

    ### general params
    pts = 21
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500

    turn_all_sequence_elements_off(m)

    ### sequence specific parameters
    m.params['MW_during_LDE'] = 0
    m.joint_params['opt_pi_pulses'] = 0
    m.joint_params['LDE_attempts'] = 1
    m.joint_params['do_final_mw_LDE'] = 1
    m.params['first_pulse_is_pi2'] = True
    ### prepare sweep
    m.params['do_general_sweep']    = True
    m.params['general_sweep_name'] = 'LDE_final_mw_phase'
    print 'sweeping the', m.params['general_sweep_name']
    m.params['general_sweep_pts'] = np.linspace(0,180,pts)
    m.params['sweep_name'] = m.params['general_sweep_name'] 
    m.params['sweep_pts'] = m.params['general_sweep_pts']

    ### upload and run

    run_sweep(m,debug = debug,upload_only = upload_only)


def lastpi2_phase_action(name, debug = False, upload_only = False):
    """
    This measurement sweeps the phase of the last pi/2 pulse and includes MW pulses in the LDE element.
    Is used as a sanity check --> how coherent are we at the last pi/2 pulse and what is the phase relation for the MW source.
    """
    m = sce_expm.SingleClickEntExpm(name)
    prepare(m)

    ### general params
    pts = 21
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1500

    turn_all_sequence_elements_off(m)

    ### sequence specific parameters
    m.params['MW_during_LDE'] = 1
    m.joint_params['opt_pi_pulses'] = 0
    m.joint_params['LDE_attempts'] = 1
    m.joint_params['do_final_mw_LDE'] = 1
    m.params['first_mw_pulse_is_pi2'] = True
    
    ### prepare sweep
    m.params['do_general_sweep']    = True
    m.params['general_sweep_name'] = 'LDE_final_mw_phase'
    print 'sweeping the', m.params['general_sweep_name']
    m.params['general_sweep_pts'] = np.linspace(0,360,pts)
    m.params['sweep_name'] = m.params['general_sweep_name'] 
    m.params['sweep_pts'] = m.params['general_sweep_pts']

    ### upload and run

    run_sweep(m,debug = debug,upload_only = upload_only)


def ionization_study_LT4(name, debug = False, upload_only = False, use_yellow = False):
    """
    Two setup experiment where LT3 does optical pi pulses only
    While LT4 repetitively runs the entire LDE element.
    """
    m = sce_expm.SingleClickEntExpm(name)
    prepare(m)

    ### general params
    pts = 21
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500

    turn_all_sequence_elements_off(m)
    if qt.current_setup == 'lt3':
        m.params['do_only_opt_pi'] = 1
        m.joint_params['opt_pi_pulses'] = 1

    ### sequence specific parameters
    m.params['MW_during_LDE'] = 1
    m.params['is_two_setup_experiment'] = 1
    m.joint_params['do_final_mw_LDE'] = 0
   #m.params['first_pulse_is_pi2'] = True
    
    ### prepare sweep
    m.params['do_general_sweep']    = True
    m.params['general_sweep_name'] = 'LDE_attempts'
    print 'sweeping the', m.params['general_sweep_name']
    m.params['general_sweep_pts'] = np.linspace(5,500,pts)
    m.params['sweep_name'] = m.params['general_sweep_name'] 
    m.params['sweep_pts'] = m.params['general_sweep_pts']
    m.params['do_yellow_with_AWG'] = use_yellow
    ### upload and run

    run_sweep(m,debug = debug,upload_only = upload_only)


def ionization_non_local(name, debug = False, upload_only = False, use_yellow = False):
    """
    Two setup experiment where LT3 does optical pi pulses only
    While LT4 repetitively runs the entire LDE element.
    """
    m = sce_expm.SingleClickEntExpm(name)
    prepare(m)

    ### general params
    pts = 10
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 250

    turn_all_sequence_elements_off(m)


    ### sequence specific parameters
    m.params['MW_during_LDE'] = 1
    m.params['is_two_setup_experiment'] = 1
    m.joint_params['do_final_mw_LDE'] = 0
    # m.params['first_pulse_is_pi2'] = True
    # m.params['mw_first_pulse_amp'] = 0
    ### prepare sweep
    if qt.current_setup == 'lt3':
        # m.params['do_only_opt_pi'] = 1
        m.joint_params['opt_pi_pulses'] = 1
        m.params['mw_first_pulse_amp'] = 0
        m.params['Hermite_pi_amp'] = 0
        m.params['Hermite_pi2_amp'] = 0

    m.params['do_general_sweep']    = True
    m.params['general_sweep_name'] = 'LDE_attempts'
    print 'sweeping the', m.params['general_sweep_name']
    m.params['general_sweep_pts'] = np.linspace(1,500,pts)
    m.params['sweep_name'] = m.params['general_sweep_name'] 
    m.params['sweep_pts'] = m.params['general_sweep_pts']
    m.params['do_yellow_with_AWG'] = use_yellow
    ### upload and run

    run_sweep(m,debug = debug,upload_only = upload_only)


if __name__ == '__main__':
    # lastpi2_measure_delay(name,debug=False,upload_only=False)
    # lastpi2_phase_vs_amplitude(name,debug=False,upload_only=False)
    lastpi2_phase_action(name,debug=False,upload_only=False)

    # ionization_study_LT4(name,debug=True, upload_only = True,use_yellow = False)

    # ionization_non_local(name+'ionization_opt_pi',debug=False, upload_only = False)
    
