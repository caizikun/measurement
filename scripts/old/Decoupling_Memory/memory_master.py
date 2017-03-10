"""
Contains all measurement that are derived from dynamical decoupling and used in this project.
"""
import numpy as np

import qt
import copy
from measurement.lib.pulsar import pulse, pulselib, element, pulsar
reload(pulsar)

import measurement.lib.measurement2.adwin_ssro.DD_2 as DD; reload(DD)
from measurement.lib.measurement2.adwin_ssro.DD_2 import Gate

class NuclearHahnEchoWithInitialization(MBI_C13):
    '''
    Made by Michiel based on NuclearRamseyWithInitialization_v2
    This class is to measure T2 using a Hahn Echo
    1. Nitrogen MBI initialisation
    2. Wait time tau
    3. Pi pulse on nuclear spin
    4. Wait time tau
    5. Pi/2 pulse on nuclear spin and read out in one function
    Start time pi pulse = tau - 0.5*time pi gate

    Sequence: |N-MBI| -|CinitA|-|Wait t|-|Carbon pi|-|Wait t|-|Tomography|
    '''
    mprefix = 'CarbonHahnInitialised' #Changed
    adwin_process = 'MBI_multiple_C13'
    echo_choice = 'TwoPiPulses' #Default echo choice

    def generate_sequence(self, upload=True, debug=False):
        pts = self.params['pts']

        ### initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Initialized Nuclear Ramsey Sequence')

        for pt in range(pts): ### Sweep over trigger time (= wait time)
            gate_seq = []

            ### Nitrogen MBI GOOD
            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]; gate_seq.extend(mbi_seq)

            ### Carbon initialization GOOD initializes in |+X>
            carbon_init_seq = self.  initialize_carbon_sequence(go_to_element = mbi,
                prefix = 'C_MBI_',
                wait_for_trigger      = True, pt =pt,
                initialization_method = self.params['C13_init_method'],
                C_init_state          = self.params['init_state'],
                addressed_carbon      = self.params['carbon_nr'],
                el_RO_result          = str(self.params['C13_MBI_RO_state']),
                el_after_init         = str(self.params['el_after_init']))
            gate_seq.extend(carbon_init_seq)

            print 'SHUTTER RISE', self.params['Shutter_rise_time']

            ### Pi-Gate option1: non detuned pi gate "in once" gate
            if self.echo_choice == 'SinglePi':
                C_Echo = Gate('C_echo_'+str(pt), 'Carbon_Gate',
                        Carbon_ind =self.params['carbon_nr'],
                        phase = self.params['C13_X_phase'])
                C_Echo.operation='pi'
                self.params['Carbon_pi_duration'] = 2 * self.params['C'+str(self.params['carbon_nr'])+'_Ren_N'+self.params['electron_transition']][0] * self.params['C'+str(self.params['carbon_nr'])+'_Ren_tau'+self.params['electron_transition']][0]

            ### Pi-Gate option: two pi/2 gates, (or in fact two pi over detuned axis)
            elif self.echo_choice == 'TwoPiPulses':
                C_Echo = Gate('C_echo'+str(pt), 'Carbon_Gate',
                        Carbon_ind =self.params['carbon_nr'],
                        phase = self.params['C13_X_phase']) #Wellicht reset?
                # Calculate gate duration as exact gate duration can only be calculated after sequence is configured

                self.params['Carbon_pi_duration'] = 4 * self.params['C'+str(self.params['carbon_nr'])+'_Ren_N'+self.params['electron_transition']][0] * self.params['C'+str(self.params['carbon_nr'])+'_Ren_tau'+self.params['electron_transition']][0]
                C_Echo_2 = Gate('C_echo2_'+str(pt), 'Carbon_Gate',
                        Carbon_ind =self.params['carbon_nr'],
                        phase = self.params['C13_X_phase'])
                # self.params['Carbon_pi_duration'] += 2 * C_Echo_2.N * C_Echo_2.tau


            ### First free evolution_time
                ### Check if free evolution time is larger than the RO time + 0.5* pi pulse duration  (it can't be shorter)
            if self.params['add_wait_gate'] == True:
                if self.params['free_evolution_time'][pt]< (3e-6+self.params['Carbon_pi_duration']/2.):
                    print ('Error: carbon evolution time (%s) is shorter than 0.5 times carbon Pi duration (%s)'
                            %(self.params['free_evolution_time'][pt],self.params['Carbon_init_RO_wait']+self.params['Carbon_pi_duration']/2.))
                    qt.msleep(5)
                    ### Add waiting time
                wait_gate = Gate('Wait_gate_'+str(pt),'passive_elt',
                         wait_time = self.params['free_evolution_time'][pt]-self.params['Carbon_pi_duration']/2.)
                wait_seq = [wait_gate]; gate_seq.extend(wait_seq)

            # Adding pi pulse to gate_seq
            gate_seq.extend([C_Echo])
            if self.echo_choice != 'SinglePi':
                gate_seq.extend([C_Echo_2])


            ### Second free evolution_time
                ### Check if free evolution time is larger than 0.5* pi pulse duration  (it can't be shorter)
            if self.params['add_wait_gate'] == True:
                if self.params['free_evolution_time'][pt]< (3e-6+self.params['Carbon_pi_duration']/2.):
                    print ('Error: carbon evolution time (%s) is shorter than 0.5 times Carbon Pi duration (%s)'
                            %(self.params['free_evolution_time'][pt],self.params['Carbon_init_RO_wait']+self.params['Carbon_pi_duration']/2.))
                    qt.msleep(5)
                    ### Add waiting time
                wait_gate_2 = Gate('Wait_gate2_'+str(pt),'passive_elt',
                         wait_time = self.params['free_evolution_time'][pt]-self.params['Carbon_pi_duration']/2.)
                wait_seq2 = [wait_gate_2]; gate_seq.extend(wait_seq2)

            ### Readout
            carbon_tomo_seq = self.readout_carbon_sequence(
                    prefix              = 'Tomo',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = [self.params['carbon_nr']],
                    RO_basis_list       = [self.params['C_RO_phase'][pt]],
                    el_state_in         = self.params['el_after_init'],
                    readout_orientation = self.params['electron_readout_orientation'])
            gate_seq.extend(carbon_tomo_seq)

            gate_seq = self.generate_AWG_elements(gate_seq,pt) # this will use resonance = 0 by default in

            ### Convert elements to AWG sequence and add to combined list
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq, explicit=True)
            combined_list_of_elements.extend(list_of_elements)

            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)

            if not debug:
                print '*'*10
                for g in gate_seq:
                    print g.name

            if debug:
                for g in gate_seq:
                    print g.name
                    if (g.C_phases_before_gate[self.params['carbon_nr']] == None):
                        print "[ None]"
                    else:
                        print "[ %.3f]" %(g.C_phases_before_gate[self.params['carbon_nr']]/np.pi*180)

                    if (g.C_phases_after_gate[self.params['carbon_nr']] == None):
                        print "[ None]"
                    else:
                        print "[ %.3f]" %(g.C_phases_after_gate[self.params['carbon_nr']]/np.pi*180)

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'

