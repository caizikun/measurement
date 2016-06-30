"""
This file contains all GHZ measurement classes.
derived from DD_2.py
"""


import qt
import copy
from measurement.lib.pulsar import pulse, pulselib, element, pulsar
reload(pulsar)

import measurement.lib.measurement2.adwin_ssro.DD_2 as DD; reload(DD)
from measurement.lib.measurement2.adwin_ssro.DD_2 import Gate




class GHZ_ThreeQB(DD.MBI_C13):
    '''
    #Sequence
                                                            --[Invert YXY_000|-|Tomography_000|
                                        --|Invert YXY_00|-|Parity_YYX_00|
                                                            --[Invert YXY_001|-|Tomography_001|
                        --|Invert XYY_9|-|Parity_YXY_0|
                                                            --[Invert YXY_010|-|Tomography_010|
                                        --|Invert YXY_01|-|Parity_YYX_01|
                                                            --[Invert YXY_011|-|Tomography_011|
    |N-MBI| -|Parity_XYY|
                                                            --[Invert YXY_100|-|Tomography_100|
                                        --|Invert YXY_10|-|Parity_YYX_10|
                                                            --[Invert YXY_101|-|Tomography_101|
                        --|Invert XYY_1|-|Parity_YXY_1|
                                                            --[Invert YXY_110|-|Tomography_110|
                                        --|Invert YXY_11|-|Parity_YYX_11|
                                                            --|Invert YXY_111|-|Tomography_111|
    For GHZ test: Tomography=Parity_XXX
    '''
    
    mprefix = 'GHZ'
    adwin_process = 'MBI_multiple_C13'

    def generate_sequence(self,upload=True,debug = False):
        pts = self.params['pts']

        ### initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('GHZ')

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

            ####################
            ### Optional: initialize C ###
            ####################

            if self.params['initialize_carbons'] == True:
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


            ########################################################    
            ### XYY, YXY, YYX Parity measurements ###
            ########################################################

            ######################
            ### Parity msmt XYY ###
            ######################

            Parity_seq_xyy = self.readout_carbon_sequence(
                        prefix              = 'Parity_XYY_' ,
                        pt                  = pt,
                        RO_trigger_duration = 150e-6,#?? Is this a good value?
                        carbon_list         = self.params['Parity_xyy_carbon_list'],
                        RO_basis_list       = self.params['Parity_xyy_RO_list'],
                        readout_orientation = self.params['Parity_xyy_RO_orientation'],
                        do_init_pi2         = self.params['Parity_xyy_do_init_pi2'],
                        wait_for_trigger    = True,
                        el_RO_result        = '0',
                        el_state_in         = 0)

            gate_seq.extend(Parity_seq_xyy)

            gate_seq0 = copy.deepcopy(gate_seq)
            gate_seq1 = copy.deepcopy(gate_seq)

            ######################
            ### Parity msmt YXY ###
            ######################
            
            el_in_state_yxy0 = 0
            el_in_state_yxy1 = 1

            Invert_parity_seq_xyy0 = self.invert_readout_carbon_sequence(
                        prefix              = 'Invert_XYY0_',
                        pt                  = pt,
                        carbon_list         = self.params['Invert_xyy_carbon_list'],
                        RO_basis_list       = self.params['Invert_xyy_RO_list'],
                        readout_orientation = self.params['Parity_xyy_RO_orientation'],
                        do_final_pi2        = self.params['Invert_xyy_do_final_pi2'],
                        inv_el_state_in     = 0,
                        el_state_in         = el_in_state_yxy0)

            Parity_seq_yxy0 = self.readout_carbon_sequence(
                        prefix              = 'Parity_YXY0_' ,
                        pt                  = pt,
                        RO_trigger_duration = 150e-6,
                        carbon_list         = self.params['Parity_yxy_carbon_list'],
                        RO_basis_list       = self.params['Parity_yxy_RO_list'],
                        readout_orientation = self.params['Parity_yxy_RO_orientation'],
                        do_init_pi2         = self.params['Parity_yxy_do_init_pi2'],
                        el_RO_result         = '0',
                        el_state_in         = 0)                        

            Invert_parity_seq_xyy1 = self.invert_readout_carbon_sequence(
                        prefix              = 'Invert_XYY1_' ,
                        pt                  = pt,
                        carbon_list         = self.params['Invert_xyy_carbon_list'],
                        RO_basis_list       = self.params['Invert_xyy_RO_list'],
                        readout_orientation = self.params['Parity_xyy_RO_orientation'],
                        do_final_pi2        = self.params['Invert_xyy_do_final_pi2'],
                        inv_el_state_in     = 0,
                        el_state_in         = el_in_state_yxy1)

            Parity_seq_yxy1 = self.readout_carbon_sequence(
                        prefix              = 'Parity_YXY1_' ,
                        pt                  = pt,
                        RO_trigger_duration = 150e-6,
                        carbon_list         = self.params['Parity_yxy_carbon_list'],
                        RO_basis_list       = self.params['Parity_yxy_RO_list'],
                        readout_orientation = self.params['Parity_yxy_RO_orientation'],
                        do_init_pi2         = self.params['Parity_yxy_do_init_pi2'],
                        el_RO_result        = '0',
                        el_state_in         = 0)

            gate_seq0.extend(Invert_parity_seq_xyy0)
            gate_seq0.extend(Parity_seq_yxy0)
            gate_seq1.extend(Invert_parity_seq_xyy1)
            gate_seq1.extend(Parity_seq_yxy1)

            gate_seq00 = copy.deepcopy(gate_seq0)
            gate_seq01 = copy.deepcopy(gate_seq0)
            gate_seq10 = copy.deepcopy(gate_seq1)
            gate_seq11 = copy.deepcopy(gate_seq1)


            ######################
            ### Parity msmt YYX ###
            ######################
            
            el_in_state_yyx00 = 0
            el_in_state_yyx01 = 1
            el_in_state_yyx10 = 0
            el_in_state_yyx11 = 1

            Invert_parity_seq_yxy00 = self.invert_readout_carbon_sequence(
                        prefix              = 'Invert_YXY00_' ,
                        pt                  = pt,
                        carbon_list         = self.params['Invert_yxy_carbon_list'],
                        RO_basis_list       = self.params['Invert_yxy_RO_list'],
                        readout_orientation = self.params['Parity_yxy_RO_orientation'],
                        do_final_pi2        = self.params['Invert_yxy_do_final_pi2'],
                        inv_el_state_in     = 0,
                        el_state_in         = el_in_state_yyx00)

            Parity_seq_yyx00 = self.readout_carbon_sequence(
                        prefix              = 'Parity_YYX00_' ,
                        pt                  = pt,
                        RO_trigger_duration = 150e-6,
                        carbon_list         = self.params['Parity_yyx_carbon_list'],
                        RO_basis_list       = self.params['Parity_yyx_RO_list'],
                        readout_orientation = self.params['Parity_yyx_RO_orientation'],
                        do_init_pi2         = self.params['Parity_yyx_do_init_pi2'],
                        el_RO_result         = '0',
                        el_state_in         = 0)

            Invert_parity_seq_yxy01 = self.invert_readout_carbon_sequence(
                        prefix              = 'Invert_YXY01_' ,
                        pt                  = pt,
                        carbon_list         = self.params['Invert_yxy_carbon_list'],
                        RO_basis_list       = self.params['Invert_yxy_RO_list'],
                        readout_orientation = self.params['Parity_yxy_RO_orientation'],
                        do_final_pi2        = self.params['Invert_yxy_do_final_pi2'],
                        inv_el_state_in     = 0,
                        el_state_in         = el_in_state_yyx01)

            Parity_seq_yyx01 = self.readout_carbon_sequence(
                        prefix              = 'Parity_YYX01_' ,
                        pt                  = pt,
                        RO_trigger_duration = 150e-6,
                        carbon_list         = self.params['Parity_yyx_carbon_list'],
                        RO_basis_list       = self.params['Parity_yyx_RO_list'],
                        readout_orientation = self.params['Parity_yyx_RO_orientation'],
                        do_init_pi2         = self.params['Parity_yyx_do_init_pi2'],
                        el_RO_result        = '0',
                        el_state_in         = 0)

            Invert_parity_seq_yxy10 = self.invert_readout_carbon_sequence(
                        prefix              = 'Invert_YXY10_' ,
                        pt                  = pt,
                        carbon_list         = self.params['Invert_yxy_carbon_list'],
                        RO_basis_list       = self.params['Invert_yxy_RO_list'],
                        readout_orientation = self.params['Parity_yxy_RO_orientation'],
                        do_final_pi2        = self.params['Invert_yxy_do_final_pi2'],
                        inv_el_state_in     = 0,
                        el_state_in         = el_in_state_yyx10)

            Parity_seq_yyx10 = self.readout_carbon_sequence(
                        prefix              = 'Parity_YYX10_' ,
                        pt                  = pt,
                        RO_trigger_duration = 150e-6,
                        carbon_list         = self.params['Parity_yyx_carbon_list'],
                        RO_basis_list       = self.params['Parity_yyx_RO_list'],
                        readout_orientation = self.params['Parity_yyx_RO_orientation'],
                        do_init_pi2         = self.params['Parity_yyx_do_init_pi2'],
                        el_RO_result        = '0',
                        el_state_in         = 0)

            Invert_parity_seq_yxy11 = self.invert_readout_carbon_sequence(
                        prefix              = 'Invert_YXY11_' ,
                        pt                  = pt,
                        carbon_list         = self.params['Invert_yxy_carbon_list'],
                        RO_basis_list       = self.params['Invert_yxy_RO_list'],
                        readout_orientation = self.params['Parity_yxy_RO_orientation'],
                        do_final_pi2        = self.params['Invert_yxy_do_final_pi2'],
                        inv_el_state_in     = 0,
                        el_state_in         = el_in_state_yyx11)

            Parity_seq_yyx11 = self.readout_carbon_sequence(
                        prefix              = 'Parity_YYX11_' ,
                        pt                  = pt,
                        RO_trigger_duration = 150e-6,
                        carbon_list         = self.params['Parity_yyx_carbon_list'],
                        RO_basis_list       = self.params['Parity_yyx_RO_list'],
                        readout_orientation = self.params['Parity_yyx_RO_orientation'],
                        do_init_pi2         = self.params['Parity_yyx_do_init_pi2'],
                        el_RO_result        = '0',
                        el_state_in         = 0)

            gate_seq00.extend(Invert_parity_seq_yxy00)
            gate_seq00.extend(Parity_seq_yyx00)
            gate_seq01.extend(Invert_parity_seq_yxy01)
            gate_seq01.extend(Parity_seq_yyx01)
            gate_seq10.extend(Invert_parity_seq_yxy10)
            gate_seq10.extend(Parity_seq_yyx10)
            gate_seq11.extend(Invert_parity_seq_yxy11)
            gate_seq11.extend(Parity_seq_yyx11)

            gate_seq000 = copy.deepcopy(gate_seq00)
            gate_seq001 = copy.deepcopy(gate_seq00)
            gate_seq010 = copy.deepcopy(gate_seq01)
            gate_seq011 = copy.deepcopy(gate_seq01)
            gate_seq100 = copy.deepcopy(gate_seq10)
            gate_seq101 = copy.deepcopy(gate_seq10)
            gate_seq110 = copy.deepcopy(gate_seq11)
            gate_seq111 = copy.deepcopy(gate_seq11)

            ######################
            ### Tomography or Parity Msmt XXX ###
            ######################

            el_in_state_tomo000 = 0
            el_in_state_tomo001 = 1
            el_in_state_tomo010 = 0
            el_in_state_tomo011 = 1
            el_in_state_tomo100 = 0
            el_in_state_tomo101 = 1
            el_in_state_tomo110 = 0
            el_in_state_tomo111 = 1

            Invert_parity_seq_yyx000= self.invert_readout_carbon_sequence(
                        prefix              = 'Invert_YYX000_' ,
                        pt                  = pt,
                        carbon_list         = self.params['Invert_yyx_carbon_list'],
                        RO_basis_list       = self.params['Invert_yxy_RO_list'],
                        readout_orientation = self.params['Parity_yyx_RO_orientation'],
                        do_final_pi2        = self.params['Invert_yyx_do_final_pi2'],
                        inv_el_state_in     = 0,
                        el_state_in         = el_in_state_tomo000)

            carbon_tomo_seq000 = self.readout_carbon_sequence(
                        prefix              = 'Tomo000_',
                        pt                  = pt,
                        go_to_element       = None,
                        event_jump_element  = None,
                        RO_trigger_duration = 10e-6,
                        carbon_list         = self.params['Tomo_carbon_list'],
                        RO_basis_list       = self.params['Tomo_RO_list'],
                        readout_orientation = self.params['Tomo_RO_orientation'],
                        do_init_pi2         = self.params['Tomo_do_init_pi2'],
                        phase_error         = self.params['final_phases'],
                        flip_RO             = self.params['flip_000'],
                        do_RO_electron      = self.params['RO_electron'],
                        el_state_in         = 0)#el_in_state_tomo000)

            Invert_parity_seq_yyx001= self.invert_readout_carbon_sequence(
                        prefix              = 'Invert_YYX001_' ,
                        pt                  = pt,
                        carbon_list         = self.params['Invert_yyx_carbon_list'],
                        RO_basis_list       = self.params['Invert_yxy_RO_list'],
                        readout_orientation = self.params['Parity_yyx_RO_orientation'],
                        do_final_pi2        = self.params['Invert_yyx_do_final_pi2'],
                        inv_el_state_in     = 0,
                        el_state_in         = el_in_state_tomo001)

            carbon_tomo_seq001 = self.readout_carbon_sequence(
                        prefix              = 'Tomo001_',
                        pt                  = pt,
                        go_to_element       = None,
                        event_jump_element  = None,
                        RO_trigger_duration = 10e-6,
                        carbon_list         = self.params['Tomo_carbon_list'],
                        RO_basis_list       = self.params['Tomo_RO_list'],
                        readout_orientation = self.params['Tomo_RO_orientation'],
                        do_init_pi2         = self.params['Tomo_do_init_pi2'],
                        phase_error         = self.params['final_phases'],
                        flip_RO             = self.params['flip_001'],
                        do_RO_electron         = self.params['RO_electron'],                        
                        el_state_in         = 0)#el_in_state_tomo000)


            Invert_parity_seq_yyx010= self.invert_readout_carbon_sequence(
                        prefix              = 'Invert_YYX010_' ,
                        pt                  = pt,
                        carbon_list         = self.params['Invert_yyx_carbon_list'],
                        RO_basis_list       = self.params['Invert_yxy_RO_list'],
                        readout_orientation = self.params['Parity_yyx_RO_orientation'],
                        do_final_pi2        = self.params['Invert_yyx_do_final_pi2'],
                        inv_el_state_in     = 0,
                        el_state_in         = el_in_state_tomo010)

            carbon_tomo_seq010 = self.readout_carbon_sequence(
                        prefix              = 'Tomo010_',
                        pt                  = pt,
                        go_to_element       = None,
                        event_jump_element  = None,
                        RO_trigger_duration = 10e-6,
                        carbon_list         = self.params['Tomo_carbon_list'],
                        RO_basis_list       = self.params['Tomo_RO_list'],
                        readout_orientation = self.params['Tomo_RO_orientation'],
                        do_init_pi2         = self.params['Tomo_do_init_pi2'],
                        phase_error         = self.params['final_phases'],
                        flip_RO             = self.params['flip_010'],
                        do_RO_electron         = self.params['RO_electron'],
                        el_state_in         = 0)#el_in_state_tomo010)

            Invert_parity_seq_yyx011= self.invert_readout_carbon_sequence(
                        prefix              = 'Invert_YYX011_' ,
                        pt                  = pt,
                        carbon_list         = self.params['Invert_yyx_carbon_list'],
                        RO_basis_list       = self.params['Invert_yxy_RO_list'],
                        readout_orientation = self.params['Parity_yyx_RO_orientation'],
                        do_final_pi2        = self.params['Invert_yyx_do_final_pi2'],
                        inv_el_state_in     = 0,
                        el_state_in         = el_in_state_tomo011)

            carbon_tomo_seq011 = self.readout_carbon_sequence(
                        prefix              = 'Tomo011_',
                        pt                  = pt,
                        go_to_element       = None,
                        event_jump_element  = None,
                        RO_trigger_duration = 10e-6,
                        carbon_list         = self.params['Tomo_carbon_list'],
                        RO_basis_list       = self.params['Tomo_RO_list'],
                        readout_orientation = self.params['Tomo_RO_orientation'],
                        do_init_pi2         = self.params['Tomo_do_init_pi2'],
                        phase_error         = self.params['final_phases'],
                        flip_RO             = self.params['flip_011'],
                        do_RO_electron         = self.params['RO_electron'],
                        el_state_in         = 0)#el_in_state_tomo011)

            Invert_parity_seq_yyx100= self.invert_readout_carbon_sequence(
                        prefix              = 'Invert_YYX100_' ,
                        pt                  = pt,
                        carbon_list         = self.params['Invert_yyx_carbon_list'],
                        RO_basis_list       = self.params['Invert_yxy_RO_list'],
                        readout_orientation = self.params['Parity_yyx_RO_orientation'],
                        do_final_pi2        = self.params['Invert_yyx_do_final_pi2'],
                        inv_el_state_in     = 0,
                        el_state_in         = el_in_state_tomo100)

            carbon_tomo_seq100 = self.readout_carbon_sequence(
                        prefix              = 'Tomo100_',
                        pt                  = pt,
                        go_to_element       = None,
                        event_jump_element  = None,
                        RO_trigger_duration = 10e-6,
                        carbon_list         = self.params['Tomo_carbon_list'],
                        RO_basis_list       = self.params['Tomo_RO_list'],
                        readout_orientation = self.params['Tomo_RO_orientation'],
                        do_init_pi2         = self.params['Tomo_do_init_pi2'],
                        phase_error         = self.params['final_phases'],
                        flip_RO             = self.params['flip_100'],
                        do_RO_electron         = self.params['RO_electron'],
                        el_state_in         = 0)#el_in_state_tomo100)

            Invert_parity_seq_yyx101= self.invert_readout_carbon_sequence(
                        prefix              = 'Invert_YYX101_' ,
                        pt                  = pt,
                        carbon_list         = self.params['Invert_yyx_carbon_list'],
                        RO_basis_list       = self.params['Invert_yxy_RO_list'],
                        readout_orientation = self.params['Parity_yyx_RO_orientation'],
                        do_final_pi2        = self.params['Invert_yyx_do_final_pi2'],
                        inv_el_state_in     = 0,  
                        el_state_in         = el_in_state_tomo101)

            carbon_tomo_seq101 = self.readout_carbon_sequence(
                        prefix              = 'Tomo101_',
                        pt                  = pt,
                        go_to_element       = None,
                        event_jump_element  = None,
                        RO_trigger_duration = 10e-6,
                        carbon_list         = self.params['Tomo_carbon_list'],
                        RO_basis_list       = self.params['Tomo_RO_list'],
                        readout_orientation = self.params['Tomo_RO_orientation'],
                        do_init_pi2         = self.params['Tomo_do_init_pi2'],
                        phase_error         = self.params['final_phases'],
                        flip_RO             = self.params['flip_101'],
                        do_RO_electron         = self.params['RO_electron'],
                        el_state_in         = 0)#el_in_state_tomo101)

            Invert_parity_seq_yyx110= self.invert_readout_carbon_sequence(
                        prefix              = 'Invert_YYX110_' ,
                        pt                  = pt,
                        carbon_list         = self.params['Invert_yyx_carbon_list'],
                        RO_basis_list       = self.params['Invert_yxy_RO_list'],
                        readout_orientation = self.params['Parity_yyx_RO_orientation'],
                        do_final_pi2        = self.params['Invert_yyx_do_final_pi2'],
                        inv_el_state_in     = 0,                        
                        el_state_in         = el_in_state_tomo110)

            carbon_tomo_seq110 = self.readout_carbon_sequence(
                        prefix              = 'Tomo110_',
                        pt                  = pt,
                        go_to_element       = None,
                        event_jump_element  = None,
                        RO_trigger_duration = 10e-6,
                        carbon_list         = self.params['Tomo_carbon_list'],
                        RO_basis_list       = self.params['Tomo_RO_list'],
                        readout_orientation = self.params['Tomo_RO_orientation'],
                        do_init_pi2         = self.params['Tomo_do_init_pi2'],
                        phase_error         = self.params['final_phases'],
                        flip_RO             = self.params['flip_110'],
                        do_RO_electron         = self.params['RO_electron'],
                        el_state_in         = 0)#el_in_state_tomo110)

            Invert_parity_seq_yyx111= self.invert_readout_carbon_sequence(
                        prefix              = 'Invert_YYX111_' ,
                        pt                  = pt,
                        carbon_list         = self.params['Invert_yyx_carbon_list'],
                        RO_basis_list       = self.params['Invert_yxy_RO_list'],
                        readout_orientation = self.params['Parity_yyx_RO_orientation'],
                        do_final_pi2        = self.params['Invert_yyx_do_final_pi2'],
                        inv_el_state_in     = 0,
                        el_state_in         = el_in_state_tomo111)

            carbon_tomo_seq111 = self.readout_carbon_sequence(
                        prefix              = 'Tomo111_',
                        pt                  = pt,
                        go_to_element       = None,
                        event_jump_element  = None,
                        RO_trigger_duration = 10e-6,
                        carbon_list         = self.params['Tomo_carbon_list'],
                        RO_basis_list       = self.params['Tomo_RO_list'],
                        readout_orientation = self.params['Tomo_RO_orientation'],
                        do_init_pi2         = self.params['Tomo_do_init_pi2'],
                        phase_error         = self.params['final_phases'],
                        flip_RO             = self.params['flip_111'],
                        do_RO_electron         = self.params['RO_electron'],
                        el_state_in         = 0)#el_in_state_tomo111)

            gate_seq000.extend(Invert_parity_seq_yyx000)
            gate_seq000.extend(carbon_tomo_seq000)
            gate_seq001.extend(Invert_parity_seq_yyx001)
            gate_seq001.extend(carbon_tomo_seq001)
            gate_seq010.extend(Invert_parity_seq_yyx010)
            gate_seq010.extend(carbon_tomo_seq010)
            gate_seq011.extend(Invert_parity_seq_yyx011)
            gate_seq011.extend(carbon_tomo_seq011)
            gate_seq100.extend(Invert_parity_seq_yyx100)
            gate_seq100.extend(carbon_tomo_seq100)
            gate_seq101.extend(Invert_parity_seq_yyx101)
            gate_seq101.extend(carbon_tomo_seq101)
            gate_seq110.extend(Invert_parity_seq_yyx110)
            gate_seq110.extend(carbon_tomo_seq110)
            gate_seq111.extend(Invert_parity_seq_yyx111)
            gate_seq111.extend(carbon_tomo_seq111)

            #####################################
            ### Jumps statements for feedback ###
            #####################################
            
            Parity_seq_xyy[-1].go_to       = Invert_parity_seq_xyy0[0].name
            Parity_seq_xyy[-1].event_jump  = Invert_parity_seq_xyy1[0].name
        

            Parity_seq_yxy0[-1].go_to        = Invert_parity_seq_yxy00[0].name
            Parity_seq_yxy0[-1].event_jump   = Invert_parity_seq_yxy01[0].name
        
            Parity_seq_yxy1[-1].go_to        = Invert_parity_seq_yxy10[0].name
            Parity_seq_yxy1[-1].event_jump   = Invert_parity_seq_yxy11[0].name
        

            Parity_seq_yyx00[-1].go_to       = Invert_parity_seq_yyx000[0].name
            Parity_seq_yyx00[-1].event_jump  = Invert_parity_seq_yyx001[0].name
        
            Parity_seq_yyx01[-1].go_to       = Invert_parity_seq_yyx010[0].name
            Parity_seq_yyx01[-1].event_jump  = Invert_parity_seq_yyx011[0].name
        
            Parity_seq_yyx10[-1].go_to       = Invert_parity_seq_yyx100[0].name
            Parity_seq_yyx10[-1].event_jump  = Invert_parity_seq_yyx101[0].name
        
            Parity_seq_yyx11[-1].go_to       = Invert_parity_seq_yyx110[0].name
            Parity_seq_yyx11[-1].event_jump  = Invert_parity_seq_yyx111[0].name

            # In the end all roads lead to Rome
            Rome = Gate('Rome_'+str(pt),'passive_elt',
                    wait_time = 3e-6)
            gate_seq111.append(Rome)

            gate_seq000[-1].go_to     = gate_seq111[-1].name
            gate_seq001[-1].go_to     = gate_seq111[-1].name    
            gate_seq010[-1].go_to     = gate_seq111[-1].name
            gate_seq011[-1].go_to     = gate_seq111[-1].name
            gate_seq100[-1].go_to     = gate_seq111[-1].name
            gate_seq101[-1].go_to     = gate_seq111[-1].name    
            gate_seq110[-1].go_to     = gate_seq111[-1].name

            ###########################################################
            ### Set the electron state outcomes for the RO triggers ###
            ###########################################################

            ### after first parity xyy msmnt
            gate_seq0[len(gate_seq)-1].el_state_before_gate     =  '0' 
            gate_seq1[len(gate_seq)-1].el_state_before_gate     =  '1' 

            ### after second parity yxy msmnt
            gate_seq00[len(gate_seq)-1].el_state_before_gate    =  '0' 
            gate_seq00[len(gate_seq0)-1].el_state_before_gate   =  '0' 

            gate_seq01[len(gate_seq)-1].el_state_before_gate    =  '0' 
            gate_seq01[len(gate_seq0)-1].el_state_before_gate   =  '1' 

            gate_seq10[len(gate_seq)-1].el_state_before_gate    =  '1' 
            gate_seq10[len(gate_seq1)-1].el_state_before_gate   =  '0' 
            
            gate_seq11[len(gate_seq)-1].el_state_before_gate    =  '1' 
            gate_seq11[len(gate_seq1)-1].el_state_before_gate   =  '1' 

            ### after third parity yyx msmnt
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

            print '*'*10
            print 'seq_merged'

            for i,g in enumerate(merged_sequence):
                pass

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

