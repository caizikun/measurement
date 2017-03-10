'''
Allows for sweeps of general parameters within the purification sequence.
Only supports single setup experiments with one specific adwin script
NK 2016
'''

import numpy as np
import qt 
import purify_slave as purify_slave; reload(purify_slave)
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
        import params_lt4
        reload(params_lt4)
        m.AWG_RO_AOM = qt.instruments['PulseAOM']
        for k in params_lt4.params_lt4:
            m.params[k] = params_lt4.params_lt4[k]
        # msmt.params['MW_BellStateOffset'] = 0.0
        # bseq.pulse_defs_lt4(msmt)
    elif setup == 'lt3' :
         import params_lt3
         reload(params_lt3)
         m.AWG_RO_AOM = qt.instruments['PulseAOM']
         for k in params_lt3.params_lt3:
             m.params[k] = params_lt3.params_lt3[k]
         #msmt.params['MW_BellStateOffset'] = 0.0
         #bseq.pulse_defs_lt3(msmt)
    else:
        print 'Sweep_purification.py: invalid setup:', setup

    if not(hasattr(m,'joint_params')):
        m.joint_params = {}
    import joint_params
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
    m.params['do_N_MBI']                = 0 
    m.params['do_carbon_init']          = 0
    m.params['do_C_init_SWAP_wo_SSRO']  = 0
    m.params['MW_before_LDE1']          = 0
    m.params['LDE_1_is_init']           = 0
    m.params['do_swap_onto_carbon']     = 0
    m.params['do_SSRO_after_electron_carbon_SWAP'] = 0
    m.params['do_LDE_2']                = 0
    m.params['do_phase_correction']     = 0 
    m.params['do_purifying_gate']       = 0 
    m.params['do_carbon_readout']       = 0 
    m.params['do_repump_after_LDE2']    = 0
    m.params['PLU_during_LDE']          = 0
    m.params['is_TPQI']                 = 0
    m.params['force_LDE_attempts_before_init'] = 0
    m.params['no_repump_after_LDE1']    = 0
    ### Should be made: PQ_during_LDE = 0??? Most of the time we don't need it.
    ### interesting to look at the spinpumping though...

def turn_all_sequence_elements_on(m):
    """
    turns all parts of the AWG sequence on. except for do_LDE_1
    Running this function before generating the sequence
    creates the full purification sequence (no special sequences such as TPQI etc.)
    """

    m.params['is_two_setup_experiment'] = 1
    m.params['do_N_MBI']                = 0 # we never do this (or might actually do this... depends)
    m.params['do_carbon_init']          = 1
    m.params['do_C_init_SWAP_wo_SSRO']  = 1
    m.params['LDE_1_is_el_init']        = 0
    m.params['do_swap_onto_carbon']     = 1
    m.params['do_SSRO_after_electron_carbon_SWAP'] = 1
    m.params['do_LDE_2']                = 1
    m.params['do_phase_correction']     = 1 
    m.params['do_purifying_gate']       = 1 
    m.params['do_carbon_readout']       = 1 
    m.params['do_repump_after_LDE2']    = 0
    m.params['PLU_during_LDE']          = 1
    m.params['is_TPQI']                 = 0
    m.params['force_LDE_attempts_before_init'] = 0
    m.params['no_repump_after_LDE1']    = 0
    
