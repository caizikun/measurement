 if g.Gate_type == 'Carbon_Gate':

                
                ### load the extra phase corrections for specific C13 crosstalks
                ### (note that this could in principle be done with a list of frequencies
                self.load_extra_phase_correction_lists(g)
                # print g.Carbon_ind,g.C_phases_after_gate

                for iC in range(len(g.C_phases_before_gate)):
                    if g.C_phases_before_gate[iC] == None and g.C_phases_after_gate[iC] == None :
                        if iC == g.Carbon_ind:
                            g.C_phases_after_gate[iC] = 0

                    elif g.C_phases_after_gate[iC] == 'reset':
                        g.C_phases_after_gate[iC] = 0

                    elif g.C_phases_after_gate[iC] == None:
                        g.C_phases_after_gate[iC] = np.mod(g.C_phases_before_gate[iC]+(2*g.tau*g.N)*C_freq[iC],  2*np.pi)
                        
                    if g.C_phases_after_gate[iC] != None:
                        #print 'gate on carbon x and transition, so i will apply a correction of on carbon ',g.Carbon_ind,self.params['electron_transition_used'],g.extra_phase_correction_list[iC],iC
                        g.C_phases_after_gate[iC] += g.extra_phase_correction_list[iC]
                    #if (iC==1) and (g.C_phases_before_gate[iC] != None):
                        #print g.name,iC,g.C_phases_before_gate[iC], g.C_phases_after_gate[iC],(g.C_phases_after_gate[iC]-g.extra_phase_correction_list[iC])










for kk, carbon_nr in enumerate(carbon_list):

            if RO_basis_list[kk] == 'Z' or RO_basis_list[kk] == '-Z':
                carbon_RO_seq.append( Gate(prefix + str(carbon_nr) + '_Ren_a_' + str(pt), 'Carbon_Gate',
                        Carbon_ind = carbon_nr, phase = 'reset',specific_transition = self.params['C'+str(carbon_nr)+'_dec_trans']))