class NuclearDD(MBI_C13):
    '''
    Made by Michiel based on NuclearHahnEchoWithInitialization
    This class is to measure Tcoh using XY4
    1. Nitrogen MBI initialisation
    2. MBI initialization nuclear spin
    3. DD on carbons
    5. Pi/2 pulse on nuclear spin and read out in one function
    Start time pi pulse = tau - 0.5*time pi gate

    Sequence: |N-MBI| -|CinitA|-|DD on carbons|-|Tomography|

    Pulse sequences
    X (x)^n
    XmX (x mx)^n
    XY-4 (xyxy)**n
    XY-8 (xyxy yxyx)**n
    XY-16 (xyxy yxyx mxmymxmy mymxmymx)**n

    '''
    mprefix = 'NuclearDD' #Changed
    adwin_process = 'MBI_multiple_C13'

    def generate_sequence(self, upload=True, debug=False):
        pts = self.params['pts']

        ### initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Initialized Nuclear Ramsey Sequence')

        # Calculate gate duration as exact gate duration can only be calculated after sequence is configured
        self.params['Carbon_pi_duration'] = 4 * self.params['C'+str(self.params['carbon_nr'])+'_Ren_N'+self.params['electron_transition']][0] * self.params['C'+str(self.params['carbon_nr'])+'_Ren_tau'+self.params['electron_transition']][0]
        if self.params['C13_DD_Scheme'] != 'No_DD' and min(self.params['free_evolution_time']) < self.params['Carbon_pi_duration']/2:
            raise Exception('Error: time between pulses (%s) is shorter than carbon Pi duration (%s)'
                        % (2*min(self.params['free_evolution_time']),self.params['Carbon_pi_duration']/2))

        DDseq = []

        if self.params['C13_DD_Scheme'] == 'auto':
            reps, pulses_remaining = divmod(self.params['Decoupling_pulses'],16)
            DDseq.extend(reps*['X','Y','X','Y','Y','X','Y','X','mX','mY','mX','mY','mY','mX','mY','mX'])
            if pulses_remaining >= 8:
                pulses_remaining -= 8
                DDseq.extend(['X', 'Y', 'X', 'Y', 'Y', 'X', 'Y', 'X'])
            if pulses_remaining >= 4:
                pulses_remaining -= 4
                DDseq.extend(['X','Y','X','Y'])
            if pulses_remaining >= 2:
                pulses_remaining -= 2
                DDseq.extend(['X','mX'])
            if pulses_remaining >= 1:
                pulses_remaining -= 1
                DDseq.extend(['X'])

        elif self.params['C13_DD_Scheme'] == 'No_DD':
            pass

        elif self.params['C13_DD_Scheme'] == 'X':
            DDseq.extend(self.params['Decoupling_pulses']*['X'])

        elif self.params['C13_DD_Scheme'] == 'XY4':
            if self.params['Decoupling_pulses'] % 4 != 0:
                raise Exception('Number of pulses must be dividable by 4')
            else:
                DDseq.extend((self.params['Decoupling_pulses'] / 2) * ['X','Y'])

        elif self.params['C13_DD_Scheme'] == 'XY8':
            if self.params['Decoupling_pulses'] % 8 != 0:
                raise Exception('Number of pulses must be dividable by 8')
            else:
                DDseq.extend((self.params['Decoupling_pulses'] / 8) * ['X','Y','X','Y','Y','X','Y','X'])

        elif self.params['C13_DD_Scheme'] == 'XY16':
            if self.params['Decoupling_pulses'] % 16 != 0:
                raise Exception('Number of pulses must be dividable by 16')
            else:
                DDseq.extend((self.params['Decoupling_pulses'] / 16) * ['X','Y','X','Y','Y','X','Y','X','mX','mY','mX','mY','mY','mX','mY','mX'])
        
        elif self.params['C13_DD_Scheme'] == 'XmX':
            if self.params['Decoupling_pulses'] % 2 != 0:
                raise Exception('Number of pulses must be dividable by 2')
            else:
                decoupling_repetitions = self.params['Decoupling_pulses'] / 2

            for n in np.arange(1,decoupling_repetitions+1):
                DDseq.extend((self.params['Decoupling_pulses'] / 2) * ['X','mX'])

        else:
            raise Exception('Choose a different C13 DD scheme')

        print DDseq
        print self.params['free_evolution_time']

        for pt in range(pts): ### Sweep over trigger time (= wait time)
            gate_seq = []

            ### Nitrogen MBI GOOD
            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]; gate_seq.extend(mbi_seq)

            ### Carbon initialization GOOD initializes in |+X>
            carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                prefix = 'C_MBI_',
                wait_for_trigger      = True, pt =pt,
                initialization_method = self.params['C13_init_method'],
                C_init_state          = self.params['init_state'],
                addressed_carbon      = self.params['carbon_nr'],
                el_RO_result          = str(self.params['C13_MBI_RO_state']),
                el_after_init         = str(self.params['el_after_init']))
            gate_seq.extend(carbon_init_seq)
            
            wait_gate = (Gate('Wait_gate_start_pt'+str(pt),'passive_elt',
                         wait_time = self.params['free_evolution_time'][pt]-self.params['Carbon_pi_duration']/2.))
            gate_seq.extend([wait_gate])

            if len(DDseq) > 0:
                for gate_nr, gate in enumerate(DDseq, start=1):
                    if gate_nr > 1:
                        wait_gate = Gate('Wait_gate' + str(gate_nr) + '_pt'+str(pt),'passive_elt',
                                             wait_time = 2*self.params['free_evolution_time'][pt]-self.params['Carbon_pi_duration'])
                        gate_seq.extend([wait_gate])

                    if gate == 'X':
                        C_phase = self.params['C13_X_phase']
                    elif gate == 'mX':
                        C_phase = self.params['C13_X_phase']+180
                    elif gate == 'Y':
                        C_phase = self.params['C13_Y_phase']
                    elif gate == 'mY':
                        C_phase = self.params['C13_Y_phase']+180
                    else:
                        raise Exception('Carbon Gate '+ Gate +' not recognized')

                    Pi_part_1 = Gate('C' + str(self.params['carbon_nr']) + '_pi' + gate + '1_' + str(gate_nr) +'_pt'+str(pt), 'Carbon_Gate',
                            Carbon_ind = self.params['carbon_nr'],
                            phase = C_phase)
                    Pi_part_2 = Gate('C' + str(self.params['carbon_nr']) + '_pi' + gate + '2_' + str(gate_nr) +'_pt'+str(pt), 'Carbon_Gate',
                            Carbon_ind = self.params['carbon_nr'],
                            phase = C_phase)
                    gate_seq.extend([Pi_part_1, Pi_part_2])
                wait_gate = Gate('Wait_gate_end_pt'+str(pt),'passive_elt',
                             wait_time = self.params['free_evolution_time'][pt]-self.params['Carbon_pi_duration']/2.)
                gate_seq.extend([wait_gate])

            ### Readout
            carbon_tomo_seq = self.readout_carbon_sequence(
                    prefix              = 'Tomo',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = [self.params['carbon_nr']],
                    RO_basis_list       = [self.params['C_RO_phase'][pt]],
                    el_state_in         = self.params['el_after_init'],
                    readout_orientation = self.params['electron_readout_orientation'])
            gate_seq.extend(carbon_tomo_seq)

            gate_seq = self.generate_AWG_elements(gate_seq,pt) # this will use resonance = 0 by default in

            ### Convert elements to AWG sequence and add to combined list
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq, explicit=True)
            combined_list_of_elements.extend(list_of_elements)

            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)

            if not debug:
                print '*'*10
                for g in gate_seq:
                    print g.name

            if debug:
                for g in gate_seq:
                    print g.name
                    if (g.C_phases_before_gate[self.params['carbon_nr']] == None):
                        print "[ None]"
                    else:
                        print "[ %.3f]" %(g.C_phases_before_gate[self.params['carbon_nr']]/np.pi*180)

                    if (g.C_phases_after_gate[self.params['carbon_nr']] == None):
                        print "[ None]"
                    else:
                        print "[ %.3f]" %(g.C_phases_after_gate[self.params['carbon_nr']]/np.pi*180)

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'

