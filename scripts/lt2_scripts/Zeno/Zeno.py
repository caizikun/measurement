"""
Contains all Zeno measurement classes.
Derived from DD_2.py
"""

import numpy as np

import qt
import copy
from measurement.lib.pulsar import pulse, pulselib, element, pulsar
reload(pulsar)

import measurement.lib.measurement2.adwin_ssro.DD_2 as DD; reload(DD)
from measurement.lib.measurement2.adwin_ssro.DD_2 import Gate





class Zeno_TwoQB(DD.MBI_C13):
    '''
    Sequence: Sequence: |N-MBI| -|Cinit|^2-|MBE|^N-(|Wait|-|Parity-measurement|-|Wait|)^M-|Tomography|
    '''
    mprefix='Zeno_TwoQubit'

    adwin_process='MBI_multiple_C13'

    ##### TODO: Add AOM control from the AWG for arbitrary AOM channels.
    # def autoconfikg(self):

    #     dephasing_AOM_voltage=qt.instruments[self.params['dephasing_AOM']].power_to_voltage(self.params['laser_dephasing_amplitude'],controller='sec')
    #     if dephasing_AOM_voltage > (qt.instruments[self.params['dephasing_AOM']]).get_sec_V_max():
    #         print 'Suggested power level would exceed V_max of the AOM driver.'
    #     else:
    #         #not sure if the secondary channel of an AOM can be obtained in this way?
    #         channelDict={'ch2m1': 'ch2_marker1'}
    #         print 'AOM voltage', dephasing_AOM_voltage
    #         self.params['Channel_alias']=qt.pulsar.get_channel_name_by_id(channelDict[qt.instruments[self.params['dephasing_AOM']].get_sec_channel()])
    #         qt.pulsar.set_channel_opt(self.params['Channel_alias'],'high',dephasing_AOM_voltage)

    #     MBI_C13.autoconfig()

    def generate_sequence(self,upload=True,debug=False):

        pts = self.params['pts']

        #self.configure_AOM
        # set the output power of the repumping AOM to the desired
        qt.pulsar.set_channel_opt('AOM_Newfocus','high', qt.instruments['NewfocusAOM'].power_to_voltage(self.params['Zeno_SP_A_power'],controller='sec'))

        ### initialize empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Zeno_TwoQubit')

        for pt in range(pts): ### Sweep evolution times
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
                    addressed_carbon      = self.params['carbon_init_list'][kk],
                    el_after_init           = '0')
                gate_seq.extend(carbon_init_seq)
                init_wait_for_trigger = False

            ### Initialize logical qubit via parity measurement.

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

            ### add pi pulse after final init.

            gate_seq.extend([Gate('2C_init_elec_X_pt'+str(pt),'electron_Gate',
                                    Gate_operation='pi',
                                    phase = self.params['X_phase'],
                                    el_state_after_gate = '1')])


            ### waiting time without Zeno msmmts.
            if self.params['Nr_Zeno_parity_msmts']==0:

                self.params['parity_duration']=0 ### this parameter is later used for data analysis.

                if self.params['free_evolution_time'][pt]!=0:
                    if self.params['free_evolution_time'][pt]< (self.params['2C_RO_trigger_duration']+3e-6): # because min length is 3e-6
                        print ('Error: carbon evolution time (%s) is shorter than Initialisation RO duration (%s)'
                                %(self.params['free_evolution_time'][pt],self.params['2C_RO_trigger_duration']))
                        qt.msleep(5)
                            ### Add waiting time
                    wait_gate = Gate('Wait_gate_'+str(pt),'passive_elt',
                                 wait_time = self.params['free_evolution_time'][pt]-self.params['2C_RO_trigger_duration'])
                    wait_seq = [wait_gate]; gate_seq.extend(wait_seq)

            ### If no waiting time:
            ### You have to implement an additional waiting time after the pi-pulse on the electron. Otherwise trouble with two consecutive MW pulses.
                else:
                    gate_seq.extend([Gate('2C_init_wait_gate_'+str(pt),'passive_elt',
                                     wait_time = 10e-6)])

            ### One or more parity measurements
            ### interleave waiting time with parity measurements.
            else:


                #Coarsely calculate the length of the carbon gates/ parity measurements.
                t_C13_gate1=2*self.params['C'+str(self.params['carbon_list'][0])+'_Ren_N'+self.params['electron_transition']][0]*(self.params['C'+str(self.params['carbon_list'][0])+'_Ren_tau'+self.params['electron_transition']][0])
                t_C13_gate2=2*self.params['C'+str(self.params['carbon_list'][1])+'_Ren_N'+self.params['electron_transition']][0]*(self.params['C'+str(self.params['carbon_list'][1])+'_Ren_tau'+self.params['electron_transition']][0])

                self.params['parity_duration']=(2*t_C13_gate1+2*t_C13_gate2+self.params['Repump_duration'])*self.params['Nr_Zeno_parity_msmts']

                print 'estimated parity duration in seconds:', self.params['parity_duration']

                if self.params['free_evolution_time'][pt]!=0:

                    if self.params['free_evolution_time'][pt]< (self.params['parity_duration'] + self.params['2C_RO_trigger_duration']+3e-6): # because min length is 3e-6
                        print ('Error: carbon evolution time (%s) is shorter than the sum of Initialisation RO duration (%s) and the duration of the parity measurements'
                                %(self.params['free_evolution_time'][pt],(self.params['parity_duration'] + self.params['2C_RO_trigger_duration']+3e-6)))
                        qt.msleep(5)

                    for i in range(self.params['Nr_Zeno_parity_msmts']):
                        
                        Parity_measurement=self.generate_parity_msmt(pt,msmt=i)
                        No_of_msmt=self.params['Nr_Zeno_parity_msmts']

                        if self.params['echo_like']:
                            ### Calculate the wait duration inbetween the parity measurements.
                            waitduration=(self.params['free_evolution_time'][pt]-self.params['parity_duration'])/(2.*No_of_msmt)
                        
                        else:
                            ### this 'lengthy' formula is used to equally space the repumping intervals in time.
                            waitduration=(self.params['free_evolution_time'][pt]-self.params['parity_duration'])/(No_of_msmt+1)+(No_of_msmt-1)*(t_C13_gate1+t_C13_gate2)/(No_of_msmt+1)

                        if i==0:
                            wait_gateA = Gate('Wait_gate_A'+str(i)+'_'+str(pt),'passive_elt',
                                        wait_time = round(waitduration-self.params['2C_RO_trigger_duration'],6)) #subtract the length of the RO-trigger for the first waiting time.
                            # print round(waitduration-self.params['2C_RO_trigger_duration'],6)
                        elif i==self.params['Nr_Zeno_parity_msmts']-1:
                            wait_gateA = Gate('Wait_gate_A'+str(i)+'_'+str(pt),'passive_elt',
                                        wait_time = round(waitduration,6))
                            # print round(waitduration,6)
                        else:
                            wait_gateA = Gate('Wait_gate_A'+str(i)+'_'+str(pt),'passive_elt',
                                        wait_time = round(waitduration,6))
                            # print round(waitduration,6)
                        #make the sequence symmetric around the parity measurements.
                        Decoupling_wait_gate = Gate('Wait_gate_B'+str(i)+'_'+str(pt),'passive_elt',
                                     wait_time = round(2*waitduration,6))

                        #for equally spaced measurements. see the entry in onenote of 30-01-2015 NK
                        equal_wait_gate = Gate('Wait_gate_B'+str(i)+'_'+str(pt),'passive_elt',
                                     wait_time = round(waitduration-(No_of_msmt-1)*(t_C13_gate1+t_C13_gate2)/(No_of_msmt+1)-2*(t_C13_gate1+t_C13_gate2)/(No_of_msmt+1),6))
                        # print round(waitduration-(No_of_msmt-1)*(t_C13_gate1+t_C13_gate2)/(No_of_msmt+1)-2*(t_C13_gate1+t_C13_gate2)/(No_of_msmt+1),6)
                        final_wait=Gate('Wait_gate_B'+str(i)+'_'+str(pt),'passive_elt',
                                     wait_time = round(waitduration,6))
                        # print round(waitduration,6)


                        if self.params['echo_like']: #this specifies the intertime delay of the Zeno measurements
                            ###
                            # echo like corresponds to the sequence: 
                            """init---(-wait-for-t---Msmt---wait-for-t)^n --- tomography """

                            ###
                            #Add waiting time
                            ### the case of only one measurement
                            if i==0 and 1==(self.params['Nr_Zeno_parity_msmts']):
                                wait_seq = [wait_gateA]
                                gate_seq.extend(wait_seq)
                                gate_seq.extend(Parity_measurement)
                                wait_seq = [final_wait]
                                gate_seq.extend(wait_seq)

                            ### the first element of a sequence with more than one measurement
                            elif i==0:
                                wait_seq = [wait_gateA]
                                gate_seq.extend(wait_seq)
                                gate_seq.extend(Parity_measurement)
                                wait_seq = [Decoupling_wait_gate]
                                gate_seq.extend(wait_seq)

                            ### not the first but also not the last element
                            elif i!=0 and i!=(self.params['Nr_Zeno_parity_msmts']-1):      
                                gate_seq.extend(Parity_measurement)
                                wait_seq = [Decoupling_wait_gate]
                                gate_seq.extend(wait_seq)

                            ### more than one measurement and the last element was reached.
                            else:
                                gate_seq.extend(Parity_measurement)
                                wait_seq = [final_wait]
                                gate_seq.extend(wait_seq)
                        
                        else:
                            # if not echo like then the measurement sequence should be equally spaced with respect to init and tomo
                            """ init --- wait for t --- (measurement --- wait for t)^n --- tomography"""
                            
                            #Add waiting time
                            ### the case of only one measurement
                            if i==0 and 1==(self.params['Nr_Zeno_parity_msmts']):
                                wait_seq = [wait_gateA]
                                gate_seq.extend(wait_seq)
                                gate_seq.extend(Parity_measurement)
                                wait_seq = [final_wait]
                                gate_seq.extend(wait_seq)

                            ### the first element of a sequence with more than one measurement
                            elif i==0:
                                wait_seq = [wait_gateA]
                                gate_seq.extend(wait_seq)
                                gate_seq.extend(Parity_measurement)
                                wait_seq = [equal_wait_gate]
                                gate_seq.extend(wait_seq)

                            ### not the first but also not the last element
                            elif i!=0 and i!=(self.params['Nr_Zeno_parity_msmts']-1):      
                                gate_seq.extend(Parity_measurement)
                                wait_seq = [equal_wait_gate]
                                gate_seq.extend(wait_seq)

                            ### more than one measurement and the last element was reached.
                            else:
                                gate_seq.extend(Parity_measurement)
                                wait_seq = [final_wait]
                                gate_seq.extend(wait_seq)
                                
                ### No waiting time, do the parity measurements directly. You have to implement an additional waiting time after the e-pulse in the beginning.
                ### as well as an additional wait time after the the last parity measurement because parity measurements also end with an e- pulse.
                else:
                    gate_seq.extend([Gate('2C_init_wait_gate_'+str(pt),'passive_elt',
                                     wait_time =10e-6)])
                    for kk in range(self.params['Nr_Zeno_parity_msmts']):
                        gate_seq.extend(self.generate_parity_msmt(pt, msmt=kk))
                    gate_seq.extend([Gate('Last_pi_wait_'+str(pt),'passive_elt',
                                     wait_time =10e-6)])
            ### Readout

            carbon_tomo_seq = self.readout_carbon_sequence(
                    prefix              = 'Tomo',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    el_state_in         = 1,
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
                #for g in gate_seq:
                #    print g.name

            if debug:
                for g in gate_seq:
                    print g.name

                    if ((g.C_phases_before_gate[self.params['carbon_list'][0]] == None) and (g.C_phases_before_gate[self.params['carbon_list'][1]] == None)):
                        print "[ None , None ]"
                    elif g.C_phases_before_gate[self.params['carbon_list'][0]] == None:
                        print "[ None , %.3f ]" %(g.C_phases_before_gate[self.params['carbon_list'][1]]/np.pi*180)
                    elif g.C_phases_before_gate[self.params['carbon_list'][1]] == None:
                        print "b[ %.3f, None ]" %(g.C_phases_before_gate[self.params['carbon_list'][0]]/np.pi*180)
                    else:
                        print "b[%.3f ,1 %.3f ]" %(g.C_phases_before_gate[self.params['carbon_list'][0]]/np.pi*180, g.C_phases_before_gate[self.params['carbon_list'][1]]/np.pi*180)


                    if ((g.C_phases_after_gate[self.params['carbon_list'][0]] == None) and (g.C_phases_after_gate[self.params['carbon_list'][1]] == None)):
                        print "[ None , None ]"
                    elif g.C_phases_after_gate[self.params['carbon_list'][0]] == None:
                        print "[ None , %.3f ]" %(g.C_phases_after_gate[self.params['carbon_list'][1]]/np.pi*180)
                    elif g.C_phases_after_gate[self.params['carbon_list'][1]] == None:
                        print "a[ %.3f, None ]" %(g.C_phases_after_gate[self.params['carbon_list'][0]]/np.pi*180)
                    else:
                        print "a[ %.3f , %.3f ]" %(g.C_phases_after_gate[self.params['carbon_list'][0]]/np.pi*180, g.C_phases_after_gate[self.params['carbon_list'][1]]/np.pi*180)

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'

    def generate_parity_msmt(self,pt,msmt=0):

        sequence=[]

        # Add an unconditional rotation before the parity measurment.

        UncondRenA=Gate('C' + str(self.params['carbon_list'][0]) + '_Uncond_Ren' + str(pt)+'_msmt_'+str(msmt), 'Carbon_Gate',
                Carbon_ind = self.params['carbon_list'][0],
                phase = self.params['C13_X_phase'])

        UncondRenB=Gate('C' + str(self.params['carbon_list'][1]) + '_Uncond_Ren' + str(pt)+'_msmt_'+str(msmt), 'Carbon_Gate',
                Carbon_ind = self.params['carbon_list'][1],
                phase = self.params['C13_X_phase'])

        #Append the two unconditional gates to the parity measurement sequence.
        sequence.append(UncondRenA)
        sequence.append(UncondRenB)
        
        sequence.extend(self.readout_carbon_sequence(
                                prefix              = 'Parity_msmt'+str(msmt),
                                pt                  = pt,
                                RO_trigger_duration = self.params['Repump_duration'],
                                carbon_list         = self.params['carbon_list'],
                                RO_basis_list       = ['X','X'],
                                el_RO_result        = '0',
                                readout_orientation = 'negative', #if correct parity --> electr0n in ms=0
                                Zeno_RO             = True))

        # Add an electorn pi pulse after repumping to ms=0
        sequence.append(Gate('2C_parity_elec_X_pt'+str(pt)+'_msmt_'+str(msmt),'electron_Gate',
                                Gate_operation='pi',
                                phase = self.params['X_phase'],
                                el_state_after_gate = '1',
                                el_state_bfore_gate= '0'))




        return sequence 




class Zeno_ThreeQB(DD.MBI_C13):

    '''
    Sequence: Sequence: |N-MBI| -|Cinit|^3-|MBE|^N-C13_Pi/2-(|Wait|-|Parity-measurement|-|Wait|)^M-|Tomography|
    '''
    mprefix='Zeno_3Qu'

    adwin_process='MBI_multiple_C13'

    def generate_sequence(self,upload=True,debug=False):

        pts = self.params['pts']

        #self.configure_AOM
        # set the output power of the repumping AOM to the desired
        qt.pulsar.set_channel_opt('AOM_Newfocus','high', qt.instruments['NewfocusAOM'].power_to_voltage(self.params['Zeno_SP_A_power'],controller='sec'))

        ### initialize empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Zeno_TwoQubit')

        for pt in range(pts): ### Sweep evolution times
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
                    addressed_carbon      = self.params['carbon_init_list'][kk],
                    el_after_init           = '0')
                gate_seq.extend(carbon_init_seq)
                init_wait_for_trigger = False

            ######################
            ### Initialize logical qubit via parity measurement.
            ##########

            C1 = self.params['carbon_list'][0] ### usually carbon 1
            C2 = self.params['carbon_list'][1] ### usually carbon 2
            C3 = self.params['carbon_list'][2] ### usually carbon 5

            ### NOTE:
            ### states: 00 --> |X1,X2,X3>
            ###         00p10 --> |X1>(|X2,X3>+ |-X2,-X3>)
            ###         00p11 --> (|X1,X2> + |-X1,-X2>)|X3>

            ### you have to choose the correct logical state.
            ### the two qubits which get put into an entangled state are always in the logical two qubit state 'X'
            do_carbonpi2_after = True
            do_carbonpi2_before = True

            if self.params['3qb_state'] == '00':
                ### initialize all 3 carbons via MBE into |XXX>
                # print "I AM HEREEEEE 00"
                self.params['carbon_MBE_list'] = [C3,C2,C1] ### order the carbons by their coherence time.
                self.params['MBE_bases'] = ['Y','Y','Y']
                self.params['carbon_MBE_logic_state'] = 'Z'
                do_carbonpi2_after = False
                do_carbonpi2_before = False

            elif self.params['3qb_state'] == '00p10':
                # print "I AM HEREEEEE 00p10"
                self.params['carbon_MBE_list'] = [C3,C2] ### initialized in maximally entangled state
                self.params['carbon_MBE_logic_state'] = 'X'
                self.params['carbon_classical'] = C1 ### rotate to +X
                do_carbonpi2_after = True
                do_carbonpi2_before = False

            elif self.params['3qb_state'] == '00p11':
                # print "I AM HEREEEEE 00p11"
                self.params['carbon_MBE_list'] = [C2,C1] ### initialized in maximally entangled state
                self.params['carbon_MBE_logic_state'] = 'X'
                self.params['carbon_classical'] = C3 ### rotate to +X
                do_carbonpi2_after = False
                do_carbonpi2_before = True

            if do_carbonpi2_before:
                UncondRen=Gate('C' + str(self.params['carbon_classical']) + '_Uncond_Ren_INIT' + str(pt), 'Carbon_Gate',
                        Carbon_ind = self.params['carbon_classical'],
                        phase = self.params['C13_Y_phase'])
                gate_seq.append(UncondRen)

            for kk in range(self.params['Nr_MBE']):
                
                probabilistic_MBE_seq =     self.logic_init_seq(
                        prefix              = '2C_init_' + str(kk+1),
                        pt                  =  pt,
                        carbon_list         = self.params['carbon_MBE_list'],
                        RO_basis_list       = self.params['MBE_bases'],
                        RO_trigger_duration = self.params['2C_RO_trigger_duration'],#150e-6,
                        el_RO_result        = '0',
                        logic_state         = self.params['carbon_MBE_logic_state'] ,
                        go_to_element       = mbi,
                        event_jump_element   = 'next',
                        readout_orientation = 'positive')

                gate_seq.extend(probabilistic_MBE_seq)


            ### add pi pulse after final init.

            gate_seq.extend([Gate('2C_init_elec_X_pt'+str(pt),'electron_Gate',
                                    Gate_operation='pi',
                                    phase = self.params['X_phase'],
                                    el_state_after_gate = '1')])

            ### rotate the last carbon to +X.
            if do_carbonpi2_after:
                UncondRen=Gate('C' + str(self.params['carbon_classical']) + '_Uncond_Ren_INIT' + str(pt), 'Carbon_Gate',
                        Carbon_ind = self.params['carbon_classical'],
                        phase = self.params['C13_Y_phase']+180)
                gate_seq.append(UncondRen)


            


            ### waiting time without Zeno msmmts.
            if self.params['Nr_Zeno_parity_msmts']==0:

                self.params['parity_duration']=0 ### this parameter is later used for data analysis.

                if self.params['free_evolution_time'][pt]!=0:
                    if self.params['free_evolution_time'][pt]< (self.params['2C_RO_trigger_duration']+3e-6): # because min length is 3e-6
                        print ('Error: carbon evolution time (%s) is shorter than Initialisation RO duration (%s)'
                                %(self.params['free_evolution_time'][pt],self.params['2C_RO_trigger_duration']))
                        qt.msleep(5)
                            ### Add waiting time
                    wait_gate = Gate('Wait_gate_'+str(pt),'passive_elt',
                                 wait_time = self.params['free_evolution_time'][pt]-self.params['2C_RO_trigger_duration'])
                    wait_seq = [wait_gate]; gate_seq.extend(wait_seq)

            ### If no waiting time:
            ### You have to implement an additional waiting time after the pi-pulse on the electron. Otherwise trouble with two consecutive MW pulses.
                else:
                    gate_seq.extend([Gate('2C_init_wait_gate_'+str(pt),'passive_elt',
                                     wait_time = 10e-6)])

            ### One or more parity measurements
            ### interleave waiting time with parity measurements.
            else:


                #Coarsely calculate the length of the carbon gates/ parity measurements.
                t_C13_gate1=2*self.params['C'+str(self.params['carbon_list'][0])+'_Ren_N'+self.params['electron_transition']][0]*(self.params['C'+str(self.params['carbon_list'][0])+'_Ren_tau'+self.params['electron_transition']][0])
                t_C13_gate2=2*self.params['C'+str(self.params['carbon_list'][1])+'_Ren_N'+self.params['electron_transition']][0]*(self.params['C'+str(self.params['carbon_list'][1])+'_Ren_tau'+self.params['electron_transition']][0])
                t_C13_gate3=2*self.params['C'+str(self.params['carbon_list'][2])+'_Ren_N'+self.params['electron_transition']][0]*(self.params['C'+str(self.params['carbon_list'][2])+'_Ren_tau'+self.params['electron_transition']][0])

                self.params['parity_duration']=(2*t_C13_gate3+2*t_C13_gate1+2*t_C13_gate2+self.params['Repump_duration'])*self.params['Nr_Zeno_parity_msmts']
                self.params['uncond_rotation_duration'] = t_C13_gate1+t_C13_gate2+t_C13_gate3


                print 'estimated parity duration in seconds:', self.params['parity_duration']

                if self.params['free_evolution_time'][pt]!=0:

                    if self.params['free_evolution_time'][pt]< (self.params['parity_duration'] + self.params['2C_RO_trigger_duration']+3e-6): # because min length is 3e-6
                        print ('Error: carbon evolution time (%s) is shorter than the sum of Initialisation RO duration (%s) and the duration of the parity measurements'
                                %(self.params['free_evolution_time'][pt],(self.params['parity_duration'] + self.params['2C_RO_trigger_duration']+3e-6)))
                        qt.msleep(5)

                    for i in range(self.params['Nr_Zeno_parity_msmts']):
                        
                        Parity_measurement=self.generate_parity_msmt(pt,msmt=i)
                        No_of_msmt=self.params['Nr_Zeno_parity_msmts']

                        ### this 'lengthy' formula is used to equally space the repumping intervals in time.
                        # waitduration=(self.params['free_evolution_time'][pt]-self.params['parity_duration'])/(No_of_msmt+1)+(No_of_msmt-1)*(t_C13_gate1+t_C13_gate2+t_C13_gate3)/(No_of_msmt+1)
                        total_evotime = self.params['free_evolution_time'][pt]-self.params['parity_duration']+self.params['uncond_rotation_duration']*self.params['Nr_Zeno_parity_msmts']
                        effective_waittime = total_evotime/float(self.params['Nr_Zeno_parity_msmts']+1)
                        actual_waitgate_not_final = effective_waittime - self.params['uncond_rotation_duration']
                        actual_waitgate_final = effective_waittime
                        print 'actual wait not final', actual_waitgate_not_final
                        print 'actual wait final', actual_waitgate_final

                        if i==0:
                            waitduration = actual_waitgate_not_final
                            wait_gateA = Gate('Wait_gate_A'+str(i)+'_'+str(pt),'passive_elt',
                                        wait_time = round(waitduration-self.params['2C_RO_trigger_duration'],6)) #subtract the length of the RO-trigger for the first waiting time.
                            # print round(waitduration-self.params['2C_RO_trigger_duration'],6)
                        elif i==self.params['Nr_Zeno_parity_msmts']-1:
                            waitduration = actual_waitgate_not_final
                            wait_gateA = Gate('Wait_gate_A'+str(i)+'_'+str(pt),'passive_elt',
                                        wait_time = round(waitduration,6))
                            # print round(waitduration,6)
                        else:
                            waitduration = actual_waitgate_not_final
                            wait_gateA = Gate('Wait_gate_A'+str(i)+'_'+str(pt),'passive_elt',
                                        wait_time = round(waitduration,6))
                            # print round(waitduration,6)

                        # tttt = round(waitduration-(No_of_msmt-1)*(t_C13_gate1+t_C13_gate2+t_C13_gate3)/(No_of_msmt+1)-2*(t_C13_gate1+t_C13_gate2+t_C13_gate3)/(No_of_msmt+1),6)*1e3

                        # print 'this is the wait duration', tttt
                                       
                        #for equally spaced measurements. see the entry in onenote of 30-01-2015 NK
                        equal_wait_gate = Gate('Wait_gate_B'+str(i)+'_'+str(pt),'passive_elt',
                                    wait_time = round(actual_waitgate_not_final,6))
                                     # wait_time = round(waitduration-(No_of_msmt-1)*(t_C13_gate1+t_C13_gate2+t_C13_gate3)/(No_of_msmt+1)-2*(t_C13_gate1+t_C13_gate2+t_C13_gate3)/(No_of_msmt+1),6))
                        # print round(waitduration-(No_of_msmt-1)*(t_C13_gate1+t_C13_gate2)/(No_of_msmt+1)-2*(t_C13_gate1+t _C13_gate2)/(No_of_msmt+1),6)
                        final_wait=Gate('Wait_gate_B'+str(i)+'_'+str(pt),'passive_elt',
                                    wait_time = round(actual_waitgate_final,6))
                                     # wait_time = round(waitduration,6))
                        # print round(waitduration,6)                       

                        # if not echo like then the measurement sequence should be equally spaced with respect to init and tomo
                        """ init --- wait for t --- (measurement --- wait for t)^n --- tomography"""
                        
                        #Add waiting time
                        ### the case of only one measurement
                        if i==0 and 1==(self.params['Nr_Zeno_parity_msmts']):
                            wait_seq = [wait_gateA]
                            gate_seq.extend(wait_seq)
                            gate_seq.extend(Parity_measurement)
                            wait_seq = [final_wait]
                            gate_seq.extend(wait_seq)

                        ### the first element of a sequence with more than one measurement
                        elif i==0:
                            wait_seq = [wait_gateA]
                            gate_seq.extend(wait_seq)
                            gate_seq.extend(Parity_measurement)
                            wait_seq = [equal_wait_gate]
                            gate_seq.extend(wait_seq)

                        ### not the first but also not the last element
                        elif i!=0 and i!=(self.params['Nr_Zeno_parity_msmts']-1):      
                            gate_seq.extend(Parity_measurement)
                            wait_seq = [equal_wait_gate]
                            gate_seq.extend(wait_seq)

                        ### more than one measurement and the last element was reached.
                        else:
                            gate_seq.extend(Parity_measurement)
                            wait_seq = [final_wait]
                            gate_seq.extend(wait_seq)
                                
                ### No waiting time, do the parity measurements directly. You have to implement an additional waiting time after the e-pulse in the beginning.
                ### as well as an additional wait time after the the last parity measurement because parity measurements also end with an e- pulse.
                else:
                    gate_seq.extend([Gate('2C_init_wait_gate_'+str(pt),'passive_elt',
                                     wait_time =10e-6)])
                    for kk in range(self.params['Nr_Zeno_parity_msmts']):
                        gate_seq.extend(self.generate_parity_msmt(pt, msmt=kk))
                    gate_seq.extend([Gate('Last_pi_wait_'+str(pt),'passive_elt',
                                     wait_time =10e-6)])
            ### Readout

            carbon_tomo_seq = self.readout_carbon_sequence(
                    prefix              = 'Tomo',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    el_state_in         = 1,
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
          
        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'

    def generate_parity_msmt(self,pt,msmt=0):

        sequence=[]

        # Add an unconditional rotation before the parity measurment.

        UncondRenA=Gate('C' + str(self.params['carbon_list'][0]) + '_Uncond_Ren' + str(pt)+'_msmt_'+str(msmt), 'Carbon_Gate',
                Carbon_ind = self.params['carbon_list'][0],
                phase = self.params['C13_X_phase'])

        UncondRenB=Gate('C' + str(self.params['carbon_list'][1]) + '_Uncond_Ren' + str(pt)+'_msmt_'+str(msmt), 'Carbon_Gate',
                Carbon_ind = self.params['carbon_list'][1],
                phase = self.params['C13_X_phase'])

        UncondRenC=Gate('C' + str(self.params['carbon_list'][2]) + '_Uncond_Ren' + str(pt)+'_msmt_'+str(msmt), 'Carbon_Gate',
                Carbon_ind = self.params['carbon_list'][2],
                phase = self.params['C13_X_phase'])

        #Append the two unconditional gates to the parity measurement sequence.
        
        sequence.append(UncondRenC) ### usually carbon 5
        sequence.append(UncondRenB) ### usually carbon 2
        sequence.append(UncondRenA) ### usually carbon 1

        sequence.extend(self.readout_carbon_sequence(
                                prefix              = 'Parity_msmt'+str(msmt),
                                pt                  = pt,
                                RO_trigger_duration = self.params['Repump_duration'],
                                carbon_list         = self.params['carbon_list'],
                                RO_basis_list       = ['X','X','X'],
                                el_RO_result        = '0',
                                readout_orientation = 'negative', #if correct parity --> electr0n in ms=0
                                Zeno_RO             = True))

        # Add an electorn pi pulse after repumping to ms=0
        sequence.append(Gate('2C_parity_elec_X_pt'+str(pt)+'_msmt_'+str(msmt),'electron_Gate',
                                Gate_operation='pi',
                                phase = self.params['X_phase'],
                                el_state_after_gate = '1',
                                el_state_bfore_gate= '0'))




        return sequence



class Zeno_TwoQB_classical(DD.MBI_C13):
    '''
    Sequence: Sequence: |N-MBI| -|MBE|^N-(|Wait|-|Parity-measurement|-|Wait|)^M-|Tomography|
    '''
    mprefix='Zeno_TwoQubit_classical'

    adwin_process='MBI_multiple_C13'

    def generate_sequence(self,upload=True,debug=False):

        pts = self.params['pts']

        #self.configure_AOM
        # set the output power of the repumping AOM to the desired
        qt.pulsar.set_channel_opt('AOM_Newfocus','high', qt.instruments['NewfocusAOM'].power_to_voltage(self.params['Zeno_SP_A_power'],controller='sec'))

        ### initialize empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Zeno_TwoQubit')

        for pt in range(pts): ### Sweep evolution times
            gate_seq = []

            ### Nitrogen MBI
            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]; gate_seq.extend(mbi_seq)

             ### Carbon initialization
             ### Initialization is not necessary for this experiment.

            # init_wait_for_trigger = True
            # for kk in range(self.params['Nr_C13_init']):
            #     carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
            #         prefix = 'C_MBI' + str(kk+1) + '_C',
            #         wait_for_trigger      = init_wait_for_trigger, pt =pt,
            #         initialization_method = self.params['init_method_list'][kk],
            #         C_init_state          = self.params['init_state_list'][kk],
            #         addressed_carbon      = self.params['carbon_init_list'][kk],
            #         el_after_init           = '0')
            #     gate_seq.extend(carbon_init_seq)
            #     init_wait_for_trigger = False

            mbi_wait_for_trig = Gate('Wait_for_MBI_'+str(pt),'passive_elt',
                         wait_time = 3e-6, wait_for_trigger = True)

            gate_seq.append(mbi_wait_for_trig)

            ### Abuse the MBE routine to initialize a classical 2 qubit correlation.

            for kk in range(self.params['Nr_MBE']):
                if 'Z' in self.params['2qb_logical_state']:
                    if self.params['2qb_logical_state'] == 'mZ':
                        init_logic_string = 'Y'
                    else: init_logic_string = 'mY'
                else:
                    init_logic_string = 'mX' ## set correct phases for the initial pi/2 pulse.

                probabilistic_MBE_seq =     self.logic_init_seq(
                        prefix              = '2C_init_' + str(kk+1),
                        pt                  =  pt,
                        carbon_list         = self.params['carbon_list'],
                        RO_basis_list       = self.params['MBE_bases'], ### needs to be changed in the exectuing script.
                        RO_trigger_duration = self.params['2C_RO_trigger_duration'],#150e-6,
                        el_RO_result        = '0',
                        logic_state         = init_logic_string,
                        go_to_element       = mbi,
                        event_jump_element   = 'next',
                        readout_orientation = 'positive')

                gate_seq.extend(probabilistic_MBE_seq)

            ### depending on the desired correlation we need to apply another pi/2 pulse after MBE!
            carbon_phase = self.params['C13_X_phase'] + 180

            if 'm' in self.params['2qb_logical_state']:
                carbon_phase  = carbon_phase + 180

            UncondRenA=Gate('C' + str(self.params['carbon_list'][0]) + 'init_Uncond_Ren' + str(pt), 'Carbon_Gate',
                    Carbon_ind = self.params['carbon_list'][0],
                    phase = carbon_phase)

            UncondRenB=Gate('C' + str(self.params['carbon_list'][1]) + 'init_Uncond_Ren' + str(pt), 'Carbon_Gate',
                    Carbon_ind = self.params['carbon_list'][1],
                    phase = self.params['C13_X_phase'] + 180)

            if 'Y' in self.params['2qb_logical_state']: ### need ZY correlations
                gate_seq.extend([UncondRenA])

            if 'X' in self.params['2qb_logical_state']: ### need ZZ correlations
                gate_seq.extend([UncondRenA,UncondRenB])

            ### add pi pulse after final init.

            gate_seq.extend([Gate('2C_init_elec_X_pt'+str(pt),'electron_Gate',
                                    Gate_operation='pi',
                                    phase = self.params['X_phase'],
                                    el_state_after_gate = '1')])


            ### waiting time without Zeno msmmts.
            if self.params['Nr_Zeno_parity_msmts']==0:

                self.params['parity_duration']=0 ### this parameter is later used for data analysis.

                if self.params['free_evolution_time'][pt]!=0:
                    if self.params['free_evolution_time'][pt]< (self.params['2C_RO_trigger_duration']+3e-6): # because min length is 3e-6
                        print ('Error: carbon evolution time (%s) is shorter than Initialisation RO duration (%s)'
                                %(self.params['free_evolution_time'][pt],self.params['2C_RO_trigger_duration']))
                        qt.msleep(5)
                            ### Add waiting time
                    wait_gate = Gate('Wait_gate_'+str(pt),'passive_elt',
                                 wait_time = self.params['free_evolution_time'][pt]-self.params['2C_RO_trigger_duration'])
                    wait_seq = [wait_gate]; gate_seq.extend(wait_seq)

            ### If no waiting time:
            ### You have to implement an additional waiting time after the pi-pulse on the electron. Otherwise trouble with two consecutive MW pulses.
                else:
                    gate_seq.extend([Gate('2C_init_wait_gate_'+str(pt),'passive_elt',
                                     wait_time = 10e-6)])

            ### One or more parity measurements
            ### interleave waiting time with parity measurements.
            else:


                #Coarsely calculate the length of the carbon gates/ parity measurements.
                t_C13_gate1=2*self.params['C'+str(self.params['carbon_list'][0])+'_Ren_N'+self.params['electron_transition']][0]*(self.params['C'+str(self.params['carbon_list'][0])+'_Ren_tau'+self.params['electron_transition']][0])
                t_C13_gate2=2*self.params['C'+str(self.params['carbon_list'][1])+'_Ren_N'+self.params['electron_transition']][0]*(self.params['C'+str(self.params['carbon_list'][1])+'_Ren_tau'+self.params['electron_transition']][0])

                self.params['parity_duration']=(2*t_C13_gate1+2*t_C13_gate2+self.params['Repump_duration'])*self.params['Nr_Zeno_parity_msmts']

                print 'estimated parity duration in seconds:', self.params['parity_duration']

                if self.params['free_evolution_time'][pt]!=0:

                    if self.params['free_evolution_time'][pt]< (self.params['parity_duration'] + self.params['2C_RO_trigger_duration']+3e-6): # because min length is 3e-6
                        print ('Error: carbon evolution time (%s) is shorter than the sum of Initialisation RO duration (%s) and the duration of the parity measurements'
                                %(self.params['free_evolution_time'][pt],(self.params['parity_duration'] + self.params['2C_RO_trigger_duration']+3e-6)))
                        qt.msleep(5)

                    for i in range(self.params['Nr_Zeno_parity_msmts']):
                        
                        Parity_measurement=self.generate_parity_msmt(pt,msmt=i)
                        No_of_msmt=self.params['Nr_Zeno_parity_msmts']


                        ### this 'lengthy' formula is used to equally space the repumping intervals in time.
                        waitduration=(self.params['free_evolution_time'][pt]-self.params['parity_duration'])/(No_of_msmt+1)+(No_of_msmt-1)*(t_C13_gate1+t_C13_gate2)/(No_of_msmt+1)

                        if i==0:
                            wait_gateA = Gate('Wait_gate_A'+str(i)+'_'+str(pt),'passive_elt',
                                        wait_time = round(waitduration-self.params['2C_RO_trigger_duration'],6)) #subtract the length of the RO-trigger for the first waiting time.
                            # print round(waitduration-self.params['2C_RO_trigger_duration'],6)
                        elif i==self.params['Nr_Zeno_parity_msmts']-1:
                            wait_gateA = Gate('Wait_gate_A'+str(i)+'_'+str(pt),'passive_elt',
                                        wait_time = round(waitduration,6))
                            # print round(waitduration,6)
                        else:
                            wait_gateA = Gate('Wait_gate_A'+str(i)+'_'+str(pt),'passive_elt',
                                        wait_time = round(waitduration,6))
                            # print round(waitduration,6)

                        #for equally spaced measurements. see the entry in onenote of 30-01-2015 NK
                        equal_wait_gate = Gate('Wait_gate_B'+str(i)+'_'+str(pt),'passive_elt',
                                     wait_time = round(waitduration-(No_of_msmt-1)*(t_C13_gate1+t_C13_gate2)/(No_of_msmt+1)-2*(t_C13_gate1+t_C13_gate2)/(No_of_msmt+1),6))
                        # print round(waitduration-(No_of_msmt-1)*(t_C13_gate1+t_C13_gate2)/(No_of_msmt+1)-2*(t_C13_gate1+t_C13_gate2)/(No_of_msmt+1),6)
                        final_wait=Gate('Wait_gate_B'+str(i)+'_'+str(pt),'passive_elt',
                                     wait_time = round(waitduration,6))
                        # print round(waitduration,6)

                        # if not echo like then the measurement sequence should be equally spaced with respect to init and tomo
                        """ init --- wait for t --- (measurement --- wait for t)^n --- tomography"""
                        
                        #Add waiting time
                        ### the case of only one measurement
                        if i==0 and 1==(self.params['Nr_Zeno_parity_msmts']):
                            wait_seq = [wait_gateA]
                            gate_seq.extend(wait_seq)
                            gate_seq.extend(Parity_measurement)
                            wait_seq = [final_wait]
                            gate_seq.extend(wait_seq)

                        ### the first element of a sequence with more than one measurement
                        elif i==0:
                            wait_seq = [wait_gateA]
                            gate_seq.extend(wait_seq)
                            gate_seq.extend(Parity_measurement)
                            wait_seq = [equal_wait_gate]
                            gate_seq.extend(wait_seq)

                        ### not the first but also not the last element
                        elif i!=0 and i!=(self.params['Nr_Zeno_parity_msmts']-1):      
                            gate_seq.extend(Parity_measurement)
                            wait_seq = [equal_wait_gate]
                            gate_seq.extend(wait_seq)

                        ### more than one measurement and the last element was reached.
                        else:
                            gate_seq.extend(Parity_measurement)
                            wait_seq = [final_wait]
                            gate_seq.extend(wait_seq)
                                
                ### No waiting time, do the parity measurements directly. You have to implement an additional waiting time after the e-pulse in the beginning.
                ### as well as an additional wait time after the the last parity measurement because parity measurements also end with an e- pulse.
                else:
                    gate_seq.extend([Gate('2C_init_wait_gate_'+str(pt),'passive_elt',
                                     wait_time =10e-6)])
                    for kk in range(self.params['Nr_Zeno_parity_msmts']):
                        gate_seq.extend(self.generate_parity_msmt(pt, msmt=kk))
                    gate_seq.extend([Gate('Last_pi_wait_'+str(pt),'passive_elt',
                                     wait_time =10e-6)])
            ### Readout

            carbon_tomo_seq = self.readout_carbon_sequence(
                    prefix              = 'Tomo',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    el_state_in         = 1,
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
                #for g in gate_seq:
                #    print g.name

            # if debug:
            #     for g in gate_seq:
            #         print g.name

            #         if ((g.C_phases_before_gate[self.params['carbon_list'][0]] == None) and (g.C_phases_before_gate[self.params['carbon_list'][1]] == None)):
            #             print "[ None , None ]"
            #         elif g.C_phases_before_gate[self.params['carbon_list'][0]] == None:
            #             print "[ None , %.3f ]" %(g.C_phases_before_gate[self.params['carbon_list'][1]]/np.pi*180)
            #         elif g.C_phases_before_gate[self.params['carbon_list'][1]] == None:
            #             print "b[ %.3f, None ]" %(g.C_phases_before_gate[self.params['carbon_list'][0]]/np.pi*180)
            #         else:
            #             print "b[%.3f ,1 %.3f ]" %(g.C_phases_before_gate[self.params['carbon_list'][0]]/np.pi*180, g.C_phases_before_gate[self.params['carbon_list'][1]]/np.pi*180)


            #         if ((g.C_phases_after_gate[self.params['carbon_list'][0]] == None) and (g.C_phases_after_gate[self.params['carbon_list'][1]] == None)):
            #             print "[ None , None ]"
            #         elif g.C_phases_after_gate[self.params['carbon_list'][0]] == None:
            #             print "[ None , %.3f ]" %(g.C_phases_after_gate[self.params['carbon_list'][1]]/np.pi*180)
            #         elif g.C_phases_after_gate[self.params['carbon_list'][1]] == None:
            #             print "a[ %.3f, None ]" %(g.C_phases_after_gate[self.params['carbon_list'][0]]/np.pi*180)
            #         else:
            #             print "a[ %.3f , %.3f ]" %(g.C_phases_after_gate[self.params['carbon_list'][0]]/np.pi*180, g.C_phases_after_gate[self.params['carbon_list'][1]]/np.pi*180)

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'

    def generate_parity_msmt(self,pt,msmt=0):

        sequence=[]

        # Add an unconditional rotation before the parity measurment.

        UncondRenA=Gate('C' + str(self.params['carbon_list'][0]) + '_Uncond_Ren' + str(pt)+'_msmt_'+str(msmt), 'Carbon_Gate',
                Carbon_ind = self.params['carbon_list'][0],
                phase = self.params['C13_X_phase'])

        UncondRenB=Gate('C' + str(self.params['carbon_list'][1]) + '_Uncond_Ren' + str(pt)+'_msmt_'+str(msmt), 'Carbon_Gate',
                Carbon_ind = self.params['carbon_list'][1],
                phase = self.params['C13_X_phase'])

        #Append the two unconditional gates to the parity measurement sequence.
        sequence.append(UncondRenA)
        sequence.append(UncondRenB)
        
        sequence.extend(self.readout_carbon_sequence(
                                prefix              = 'Parity_msmt'+str(msmt),
                                pt                  = pt,
                                RO_trigger_duration = self.params['Repump_duration'],
                                carbon_list         = self.params['carbon_list'],
                                RO_basis_list       = ['X','X'],
                                el_RO_result        = '0',
                                readout_orientation = 'negative', #if correct parity --> electr0n in ms=0
                                Zeno_RO             = True))

        # Add an electorn pi pulse after repumping to ms=0
        sequence.append(Gate('2C_parity_elec_X_pt'+str(pt)+'_msmt_'+str(msmt),'electron_Gate',
                                Gate_operation='pi',
                                phase = self.params['X_phase'],
                                el_state_after_gate = '1',
                                el_state_bfore_gate= '0'))




        return sequence 

        
class Zeno_simplified(DD.MBI_C13):
    """
    This class is a simplified version of the Zeno_TwoQB class.
    We try to build the same measurement up from scratch (in a very static way) and therefore try to reproduce the 'dip' we see in the signal.
    """

    mprefix         = 'Zeno_simplified'
    adwin_process   = 'MBI_multiple_C13'

    def generate_sequence(self,upload=True,debug = False):

        # set the output power of the repumping AOM to the desired
        qt.pulsar.set_channel_opt('AOM_Newfocus','high', qt.instruments['NewfocusAOM'].power_to_voltage(self.params['Zeno_SP_A_power'],controller='sec'))

        ## Generate the sequence.
        combined_seq=pulsar.Sequence('Zeno_thin')
        combined_list_of_elements = []


        for pt in range(self.params['pts']):

            gate_seq = []

            ### Nitrogen MBI

            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]

            gate_seq.extend(mbi_seq)

            ### 2x Carbon init
            init_wait_for_trigger = True
            for kk in range(self.params['Nr_C13_init']):
                carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                    prefix = 'C_MBI' + str(kk+1) + '_C',
                    wait_for_trigger      = init_wait_for_trigger, pt = pt,
                    initialization_method = 'swap',
                    C_init_state          = self.params['init_state_list'][kk],
                    addressed_carbon      = self.params['carbon_init_list'][kk],
                    el_after_init           = '0')

                gate_seq.extend(carbon_init_seq)
                init_wait_for_trigger = False

            ### 1x MBE
            ############################################

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

            ############################################

            ### add a pi pulse on the electronic state
            gate_seq.extend([Gate('Init_elec_pi_X_pt'+str(pt),'electron_Gate',
                                        Gate_operation='pi',
                                        phase = self.params['X_phase'],
                                        el_state_after_gate = '1')])

            ### wait for a specific time
            wait1 = Gate('wait1_'+str(pt), 'passive_elt', 
                wait_time = self.params['waittime1'][pt]-self.params['2C_RO_trigger_duration'])
            gate_seq.extend([wait1])


            ### do the first parity measurement
            C1_str = str(self.params['carbon_list'][0])
            C2_str = str(self.params['carbon_list'][1])
            ##################################################################
            ### define gates 
            #### unconditional
            uncond1 = Gate('Uncond_C'+ C1_str + '_1_' + str(pt), 'Carbon_Gate',
             Carbon_ind = int(C1_str),
             phase = self.params['C13_X_phase'])
            uncond2 = Gate('Uncond_C'+ C2_str + '_1_' + str(pt), 'Carbon_Gate',
             Carbon_ind = int(C2_str),
             phase = self.params['C13_X_phase'])
            
            #### conditional
            cond1 = Gate('Cond_C'+ C1_str + '_1_' + str(pt), 'Carbon_Gate',
             Carbon_ind = int(C1_str),
             phase = self.params['C13_X_phase'])
            cond2 = Gate('Cond_C'+ C2_str + '_1_' + str(pt), 'Carbon_Gate',
             Carbon_ind = int(C2_str),
             phase = self.params['C13_X_phase'])

            #### electron pulses
            initial_pi2 = Gate('Msmt1_initPi2_'+str(pt), 'electron_Gate',
                Gate_operation='pi2',
                phase = self.params['Y_phase'])

            final_pi2 = Gate('Msmt1_finalPi2_'+str(pt), 'electron_Gate',
                Gate_operation='pi2',
                phase = self.params['Y_phase']) ## the measurement outcome for a succesfull parity measurement should be 0!
            final_pi2.el_state_after_gate = '0' ### what if we use this for the Read-out of the carbons?

            #### Zeno repumper
            Laser = Gate('Zeno_repumper1_'+str(pt),'Trigger')
            Laser.channel = 'AOM_Newfocus'
            Laser.elements_duration = self.params['Repump_duration']
            # Laser.el_state_before_gate ='0' ### this is used in the carbon RO sequence generator.

            #### put together
            gate_seq.extend([uncond1,uncond2,initial_pi2,cond1,cond2,final_pi2,Laser])

            ##################################################################

            ### add electronic pi pulse
            gate_seq.extend([Gate('Msmt1_elec_pi_X_pt'+str(pt),'electron_Gate',
                                        Gate_operation='pi',
                                        phase = self.params['X_phase'],
                                        el_state_after_gate = '1',
                                        el_state_bfore_gate = '0')])

            ### wait again
            wait1 = Gate('wait2_'+str(pt), 'passive_elt')
            wait1.wait_time = self.params['waittime2'][pt]
            gate_seq.extend([wait1])


            ### do the next parity measurement
            ##################################################################################
            ### define gates 
            #### unconditional
            uncond1 = Gate('Uncond_C'+ C1_str + '_2_' + str(pt), 'Carbon_Gate',
             Carbon_ind = int(C1_str),
             phase = self.params['C13_X_phase'])
            uncond2 = Gate('Uncond_C'+ C2_str + '_2_' + str(pt), 'Carbon_Gate',
             Carbon_ind = int(C2_str),
             phase = self.params['C13_X_phase'])
            
            #### conditional
            cond1 = Gate('Cond_C'+ C1_str + '_2_' + str(pt), 'Carbon_Gate',
             Carbon_ind = int(C1_str),
             phase = self.params['C13_X_phase'])
            cond2 = Gate('Cond_C'+ C2_str + '_2_' + str(pt), 'Carbon_Gate',
             Carbon_ind = int(C2_str),
             phase = self.params['C13_X_phase'])

            #### electron pulses
            initial_pi2 = Gate('Msmt2_initPi2_'+str(pt), 'electron_Gate',
                Gate_operation='pi2',
                phase = self.params['Y_phase'])

            final_pi2 = Gate('Msmt2_finalPi2_'+str(pt), 'electron_Gate',
                Gate_operation='pi2',
                phase = self.params['Y_phase']) ## the measurement outcome for a succesfull parity measurement should be 0!
            final_pi2.el_state_after_gate = '0' ### what if we use this for the Read-out of the carbons?

            #### Zeno repumper
            Laser = Gate('Zeno_repumper2_'+str(pt),'Trigger')
            Laser.channel = 'AOM_Newfocus'
            Laser.elements_duration = self.params['Repump_duration']
            # Laser.el_state_before_gate ='0' ### this is used in the carbon RO sequence generator.

            #### put together
            gate_seq.extend([uncond1,uncond2,initial_pi2,cond1,cond2,final_pi2,Laser])
            ######################################################################################

            ### add electronic pi pulse
            gate_seq.extend([Gate('Msmt2_elec_pi_X_pt'+str(pt),'electron_Gate',
                                        Gate_operation='pi',
                                        phase = self.params['X_phase'],
                                        el_state_after_gate = '1',
                                        el_state_bfore_gate = '0')])

            ### wait again
            wait1 = Gate('wait3_'+str(pt), 'passive_elt')
            wait1.wait_time = self.params['waittime2'][pt]
            gate_seq.extend([wait1])

            ### do the last parity measurement
            ##################################################################################
            ### define gates 
            #### unconditional
            uncond1 = Gate('Uncond_C'+ C1_str + '_3_' + str(pt), 'Carbon_Gate',
             Carbon_ind = int(C1_str),
             phase = self.params['C13_X_phase'])
            uncond2 = Gate('Uncond_C'+ C2_str + '_3_' + str(pt), 'Carbon_Gate',
             Carbon_ind = int(C2_str),
             phase = self.params['C13_X_phase'])
            
            #### conditional
            cond1 = Gate('Cond_C'+ C1_str + '_3_' + str(pt), 'Carbon_Gate',
             Carbon_ind = int(C1_str),
             phase = self.params['C13_X_phase'])
            cond2 = Gate('Cond_C'+ C2_str + '_3_' + str(pt), 'Carbon_Gate',
             Carbon_ind = int(C2_str),
             phase = self.params['C13_X_phase'])

            #### electron pulses
            initial_pi2 = Gate('Msmt3_initPi2_'+str(pt), 'electron_Gate',
                Gate_operation='pi2',
                phase = self.params['Y_phase'])

            final_pi2 = Gate('Msmt3_finalPi2_'+str(pt), 'electron_Gate',
                Gate_operation='pi2',
                phase = self.params['Y_phase']) ## the measurement outcome for a succesfull parity measurement should be 0!
            final_pi2.el_state_after_gate = '0' ### what if we use this for the Read-out of the carbons?

            #### Zeno repumper
            Laser = Gate('Zeno_repumper3_'+str(pt),'Trigger')
            Laser.channel = 'AOM_Newfocus'
            Laser.elements_duration = self.params['Repump_duration']
            # Laser.el_state_before_gate ='0' ### this is used in the carbon RO sequence generator.

            #### put together
            gate_seq.extend([uncond1,uncond2,initial_pi2,cond1,cond2,final_pi2,Laser])
            ######################################################################################

            ### add electronic pi pulse
            gate_seq.extend([Gate('Msmt3_elec_pi_X_pt'+str(pt),'electron_Gate',
                                        Gate_operation='pi',
                                        phase = self.params['X_phase'],
                                        el_state_after_gate = '1',
                                        el_state_bfore_gate = '0')])

            ### final waiting time
            wait1 = Gate('wait4_'+str(pt), 'passive_elt')
            wait1.wait_time = self.params['waittime1'][pt]
            gate_seq.extend([wait1])

            ### Readout

            carbon_tomo_seq = self.readout_carbon_sequence(
                    prefix              = 'Tomo',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    el_state_in         = 1,
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

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'

class Zeno_ErrDetection(DD.MBI_C13):
    '''
    Sequence: Sequence: |N-MBI| -|Cinit|^2-|MBE|^N-(|Wait|-|Parity-measurement|-|Wait|)^M-|Tomography|
    '''
    """
    In contrast to the Zeno_TwoQB class, this class uses actual parity measurements with full read-outs to determine whether or not an error occured.
    Conditioned on detecting corrrect parity """

    mprefix='Zeno_ErrDet'
    adwin_process='MBI_multiple_C13'

    def generate_sequence(self,upload=True,debug=False):

        pts = self.params['pts']

        ### initialize empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Zeno_ErrDet')

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
                    addressed_carbon      = self.params['carbon_init_list'][kk],
                    el_after_init           = '0')
                gate_seq.extend(carbon_init_seq)
                init_wait_for_trigger = False

            ### Initialize logical qubit via parity measurement.


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
            gate_seq.extend([Gate('2C_init_elec_X_pt'+str(pt),'electron_Gate',
                                    Gate_operation='pi',
                                    phase = self.params['X_phase'],
                                    el_state_after_gate = '1')])


            ### waiting time without Zeno msmmts.
            if self.params['Nr_Zeno_parity_msmts']==0:
                if self.params['free_evolution_time'][pt]!=0:
                    if self.params['free_evolution_time'][pt]< (self.params['2C_RO_trigger_duration']+3e-6): # because min length is 3e-6
                        print ('Error: carbon evolution time (%s) is shorter than Initialisation RO duration (%s)'
                                %(self.params['free_evolution_time'][pt],self.params['2C_RO_trigger_duration']))
                        qt.msleep(5)
                            ### Add waiting time
                    wait_gate = Gate('Wait_gate_'+str(pt),'passive_elt',
                                 wait_time = self.params['free_evolution_time'][pt]-self.params['2C_RO_trigger_duration'])
                    wait_seq = [wait_gate]; gate_seq.extend(wait_seq)

            ### You have to implement an additional waiting time after the e-pulse. Otherwise trouble with two consecutive MW pulses.
                else:
                    gate_seq.extend([Gate('2C_init_wait_gate_'+str(pt),'passive_elt',
                                     wait_time = 10e-6)])

            ### interleave waiting time with parity measurements.
            else:


                #Coarsely calculate the length of the carbon gates/ parity measurements.
                t_C13_gate1=2*self.params['C'+str(self.params['carbon_list'][0])+'_Ren_N'+self.params['electron_transition']][0]*(self.params['C'+str(self.params['carbon_list'][0])+'_Ren_tau'+self.params['electron_transition']][0])
                t_C13_gate2=2*self.params['C'+str(self.params['carbon_list'][1])+'_Ren_N'+self.params['electron_transition']][0]*(self.params['C'+str(self.params['carbon_list'][1])+'_Ren_tau'+self.params['electron_transition']][0])

                self.params['parity_duration']=(2*t_C13_gate1+2*t_C13_gate2+150e-6)*self.params['Nr_Zeno_parity_msmts']

                print 'estimated parity duration in seconds:', self.params['parity_duration']

                if self.params['free_evolution_time'][pt]!=0:

                    if self.params['free_evolution_time'][pt]< (self.params['parity_duration'] + self.params['2C_RO_trigger_duration']+3e-6): # because min length is 3e-6
                        print ('Error: carbon evolution time (%s) is shorter than the sum of Initialisation RO duration (%s) and the duration of the parity measurements'
                                %(self.params['free_evolution_time'][pt],(self.params['parity_duration'] + self.params['2C_RO_trigger_duration']+3e-6)))
                        qt.msleep(5)

                    for i in range(self.params['Nr_Zeno_parity_msmts']):
                        
                        Parity_measurement=self.generate_parity_msmt(pt,msmt=i)
                        No_of_msmt=self.params['Nr_Zeno_parity_msmts']

                        if self.params['echo_like']:
                            ### Calculate the wait duration inbetween the parity measurements.
                            waitduration=(self.params['free_evolution_time'][pt]-self.params['parity_duration'])/(2.*No_of_msmt)
                        
                        else:
                            ### this 'lengthy' formula is used to equally space the repumping intervals in time.
                            waitduration=(self.params['free_evolution_time'][pt]-self.params['parity_duration'])/(No_of_msmt+1)+(No_of_msmt-1)*(t_C13_gate1+t_C13_gate2)/(No_of_msmt+1)

                        if i==0:
                            wait_gateA = Gate('Wait_gate_A'+str(i)+'_'+str(pt),'passive_elt',
                                        wait_time = round(waitduration-self.params['2C_RO_trigger_duration'],6)) #subtract the length of the RO-trigger for the first waiting time.
                            # print round(waitduration-self.params['2C_RO_trigger_duration'],6)
                        elif i==self.params['Nr_Zeno_parity_msmts']-1:
                            wait_gateA = Gate('Wait_gate_A'+str(i)+'_'+str(pt),'passive_elt',
                                        wait_time = round(waitduration,6))
                            # print round(waitduration,6)
                        else:
                            wait_gateA = Gate('Wait_gate_A'+str(i)+'_'+str(pt),'passive_elt',
                                        wait_time = round(waitduration,6))
                            # print round(waitduration,6)
                        #make the sequence symmetric around the parity measurements.
                        Decoupling_wait_gate = Gate('Wait_gate_B'+str(i)+'_'+str(pt),'passive_elt',
                                     wait_time = round(2*waitduration,6))

                        #for equally spaced measurements. see the entry in onenote of 30-01-2015 NK
                        equal_wait_gate = Gate('Wait_gate_B'+str(i)+'_'+str(pt),'passive_elt',
                                     wait_time = round(waitduration-(No_of_msmt-1)*(t_C13_gate1+t_C13_gate2)/(No_of_msmt+1)-2*(t_C13_gate1+t_C13_gate2)/(No_of_msmt+1),6))
                        # print round(waitduration-(No_of_msmt-1)*(t_C13_gate1+t_C13_gate2)/(No_of_msmt+1)-2*(t_C13_gate1+t_C13_gate2)/(No_of_msmt+1),6)
                        final_wait=Gate('Wait_gate_B'+str(i)+'_'+str(pt),'passive_elt',
                                     wait_time = round(waitduration,6))
                        # print round(waitduration,6)


                        if self.params['echo_like']: #this specifies the intertime delay of the Zeno measurements
                            ###
                            # echo like corresponds to the sequence: 
                            """init---(-wait-for-t---Msmt---wait-for-t)^n --- tomography """

                            ###
                            #Add waiting time
                            ### the case of only one measurement
                            if i==0 and 1==(self.params['Nr_Zeno_parity_msmts']):
                                wait_seq = [wait_gateA]
                                gate_seq.extend(wait_seq)
                                gate_seq.extend(Parity_measurement)
                                wait_seq = [final_wait]
                                gate_seq.extend(wait_seq)

                            ### the first element of a sequence with more than one measurement
                            elif i==0:
                                wait_seq = [wait_gateA]
                                gate_seq.extend(wait_seq)
                                gate_seq.extend(Parity_measurement)
                                wait_seq = [Decoupling_wait_gate]
                                gate_seq.extend(wait_seq)

                            ### not the first but also not the last element
                            elif i!=0 and i!=(self.params['Nr_Zeno_parity_msmts']-1):      
                                gate_seq.extend(Parity_measurement)
                                wait_seq = [Decoupling_wait_gate]
                                gate_seq.extend(wait_seq)

                            ### more than one measurement and the last element was reached.
                            else:
                                gate_seq.extend(Parity_measurement)
                                wait_seq = [final_wait]
                                gate_seq.extend(wait_seq)
                        
                        else:
                            # if not echo like then the measurement sequence should be equally spaced with respect to init and tomo
                            """ init --- wait for t --- (measurement --- wait for t)^n --- tomography"""
                            
                            #Add waiting time
                            ### the case of only one measurement
                            if i==0 and 1==(self.params['Nr_Zeno_parity_msmts']):
                                wait_seq = [wait_gateA]
                                gate_seq.extend(wait_seq)
                                gate_seq.extend(Parity_measurement)
                                wait_seq = [final_wait]
                                gate_seq.extend(wait_seq)

                            ### the first element of a sequence with more than one measurement
                            elif i==0:
                                wait_seq = [wait_gateA]
                                gate_seq.extend(wait_seq)
                                gate_seq.extend(Parity_measurement)
                                wait_seq = [equal_wait_gate]
                                gate_seq.extend(wait_seq)

                            ### not the first but also not the last element
                            elif i!=0 and i!=(self.params['Nr_Zeno_parity_msmts']-1):      
                                gate_seq.extend(Parity_measurement)
                                wait_seq = [equal_wait_gate]
                                gate_seq.extend(wait_seq)

                            ### more than one measurement and the last element was reached.
                            else:
                                gate_seq.extend(Parity_measurement)
                                wait_seq = [final_wait]
                                gate_seq.extend(wait_seq)
                                
                ### No waiting time, do the parity measurements directly. You have to implement an additional waiting time after the e-pulse in the beginning.
                ### as well as an additional wait time after the the last parity measurement because parity measurements also end with an e- pulse.
                else:
                    gate_seq.extend([Gate('2C_init_wait_gate_'+str(pt),'passive_elt',
                                     wait_time =10e-6)])
                    for kk in range(self.params['Nr_Zeno_parity_msmts']):
                        gate_seq.extend(self.generate_parity_msmt(pt, msmt=kk))
                    gate_seq.extend([Gate('Last_pi_wait_'+str(pt),'passive_elt',
                                     wait_time =10e-6)])
            ### Readout

            carbon_tomo_seq = self.readout_carbon_sequence(
                    prefix              = 'Tomo',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    el_state_in         = 1,
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
                #for g in gate_seq:
                #    print g.name

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
    
    def generate_parity_msmt(self,pt,msmt=0):

        sequence=[]

        # Add an unconditional rotation before the parity measurment.

        UncondRenA=Gate('C' + str(self.params['carbon_list'][0]) + '_Uncond_Ren' + str(pt)+'_msmt_'+str(msmt), 'Carbon_Gate',
                Carbon_ind = self.params['carbon_list'][0],
                phase = self.params['C13_X_phase'])

        UncondRenB=Gate('C' + str(self.params['carbon_list'][1]) + '_Uncond_Ren' + str(pt)+'_msmt_'+str(msmt), 'Carbon_Gate',
                Carbon_ind = self.params['carbon_list'][1],
                phase = self.params['C13_X_phase'])

        #Append the two unconditional gates to the parity measurement sequence.
        sequence.append(UncondRenA)
        sequence.append(UncondRenB)

        sequence.extend(self.readout_carbon_sequence(
                                prefix              = 'Parity_msmt'+str(msmt),
                                pt                  = pt,
                                RO_trigger_duration = 150e-6,
                                carbon_list         = self.params['carbon_list'],
                                RO_basis_list       = ['X','X'],
                                el_RO_result        = '0',
                                go_to_element       = 'next',
                                event_jump_element  = 'next', 
                                readout_orientation = 'negative', #if correct parity --> electr0n in ms=0
                                Zeno_RO             = False))

        # Add an electorn pi pulse after repumping to ms=0
        sequence.append(Gate('2C_parity_elec_X_pt'+str(pt)+'_msmt_'+str(msmt),'electron_Gate',
                                Gate_operation='pi',
                                phase = self.params['X_phase'],
                                el_state_after_gate = '1'))




        return sequence 


class Zeno_OneQB(DD.MBI_C13):
    '''
    Takes one carbon. Initialises via swap and rotates to X via a pi/2 rotation
    Several projective X measurements are performed afterwards
    Sequence: Sequence: |N-MBI| -|Cinit|-|C-Pi/2|-(|Wait|-|X-measurement|-|Wait|)^M-|Tomography|
    '''
    mprefix='Zeno_OneQubit'

    adwin_process='MBI_multiple_C13'

    def generate_sequence(self,upload=True,debug=False):

        pts = self.params['pts']

        #self.configure_AOM
        # set the output power of the repumping AOM to the desired
        qt.pulsar.set_channel_opt('AOM_Newfocus','high', qt.instruments['NewfocusAOM'].power_to_voltage(self.params['Zeno_SP_A_power'],controller='sec'))
        ### initialize empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Zeno_TwoQubit')

        for pt in range(pts): ### Sweep evolution times
            gate_seq = []

            ### Nitrogen MBI
            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]; gate_seq.extend(mbi_seq)

            ### Carbon initialization
            init_wait_for_trigger = True
            for kk in range(self.params['Nr_C13_init']):
                if self.params['logical_state']=='mZ':
                    self.params['init_state_list'][kk]='down'
                carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                    prefix = 'C_MBI' + str(kk+1) + '_C',
                    wait_for_trigger      = init_wait_for_trigger, pt =pt,
                    initialization_method = self.params['init_method_list'][kk],
                    C_init_state          = self.params['init_state_list'][kk],
                    addressed_carbon      = self.params['carbon_init_list'][kk],
                    el_after_init           = '0')
                gate_seq.extend(carbon_init_seq)
                init_wait_for_trigger = False

            ### Initialize single qubit by doing a pi/2 rotation.
            phase=0
            init = self.params['logical_state']
            if 'X' in init:
                phase = self.params['C13_Y_phase']
            if 'Y' in init:
                phase = self.params['C13_X_phase']
            if 'm' in init:
                phase = phase +180
            UncondRenA=Gate('C' + str(self.params['carbon_list'][0]) + '_Uncond_Ren' + str(pt), 'Carbon_Gate',
                Carbon_ind = self.params['carbon_list'][0],
                phase = phase)
            if not 'Z' in init:
                gate_seq.append(UncondRenA)

            

            ### add pi pulse after final init.
            if self.params['do_pi']:
                gate_seq.extend([Gate('2C_init_elec_X_pt'+str(pt),'electron_Gate',
                                        Gate_operation='pi',
                                        phase = self.params['X_phase'],
                                        el_state_after_gate = '1')])


            print'this is the free evo time',self.params['free_evolution_time'][pt]

            ### waiting time without Zeno msmmts.
            if self.params['Nr_Zeno_parity_msmts']==0:

                self.params['parity_duration'] = 0 ### this parameter is later used for data analysis.

                if self.params['free_evolution_time'][pt]!=0:
                    if self.params['free_evolution_time'][pt]< (self.params['2C_RO_trigger_duration']+3e-6): # because min length is 3e-6
                        print ('Error: carbon evolution time (%s) is shorter than Initialisation RO duration (%s)'
                                %(self.params['free_evolution_time'][pt],self.params['2C_RO_trigger_duration']))
                        qt.msleep(5)
                            ### Add waiting time
                    wait_gate = Gate('Wait_gate_'+str(pt),'passive_elt',
                                 wait_time = self.params['free_evolution_time'][pt]-self.params['2C_RO_trigger_duration'])
                    wait_seq = [wait_gate]; gate_seq.extend(wait_seq)

            ### If no waiting time:
            ### You have to implement an additional waiting time after the pi-pulse on the electron. Otherwise trouble with two consecutive MW pulses.
                else:
                    gate_seq.extend([Gate('2C_init_wait_gate_'+str(pt),'passive_elt',
                                     wait_time = 10e-6)])

            ### One or more parity measurements
            ### interleave waiting time with parity measurements.
            else:


                #Coarsely calculate the length of the carbon gates/ parity measurements.
                t_C13_gate1=2*self.params['C'+str(self.params['carbon_list'][0])+'_Ren_N'+self.params['electron_transition']][0]*(self.params['C'+str(self.params['carbon_list'][0])+'_Ren_tau'+self.params['electron_transition']][0])

                self.params['parity_duration']=(t_C13_gate1+self.params['Repump_duration'])*self.params['Nr_Zeno_parity_msmts']

                print 'estimated parity duration in seconds:', self.params['parity_duration']

                if self.params['free_evolution_time'][pt]!=0:

                    if self.params['free_evolution_time'][pt]< (self.params['parity_duration'] + self.params['2C_RO_trigger_duration']+3e-6): # because min length is 3e-6
                        print ('Error: carbon evolution time (%s) is shorter than the sum of Initialisation RO duration (%s) and the duration of the parity measurements'
                                %(self.params['free_evolution_time'][pt],(self.params['parity_duration'] + self.params['2C_RO_trigger_duration']+3e-6)))
                        qt.msleep(5)

                    for i in range(self.params['Nr_Zeno_parity_msmts']):
                        
                        Parity_measurement=self.generate_parity_msmt(pt,msmt=i)
                        No_of_msmt=self.params['Nr_Zeno_parity_msmts']

                        if self.params['echo_like']:
                            ### Calculate the wait duration inbetween the parity measurements.
                            waitduration=(self.params['free_evolution_time'][pt]-self.params['parity_duration'])/(2.*No_of_msmt)
                        
                        else:
                            ### this 'lengthy' formula is used to equally space the repumping intervals in time.
                            waitduration=(self.params['free_evolution_time'][pt]-self.params['parity_duration'])/(No_of_msmt+1)

                        if i==0:
                            wait_gateA = Gate('Wait_gate_A'+str(i)+'_'+str(pt),'passive_elt',
                                        wait_time = round(waitduration-self.params['2C_RO_trigger_duration'],6)) #subtract the length of the RO-trigger for the first waiting time.
                            # print round(waitduration-self.params['2C_RO_trigger_duration'],6)
                        elif i==self.params['Nr_Zeno_parity_msmts']-1:
                            wait_gateA = Gate('Wait_gate_A'+str(i)+'_'+str(pt),'passive_elt',
                                        wait_time = round(waitduration,6))
                            # print round(waitduration,6)
                        else:
                            wait_gateA = Gate('Wait_gate_A'+str(i)+'_'+str(pt),'passive_elt',
                                        wait_time = round(waitduration,6))
                            # print round(waitduration,6)
                        #make the sequence symmetric around the parity measurements.
                        Decoupling_wait_gate = Gate('Wait_gate_B'+str(i)+'_'+str(pt),'passive_elt',
                                     wait_time = round(2*waitduration,6))

                        #for equally spaced measurements. 
                        equal_wait_gate = Gate('Wait_gate_B'+str(i)+'_'+str(pt),'passive_elt',
                                     wait_time = round(waitduration,6))
                        # print round(waitduration-(No_of_msmt-1)*(t_C13_gate1+t_C13_gate2)/(No_of_msmt+1)-2*(t_C13_gate1+t_C13_gate2)/(No_of_msmt+1),6)
                        final_wait=Gate('Wait_gate_B'+str(i)+'_'+str(pt),'passive_elt',
                                     wait_time = round(waitduration,6))
                        # print round(waitduration,6)


                        if self.params['echo_like']: #this specifies the intertime delay of the Zeno measurements
                            ###
                            # echo like corresponds to the sequence: 
                            """init---(-wait-for-t---Msmt---wait-for-t)^n --- tomography """

                            ###
                            #Add waiting time
                            ### the case of only one measurement
                            if i==0 and 1==(self.params['Nr_Zeno_parity_msmts']):
                                wait_seq = [wait_gateA]
                                gate_seq.extend(wait_seq)
                                gate_seq.extend(Parity_measurement)
                                wait_seq = [final_wait]
                                gate_seq.extend(wait_seq)

                            ### the first element of a sequence with more than one measurement
                            elif i==0:
                                wait_seq = [wait_gateA]
                                gate_seq.extend(wait_seq)
                                gate_seq.extend(Parity_measurement)
                                wait_seq = [Decoupling_wait_gate]
                                gate_seq.extend(wait_seq)

                            ### not the first but also not the last element
                            elif i!=0 and i!=(self.params['Nr_Zeno_parity_msmts']-1):      
                                gate_seq.extend(Parity_measurement)
                                wait_seq = [Decoupling_wait_gate]
                                gate_seq.extend(wait_seq)

                            ### more than one measurement and the last element was reached.
                            else:
                                gate_seq.extend(Parity_measurement)
                                wait_seq = [final_wait]
                                gate_seq.extend(wait_seq)
                        
                        else:
                            # if not echo like then the measurement sequence should be equally spaced with respect to init and tomo
                            """ init --- wait for t --- (measurement --- wait for t)^n --- tomography"""
                            
                            #Add waiting time
                            ### the case of only one measurement
                            if i==0 and 1==(self.params['Nr_Zeno_parity_msmts']):
                                wait_seq = [wait_gateA]
                                gate_seq.extend(wait_seq)
                                gate_seq.extend(Parity_measurement)
                                wait_seq = [final_wait]
                                gate_seq.extend(wait_seq)

                            ### the first element of a sequence with more than one measurement
                            elif i==0:
                                wait_seq = [wait_gateA]
                                gate_seq.extend(wait_seq)
                                gate_seq.extend(Parity_measurement)
                                wait_seq = [equal_wait_gate]
                                gate_seq.extend(wait_seq)

                            ### not the first but also not the last element
                            elif i!=0 and i!=(self.params['Nr_Zeno_parity_msmts']-1):      
                                gate_seq.extend(Parity_measurement)
                                wait_seq = [equal_wait_gate]
                                gate_seq.extend(wait_seq)

                            ### more than one measurement and the last element was reached.
                            else:
                                gate_seq.extend(Parity_measurement)
                                wait_seq = [final_wait]
                                gate_seq.extend(wait_seq)
                                
                ### No waiting time, do the parity measurements directly. You have to implement an additional waiting time after the e-pulse in the beginning.
                ### as well as an additional wait time after the the last parity measurement because parity measurements also end with an e- pulse.
                else:
                    gate_seq.extend([Gate('2C_init_wait_gate_'+str(pt),'passive_elt',
                                     wait_time =10e-6)])
                    for kk in range(self.params['Nr_Zeno_parity_msmts']):
                        gate_seq.extend(self.generate_parity_msmt(pt, msmt=kk))
                        gate_seq.extend([Gate('Last_pi_wait_'+str(pt)+str(kk),'passive_elt',
                                         wait_time =10e-6)])

            if self.params['do_pi']:          
                carbon_tomo_seq = self.readout_carbon_sequence(
                        prefix              = 'Tomo',
                        pt                  = pt,
                        go_to_element       = None,
                        event_jump_element  = None,
                        RO_trigger_duration = 10e-6,
                        el_state_in         = 1,
                        carbon_list         = self.params['carbon_list'],
                        RO_basis_list       = self.params['C_RO_phase'][pt],
                        readout_orientation = self.params['electron_readout_orientation'])
            else:
                carbon_tomo_seq = self.readout_carbon_sequence(
                        prefix              = 'Tomo',
                        pt                  = pt,
                        go_to_element       = None,
                        event_jump_element  = None,
                        RO_trigger_duration = 10e-6,
                        el_state_in         = 0,
                        carbon_list         = self.params['carbon_list'],
                        RO_basis_list       = self.params['C_RO_phase'][pt],
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
                #for g in gate_seq:
                #    print g.name

            # if debug:
            #     for g in gate_seq:
            #         print g.name

                    # if ((g.C_phases_before_gate[self.params['carbon_list'][0]] == None) and (g.C_phases_before_gate[self.params['carbon_list'][1]] == None)):
                    #     print "[ None , None ]"
                    # elif g.C_phases_before_gate[self.params['carbon_list'][0]] == None:
                    #     print "[ None , %.3f ]" %(g.C_phases_before_gate[self.params['carbon_list'][1]]/np.pi*180)
                    # elif g.C_phases_before_gate[self.params['carbon_list'][1]] == None:
                    #     print "b[ %.3f, None ]" %(g.C_phases_before_gate[self.params['carbon_list'][0]]/np.pi*180)
                    # else:
                    #     print "b[%.3f ,1 %.3f ]" %(g.C_phases_before_gate[self.params['carbon_list'][0]]/np.pi*180, g.C_phases_before_gate[self.params['carbon_list'][1]]/np.pi*180)


                    # if ((g.C_phases_after_gate[self.params['carbon_list'][0]] == None) and (g.C_phases_after_gate[self.params['carbon_list'][1]] == None)):
                    #     print "[ None , None ]"
                    # elif g.C_phases_after_gate[self.params['carbon_list'][0]] == None:
                    #     print "[ None , %.3f ]" %(g.C_phases_after_gate[self.params['carbon_list'][1]]/np.pi*180)
                    # elif g.C_phases_after_gate[self.params['carbon_list'][1]] == None:
                    #     print "a[ %.3f, None ]" %(g.C_phases_after_gate[self.params['carbon_list'][0]]/np.pi*180)
                    # else:
                    #     print "a[ %.3f , %.3f ]" %(g.C_phases_after_gate[self.params['carbon_list'][0]]/np.pi*180, g.C_phases_after_gate[self.params['carbon_list'][1]]/np.pi*180)

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug,verbose=False)

        else:
            print 'upload = false, no sequence uploaded to AWG'

    def generate_parity_msmt(self,pt,msmt=0):

        sequence=[]

        
        sequence.extend(self.readout_carbon_sequence(
                                prefix              = 'Parity_msmt'+str(msmt),
                                pt                  = pt,
                                RO_trigger_duration = self.params['Repump_duration'],
                                carbon_list         = self.params['carbon_list'],
                                RO_basis_list       = ['X'],
                                el_RO_result        = '0',
                                readout_orientation = 'negative', #if correct parity --> electr0n in ms=0
                                Zeno_RO             = True,
                                add_wait_to_Zeno    = self.params['wait_gates_in_parity'][pt]))

        # Add an electorn pi pulse after repumping to ms=0
        sequence.append(Gate('2C_parity_elec_X_pt'+str(pt)+'_msmt_'+str(msmt),'electron_Gate',
                                Gate_operation='pi',
                                phase = self.params['X_phase'],
                                el_state_after_gate = '1',
                                el_state_bfore_gate= '0'))
        return sequence

