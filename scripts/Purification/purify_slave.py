"""
Contains the single-setup experiments of the purification project.

NK 2016
"""
import numpy as np
import qt


import measurement.lib.measurement2.measurement as m2
from measurement.lib.pulsar import pulse, pulselib, element, pulsar
reload(pulsar)
import measurement.lib.measurement2.adwin_ssro.DD_2 as DD; reload(DD)
import LDE_element as LDE_elt; reload(LDE_elt)
execfile(qt.reload_current_setup)


class purify_single_setup(DD.MBI_C13):

    """
    measurement class for testing when both setups are operating without any PQ instrument 
    for single-setup testing and phase calibrations
    """
    mprefix = 'purifcation slave'
    adwin_process = 'purification'
    def __init__(self,name):
        DD.MBI_C13.__init__(self,name)
        self.joint_params = m2.MeasurementParameters('JointParameters')
        self.params = m2.MeasurementParameters('LocalParameters')

    def autoconfig(self):

        # setup logical adwin parameters --> how many C13 intialization steps are there?
        # this can go out soon.
        self.params['C13_MBI_threshold_list'] = [1]*(self.params['do_swap_onto_carbon'] + self.params['do_purifying_gate'])
        if self.params['do_carbon_init'] > 0: 
            if self.params['carbon_init_method'] == 'MBI':
                self.params['C13_MBI_threshold_list'] =[1] + self.params['C13_MBI_threshold_list'] 
            else:
                self.params['C13_MBI_threshold_list'] =[0] + self.params['C13_MBI_threshold_list'] 
        
        self.params['Nr_C13_init'] = len(self.params['C13_MBI_threshold_list'])
        

        self.params['LDE_attempts'] = self.joint_params['LDE_attempts']

        DD.MBI_C13.autoconfig(self)


        # add values from AWG calibrations
        self.params['SP_voltage_AWG'] = \
                self.A_aom.power_to_voltage( self.params['AWG_SP_power'], controller='sec')

        qt.pulsar.set_channel_opt('AOM_Newfocus', 'high', self.params['SP_voltage_AWG'])




        '''
        Potentially useful autoconfig AOM coonfiguration below:
            - Yellow during LDE
            - RO via the AWG/ PulseAOM
        '''

        # self.params['RO_voltage_AWG'] = \
        #         self.AWG_RO_AOM.power_to_voltage(
        #                 self.params['AWG_RO_power'], controller='sec')
        # self.params['yellow_voltage_AWG'] = \
        #         self.yellow_aom.power_to_voltage(
        #                 self.params['AWG_yellow_power'], controller='sec')

        #print 'setting AWG SP voltage:', self.params['SP_voltage_AWG']

        # if self.params['LDE_yellow_duration'] > 0.:
        #     qt.pulsar.set_channel_opt('AOM_Yellow', 'high', self.params['yellow_voltage_AWG'])
        # else:
        #     print self.mprefix, self.name, ': Ignoring yellow'

    def run(self, autoconfig=True, setup=True):

        """
        inherited from pulsar msmt.
        """
        if autoconfig:
            self.autoconfig()
       
        
        if setup:
            self.setup()

        for i in range(10):
            self.physical_adwin.Stop_Process(i+1)
            qt.msleep(0.1)
        qt.msleep(1)
        # self.adwin.load_MBI()   
        # New functionality, now always uses the adwin_process specified as a class variables 
        loadstr = 'self.adwin.load_'+str(self.adwin_process)+'()'   

        exec(loadstr)
        qt.msleep(1)
        # print loadstr 

        length = self.params['nr_of_ROsequences']


        self.start_adwin_process(stop_processes=['counter'], load=False)
        qt.msleep(1)
        self.start_keystroke_monitor('abort')

        while self.adwin_process_running():

            if self.keystroke('abort') != '':
                print 'aborted.'
                self.stop_keystroke_monitor('abort')
                break

            reps_completed = self.adwin_var('completed_reps')
            print('completed %s / %s readout repetitions' % \
                    (reps_completed, self.params['repetitions']))
            qt.msleep(1)

        try:
            self.stop_keystroke_monitor('abort')
        except KeyError:
            pass # means it's already stopped

        self.stop_adwin_process()
        reps_completed = self.adwin_var('completed_reps')
        print('completed %s / %s readout repetitions' % \
                (reps_completed, self.params['repetitions']))

    def save(self, name='adwindata'):
        reps = self.adwin_var('completed_reps')
        sweeps = self.params['pts'] * self.params['reps_per_ROsequence']
        if self.params['Nr_parity_msmts'] == 0:
            parity_reps = 1
        else:
            parity_reps =  reps*self.params['Nr_parity_msmts']


        self.save_adwin_data(name,
                [   ('CR_before', reps),
                    ('CR_after', reps),
                    ('C13_MBI_attempts', reps), 
                    ('C13_MBI_starts', reps), 
                    ('C13_MBI_success', reps), 
                    ('SSRO_result_after_Cinit',reps),
                    ('statistics', 10),
                    ('adwin_communication_time'              ,reps),  
                    ('plu_which'                             ,reps),  
                    ('attempts_first'                        ,reps),  
                    ('attempts_second'                       ,reps), 
                    ('SSRO_after_electron_carbon_SWAP_result',reps), 
                    ('carbon_readout_result'                 ,reps),
                    ('electron_readout_result'               , reps),
                    ('ssro_results'                           , reps), 
                    ])
        return

    def load_remote_carbon_params(self,master=True):
        """
        Generates a hypothetical carbon with index = 9 from the joint measurement parameters.
        These parameters are then used for the sequence duration calculation.
        Watch out:  partially overwrites connection element parameters 
                    and stores the old parameters in the msmt_params.
        """
        if master:
            prefix = 'master'
        else: 
            prefix = 'slave'

        e_trans = self.params['electron_transition']

        self.params['C9_Ren_tau' + e_trans]                        = self.joint_params[prefix + '_tau']
        self.params['C9_Ren_N' + e_trans]                          = self.joint_params[prefix + '_N']
        self.params['C9_Ren_extra_phase_correction_list' + e_trans] = np.array([0]*9+[self.joint_params[prefix + '_eigen_phase']])
        self.params['C9_freq_0']                                   = self.joint_params[prefix + '_freq_0']
        self.params['C9_freq_1'+ e_trans]                          = self.joint_params[prefix + '_freq_1']
        self.params['C9_freq'+ e_trans]                            = self.joint_params[prefix + '_freq']
        
        
        # store parameters for phase gates
        self.params['stored_min_phase_correct']    = self.params['min_phase_correct'] 
        self.params['stored_min_dec_tau']          = self.params['min_dec_tau'] 
        self.params['stored_max_dec_tau']          = self.params['max_dec_tau'] 
        self.params['stored_dec_pulse_multiple']   = self.params['dec_pulse_multiple'] 
        self.params['stored_carbon_init_RO_wait']  = self.params['Carbon_init_RO_wait']

        # overwrite parameters for phase gates for sequence calculation 

        self.params['min_phase_correct'] = self.joint_params[prefix + '_min_phase_correct']
        self.params['min_dec_tau'] = self.joint_params[prefix + '_min_dec_tau']
        self.params['max_dec_tau'] = self.joint_params[prefix + '_max_dec_tau']
        self.params['dec_pulse_multiple'] = self.joint_params[prefix + '_dec_pulse_multiple']
        self.params['Carbon_init_RO_wait'] = self.joint_params[prefix + '_carbon_init_RO_wait']

    def restore_msmt_parameters(self):
        """
        Reloads the stored parameters for regular operation.
        """
        self.params['min_phase_correct']    = self.params['stored_min_phase_correct']
        self.params['min_dec_tau']          = self.params['stored_min_dec_tau']
        self.params['max_dec_tau']          = self.params['stored_max_dec_tau'] 
        self.params['dec_pulse_multiple']   = self.params['stored_dec_pulse_multiple'] 
        self.params['Carbon_init_RO_wait']  = self.params['stored_carbon_init_RO_wait']

    def calculate_sequence_duration(self,gate_seq,verbose = False,**kw):
        """
        Input: A list of gates as specified for regular DD sequences:
        Output: The duration of the input sequence in the AWG 
        The calculation includes phase gates and extra us due to triggers and tau_cut.
        Calucation is achieved by running through the flow of DD_2.py / the MBI_C13 class

        Known bug: The length of the first MW element depends on the used channel delays.
        If the Pulsemod delay is larger than 500 ns --> TROUBLE! don't do that!
        """

        gate_seq = self.generate_AWG_elements(gate_seq,0)


        gate_seq[-1].event_jump = None # necessary manipulation of the last gate. don't change this

        list_of_elements,gate_seq = self.combine_to_AWG_sequence(gate_seq, explicit = True)

        duration = 0

        for e in gate_seq.elements[:-1]: #do not take the ro trigger into account --> delete the last element
            for ee in list_of_elements:
                if ee.name in e['wfname']:
                    duration+=ee.length()*e['repetitions']

                    if verbose:
                        print ee.name,ee.ideal_length(),ee.length(),ee.samples(),e['repetitions'],duration
        return duration


    def calculate_C13_init_duration(self,master = True,**kw):

        # load remote params and store current msmt params
        self.load_remote_carbon_params(master = master) # generate carbon 9 from the joint params

        # generate the list of gates in the remote setting
        carbon_init_seq = DD.MBI_C13.initialize_carbon_sequence(self,go_to_element = 'start',
                    prefix = 'C_Init', pt=0,
                    addressed_carbon = 9)
        # calculate remote sequence duration
        seq_duration = self.calculate_sequence_duration(carbon_init_seq,**kw)
        
        #restore actual msmt params.
        self.restore_msmt_parameters()

        return seq_duration

    def calculate_C13_swap_duration(self,master=True,**kw):
        '''
        Calculates the duration of the swap. At the moment only one swap type supported
        '''
        # load remote params and store current msmt params
        self.load_remote_carbon_params(master = master) # generate carbon 9 from the joint params

        # generate the list of gates in the remote setting
        if self.params['do_carbon_init'] > 0:#the carbon has been initialized. use a slight difference in the sequence
            carbon_init_seq = DD.MBI_C13.carbon_swap_gate(self,go_to_element = 'start',
                        prefix = 'C_swap', pt=0,
                        addressed_carbon = 9)
        else:
            # no C13 init, calculate the other gate sequence.
            # TODO make correct gate sequence in DD_2.py
            carbon_init_seq = []
            return 0


        # calculate remote sequence duration
        seq_duration = self.calculate_sequence_duration(carbon_init_seq,**kw)
        
        #restore actual msmt params.
        self.restore_msmt_parameters()

        #need to also factor the LDE rephasing element in
        if master:
            seq_duration += self.joint_params['master_average_repump_time']
        else:
            seq_duration += self.joint_params['slave_average_repump_time']

        return seq_duration

    def initialize_carbon_sequence(self,**kw):
        """
        manipulates the length of the C_init RO_wait in order to correctly synchronize both AWGs
        only does this on the side of the setup with the shorter carbon gate time!
        """
        setup = qt.current_setup
        master_setup = self.joint_params['master_setup']
        # store this value as it is also important for the AWG/ADWIN communication
        store_C_init_RO_wait = self.params['Carbon_init_RO_wait']

        # calculate sequence durations 
        master_seq_duration = self.calculate_C13_init_duration(master = False,verbose=False,**kw)
        slave_seq_duration = self.calculate_C13_init_duration(master= False,verbose=False,**kw)

        init_RO_wait_diff = self.joint_params['master_carbon_init_RO_wait'] - self.joint_params['slave_carbon_init_RO_wait']


        if self.params['is_two_setup_experiment'] > 0:
            if setup == master_setup and (master_seq_duration-slave_seq_duration + init_RO_wait_diff < 0):
                # adjust the length of the element of the master RO wait time.
                self.params['Carbon_init_RO_wait'] = self.params['Carbon_init_RO_wait'] + slave_seq_duration - master_seq_duration - init_RO_wait_diff
            
            elif setup != master_setup and (master_seq_duration-slave_seq_duration + init_RO_wait_diff > 0):
                # adjust the length of the element of the slave RO wait time.

                self.params['Carbon_init_RO_wait'] = self.params['Carbon_init_RO_wait'] + master_seq_duration - slave_seq_duration + init_RO_wait_diff

        seq = DD.MBI_C13.initialize_carbon_sequence(self,**kw)

        ### restore the old value
        self.params['Carbon_init_RO_wait'] = store_C_init_RO_wait

        return seq

    def carbon_swap_gate(self,**kw):
        """
        manipulates the length of the C_init RO_wait in order to correctly synchronize both AWGs
        only does this on the side of the setup with the shorter carbon gate time!
        additionally inserts a wait time to preserve the coherence of the electron state after the LDE element. 
        """
        setup = qt.current_setup
        master_setup = self.joint_params['master_setup']
        # store this value as it is also important for the AWG/ADWIN communication
        store_C_init_RO_wait = self.params['Carbon_init_RO_wait']

        # calculate sequence durations 
        master_seq_duration = self.calculate_C13_swap_duration(master = True,verbose=False,**kw)
        slave_seq_duration = self.calculate_C13_swap_duration(master= False,verbose=False,**kw)

        init_RO_wait_diff = self.joint_params['master_carbon_init_RO_wait'] - self.joint_params['slave_carbon_init_RO_wait']
        

        if self.params['is_two_setup_experiment'] > 0:
            if setup == master_setup and (master_seq_duration-slave_seq_duration + init_RO_wait_diff < 0):
                # adjust the length of the element of the master RO wait time.

                self.params['Carbon_init_RO_wait'] = self.params['Carbon_init_RO_wait'] + slave_seq_duration - master_seq_duration - init_RO_wait_diff
            
            elif setup != master_setup and (master_seq_duration-slave_seq_duration + init_RO_wait_diff > 0):
                # adjust the length of the element of the slave RO wait time.
                self.params['Carbon_init_RO_wait'] = self.params['Carbon_init_RO_wait'] + master_seq_duration - slave_seq_duration + init_RO_wait_diff

        seq = DD.MBI_C13.carbon_swap_gate(self,**kw)

        ### restore the old value
        self.params['Carbon_init_RO_wait'] = store_C_init_RO_wait

        return seq


    def generate_AWG_sync_elt(self,Gate):
        ### used in non-local msmts syncs master and slave AWGs
        ### uses the scheme 'single_element'
        
        #if self.joint_params['master_setup'] == qt.current_setup:
        Gate.elements = [LDE_elt._master_sequence_start_element(self,Gate)]
        Gate.wait_for_trigger = True
        # else: not used!
        #     Gate.elements = [LDE_elt._slave_Sequence_start_element]

    def generate_LDE_rephasing_elt(self,Gate):
        ### used in non-local msmts syncs master and slave AWGs
        ### uses the scheme 'single_element' --> this will throw a warning in DD_2.py
        

        Gate.elements = [LDE_elt._LDE_rephasing_elt(self,Gate)]
        Gate.wait_for_trigger = False

    def generate_LDE_element(self,Gate):
        """
        the parent function in DD_2 is overwritten by this special function that relies solely on
        msmt_params, joint_params & params_lt3 / params_lt4.
        """

        LDE_elt.generate_LDE_elt(self,Gate)

        if self.joint_params['opt_pi_pulses'] == 2:#i.e. we do barret & kok or SPCorrs etc.
            Gate.event_jump = 'next'
            Gate.go_to = 'next' 
        else:
            Gate.event_jump = 'next'
            Gate.go_to = 'start'
            
            if self.params['do_phase_correction'] == 0 and 'LDE2' in Gate.name:
                Gate.go_to = None
                Gate.event_jump = None
            elif self.params['LDE_1_is_init'] > 0 or self.params['do_swap_onto_carbon'] == 0 and 'LDE1' in Gate.name:
                Gate.go_to = None
                Gate.event_jump = None

    def generate_sequence(self,upload=True,debug=False):
        """
        generate the sequence for the purification experiment.
        Tries to be as general as possible in order to suffice for multiple calibration measurements
        """


        ### initialize empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Purification')

        ### create a list of gates according to the current sweep.
        for pt in range(self.params['pts']):

            #sweep parameter
            if self.params['do_general_sweep'] == 1:
                self.params[self.params['general_sweep_name']] = self.params['general_sweep_pts'][pt]

            gate_seq = []


            ### generate all gates within the sequence
            AWG_sync_wait = DD.Gate('AWG_sync','single_element',wait_time = self.params['AWG_wait_for_lt3_start'] )
            AWG_sync_wait.scheme = 'single_element'
            self.generate_AWG_sync_elt(AWG_sync_wait)


            

            ### LDE elements
            LDE1 = DD.Gate('LDE1'+str(pt),'LDE')
            LDE1.el_state_after_gate = 'sup'

                ### if statement to decide what LDE1 does: init or entangling.
            if self.params['LDE_1_is_init'] >0:
                LDE1.reps = 1

                if self.params['input_el_state'] in ['X','mX','Y','mY']:
                    LDE1.first_pulse_is_pi2 = True
            else:
                LDE1.reps = self.params['LDE_attempts']
            


            ### LDE elements need rephasing or repumping elements
            LDE_rephase1 = DD.Gate('LDE_rephasing_1'+str(pt),'single_element',wait_time = self.params['average_repump_time'])
            LDE_rephase1.scheme = 'single_element'
            self.generate_LDE_rephasing_elt(LDE_rephase1)

            LDE_repump1 = DD.Gate('LDE_repump_1_'+str(pt),'Trigger',duration = 5e-6)

            ### WE have two LDE elements with potentially different functions
            LDE2 = DD.Gate('LDE2'+str(pt),'LDE')
            LDE2.el_state_after_gate = 'sup'
            LDE2.reps = self.params['LDE_attempts']

            LDE_rephase2 = DD.Gate('LDE_rephasing_2_'+str(pt),'single_element',wait_time = self.params['average_repump_time'])
            LDE_rephase2.scheme = 'single_element'
            self.generate_LDE_rephasing_elt(LDE_rephase2)

            LDE_repump2 = DD.Gate('LDE_repump_2_'+str(pt),'Trigger',duration = 5e-6)




            ### apply phase correction to the carbon. gets a jump element via the adwin to the next element.
            dynamic_phase_correct = DD.Gate(
                    'C13_Phase_correct'+str(pt),
                    'Carbon_Gate',
                    Carbon_ind          = self.params['carbon'], 
                    event_jump          = 'next',
                    tau                 = 2.32e-6,#1/self.params['C'+str(self.params['carbon'])+'_freq_0'],
                    N                   = 2)
            # additional parameters needed for DD_2.py
            dynamic_phase_correct.scheme = 'carbon_phase_feedback'
            dynamic_phase_correct.reps = self.params['phase_correct_max_reps']-1

            final_dynamic_phase_correct = DD.Gate(
                    'Final C13_Phase_correct'+str(pt),
                    'Carbon_Gate',
                    Carbon_ind  = self.params['carbon'], 
                    tau         = 2.32e-6,#1/self.params['C'+str(self.params['carbon'])+'_freq_0'],
                    N           = 2,
                    no_connection_elt = True)


            ### this really needs to be combined with the RO MW (not if tau_cut does it's job!)
            #pulse
            final_dynamic_phase_correct.scheme = 'carbon_phase_feedback_end_elt'
            final_dynamic_phase_correct.C_phases_after_gate = [None]*10
            final_dynamic_phase_correct.C_phases_after_gate[self.params['carbon']] = 'reset'

            ### comment we could include branching for the last tomography step.! otherwise the phase will be off upon measuring the wrong outcome (i.e. the dark state)
            carbon_purify_seq = self.readout_carbon_sequence(
                prefix              = 'Purify',
                pt                  = pt,
                go_to_element       = None,
                event_jump_element  = None,
                RO_trigger_duration = self.params['Carbon_init_RO_wait'],
                el_state_in         = 0, # gives a relative phase correction.
                carbon_list         = [self.params['carbon']],
                RO_basis_list       = ['X'])
                



            e_RO = self.readout_carbon_sequence(
                    prefix              = 'Tomo',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    el_state_in         = 0,
                    carbon_list         = [],
                    RO_basis_list       = [],
                    do_RO_electron      = True,
                    do_init_pi2         = False) 




            #######################################################################
            ### append all necessary gates according to the current measurement ###
            #######################################################################

            if self.params['do_N_MBI'] > 0: 
                ### Nitrogen MBI
                mbi = DD.Gate('MBI_'+str(pt),'MBI')
                gate_seq.append(mbi)


            # this could be used for the synchronization of the two setups
            # gate_seq.append(DD.Gate('dummy_wait'+str(pt),'passive_elt',wait_time = 3e-6))


            if self.params['do_carbon_init'] > 0:
                ### initialize carbon in +Z or +X
                carbon_init_seq = self.initialize_carbon_sequence(go_to_element = 'start',
                        prefix = 'C_Init', pt =pt,
                        addressed_carbon = self.params['carbon'],initialization_method = self.params['carbon_init_method'])

                if gate_seq != []:
                    carbon_init_seq[0].wait_for_trigger = False

                gate_seq.extend(carbon_init_seq)

            #### insert a MW pi pulse when repumping
            if self.params['MW_before_LDE1'] > 0:
                mw_pi = DD.Gate('elec_pi_'+str(pt),'electron_Gate',
                    Gate_operation='pi')

                if gate_seq == []:
                    mw_pi.wait_for_trigger = True
                gate_seq.append(mw_pi)


            if self.params['do_LDE_1'] > 0:
                ### needs corresponding adwin parameter 
                if gate_seq == []:
                    LDE1.wait_for_trigger = True
                gate_seq.append(LDE1)

                if self.params['do_swap_onto_carbon'] > 0:
                    gate_seq.append(LDE_rephase1)

                elif self.params['LDE_1_is_init'] == 0:
                    gate_seq.append(LDE_repump1)

            if self.params['do_swap_onto_carbon'] > 0:
                ### Elementes for swapping
                swap_with_init = self.carbon_swap_gate(
                                go_to_element = 'start',
                                pt = pt,
                                addressed_carbon = self.params['carbon'])

                ### need to write this method XXX
                #swap_without_init = 

                if self.params['do_carbon_init'] > 0:
                    # put stens gate seq here
                    gate_seq.extend(swap_with_init)
                else:
                    #do full swap: need to figure out the full gate sequence.
                    #gate_seq.extend(swap_without_init)
                    pass

            if self.params['do_LDE_2'] > 0:
                if gate_seq == []:
                    LDE2.wait_for_trigger = True

                gate_seq.append(LDE2)

                if self.params['do_purifying_gate'] > 0 or self.params['do_phase_correction'] > 0:
                    # electron has to stay coherent after LDE attempts
                    gate_seq.append(LDE_rephase2)

                else: # this is used if we sweep the number of repetitions for Qmemory testing.
                    gate_seq.append(LDE_repump2)

            if self.params['do_phase_correction'] > 0:
                gate_seq.extend([dynamic_phase_correct,final_dynamic_phase_correct])

            if self.params['do_purifying_gate'] > 0:
                gate_seq.extend(carbon_purify_seq)



            if self.params['do_carbon_readout'] > 0:

                carbon_tomo_seq = self.readout_carbon_sequence(
                        prefix              = 'Tomo',
                        pt                  = pt,
                        go_to_element       = None,
                        event_jump_element  = None,
                        RO_trigger_duration = 10e-6,
                        el_state_in         = 0,
                        carbon_list         = [self.params['carbon']],
                        RO_basis_list       = self.params['Tomography_bases'],
                        readout_orientation = self.params['carbon_readout_orientation']) 
                gate_seq.extend(carbon_tomo_seq)

            else: #No carbon spin RO? Do espin RO!
                gate_seq.extend(e_RO)


            ###############################################
            # prepare and program the actual AWG sequence #
            ###############################################
            print len(gate_seq)
            #### insert elements here
            gate_seq = self.generate_AWG_elements(gate_seq,pt)

            ### Convert elements to AWG sequence and add to combined list
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq, explicit=True)
            combined_list_of_elements.extend(list_of_elements)

            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)

        print upload
        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'



class purify_slave(purify_single_setup):

    """
    measurement class that is exectued on LT3 for remote measurements.
    Comes with a slightly adapted adwin process for setup communication.
    """
    mprefix = 'purifcation slave'
    ### XXX
    ### insert remote slave_adwin process here
    adwin_process = 'purification'