class MultiNuclearDD(MBI_C13):
    '''
    Made by Michiel based on NuclearDD
    This class is to measure Tcoh using XY4
    1. Nitrogen MBI initialisation
    2. MBI initialization nuclear spin
    3. DD on carbons
    5. Pi/2 pulse on nuclear spin and read out in one function
    Start time pi pulse = tau - 0.5*time pi gate

    Sequence: |N-MBI| -|CinitA|-|DD on carbons|-|Tomography|

    Pulse sequences
    X (x)^n
    XmX (x mx)^n
    XY-4 (xyxy)**n
    XY-8 (xyxy yxyx)**n
    XY-16 (xyxy yxyx mxmymxmy mymxmymx)**n

    '''
    mprefix = 'NuclearDD' #Changed
    adwin_process = 'MBI_multiple_C13'

    def generate_sequence(self, upload=True, debug=False):
        pts = self.params['pts']

        ### initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Initialized Nuclear Ramsey Sequence')

        # Calculate gate duration as exact gate duration can only be calculated after sequence is configured
        self.params['Carbon_pi_duration_list'] = []
        for kk in range(self.params['Nr_C13_init']):
            self.params['Carbon_pi_duration_list'].append(4 * self.params['C'+str(self.params['carbon_init_list'][kk])+'_Ren_N'+self.params['electron_transition']][0] * self.params['C'+str(self.params['carbon_init_list'][kk])+'_Ren_tau'+self.params['electron_transition']][0])


        if self.params['C13_DD_Scheme'] != 'No_DD' and min(self.params['free_evolution_time']) < sum(self.params['Carbon_pi_duration_list'])/2:
            raise Exception('Error: time between pulses (%s) is shorter than havle carbon Pi durations (%s)'
                        % (min(self.params['free_evolution_time']),sum(self.params['Carbon_pi_duration_list'])/2))

        DDseq = []

        if self.params['C13_DD_Scheme'] == 'auto':
            reps, pulses_remaining = divmod(self.params['Decoupling_pulses'],16)
            DDseq.extend(reps*['X','Y','X','Y','Y','X','Y','X','mX','mY','mX','mY','mY','mX','mY','mX'])
            if pulses_remaining >= 8:
                pulses_remaining -= 8
                DDseq.extend(['X', 'Y', 'X', 'Y', 'Y', 'X', 'Y', 'X'])
            if pulses_remaining >= 4:
                pulses_remaining -= 4
                DDseq.extend(['X','Y','X','Y'])
            if pulses_remaining >= 2:
                pulses_remaining -= 2
                DDseq.extend(['X','mX'])
            if pulses_remaining >= 1:
                pulses_remaining -= 1
                DDseq.extend(['X'])

        elif self.params['C13_DD_Scheme'] == 'No_DD':
            pass

        elif self.params['C13_DD_Scheme'] == 'X':
            DDseq.extend(self.params['Decoupling_pulses']*['X'])

        elif self.params['C13_DD_Scheme'] == 'XY4':
            if self.params['Decoupling_pulses'] % 4 != 0:
                raise Exception('Number of pulses must be dividable by 4')
            else:
                DDseq.extend((self.params['Decoupling_pulses'] / 2) * ['X','Y'])

        elif self.params['C13_DD_Scheme'] == 'XY8':
            if self.params['Decoupling_pulses'] % 8 != 0:
                raise Exception('Numb0er of pulses must be dividable by 8')
            else:
                DDseq.extend((self.params['Decoupling_pulses'] / 8) * ['X','Y','X','Y','Y','X','Y','X'])

        elif self.params['C13_DD_Scheme'] == 'XY16':
            if self.params['Decoupling_pulses'] % 16 != 0:
                raise Exception('Number of pulses must be dividable by 16')
            else:
                DDseq.extend((self.params['Decoupling_pulses'] / 16) * ['X','Y','X','Y','Y','X','Y','X','mX','mY','mX','mY','mY','mX','mY','mX'])
        
        elif self.params['C13_DD_Scheme'] == 'XmX':
            if self.params['Decoupling_pulses'] % 2 != 0:
                raise Exception('Number of pulses must be dividable by 2')
            else:
                decoupling_repetitions = self.params['Decoupling_pulses'] / 2

            for n in np.arange(1,decoupling_repetitions+1):
                DDseq.extend((self.params['Decoupling_pulses'] / 2) * ['X','mX'])

        else:
            raise Exception('Choose a different C13 DD scheme')

        print DDseq
        print self.params['free_evolution_time']
        print self.params['Tomography Bases']

        for pt in range(pts): ### Sweep over trigger time (= wait time)
            gate_seq = []

            ### Nitrogen MBI GOOD
            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]; gate_seq.extend(mbi_seq)

            init_wait_for_trigger = True
            # elafterinit = 0
            for kk in range(self.params['Nr_C13_init']):
                print self.params['init_method_list'][kk]
                print self.params['init_state_list'][kk]
                print self.params['carbon_init_list'][kk]
                # if kk == self.params['Nr_C13_init']-1:
                #     elafterinit = self.params['el_after_init']
                if self.params['init_state_list'][kk] != 'M':
                    carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                        prefix = 'C_MBI' + str(kk+1) + '_C',
                        wait_for_trigger      = init_wait_for_trigger, pt =pt,
                        initialization_method = self.params['init_method_list'][kk],
                        C_init_state          = self.params['init_state_list'][kk],
                        addressed_carbon      = self.params['carbon_init_list'][kk],
                        el_after_init         = '0')
                    gate_seq.extend(carbon_init_seq)
                    init_wait_for_trigger = False

            # Initialize classically correlated state
            if self.params['2qb_logical_state'] == 'classical':
                for kk in range(self.params['Nr_C13_init']):
                    if self.params['classical_state'][kk] == 'X':
                        C_phase = self.params['C13_Y_phase']+180
                    elif self.params['classical_state'][kk] == 'mX':
                        C_phase = self.params['C13_Y_phase']
                    elif self.params['classical_state'][kk] == 'Y':
                        C_phase = self.params['C13_Y_phase']+180
                    elif self.params['classical_state'][kk] == 'mY':
                        C_phase = self.params['C13_Y_phase']
                    else:
                        pass

                    if self.params['classical_state'][kk] in ['X','mX','Y','mY']:
                        Pi2 = Gate('C' + str(self.params['carbon_init_list'][kk]) + '_class_init_'+ self.params['classical_state'][kk] +'_pt'+str(pt), 
                                        'Carbon_Gate', Carbon_ind = self.params['carbon_init_list'][kk],
                                        phase = C_phase)
                        gate_seq.extend([Pi2])

            ### Initialize logical qubit via parity measurement.
            else: 
                for kk in range(self.params['Nr_MBE']):
                    
                    probabilistic_MBE_seq =     self.logic_init_seq(
                            prefix              = '2C_init_' + str(kk+1),
                            pt                  =  pt,
                            carbon_list         = self.params['carbon_init_list'],
                            RO_basis_list       = self.params['MBE_bases'],
                            RO_trigger_duration = self.params['2C_RO_trigger_duration'],#150e-6,
                            el_RO_result        = '0',
                            logic_state         = self.params['2qb_logical_state'] ,
                            go_to_element       = mbi,
                            event_jump_element   = 'next',
                            readout_orientation = 'positive')

                    gate_seq.extend(probabilistic_MBE_seq)

            ### add pi pulse after final init.
            if self.params['el_after_init'] == 1:
                gate_seq.extend([Gate('2C_init_elec_X_pt'+str(pt),'electron_Gate',
                                        Gate_operation='pi',
                                        phase = self.params['X_phase'],
                                        el_state_after_gate = '1')])    

            if self.params['wait_gate'] == True:
                if len(DDseq) > 0:
                    wait_gate = (Gate('Wait_gate_start_pt'+str(pt),'passive_elt',
                                 wait_time = self.params['free_evolution_time'][pt]-sum(self.params['Carbon_pi_duration_list'])/2.))
                    gate_seq.extend([wait_gate])
                    for gate_nr, gate in enumerate(DDseq, start=1):
                        if gate_nr > 1:
                            wait_gate = Gate('Wait_gate' + str(gate_nr) + '_pt'+str(pt),'passive_elt',
                                                 wait_time = 2*self.params['free_evolution_time'][pt]-sum(self.params['Carbon_pi_duration_list']))
                            gate_seq.extend([wait_gate])
                        for kk in range(self.params['Nr_C13_init']):
                            if gate == 'X':
                                C_phase = self.params['C13_X_phase']
                            elif gate == 'mX':
                                C_phase = self.params['C13_X_phase']+180
                            elif gate == 'Y':
                                C_phase = self.params['C13_Y_phase']
                            elif gate == 'mY':
                                C_phase = self.params['C13_Y_phase']+180
                            else:
                                raise Exception('Carbon Gate '+ Gate +' not recognized')

                            Pi_part_1 = Gate('C' + str(self.params['carbon_init_list'][kk]) + '_pi' + gate + '1_' + str(gate_nr) +'_pt'+str(pt), 'Carbon_Gate',
                                    Carbon_ind = self.params['carbon_init_list'][kk],
                                    phase = C_phase)
                            Pi_part_2 = Gate('C' + str(self.params['carbon_init_list'][kk]) + '_pi' + gate + '2_' + str(gate_nr) +'_pt'+str(pt), 'Carbon_Gate',
                                    Carbon_ind = self.params['carbon_init_list'][kk],
                                    phase = C_phase)
                            gate_seq.extend([Pi_part_1, Pi_part_2])
                    wait_gate = Gate('Wait_gate_end_pt'+str(pt),'passive_elt',
                                 wait_time = self.params['free_evolution_time_RO'][pt]-sum(self.params['Carbon_pi_duration_list'])/2.)
                    gate_seq.extend([wait_gate])

                else:
                    wait_gate = (Gate('Wait_gate_start_pt'+str(pt),'passive_elt',
                                 wait_time = self.params['free_evolution_time'][pt]))
                    gate_seq.extend([wait_gate])
            else:
                wait_gate = (Gate('Wait_gate_start_pt'+str(pt),'passive_elt',
                                 wait_time = 3e-6))
                gate_seq.extend([wait_gate])

            ### Readout
            carbon_tomo_seq = self.readout_carbon_sequence(
                    prefix              = 'Tomo',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_init_list'],
                    RO_basis_list       = self.params['Tomography Bases'][pt],
                    el_state_in         = self.params['el_after_init'],
                    readout_orientation = self.params['electron_readout_orientation'])
            gate_seq.extend(carbon_tomo_seq)

            gate_seq = self.generate_AWG_elements(gate_seq,pt) # this will use resonance = 0 by default in

            ### Convert elements to AWG sequence and add to combined list
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq, explicit=True)
            combined_list_of_elements.extend(list_of_elements)

            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)

            if not debug:
                print '*'*10
                for g in gate_seq:
                    print g.name

            # if debug:
            #     for g in gate_seq:
            #         print g.name
            #         if (g.C_phases_before_gate[self.params['carbon_nr']] == None):
            #             print "[ None]"
            #         else:
            #             print "[ %.3f]" %(g.C_phases_before_gate[self.params['carbon_nr']]/np.pi*180)

            #         if (g.C_phases_after_gate[self.params['carbon_nr']] == None):
            #             print "[ None]"
            #         else:
            #             print "[ %.3f]" %(g.C_phases_after_gate[self.params['carbon_nr']]/np.pi*180)

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'