class GHZ_ThreeQB_Unbranched(DD.MBI_C13):
    '''
    #Sequence

    |N-MBI| -|Parity_XYY| -- |undo_phase| -- |invert_XYY| 
            -|Parity_YXY| -- |undo_phase| -- |invert_YXY|
            -|Parity_YYX| -- |undo_phase| -- |invert_YYX|
            -|Tomography|
                                                         
    For GHZ test: Tomography=Parity_XXX
    '''
    
    mprefix = 'GHZ'
    adwin_process = 'MBI_multiple_C13'

    def generate_sequence(self,upload=True,debug = False):
        pts = self.params['pts']

        ### initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('GHZ')

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

            ####################
            ### Optional: initialize C ###
            ####################

            init_wait_for_trigger = True
            if self.params['initialize_carbons'] == True:
                for kk in range(self.params['Nr_C13_init']):
                    carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                        prefix = 'C_MBI_step_' + str(kk+1) + '_C',
                        wait_for_trigger      = init_wait_for_trigger, pt =pt,
                        initialization_method = self.params['init_method_list'][kk],
                        C_init_state          = self.params['init_state_list'][kk],
                        addressed_carbon      = self.params['carbon_init_list'][kk])
                    gate_seq.extend(carbon_init_seq)
                    init_wait_for_trigger = False


            ########################################################    
            ### XYY, YXY, YYX Parity measurements ###
            ########################################################

            #######################
            ### Parity msmt XYY ###
            #######################


            RO_and_invert_Parity_seq_xyy = self.readout_and_invert_carbons_sequence(
                        prefix = 'Parity_xyy_',
                        RO_trigger_duration = self.params['RO_trigger_duration'],
                        carbon_list         = self.params['Parity_xyy_carbon_list'],
                        inv_carbon_list     = self.params['Invert_xyy_carbon_list'],
                        RO_basis_list       = self.params['Parity_xyy_RO_list'],
                        inv_RO_basis_list   = self.params['Invert_xyy_RO_list'],
                        readout_orientation = self.params['Parity_xyy_RO_orientation'],
                        wait_for_trigger    = init_wait_for_trigger,
                        do_init_pi2         = self.params['Parity_xyy_do_init_pi2'],
                        do_final_pi2        = self.params['Invert_xyy_do_final_pi2'],
                        composite_pi        = self.params['Use_composite_pi'])
            gate_seq.extend(RO_and_invert_Parity_seq_xyy)


            RO_and_invert_Parity_seq_yxy = self.readout_and_invert_carbons_sequence(
                        prefix = 'Parity_yxy_',
                        RO_trigger_duration = self.params['RO_trigger_duration'],
                        carbon_list         = self.params['Parity_yxy_carbon_list'],
                        inv_carbon_list     = self.params['Invert_yxy_carbon_list'],
                        RO_basis_list       = self.params['Parity_yxy_RO_list'],
                        inv_RO_basis_list   = self.params['Invert_yxy_RO_list'],
                        readout_orientation = self.params['Parity_yxy_RO_orientation'],
                        do_init_pi2         = self.params['Parity_yxy_do_init_pi2'],
                        do_final_pi2        = self.params['Invert_yxy_do_final_pi2'],
                        composite_pi        = self.params['Use_composite_pi'])

            gate_seq.extend(RO_and_invert_Parity_seq_yxy)

            RO_and_invert_Parity_seq_yyx = self.readout_and_invert_carbons_sequence(
                        prefix = 'Parity_yyx_',
                        RO_trigger_duration = self.params['RO_trigger_duration'],
                        carbon_list         = self.params['Parity_yyx_carbon_list'],
                        inv_carbon_list     = self.params['Invert_yyx_carbon_list'],
                        RO_basis_list       = self.params['Parity_yyx_RO_list'],
                        inv_RO_basis_list   = self.params['Invert_yyx_RO_list'],
                        readout_orientation = self.params['Parity_yyx_RO_orientation'],
                        wait_for_trigger    = init_wait_for_trigger,
                        do_init_pi2         = self.params['Parity_yyx_do_init_pi2'],
                        do_final_pi2        = self.params['Invert_yyx_do_final_pi2'],
                        composite_pi        = self.params['Use_composite_pi'])
            
            gate_seq.extend(RO_and_invert_Parity_seq_yyx)

            carbon_tomo_seq = self.readout_carbon_sequence(
                        prefix              = 'Tomo_',
                        pt                  = pt,
                        go_to_element       = None,
                        event_jump_element  = None,
                        RO_trigger_duration = self.params['Tomo_RO_trigger_duration'],
                        carbon_list         = self.params['Tomo_carbon_list'],
                        RO_basis_list       = self.params['Tomo_RO_list'],
                        readout_orientation = self.params['Tomo_RO_orientation'],
                        do_init_pi2         = self.params['Tomo_do_init_pi2'],
                        phase_error         = self.params['final_phases'],
                        flip_RO             = self.params['flip_000'],
                        do_RO_electron      = self.params['RO_electron'],
                        el_state_in         = 0)

            gate_seq.extend(carbon_tomo_seq)

            # In the end all roads lead to Rome
            Rome = Gate('Rome_'+str(pt),'passive_elt',
                    wait_time = 3e-6)
            gate_seq.append(Rome)

            ######################################
            ### Generate the AWG sequence ###
            ######################################

            gate_seq  = self.generate_AWG_elements(gate_seq,pt)

            ##############################################
            ### Merge the branches into 1 AWG sequence ###
            ##############################################

            merged_sequence = []
            merged_sequence.extend(gate_seq)                 

            print '*'*10
            print 'seq_merged'

            for i,g in enumerate(merged_sequence):
                pass

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

