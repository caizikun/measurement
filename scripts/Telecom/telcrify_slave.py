"""
Contains the single-setup experiments of the purification project.
This class provides the sequence generation for the purification experiment.

NK 2016
"""
import numpy as np
import qt


import measurement.lib.measurement2.measurement as m2
from measurement.lib.pulsar import pulse, pulselib, element, pulsar
reload(pulsar)
import measurement.lib.measurement2.adwin_ssro.DD_2 as DD; reload(DD)
import measurement.lib.measurement2.adwin_ssro.pulse_select as ps
import LDE_element as LDE_elt; reload(LDE_elt)
execfile(qt.reload_current_setup)
import copy



class purify_single_setup(DD.MBI_C13):

    """
    measurement class for testing when both setups are operating without any PQ instrument 
    for single-setup testing and phase calibrations
    """
    mprefix = 'telcrifcation slave'
    adwin_process = 'purification'
    def __init__(self,name):
        DD.MBI_C13.__init__(self,name)
        #self.joint_params = m2.MeasurementParameters('JointParameters')
        self.params = m2.MeasurementParameters('LocalParameters')
        self.current_setup = qt.current_setup
    

    def reset_plu(self): 
        self.adwin.start_set_dio(dio_no=0, dio_val=0)
        qt.msleep(0.1)
        self.adwin.start_set_dio(dio_no=0, dio_val=1)
        qt.msleep(0.1)
        self.adwin.start_set_dio(dio_no=0, dio_val=0)
        qt.msleep(0.1)

    def autoconfig(self):

        self.channel_dictionary = { 'ch1m1': 'ch1_marker1',
                                    'ch1m2': 'ch1_marker2',
                                    'ch2m1': 'ch2_marker1',
                                    'ch2m2': 'ch2_marker2',
                                    'ch3m1': 'ch3_marker1',
                                    'ch3m2': 'ch3_marker2',
                                    'ch4m1': 'ch4_marker1',
                                    'ch4m2': 'ch4_marker2',}


        for i in range(10):
            self.physical_adwin.Stop_Process(i+1)
            qt.msleep(0.3)
        qt.msleep(1)
        # self.adwin.load_MBI()   
        # New functionality, now always uses the adwin_process specified as a class variables 
        loadstr = 'self.adwin.load_'+str(self.adwin_process)+'()'   
        latest_process = qt.instruments['adwin'].get_latest_process()
        boolish = self.adwin_process in latest_process

        if not boolish:
            print 'executing ADWin load'
            exec(loadstr)
            qt.msleep(1)
        else:
            print 'Omitting adwin load!!! Be wary of your changes!'

        # self.params['LDE1_attempts'] = self.params['LDE1_attempts']
        # self.params['LDE2_attempts'] = self.params['LDE2_attempts']
        
        DD.MBI_C13.autoconfig(self)

        self.params['Carbon_init_RO_wait'] = (self.params['C13_MBI_RO_duration'])*1e-6+50e-6

        # add values from AWG calibrations
        self.params['SP_voltage_AWG'] = \
                self.A_aom.power_to_voltage( self.params['AWG_SP_power'], controller='sec')

        qt.pulsar.set_channel_opt('AOM_Newfocus', 'high', self.params['SP_voltage_AWG'])

        ### Adwin LT4 is connected to the plu. Needs to reset it.
        ####if self.current_setup == self.joint_params['master_setup'] and self.params['is_two_setup_experiment'] > 0:
        ####    self.reset_plu()

        if (self.params['do_general_sweep'] > 0) and (self.params['general_sweep_name'] == 'total_phase_offset_after_sequence'):
            length = self.params['pts']
            self.physical_adwin.Set_Data_Float(np.array(self.params['general_sweep_pts'])%360, 110, 1, length)
        
        elif (self.params['do_general_sweep'] > 0) and (self.params['general_sweep_name'] != 'total_phase_offset_after_sequence'):
            length = self.params['pts']
            self.physical_adwin.Set_Data_Float(np.array(length*[self.params['total_phase_offset_after_sequence']])%360, 110, 1, length)
        
        ### in order to sweep the offset phase for dynamic phase correction we manipulate a data array in the adwin here.


    def run(self, autoconfig=False, setup=False):

        """
        inherited from pulsar msmt.
        """
        if autoconfig:
            self.autoconfig()
       
        
        if setup:
            self.setup()

        # print loadstr 

        length = self.params['nr_of_ROsequences']

        qt.msleep(2)
        self.start_adwin_process(load=False)
        qt.msleep(0.1)
        self.start_keystroke_monitor('abort')
        # self.remote_helper.set_is_running(True)

        while self.adwin_process_running():

            if self.keystroke('abort') != '':
                print 'aborted.'
                self.stop_keystroke_monitor('abort')
                break

            reps_completed = self.adwin_var('completed_reps')
            # try:
            #     self.remote_helper.set_completed_reps(reps_completed)
            # except:
            #     print 'this remote helper thing does not work'
            print('completed %s / %s readout repetitions' % \
                    (reps_completed, self.params['repetitions']))
            qt.msleep(1)

        try:
            self.stop_keystroke_monitor('abort')
        except KeyError:
            pass # means it's already stopped

        self.stop_adwin_process()
        # self.remote_helper.set_is_running(False)

        reps_completed = self.adwin_var('completed_reps')
        print('completed %s / %s readout repetitions' % \
                (reps_completed, self.params['repetitions']))

    def save(self, name='adwindata'):
        reps = self.adwin_var('completed_reps')
        # sweeps = self.params['pts'] * self.params['reps_per_ROsequence']


        self.save_adwin_data(name,
                [   ('CR_before',1, reps),
                    ('CR_after',1, reps),
                    ('Phase_correction_repetitions',1, reps), 
                    ('statistics', 10),
                    ('adwin_communication_time'              ,1,reps),  
                    ('invalid_data_markers'                  ,1,reps), 
                    ('counted_awg_reps'                      ,1,reps),  
                    ('attempts_first'                        ,1,reps),  
                    ('attempts_second'                       ,1,reps), 
                    ('carbon_readout_result'                 ,1,reps),
                    ('electron_readout_result'               ,1,reps),
                    ('ssro_results'                          ,1,reps), 
                    ('compensated_phase'                     ,1,reps), 
                    ('min_phase_deviation'                   ,1,reps), 
                    'completed_reps'
                    ])
        return

    
    def _Trigger_element(self,duration = 10e-6, name='Adwin_trigger', outputChannel='adwin_sync'):
        """
        The Trigger element of DD_2 is changed such that there is a 5 us waiting time at the end of the elements.
        Helps with the adwin counting and saves time for the adwin.
        """

        if outputChannel == 'adwin_sync':
            TrigHigh = pulse.SquarePulse(channel = outputChannel,
                length = duration-5e-6, amplitude = 2)
            TrigLow = pulse.SquarePulse(channel = outputChannel,
                length = 5e-6, amplitude = 0)
            Trig_element = element.Element(name, pulsar=qt.pulsar,
                global_time = True)

            if duration == 10e-6:
                Trig_element.append(TrigLow)
            Trig_element.append(TrigHigh)
            Trig_element.append(TrigLow)

        else:
            #Output channels for lasers are defined on AWG marker channels. Therefore, amplitue=1.=HIGH!
            Trig = pulse.SquarePulse(channel = outputChannel,
                length = duration, amplitude = 1.)
            Trig_element = element.Element(name, pulsar=qt.pulsar,
                global_time = True)
            Trig_element.append(Trig)

        return Trig_element

   

    def restore_msmt_parameters(self):
        """
        Reloads the stored parameters for regular operation.
        """
        self.params['min_phase_correct']    = self.params['stored_min_phase_correct']
        self.params['min_dec_tau']          = self.params['stored_min_dec_tau']
        self.params['max_dec_tau']          = self.params['stored_max_dec_tau'] 
        self.params['dec_pulse_multiple']   = self.params['stored_dec_pulse_multiple'] 
        self.params['Carbon_init_RO_wait']  = self.params['stored_carbon_init_RO_wait']
        self.params['min_dec_duration']     = self.params['min_dec_tau']*self.params['dec_pulse_multiple']*2
        self.params['fast_pi_duration']     = self.params['stored_fast_pi_duration']
        self.params['fast_pi2_duration']    = self.params['stored_fast_pi2_duration']



    def calculate_sequence_duration(self,gate_seq,verbose = False,**kw):
        """
        Input: A list of gates as specified for regular DD sequences:
        Output: The duration of the input sequence in the AWG 
        The calculation includes phase gates and extra us due to triggers and tau_cut.
        Calucation is achieved by running through the flow of DD_2.py / the MBI_C13 class

        Known bug: The length of the first MW element depends on the used channel delays.
        If the Pulsemod delay is larger than 500 ns --> TROUBLE! don't do that!
        Solution --> we implemented a parameter that accounts for this.
        """

        gate_seq = self.generate_AWG_elements(gate_seq,0)


        gate_seq[-1].event_jump = None # necessary manipulation of the last gate. don't change this

        list_of_elements,gate_seq = self.combine_to_AWG_sequence(gate_seq, explicit = True)

        duration = 0

        for e in gate_seq.elements[:-1]: #do not take the ro trigger into account --> omit the last element
            for ee in list_of_elements:
                if ee.name in e['wfname']:
                    duration+=ee.length()*e['repetitions']

                    if verbose:
                        print ee.name,ee.ideal_length(),ee.length(),ee.samples(),e['repetitions'],duration*1e6
        return duration



    
    

    



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

        if Gate.reps == 1:
            if self.params['opt_pi_pulses'] == 2:#i.e. we do barret & kok or SPCorrs etc.
                Gate.event_jump = 'next'
                if self.params['PLU_during_LDE'] > 0:
                    Gate.go_to = 'start'
                else:
                    Gate.go_to = 'next'
            else:
                Gate.event_jump = 'next'
                Gate.go_to = 'start'

                if self.params['PLU_during_LDE'] == 0:
                    Gate.go_to = None
                
                if self.params['do_phase_correction'] == 0 and 'LDE2' in Gate.name:
                    Gate.go_to = None
                    Gate.event_jump = None
                elif (self.params['LDE_1_is_init'] > 0) and ('LDE1' in Gate.name):
                    Gate.go_to = None
                    Gate.event_jump = None
        else:
            Gate.go_to = None
            Gate.event_jump = 'second_next' ### the repeated LDE element has to jump over the final one.

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

      

            ### LDE elements: WE have two LDE elements with potentially different functions
            LDE1 = DD.Gate('LDE1'+str(pt),'LDE')
            LDE1.el_state_after_gate = 'sup'

            if self.params['LDE1_attempts'] > 1:
                LDE1.reps = self.params['LDE1_attempts']-1
                LDE1.is_final = False
                LDE1_final = DD.Gate('LDE1_final_'+str(pt),'LDE')
                LDE1_final.el_state_after_gate = 'sup'
                LDE1_final.reps = 1
                LDE1_final.is_final = True
            else:
                LDE1.is_final = True

            if self.params['LDE1_attempts'] != 1:
                LDE1.reps = self.params['LDE1_attempts'] - 1
            


            ### LDE elements need rephasing or repumping elements
            LDE_rephase1 = DD.Gate('LDE_rephasing_1'+str(pt),'single_element',wait_time = self.params['average_repump_time'])
            LDE_rephase1.scheme = 'single_element'

            LDE_repump1 = DD.Gate('LDE_repump_1_'+str(pt),'Trigger')
            LDE_repump1.duration = 2e-6
            LDE_repump1.elements_duration = LDE_repump1.duration
            LDE_repump1.channel = 'AOM_Newfocus'
            LDE_repump1.el_state_before_gate = '0' 



            e_RO =  [DD.Gate('Tomo_Trigger_'+str(pt),'Trigger',
                wait_time = 10e-6)]

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

                # print 'LDE1 reps',LDE1.reps
                ### append last adwin synchro element 
                if not LDE1.is_final:
                    gate_seq.append(LDE1_final)

                if self.params['do_swap_onto_carbon'] > 0:
                    gate_seq.append(LDE_rephase1)

                elif self.params['LDE_1_is_init'] == 0 and self.params['opt_pi_pulses'] < 2 and self.params['no_repump_after_LDE1'] == 0:
                    gate_seq.append(LDE_repump1)
                    # gate_seq.append(DD.Gate('LDE_1_wait'+str(pt),'passive_elt',wait_time = 3e-6))

            if self.params['do_swap_onto_carbon'] > 0:
                ### Elementes for swapping
                swap_with_init = self.carbon_swap_gate(
                                go_to_element = 'start',
                                pt = pt,
                                addressed_carbon = self.params['carbon'],
                                swap_type               = 'swap_w_init',
                                RO_after_swap           = True)


                if self.params['do_carbon_init'] > 0:
                    ### important to realize that the tau_cut of a potential decoupling sequence can alter the
                    ### electron rephasing element. --> Therefore the element has to be rebuilt
                    self.generate_LDE_rephasing_elt(LDE_rephase1)

                    gate_seq.extend(swap_with_init)
                else:
                    self.generate_LDE_rephasing_elt(LDE_rephase1)

                    gate_seq.extend(swap_with_init)
                    print '*'*20
                    print 'Warning '*4
                    print 'Swap without initialization not implemented'
                    print '*'*20


            if self.params['do_LDE_2'] > 0:
                if gate_seq == []:
                    LDE2.wait_for_trigger = True

                gate_seq.append(LDE2)

                # need a final element for adwin communication
                if self.params['LDE2_attempts']> 1:
                    gate_seq.append(LDE2_final)

                if (self.params['do_purifying_gate'] > 0 or self.params['do_phase_correction'] > 0) and self.params['do_repump_after_LDE2'] == 0:
                    # electron has to stay coherent after LDE attempts
                    self.generate_LDE_rephasing_elt(LDE_rephase2)
                    gate_seq.append(LDE_rephase2)

                else: # this is used if we sweep the number of repetitions for Qmemory testing.
                    gate_seq.append(LDE_repump2)

            if self.params['do_phase_correction'] > 0 and self.params['phase_correct_max_reps']>0:
                gate_seq.extend(dynamic_phase_correct_list)

            if self.params['do_purifying_gate'] > 0:
                gate_seq.extend(carbon_purify_seq)



            if self.params['do_carbon_readout'] > 0:
                if self.params['do_purifying_gate'] >0:
                    ### prepare branching of the sequence
                    gate_seq0 = copy.deepcopy(gate_seq)
                    gate_seq1 = copy.deepcopy(gate_seq)


                    carbon_tomo_seq0 = self.readout_carbon_sequence(
                            prefix              = 'Tomo0',
                            pt                  = pt,
                            go_to_element       = None,
                            event_jump_element  = None,
                            RO_trigger_duration = 10e-6,
                            el_state_in         = 0,
                            carbon_list         = [self.params['carbon']],
                            RO_basis_list       = self.params['Tomography_bases'],
                            readout_orientation = self.params['carbon_readout_orientation']) 
                    gate_seq0.extend(carbon_tomo_seq0)

                    carbon_tomo_seq1 = self.readout_carbon_sequence(
                            prefix              = 'Tomo1',
                            pt                  = pt,
                            go_to_element       = None,
                            event_jump_element  = None,
                            RO_trigger_duration = 10e-6,
                            el_state_in         = 1,
                            carbon_list         = [self.params['carbon']],
                            RO_basis_list       = self.params['Tomography_bases'],
                            readout_orientation = self.params['carbon_readout_orientation']) 
                    gate_seq1.extend(carbon_tomo_seq1)


                    # Make jump statements for branching to two different ROs
                    gate_seq[-1].go_to       = carbon_tomo_seq1[0].name
                    gate_seq[-1].event_jump  = carbon_tomo_seq0[0].name


                    # In the end all roads lead to Rome
                    Rome = DD.Gate('Rome_'+str(pt),'passive_elt',
                            wait_time = 3e-6)
                    gate_seq1.append(Rome)
                    gate_seq0[-1].go_to = gate_seq1[-1].name

                    # take care of electron states after the purification msmt. I.e. the electron state is set during the trigger.
                    
                    gate_seq0[len(gate_seq)-1].el_state_before_gate =  '0' #Element -1
                    gate_seq1[len(gate_seq)-1].el_state_before_gate =  '1' #Element -1

                    ### generate and merge branches
                    gate_seq = self.generate_AWG_elements(gate_seq,pt)
                    gate_seq0 = self.generate_AWG_elements(gate_seq0,pt)
                    gate_seq1 = self.generate_AWG_elements(gate_seq1,pt)

                    merged_sequence = []
                    merged_sequence.extend(gate_seq)
                    merged_sequence.extend(gate_seq0[len(gate_seq):])
                    merged_sequence.extend(gate_seq1[len(gate_seq):])
                    gate_seq = copy.deepcopy(merged_sequence) # for further processing

                else: ### no purifying gate --> we don't need branching!
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
                    # e_RO =  [DD.Gate('Tomo_Trigger_'+str(pt),'Trigger',
                    #     wait_time = 20e-6)]
                    # gate_seq.extend(e_RO)
                # print 'This is the tomography base', self.params['Tomography_bases']
            
            else: #No carbon spin RO? Do espin RO!
                if self.params['do_purifying_gate'] == 0:
                    gate_seq.extend(e_RO)


            ###############################################
            # prepare and program the actual AWG sequence #
            ###############################################

            #### insert elements here

            if not (self.params['do_purifying_gate'] > 0 and self.params['do_carbon_readout'] > 0):
                gate_seq = self.generate_AWG_elements(gate_seq,pt)

            

            #### for carbon phase debbuging purposes.
            # for g in gate_seq:
            #     if not 'correct' in g.name:
            #         print g.name
            #         self.print_carbon_phases(g,[self.params['carbon']],verbose=True)


            ### Convert elements to AWG sequence and add to combined list
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq, explicit=True)
            combined_list_of_elements.extend(list_of_elements)

            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)




