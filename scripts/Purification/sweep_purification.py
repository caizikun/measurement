'''
Allows for sweeps of general parameters within the purification sequence.
Only supports single setup experiments with one specific adwin script

NK 2016
'''
import numpy as np
import qt 
import purify_slave; reload(purify_slave)


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


    if setup == 'lt1':
        import params_lt1
        reload(params_lt1)
        for k in params_lt1.params_lt1:
            m.params[k] = params_lt1.params_lt1[k]

        ### below: copied from bell and commented out for later
    elif setup == 'lt4' :
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


def run_sweep(m,debug=True, upload_only=True):


    m.autoconfig()
    print m.params['C13_MBI_threshold_list']
    m.generate_sequence()
    if upload_only:
        return
    m.setup(debug=debug)

    if not debug:
        m.run(autoconfig=False, setup=False)    
        m.save()    
        m.finish()

def generate_AWG_seq(name):

    m = purify_slave.purify_single_setup(name)
    prepare(m)

    ### general params
    m.params['pts'] = 1
    m.params['reps_per_ROsequence'] = 1

    ### adwin process variables: should be automatically set.
    m.params['Nr_C13_init']     = 0 # Not necessary (only for C13 MBI)
    m.params['Nr_MBE']          = 0 # Not necessary (only for C13 MBI)
    m.params['Nr_parity_msmts'] = 0 # Not necessary (only for C13 MBI)
    m.params['Tomography_bases'] = ['X']


    ### which parts of the sequence do you want to incorporate.
    m.params['do_general_sweep']    = False
    m.params['is_two_setup_experiment']           = 1 
    m.params['do_N_MBI']            = 0 # Not necessary (only for C13 MBI)
    #m.params['electron_ro_after_first_seq'] = 0 # for Barret-Kok- SPCORR...
    # electron_ro_after_first_seq not required.
    m.params['do_carbon_init']  = 1 
    m.params['do_C_init_SWAP_wo_SSRO'] = 0
    
    # TODO finish jumping and event triggering for LDE / INIT ELEMENT
    # we always do LDE1
    m.params['do_swap_onto_carbon']    = 1
    m.params['do_SSRO_after_electron_carbon_SWAP'] = 0
    m.params['do_LDE_2']            = 1
    m.params['do_phase_correction'] = 1 # previously: phase_correct
    m.params['do_purifying_gate']   = 1 # previously: purify
    m.params['do_carbon_readout']  = 1 

    ### upload sequence & run

    run_sweep(m,debug = True,upload_only = True)

def SPCorrs(name,debug = False,upload_only = False):
    """
    Performs a regular Spin-photon correlation measurement.
    NOTE: purify_single_setup has to be updated to be pq measurement for this to actually work.
    """
    m = purify_slave.purify_single_setup(name)
    prepare(m)

    ### general params
    m.params['pts'] = 1
    m.params['reps_per_ROsequence'] = 1000

    ### adwin process variables: should be automatically set.
    m.params['Nr_C13_init']     = 0 # Not necessary (only for C13 MBI)
    m.params['Nr_MBE']          = 0 # Not necessary (only for C13 MBI)
    m.params['Nr_parity_msmts'] = 0 # Not necessary (only for C13 MBI)


    ### which parts of the sequence do you want to incorporate.
    m.params['do_general_sweep']    = False
    m.params['is_two_setup_experiment'] = 0
    m.params['do_N_MBI']            = 0 # Not necessary (only for C13 MBI)
    #m.params['electron_ro_after_first_seq'] = 0 # for Barret-Kok- SPCORR...
    # electron_ro_after_first_seq not required.
    m.params['do_carbon_init']  = 0
    m.params['do_C_init_SWAP_wo_SSRO'] = 0
    
    # TODO finish jumping and event triggering for LDE / INIT ELEMENT
    m.params['do_swap_onto_carbon']    = 0
    m.params['do_SSRO_after_electron_carbon_SWAP'] = 0
    m.params['do_LDE_2']            = 0
    m.params['do_phase_correction'] = 0 
    m.params['do_purifying_gate']   = 0 
    m.params['do_carbon_readout']  = 0 


    m.joint_params['opt_pi_pulses'] = 2

    ### upload

    run_sweep(m,debug = debug,upload_only = upload_only)

# def sweep_average_repump_time(name):

#     m = purify_slave.purify_single_setup(name)
#     prepare(m)

#     ### general params
#     m.params['pts'] = 1
#     m.params['reps_per_ROsequence'] = 1

#     ### adwin process variables: should be set automatically.
#     m.params['Nr_MBE']          = 0
#     m.params['Nr_parity_msmts'] = 0
#     m.params['Tomography_bases'] = ['X']



