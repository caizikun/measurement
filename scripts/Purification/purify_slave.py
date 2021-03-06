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
    mprefix = 'purifcation slave'
    adwin_process = 'purification'
    def __init__(self,name):
        DD.MBI_C13.__init__(self,name)
        self.joint_params = m2.MeasurementParameters('JointParameters')
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


        #self.adwin.boot() # uncomment to avoid memory fragmentation of the adwin.
        # this is most of the time only necessary if you made a programming error ;)
        # check variable declarations and definitions

        qt.msleep(0.5)

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
            # exec(loadstr)

        self.params['LDE1_attempts'] = self.joint_params['LDE1_attempts']
        self.params['LDE2_attempts'] = self.joint_params['LDE2_attempts']
        
        DD.MBI_C13.autoconfig(self)

        self.params['Carbon_init_RO_wait'] = (self.params['C13_MBI_RO_duration'])*1e-6+50e-6

        # add values from AWG calibrations
        self.params['SP_voltage_AWG'] = \
                self.E_aom.power_to_voltage( self.params['AWG_SP_power'], controller='sec')

        qt.pulsar.set_channel_opt('AOM_Newfocus', 'high', self.params['SP_voltage_AWG'])

        ### Adwin LT4 is connected to the plu. Needs to reset it.
        if self.current_setup == self.joint_params['master_setup'] and self.params['is_two_setup_experiment'] > 0:
            self.reset_plu()

        if (self.params['do_general_sweep'] > 0) and (self.params['general_sweep_name'] == 'total_phase_offset_after_sequence'):
            length = self.params['pts']
            self.physical_adwin.Set_Data_Float(np.array(self.params['general_sweep_pts'])%360, 110, 1, length)
        
        elif (self.params['do_general_sweep'] > 0) and (self.params['general_sweep_name'] != 'total_phase_offset_after_sequence'):
            length = self.params['pts']
            self.physical_adwin.Set_Data_Float(np.array(length*[self.params['total_phase_offset_after_sequence']])%360, 110, 1, length)
        
        if qt.current_setup == 'lt3':
            self.params['Yellow_voltage_AWG'] = \
                    self.repump_aom.power_to_voltage( self.params['Yellow_AWG_power'], controller='sec')
            qt.pulsar.set_channel_opt('AOM_Yellow', 'high', self.params['Yellow_voltage_AWG'])
        
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
                    ('invalid_data_markers'                  ,1,reps), 
                    ('adwin_communication_time'              ,1,reps),  
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

    def load_remote_carbon_params(self,master=True):
        """
        Generates a hypothetical carbon with index = 9 from the joint measurement parameters.
        These parameters are then used for the sequence duration calculation.
        Watch out:  partially overwrites connection element parameters 
                    and stores the old parameters in the msmt_params.
        """

        ps.check_pulse_shape(self) ### this updates parameters for MW pulses.


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
        self.params['stored_min_dec_duration']     = self.params['min_dec_duration']
        self.params['stored_fast_pi_duration']     = self.params['fast_pi_duration']
        self.params['stored_fast_pi2_duration']    = self.params['fast_pi2_duration']

        # overwrite parameters for phase gates for sequence calculation 

        self.params['min_phase_correct'] = self.joint_params[prefix + '_min_phase_correct']
        self.params['min_dec_tau'] = self.joint_params[prefix + '_min_dec_tau']
        self.params['max_dec_tau'] = self.joint_params[prefix + '_max_dec_tau']
        self.params['dec_pulse_multiple'] = self.joint_params[prefix + '_dec_pulse_multiple']
        self.params['Carbon_init_RO_wait'] = self.joint_params[prefix + '_carbon_init_RO_wait']
        self.params['min_dec_duration']    = self.params['min_dec_tau']*self.params['dec_pulse_multiple']*2
        self.params['fast_pi_duration']     = self.joint_params[prefix + '_fast_pi_duration']
        self.params['fast_pi2_duration']    = self.joint_params[prefix + '_fast_pi2_duration']

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


    def calculate_C13_init_duration(self,master = True,**kw):

        # load remote params and store current msmt params
        self.load_remote_carbon_params(master = master) # generate carbon 9 from the joint params

        # generate the list of gates in the remote setting
        carbon_init_seq = DD.MBI_C13.initialize_carbon_sequence(self,go_to_element = 'start',
                    prefix = 'C_Init', pt=0,
                    addressed_carbon = 9,initialization_method = self.params['carbon_init_method'])
        # calculate remote sequence duration
        seq_duration = self.calculate_sequence_duration(carbon_init_seq,)
        
        #restore actual msmt params.
        self.restore_msmt_parameters()

        if master:
            return seq_duration
        else:
            return seq_duration-self.joint_params['master_slave_AWG_first_element_delay']

    def calculate_C13_swap_duration(self,master=True,**kw):
        '''
        Calculates the duration of the swap. At the moment only one swap type supported
        '''
        # load remote params and store current msmt params
        self.load_remote_carbon_params(master = master) # generate carbon 9 from the joint params
        place_holder = kw.pop('addressed_carbon',9)

        # generate the list of gates in the remote setting
        if self.params['do_carbon_init'] > 0:#the carbon has been initialized. use a slight difference in the sequence
            carbon_init_seq = DD.MBI_C13.carbon_swap_gate_multi_options(self,
                                                            prefix = 'C_swap',
                                                            addressed_carbon = 9,**kw)
        else:
            # no C13 init, calculate the other gate sequence.
            # TODO make correct gate sequence in DD_2.py
            carbon_init_seq = []
            print 'Warning: swap without prior initialization not implemented!' 
            return 0


        # calculate remote sequence duration
        seq_duration = self.calculate_sequence_duration(carbon_init_seq,**kw)
        
        #restore actual msmt params.
        self.restore_msmt_parameters()

        #need to also factor the LDE rephasing element in
        if master:
            seq_duration += self.joint_params['master_average_repump_time']
        else:
            seq_duration += self.joint_params['slave_average_repump_time']+self.joint_params['master_slave_AWG_first_element_delay']

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
        master_seq_duration = self.calculate_C13_init_duration(master = True,verbose=False,**kw)
        slave_seq_duration = self.calculate_C13_init_duration(master= False,verbose=False,**kw)
        
        init_RO_wait_diff = self.joint_params['master_carbon_init_RO_wait'] - self.joint_params['slave_carbon_init_RO_wait']

        # print (master_seq_duration+self.joint_params['master_carbon_init_RO_wait'])*1e6,(slave_seq_duration+self.joint_params['slave_carbon_init_RO_wait'])*1e6
        # print 'this is the RO wait before calculation', self.params['Carbon_init_RO_wait']

        do_wait = False
        ### determine whether or not to wait for the other setup
        if self.params['is_two_setup_experiment'] > 0:
            if setup == master_setup and (master_seq_duration-slave_seq_duration + init_RO_wait_diff < 0):
                # adjust the length of the element of the master RO wait time.
                self.params['Carbon_init_RO_wait'] = self.params['Carbon_init_RO_wait'] + slave_seq_duration - master_seq_duration - init_RO_wait_diff
                time_diff = slave_seq_duration - master_seq_duration - init_RO_wait_diff
            
            elif setup != master_setup and (master_seq_duration-slave_seq_duration + init_RO_wait_diff > 0):
                # adjust the length of the element of the slave RO wait time.
                self.params['Carbon_init_RO_wait'] = self.params['Carbon_init_RO_wait'] + master_seq_duration - slave_seq_duration + init_RO_wait_diff
                
                # time_diff = master_seq_duration - slave_seq_duration + init_RO_wait_diff

                # microseconds,nanoseconds = divmod(time_diff*1e9,1e3)
                # self.params['Carbon_init_RO_wait'] = self.params['Carbon_init_RO_wait'] + nanoseconds*1e-9
                # wait_for_other_setup = DD.Gate('wait_for_others_init_'+str(kw.get('pt',0)),'passive_elt',wait_time = (microseconds+2)*1e-6) #+2 because DD_2 thinks it is smart.
                # do_wait = True
        # print 'after calculating for the slave:', (self.params['Carbon_init_RO_wait']+slave_seq_duration)*1e6

        ### prepare the actual sequence with adjusted trigger length.
        seq = DD.MBI_C13.initialize_carbon_sequence(self,**kw)


        if do_wait:
            seq[-1].event_jump = 'next'
            seq.append(wait_for_other_setup)

        ### restore the old value
        self.params['Carbon_init_RO_wait'] = store_C_init_RO_wait

        return seq

    def carbon_swap_gate(self,**kw):
        """
        manipulates the length of the C_init RO_wait in order to correctly synchronize both AWGs
        only does this on the side of the setup with the shorter carbon gate time!
        additionally inserts a wait time to preserve the coherence of the electron state after the LDE element. 
        """
        """
        swap_type               = 'swap_w_init',
        RO_after_swap           = True
        """
        setup = qt.current_setup
        master_setup = self.joint_params['master_setup']
        # store this value as it is also important for the AWG/ADWIN communication
        store_C_init_RO_wait = self.params['Carbon_init_RO_wait']

        # calculate sequence durations 
 
        master_seq_duration = self.calculate_C13_swap_duration(master = True,verbose=False,**kw)

        slave_seq_duration = self.calculate_C13_swap_duration(master= False,verbose=False,**kw)

        init_RO_wait_diff = self.joint_params['master_carbon_init_RO_wait'] - self.joint_params['slave_carbon_init_RO_wait']
        
        # print 'master/slave durations'
        # print (master_seq_duration+self.joint_params['master_carbon_init_RO_wait'])*1e6,(slave_seq_duration+self.joint_params['slave_carbon_init_RO_wait'])*1e6
        # print 'this is the RO wait before calculation', self.params['Carbon_init_RO_wait']
        do_wait = False

        if self.params['is_two_setup_experiment'] > 0:
            if setup == master_setup and (master_seq_duration-slave_seq_duration + init_RO_wait_diff < 0):
                # adjust the length of the element of the master RO wait time.

                self.params['Carbon_init_RO_wait'] = self.params['Carbon_init_RO_wait'] + slave_seq_duration - master_seq_duration - init_RO_wait_diff
            
            elif setup != master_setup and (master_seq_duration-slave_seq_duration + init_RO_wait_diff > 0):
                # adjust the length of the element of the slave RO wait time.
                self.params['Carbon_init_RO_wait'] = self.params['Carbon_init_RO_wait'] + master_seq_duration - slave_seq_duration + init_RO_wait_diff
                # time_diff = master_seq_duration - slave_seq_duration + init_RO_wait_diff

                # microseconds,nanoseconds = divmod(time_diff*1e9,1e3)
                # self.params['Carbon_init_RO_wait'] = self.params['Carbon_init_RO_wait'] + nanoseconds*1e-9
                # wait_for_other_setup = DD.Gate('wait_for_others_swap_'+str(kw.get('pt',0)),'passive_elt',wait_time = (microseconds+2)*1e-6) #+2 because DD_2 thinks it is smart.
                # do_wait = True

        #### In case that we have a large discrepancy in duration for the swap we bridge time by decoupling the electron spin before the swap.
        if self.params['Carbon_init_RO_wait'] - store_C_init_RO_wait > 2000e-6:
            print 'WARNING: Decoupling before Swap gate. I AM BROKEN!!! FIX ME!!!'
            bridged_time = self.params['Carbon_init_RO_wait'] - store_C_init_RO_wait
            no_of_pulses_float = bridged_time/(2*self.params['decouple_before_swap_tau']) ### I for now use the dynamic phase tau with an additional factor of 4. 
            no_of_pulses_int = np.floor(no_of_pulses_float)

            # we only allow an even amount of pulses
            if no_of_pulses_int % 2 == 1:
                no_of_pulses_int -= 1

            # recalculate the trigger duration for the SWAP RO:
            self.params['Carbon_init_RO_wait'] = store_C_init_RO_wait + bridged_time - \
                                                        no_of_pulses_int*2*self.params['decouple_before_swap_tau']

            ElectronDD = DD.Gate('electron_decoupling'+str(kw.get('pt',0)), 'Carbon_Gate',Carbon_ind = self.params['carbon'])
            ElectronDD.N = no_of_pulses_int
            ElectronDD.tau = self.params['decouple_before_swap_tau']
            self.params['ElectronDD_tau'] = ElectronDD.tau ### we create this parameter for communication with LDE element. See _LDE_rephasing_elt(...) in LDE_element.py
            ElectronDD.no_connection_elt = True
            # print 'number of pi pulses in the connection', ElectronDD.N
            ### we rephase by hand here. not recommended usually but crucial to keep the timing correct for both setups!!!
            pi_duration =  self.params['fast_pi_duration']
            c_gate_tau = self.params['C'+str(self.params['carbon'])+'_Ren_tau'+self.params['electron_transition']][0]

            pulse_tau_1              = c_gate_tau - pi_duration/2.0
            n_wait_reps, tau_remaind_1 = divmod(round(2*pulse_tau_1*1e9),1e3) 
            if n_wait_reps %2 == 0:
                tau_cut_1 = 1e-6
            else:
                tau_cut_1 = 1.5e-6

            pulse_tau_2              = ElectronDD.tau - pi_duration/2.0
            n_wait_reps, tau_remaind_2 = divmod(round(2*pulse_tau_2*1e9),1e3) 

            if n_wait_reps %2 == 0:
                tau_cut_2 = 1e-6
            else:
                tau_cut_2 = 1.5e-6

            rephase_wait = tau_cut_1+tau_cut_2

            rephasing_wait_gate  = DD.Gate('Swap_connect_'+str(kw.get('pt',0)),'single_element',wait_time = rephase_wait)
            rephasing_wait_gate.scheme = 'single_element'
            rephasing_wait_gate.elements = [LDE_elt._LDE_rephasing_elt(self,rephasing_wait_gate,forced_wait_duration = rephase_wait)]

            seq = [ElectronDD,rephasing_wait_gate]
        else:
            seq = []
            


        seq.extend(DD.MBI_C13.carbon_swap_gate_multi_options(self,**kw))
        if do_wait:
            seq[-1].event_jump = 'next'
            seq.append(wait_for_other_setup)
        ### restore the old value
        self.params['Carbon_init_RO_wait'] = store_C_init_RO_wait

        return seq




    def generate_delayline_phase_correction_elements(self,g1,g2,g3):
        """
        generate the elements for doing phase correction using the delay line
        """

        pulse_pi = ps.X_pulse(self)

        self_trigger = pulse.SquarePulse(channel='self_trigger',
            length = self.params['self_trigger_duration'],
            amplitude = 2.)

        final_wait = pulse.SquarePulse(channel='adwin_sync',
            length = self.params['self_trigger_duration'], 
            amplitude = 0.)



        ## do stuff generate g1_elt ,g2_elt...
        g1_elt = element.Element(g1.name, pulsar=qt.pulsar, global_time=True)
        g1_elt.append(pulse.cp(self_trigger))

        g2_elt = element.Element(g2.name, pulsar=qt.pulsar, global_time=True)
        g2_elt.append(pulse.cp(pulse_pi))
        g2_elt.append(pulse.cp(self_trigger))

        g3_elt = element.Element(g3.name, pulsar=qt.pulsar, global_time=True)
        g3_elt.append(pulse.cp(final_wait))

        g1.elements = [g1_elt]
        g2.elements = [g2_elt]
        g3.elements = [g3_elt]


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
            if self.joint_params['opt_pi_pulses'] == 2:#i.e. we do barret & kok or SPCorrs etc.
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

            ### if statement to decide what LDE1 does: init of the carbon via swap or entangling.
            if self.params['LDE_1_is_init'] >0:
                if self.params['force_LDE_attempts_before_init'] == 0 or self.params['LDE1_attempts'] == 1: 
                    LDE1.reps = 1
                    LDE1.is_final = True

                    manipulated_LDE_elt = copy.deepcopy(LDE1)
                else:
                    manipulated_LDE_elt = copy.deepcopy(LDE1_final)
                    LDE1.reps = self.params['LDE1_attempts'] - 1

                if self.params['input_el_state'] in ['X','mX','Y','mY']:
                    manipulated_LDE_elt.first_pulse_is_pi2 = True

                    #### define some phases:
                    x_phase = self.params['X_phase']
                    y_phase = self.params['Y_phase']
                    first_mw_phase_dict = { 'X' :   y_phase, 
                                            'mX':   y_phase + 180,
                                            'Y' :   x_phase + 180, 
                                            'mY':   x_phase}

                    manipulated_LDE_elt.first_mw_pulse_phase = first_mw_phase_dict[self.params['input_el_state']]

                elif self.params['input_el_state'] in ['Z']:
                    manipulated_LDE_elt.no_first_pulse = True

                elif self.params['input_el_state'] in ['mZ']:
                    manipulated_LDE_elt.no_mw_pulse = True



                ### clean up by casting the manipulation back onto the original object:
                if self.params['force_LDE_attempts_before_init'] == 0 or self.params['LDE1_attempts'] == 1: 
                    LDE1 = manipulated_LDE_elt
                else:
                    LDE1_final = manipulated_LDE_elt

            ### if more than 1 reps then we need to take the final element into account
            elif self.params['LDE1_attempts'] != 1:
                LDE1.reps = self.params['LDE1_attempts'] - 1
            


            ### LDE elements need rephasing or repumping elements
            LDE_rephase1 = DD.Gate('LDE_rephasing_1'+str(pt),'single_element',wait_time = self.params['average_repump_time'])
            LDE_rephase1.scheme = 'single_element'

            LDE_repump1 = DD.Gate('LDE_repump_1_'+str(pt),'Trigger')
            LDE_repump1.duration = 2e-6
            LDE_repump1.elements_duration = LDE_repump1.duration
            LDE_repump1.channel = 'AOM_Newfocus'
            LDE_repump1.el_state_before_gate = '0' 

            ### Second LDE element goes here.
            LDE2 = DD.Gate('LDE2'+str(pt),'LDE')
            LDE2.el_state_after_gate = 'sup'
            if self.params['LDE2_attempts']>1:
                LDE2.is_final = False
                LDE2.reps = self.params['LDE2_attempts']-1
                LDE2_final = DD.Gate('LDE2_final_'+str(pt),'LDE')
                LDE2_final.el_state_after_gate = 'sup'
                LDE2_final.reps = 1
                LDE2_final.is_final = True
            else:
                LDE2.is_final = True

            ### LDE elements need rephasing or RO elements afterwards
            LDE_rephase2 = DD.Gate('LDE_rephasing_2_'+str(pt),'single_element',wait_time = self.params['average_repump_time'])
            LDE_rephase2.scheme = 'single_element'


            LDE_repump2 = DD.Gate('LDE_RO_2_'+str(pt),'Trigger')
            LDE_repump2.duration = 10e-6
            LDE_repump2.elements_duration = LDE_repump2.duration
            LDE_repump2.channel ='AOM_Newfocus'
            LDE_repump2.el_state_before_gate = '0'


            ################################
            ### Dynamic phase correction ###
            ################################

            #### put jesse phawse correction gates here
            if self.params['do_phase_fb_delayline'] > 0:
                #generate gates g1,g2,g3

                g1 = DD.Gate(
                    'C13_correct_delay_start' +str(pt),
                    'single_element',
                    no_connection_elt = True
                    )
                g1.scheme = 'single_element'

                g2 = DD.Gate(
                    'C13_correct_delay_pi' + str(pt),
                    'single_element',
                    no_connection_elt = True,
                    wait_for_trigger = True
                    )
                g2.scheme = 'single_element'

                g3 = DD.Gate(
                    'C13_correct_delay_wait' + str(pt),
                    'single_element',
                    no_connection_elt = True,
                    wait_for_trigger = True
                    )
                g3.scheme = 'single_element'

                self.generate_delayline_phase_correction_elements(g1,g2,g3)
                dynamic_phase_correct_list = [g1,g2,g3]
            else:
                final_dynamic_phase_correct_even = DD.Gate( #### this gate does X - mX for the applied pi-pulses
                        'Final_C13_correct_even'+str(pt),
                        'Carbon_Gate',
                        Carbon_ind  = self.params['carbon'], 
                        tau         = self.params['dynamic_phase_tau'],
                        N           = self.params['dynamic_phase_N'], 
                        no_connection_elt = True,
                        go_to = 'second_next')

                final_dynamic_phase_correct_odd = DD.Gate( ### this gate does X - Y in order to finish off a clean XY-4 sequence
                        'Final_C13_correct_odd'+str(pt),
                        'Carbon_Gate',
                        Carbon_ind  = self.params['carbon'], 
                        tau         = self.params['dynamic_phase_tau'],
                        N           = self.params['dynamic_phase_N'], 
                        no_connection_elt = True)

                ### by definition the AWG does not have to do anything here. --> therefore we reset the phase
                final_dynamic_phase_correct_even.scheme = 'carbon_phase_feedback_end_elt'
                final_dynamic_phase_correct_even.C_phases_after_gate = [None]*10
                final_dynamic_phase_correct_even.C_phases_after_gate[self.params['carbon']] = 'reset'

                final_dynamic_phase_correct_odd.scheme = 'carbon_phase_feedback_end_elt'
                final_dynamic_phase_correct_odd.C_phases_after_gate = [None]*10
                final_dynamic_phase_correct_odd.C_phases_after_gate[self.params['carbon']] = 'reset'
                ### apply phase correction to the carbon. gets a jump element via the adwin to the next element.

                start_dynamic_phase_correct = DD.Gate(
                        'Start_C13_Phase_correct'+str(pt),
                        'Carbon_Gate',
                        Carbon_ind          = self.params['carbon'], 
                        event_jump          = final_dynamic_phase_correct_odd.name,
                        tau                 = self.params['dynamic_phase_tau'],
                        N                   = self.params['dynamic_phase_N'], 
                        no_connection_elt = True)

                # additional parameters needed for DD_2.py
                start_dynamic_phase_correct.scheme = 'carbon_phase_feedback_start_elt'

                dynamic_phase_correct_list = [start_dynamic_phase_correct]

                for i in range(self.params['phase_correct_max_reps']-2):

                    if (i+1) % 2 == 0:
                        dynamic_phase_correct = DD.Gate(
                                'C13_Phase_correct'+str(pt)+'_'+str(i),
                                'Carbon_Gate',
                                Carbon_ind          = self.params['carbon'], 
                                event_jump          = final_dynamic_phase_correct_odd.name, ### odd because the starting element counts as the first correction
                                tau                 = self.params['dynamic_phase_tau'],
                                N                   = self.params['dynamic_phase_N'], 
                                no_connection_elt = True)
                    else:
                        dynamic_phase_correct = DD.Gate(
                                'C13_Phase_correct'+str(pt)+'_'+str(i),
                                'Carbon_Gate',
                                Carbon_ind          = self.params['carbon'], 
                                event_jump          = final_dynamic_phase_correct_even.name,
                                tau                 = self.params['dynamic_phase_tau'],
                                N                   = self.params['dynamic_phase_N'], 
                                no_connection_elt = True)

                    # additional parameters needed for DD_2.py
                    dynamic_phase_correct.scheme = 'carbon_phase_feedback'
                    dynamic_phase_correct.reps = 1
                    ### append to list
                    dynamic_phase_correct_list.append(dynamic_phase_correct)

                #### finish the list of phase correcting gates
                dynamic_phase_correct_list.append(final_dynamic_phase_correct_even)
                dynamic_phase_correct_list.append(final_dynamic_phase_correct_odd)


            #######################
            ##### purify gate #####
            #######################

            carbon_purify_seq = self.readout_carbon_sequence(
                prefix              = 'Purify',
                pt                  = pt,
                go_to_element       = None,
                event_jump_element  = None,
                RO_trigger_duration = self.params['Carbon_init_RO_wait'],
                el_state_in         = 0, # gives a relative phase correction.
                carbon_list         = [self.params['carbon']],
                RO_basis_list       = ['X'])

            ####
            #### some variations of the purifcation gate for testing
            ####
            
            #uncomment for the investigation of our asymmetric RO:
            # del carbon_purify_seq[-2] # get rid of the last pi/2 pulse.
            # del carbon_purify_seq[0]

            ### uncomment for testing the electron coherence after the purifying gate
            #elec_toY = DD.Gate('Pi2onEL'+'_x_pt'+str(pt),'electron_Gate',
            #             Gate_operation='pi2',
            #             phase = self.params['X_phase'])
            # e_RO_puri =  DD.Gate('Puri_Trigger_'+str(pt),'Trigger',
            #             wait_time = 80e-6,go_to = None, event_jump = None)  
            # carbon_purify_seq = [elec_toY,e_RO_puri]

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

                elif self.params['LDE_1_is_init'] == 0 and self.joint_params['opt_pi_pulses'] < 2 and self.params['no_repump_after_LDE1'] == 0:
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
            self.dump_AWG_seq()
        else:

            print 'upload = false, no sequence uploaded to AWG'
            