class NuclearDD_OLD(MBI_C13):
    '''
    Made by Michiel based on NuclearHahnEchoWithInitialization
    This class is to measure Tcoh using XY4
    1. Nitrogen MBI initialisation
    2. MBI initialization nuclear spin
    3. DD on carbons
    5. Pi/2 pulse on nuclear spin and read out in one function
    Start time pi pulse = tau - 0.5*time pi gate

    Sequence: |N-MBI| -|CinitA|-|DD on carbons|-|Tomography|

    XY-4 (xyxy)**n
    XY-8 (xyxy yxyx)**n
    XY-16 (xyxy yxyx mxmymxmy mymxmymx)**n
    '''
    mprefix = 'NuclearDD' #Changed
    adwin_process = 'MBI_multiple_C13'


    # def C13_pi(rep,pt,phase,nr=1):
    #     if phase = 
    #     C_Echo_1 = Gate('C_echoX'+ str(nr) +'_rep'+str(rep)+'_pt'+str(pt), 'Carbon_Gate',
    #             Carbon_ind =self.params['carbon_nr'],
    #             phase = self.params['C13_X_phase'])
    #     C_Echo_2 = Gate('C_echoX' + str(nr) +'_rep'+str(rep)+'_pt'+str(pt), 'Carbon_Gate',
    #             Carbon_ind =self.params['carbon_nr'],
    #             phase = self.params['C13_X_phase'])
    #     return [C_Echo_X1,C_Echo_X2]

    # def free_evolution(rep,pt,nr=1,tau=1):
    #     wait_gate = Gate('Wait_gate' + str(nr) '_rep'+str(n)+'_pt'+str(pt),'passive_elt',
    #                          wait_time = self.params['free_evolution_time'][pt]-self.params['Carbon_pi_duration']/2)
    #     return wait_gate

    def generate_sequence(self, upload=True, debug=False):
        pts = self.params['pts']

        ### initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Initialized Nuclear Ramsey Sequence')

        for pt in range(pts): ### Sweep over trigger time (= wait time)
            gate_seq = []

            ### Nitrogen MBI GOOD
            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]; gate_seq.extend(mbi_seq)

            ### Carbon initialization GOOD initializes in |+X>
            carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                prefix = 'C_MBI_',
                wait_for_trigger      = True, pt =pt,
                initialization_method = self.params['C13_init_method'],
                C_init_state          = self.params['init_state'],
                addressed_carbon      = self.params['carbon_nr'],
                el_RO_result          = str(self.params['C13_MBI_RO_state']),
                el_after_init         = str(self.params['el_after_init']))
            gate_seq.extend(carbon_init_seq)

            # Calculate gate duration as exact gate duration can only be calculated after sequence is configured
            
            self.params['Carbon_pi_duration'] = 4 * self.params['C'+str(self.params['carbon_nr'])+'_Ren_N'+self.params['electron_transition']][0] * self.params['C'+str(self.params['carbon_nr'])+'_Ren_tau'+self.params['electron_transition']][0]
            if self.params['C13_DD_Scheme'] != 'No_DD' and self.params['free_evolution_time'][pt] < self.params['Carbon_pi_duration']/2:
                raise Exception('Error: time between pulses (%s) is shorter than carbon Pi duration (%s)'
                            % (2*self.params['free_evolution_time'][pt],self.params['Carbon_pi_duration']/2))

            #Make carbon pulses
            

            # def C13_pi_mX(rep,pt):
            #     C_Echo_mX1 = Gate('C_echomX1_rep'+str(n)+'_pt'+str(pt), 'Carbon_Gate',
            #             Carbon_ind =self.params['carbon_nr'],
            #             phase = self.params['C13_X_phase']+180)
            #     C_Echo_mX2 = Gate('C_echomX2_rep'+str(n)+'_pt'+str(pt), 'Carbon_Gate',
            #             Carbon_ind =self.params['carbon_nr'],
            #             phase = self.params['C13_X_phase']+180)
            #     return [C_Echo_X1,C_Echo_X2]

            if self.params['C13_DD_Scheme'] == 'No_DD':
                pass

            elif self.params['C13_DD_Scheme'] == 'X':
                decoupling_repetitions = self.params['Decoupling_pulses']

                for n in np.arange(1,decoupling_repetitions+1):
                    wait_gate1 = Gate('Wait_gate1_rep'+str(n)+'_pt'+str(pt),'passive_elt',
                             wait_time = self.params['free_evolution_time'][pt]-self.params['Carbon_pi_duration']/2.)
                    C_Echo_X1 = Gate('C_echoX1_rep'+str(n)+'_pt'+str(pt), 'Carbon_Gate',
                            Carbon_ind =self.params['carbon_nr'],
                            phase = self.params['C13_X_phase'])
                    C_Echo_X2 = Gate('C_echoX2_rep'+str(n)+'_pt'+str(pt), 'Carbon_Gate',
                            Carbon_ind =self.params['carbon_nr'],
                            phase = self.params['C13_X_phase'])
                    wait_gate3 = Gate('Wait_gate3_rep'+str(n)+'_pt'+str(pt),'passive_elt',
                             wait_time = self.params['free_evolution_time'][pt]-self.params['Carbon_pi_duration']/2)
                    DDseq = [wait_gate1,C_Echo_X1,C_Echo_X2,wait_gate3]
                    gate_seq.extend(DDseq)

            elif self.params['C13_DD_Scheme'] == 'XY4':
                if self.params['Decoupling_pulses'] % 4 != 0:
                    raise Exception('Number of pulses must be dividable by 4')
                else:
                    decoupling_repetitions = self.params['Decoupling_pulses'] / 2

                # XY4^(N/4
                for n in np.arange(1,decoupling_repetitions+1):
                    wait_gate1 = Gate('Wait_gate1_rep'+str(n)+'_pt'+str(pt),'passive_elt',
                             wait_time = self.params['free_evolution_time'][pt]-self.params['Carbon_pi_duration']/2.)
                    C_Echo_X1 = Gate('C_echoX1_rep'+str(n)+'_pt'+str(pt), 'Carbon_Gate',
                            Carbon_ind =self.params['carbon_nr'],
                            phase = self.params['C13_X_phase'])
                    C_Echo_X2 = Gate('C_echoX2_rep'+str(n)+'_pt'+str(pt), 'Carbon_Gate',
                            Carbon_ind =self.params['carbon_nr'],
                            phase = self.params['C13_X_phase'])
                    wait_gate2 = Gate('Wait_gate2_rep'+str(n)+'_pt'+str(pt),'passive_elt',
                             wait_time = 2*self.params['free_evolution_time'][pt]-self.params['Carbon_pi_duration'])
                    C_Echo_Y1 = Gate('C_echoY1_rep'+str(n)+'_pt'+str(pt), 'Carbon_Gate',
                            Carbon_ind =self.params['carbon_nr'],
                            phase = self.params['C13_X_phase'])
                    C_Echo_Y2 = Gate('C_echoY2_rep'+str(n)+'_pt'+str(pt), 'Carbon_Gate',
                            Carbon_ind =self.params['carbon_nr'],
                            phase = self.params['C13_X_phase'])
                    wait_gate3 = Gate('Wait_gate3_rep'+str(n)+'_pt'+str(pt),'passive_elt',
                             wait_time = self.params['free_evolution_time'][pt]-self.params['Carbon_pi_duration']/2)
                    DDseq = [wait_gate1,C_Echo_X1,C_Echo_X2,wait_gate2,C_Echo_Y1,C_Echo_Y2,wait_gate3]
                    gate_seq.extend(DDseq)


            elif self.params['C13_DD_Scheme'] == 'XY8':
                if self.params['Decoupling_pulses'] % 8 != 0:
                    raise Exception('Number of pulses must be dividable by 8')
                else:
                    decoupling_repetitions = self.params['Decoupling_pulses'] / 2

                # XY4^(N/4
                for n in np.arange(1,decoupling_repetitions+1):
                    wait_gate1 = Gate('Wait_gate1_rep'+str(n)+'_pt'+str(pt),'passive_elt',
                             wait_time = self.params['free_evolution_time'][pt]-self.params['Carbon_pi_duration']/2.)
                    C_Echo_X1 = Gate('C_echoX1_rep'+str(n)+'_pt'+str(pt), 'Carbon_Gate',
                            Carbon_ind =self.params['carbon_nr'],
                            phase = self.params['C13_X_phase'])
                    C_Echo_X2 = Gate('C_echoX2_rep'+str(n)+'_pt'+str(pt), 'Carbon_Gate',
                            Carbon_ind =self.params['carbon_nr'],
                            phase = self.params['C13_X_phase'])
                    wait_gate2 = Gate('Wait_gate2_rep'+str(n)+'_pt'+str(pt),'passive_elt',
                             wait_time = 2*self.params['free_evolution_time'][pt]-self.params['Carbon_pi_duration'])
                    C_Echo_Y1 = Gate('C_echoY1_rep'+str(n)+'_pt'+str(pt), 'Carbon_Gate',
                            Carbon_ind =self.params['carbon_nr'],
                            phase = self.params['C13_X_phase'])
                    C_Echo_Y2 = Gate('C_echoY2_rep'+str(n)+'_pt'+str(pt), 'Carbon_Gate',
                            Carbon_ind =self.params['carbon_nr'],
                            phase = self.params['C13_X_phase'])
                    wait_gate3 = Gate('Wait_gate3_rep'+str(n)+'_pt'+str(pt),'passive_elt',
                             wait_time = self.params['free_evolution_time'][pt]-self.params['Carbon_pi_duration']/2)
                    DDseq = [wait_gate1,C_Echo_X1,C_Echo_X2,wait_gate2,C_Echo_Y1,C_Echo_Y2,wait_gate3]
                    gate_seq.extend(DDseq)
               
            elif self.params['C13_DD_Scheme'] == 'XmX':
                if self.params['Decoupling_pulses'] % 2 != 0:
                    raise Exception('Number of pulses must be dividable by 2')
                else:
                    decoupling_repetitions = self.params['Decoupling_pulses'] / 2

                for n in np.arange(1,decoupling_repetitions+1):
                    wait_gate1 = Gate('Wait_gate1_rep'+str(n)+'_pt'+str(pt),'passive_elt',
                             wait_time = self.params['free_evolution_time'][pt]-self.params['Carbon_pi_duration']/2.)
                    C_Echo_X1 = Gate('C_echoX1_rep'+str(n)+'_pt'+str(pt), 'Carbon_Gate',
                            Carbon_ind =self.params['carbon_nr'],
                            phase = self.params['C13_X_phase'])
                    C_Echo_X2 = Gate('C_echoX2_rep'+str(n)+'_pt'+str(pt), 'Carbon_Gate',
                            Carbon_ind =self.params['carbon_nr'],
                            phase = self.params['C13_X_phase'])
                    wait_gate2 = Gate('Wait_gate2_rep'+str(n)+'_pt'+str(pt),'passive_elt',
                             wait_time = 2*self.params['free_evolution_time'][pt]-self.params['Carbon_pi_duration'])
                    C_Echo_mX1 = Gate('C_echomX1_rep'+str(n)+'_pt'+str(pt), 'Carbon_Gate',
                            Carbon_ind =self.params['carbon_nr'],
                            phase = self.params['C13_X_phase']+180)
                    C_Echo_mX2 = Gate('C_echomX2_rep'+str(n)+'_pt'+str(pt), 'Carbon_Gate',
                            Carbon_ind =self.params['carbon_nr'],
                            phase = self.params['C13_X_phase']+180)
                    wait_gate3 = Gate('Wait_gate3_rep'+str(n)+'_pt'+str(pt),'passive_elt',
                             wait_time = self.params['free_evolution_time'][pt]-self.params['Carbon_pi_duration']/2)
                    DDseq = [wait_gate1,C_Echo_X1,C_Echo_X2,wait_gate2,C_Echo_mX1,C_Echo_mX2,wait_gate3]
                    gate_seq.extend(DDseq)     

            else:
                raise Exception('Choose a different C13 DD scheme')
        


            ### Readout
            carbon_tomo_seq = self.readout_carbon_sequence(
                    prefix              = 'Tomo',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = [self.params['carbon_nr']],
                    RO_basis_list       = [self.params['C_RO_phase'][pt]],
                    el_state_in         = self.params['el_after_init'],
                    readout_orientation = self.params['electron_readout_orientation'])
            gate_seq.extend(carbon_tomo_seq)

            gate_seq = self.generate_AWG_elements(gate_seq,pt) # this will use resonance = 0 by default in

            ### Convert elements to AWG sequence and add to combined list
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq, explicit=True)
            combined_list_of_elements.extend(list_of_elements)

            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)

            if not debug:
                print '*'*10
                for g in gate_seq:
                    print g.name

            if debug:
                for g in gate_seq:
                    print g.name
                    if (g.C_phases_before_gate[self.params['carbon_nr']] == None):
                        print "[ None]"
                    else:
                        print "[ %.3f]" %(g.C_phases_before_gate[self.params['carbon_nr']]/np.pi*180)

                    if (g.C_phases_after_gate[self.params['carbon_nr']] == None):
                        print "[ None]"
                    else:
                        print "[ %.3f]" %(g.C_phases_after_gate[self.params['carbon_nr']]/np.pi*180)

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'

