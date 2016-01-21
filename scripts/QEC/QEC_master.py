"""
QEC master file
Contains all measurement classes related to the quantum error correction project.
"""


import numpy as np
import qt
import copy
from measurement.lib.pulsar import pulse, pulselib, element, pulsar
reload(pulsar)

import measurement.lib.measurement2.adwin_ssro.DD_2 as DD; reload(DD)
from measurement.lib.measurement2.adwin_ssro.DD_2 import Gate


class Three_QB_QEC(MBI_C13):
    '''
    Sequence: |N-MBI| -|Cinit|^N-|MBE|^N-|Tomography|
    '''
    mprefix = 'Three_QB_QEC'
    adwin_process = 'MBI_multiple_C13'

    def generate_sequence(self, upload=True, debug=False):
        pts = self.params['pts']

        ### initialize empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Two Qubit MBE')

        for pt in range(pts): ### Sweep over RO basis
            gate_seq = []

            ### Nitrogen MBI
            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]; gate_seq.extend(mbi_seq)

            ### Carbon initialization
            init_wait_for_trigger = True
            for kk in range(self.params['Nr_C13_init']):
                carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                    prefix = 'C_MBI' + str(kk+1) + '_C',
                    wait_for_trigger      = init_wait_for_trigger, pt =pt,
                    initialization_method = self.params['init_method_list'][kk],
                    C_init_state          = self.params['init_state_list'][kk],
                    addressed_carbon      = self.params['carbon_init_list'][kk])
                gate_seq.extend(carbon_init_seq)
                init_wait_for_trigger = False

            ### MBE - measurement based entanglement
            for kk in range(self.params['Nr_MBE']):
                print '3C_init_'
                probabilistic_MBE_seq =     self.logic_init_seq(
                        prefix              = '3C_init_' + str(kk+1),
                        pt                  =  pt,
                        carbon_list         = self.params['MBE_list'],
                        RO_basis_list       = self.params['MBE_bases'],
                        RO_trigger_duration = 150e-6,
                        el_RO_result        = '0',
                        logic_state         = self.params['3qb_logical_state'] ,
                        go_to_element       = mbi,
                        event_jump_element   = 'next',
                        readout_orientation = 'positive',
                        phase_error         = self.params['phase_error_array'][pt])

                gate_seq.extend(probabilistic_MBE_seq)

            ### Check if free evolution time is larger than the RO time (it can't be shorter)
            if self.params['add_wait_gate'] == True:
                wait_gate = Gate('Wait_gate_'+str(pt),'passive_elt',
                         wait_time = self.params['free_evolution_time'][pt])
                wait_seq = [wait_gate];
                if self.params['free_evolution_time'][pt] !=0:
                    gate_seq.extend(wait_seq)

            ### Readout

            carbon_tomo_seq = self.readout_carbon_sequence(
                    prefix              = 'Tomo',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomography Bases'],
                    readout_orientation = self.params['electron_readout_orientation'])
            gate_seq.extend(carbon_tomo_seq)

            gate_seq = self.generate_AWG_elements(gate_seq,pt)

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

                    if ((g.C_phases_before_gate[self.params['carbon_list'][0]] == None) and (g.C_phases_before_gate[self.params['carbon_list'][1]] == None)):
                        print "[ None , None ]"
                    elif g.C_phases_before_gate[self.params['carbon_list'][0]] == None:
                        print "[ None , %.3f ]" %(g.C_phases_before_gate[self.params['carbon_list'][1]]/np.pi*180)
                    elif g.C_phases_before_gate[self.params['carbon_list'][1]] == None:
                        print "[ %.3f, None ]" %(g.C_phases_before_gate[self.params['carbon_list'][0]]/np.pi*180)
                    else:
                        print "[ %.3f , %.3f ]" %(g.C_phases_before_gate[self.params['carbon_list'][0]]/np.pi*180, g.C_phases_before_gate[self.params['carbon_list'][1]]/np.pi*180)


                    if ((g.C_phases_after_gate[self.params['carbon_list'][0]] == None) and (g.C_phases_after_gate[self.params['carbon_list'][1]] == None)):
                        print "[ None , None ]"
                    elif g.C_phases_after_gate[self.params['carbon_list'][0]] == None:
                        print "[ None , %.3f ]" %(g.C_phases_after_gate[self.params['carbon_list'][1]]/np.pi*180)
                    elif g.C_phases_after_gate[self.params['carbon_list'][1]] == None:
                        print "[ %.3f, None ]" %(g.C_phases_after_gate[self.params['carbon_list'][0]]/np.pi*180)
                    else:
                        print "[ %.3f , %.3f ]" %(g.C_phases_after_gate[self.params['carbon_list'][0]]/np.pi*180, g.C_phases_after_gate[self.params['carbon_list'][1]]/np.pi*180)

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'

