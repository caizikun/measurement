"""
Contains the single-setup experiments of the purification project.

NK 2016
"""
import numpy as np
import qt

execfile(qt.reload_current_setup)
import measurement.lib.measurement2.measurement as m2
from measurement.lib.pulsar import pulse, pulselib, element, pulsar
reload(pulsar)
import measurement.lib.measurement2.adwin_ssro.DD_2 as DD; reload(DD)
import LDE_element as LDE_elt; reload(LDE_elt)



class purify_single_setup(DD.MBI_C13):

    """
    measurement class for testing when both setups are operating without any PQ instrument 
    for single-setup testing and phase calibrations
    """
    mprefix = 'purifcation slave'
    adwin_process = 'MBI_multiple_C13' ### TODO make adwin script with 'no mbi' flag

    def __init__(self,name):
        DD.MBI_C13.__init__(self,name)
        self.joint_params = m2.MeasurementParameters('JointParameters')
        self.params = m2.MeasurementParameters('LocalParameters')

    def autoconfig(self):
        DD.MBI_C13.autoconfig(self)


        # add values from AWG calibrations
        self.params['SP_voltage_AWG'] = \
                self.A_aom.power_to_voltage(
                        self.params['AWG_SP_power'], controller='sec')

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

    # def initialize_carbon_sequence(**kw):
    #     """
    #     manipulates the length of the C_init RO_wait in order to correctly synchronize both AWGs
    #     only does this on the side of master AWG.
    #     """

    #     store_C_init_RO_wait = self.params['Carbon_init_RO_wait']

    #     master_REN_duration = self.joint_params['master_Ren_N']*2*self.joint_params['master_Ren_tau']
    #     slave_REN_duration = self.joint_params['slave_Ren_N']*2*self.joint_params['slave_Ren_tau']
    #     master_slave_diff = 2*(master_REN_duration - slave_REN_duration)
    #     if setup == master_setup and master_REN_duration-slave_REN_duration:
            
    #         carbon_str = str(kw.get('addressed_carbon',1))
    #         ### calculate the necessary wait length.
    #         if 
    #         self.params['Carbon_init_RO_wait'] = self.params['slave_init_RO_wait'] + slave_REN_duration - local_REN_duration

    #     seq = MBI_C13.initialize_carbon_sequence(**kw)

    #     ### restore the old value
    #     self.params['Carbon_init_RO_wait'] = store_C_init_RO_wait

    #     return seq



    def generate_AWG_sync_elt(self,Gate):
        ### used in non-local msmts syncs master and slave AWGs
        ### uses the scheme 'single_element'
        
        #if self.joint_params['master_setup'] == qt.current_setup:
        Gate.elements = [LDE_elt._master_sequence_start_element(self,Gate)]
        Gate.wait_for_trigger = True
        # else: not used!
        #     Gate.elements = [LDE_elt._slave_Sequence_start_element]

    def generate_LDE_element(self,Gate):
        """
        the parent function in DD_2 is overwritten by this special function that relies solely on
        msmt_params, joint_params & params_lt3 / params_lt4.
        """

        LDE_elt.generate_LDE_elt(self,Gate)

        if self.joint_params['opt_pi_pulses'] == 2:#i.e. we do barret & kok
            Gate.event_jump = 'start'
        else:
            Gate.event_jump = 'next'


    def generate_sequence(self,upload=True,debug=False):
        """
        generate the sequence for the purification experiment.
        Tries to be as general as possible in order to suffice for multiple calibration measurements
        """


        ### initialize empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Purification')

        for pt in range(self.params['pts']):

            #sweep parameter
            if self.params['do_general_sweep'] == 1:
                self.params[self.params['general_sweep_name']] = self.params['general_sweep_pts'][i]

            gate_seq = []


            ### generate all gates within the sequence
            AWG_sync_wait = DD.Gate('AWG_sync','single_element',wait_time = self.params['AWG_wait_for_lt3_start'] )
            AWG_sync_wait.scheme = 'single_element'
            self.generate_AWG_sync_elt(AWG_sync_wait)
            ### Nitrogen MBI
            mbi = DD.Gate('MBI_'+str(pt),'MBI')
            
            ### initialize carbon in +Z
            carbon_init_seq = self.initialize_carbon_sequence(go_to_element = 'start',
                    prefix = 'C_Init', pt =pt,
                    addressed_carbon = self.params['carbon'])

            ### LDE elements
            LDE1 = DD.Gate('LDE1'+str(pt),'LDE')
            LDE2 = DD.Gate('LDE2'+str(pt),'LDE')

            ### Elementes for swapping
            swap_with_init = self.carbon_swap_gate(
                            go_to_element = 'start',
                            pt = pt,
                            addressed_carbon = self.params['carbon'])

            ### need to write this method XXX
            #swap_without_init = 

            ### apply phase correction to the carbon. gets a jump element via the adwin to the next element.
            dynamic_phase_correct = DD.Gate(
                    'C13_Phase_correct'+str(pt),
                    'Carbon_Gate',
                    Carbon_ind          = self.params['carbon'], 
                    event_jump          = 'next',
                    tau                 = 1/self.params['C'+str(self.params['carbon'])+'_freq_0'],
                    N                   = 2)
            # additional parameters needed for DD_2.py
            dynamic_phase_correct.scheme = 'carbon_phase_feedback'
            dynamic_phase_correct.reps = self.params['phase_correct_max_reps']-1

            final_dynamic_phase_correct = DD.Gate(
                    'Final C13_Phase_correct'+str(pt),
                    'Carbon_Gate',
                    Carbon_ind  = self.params['carbon'], 
                    tau         = 1/self.params['C'+str(self.params['carbon'])+'_freq_0'],
                    N           = 2,
                    no_connection_elt = True)


            ### this really needs to be combined with the RO MW (not if tau_cut does it's job!)
            #pulse
            final_dynamic_phase_correct.scheme = 'carbon_phase_feedback_end_elt'
            final_dynamic_phase_correct.C_phases_after_gate = [None]*10
            final_dynamic_phase_correct.C_phases_after_gate[self.params['carbon']] = 'reset'

            carbon_purify_seq = self.readout_carbon_sequence(
                prefix              = 'Purify',
                pt                  = pt,
                go_to_element       = None,
                event_jump_element  = None,
                RO_trigger_duration = 10e-6,
                el_state_in         = 0, # gives a relative phase correction.
                carbon_list         = [self.params['carbon']],
                RO_basis_list       = ['X'])
                

            carbon_tomo_seq = self.readout_carbon_sequence(
                    prefix              = 'Tomo',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    el_state_in         = 0,
                    carbon_list         = [self.params['carbon']],
                    RO_basis_list       = self.params['Tomography_bases']) 

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




            ###
            ### append all necessary gates according to the current measurement


            if self.params['do_N_MBI'] > 0: 
                ### needs corresponding adwin parameter (Nr_N_init)
                gate_seq.append(mbi)

            # if self.params['non_local'] > 0 and self.joint_params['master_setup'] == qt.current_setup:
            #     # master AWG gets the first trigger and has to wait for the slave awg to respond
            #     gate_seq.append(AWG_sync_wait)

            if self.params['init_carbon'] > 0:
                ### needs corresponding adwin parameter (Nr_C13_init)
                if gate_seq != []:
                    carbon_init_seq[0].wait_for_trigger = False

                gate_seq.extend(carbon_init_seq)

            if self.params['do_LDE_1'] > 0:
                ### needs corresponding adwin parameter 
                if gate_seq == []:
                    LDE1.wait_for_trigger = True
                gate_seq.append(LDE1)
                #insert wait gate for AOM delay when measuring on carbon spins!

            if self.params['swap_onto_carbon'] > 0:
                if self.params['init_carbon']:
                    # put simons gate seq here
                    gate_seq.extend(swap_with_init)
                else:
                    #do full swap: see the 'sten' function.
                    pass

            if self.params['do_LDE_2'] > 0:
                gate_seq.append(LDE2)
                #insert wait gate for AOM delay!

            if self.params['phase_correct'] > 0:
                gate_seq.extend([dynamic_phase_correct,final_dynamic_phase_correct])

            if self.params['purify'] > 0:
                gate_seq.extend(carbon_purify_seq)

            if self.params['final_RO_in_adwin'] == 0:

                if self.params['C13_RO'] > 0:
                    gate_seq.extend(carbon_tomo_seq)

                else: #No carbon spin RO? Do espin RO!
                    gate_seq.extend(e_RO)



            #### insert elements here
            gate_seq = self.generate_AWG_elements(gate_seq,pt)

            ### Convert elements to AWG sequence and add to combined list
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq, explicit=True)
            combined_list_of_elements.extend(list_of_elements)

            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)


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
    adwin_process = purification
