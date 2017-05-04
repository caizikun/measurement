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
import measurement.lib.measurement2.adwin_ssro.DD_2 as DD;reload(DD)
import measurement.lib.measurement2.adwin_ssro.pulse_select as ps
import sce_expm_LDE_element as LDE_elt; reload(LDE_elt)
execfile(qt.reload_current_setup)
import copy

class SingleClickEntExpm(DD.MBI_C13):

    """
    measurement class for testing when both setups are operating without any PQ instrument 
    for single-setup testing and phase calibrations
    """
    mprefix = 'single_click_ent'
    adwin_process = 'single_click_ent'
    # adwin_process = 'MBI_multiple_C13'
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

        for i in range(10):
            self.physical_adwin.Stop_Process(i+1)
            qt.msleep(0.3)
        qt.msleep(1)
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


        self.params['LDE_attempts'] = self.joint_params['LDE_attempts']
        
        DD.MBI_C13.autoconfig(self)

        # add values from AWG calibrations
        self.params['SP_voltage_AWG'] = \
                self.A_aom.power_to_voltage( self.params['AWG_SP_power'], controller='sec')

        # qt.pulsar.set_channel_opt('AOM_Newfocus', 'high', self.params['SP_voltage_AWG'])

        ### Adwin LT4 is connected to the plu. Needs to reset it.
        if self.current_setup == self.joint_params['master_setup'] and self.params['is_two_setup_experiment'] > 0:
            self.reset_plu()
        

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
        stab_reps = self.adwin_var('store_index_stab')
        
        toSave =   [   ('CR_before',1, reps),
                    ('CR_after',1, reps),
                    ('statistics', 10),
                    ('adwin_communication_time'              ,1,reps),  
                    ('counted_awg_reps'                      ,1,reps),  
                    ('ssro_results'                          ,1,reps), 
                    ('DD_repetitions'                        ,1,reps),
                    ('invalid_data_markers'                  ,1,reps),  
                    'completed_reps',
                    'store_index_stab'
                    ]

        # if self.params['record_expm_params']::
        #     toSave.extend(
        #             [('expm_mon_taper_freq'          ,1,reps), 
        #              ('expm_mon_nf_freq'             ,1,reps), 
        #              ('expm_mon_yellow_freq'         ,1,reps), 
        #              ('expm_mon_gate_voltage'        ,1,reps), 
        #              ('expm_mon_cr_counts'           ,1,reps), 
        #              ('expm_mon_repump_counts'       ,1,reps)]) 
            
        if self.params['do_phase_stabilisation']:
            toSave.append(('pid_counts_1',1,stab_reps*self.params['pid_points']))
            toSave.append(('pid_counts_2',1,stab_reps*self.params['pid_points']))
        
        if self.params['only_meas_phase']: 
            toSave.append(('sampling_counts_1',1,reps*self.params['sample_points']))
            toSave.append(('sampling_counts_2',1,reps*self.params['sample_points']))

        
        self.save_adwin_data(name,toSave)

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

    def generate_LDE_rephasing_elt(self,Gate):
        """
        Is used to rephase the electron spin after a successful entanglement generation event.
        uses the scheme 'single_element' --> this will throw a warning in DD_2.py
        """
        LDE_elt.generate_LDE_rephasing_elt(self,Gate)
        Gate.wait_for_trigger = False

    def generate_LDE_element(self,Gate):
        """
        the parent function in DD_2 is overwritten by this special function that relies solely on
        msmt_params, joint_params & params_lt3 / params_lt4.
        """

        LDE_elt.generate_LDE_elt(self,Gate)

        if Gate.is_final == 1: ### final LDe element has only one rep.
            if self.joint_params['opt_pi_pulses'] == 2:#i.e. we do barret & kok or SPCorrs etc.
                Gate.event_jump = 'next'
                if self.params['PLU_during_LDE'] > 0:
                    Gate.go_to = 'end' # go to the last trigger that signifies the Adwin you are done
                else:
                    Gate.go_to = 'next'
            else:
                Gate.event_jump = 'next'
                Gate.go_to = 'Fail_done'+str(self.pt)#'end' # go to the last trigger that signifies the Adwin you are done

                if self.params['PLU_during_LDE'] == 0:
                    Gate.go_to = None
                
                if (self.params['LDE_is_init'] > 0) and ('LDE' in Gate.name):
                    Gate.go_to = None
                    Gate.event_jump = None
        else:
            Gate.go_to = None
            Gate.event_jump ='LDE_rephasing_'+str(self.pt) ### the repeated LDE element has to jump to the rephasing element upon trigger.

    def generate_sequence(self,upload=True,debug=False):
        """
        generate the sequence for the single click experiment.
        Tries to be as general as possible in order to suffice for multiple calibration measurements
        """

        if self.params['only_meas_phase']:
            return # NO AWG NEEDED

        ### initialize empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('SingleClickEnt')

        ### create a list of gates according to the current sweep.
        for pt in range(self.params['pts']):
            self.pt = pt
            #sweep parameter
            if self.params['do_general_sweep'] == 1:
                self.params[self.params['general_sweep_name']] = self.params['general_sweep_pts'][pt]

            gate_seq = []

            LDE = DD.Gate('LDE'+str(pt),'LDE')

            if self.params['LDE_attempts'] > 1:
                LDE.reps = self.params['LDE_attempts']-1
                LDE.is_final = False
                LDE_final = DD.Gate('LDE_final_'+str(pt),'LDE')
                LDE_final.reps = 1
                LDE_final.is_final = True
            else:
                LDE.is_final = True

            ### if statement to decide what LDE does: entangling or just make a specific e state.
            if self.params['LDE_is_init'] >0:
                if self.params['force_LDE_attempts_before_init'] == 0 or self.params['LDE_attempts'] == 1: 
                    LDE.reps = 1
                    LDE.is_final = True

                    manipulated_LDE_elt = copy.deepcopy(LDE)
                else:
                    manipulated_LDE_elt = copy.deepcopy(LDE_final)
                    LDE.reps = self.params['LDE_attempts'] - 1

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
                if self.params['force_LDE_attempts_before_init'] == 0 or self.params['LDE_attempts'] == 1: 
                    LDE = manipulated_LDE_elt
                else:
                    LDE_final = manipulated_LDE_elt

            ### if more than 1 reps then we need to take the final element into account
            elif self.params['LDE_attempts'] != 1:

                ############ do the yellow check here!
                LDE.reps = self.params['LDE_attempts'] - 1

                if self.params['do_yellow_with_AWG'] > 0:
                    LDE_list = []
                    LDE_reionize = DD.Gate('LDE_reionize_'+str(pt),'Trigger')
                    LDE_reionize.duration = self.joint_params['Yellow_AWG_duration']
                    LDE_reionize.elements_duration = LDE_reionize.duration
                    LDE_reionize.channel = 'AOM_Newfocus' #### this needs to change

                    LDE_rounds, remaining_LDE_reps = divmod(LDE.reps,self.joint_params['LDE_attempts_before_yellow'])

                    for i in range(LDE_rounds):
                        #### when putting more stuff in the AWG have to make sure that names are unique
                        ## LDE elts
                        L = copy.deepcopy(LDE)
                        L.name = L.name + '_' + str(i)
                        L.reps = self.joint_params['LDE_attempts_before_yellow']
                        LDE_list.append(L)

                        ### yellow elts
                        Y = copy.deepcopy(LDE_reionize)
                        Y.name = Y.name + '_' + str(i)

                        LDE_list.append(Y)


                    LDE.reps = remaining_LDE_reps
                    LDE.name = LDE.name + str(1+i)
                    LDE_list.append(LDE)

                    ### shelf in a reionization element after so and so many LDE attempts
                    #self.joint_params['LDE_attempts_before_yellow']
                else:
                    LDE_list = [LDE]
            else:
                LDE_list = [LDE]

            ### LDE elements need rephasing or repumping elements
            LDE_repump = DD.Gate('LDE_repump_'+str(pt),'Trigger')
            LDE_repump.duration = 2e-6
            LDE_repump.elements_duration = LDE_repump.duration
            LDE_repump.channel = 'AOM_Newfocus'
            LDE_repump.el_state_before_gate = '0' 

            LDE_rephasing = DD.Gate('LDE_rephasing_'+str(pt),'single_element')
            LDE_rephasing.scheme = 'single_element'
            self.generate_LDE_rephasing_elt(LDE_rephasing)
            LDE_rephasing.go_to = 'Tomo_Trigger_'+str(pt)

            e_RO =  [DD.Gate('Tomo_Trigger_'+str(pt),'Trigger',
                wait_time = 10e-6)]
            Fail_done =  DD.Gate('Fail_done'+str(pt),'Trigger',
                wait_time = 10e-6)
            Fail_done.go_to = 'wait_for_adwin_'+str(pt)#LDE_list[0].name


            #######################################################################
            ### append all necessary gates according to the current measurement ###
            #######################################################################
            waiting_for_adwin = DD.Gate('wait_for_adwin_'+str(pt),'passive_elt',wait_time = 10e-6)
            waiting_for_adwin.wait_for_trigger = True
            gate_seq.append(waiting_for_adwin)
            if self.params['do_N_MBI'] > 0: 
                ### Nitrogen MBI
                mbi = DD.Gate('MBI_'+str(pt),'MBI')
                gate_seq.append(mbi)

            #### insert a MW pi pulse when repumping
            if self.params['MW_before_LDE'] > 0:
                mw_pi = DD.Gate('elec_pi_'+str(pt),'electron_Gate',
                    Gate_operation='pi')

                if gate_seq == []:
                    mw_pi.wait_for_trigger = True
                gate_seq.append(mw_pi)


            if self.params['do_LDE'] > 0:
                ### needs corresponding adwin parameter 
                if gate_seq == []:
                    LDE_list[0].wait_for_trigger = True
                gate_seq.extend(LDE_list)

                ### append last adwin synchro element 
                if not LDE_list[0].is_final:
                    gate_seq.append(LDE_final)
                    gate_seq.append(LDE_rephasing)

                    
                    if self.params['PLU_during_LDE'] > 0:
                        gate_seq.append(Fail_done)

                elif self.params['LDE_is_init'] == 0 and self.joint_params['opt_pi_pulses'] < 2 and self.params['no_repump_after_LDE'] == 0:
                    gate_seq.append(LDE_repump)

                else:
                    ### there is only a single LDE repetition in the LDE element and we do not repump. 
                    ### --> add the rephasing element
                    gate_seq.append(LDE_rephasing)
            # gate_seq.append(LDE_repump)
            gate_seq.extend(e_RO)


            ###############################################
            # prepare and program the actual AWG sequence #
            ###############################################

            #### insert elements here
            gate_seq = self.generate_AWG_elements(gate_seq,pt)

            ### Convert elements to AWG sequence and add to combined list
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq, explicit=True)
            combined_list_of_elements.extend(list_of_elements)

            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)
        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug,verbose=False)
        else:

            print 'upload = false, no sequence uploaded to AWG'
            


