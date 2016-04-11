"""
Contains all Quantum Memory measurement classes.
Derived from DD_2.py
"""

import numpy as np

import qt
import copy
from measurement.lib.pulsar import pulse, pulselib, element, pulsar
reload(pulsar)

import measurement.lib.measurement2.adwin_ssro.DD_2 as DD; reload(DD)
from measurement.lib.measurement2.adwin_ssro.DD_2 import Gate


class QMemory_repumping(DD.MBI_C13):
    """
    Takes a carbon and initializes it with MBI.
    We then run the following sequence N times on the electronic spin:
    pi/2__t__pi__t-trep__repump
    afterwards the blochvector should be measured in the XY plane.
    Comes with the possibility to sweep the following parameters:
    t
    trep
    Repump_duration
    N

    TODO:
    An alternative mode to determine the AOM <--> MW delays.
    """

    mprefix = 'Memory'
    adwin_process = 'MBI_multiple_C13'

    def generate_sequence(self,upload=True,debug = False):
        if qt.instruments['NewfocusAOM'].get_sec_V_max() < qt.instruments['NewfocusAOM'].power_to_voltage(self.params['fast_repump_power'],controller='sec'):
            raise ValueError('REPUMP VOLTAGE TO HIGH!!')
        else: 
            qt.pulsar.set_channel_opt('AOM_Newfocus','high', qt.instruments['NewfocusAOM'].power_to_voltage(self.params['fast_repump_power'],controller='sec'))

        pts = self.params['pts']

        ### initialize empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Qmem Dephasing')

        for pt in range(pts): ### Sweep over RO basis
            gate_seq = []

            # gate_seq.append(Gate('Wait_gate_'+str(pt),'passive_elt',
            #             wait_time = 0.2,wait_for_trigger = True))
            
            ### Nitrogen MBI
            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]; gate_seq.extend(mbi_seq)

            #
            # gate_seq.append(Gate('Wait_gate_'+str(pt),'passive_elt',
            #                             wait_time = 0.2,wait_for_trigger = True))
            # short_wait = Gate('Wait_short_'+str(pt),'passive_elt',
            #                             wait_time = 5e-6,wait_for_trigger = False)
            # gate_seq.append(short_wait)
            # gate_seq.extend(self.readout_carbon_sequence(
            #         prefix              = 'Electron_reinit',
            #         pt                  = pt,
            #         go_to_element       = None,
            #         event_jump_element  = None,
            #         RO_trigger_duration = 5e-6,
            #         carbon_list         = [],#self.params['carbon_list'],
            #         do_RO_electron      = True,
            #         do_init_pi2         = False,
            #         RO_basis_list       = [],
            #         el_state_in         = 0,
            #         readout_orientation = self.params['electron_readout_orientation'],
            #         Zeno_RO             = True))
            ### Carbon initialization
            init_wait_for_trigger = True


            
            for kk in range(self.params['Nr_C13_init']):

                carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                    prefix = 'C_MBI' + str(kk+1) + '_C',
                    wait_for_trigger      = init_wait_for_trigger, pt =pt,
                    initialization_method = self.params['init_method_list'][kk],
                    C_init_state          = self.params['init_state_list'][kk],
                    addressed_carbon      = self.params['carbon_init_list'][kk],
                    el_after_init         = self.params['el_after_init'])
                gate_seq.extend(carbon_init_seq)
                init_wait_for_trigger = False

            
            ############################
            ###  DFS initialization  ###
            ############################

            for kk in range(self.params['Nr_MBE']):
                
                probabilistic_MBE_seq =     self.logic_init_seq(
                        prefix              = '2C_init_' + str(kk+1),
                        pt                  =  pt,
                        carbon_list         = self.params['carbon_list'],
                        RO_basis_list       = self.params['MBE_bases'],
                        RO_trigger_duration = self.params['2C_RO_trigger_duration'],#150e-6,
                        el_RO_result        = '0',
                        logic_state         = self.params['2qb_logical_state'] ,
                        go_to_element       = mbi,
                        event_jump_element   = 'next',
                        readout_orientation = 'positive')

                gate_seq.extend(probabilistic_MBE_seq)

            if len(self.params['carbon_list']) == 3:
                for c in self.params['carbon_list']:
                    C_gate = Gate('C' + str(c) + '_Uncond_Ren' + str(pt), 'Carbon_Gate',
                                    Carbon_ind = c,
                                    phase = self.params['C13_Y_phase'])
                    gate_seq.append(C_gate)

            ############################
            ### Repetitive repumping ###
            ############################
            if self.params['fast_repump_repetitions'][pt] != 0:
                gate_seq.extend(self.generate_repumper(pt))



            ############################
            ###     Tomography       ###
            ############################  
            carbon_tomo_seq = self.readout_carbon_sequence(
                    prefix              = 'Tomo',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomo_bases'],
                    el_state_in         = 0,
                    readout_orientation = self.params['electron_readout_orientation'])
            
            # gate_seq.append(
            #     Gate('ro'+'_Trigger_'+str(pt),'Trigger',
            #     wait_time = 10e-6,
            #     go_to = None, event_jump = None,
            #     el_state_before_gate = '0'))
            gate_seq.extend(carbon_tomo_seq)

            gate_seq = self.generate_AWG_elements(gate_seq,pt)

            ### Convert elements to AWG sequence and add to combined list`
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq, explicit=True)
            combined_list_of_elements.extend(list_of_elements)

            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)


        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'


    def generate_repumper(self,pt):
        """ generate a primitive LDE element."""

        #extract parameters
        t = self.params['repump_wait'][pt]
        t_rep = self.params['average_repump_time'][pt]
        repump_duration = self.params['fast_repump_duration'][pt]
        N = self.params['fast_repump_repetitions'][pt]


        Laser=Gate('repump'+str(pt),'LDE',
            duration = repump_duration+2*t-t_rep
            )

        Laser.pi_amp = self.params['pi_amps'][pt]
        Laser.t = t
        # print "t_rep in sequencer {:.2}".format(t_rep)
        Laser.t_rep = t_rep
        Laser.reps = N
        Laser.repump_duration = repump_duration
        Laser.do_pi = self.params['do_pi']
        Laser.do_BB1 = self.params['do_BB1']

        Laser.channel='AOM_Newfocus'
        Laser.elements_duration= repump_duration+2*t-t_rep
        Laser.el_state_after_gate='0'

        return [Laser]