class Electron_T1(MBI_C13):
    mprefix = 'NuclearDD' 
    adwin_process='MBI_multiple_C13'
   
    def generate_sequence(self, upload=True, debug=False):
        pts = self.params['pts']

        ### initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Initialized Nuclear Ramsey Sequence')

        # Calculate gate duration as exact gate duration can only be calculated after sequence is configured

        for pt in range(pts): ### Sweep over trigger time (= wait time)
            gate_seq = []

            ### Nitrogen MBI GOOD
            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]; gate_seq.extend(mbi_seq)
            
            # wait_gate = (Gate('Wait_gate_before_init_pulse_pt'+str(pt),'passive_elt',
            #                      wait_time = 5e-6))
            # gate_seq.extend([wait_gate])
            el_state = '0'
            wait_gate = (Gate('Wait_for_SP_pt'+str(pt),'passive_elt',
                             wait_time = 1.5e-3))
            gate_seq.extend([wait_gate])
            print "init_el_state", self.params['init_el_state']
            if self.params['init_el_state'] == '1':
                gate_seq.extend([Gate('init_elec_X_pt'+str(pt),'electron_Gate',
                                            Gate_operation='pi',
                                            phase = self.params['X_phase'],
                                            el_state_after_gate = '1')])
                el_state = '1'

            # wait_gate = (Gate('Wait_gate_after_init_pulse_pt'+str(pt),'passive_elt',
            #                      wait_time = 5e-6))
            # gate_seq.extend([wait_gate])


            # wait_reps = self.params['free_evolution_time'][pt] / 0.5
            #     print wait_reps
            # for i in range(500):
            #     wait_gate = (Gate('Wait_gate_'+ str(i+1) +'_pt'+str(pt),'passive_elt',
            #                  wait_time = self.params['free_evolution_time'][pt]/500.))
            #     gate_seq.extend([wait_gate])

            # if self.params['free_evolution_time'][pt] > 0.5:
            #     wait_reps = self.params['free_evolution_time'][pt] / 0.5
            #     print wait_reps
            #     for i in range(int(wait_reps)):
            #         wait_gate = (Gate('Wait_gate_'+ str(i+1) +'_pt'+str(pt),'passive_elt',
            #                      wait_time = self.params['free_evolution_time'][pt]/wait_reps))
            #         gate_seq.extend([wait_gate])
            # else:
            wait_gate = (Gate('Wait_gate_pt'+str(pt),'passive_elt',
                             wait_time = self.params['free_evolution_time'][pt]))
            gate_seq.extend([wait_gate])

            # wait_gate = (Gate('Wait_gate_before_RO_pulse_pt'+str(pt),'passive_elt',
            #                      wait_time = 5e-6))
            # gate_seq.extend([wait_gate])
            print 'RO_el_state', self.params['RO_el_state']
            if self.params['RO_el_state'] == '1':
                # if el_state == '0':
                #     el_state = '0'
                # if el_state == '1':
                #     el_state = '1'
                gate_seq.extend([Gate('RO_elec_X_pt'+str(pt),'electron_Gate',
                                            Gate_operation='pi',
                                            phase = -self.params['X_phase'],
                                            el_state_after_gate = el_state)])
        

            # wait_gate = (Gate('Wait_gate_after_RO_pulse_pt'+str(pt),'passive_elt',
            #                      wait_time = 5e-6))
            # gate_seq.extend([wait_gate])

            RO_trig = (Gate('RO_Trigger_'+str(pt),'Trigger',
                wait_time = 10e-6,
                go_to = None, event_jump = None,
                el_state_before_gate = '1'))
            gate_seq.extend([RO_trig])
            
            gate_seq = self.generate_AWG_elements(gate_seq,pt) # this will use resonance = 0 by default in

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