def repump_speed(name,debug = False,upload_only=False):
    """
    Initializes the electron in ms = -1 
    and sweeps the repump duration at the beginning of LDE_1
    """

    m = purify_slave.purify_single_setup(name)
    prepare(m)

    ### general params
    pts = 101
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500

    turn_all_sequence_elements_off(m)

    ### sequence specific parameters
    
    m.params['MW_before_LDE1'] = 1 # allows for init in -1 before LDE
    m.params['LDE_1_is_init']  = 1
    m.params['input_el_state'] = 'mZ'
    m.params['MW_during_LDE'] = 0
    m.joint_params['opt_pi_pulses'] = 0
    m.joint_params['LDE1_attempts'] = 1

    m.params['msmt_based_reset'] = 1
    m.params['LDE_SP_duration'] = 1e-6
    m.params['E_RO_amplitudes_AWG'] = 30e-9
    m.params['E_RO_voltages_AWG'] = \
                        MatisseAOM.power_to_voltage(
                                m.params['E_RO_amplitudes_AWG'], controller='sec')
    qt.pulsar.set_channel_opt('AOM_Matisse', 'high', m.params['E_RO_voltages_AWG'])

    # m.params['is_two_setup_experiment'] = 1

    # m.params['Hermite_pi_amp'] = 0
    ### prepare sweep
    m.params['do_general_sweep']    = True
    m.params['general_sweep_name'] = 'LDE_SP_duration'
    print 'sweeping the', m.params['general_sweep_name']
    m.params['general_sweep_pts'] = np.linspace(0.0,2.e-6,pts)
    m.params['sweep_name'] = m.params['general_sweep_name'] 
    m.params['sweep_pts'] = m.params['general_sweep_pts']*1e9
    m.params['is_two_setup_experiment']=0   #XXXX

    ### upload and run

    run_sweep(m,debug = debug,upload_only = upload_only)


def sweep_average_repump_time(name,do_Z = False,upload_only = False,debug=False):
    """
    sweeps the average repump time.
    runs the measurement for X and Y tomography. Also does positive vs. negative RO
    """
    m = purify_slave.purify_single_setup(name)
    prepare(m)

    ### general params
    pts = 16
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500

    turn_all_sequence_elements_off(m)

    ### sequence specific parameters
    m.params['is_two_setup_experiment'] = 0
    m.params['PLU_during_LDE'] = 0

    ###parts of the sequence: choose which ones you want to incorporate and check the result.
    m.params['do_general_sweep']    = 1
    m.params['do_carbon_init']  = 1 
    m.params['do_carbon_readout']  = 1 

    m.joint_params['LDE1_attempts'] = 5
    m.params['MW_during_LDE'] = 1
    m.joint_params['opt_pi_pulses'] = 0

    m.params['msmt_based_reset'] = 1
    m.params['LDE_SP_duration'] = 2e-6
    m.params['E_RO_amplitudes_AWG'] = 40e-9
    m.params['E_RO_voltages_AWG'] = \
                        MatisseAOM.power_to_voltage(
                                m.params['E_RO_amplitudes_AWG'], controller='sec')
    qt.pulsar.set_channel_opt('AOM_Matisse', 'high', m.params['E_RO_voltages_AWG'])

    ### define sweep
    m.params['general_sweep_name'] = 'average_repump_time'
    print 'sweeping the', m.params['general_sweep_name']
    m.params['general_sweep_pts'] = np.linspace(0e-6,4e-6,pts)
    m.params['sweep_name'] = m.params['general_sweep_name'] 
    m.params['sweep_pts'] = m.params['general_sweep_pts']*1e6

    
    ### loop over tomography bases and RO directions upload & run
    breakst = False
    autoconfig = True
    if do_Z:
        for t in ['Z']:
            m.joint_params['LDE1_attempts'] = 800
            if breakst:
                break
            for ro in ['positive','negative']:
                breakst = show_stopper()
                if breakst:
                    break
                save_name = t+'_'+ro
                m.params['Tomography_bases'] = [t]
                m.params['carbon_readout_orientation'] = ro
                m.params['do_C_init_SWAP_wo_SSRO'] = 1

                run_sweep(m,debug = debug,upload_only = upload_only,multiple_msmts = True,save_name=save_name,autoconfig=autoconfig)
                autoconfig = False

    else:
        for t in ['X','Y']:
            if breakst:
                break
            for ro in ['positive','negative']:
                breakst = show_stopper()
                if breakst:
                    break
                m.params['carbon_init_method'] = 'MBI'
                m.params['do_C_init_SWAP_wo_SSRO'] = 0
                save_name = t+'_'+ro
                m.params['Tomography_bases'] = [t]
                m.params['carbon_readout_orientation'] = ro
                run_sweep(m,debug = debug,upload_only = upload_only,multiple_msmts = True,save_name=save_name,autoconfig=autoconfig)
                autoconfig = False

    m.finish()