class Zeno_OneQB_Zmeasurement(DD.MBI_C13):
    '''
    Takes one carbon. Initialises via swap in +Z or -Z
    Several projective Z measurements are performed afterwards
    Sequence: Sequence: |N-MBI| -|Cinit (swap)|-(|Wait|-|Z-measurement|-|Wait|)^M-|Tomography|
    The class also comes with possibility to plug in a pi/2 pusel on the carbon to generate different states.
    '''
    mprefix='Zeno_Zcorrelations'

    adwin_process='MBI_multiple_C13'

    ##### TODO: Add AOM control from the AWG for arbitrary AOM channels.
    # def autoconfikg(self):

    #     dephasing_AOM_voltage=qt.instruments[self.params['dephasing_AOM']].power_to_voltage(self.params['laser_dephasing_amplitude'],controller='sec')
    #     if dephasing_AOM_voltage > (qt.instruments[self.params['dephasing_AOM']]).get_sec_V_max():
    #         print 'Suggested power level would exceed V_max of the AOM driver.'
    #     else:
    #         #not sure if the secondary channel of an AOM can be obtained in this way?
    #         channelDict={'ch2m1': 'ch2_marker1'}
    #         print 'AOM voltage', dephasing_AOM_voltage
    #         self.params['Channel_alias']=qt.pulsar.get_channel_name_by_id(channelDict[qt.instruments[self.params['dephasing_AOM']].get_sec_channel()])
    #         qt.pulsar.set_channel_opt(self.params['Channel_alias'],'high',dephasing_AOM_voltage)

    #     MBI_C13.autoconfig()

    def generate_sequence(self,upload=True,debug=False):

        pts = self.params['pts']

        #self.configure_AOM
        # set the output power of the repumping AOM to the desired
        qt.pulsar.set_channel_opt('AOM_Newfocus','high', qt.instruments['NewfocusAOM'].power_to_voltage(self.params['Zeno_SP_A_power'],controller='sec'))

        ### initialize empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Zeno_OneQubit')

        for pt in range(pts): ### Sweep evolution times
            gate_seq = []

            ### Nitrogen MBI
            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]; gate_seq.extend(mbi_seq)

            ### Carbon initialization
            init_wait_for_trigger = True
            for kk in range(self.params['Nr_C13_init']):
                if self.params['logical_state']=='mZ':
                    self.params['init_state_list'][kk]='down'
                carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                    prefix = 'C_MBI' + str(kk+1) + '_C',
                    wait_for_trigger      = init_wait_for_trigger, pt =pt,
                    initialization_method = self.params['init_method_list'][kk],
                    C_init_state          = self.params['init_state_list'][kk],
                    addressed_carbon      = self.params['carbon_init_list'][kk],
                    el_after_init           = '0')
                gate_seq.extend(carbon_init_seq)
                init_wait_for_trigger = False

            ### Initialize single qubit by doing a pi/2 rotation.
            phase=0
            init = self.params['logical_state']
            if 'X' in init:
                phase = self.params['C13_Y_phase']
            if 'Y' in init:
                phase = self.params['C13_X_phase']
            if 'm' in init:
                phase = phase +180
            UncondRenA=Gate('C' + str(self.params['carbon_list'][0]) + '_Uncond_Ren' + str(pt), 'Carbon_Gate',
                Carbon_ind = self.params['carbon_list'][0],
                phase = phase)
            if not 'Z' in init:
                gate_seq.append(UncondRenA)

            

            ### add pi pulse after final init.
            if self.params['do_pi']:
                gate_seq.extend([Gate('2C_init_elec_X_pt'+str(pt),'electron_Gate',
                                        Gate_operation='pi',
                                        phase = self.params['X_phase'],
                                        el_state_after_gate = '1')])


            ### waiting time without Zeno msmmts.
            if self.params['Nr_Zeno_parity_msmts']==0:

                self.params['parity_duration'] = 0 ### this parameter is later used for data analysis.

                if self.params['free_evolution_time'][pt]!=0:
                    if self.params['free_evolution_time'][pt]< (self.params['2C_RO_trigger_duration']+3e-6): # because min length is 3e-6
                        print ('Error: carbon evolution time (%s) is shorter than Initialisation RO duration (%s)'
                                %(self.params['free_evolution_time'][pt],self.params['2C_RO_trigger_duration']))
                        qt.msleep(5)
                            ### Add waiting time
                    wait_gate = Gate('Wait_gate_'+str(pt),'passive_elt',
                                 wait_time = self.params['free_evolution_time'][pt]-self.params['2C_RO_trigger_duration'])
                    wait_seq = [wait_gate]; gate_seq.extend(wait_seq)

            ### If no waiting time:
            ### You have to implement an additional waiting time after the pi-pulse on the electron. Otherwise trouble with two consecutive MW pulses.
                else:
                    gate_seq.extend([Gate('2C_init_wait_gate_'+str(pt),'passive_elt',
                                     wait_time = 10e-6)])

            ### One or more parity measurements
            ### interleave waiting time with parity measurements.
            else:
                #Coarsely calculate the length of the carbon gates/ parity measurements.
                t_C13_gate1=2*self.params['C'+str(self.params['carbon_list'][0])+'_Ren_N'+self.params['electron_transition']][0]*(self.params['C'+str(self.params['carbon_list'][0])+'_Ren_tau'+self.params['electron_transition']][0])

                self.params['parity_duration']=(3*t_C13_gate1+self.params['Repump_duration'])*self.params['Nr_Zeno_parity_msmts'] ### Z measurements take two carobn gates.

                print 'estimated parity duration in seconds:', self.params['parity_duration']

                if self.params['free_evolution_time'][pt]!=0:

                    if self.params['free_evolution_time'][pt]< (self.params['parity_duration'] + self.params['2C_RO_trigger_duration']+3e-6): # because min length of a wait_gate is 3e-6
                        print ('Error: carbon evolution time (%s) is shorter than the sum of Initialisation RO duration (%s) and the duration of the parity measurements'
                                %(self.params['free_evolution_time'][pt],(self.params['parity_duration'] + self.params['2C_RO_trigger_duration']+3e-6)))
                        qt.msleep(5)

                    for i in range(self.params['Nr_Zeno_parity_msmts']):
                        
                        Parity_measurement=self.generate_parity_msmt(pt, self.params['do_pi'], msmt=i)
                        No_of_msmt=self.params['Nr_Zeno_parity_msmts']
                        
                        
                        
                        waitduration=(self.params['free_evolution_time'][pt]-self.params['parity_duration']/2.)

                        if i==0:
                            wait_gateA = Gate('Wait_gate_A'+str(i)+'_'+str(pt),'passive_elt',
                                        wait_time = round(waitduration-self.params['2C_RO_trigger_duration'],6)) #subtract the length of the RO-trigger for the first waiting time.
                            # print round(waitduration-self.params['2C_RO_trigger_duration'],6)
                        elif i==self.params['Nr_Zeno_parity_msmts']-1:
                            wait_gateA = Gate('Wait_gate_A'+str(i)+'_'+str(pt),'passive_elt',
                                        wait_time = round(waitduration,6))
                            # print round(waitduration,6)
                        else:
                            wait_gateA = Gate('Wait_gate_A'+str(i)+'_'+str(pt),'passive_elt',
                                        wait_time = round(waitduration,6))
                            # print round(waitduration,6)

                        #for equally spaced measurements. 
                        equal_wait_gate = Gate('Wait_gate_B'+str(i)+'_'+str(pt),'passive_elt',
                                     wait_time = round(waitduration,6))
                        # print round(waitduration-(No_of_msmt-1)*(t_C13_gate1+t_C13_gate2)/(No_of_msmt+1)-2*(t_C13_gate1+t_C13_gate2)/(No_of_msmt+1),6)
                        final_wait=Gate('Wait_gate_B'+str(i)+'_'+str(pt),'passive_elt',
                                     wait_time = round(waitduration,6))
                        # print round(waitduration,6)

                        # the measurement sequence should be equally spaced with respect to init and tomo
                        """ init --- wait for t --- (measurement --- wait for t)^n --- tomography"""
                        
                        #Add waiting time
                        ### the case of only one measurement
                        if i==0 and 1==(self.params['Nr_Zeno_parity_msmts']):
                            wait_seq = [wait_gateA]
                            gate_seq.extend(wait_seq)
                            gate_seq.extend(Parity_measurement)
                            wait_seq = [final_wait]
                            gate_seq.extend(wait_seq)

                        ### the first element of a sequence with more than one measurement
                        elif i==0:
                            wait_seq = [wait_gateA]
                            gate_seq.extend(wait_seq)
                            gate_seq.extend(Parity_measurement)
                            wait_seq = [equal_wait_gate]
                            gate_seq.extend(wait_seq)

                        ### not the first but also not the last element
                        elif i!=0 and i!=(self.params['Nr_Zeno_parity_msmts']-1):      
                            gate_seq.extend(Parity_measurement)
                            wait_seq = [equal_wait_gate]
                            gate_seq.extend(wait_seq)

                        ### more than one measurement and the last element was reached.
                        else:
                            gate_seq.extend(Parity_measurement)
                            wait_seq = [final_wait]
                            gate_seq.extend(wait_seq)
                                
                ### No waiting time, do the parity measurements directly. You have to implement an additional waiting time after the e-pulse in the beginning.
                ### as well as an additional wait time after the the last parity measurement because parity measurements also end with an e- pulse.
                else:
                    gate_seq.extend([Gate('2C_init_wait_gate_'+str(pt),'passive_elt',
                                     wait_time =10e-6)])
                    for kk in range(self.params['Nr_Zeno_parity_msmts']):
                        gate_seq.extend(self.generate_parity_msmt(pt, self.params['do_pi'], msmt=kk))
                    gate_seq.extend([Gate('Last_pi_wait_'+str(pt),'passive_elt',
                                     wait_time =10e-6)])

            if self.params['do_pi']:          
                carbon_tomo_seq = self.readout_carbon_sequence(
                        prefix              = 'Tomo',
                        pt                  = pt,
                        go_to_element       = None,
                        event_jump_element  = None,
                        RO_trigger_duration = 10e-6,
                        el_state_in         = 1,
                        carbon_list         = self.params['carbon_list'],
                        RO_basis_list       = self.params['C_RO_phase'][pt],
                        readout_orientation = self.params['electron_readout_orientation'])
            else:
                carbon_tomo_seq = self.readout_carbon_sequence(
                        prefix              = 'Tomo',
                        pt                  = pt,
                        go_to_element       = None,
                        event_jump_element  = None,
                        RO_trigger_duration = 10e-6,
                        el_state_in         = 0,
                        carbon_list         = self.params['carbon_list'],
                        RO_basis_list       = self.params['C_RO_phase'][pt],
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
                #for g in gate_seq:
                #    print g.name

            # if debug:
            #     for g in gate_seq:
            #         print g.name

            #         if ((g.C_phases_before_gate[self.params['carbon_list'][0]] == None) and (g.C_phases_before_gate[self.params['carbon_list'][1]] == None)):
            #             print "[ None , None ]"
            #         elif g.C_phases_before_gate[self.params['carbon_list'][0]] == None:
            #             print "[ None , %.3f ]" %(g.C_phases_before_gate[self.params['carbon_list'][1]]/np.pi*180)
            #         elif g.C_phases_before_gate[self.params['carbon_list'][1]] == None:
            #             print "b[ %.3f, None ]" %(g.C_phases_before_gate[self.params['carbon_list'][0]]/np.pi*180)
            #         else:
            #             print "b[%.3f ,1 %.3f ]" %(g.C_phases_before_gate[self.params['carbon_list'][0]]/np.pi*180, g.C_phases_before_gate[self.params['carbon_list'][1]]/np.pi*180)


            #         if ((g.C_phases_after_gate[self.params['carbon_list'][0]] == None) and (g.C_phases_after_gate[self.params['carbon_list'][1]] == None)):
            #             print "[ None , None ]"
            #         elif g.C_phases_after_gate[self.params['carbon_list'][0]] == None:
            #             print "[ None , %.3f ]" %(g.C_phases_after_gate[self.params['carbon_list'][1]]/np.pi*180)
            #         elif g.C_phases_after_gate[self.params['carbon_list'][1]] == None:
            #             print "a[ %.3f, None ]" %(g.C_phases_after_gate[self.params['carbon_list'][0]]/np.pi*180)
            #         else:
            #             print "a[ %.3f , %.3f ]" %(g.C_phases_after_gate[self.params['carbon_list'][0]]/np.pi*180, g.C_phases_after_gate[self.params['carbon_list'][1]]/np.pi*180)

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'

    def generate_parity_msmt(self,pt,do_pi,msmt=0):

        sequence=[]


        if do_pi:
            RO_orientation = 'negative'
        else:
            RO_orientation = 'positive'

        ### construct a Z measurement.

        UncondRen=Gate('C' + str(self.params['carbon_list'][0]) + '_Uncond_RenA' + str(pt)+'_msmt_'+str(msmt), 'Carbon_Gate',
                Carbon_ind = self.params['carbon_list'][0],
                phase = self.params['C13_Y_phase'])

        sequence.append(UncondRen)

        sequence.extend(self.readout_carbon_sequence(
                                prefix              = 'Parity_msmt'+str(msmt),
                                pt                  = pt,
                                RO_trigger_duration = self.params['Repump_duration'],
                                carbon_list         = self.params['carbon_list'],
                                RO_basis_list       = ['X'],
                                el_RO_result        = '0',
                                readout_orientation = RO_orientation, #if correct parity --> electr0n in ms=0
                                Zeno_RO             = True))

        UncondRen=Gate('C' + str(self.params['carbon_list'][0]) + '_Uncond_RenB' + str(pt)+'_msmt_'+str(msmt), 'Carbon_Gate',
                Carbon_ind = self.params['carbon_list'][0],
                phase = self.params['C13_Y_phase']+180)

        sequence.append(UncondRen)
            # Add an electorn pi pulse after repumping to ms=0
        if do_pi:    
            sequence.append(Gate('2C_parity_elec_X_pt'+str(pt)+'_msmt_'+str(msmt),'electron_Gate',
                                    Gate_operation='pi',
                                    phase = self.params['X_phase'],
                                    el_state_after_gate = '1',
                                    el_state_bfore_gate= '0'))



        return sequence 