class Three_QB_det_QEC(MBI_C13):
    '''
    #Sequence
                                              --|Tomography00|
                                --|Parity_b_0|
                                              --|Tomography01|
    |N-MBI| -|Cinits|-|Parity_a|
                                               --|Tomography10|
                                --|Parity_b_1|
                                              --|Tomography11|
    '''
    mprefix         = 'Three_QB_det_QEC'
    adwin_process   = 'MBI_multiple_C13'

    def generate_sequence(self,upload=True,debug = False):
        pts = self.params['pts']

        ### initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Two Qubit MBE')

        for pt in range(pts):
            print
            print '-' *20

            gate_seq = []

            ### Nitrogen MBI
            mbi = Gate('N_MBI_pt'+str(pt),'MBI')
            mbi_seq = [mbi]
            gate_seq.extend(mbi_seq)

            ### Carbon initialization
            init_wait_for_trigger = True
            for kk in range(self.params['Nr_C13_init']):
                carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                    prefix = 'C_MBI_step_' + str(kk+1) + '_C',
                    wait_for_trigger      = init_wait_for_trigger, pt =pt,
                    initialization_method = self.params['init_method_list'][kk],
                    C_init_state          = self.params['init_state_list'][kk],
                    addressed_carbon      = self.params['carbon_init_list'][kk])
                gate_seq.extend(carbon_init_seq)
                init_wait_for_trigger = False

            ### Encoding of logical state

            for kk in range(self.params['Nr_MBE']):

                probabilistic_MBE_seq =     self.logic_init_seq(
                        prefix              = 'Encode_' ,
                        pt                  =  pt,
                        carbon_list         = self.params['MBE_list'],
                        RO_basis_list       = self.params['MBE_bases'],
                        RO_trigger_duration = 90e-6,
                        el_RO_result        = '0',
                        logic_state         = self.params['3qb_logical_state'] ,
                        go_to_element       = mbi,
                        event_jump_element   = 'next',
                        readout_orientation = 'positive',
                        phase_error         = self.params['phase_error_array_1'][pt])

                gate_seq.extend(probabilistic_MBE_seq)

            ### Add optional free evolution time (+optional pi-pulse)
            if self.params['add_wait_gate'] == True:
                if self.params['wait_in_msm1'] == True:
                    pi_pulse_el = Gate('el_pi_pt'+str(pt),'electron_Gate',
                                    Gate_operation='pi',
                                    phase = self.params['X_phase'],el_state_after_gate = '1')
                wait_gate = Gate('Wait_gate_pt'+str(pt),'passive_elt',
                         wait_time = self.params['free_evolution_time_1'][pt])
                wait_seq = [wait_gate];
                if self.params['free_evolution_time_1'][pt] !=0:
                    if self.params['wait_in_msm1'] == True:
                        gate_seq.extend([pi_pulse_el])
                    gate_seq.extend(wait_seq)

            ### Parity measurements to detect error syndrome

            ### Parity msmt a
            if self.params['add_wait_gate'] == True and self.params['free_evolution_time_1'][pt] !=0 and self.params['wait_in_msm1'] == True:
                el_in_state = 1
            else:
                el_in_state = 0

            Parity_seq_a = self.readout_carbon_sequence(
                        prefix              = 'Parity_A_' ,
                        pt                  = pt,
                        RO_trigger_duration = 150e-6,
                        carbon_list         = self.params['Parity_a_carbon_list'],
                        RO_basis_list       = self.params['Parity_a_RO_list'],
                        el_RO_result         = '0',
                        readout_orientation = self.params['Parity_a_RO_orientation'],
                        el_state_in     = el_in_state)

            gate_seq.extend(Parity_seq_a)

            #############################
            gate_seq0 = copy.deepcopy(gate_seq)
            gate_seq1 = copy.deepcopy(gate_seq)

            ### Parity msmt b
            el_in_state_b0 = 0
            el_in_state_b1 = 1

            Parity_seq_b0 = self.readout_carbon_sequence(
                        prefix              = 'Parity_B0_' ,
                        pt                  = pt,
                        RO_trigger_duration = 150e-6,
                        carbon_list         = self.params['Parity_b_carbon_list'],
                        RO_basis_list       = self.params['Parity_b_RO_list'],
                        el_RO_result         = '0',
                        readout_orientation = self.params['Parity_b_RO_orientation'],
                        el_state_in     = el_in_state_b0)

            Parity_seq_b1 = self.readout_carbon_sequence(
                        prefix              = 'Parity_B1_' ,
                        pt                  = pt,
                        RO_trigger_duration = 150e-6,
                        carbon_list         = self.params['Parity_b_carbon_list'],
                        RO_basis_list       = self.params['Parity_b_RO_list'],
                        el_RO_result        = '0',
                        readout_orientation = self.params['Parity_b_RO_orientation'],
                        el_state_in     = el_in_state_b1)

            gate_seq0.extend(Parity_seq_b0)
            gate_seq1.extend(Parity_seq_b1)

            gate_seq00 = copy.deepcopy(gate_seq0)
            gate_seq01 = copy.deepcopy(gate_seq0)
            gate_seq10 = copy.deepcopy(gate_seq1)
            gate_seq11 = copy.deepcopy(gate_seq1)

            ### add half of the wait time again if we want to sweep time
            if self.params['add_wait_gate'] == True:
                wait_gate2_00 = Gate('Wait_gate2_00_'+str(pt),'passive_elt',
                         wait_time = self.params['free_evolution_time_2'][pt])
                wait_gate2_01 = Gate('Wait_gate2_01_'+str(pt),'passive_elt',
                         wait_time = self.params['free_evolution_time_2'][pt])

                wait_gate2_10 = Gate('Wait_gate2_10_'+str(pt),'passive_elt',
                         wait_time = self.params['free_evolution_time_2'][pt])
                wait_gate2_11 = Gate('Wait_gate2_11_'+str(pt),'passive_elt',
                         wait_time = self.params['free_evolution_time_2'][pt])

                wait_seq2_00 = [wait_gate2_00];
                wait_seq2_01 = [wait_gate2_01];
                wait_seq2_10 = [wait_gate2_10];
                wait_seq2_11 = [wait_gate2_11];

                if self.params['free_evolution_time_2'][pt] !=0:
                    gate_seq00.extend(wait_seq2_00)
                    gate_seq01.extend(wait_seq2_01)
                    gate_seq10.extend(wait_seq2_10)
                    gate_seq11.extend(wait_seq2_11)



            carbon_tomo_seq00 = self.readout_carbon_sequence(
                    prefix              = 'Tomo00_',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomo_Bases_00'],
                    readout_orientation = self.params['electron_readout_orientation'],
                    el_state_in     = 0,
                    phase_error = self.params['phase_error_array_2'][pt])

            gate_seq00.extend(carbon_tomo_seq00)

            carbon_tomo_seq01 = self.readout_carbon_sequence(
                    prefix              = 'Tomo01_',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomo_Bases_01'],
                    readout_orientation = self.params['electron_readout_orientation'],
                    el_state_in     = 1,
                    phase_error = self.params['phase_error_array_2'][pt])
            gate_seq01.extend(carbon_tomo_seq01)

            carbon_tomo_seq10 = self.readout_carbon_sequence(
                    prefix              = 'Tomo10_',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomo_Bases_10'],
                    readout_orientation = self.params['electron_readout_orientation'],
                    el_state_in     = 0,
                    phase_error = self.params['phase_error_array_2'][pt])
            gate_seq10.extend(carbon_tomo_seq10)

            carbon_tomo_seq11 = self.readout_carbon_sequence(
                    prefix              = 'Tomo11_',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomo_Bases_11'],
                    readout_orientation = self.params['electron_readout_orientation'],
                    el_state_in     = 1,
                    phase_error = self.params['phase_error_array_2'][pt])

            gate_seq11.extend(carbon_tomo_seq11)

            # Make jump statements for branching to two different ROs
            Parity_seq_a[-1].go_to       = Parity_seq_b0[0].name
            Parity_seq_a[-1].event_jump  = Parity_seq_b1[0].name

            if self.params['free_evolution_time_2'][pt] !=0 and self.params['add_wait_gate'] == True:
                Parity_seq_b0[-1].go_to       = wait_seq2_00[0].name
                Parity_seq_b0[-1].event_jump  = wait_seq2_01[0].name

                Parity_seq_b1[-1].go_to       = wait_seq2_10[0].name
                Parity_seq_b1[-1].event_jump  = wait_seq2_11[0].name
            else:
                Parity_seq_b0[-1].go_to       = carbon_tomo_seq00[0].name
                Parity_seq_b0[-1].event_jump  = carbon_tomo_seq01[0].name

                Parity_seq_b1[-1].go_to       = carbon_tomo_seq10[0].name
                Parity_seq_b1[-1].event_jump  = carbon_tomo_seq11[0].name

            # In the end all roads lead to Rome
            Rome = Gate('Rome_'+str(pt),'passive_elt',
                    wait_time = 3e-6)
            gate_seq11.append(Rome)
            gate_seq00[-1].go_to     = gate_seq11[-1].name
            gate_seq01[-1].go_to     = gate_seq11[-1].name
            gate_seq10[-1].go_to     = gate_seq11[-1].name

            ################################################################
            ### Generate the AWG_elements, including all the phase gates for all branches###
            ################################################################

            gate_seq0[len(gate_seq)-1].el_state_before_gate =  '0' #Element -1

            gate_seq00[len(gate_seq)-1].el_state_before_gate =  '0' #Element -1
            gate_seq01[len(gate_seq)-1].el_state_before_gate =  '0' #Element -1
            gate_seq00[len(gate_seq0)-1].el_state_before_gate = '0' #Element -1
            gate_seq01[len(gate_seq0)-1].el_state_before_gate = '1' #Element -1

            gate_seq1[len(gate_seq)-1].el_state_before_gate =  '1' #Element -1

            gate_seq10[len(gate_seq)-1].el_state_before_gate =  '1' #Element -1
            gate_seq11[len(gate_seq)-1].el_state_before_gate =  '1' #Element -1
            gate_seq10[len(gate_seq1)-1].el_state_before_gate = '0' #Element -1
            gate_seq11[len(gate_seq1)-1].el_state_before_gate = '1' #Element -1

            gate_seq  = self.generate_AWG_elements(gate_seq,pt)
            gate_seq00 = self.generate_AWG_elements(gate_seq00,pt)
            gate_seq0  = self.generate_AWG_elements(gate_seq0,pt)
            gate_seq01 = self.generate_AWG_elements(gate_seq01,pt)
            gate_seq1  = self.generate_AWG_elements(gate_seq1,pt)
            gate_seq10 = self.generate_AWG_elements(gate_seq10,pt)
            gate_seq11 = self.generate_AWG_elements(gate_seq11,pt)

            # Merge the bracnhes into one AWG sequence
            merged_sequence = []
            merged_sequence.extend(gate_seq)                  #TODO: remove gate_seq and add gate_seq1 to gate_seq0 without common part

            merged_sequence.extend(gate_seq0[len(gate_seq):])
            merged_sequence.extend(gate_seq1[len(gate_seq):])

            merged_sequence.extend(gate_seq00[len(gate_seq0):])
            merged_sequence.extend(gate_seq01[len(gate_seq0):])
            merged_sequence.extend(gate_seq10[len(gate_seq1):])
            merged_sequence.extend(gate_seq11[len(gate_seq1):])

            print '*'*10
            print 'seq_merged'
            for i,g in enumerate(merged_sequence):
                print
                print g.name
                print g.Gate_type
                if debug and hasattr(g,'el_state_before_gate'):# != None:
                    # print g.el_state_before_gate
                    print '                        el state before and after (%s,%s)'%(g.el_state_before_gate, g.el_state_after_gate)
                elif debug:
                    print 'does not have attribute el_state_before_gate'


                if  debug==True:
                    phase_Q1 = g.C_phases_before_gate[self.params['carbon_list'][0]]
                    if phase_Q1 != None:
                        phase_Q1 = np.round(phase_Q1/np.pi*180,decimals = 1)
                    phase_Q2 = g.C_phases_before_gate[self.params['carbon_list'][1]]
                    if phase_Q2 != None:
                        phase_Q2 = np.round(phase_Q2/np.pi*180,decimals = 1)
                    phase_Q3 = g.C_phases_before_gate[self.params['carbon_list'][2]]
                    if phase_Q3 != None:
                        phase_Q3 = np.round(phase_Q3/np.pi*180,decimals = 1)
                        print '                        '+ str(phase_Q1)+ '   '+ str(phase_Q2)+ '   ' +str(phase_Q3)
                    phase_Q1 = g.C_phases_after_gate[self.params['carbon_list'][0]]
                    if phase_Q1 != None:
                        phase_Q1 = np.round(phase_Q1/np.pi*180,decimals = 1)
                    phase_Q2 = g.C_phases_after_gate[self.params['carbon_list'][1]]
                    if phase_Q2 != None:
                        phase_Q2 = np.round(phase_Q2/np.pi*180,decimals = 1)
                    phase_Q3 = g.C_phases_after_gate[self.params['carbon_list'][2]]
                    if phase_Q3 != None:
                        phase_Q3 = np.round(phase_Q3/np.pi*180,decimals = 1)
                        print '                        '+ str(phase_Q1)+ '   '+ str(phase_Q2)+ '   ' +str(phase_Q3)

            #Convert elements to AWG sequence and add to combined list
            list_of_elements, seq = self.combine_to_AWG_sequence(merged_sequence, explicit=True)
            combined_list_of_elements.extend(list_of_elements)

            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'