def sweep_number_of_reps(name,do_Z = False, upload_only = False, debug=False):

    """
    runs the measurement for X and Y tomography. Also does positive vs. negative RO
    """
    m = purify_slave.purify_single_setup(name)
    prepare(m)

    ### general params
    pts = 15
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 500

    turn_all_sequence_elements_off(m)

    ###parts of the sequence: choose which ones you want to incorporate and check the result.
    m.params['do_general_sweep']    = 1
    m.params['do_carbon_init']  = 1
    m.params['do_carbon_readout']  = 1 
    # m.params['mw_first_pulse_amp'] = 0
    m.params['MW_during_LDE'] = 1
    # m.params['mw_first_pulse_amp'] = 0#m.params['Hermite_pi_amp']
    #m.params['mw_first_pulse_phase'] = m.params['Y_phase']# +180 
    #m.params['mw_first_pulse_length'] = m.params['Hermite_pi_length']
    m.joint_params['opt_pi_pulses'] = 0

    m.params['msmt_based_reset'] = 1
    m.params['LDE_SP_duration'] = 2e-6
    m.params['E_RO_amplitudes_AWG'] = 30e-9
    m.params['E_RO_voltages_AWG'] = \
                        MatisseAOM.power_to_voltage(
                                m.params['E_RO_amplitudes_AWG'], controller='sec')
    qt.pulsar.set_channel_opt('AOM_Matisse', 'high', m.params['E_RO_voltages_AWG'])

    ### calculate the sweep array
    minReps = 1
    maxReps = 1000
    step = int((maxReps-minReps)/pts)+1
    ### define sweep
    m.params['general_sweep_name'] = 'LDE1_attempts'
    print 'sweeping the', m.params['general_sweep_name']
    m.params['general_sweep_pts'] = np.arange(minReps,maxReps,step)
    m.params['sweep_name'] = m.params['general_sweep_name'] 
    m.params['sweep_pts'] = m.params['general_sweep_pts']
    print 'sweep pts', np.arange(minReps,maxReps,step)
    ### loop over tomography bases and RO directions upload & run

    breakst = False
    autoconfig = True
    if do_Z:
        for t in ['Z']:
            if breakst:
                break
            for ro in ['positive','negative']:
                breakst = show_stopper()
                if breakst:
                    break
                print t,ro
                m.params['do_C_init_SWAP_wo_SSRO'] = 1
                save_name = t+'_'+ro
                m.params['Tomography_bases'] = [t]
                m.params['carbon_readout_orientation'] = ro
                run_sweep(m,debug = debug, upload_only = upload_only,multiple_msmts = True,save_name=save_name,autoconfig = autoconfig)
                autoconfig = False

    else:
        for t in ['X','Y']:
            if breakst:
                break
            for ro in ['positive','negative']:
                breakst = show_stopper()
                if breakst:
                    break
                m.params['do_C_init_SWAP_wo_SSRO'] = 0
                m.params['carbon_init_method'] = 'MBI'
                print t,ro
                save_name = t+'_'+ro
                m.params['Tomography_bases'] = [t]
                m.params['carbon_readout_orientation'] = ro
                run_sweep(m,debug = debug, upload_only = upload_only,multiple_msmts = True,save_name=save_name,autoconfig=autoconfig)
                autoconfig = False

    m.finish()


if __name__ == '__main__':

    #repump_speed(name+'_repump_speed',upload_only = False)

    # sweep_average_repump_time(name+'_Sweep_Repump_time_Z',do_Z = True,debug = False)
    sweep_average_repump_time(name+'_Sweep_Repump_time_X',do_Z = False,upload_only = False, debug=False)

    # sweep_number_of_reps(name+'_sweep_number_of_reps_X',do_Z = False, debug=False)
    # sweep_number_of_reps(name+'_sweep_number_of_reps_Z',do_Z = True)

 