class GHZ_3mmts_Unbranched(DD.MBI_C13):
    '''
    #Sequence

    |N-MBI| -|Parity_A| -- |undo_phase| -- |invert_A| 
            -|Parity_B| -- |undo_phase| -- |invert_B|
            -|Tomography|
                                                         
    '''
    
    mprefix = 'GHZ'
    adwin_process = 'MBI_multiple_C13'

    def generate_sequence(self,upload=True,debug = False):
        pts = self.params['pts']

        ### initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('GHZ')

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

            ####################
            ### Optional: initialize C ###
            ####################

            init_wait_for_trigger = True
            if self.params['initialize_carbons'] == True:
                for kk in range(self.params['Nr_C13_init']):
                    carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                        prefix = 'C_MBI_step_' + str(kk+1) + '_C',
                        wait_for_trigger      = init_wait_for_trigger, pt =pt,
                        initialization_method = self.params['init_method_list'][kk],
                        C_init_state          = self.params['init_state_list'][kk],
                        addressed_carbon      = self.params['carbon_init_list'][kk])
                    gate_seq.extend(carbon_init_seq)
                    init_wait_for_trigger = False


            ########################################################    
            ### XYY, YXY, YYX Parity measurements ###
            ########################################################

            #######################
            ### Parity msmt XYY ###
            #######################


            RO_and_invert_Parity_seq_A = self.readout_and_invert_carbons_sequence(
                        prefix = 'Parity_A_',
                        RO_trigger_duration = self.params['RO_trigger_duration'],
                        carbon_list         = self.params['Parity_A_carbon_list'],
                        inv_carbon_list     = self.params['Invert_A_carbon_list'],
                        RO_basis_list       = self.params['Parity_A_RO_list'],
                        inv_RO_basis_list   = self.params['Invert_A_RO_list'],
                        readout_orientation = self.params['Parity_A_RO_orientation'],
                        wait_for_trigger    = init_wait_for_trigger,
                        do_init_pi2         = self.params['Parity_A_do_init_pi2'],
                        do_final_pi2        = self.params['Invert_A_do_final_pi2'],
                        composite_pi        = self.params['Use_composite_pi'])
            gate_seq.extend(RO_and_invert_Parity_seq_A)


            RO_and_invert_Parity_seq_B = self.readout_and_invert_carbons_sequence(
                        prefix = 'Parity_B_',
                        RO_trigger_duration = self.params['RO_trigger_duration'],
                        carbon_list         = self.params['Parity_B_carbon_list'],
                        inv_carbon_list     = self.params['Invert_B_carbon_list'],
                        RO_basis_list       = self.params['Parity_B_RO_list'],
                        inv_RO_basis_list   = self.params['Invert_B_RO_list'],
                        readout_orientation = self.params['Parity_B_RO_orientation'],
                        do_init_pi2         = self.params['Parity_B_do_init_pi2'],
                        do_final_pi2        = self.params['Invert_B_do_final_pi2'],
                        composite_pi        = self.params['Use_composite_pi'])

            gate_seq.extend(RO_and_invert_Parity_seq_B)


            carbon_tomo_seq = self.readout_carbon_sequence(
                        prefix              = 'Tomo_',
                        pt                  = pt,
                        go_to_element       = None,
                        event_jump_element  = None,
                        RO_trigger_duration = self.params['Tomo_RO_trigger_duration'],
                        carbon_list         = self.params['Tomo_carbon_list'],
                        RO_basis_list       = self.params['Tomo_RO_list'],
                        readout_orientation = self.params['Tomo_RO_orientation'],
                        do_init_pi2         = self.params['Tomo_do_init_pi2'],
                        phase_error         = self.params['final_phases'],
                        flip_RO             = self.params['flip_000'],
                        do_RO_electron      = self.params['RO_electron'],
                        el_state_in         = 0)

            gate_seq.extend(carbon_tomo_seq)

            # In the end all roads lead to Rome
            Rome = Gate('Rome_'+str(pt),'passive_elt',
                    wait_time = 3e-6)
            gate_seq.append(Rome)

            ######################################
            ### Generate the AWG sequence ###
            ######################################

            gate_seq  = self.generate_AWG_elements(gate_seq,pt)

            ##############################################
            ### Merge the branches into 1 AWG sequence ###
            ##############################################

            merged_sequence = []
            merged_sequence.extend(gate_seq)                 

            print '*'*10
            print 'seq_merged'

            for i,g in enumerate(merged_sequence):
                pass

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