class Three_QB_det_rep_QEC(MBI_C13):
    '''
    #Sequence
                                                                       --|Tomography0000|
                                                        --|Parity_b_000|
                                                                       --|Tomography0001|
                                              -|Parity_a00|
                                                                       --|Tomography0010|
                                                        --|Parity_b_001|
                                                                       --|Tomography0011|
                                --|Parity_b_0|
                                                                       --|Tomography0100|
                                                        --|Parity_b_010|
                                                                       --|Tomography0101|
                                              -|Parity_a01|
                                                                       --|Tomography0110|
                                                        --|Parity_b_011|
                                                                       --|Tomography0111|
    |N-MBI| -|Cinits|-|Parity_a|
                                                                       --|Tomography1000|
                                                        --|Parity_b_100|
                                                                       --|Tomography1001|
                                              -|Parity_a10|
                                                                       --|Tomography1010|
                                                        --|Parity_b_101|
                                                                       --|Tomography1011|
                                --|Parity_b_1|
                                                                       --|Tomography1100|
                                                        --|Parity_b_110|
                                                                       --|Tomography1101|
                                              -|Parity_a11|
                                                                       --|Tomography1110|
                                                        --|Parity_b_111|
                                                                       --|Tomography1111|

    '''
    mprefix = 'Three_QB_det_rep_QEC'
    adwin_process = 'MBI_multiple_C13'

    def generate_sequence(self,upload=True,debug = False):
        pts = self.params['pts']

        ### initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Two Qubit MBE')

        for pt in range(pts):
            print
            print '-' *20

            gate_seq = []

            ####################
            ### Nitrogen MBI ###
            ####################

            mbi = Gate('N_MBI_pt'+str(pt),'MBI')
            mbi_seq = [mbi]
            gate_seq.extend(mbi_seq)

            #############################
            ### Carbon initialization ###
            #############################

            init_wait_for_trigger = True
            for kk in range(self.params['Nr_C13_init']):
                carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                    prefix = 'C_MBI_step_' + str(kk+1) + '_C',
                    wait_for_trigger      = init_wait_for_trigger, pt =pt,
                    initialization_method = self.params['init_method_list'][kk],
                    C_init_state          = self.params['init_state_list'][kk],
                    addressed_carbon      = self.params['carbon_init_list'][kk])
                gate_seq.extend(carbon_init_seq)
                init_wait_for_trigger = False

            #################################
            ### Encoding of logical state ###
            #################################

            for kk in range(self.params['Nr_MBE']):

                probabilistic_MBE_seq =     self.logic_init_seq(
                        prefix              = 'Encode_' ,
                        pt                  =  pt,
                        carbon_list         = self.params['MBE_list'],
                        RO_basis_list       = self.params['MBE_bases'],
                        RO_trigger_duration = 90e-6,
                        el_RO_result        = '0',
                        logic_state         = self.params['3qb_logical_state'] ,
                        go_to_element       = mbi,
                        event_jump_element   = 'next',
                        readout_orientation = 'positive',
                        phase_error         = self.params['phase_error_array_1'][pt])

                gate_seq.extend(probabilistic_MBE_seq)

            ########################################################    
            ### Parity measurements to detect and correct errors ###
            ########################################################

            ######################
            ### Parity msmt 1A ###
            ######################

            Parity_seq_a = self.readout_carbon_sequence(
                        prefix              = 'Parity_A_' ,
                        pt                  = pt,
                        RO_trigger_duration = 150e-6,
                        carbon_list         = self.params['Parity_a_carbon_list'],
                        RO_basis_list       = self.params['Parity_a_RO_list'],
                        el_RO_result         = '0',
                        readout_orientation = self.params['Parity_a_RO_orientation'],
                        el_state_in     = 0)

            gate_seq.extend(Parity_seq_a)

            gate_seq0 = copy.deepcopy(gate_seq)
            gate_seq1 = copy.deepcopy(gate_seq)

            ######################
            ### Parity msmt 1B ###
            ######################
            
            el_in_state_b0 = 0
            el_in_state_b1 = 1

            Parity_seq_b0 = self.readout_carbon_sequence(
                        prefix              = 'Parity_B0_' ,
                        pt                  = pt,
                        RO_trigger_duration = 150e-6,
                        carbon_list         = self.params['Parity_b_carbon_list'],
                        RO_basis_list       = self.params['Parity_b_RO_list'],
                        el_RO_result         = '0',
                        readout_orientation = self.params['Parity_b_RO_orientation'],
                        el_state_in     = el_in_state_b0)

            Parity_seq_b1 = self.readout_carbon_sequence(
                        prefix              = 'Parity_B1_' ,
                        pt                  = pt,
                        RO_trigger_duration = 150e-6,
                        carbon_list         = self.params['Parity_b_carbon_list'],
                        RO_basis_list       = self.params['Parity_b_RO_list'],
                        el_RO_result        = '0',
                        readout_orientation = self.params['Parity_b_RO_orientation'],
                        el_state_in     = el_in_state_b1)

            gate_seq0.extend(Parity_seq_b0)
            gate_seq1.extend(Parity_seq_b1)

            gate_seq00 = copy.deepcopy(gate_seq0)
            gate_seq01 = copy.deepcopy(gate_seq0)
            gate_seq10 = copy.deepcopy(gate_seq1)
            gate_seq11 = copy.deepcopy(gate_seq1)

            ######################
            ### Parity msmt 2A ###
            ######################
            
            el_in_state_a00 = 0
            el_in_state_a01 = 1
            el_in_state_a10 = 0
            el_in_state_a11 = 1

            ### errors on qubit 3 and 1 (Carbon 2 and 1)
            applied_error = [self.params['phase_error_array_2'][0,2], self.params['phase_error_array_2'][0,0]]
            
            Parity_seq_a00 = self.readout_carbon_sequence(
                        prefix              = 'Parity_A00_' ,
                        pt                  = pt,
                        RO_trigger_duration = 150e-6,
                        carbon_list         = self.params['Parity_a_carbon_list'],
                        RO_basis_list       = self.params['Parity_a_RO_list'],
                        el_RO_result        = '0',
                        readout_orientation = self.params['Parity_a_RO_orientation'],
                        el_state_in         = el_in_state_a00,
                        phase_error         = [self.params['phase_correct_list_A00'][0] + applied_error[0], self.params['phase_correct_list_A00'][1] + applied_error[1]])    

            Parity_seq_a01 = self.readout_carbon_sequence(
                        prefix              = 'Parity_A01_' ,
                        pt                  = pt,
                        RO_trigger_duration = 150e-6,
                        carbon_list         = self.params['Parity_a_carbon_list'],
                        RO_basis_list       = self.params['Parity_a_RO_list'],
                        el_RO_result        = '0',
                        readout_orientation = self.params['Parity_a_RO_orientation'],
                        el_state_in         = el_in_state_a01,
                        phase_error         = [self.params['phase_correct_list_A01'][0] + applied_error[0], self.params['phase_correct_list_A01'][1] + applied_error[1]])                                    

            Parity_seq_a10 = self.readout_carbon_sequence(
                        prefix              = 'Parity_A10_' ,
                        pt                  = pt,
                        RO_trigger_duration = 150e-6,
                        carbon_list         = self.params['Parity_a_carbon_list'],
                        RO_basis_list       = self.params['Parity_a_RO_list'],
                        el_RO_result        = '0',
                        readout_orientation = self.params['Parity_a_RO_orientation'],
                        el_state_in         = el_in_state_a10,
                        phase_error         = [ self.params['phase_correct_list_A10'][0] + applied_error[0], self.params['phase_correct_list_A10'][1]+ applied_error[1]])    

            Parity_seq_a11 = self.readout_carbon_sequence(
                        prefix              = 'Parity_A11_' ,
                        pt                  = pt,
                        RO_trigger_duration = 150e-6,
                        carbon_list         = self.params['Parity_a_carbon_list'],
                        RO_basis_list       = self.params['Parity_a_RO_list'],
                        el_RO_result        = '0',
                        readout_orientation = self.params['Parity_a_RO_orientation'],
                        el_state_in         = el_in_state_a11,
                        phase_error         = [self.params['phase_correct_list_A11'][0]+ applied_error[0], self.params['phase_correct_list_A11'][1]+ applied_error[1]]) 

            gate_seq00.extend(Parity_seq_a00)
            gate_seq01.extend(Parity_seq_a01)
            gate_seq10.extend(Parity_seq_a10)
            gate_seq11.extend(Parity_seq_a11)

            gate_seq000 = copy.deepcopy(gate_seq00)
            gate_seq001 = copy.deepcopy(gate_seq00)
            
            gate_seq100 = copy.deepcopy(gate_seq10)
            gate_seq101 = copy.deepcopy(gate_seq10)

            gate_seq010 = copy.deepcopy(gate_seq01)
            gate_seq011 = copy.deepcopy(gate_seq01)

            gate_seq110 = copy.deepcopy(gate_seq11)
            gate_seq111 = copy.deepcopy(gate_seq11)

            ######################
            ### Parity msmt 2B ###
            ######################

            el_in_state_b000 = 0
            el_in_state_b001 = 1
            el_in_state_b010 = 0
            el_in_state_b011 = 1
            el_in_state_b100 = 0
            el_in_state_b101 = 1
            el_in_state_b110 = 0
            el_in_state_b111 = 1 

            ### errors on qubit 2 only (Carbon 5)
            applied_error = [self.params['phase_error_array_2'][0,1], 0.]                              
            
            Parity_seq_b000 = self.readout_carbon_sequence(
                        prefix              = 'Parity_B000_' ,
                        pt                  = pt,
                        RO_trigger_duration = 150e-6,
                        carbon_list         = self.params['Parity_b_carbon_list'],
                        RO_basis_list       = self.params['Parity_b_RO_list'],
                        el_RO_result        = '0',
                        readout_orientation = self.params['Parity_b_RO_orientation'],
                        el_state_in         = el_in_state_b000,
                        phase_error         = applied_error)

            Parity_seq_b001 = self.readout_carbon_sequence(
                        prefix              = 'Parity_B001_' ,
                        pt                  = pt,
                        RO_trigger_duration = 150e-6,
                        carbon_list         = self.params['Parity_b_carbon_list'],
                        RO_basis_list       = self.params['Parity_b_RO_list'],
                        el_RO_result        = '0',
                        readout_orientation = self.params['Parity_b_RO_orientation'],
                        el_state_in         = el_in_state_b001,
                        phase_error         = applied_error)

            Parity_seq_b010 = self.readout_carbon_sequence(
                        prefix              = 'Parity_B010_' ,
                        pt                  = pt,
                        RO_trigger_duration = 150e-6,
                        carbon_list         = self.params['Parity_b_carbon_list'],
                        RO_basis_list       = self.params['Parity_b_RO_list'],
                        el_RO_result        = '0',
                        readout_orientation = self.params['Parity_b_RO_orientation'],
                        el_state_in         = el_in_state_b010,
                        phase_error         = applied_error)

            Parity_seq_b011 = self.readout_carbon_sequence(
                        prefix              = 'Parity_B011_' ,
                        pt                  = pt,
                        RO_trigger_duration = 150e-6,
                        carbon_list         = self.params['Parity_b_carbon_list'],
                        RO_basis_list       = self.params['Parity_b_RO_list'],
                        el_RO_result        = '0',
                        readout_orientation = self.params['Parity_b_RO_orientation'],
                        el_state_in         = el_in_state_b011,
                        phase_error         = applied_error)                                    

            Parity_seq_b100 = self.readout_carbon_sequence(
                        prefix              = 'Parity_B100_' ,
                        pt                  = pt,
                        RO_trigger_duration = 150e-6,
                        carbon_list         = self.params['Parity_b_carbon_list'],
                        RO_basis_list       = self.params['Parity_b_RO_list'],
                        el_RO_result        = '0',
                        readout_orientation = self.params['Parity_b_RO_orientation'],
                        el_state_in         = el_in_state_b100,
                        phase_error         = applied_error)

            Parity_seq_b101 = self.readout_carbon_sequence(
                        prefix              = 'Parity_B101_' ,
                        pt                  = pt,
                        RO_trigger_duration = 150e-6,
                        carbon_list         = self.params['Parity_b_carbon_list'],
                        RO_basis_list       = self.params['Parity_b_RO_list'],
                        el_RO_result        = '0',
                        readout_orientation = self.params['Parity_b_RO_orientation'],
                        el_state_in         = el_in_state_b101,
                        phase_error         = applied_error)

            Parity_seq_b110 = self.readout_carbon_sequence(
                        prefix              = 'Parity_B110_' ,
                        pt                  = pt,
                        RO_trigger_duration = 150e-6,
                        carbon_list         = self.params['Parity_b_carbon_list'],
                        RO_basis_list       = self.params['Parity_b_RO_list'],
                        el_RO_result        = '0',
                        readout_orientation = self.params['Parity_b_RO_orientation'],
                        el_state_in         = el_in_state_b110,
                        phase_error         = applied_error)

            Parity_seq_b111 = self.readout_carbon_sequence(
                        prefix              = 'Parity_B111_' ,
                        pt                  = pt,
                        RO_trigger_duration = 150e-6,
                        carbon_list         = self.params['Parity_b_carbon_list'],
                        RO_basis_list       = self.params['Parity_b_RO_list'],
                        el_RO_result        = '0',
                        readout_orientation = self.params['Parity_b_RO_orientation'],
                        el_state_in         = el_in_state_b111,
                        phase_error         = applied_error)  

            gate_seq000.extend(Parity_seq_b000)
            gate_seq001.extend(Parity_seq_b001)

            gate_seq010.extend(Parity_seq_b010)
            gate_seq011.extend(Parity_seq_b011)
            
            gate_seq100.extend(Parity_seq_b100)
            gate_seq101.extend(Parity_seq_b101)
            
            gate_seq110.extend(Parity_seq_b110)
            gate_seq111.extend(Parity_seq_b111)

            gate_seq0000 = copy.deepcopy(gate_seq000)
            gate_seq0001 = copy.deepcopy(gate_seq000)
            gate_seq0010 = copy.deepcopy(gate_seq001)
            gate_seq0011 = copy.deepcopy(gate_seq001)
            gate_seq0100 = copy.deepcopy(gate_seq010)
            gate_seq0101 = copy.deepcopy(gate_seq010)
            gate_seq0110 = copy.deepcopy(gate_seq011)
            gate_seq0111 = copy.deepcopy(gate_seq011)
            gate_seq1000 = copy.deepcopy(gate_seq100)
            gate_seq1001 = copy.deepcopy(gate_seq100)
            gate_seq1010 = copy.deepcopy(gate_seq101)
            gate_seq1011 = copy.deepcopy(gate_seq101)
            gate_seq1100 = copy.deepcopy(gate_seq110)
            gate_seq1101 = copy.deepcopy(gate_seq110)
            gate_seq1110 = copy.deepcopy(gate_seq111)
            gate_seq1111 = copy.deepcopy(gate_seq111)

            ############################
            ### Tomography sequences ###
            ############################

            carbon_tomo_seq0000 = self.readout_carbon_sequence(
                    prefix              = 'Tomo0000_',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomo_Bases_0000'],
                    readout_orientation = self.params['electron_readout_orientation'],
                    el_state_in         = 0,
                    phase_error         = self.params['phase_error_array_3'][pt])

            gate_seq0000.extend(carbon_tomo_seq0000)

            carbon_tomo_seq0001 = self.readout_carbon_sequence(
                    prefix              = 'Tomo0001_',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomo_Bases_0001'],
                    readout_orientation = self.params['electron_readout_orientation'],
                    el_state_in         = 1,
                    phase_error         = self.params['phase_error_array_3'][pt])

            gate_seq0001.extend(carbon_tomo_seq0001)

            carbon_tomo_seq0010 = self.readout_carbon_sequence(
                    prefix              = 'Tomo0010_',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomo_Bases_0010'],
                    readout_orientation = self.params['electron_readout_orientation'],
                    el_state_in         = 0,
                    phase_error         = self.params['phase_error_array_3'][pt])

            gate_seq0010.extend(carbon_tomo_seq0010)

            carbon_tomo_seq0011 = self.readout_carbon_sequence(
                    prefix              = 'Tomo0011_',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomo_Bases_0011'],
                    readout_orientation = self.params['electron_readout_orientation'],
                    el_state_in         = 1,
                    phase_error         = self.params['phase_error_array_3'][pt])

            gate_seq0011.extend(carbon_tomo_seq0011)




            carbon_tomo_seq0100 = self.readout_carbon_sequence(
                    prefix              = 'Tomo0100_',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomo_Bases_0100'],
                    readout_orientation = self.params['electron_readout_orientation'],
                    el_state_in         = 0,
                    phase_error         = self.params['phase_error_array_3'][pt])
            gate_seq0100.extend(carbon_tomo_seq0100)

            carbon_tomo_seq0101 = self.readout_carbon_sequence(
                    prefix              = 'Tomo0101_',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomo_Bases_0101'],
                    readout_orientation = self.params['electron_readout_orientation'],
                    el_state_in         = 1,
                    phase_error         = self.params['phase_error_array_3'][pt])
            gate_seq0101.extend(carbon_tomo_seq0101)

            carbon_tomo_seq0110 = self.readout_carbon_sequence(
                    prefix              = 'Tomo0110_',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomo_Bases_0110'],
                    readout_orientation = self.params['electron_readout_orientation'],
                    el_state_in         = 0,
                    phase_error         = self.params['phase_error_array_3'][pt])
            gate_seq0110.extend(carbon_tomo_seq0110)

            carbon_tomo_seq0111 = self.readout_carbon_sequence(
                    prefix              = 'Tomo0111_',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomo_Bases_0111'],
                    readout_orientation = self.params['electron_readout_orientation'],
                    el_state_in         = 1,
                    phase_error         = self.params['phase_error_array_3'][pt])
            gate_seq0111.extend(carbon_tomo_seq0111)




            carbon_tomo_seq1000 = self.readout_carbon_sequence(
                    prefix              = 'Tomo1000_',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomo_Bases_1000'],
                    readout_orientation = self.params['electron_readout_orientation'],
                    el_state_in         = 0,
                    phase_error         = self.params['phase_error_array_3'][pt])
            gate_seq1000.extend(carbon_tomo_seq1000)

            carbon_tomo_seq1001 = self.readout_carbon_sequence(
                    prefix              = 'Tomo1001_',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomo_Bases_1001'],
                    readout_orientation = self.params['electron_readout_orientation'],
                    el_state_in         = 1,
                    phase_error         = self.params['phase_error_array_3'][pt])
            gate_seq1001.extend(carbon_tomo_seq1001)

            carbon_tomo_seq1010 = self.readout_carbon_sequence(
                    prefix              = 'Tomo1010_',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomo_Bases_1010'],
                    readout_orientation = self.params['electron_readout_orientation'],
                    el_state_in         = 0,
                    phase_error         = self.params['phase_error_array_3'][pt])
            gate_seq1010.extend(carbon_tomo_seq1010)

            carbon_tomo_seq1011 = self.readout_carbon_sequence(
                    prefix              = 'Tomo1011_',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomo_Bases_1011'],
                    readout_orientation = self.params['electron_readout_orientation'],
                    el_state_in         = 1,
                    phase_error         = self.params['phase_error_array_3'][pt])
            gate_seq1011.extend(carbon_tomo_seq1011)




            carbon_tomo_seq1100 = self.readout_carbon_sequence(
                    prefix              = 'Tomo1100_',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomo_Bases_1100'],
                    readout_orientation = self.params['electron_readout_orientation'],
                    el_state_in         = 0,
                    phase_error         = self.params['phase_error_array_3'][pt])
            gate_seq1100.extend(carbon_tomo_seq1100)

            carbon_tomo_seq1101 = self.readout_carbon_sequence(
                    prefix              = 'Tomo1101_',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomo_Bases_1101'],
                    readout_orientation = self.params['electron_readout_orientation'],
                    el_state_in         = 1,
                    phase_error         = self.params['phase_error_array_3'][pt])
            gate_seq1101.extend(carbon_tomo_seq1101)

            carbon_tomo_seq1110 = self.readout_carbon_sequence(
                    prefix              = 'Tomo1110_',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomo_Bases_1110'],
                    readout_orientation = self.params['electron_readout_orientation'],
                    el_state_in         = 0,
                    phase_error         = self.params['phase_error_array_3'][pt])
            gate_seq1110.extend(carbon_tomo_seq1110)

            carbon_tomo_seq1111 = self.readout_carbon_sequence(
                    prefix              = 'Tomo1111_',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomo_Bases_1111'],
                    readout_orientation = self.params['electron_readout_orientation'],
                    el_state_in         = 1,
                    phase_error         = self.params['phase_error_array_3'][pt])
            gate_seq1111.extend(carbon_tomo_seq1111)


            #####################################
            ### Jumps statements for feedback ###
            #####################################
            
            Parity_seq_a[-1].go_to       = Parity_seq_b0[0].name
            Parity_seq_a[-1].event_jump  = Parity_seq_b1[0].name

            
            Parity_seq_b0[-1].go_to       = Parity_seq_a00[0].name
            Parity_seq_b0[-1].event_jump  = Parity_seq_a01[0].name

            Parity_seq_b1[-1].go_to       = Parity_seq_a10[0].name
            Parity_seq_b1[-1].event_jump  = Parity_seq_a11[0].name

            
            Parity_seq_a00[-1].go_to       = Parity_seq_b000[0].name
            Parity_seq_a00[-1].event_jump  = Parity_seq_b001[0].name

            Parity_seq_a01[-1].go_to       = Parity_seq_b010[0].name
            Parity_seq_a01[-1].event_jump  = Parity_seq_b011[0].name

            Parity_seq_a10[-1].go_to       = Parity_seq_b100[0].name
            Parity_seq_a10[-1].event_jump  = Parity_seq_b101[0].name

            Parity_seq_a11[-1].go_to       = Parity_seq_b110[0].name
            Parity_seq_a11[-1].event_jump  = Parity_seq_b111[0].name


            Parity_seq_b000[-1].go_to      = carbon_tomo_seq0000[0].name
            Parity_seq_b000[-1].event_jump = carbon_tomo_seq0001[0].name

            Parity_seq_b001[-1].go_to      = carbon_tomo_seq0010[0].name
            Parity_seq_b001[-1].event_jump = carbon_tomo_seq0011[0].name

            Parity_seq_b010[-1].go_to      = carbon_tomo_seq0100[0].name
            Parity_seq_b010[-1].event_jump = carbon_tomo_seq0101[0].name

            Parity_seq_b011[-1].go_to      = carbon_tomo_seq0110[0].name
            Parity_seq_b011[-1].event_jump = carbon_tomo_seq0111[0].name

            Parity_seq_b100[-1].go_to      = carbon_tomo_seq1000[0].name
            Parity_seq_b100[-1].event_jump = carbon_tomo_seq1001[0].name

            Parity_seq_b101[-1].go_to      = carbon_tomo_seq1010[0].name
            Parity_seq_b101[-1].event_jump = carbon_tomo_seq1011[0].name

            Parity_seq_b110[-1].go_to      = carbon_tomo_seq1100[0].name
            Parity_seq_b110[-1].event_jump = carbon_tomo_seq1101[0].name

            Parity_seq_b111[-1].go_to      = carbon_tomo_seq1110[0].name
            Parity_seq_b111[-1].event_jump = carbon_tomo_seq1111[0].name

            # In the end all roads lead to Rome
            Rome = Gate('Rome_'+str(pt),'passive_elt',
                    wait_time = 3e-6)
            gate_seq1111.append(Rome)

            gate_seq0000[-1].go_to     = gate_seq1111[-1].name
            gate_seq0001[-1].go_to     = gate_seq1111[-1].name
            
            gate_seq0010[-1].go_to     = gate_seq1111[-1].name
            gate_seq0011[-1].go_to     = gate_seq1111[-1].name
            
            gate_seq0100[-1].go_to     = gate_seq1111[-1].name
            gate_seq0101[-1].go_to     = gate_seq1111[-1].name

            gate_seq0110[-1].go_to     = gate_seq1111[-1].name
            gate_seq0111[-1].go_to     = gate_seq1111[-1].name
            
            gate_seq1000[-1].go_to     = gate_seq1111[-1].name
            gate_seq1001[-1].go_to     = gate_seq1111[-1].name
            
            gate_seq1100[-1].go_to     = gate_seq1111[-1].name
            gate_seq1101[-1].go_to     = gate_seq1111[-1].name
        
            gate_seq1010[-1].go_to     = gate_seq1111[-1].name
            gate_seq1011[-1].go_to     = gate_seq1111[-1].name
            
            gate_seq1110[-1].go_to     = gate_seq1111[-1].name
                        
            ###########################################################
            ### Set the electron state outcomes for the RO triggers ###
            ###########################################################

            ### after first parity msmnt
            gate_seq0[len(gate_seq)-1].el_state_before_gate     =  '0' 
            gate_seq1[len(gate_seq)-1].el_state_before_gate     =  '1' 

            ### after second parity msmnt
            gate_seq00[len(gate_seq)-1].el_state_before_gate    =  '0' 
            gate_seq00[len(gate_seq0)-1].el_state_before_gate   =  '0' 

            gate_seq01[len(gate_seq)-1].el_state_before_gate    =  '0' 
            gate_seq01[len(gate_seq0)-1].el_state_before_gate   =  '1' 

            gate_seq10[len(gate_seq)-1].el_state_before_gate    =  '1' 
            gate_seq10[len(gate_seq1)-1].el_state_before_gate   =  '0' 
            
            gate_seq11[len(gate_seq)-1].el_state_before_gate    =  '1' 
            gate_seq11[len(gate_seq1)-1].el_state_before_gate   =  '1' 

            ### after third parity msmnt
            gate_seq000[len(gate_seq)-1].el_state_before_gate    =  '0' 
            gate_seq000[len(gate_seq0)-1].el_state_before_gate   =  '0' 
            gate_seq000[len(gate_seq00)-1].el_state_before_gate  =  '0' 

            gate_seq001[len(gate_seq)-1].el_state_before_gate    =  '0' 
            gate_seq001[len(gate_seq0)-1].el_state_before_gate   =  '0' 
            gate_seq001[len(gate_seq00)-1].el_state_before_gate  =  '1' 

            gate_seq010[len(gate_seq)-1].el_state_before_gate    =  '0' 
            gate_seq010[len(gate_seq0)-1].el_state_before_gate   =  '1' 
            gate_seq010[len(gate_seq01)-1].el_state_before_gate  =  '0' 

            gate_seq011[len(gate_seq)-1].el_state_before_gate    =  '0' 
            gate_seq011[len(gate_seq0)-1].el_state_before_gate   =  '1' 
            gate_seq011[len(gate_seq01)-1].el_state_before_gate  =  '1' 

            gate_seq100[len(gate_seq)-1].el_state_before_gate    =  '1' 
            gate_seq100[len(gate_seq1)-1].el_state_before_gate   =  '0' 
            gate_seq100[len(gate_seq10)-1].el_state_before_gate  =  '0' 

            gate_seq101[len(gate_seq)-1].el_state_before_gate    =  '1' 
            gate_seq101[len(gate_seq1)-1].el_state_before_gate   =  '0' 
            gate_seq101[len(gate_seq10)-1].el_state_before_gate  =  '1' 

            gate_seq110[len(gate_seq)-1].el_state_before_gate    =  '1' 
            gate_seq110[len(gate_seq1)-1].el_state_before_gate   =  '1' 
            gate_seq110[len(gate_seq11)-1].el_state_before_gate  =  '0' 

            gate_seq111[len(gate_seq)-1].el_state_before_gate    =  '1' 
            gate_seq111[len(gate_seq1)-1].el_state_before_gate   =  '1' 
            gate_seq111[len(gate_seq11)-1].el_state_before_gate  =  '1' 

            ### after fourth parity msmnt
            gate_seq0000[len(gate_seq)-1].el_state_before_gate      =  '0' 
            gate_seq0000[len(gate_seq0)-1].el_state_before_gate     =  '0' 
            gate_seq0000[len(gate_seq00)-1].el_state_before_gate    =  '0' 
            gate_seq0000[len(gate_seq000)-1].el_state_before_gate   =  '0'

            gate_seq0001[len(gate_seq)-1].el_state_before_gate      =  '0' 
            gate_seq0001[len(gate_seq0)-1].el_state_before_gate     =  '0' 
            gate_seq0001[len(gate_seq00)-1].el_state_before_gate    =  '0' 
            gate_seq0001[len(gate_seq000)-1].el_state_before_gate   =  '1'

            gate_seq0010[len(gate_seq)-1].el_state_before_gate      =  '0' 
            gate_seq0010[len(gate_seq0)-1].el_state_before_gate     =  '0' 
            gate_seq0010[len(gate_seq00)-1].el_state_before_gate    =  '1' 
            gate_seq0010[len(gate_seq001)-1].el_state_before_gate   =  '0'

            gate_seq0011[len(gate_seq)-1].el_state_before_gate      =  '0' 
            gate_seq0011[len(gate_seq0)-1].el_state_before_gate     =  '0' 
            gate_seq0011[len(gate_seq00)-1].el_state_before_gate    =  '1' 
            gate_seq0011[len(gate_seq001)-1].el_state_before_gate   =  '1'

            gate_seq0100[len(gate_seq)-1].el_state_before_gate      =  '0' 
            gate_seq0100[len(gate_seq0)-1].el_state_before_gate     =  '1' 
            gate_seq0100[len(gate_seq01)-1].el_state_before_gate    =  '0' 
            gate_seq0100[len(gate_seq010)-1].el_state_before_gate   =  '0'

            gate_seq0101[len(gate_seq)-1].el_state_before_gate      =  '0' 
            gate_seq0101[len(gate_seq0)-1].el_state_before_gate     =  '1' 
            gate_seq0101[len(gate_seq01)-1].el_state_before_gate    =  '0' 
            gate_seq0101[len(gate_seq010)-1].el_state_before_gate   =  '1'

            gate_seq0110[len(gate_seq)-1].el_state_before_gate      =  '0' 
            gate_seq0110[len(gate_seq0)-1].el_state_before_gate     =  '1' 
            gate_seq0110[len(gate_seq01)-1].el_state_before_gate    =  '1' 
            gate_seq0110[len(gate_seq011)-1].el_state_before_gate   =  '0'

            gate_seq0111[len(gate_seq)-1].el_state_before_gate      =  '0' 
            gate_seq0111[len(gate_seq0)-1].el_state_before_gate     =  '1' 
            gate_seq0111[len(gate_seq01)-1].el_state_before_gate    =  '1' 
            gate_seq0111[len(gate_seq011)-1].el_state_before_gate   =  '1'

            gate_seq1000[len(gate_seq)-1].el_state_before_gate      =  '1' 
            gate_seq1000[len(gate_seq1)-1].el_state_before_gate     =  '0' 
            gate_seq1000[len(gate_seq10)-1].el_state_before_gate    =  '0' 
            gate_seq1000[len(gate_seq100)-1].el_state_before_gate   =  '0'

            gate_seq1001[len(gate_seq)-1].el_state_before_gate      =  '1' 
            gate_seq1001[len(gate_seq1)-1].el_state_before_gate     =  '0' 
            gate_seq1001[len(gate_seq10)-1].el_state_before_gate    =  '0' 
            gate_seq1001[len(gate_seq100)-1].el_state_before_gate   =  '1'

            gate_seq1010[len(gate_seq)-1].el_state_before_gate      =  '1' 
            gate_seq1010[len(gate_seq1)-1].el_state_before_gate     =  '0' 
            gate_seq1010[len(gate_seq10)-1].el_state_before_gate    =  '1' 
            gate_seq1010[len(gate_seq101)-1].el_state_before_gate   =  '0'

            gate_seq1011[len(gate_seq)-1].el_state_before_gate      =  '1' 
            gate_seq1011[len(gate_seq1)-1].el_state_before_gate     =  '0' 
            gate_seq1011[len(gate_seq10)-1].el_state_before_gate    =  '1' 
            gate_seq1011[len(gate_seq101)-1].el_state_before_gate   =  '1'

            gate_seq1100[len(gate_seq)-1].el_state_before_gate      =  '1' 
            gate_seq1100[len(gate_seq1)-1].el_state_before_gate     =  '1' 
            gate_seq1100[len(gate_seq11)-1].el_state_before_gate    =  '0' 
            gate_seq1100[len(gate_seq110)-1].el_state_before_gate   =  '0'

            gate_seq1101[len(gate_seq)-1].el_state_before_gate      =  '1' 
            gate_seq1101[len(gate_seq1)-1].el_state_before_gate     =  '1' 
            gate_seq1101[len(gate_seq11)-1].el_state_before_gate    =  '0' 
            gate_seq1101[len(gate_seq110)-1].el_state_before_gate   =  '1'

            gate_seq1110[len(gate_seq)-1].el_state_before_gate      =  '1' 
            gate_seq1110[len(gate_seq1)-1].el_state_before_gate     =  '1' 
            gate_seq1110[len(gate_seq11)-1].el_state_before_gate    =  '1' 
            gate_seq1110[len(gate_seq111)-1].el_state_before_gate   =  '0'

            gate_seq1111[len(gate_seq)-1].el_state_before_gate      =  '1' 
            gate_seq1111[len(gate_seq1)-1].el_state_before_gate     =  '1' 
            gate_seq1111[len(gate_seq11)-1].el_state_before_gate    =  '1' 
            gate_seq1111[len(gate_seq111)-1].el_state_before_gate   =  '1'

            ######################################
            ### Generate all the AWG sequences ###
            ######################################

            gate_seq  = self.generate_AWG_elements(gate_seq,pt)

            gate_seq0  = self.generate_AWG_elements(gate_seq0,pt)
            gate_seq1  = self.generate_AWG_elements(gate_seq1,pt)

            gate_seq00 = self.generate_AWG_elements(gate_seq00,pt)
            gate_seq01 = self.generate_AWG_elements(gate_seq01,pt)
            gate_seq10 = self.generate_AWG_elements(gate_seq10,pt)
            gate_seq11 = self.generate_AWG_elements(gate_seq11,pt)

            gate_seq000 = self.generate_AWG_elements(gate_seq000,pt)
            gate_seq010 = self.generate_AWG_elements(gate_seq010,pt)
            gate_seq100 = self.generate_AWG_elements(gate_seq100,pt)
            gate_seq001 = self.generate_AWG_elements(gate_seq001,pt)
            gate_seq110 = self.generate_AWG_elements(gate_seq110,pt)
            gate_seq011 = self.generate_AWG_elements(gate_seq011,pt)
            gate_seq101 = self.generate_AWG_elements(gate_seq101,pt)
            gate_seq111 = self.generate_AWG_elements(gate_seq111,pt)

            gate_seq0000 = self.generate_AWG_elements(gate_seq0000,pt)
            gate_seq0100 = self.generate_AWG_elements(gate_seq0100,pt)
            gate_seq1000 = self.generate_AWG_elements(gate_seq1000,pt)
            gate_seq0010 = self.generate_AWG_elements(gate_seq0010,pt)
            gate_seq1100 = self.generate_AWG_elements(gate_seq1100,pt)
            gate_seq0110 = self.generate_AWG_elements(gate_seq0110,pt)
            gate_seq1010 = self.generate_AWG_elements(gate_seq1010,pt)
            gate_seq1110 = self.generate_AWG_elements(gate_seq1110,pt)
            gate_seq0001 = self.generate_AWG_elements(gate_seq0001,pt)
            gate_seq0101 = self.generate_AWG_elements(gate_seq0101,pt)
            gate_seq1001 = self.generate_AWG_elements(gate_seq1001,pt)
            gate_seq0011 = self.generate_AWG_elements(gate_seq0011,pt)
            gate_seq1101 = self.generate_AWG_elements(gate_seq1101,pt)
            gate_seq0111 = self.generate_AWG_elements(gate_seq0111,pt)
            gate_seq1011 = self.generate_AWG_elements(gate_seq1011,pt)
            gate_seq1111 = self.generate_AWG_elements(gate_seq1111,pt)

            ##############################################
            ### Merge the branches into 1 AWG sequence ###
            ##############################################

            merged_sequence = []
            merged_sequence.extend(gate_seq)                 

            merged_sequence.extend(gate_seq0[len(gate_seq):])
            merged_sequence.extend(gate_seq1[len(gate_seq):])

            merged_sequence.extend(gate_seq00[len(gate_seq0):])
            merged_sequence.extend(gate_seq01[len(gate_seq0):])
            merged_sequence.extend(gate_seq10[len(gate_seq1):])
            merged_sequence.extend(gate_seq11[len(gate_seq1):])

            merged_sequence.extend(gate_seq000[len(gate_seq00):])
            merged_sequence.extend(gate_seq010[len(gate_seq01):])
            merged_sequence.extend(gate_seq100[len(gate_seq10):])
            merged_sequence.extend(gate_seq110[len(gate_seq11):])
            merged_sequence.extend(gate_seq001[len(gate_seq00):])
            merged_sequence.extend(gate_seq011[len(gate_seq01):])
            merged_sequence.extend(gate_seq101[len(gate_seq10):])
            merged_sequence.extend(gate_seq111[len(gate_seq11):])

            merged_sequence.extend(gate_seq0000[len(gate_seq000):])
            merged_sequence.extend(gate_seq0100[len(gate_seq010):])
            merged_sequence.extend(gate_seq1000[len(gate_seq100):])
            merged_sequence.extend(gate_seq1100[len(gate_seq110):])
            merged_sequence.extend(gate_seq0010[len(gate_seq001):])
            merged_sequence.extend(gate_seq0110[len(gate_seq011):])
            merged_sequence.extend(gate_seq1010[len(gate_seq101):])
            merged_sequence.extend(gate_seq1110[len(gate_seq111):])
            merged_sequence.extend(gate_seq0001[len(gate_seq000):])
            merged_sequence.extend(gate_seq0101[len(gate_seq010):])
            merged_sequence.extend(gate_seq1001[len(gate_seq100):])
            merged_sequence.extend(gate_seq1101[len(gate_seq110):])
            merged_sequence.extend(gate_seq0011[len(gate_seq001):])
            merged_sequence.extend(gate_seq0111[len(gate_seq011):])
            merged_sequence.extend(gate_seq1011[len(gate_seq101):])
            merged_sequence.extend(gate_seq1111[len(gate_seq111):])


            print '*'*10
            print 'seq_merged'
            for i,g in enumerate(merged_sequence):
                pass
                # print
                # print g.name
                # print g.Gate_type
                # if debug and hasattr(g,'el_state_before_gate'):# != None:
                #     # print g.el_state_before_gate
                #     print '                        el state before and after (%s,%s)'%(g.el_state_before_gate, g.el_state_after_gate)
                # elif debug:
                #     print 'does not have attribute el_state_before_gate'


                # if  debug==True:
                #     phase_Q1 = g.C_phases_before_gate[self.params['carbon_list'][0]]
                #     if phase_Q1 != None:
                #         phase_Q1 = np.round(phase_Q1/np.pi*180,decimals = 1)
                #     phase_Q2 = g.C_phases_before_gate[self.params['carbon_list'][1]]
                #     if phase_Q2 != None:
                #         phase_Q2 = np.round(phase_Q2/np.pi*180,decimals = 1)
                #     phase_Q3 = g.C_phases_before_gate[self.params['carbon_list'][2]]
                #     if phase_Q3 != None:
                #         phase_Q3 = np.round(phase_Q3/np.pi*180,decimals = 1)
                #         print '                        '+ str(phase_Q1)+ '   '+ str(phase_Q2)+ '   ' +str(phase_Q3)
                #     phase_Q1 = g.C_phases_after_gate[self.params['carbon_list'][0]]
                #     if phase_Q1 != None:
                #         phase_Q1 = np.round(phase_Q1/np.pi*180,decimals = 1)
                #     phase_Q2 = g.C_phases_after_gate[self.params['carbon_list'][1]]
                #     if phase_Q2 != None:
                #         phase_Q2 = np.round(phase_Q2/np.pi*180,decimals = 1)
                #     phase_Q3 = g.C_phases_after_gate[self.params['carbon_list'][2]]
                #     if phase_Q3 != None:
                #         phase_Q3 = np.round(phase_Q3/np.pi*180,decimals = 1)
                #         print '                        '+ str(phase_Q1)+ '   '+ str(phase_Q2)+ '   ' +str(phase_Q3)

            #Convert elements to AWG sequence and add to combined list
            list_of_elements, seq = self.combine_to_AWG_sequence(merged_sequence, explicit=True)
            combined_list_of_elements.extend(list_of_elements)

            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'