#     ###parts of the sequence: choose which ones you want to incorporate and check the result.
#     m.params['do_general_sweep']    = 0
#     m.params['is_two_setup_experiment']           = 0
#     m.params['do_N_MBI']            = 0
#     m.params['init_carbon']         = 1; m.params['carbon_init_method'] = 'MBI';
#     m.params['do_LDE_1']            = 0 
#     m.params['swap_onto_carbon']    = 0
#     m.params['do_LDE_2']            = 1 
#     m.params['do_phase_correction']       = 0
#     m.params['do_purifying_gate']              = 0
#     m.params['C13_RO']              = 1 #if 0 then RO of the electron via an adwin trigger.
#     m.params['final_RO_in_adwin']   = 0 # this gets rid of the final RO since it is done in the adwin

#     ### upload
    
#     run_sweep(m,debug = True,upload_only = True)

# def sweep_number_of_reps(name):

#     m = purify_slave.purify_single_setup(name)
#     prepare(m)

#     ### general params
#     m.params['pts'] = 1
#     m.params['reps_per_ROsequence'] = 1

#     ### adwin process variables: should be set automatically.
#     m.params['Nr_C13_init']     = 1
#     m.params['Nr_MBE']          = 0
#     m.params['Nr_parity_msmts'] = 0
#     m.params['Tomography_bases'] = ['X']



#     ###parts of the sequence: choose which ones you want to incorporate and check the result.
#     m.params['do_general_sweep']    = 0
#     m.params['is_two_setup_experiment']           = 0
#     m.params['do_N_MBI']            = 0
#     m.params['init_carbon']         = 1; m.params['carbon_init_method'] = 'MBI';
#     m.params['do_LDE_1']            = 0 
#     m.params['swap_onto_carbon']    = 0
#     m.params['do_LDE_2']            = 1 
#     m.params['do_phase_correction']       = 0
#     m.params['do_purifying_gate']              = 1
#     m.params['C13_RO']              = 1 #if 0 then RO of the electron via an adwin trigger.
#     m.params['final_RO_in_adwin']   = 0 # this gets rid of the final RO since it is done in the adwin

#     ### upload
#     run_sweep(m,debug = True,upload_only = True)

# def calibrate_memory_phase(name):

#     m = purify_slave.purify_single_setup(name)
#     prepare(m)

#     ### general params
#     m.params['pts'] = 1
#     m.params['reps_per_ROsequence'] = 1

#     ### adwin process variables: should be set automatically.
#     m.params['Nr_C13_init']     = 1
#     m.params['Nr_MBE']          = 0
#     m.params['Nr_parity_msmts'] = 0
#     m.params['Tomography_bases'] = ['X']



#     ###parts of the sequence: choose which ones you want to incorporate and check the result.
#     m.params['do_general_sweep']    = 0
#     m.params['is_two_setup_experiment']           = 0
#     m.params['do_N_MBI']            = 0
#     m.params['init_carbon']         = 1; m.params['carbon_init_method'] = 'MBI';
#     m.params['do_LDE_1']            = 0 
#     m.params['swap_onto_carbon']    = 0
#     m.params['do_LDE_2']            = 1 
#     m.params['do_phase_correction']       = 0
#     m.params['do_purifying_gate']              = 1
#     m.params['C13_RO']              = 1 #if 0 then RO of the electron via an adwin trigger.
#     m.params['final_RO_in_adwin']   = 0 # this gets rid of the final RO since it is done in the adwin

#     ### upload
#     run_sweep(m,debug = True,upload_only = True)

# def check_dynamic_phase_correct(name):

#     m = purify_slave.purify_single_setup(name)
#     prepare(m)

#     ### general params
#     m.params['pts'] = 1
#     m.params['reps_per_ROsequence'] = 1

#     ### adwin process variables: should be set automatically.
#     m.params['Nr_C13_init']     = 1
#     m.params['Nr_MBE']          = 0
#     m.params['Nr_parity_msmts'] = 0
#     m.params['Tomography_bases'] = ['X']



#     ###parts of the sequence: choose which ones you want to incorporate and check the result.
#     m.params['do_general_sweep']    = 0
#     m.params['is_two_setup_experiment']           = 0
#     m.params['do_N_MBI']            = 0
#     m.params['init_carbon']         = 1; m.params['carbon_init_method'] = 'MBI';
#     m.params['do_LDE_1']            = 0 
#     m.params['swap_onto_carbon']    = 0
#     m.params['do_LDE_2']            = 1 
#     m.params['do_phase_correction']       = 0
#     m.params['do_purifying_gate']              = 1
#     m.params['C13_RO']              = 1 #if 0 then RO of the electron via an adwin trigger.
#     m.params['final_RO_in_adwin']   = 0 # this gets rid of the final RO since it is done in the adwin

#     ### upload
#     run_sweep(m,debug = True,upload_only = True)

if __name__ == '__main__':
    # generate_AWG_seq('Sequence_testing')
    SPCorrs('Sequence_testing')