class GHZ_Debug_ZZTomo(DD.MBI_C13):
    '''
    #Sequence

                        --|Invert IIX_9|-|Tomo_0|
    |N-MBI| - |Init|-|Parity_IIX|
                        --|Invert IIX_1|-|Tomo_1|
    '''
    
    mprefix = 'GHZ'
    adwin_process = 'MBI_multiple_C13'

    def generate_sequence(self,upload=True,debug = False):
        pts = self.params['pts']

        ### initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('GHZ')

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


            ####################
            ### Initialize C ###
            ####################

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

            ########################################################    
            ### Measurements ###
            ########################################################

            ######################
            ### Parity msmt ###
            ######################

            Parity_seq_A = self.readout_carbon_sequence(
                        prefix              = 'Parity_A_' ,
                        pt                  = pt,
                        RO_trigger_duration = 150e-6,#?? Is this a good value?
                        carbon_list         = self.params['Parity_A_carbon_list'],
                        RO_basis_list       = self.params['Parity_A_RO_list'],
                        readout_orientation = self.params['Parity_A_RO_orientation'],
                        el_RO_result        = '0',
                        el_state_in         = 0)

            gate_seq.extend(Parity_seq_A)

            gate_seq0 = copy.deepcopy(gate_seq)
            gate_seq1 = copy.deepcopy(gate_seq)

            ######################
            ### Tomo msmt ###
            ######################

            el_in_state_yxy0 = 0
            el_in_state_yxy1 = 1

            if self.params['do_invert_RO'] == True:

                Invert_parity_seq_A0 = self.invert_readout_carbon_sequence(
                            prefix              = 'Invert_A0_',
                            pt                  = pt,
                            carbon_list         = self.params['Parity_A_carbon_list'],
                            RO_basis_list       = self.params['Parity_A_RO_list'],
                            readout_orientation = self.params['Parity_A_RO_orientation'],
                            do_final_pi2        = self.params['Invert_A_do_final_pi2'],
                            inv_el_state_in     = 0,
                            el_state_in         = el_in_state_yxy0)

                Tomo_seq_B0 = self.readout_carbon_sequence(
                            prefix              = 'Tomo_B0_' ,
                            pt                  = pt,
                            RO_trigger_duration = 150e-6,
                            carbon_list         = self.params['Tomo_carbon_list'],
                            RO_basis_list       = self.params['Tomo_RO_list'],
                            readout_orientation = self.params['Tomo_RO_orientation'],
                            do_init_pi2         = self.params['Tomo_do_init_pi2'],
                            el_RO_result         = '0',
                            el_state_in         = 0)                        

                Invert_parity_seq_A1 = self.invert_readout_carbon_sequence(
                            prefix              = 'Invert_A1_' ,
                            pt                  = pt,
                            carbon_list         = self.params['Parity_A_carbon_list'],
                            RO_basis_list       = self.params['Parity_A_RO_list'],
                            readout_orientation = self.params['Parity_A_RO_orientation'],
                            do_final_pi2        = self.params['Invert_A_do_final_pi2'],
                            inv_el_state_in     = 0,
                            el_state_in         = el_in_state_yxy1)

                Tomo_seq_B1 = self.readout_carbon_sequence(
                            prefix              = 'Tomo_B1_' ,
                            pt                  = pt,
                            RO_trigger_duration = 150e-6,
                            carbon_list         = self.params['Tomo_carbon_list'],
                            RO_basis_list       = self.params['Tomo_RO_list'],
                            readout_orientation = self.params['Tomo_RO_orientation'],
                            do_init_pi2         = self.params['Tomo_do_init_pi2'],
                            el_RO_result        = '0',
                            el_state_in         = 0)

                gate_seq0.extend(Invert_parity_seq_A0)
                gate_seq1.extend(Invert_parity_seq_A1)
                gate_seq0.extend(Tomo_seq_B0)
                gate_seq1.extend(Tomo_seq_B1)


            elif self.params['do_tomo'] == True:

                Tomo_seq_B0 = self.readout_carbon_sequence(
                            prefix              = 'Tomo_B0_' ,
                            pt                  = pt,
                            RO_trigger_duration = 10e-6,
                            go_to_element       = None,
                            event_jump_element  = None,
                            carbon_list         = self.params['Tomo_carbon_list'],
                            RO_basis_list       = self.params['Tomo_RO_list'],
                            readout_orientation = self.params['Tomo_RO_orientation'],
                            do_init_pi2         = self.params['Tomo_do_init_pi2'],
                            el_RO_result        = '0',
                            el_state_in         = el_in_state_yxy0)                        

                Tomo_seq_B1 = self.readout_carbon_sequence(
                            prefix              = 'Tomo_B1_' ,
                            pt                  = pt,
                            RO_trigger_duration = 10e-6,
                            go_to_element       = None,
                            event_jump_element  = None,
                            carbon_list         = self.params['Tomo_carbon_list'],
                            RO_basis_list       = self.params['Tomo_RO_list'],
                            readout_orientation = self.params['Tomo_RO_orientation'],
                            do_init_pi2         = self.params['Tomo_do_init_pi2'],
                            el_RO_result        = '0',
                            el_state_in         = el_in_state_yxy1) 

                gate_seq0.extend(Tomo_seq_B0)
                gate_seq1.extend(Tomo_seq_B1)

            elif self.params['do_e_RO'] == True:
                gate_seq0.append(Gate('eRO_0_Trigger_'+str(pt),'Trigger',
                wait_time = 116e-6,
                go_to = 'next', event_jump = 'next',
                el_state_before_gate = '0'))

                gate_seq1.append(Gate('eRO_1_Trigger_'+str(pt),'Trigger',
                wait_time = 116e-6,
                go_to = 'next', event_jump = 'next',
                el_state_before_gate = '0'))

            #####################################
            ### Jumps statements for feedback ###
            #####################################
            
            if self.params['do_invert_RO'] == True:
                Parity_seq_A[-1].go_to       = Invert_parity_seq_A0[0].name
                Parity_seq_A[-1].event_jump  = Invert_parity_seq_A1[0].name

            elif self.params['do_tomo'] == True:
                Parity_seq_A[-1].go_to       = Tomo_seq_B0[0].name
                Parity_seq_A[-1].event_jump  = Tomo_seq_B1[0].name

            elif self.params['do_e_RO'] == True:
                Parity_seq_A[-1].go_to       = gate_seq0[-1].name
                Parity_seq_A[-1].event_jump  = gate_seq1[-1].name
             
            # In the end all roads lead to Rome
            Rome = Gate('Rome_'+str(pt),'passive_elt',
                    wait_time = 3e-6)
            gate_seq1.append(Rome)

            gate_seq0[-1].go_to     = gate_seq1[-1].name
       
            ###########################################################
            ### Set the electron state outcomes for the RO triggers ###
            ###########################################################

            ### after first parity xyy msmnt
            gate_seq0[len(gate_seq)-1].el_state_before_gate     =  '0' 
            gate_seq1[len(gate_seq)-1].el_state_before_gate     =  '1' 

        
            ######################################
            ### Generate all the AWG sequences ###
            ######################################

            gate_seq  = self.generate_AWG_elements(gate_seq,pt)

            gate_seq0  = self.generate_AWG_elements(gate_seq0,pt)
            gate_seq1  = self.generate_AWG_elements(gate_seq1,pt)

            ##############################################
            ### Merge the branches into 1 AWG sequence ###
            ##############################################

            merged_sequence = []
            merged_sequence.extend(gate_seq)                 

            merged_sequence.extend(gate_seq0[len(gate_seq):])
            merged_sequence.extend(gate_seq1[len(gate_seq):])

            print '*'*10
            print 'seq_merged'

            for i,g in enumerate(merged_sequence):
                pass
  
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