class Three_QB_det_QEC_ENC(MBI_C13):
    '''
    for one error, positive and negative, QEC and encoding is measured in the same run
    '''
    mprefix         = 'Three_QB_det_QEC_ENC'
    adwin_process   = 'MBI_multiple_C13'

    def generate_sequence(self,upload=True,debug = False):
        pts = self.params['pts']

        ### initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Two Qubit MBE')

        for pt in range(pts):
            print
            print '-' *20

            if pt%2 == 0:
                extra_prefix = 'QEC'

            elif pt%2 == 0:
                extra_prefix = 'ENC'

            gate_seq = []

            ### Nitrogen MBI
            mbi = Gate('N_MBI_pt'+str(pt),'MBI')
            mbi_seq = [mbi]
            gate_seq.extend(mbi_seq)

            ### Carbon initialization
            init_wait_for_trigger = True
            for kk in range(self.params['Nr_C13_init']):
                carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                    prefix                = extra_prefix + 'C_MBI_step_' + str(kk+1) + '_C',
                    wait_for_trigger      = init_wait_for_trigger, pt =pt,
                    initialization_method = self.params['init_method_list'][kk],
                    C_init_state          = self.params['init_state_list'][kk],
                    addressed_carbon      = self.params['carbon_init_list'][kk])
                gate_seq.extend(carbon_init_seq)
                init_wait_for_trigger = False

            ### Encoding of logical state

            for kk in range(self.params['Nr_MBE']):

                probabilistic_MBE_seq =     self.logic_init_seq(
                        prefix              = extra_prefix+'Encode_' ,
                        pt                  =  pt,
                        carbon_list         = self.params['MBE_list'],
                        RO_basis_list       = self.params['MBE_bases'],
                        RO_trigger_duration = 90e-6,
                        el_RO_result        = '0',
                        logic_state         = self.params['3qb_logical_state'] ,
                        go_to_element       = mbi,
                        event_jump_element   = 'next',
                        readout_orientation = 'positive',
                        phase_error         = self.params['phase_error_array'][pt])

                gate_seq.extend(probabilistic_MBE_seq)

            if pt%2 == 1: # just RO, no QEC
                carbon_tomo_seq = self.readout_carbon_sequence(
                        prefix              = extra_prefix+'Tomo',
                        pt                  = pt,
                        go_to_element       = None,
                        event_jump_element  = None,
                        RO_trigger_duration = 10e-6,
                        carbon_list         = self.params['carbon_list'],
                        RO_basis_list       = self.params['Tomography Bases'],
                        readout_orientation = self.params['electron_readout_orientation'])
                gate_seq.extend(carbon_tomo_seq)

                gate_seq = self.generate_AWG_elements(gate_seq,pt)

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

                        if ((g.C_phases_before_gate[self.params['carbon_list'][0]] == None) and (g.C_phases_before_gate[self.params['carbon_list'][1]] == None)):
                            print "[ None , None ]"
                        elif g.C_phases_before_gate[self.params['carbon_list'][0]] == None:
                            print "[ None , %.3f ]" %(g.C_phases_before_gate[self.params['carbon_list'][1]]/np.pi*180)
                        elif g.C_phases_before_gate[self.params['carbon_list'][1]] == None:
                            print "[ %.3f, None ]" %(g.C_phases_before_gate[self.params['carbon_list'][0]]/np.pi*180)
                        else:
                            print "[ %.3f , %.3f ]" %(g.C_phases_before_gate[self.params['carbon_list'][0]]/np.pi*180, g.C_phases_before_gate[self.params['carbon_list'][1]]/np.pi*180)


                        if ((g.C_phases_after_gate[self.params['carbon_list'][0]] == None) and (g.C_phases_after_gate[self.params['carbon_list'][1]] == None)):
                            print "[ None , None ]"
                        elif g.C_phases_after_gate[self.params['carbon_list'][0]] == None:
                            print "[ None , %.3f ]" %(g.C_phases_after_gate[self.params['carbon_list'][1]]/np.pi*180)
                        elif g.C_phases_after_gate[self.params['carbon_list'][1]] == None:
                            print "[ %.3f, None ]" %(g.C_phases_after_gate[self.params['carbon_list'][0]]/np.pi*180)
                        else:
                            print "[ %.3f , %.3f ]" %(g.C_phases_after_gate[self.params['carbon_list'][0]]/np.pi*180, g.C_phases_after_gate[self.params['carbon_list'][1]]/np.pi*180)

            elif pt%2 == 0: # DO QEC

                ### Parity measurements to detect error syndrome

                ### Parity msmt a
                if self.params['add_wait_gate'] == True and self.params['free_evolution_time_1'][pt] !=0 and self.params['wait_in_msm1'] == True:
                    el_in_state = 1
                else:
                    el_in_state = 0

                Parity_seq_a = self.readout_carbon_sequence(
                            prefix              = extra_prefix+'Parity_A_' ,
                            pt                  = pt,
                            RO_trigger_duration = 150e-6,
                            carbon_list         = self.params['Parity_a_carbon_list'],
                            RO_basis_list       = self.params['Parity_a_RO_list'],
                            el_RO_result         = '0',
                            readout_orientation = self.params['Parity_a_RO_orientation'],
                            el_state_in     = el_in_state)

                gate_seq.extend(Parity_seq_a)

                #############################
                gate_seq0 = copy.deepcopy(gate_seq)
                gate_seq1 = copy.deepcopy(gate_seq)

                ### Parity msmt b
                el_in_state_b0 = 0
                el_in_state_b1 = 1

                Parity_seq_b0 = self.readout_carbon_sequence(
                            prefix              = extra_prefix+'Parity_B0_' ,
                            pt                  = pt,
                            RO_trigger_duration = 150e-6,
                            carbon_list         = self.params['Parity_b_carbon_list'],
                            RO_basis_list       = self.params['Parity_b_RO_list'],
                            el_RO_result         = '0',
                            readout_orientation = self.params['Parity_b_RO_orientation'],
                            el_state_in     = el_in_state_b0)

                Parity_seq_b1 = self.readout_carbon_sequence(
                            prefix              = extra_prefix+'Parity_B1_' ,
                            pt                  = pt,
                            RO_trigger_duration = 150e-6,
                            carbon_list         = self.params['Parity_b_carbon_list'],
                            RO_basis_list       = self.params['Parity_b_RO_list'],
                            el_RO_result        = '0',
                            readout_orientation = self.params['Parity_b_RO_orientation'],
                            el_state_in     = el_in_state_b1)

                gate_seq0.extend(Parity_seq_b0)
                gate_seq1.extend(Parity_seq_b1)

                gate_seq00 = copy.deepcopy(gate_seq0)
                gate_seq01 = copy.deepcopy(gate_seq0)
                gate_seq10 = copy.deepcopy(gate_seq1)
                gate_seq11 = copy.deepcopy(gate_seq1)

                ### add half of the wait time again if we want to sweep time
                if self.params['add_wait_gate'] == True:
                    wait_gate2_00 = Gate('Wait_gate2_00_'+str(pt),'passive_elt',
                             wait_time = self.params['free_evolution_time_2'][pt])
                    wait_gate2_01 = Gate('Wait_gate2_01_'+str(pt),'passive_elt',
                             wait_time = self.params['free_evolution_time_2'][pt])

                    wait_gate2_10 = Gate('Wait_gate2_10_'+str(pt),'passive_elt',
                             wait_time = self.params['free_evolution_time_2'][pt])
                    wait_gate2_11 = Gate('Wait_gate2_11_'+str(pt),'passive_elt',
                             wait_time = self.params['free_evolution_time_2'][pt])

                    wait_seq2_00 = [wait_gate2_00];
                    wait_seq2_01 = [wait_gate2_01];
                    wait_seq2_10 = [wait_gate2_10];
                    wait_seq2_11 = [wait_gate2_11];

                    if self.params['free_evolution_time_2'][pt] !=0:
                        gate_seq00.extend(wait_seq2_00)
                        gate_seq01.extend(wait_seq2_01)
                        gate_seq10.extend(wait_seq2_10)
                        gate_seq11.extend(wait_seq2_11)



                carbon_tomo_seq00 = self.readout_carbon_sequence(
                        prefix              = extra_prefix+'Tomo00_',
                        pt                  = pt,
                        go_to_element       = None,
                        event_jump_element  = None,
                        RO_trigger_duration = 10e-6,
                        carbon_list         = self.params['carbon_list'],
                        RO_basis_list       = self.params['Tomo_Bases_00'],
                        readout_orientation = self.params['electron_readout_orientation'],
                        el_state_in     = 0,
                        phase_error = self.params['phase_error_array_2'][pt])

                gate_seq00.extend(carbon_tomo_seq00)

                carbon_tomo_seq01 = self.readout_carbon_sequence(
                        prefix              = extra_prefix+'Tomo01_',
                        pt                  = pt,
                        go_to_element       = None,
                        event_jump_element  = None,
                        RO_trigger_duration = 10e-6,
                        carbon_list         = self.params['carbon_list'],
                        RO_basis_list       = self.params['Tomo_Bases_01'],
                        readout_orientation = self.params['electron_readout_orientation'],
                        el_state_in     = 1,
                        phase_error = self.params['phase_error_array_2'][pt])
                gate_seq01.extend(carbon_tomo_seq01)

                carbon_tomo_seq10 = self.readout_carbon_sequence(
                        prefix              = extra_prefix+'Tomo10_',
                        pt                  = pt,
                        go_to_element       = None,
                        event_jump_element  = None,
                        RO_trigger_duration = 10e-6,
                        carbon_list         = self.params['carbon_list'],
                        RO_basis_list       = self.params['Tomo_Bases_10'],
                        readout_orientation = self.params['electron_readout_orientation'],
                        el_state_in     = 0,
                        phase_error = self.params['phase_error_array_2'][pt])
                gate_seq10.extend(carbon_tomo_seq10)

                carbon_tomo_seq11 = self.readout_carbon_sequence(
                        prefix              = extra_prefix+'Tomo11_',
                        pt                  = pt,
                        go_to_element       = None,
                        event_jump_element  = None,
                        RO_trigger_duration = 10e-6,
                        carbon_list         = self.params['carbon_list'],
                        RO_basis_list       = self.params['Tomo_Bases_11'],
                        readout_orientation = self.params['electron_readout_orientation'],
                        el_state_in     = 1,
                        phase_error = self.params['phase_error_array_2'][pt])

                gate_seq11.extend(carbon_tomo_seq11)

                # Make jump statements for branching to two different ROs
                Parity_seq_a[-1].go_to       = Parity_seq_b0[0].name
                Parity_seq_a[-1].event_jump  = Parity_seq_b1[0].name

                if self.params['free_evolution_time_2'][pt] !=0 and self.params['add_wait_gate'] == True:
                    Parity_seq_b0[-1].go_to       = wait_seq2_00[0].name
                    Parity_seq_b0[-1].event_jump  = wait_seq2_01[0].name

                    Parity_seq_b1[-1].go_to       = wait_seq2_10[0].name
                    Parity_seq_b1[-1].event_jump  = wait_seq2_11[0].name
                else:
                    Parity_seq_b0[-1].go_to       = carbon_tomo_seq00[0].name
                    Parity_seq_b0[-1].event_jump  = carbon_tomo_seq01[0].name

                    Parity_seq_b1[-1].go_to       = carbon_tomo_seq10[0].name
                    Parity_seq_b1[-1].event_jump  = carbon_tomo_seq11[0].name

                # In the end all roads lead to Rome
                Rome = Gate('Rome_'+str(pt),'passive_elt',
                        wait_time = 3e-6)
                gate_seq11.append(Rome)
                gate_seq00[-1].go_to     = gate_seq11[-1].name
                gate_seq01[-1].go_to     = gate_seq11[-1].name
                gate_seq10[-1].go_to     = gate_seq11[-1].name

                ################################################################
                ### Generate the AWG_elements, including all the phase gates for all branches###
                ################################################################

                gate_seq0[len(gate_seq)-1].el_state_before_gate =  '0' #Element -1

                gate_seq00[len(gate_seq)-1].el_state_before_gate =  '0' #Element -1
                gate_seq01[len(gate_seq)-1].el_state_before_gate =  '0' #Element -1
                gate_seq00[len(gate_seq0)-1].el_state_before_gate = '0' #Element -1
                gate_seq01[len(gate_seq0)-1].el_state_before_gate = '1' #Element -1

                gate_seq1[len(gate_seq)-1].el_state_before_gate =  '1' #Element -1

                gate_seq10[len(gate_seq)-1].el_state_before_gate =  '1' #Element -1
                gate_seq11[len(gate_seq)-1].el_state_before_gate =  '1' #Element -1
                gate_seq10[len(gate_seq1)-1].el_state_before_gate = '0' #Element -1
                gate_seq11[len(gate_seq1)-1].el_state_before_gate = '1' #Element -1

                gate_seq  = self.generate_AWG_elements(gate_seq,pt)
                gate_seq00 = self.generate_AWG_elements(gate_seq00,pt)
                gate_seq0  = self.generate_AWG_elements(gate_seq0,pt)
                gate_seq01 = self.generate_AWG_elements(gate_seq01,pt)
                gate_seq1  = self.generate_AWG_elements(gate_seq1,pt)
                gate_seq10 = self.generate_AWG_elements(gate_seq10,pt)
                gate_seq11 = self.generate_AWG_elements(gate_seq11,pt)

                # Merge the bracnhes into one AWG sequence
                merged_sequence = []
                merged_sequence.extend(gate_seq)                  #TODO: remove gate_seq and add gate_seq1 to gate_seq0 without common part

                merged_sequence.extend(gate_seq0[len(gate_seq):])
                merged_sequence.extend(gate_seq1[len(gate_seq):])

                merged_sequence.extend(gate_seq00[len(gate_seq0):])
                merged_sequence.extend(gate_seq01[len(gate_seq0):])
                merged_sequence.extend(gate_seq10[len(gate_seq1):])
                merged_sequence.extend(gate_seq11[len(gate_seq1):])

                print '*'*10
                print 'seq_merged'
                for i,g in enumerate(merged_sequence):
                    print
                    print g.name
                    print g.Gate_type
                    if debug and hasattr(g,'el_state_before_gate'):# != None:
                        # print g.el_state_before_gate
                        print '                        el state before and after (%s,%s)'%(g.el_state_before_gate, g.el_state_after_gate)
                    elif debug:
                        print 'does not have attribute el_state_before_gate'


                    if  debug==True:
                        phase_Q1 = g.C_phases_before_gate[self.params['carbon_list'][0]]
                        if phase_Q1 != None:
                            phase_Q1 = np.round(phase_Q1/np.pi*180,decimals = 1)
                        phase_Q2 = g.C_phases_before_gate[self.params['carbon_list'][1]]
                        if phase_Q2 != None:
                            phase_Q2 = np.round(phase_Q2/np.pi*180,decimals = 1)
                        phase_Q3 = g.C_phases_before_gate[self.params['carbon_list'][2]]
                        if phase_Q3 != None:
                            phase_Q3 = np.round(phase_Q3/np.pi*180,decimals = 1)
                            print '                        '+ str(phase_Q1)+ '   '+ str(phase_Q2)+ '   ' +str(phase_Q3)
                        phase_Q1 = g.C_phases_after_gate[self.params['carbon_list'][0]]
                        if phase_Q1 != None:
                            phase_Q1 = np.round(phase_Q1/np.pi*180,decimals = 1)
                        phase_Q2 = g.C_phases_after_gate[self.params['carbon_list'][1]]
                        if phase_Q2 != None:
                            phase_Q2 = np.round(phase_Q2/np.pi*180,decimals = 1)
                        phase_Q3 = g.C_phases_after_gate[self.params['carbon_list'][2]]
                        if phase_Q3 != None:
                            phase_Q3 = np.round(phase_Q3/np.pi*180,decimals = 1)
                            print '                        '+ str(phase_Q1)+ '   '+ str(phase_Q2)+ '   ' +str(phase_Q3)

                #Convert elements to AWG sequence and add to combined list
                list_of_elements, seq = self.combine_to_AWG_sequence(merged_sequence, explicit=True)
                combined_list_of_elements.extend(list_of_elements)

                for seq_el in seq.elements:
                    combined_seq.append_element(seq_el)

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'
            
