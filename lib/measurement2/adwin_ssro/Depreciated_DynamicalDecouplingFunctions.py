'''
Here old functions of several of the sequences of 
the dynamical decoupling class are stored so they can be easily recovered 
'''
class NuclearRamsey_no_elDD(DynamicalDecoupling):
    '''
    The NuclearRamsey class performs a ramsey experiment on a nuclear spin that is resonantly controlled using a decoupling sequence.
    The no DD variant does not decouple the electronic spin while the nuclear spin evolves. Instead it applies a pi/2 pulse to bring the
        electronic spin in a mixed state, let the nucleus evolve and then applies a second pi/2 pulse before the second Ren gate to read out.
    ---|pi/2| - |Ren| - |pi/2|--|Wait| -- |pi/2|- |Ren| - |pi/2| ---
    '''
    mprefix = 'CarbonRamsey'

    def generate_sequence(self, upload= True, debug = False):
        pts = self.params['pts']
        # #initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Nuclear Ramsey Sequence')

        for pt in range(pts):

            ###########################################
            #####    Generating the sequence elements      ######
            ###########################################
            initial_Pi2 = Gate('initial_pi2_'+str(pt),'electron_Gate')
            Ren_a = Gate('Ren_a_'+str(pt), 'Carbon_Gate')
            pi_2_a = Gate('pi2_a_'+str(pt),'electron_Gate')
            wait_gate = Gate('Wait_gate_'+str(pt),'passive_elt')
            pi_2_b = Gate('pi2_b_'+str(pt),'electron_Gate')
            Ren_b = Gate('Ren_b_'+str(pt), 'Carbon_Gate')
            final_Pi2 = Gate('final_pi2_'+str(pt),'electron_Gate')

            gate_seq = [initial_Pi2, Ren_a, pi_2_a, wait_gate, pi_2_b, Ren_b, final_Pi2]
            ############

            Ren_a.Carbon_ind = self.params['Addressed_Carbon']
            Ren_b.Carbon_ind = self.params['Addressed_Carbon'] #Default phase = 0
            Ren_a.scheme = self.params['Ren_Decoupling_scheme']
            Ren_b.scheme = self.params['Ren_Decoupling_scheme']
            Ren_b.phase = self.params['Phases_of_Ren_B'][pt]

            ###########
            # Set parameters for and generate the main DD element
            ###########
            wait_gate.wait_time = self.params['wait_times'][pt]  #here comes something with duration


            initial_Pi2.Gate_operation = 'pi2'

            initial_Pi2.phase = self.params['Y_phase']
            pi_2_a.Gate_operation='pi2'
            pi_2_a.phase = self.params['X_phase']
            pi_2_b.Gate_operation='pi2'

            pi_2_b.phase = self.params['Y_phase']
            final_Pi2.Gate_operation = 'pi2'
            final_Pi2.phase = self.params['X_phase']

            for g in gate_seq:
                if g.Gate_type =='Carbon_Gate' or g.Gate_type =='electron_decoupling':
                    self.get_gate_parameters(g)
                    self.generate_decoupling_sequence_elements(g)
                elif g.Gate_type =='passive_elt':
                    self.generate_passive_wait_element(g)
            #Insert connection elements in sequence
            gate_seq = self.insert_phase_gates(gate_seq,pt)
            #generate connection elements with proper phases, also includes electron pulses
            self.calc_and_gen_connection_elts(gate_seq)
            #Convert elements to AWG sequence and add to combined list
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq)
            combined_list_of_elements.extend(list_of_elements)

            if self.params['sweep_name']== 'Free Evolution time (s)':
                #This should correctly
                self.params['sweep_pts'][pt]= wait_gate.wait_time+gate_seq[gate_seq.index(wait_gate)+1].dec_duration
                #the gate_seq.index part always takes the dec duration of the element following the DD_gate. This gives the correct free evolution time on the axis.
                #It might be worng for the case of 0 pulses tough. Have to check what happens in that case for the duration.

                print 'changed sweep pt to %s' %(self.params['sweep_pts'][pt])

            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)
        else:
            print 'upload = false, no sequence uploaded to AWG'