class test_undo_RO_phase_and_invert(DD.MBI_C13):

    mprefix = 'test_undo_RO_phase'
    adwin_process = 'MBI_multiple_C13'

    def generate_sequence(self,upload=True,debug = False):
        pts = self.params['pts']

        ### initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('test_undoROphase')

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


            ####################
            ### Initialize C ###
            ####################

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

            ########################################################    
            ### Measurements ###
            ########################################################

            ######################
            ### Parity msmt and inversion###
            ######################

            RO_and_invert_Parity_seq_A = self.readout_and_invert_carbons_sequence(
                        prefix = 'Parity_A',
                        RO_trigger_duration = self.params['RO_trigger_duration'],
                        carbon_list         = self.params['Parity_A_carbon_list'],
                        RO_basis_list       = self.params['Parity_A_RO_list'],
                        readout_orientation = self.params['Parity_A_RO_orientation'],
                        wait_for_trigger    = init_wait_for_trigger,
                        do_init_pi2         = self.params['Parity_A_do_init_pi2'],
                        do_final_pi2        = self.params['Invert_A_do_final_pi2'],
                        composite_pi        = self.params['use_composite_pi'])
            gate_seq.extend(RO_and_invert_Parity_seq_A)


            ######################
            ### Tomography ####
            ######################
            Tomo_seq_B = self.readout_carbon_sequence(
                        prefix              = 'Tomo_B_' ,
                        pt                  = pt,
                        RO_trigger_duration = 10e-6,
                        go_to_element       = None,
                        event_jump_element  = None,
                        carbon_list         = self.params['Tomo_carbon_list'],
                        RO_basis_list       = self.params['Tomo_RO_list'],
                        readout_orientation = self.params['Tomo_RO_orientation'],
                        do_init_pi2         = self.params['Tomo_do_init_pi2'],
                        el_RO_result         = '0',
                        el_state_in         = 0)    

            gate_seq.extend(Tomo_seq_B)

            #####################################
            ### Jumps statements for feedback ###
            #####################################
            ### doing this because the adwin will give the triggers. But both lead to the same sequence.

            # Parity_seq_A[-1].go_to       = undo_RO_phases_seq_A[0].name
            # Parity_seq_A[-1].event_jump  = undo_RO_phases_seq_A[0].name

            # In the end the road leads to Rome
            Rome = Gate('Rome_'+str(pt),'passive_elt',
                    wait_time = 3e-6)
            gate_seq.append(Rome)
        
            ######################################
            ### Generate the AWG sequence ###
            ######################################

            gate_seq  = self.generate_AWG_elements(gate_seq,pt)

            ##############################################
            ### Merge the branches into 1 AWG sequence ###
            ##############################################

            merged_sequence = []
            merged_sequence.extend(gate_seq)                 

            print '*'*10
            print 'seq_merged'

            for i,g in enumerate(merged_sequence):
                pass
  
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


class test_undo_RO_phase(DD.MBI_C13):

    mprefix = 'test_undo_RO_phase'
    adwin_process = 'MBI_multiple_C13'

    def generate_sequence(self,upload=True,debug = False):
        pts = self.params['pts']

        ### initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('test_undoROphase')

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


            ####################
            ### Initialize C ###
            ####################

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

            ########################################################    
            ### Measurements ###
            ########################################################

            ######################
            ### Parity msmt ###
            ######################

            Parity_seq_A = self.readout_carbon_sequence(
                        prefix              = 'Parity_A_' ,
                        pt                  = pt,
                        RO_trigger_duration = self.params['RO_trigger_duration'],#?? Is this a good value?
                        carbon_list         = self.params['Parity_A_carbon_list'],
                        RO_basis_list       = self.params['Parity_A_RO_list'],
                        readout_orientation = self.params['Parity_A_RO_orientation'],
                        wait_for_trigger    = init_wait_for_trigger,
                        el_RO_result        = '0',
                        el_state_in         = 0)

            gate_seq.extend(Parity_seq_A)

            gate_seq0 = copy.deepcopy(gate_seq)
            gate_seq1 = copy.deepcopy(gate_seq)   
            ######################
            ### undo RO phases ###
            ######################

            undo_RO_phases_seq_A0 = self.undo_ROphases(
                        prefix              = 'undo_phases_parity_A0_',
                        pt                  = pt,
                        RO_trigger_duration = self.params['RO_trigger_duration'],
                        conditional_pi      = self.params['undo_parityA_conditional_pi'],
                        conditional_pi2     = self.params['undo_parityA_conditional_pi2'],
                        pi2_phase           = self.params['Y_phase'],
                        el_state_in         = 0)

            undo_RO_phases_seq_A1 = self.undo_ROphases(
                        prefix              = 'undo_phases_parity_A1_',
                        pt                  = pt,
                        RO_trigger_duration = self.params['RO_trigger_duration'],
                        conditional_pi      = self.params['undo_parityA_conditional_pi'],
                        conditional_pi2     = self.params['undo_parityA_conditional_pi2'],
                        pi2_phase           = self.params['Y_phase'],
                        el_state_in         = 1)
            
            gate_seq0.extend(undo_RO_phases_seq_A0)
            gate_seq1.extend(undo_RO_phases_seq_A1)

            ##########################
            ### Tomo parity msmt ###
            ##########################

            Tomo_seq_B = self.readout_carbon_sequence(
                        prefix              = 'Tomo_B_' ,
                        pt                  = pt,
                        RO_trigger_duration = 10e-6,
                        go_to_element       = None,
                        event_jump_element  = None,                        
                        carbon_list         = self.params['Tomo_carbon_list'],
                        RO_basis_list       = self.params['Tomo_RO_list'],
                        readout_orientation = self.params['Tomo_RO_orientation'],
                        do_init_pi2         = self.params['Tomo_do_init_pi2'],
                        el_RO_result         = '0',
                        el_state_in         = 0)    

            # also attach the Tomo_seq to gate_seq1, to get the phase correction for the Ren gate included.
            gate_seq0.extend(Tomo_seq_B)
            gate_seq1.extend(Tomo_seq_B) 

            #####################################
            ### Jumps statements for feedback ###
            #####################################
            ### doing this because the adwin will give the triggers. But both lead to the same sequence.

            Parity_seq_A[-1].go_to      = undo_RO_phases_seq_A0[0].name
            Parity_seq_A[-1].event_jump = undo_RO_phases_seq_A1[0].name

            #everything goes to Tomo_seq_B after the small-branching
            undo_RO_phases_seq_A0[-1].go_to = Tomo_seq_B[0].name
            undo_RO_phases_seq_A1[-1].go_to = Tomo_seq_B[0].name

            # In the end the road leads to Rome. It has to be the last element, so append it to gate_seq1
            Rome = Gate('Rome_'+str(pt),'passive_elt',
                    wait_time = 3e-6)
            gate_seq1.append(Rome)

            gate_seq0[-1].go_to         = gate_seq1[-1].name
            #gate_seq0[-1].event_jump    = gate_seq1[-1].name
        
            ######################################
            ### Generate the AWG sequence ###
            ######################################
            gate_seq  = self.generate_AWG_elements(gate_seq,pt)

            gate_seq0  = self.generate_AWG_elements(gate_seq0,pt)
            gate_seq1  = self.generate_AWG_elements(gate_seq1,pt)

            ##############################################
            ### Merge the branches into 1 AWG sequence ###
            ##############################################

            merged_sequence = []
            #gate_seq0 is my leading sequence, but for the go_to of the parityA to work, I must also add gate_seq.
            merged_sequence.extend(gate_seq)
            merged_sequence.extend(gate_seq0[len(gate_seq):])                

            #only add the undo_RO_phases part of sequence1
            merged_sequence.extend(gate_seq1[len(gate_seq):len(gate_seq)+len(undo_RO_phases_seq_A1)])

            merged_sequence.append(gate_seq1[-1])

            print '*'*10
            print 'seq_merged'

            for i,g in enumerate(merged_sequence):
                pass
  
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



