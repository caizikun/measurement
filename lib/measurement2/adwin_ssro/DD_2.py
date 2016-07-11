'''
Measurement classes for everything dynamical decoupling related.
File made by Adriaan Rol
Edited by THT
Cast into v2 by NK
'''
import numpy as np
from scipy.special import erfinv
import qt
import copy
from measurement.lib.pulsar import pulse, pulselib, element, pulsar, eom_pulses
reload(pulsar)
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt;
import pulse_select as ps; reload(ps)




class Gate(object):
    '''
    The class for Gate objects that are used routinely in generating gate sequences.
    The gate object contains the metadata for generating the AWG elements and while
    running trough the sequence classes data relating to the AWG elements gets added
    before they are uploaded .
    '''
    def __init__(self,name,Gate_type,**kw):

        '''
        Supported gate types in the scripts are
        connection/phase gates: 'Connection_element' , 'electron_Gate',
        decoupling gates:  'Carbon_Gate', 'electron_decoupling'
        misc gates: 'passive_elt', (also has tau_cut)
        special gates: 'mbi', 'Trigger', 'LDE'
        '''
        self.name       = name
        self.prefix     = name          ### Default prefix is identical to name, can be overwritten

        # Information on what type of gate to implement
        self.Gate_type  = Gate_type
        self.phase      = kw.pop('phase',0)             ### Both for electron and Carbon gates
        self.extra_phase_after_gate = kw.pop('extra_phase_after_gate', 0)

        self.Carbon_ind = kw.pop('Carbon_ind',0)        ### 0 is the electronic spin, the rest are carbon spins

        self.N          = kw.pop('N',None)
        self.tau        = kw.pop('tau',None)

        self.comp       = kw.pop('comp',False)

        self.N2         = kw.pop('N2',None)
        self.tau2       = kw.pop('tau2',None)
        self.comp_phase = kw.pop('comp_phase',None)

        self.no_connection_elt = kw.pop('no_connection_elt',False) # avoids the insertion of carbon phase gates. For adaptive feedback. Use with care.

        self.wait_time  = kw.pop('wait_time',None)
        self.reps = kw.pop('reps',1) # only overwritten in case of Carbon decoupling elements or RF elements
        self.dec_duration = kw.pop('dec_duration', None)  # can be specified if a custom dec duration is desired


        self.specific_transition = kw.pop('specific_transition',None) # used to specify the mw transition 
        self.fixed_dec_duration = kw.pop('fixed_dec_duration',False)
        self.second_pi_phase    = kw.pop('second_pi_phase',102.8) # parameter for the transfer gate
        self.delay              =kw.pop('delay',230e-9) # parameter for the transfer gate

        self.Gate_operation = kw.pop('Gate_operation',None) ### For electron gates,'pi2', 'pi', 'general'
        self.amplitude      = kw.pop('amplitude', 0)        ### For electron gates, sets amplitude in case of 'general'
        self.length         = kw.pop('length',0)            ### For electron gates, sets length in case of 'general'
        self.RFfreq         = kw.pop('RFfreq',None)

        #Scheme is used both for generating decoupling elements as well as the combine to sequence command
        if self.Gate_type in ['Connection_element','electron_Gate','passive_elt','mbi']:
            self.scheme = 'single_element'
        else:
            self.scheme = kw.pop('scheme','auto')

        #Information on how to implement the gate (times, repetitions etc)

        # Information on how to combine the gates in the AWG.
        self.wait_for_trigger   = kw.pop('wait_for_trigger',False)
        self.event_jump         = kw.pop('event_jump',None)
        self.go_to              = kw.pop('go_to',None)

        # Empty list of C_phases before gate
        self.C_phases_before_gate   = [None]*10
        self.C_phases_after_gate    = [None]*10
        self.el_state_before_gate   = kw.pop('el_state_before_gate',None)
        self.el_state_after_gate    = kw.pop('el_state_after_gate',None)
        if self.Gate_type =='Carbon_Gate' and self.phase != None:   #THT: when is self.phase none? Isnt the default 0?
            if self.phase == 'reset':
                self.C_phases_after_gate[self.Carbon_ind] = self.phase
            else :
                self.C_phases_after_gate[self.Carbon_ind] = (self.phase + self.extra_phase_after_gate)/180.*np.pi


        ### In case a gate adds phases to other Carbon spins that cannot be corrected by the precession frq alone
        ### this parameter can add an extra phase correction to each Carbon spin, default is 0.
        self.extra_phase_correction_list = [0]*10


        '''
        Description of other attributes that get added by functions
        self.elements = elements
        self.repetitions = repetitions
        self.wait_reps = wait_reps
        self.elements_duration  # this is the duration of the AWG element corresponding to this gate.
          Note the difference with the gate duration (tau_cut)
        self.tau_cut # time removed from a decoupling sequence in final and initial element.
        self.tau_cut_before # this is the tau_cut of the previous element, gets added to connection type elements to calculate dec times
        self.tau_cut_after # this is the tau_cut of the following element
        self.dec_duration # this is the calculated decoupling duration for connection elements, this is used to correct for phases
        self.channel # whenever a trigger element outputs a signal on a marker channel, this identifies the channel type=string
                       Currently possible channel names for LT2: 'AOM_Newfocus'
        If there are any attributes being used frequently that are still missing here please add them for documentation
        '''

class DynamicalDecoupling(pulsar_msmt.MBI):

    '''
    This is a general class for decoupling gate sequences used in addressing Carbon -13 atoms. It contains functions needed for generating the pulse sequences for the AWG.
    It makes extensive use of the Gate class also found in this file.
    It is a child of PulsarMeasurment.MBI
    '''
    mprefix = 'DecouplingSequence'
    def autoconfig(self):

        self.params['min_dec_duration'] = self.params['min_dec_tau']*self.params['dec_pulse_multiple']*2

        pulsar_msmt.MBI.autoconfig(self)


    def get_tau_larmor(self):
        f_larmor = (self.params['ms+1_cntr_frq']-self.params['zero_field_splitting'])*self.params['g_factor_C13']/self.params['g_factor']
        tau_larmor = round(1/f_larmor,9)#rounds to ns
        return tau_larmor

    def _MBI_element(self,name ='MBI_CNOT'):
        # define the necessary pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 100e-9, amplitude = 0)

        X = pulselib.MW_IQmod_pulse('MBI MW pulse',
            I_channel = 'MW_Imod', Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod', Sw_channel=self.params['MW_switch_channel'],
            frequency = self.params['AWG_MBI_MW_pulse_ssbmod_frq'],
            amplitude = self.params['AWG_MBI_MW_pulse_amp'],
            length = self.params['AWG_MBI_MW_pulse_duration'],
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            Sw_risetime = self.params['MW_switch_risetime'])

        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = (self.params['AWG_to_adwin_ttl_trigger_duration'] \
                + self.params['AWG_wait_for_adwin_MBI_duration']),
            amplitude = 2)

        # the actual element
        mbi_element = element.Element(name, pulsar=qt.pulsar)
        mbi_element.append(T)
        mbi_element.append(X)
        mbi_element.append(adwin_sync)

        return mbi_element



    def _X_elt(self):
        '''
        X element that is used in different measurement child classes
        '''
        choose_source=self.params['multiple_source']
        
        if not choose_source:
            X = ps.X_pulse(self)
            return X           
        else:
            if self.params['electron_transition'] == self.params['mw1_transition']:
                X = ps.X_pulse(self)
                #print 'selecting mwsource 1 because el =p1'
                return X 
            elif self.params['electron_transition'] == self.params['mw2_transition']:
                X = ps.mw2_X_pulse(self)
                #print 'selecting mwsource 2 because el =m1'
                return X
            else:
                print 'Please define the used transition: transition is (%s)' %self.params['electron_transition']


        
        # X = pulselib.MW_IQmod_pulse('electron X-Pi-pulse',
        #     I_channel='MW_Imod', Q_channel='MW_Qmod',
        #     PM_channel='MW_pulsemod', Sw_channel=self.params['MW_switch_channel'],
        #     frequency = self.params['AWG_MBI_MW_pulse_mod_frq'],
        #     PM_risetime = self.params['MW_pulse_mod_risetime'],
        #     Sw_risetime = self.params['MW_switch_risetime'],
        #     length = self.params['fast_pi_duration'],
        #     amplitude = self.params['fast_pi_amp'],
        #     phase =  self.params['X_phase'])     
      
    def _mX_elt(self):
        '''
        X element that is used in different measurement child classes
        '''

        choose_source=self.params['multiple_source']

        if not choose_source:
            X = ps.mX_pulse(self)
            return X           
        else:
            if self.params['electron_transition'] == self.params['mw1_transition']:
                X = ps.mX_pulse(self)
                return X 
            elif self.params['electron_transition'] == self.params['mw2_transition']:
                X = ps.mw2_mX_pulse(self)
                return X
            else:
                print 'Please define the used transition: transition is (%s)' %self.params['electron_transition']
        # X = pulselib.MW_IQmod_pulse('electron X-Pi-pulse',
        #     I_channel='MW_Imod', Q_channel='MW_Qmod',
        #     PM_channel='MW_pulsemod', Sw_channel=self.params['MW_switch_channel'],
        #     frequency = self.params['AWG_MBI_MW_pulse_mod_frq'],
        #     PM_risetime = self.params['MW_pulse_mod_risetime'],
        #     Sw_risetime = self.params['MW_switch_risetime'],
        #     length = self.params['fast_pi_duration'],
        #     amplitude = self.params['fast_pi_amp'],
        #     phase =  self.params['X_phase']+180)       

    def _pi2_elt(self):
        '''
        xpi2 element that is used in different measurement child classes
        '''
        choose_source=self.params['multiple_source']

        if not choose_source:
            X = ps.Xpi2_pulse(self)
            return X           
        else:
            if self.params['electron_transition'] == self.params['mw1_transition']:
                X = ps.Xpi2_pulse(self)
                return X 
            elif self.params['electron_transition'] == self.params['mw2_transition']:
                X = ps.mw2_Xpi2_pulse(self)
                return X
            else:
                print 'Please define the used transition: transition is (%s)' %self.params['electron_transition']
        # pi2 = pulselib.MW_IQmod_pulse('electron Pi/2-pulse',
        #     I_channel='MW_Imod', Q_channel='MW_Qmod',
        #     PM_channel='MW_pulsemod', Sw_channel=self.params['MW_switch_channel'],
        #     frequency = self.params['fast_pi2_mod_frq'],
        #     PM_risetime = self.params['MW_pulse_mod_risetime'],
        #     Sw_risetime = self.params['MW_switch_risetime'],
        #     length = self.params['fast_pi2_duration'],
        #     amplitude = self.params['fast_pi2_amp'],
        #     phase = self.params['X_phase'])

    def _mpi2_elt(self):
        '''
        xpi2 element that is used in different measurement child classes
        '''
        choose_source=self.params['multiple_source']

        if not choose_source:
            X = ps.mXpi2_pulse(self)
            return X           
        else:
            if self.params['electron_transition'] == self.params['mw1_transition']:
                X = ps.mXpi2_pulse(self)
                return X 
            elif self.params['electron_transition'] == self.params['mw2_transition']:
                X = ps.mw2_mXpi2_pulse(self)
                return X
            else:
                print 'Please define the used transition: transition is (%s)' %self.params['electron_transition']
        
        # pi2 = pulselib.MW_IQmod_pulse('electron Pi/2-pulse',
        #     I_channel='MW_Imod', Q_channel='MW_Qmod',
        #     PM_channel='MW_pulsemod',
        #     frequency = self.params['fast_pi2_mod_frq'],
        #     PM_risetime = self.params['MW_pulse_mod_risetime'],
        #     length = self.params['fast_pi2_duration'],
        #     amplitude = self.params['fast_pi2_amp'],
        #     phase = self.params['X_phase'])

    def _Ypi2_elt(self):
        '''
        ypi2 element that is used in different measurement child classes
        '''
        choose_source=self.params['multiple_source']

        if not choose_source:
            X = ps.Ypi2_pulse(self)
            return X           
        else:
            if self.params['electron_transition'] ==self.params['mw1_transition']:
                X = ps.Ypi2_pulse(self)
                return X 
            elif self.params['electron_transition'] == self.params['mw2_transition']:
                X = ps.mw2_Ypi2_pulse(self)
                return X
            else:
                print 'Please define the used transition: transition is (%s)' %self.params['electron_transition']

    def _mYpi2_elt(self):
        '''
        ypi2 element that is used in different measurement child classes
        '''
        choose_source=self.params['multiple_source']

        if not choose_source:
            X = ps.mYpi2_pulse(self)
            return X           
        else:
            if self.params['electron_transition'] == self.params['mw1_transition']:
                X = ps.mYpi2_pulse(self)
                return X 
            elif self.params['electron_transition'] == self.params['mw2_transition']:
                X = ps.mw2_mYpi2_pulse(self)
                return X
            else:
                print 'Please define the used transition: transition is (%s)' %self.params['electron_transition']

    def _electron_pulse_elt(self, length, amplitude):
        '''
        general electron pulse element that is used in different measurement child classes
        '''
        electron_pulse = pulselib.MW_IQmod_pulse('electron-pulse',
            I_channel='MW_Imod', Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod', Sw_channel=self.params['MW_switch_channel'],
            frequency = self.params['fast_pi2_mod_frq'],
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            Sw_risetime = self.params['MW_switch_risetime'],
            length = length,
            amplitude = amplitude,
            phase = self.params['X_phase'])
        return electron_pulse

    def _spec_pi2_elt(self):
        '''
        xpi2 element with custom duration used for testing purposes only
        uses:
        self.params['cust_pi2_duration']
        self.params['cust_pi2_amp']
        '''
        pi2 = pulselib.MW_IQmod_pulse('electron Pi/2-pulse',
            I_channel='MW_Imod', Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod', Sw_channel=self.params['MW_switch_channel'],
            frequency = self.params['fast_pi2_mod_frq'],
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            Sw_risetime = self.params['MW_switch_risetime'],
            length = self.params['cust_pi2_duration'],
            amplitude = self.params['cust_pi2_amp'],
            phase = self.params['X_phase'])
        return pi2


    def _Y_elt(self):
        '''
        Y element that is used in different measurement child classes
        '''
        choose_source=self.params['multiple_source']

        if not choose_source:
            Y = ps.Y_pulse(self)
            return Y           
        else:
            if self.params['electron_transition'] == self.params['mw1_transition']:
                Y = ps.Y_pulse(self)
                return Y 
            elif self.params['electron_transition'] == self.params['mw2_transition']:
                Y = ps.mw2_Y_pulse(self)
                return Y
            else:
                print 'Please define the used transition: transition is (%s)' %self.params['electron_transition']
        # Y = pulselib.MW_IQmod_pulse('electron X-Pi-pulse',
        #     I_channel='MW_Imod', Q_channel='MW_Qmod',
        #     PM_channel='MW_pulsemod', Sw_channel=self.params['MW_switch_channel'],
        #     frequency = self.params['AWG_MBI_MW_pulse_mod_frq'],
        #     PM_risetime = self.params['MW_pulse_mod_risetime'],
        #     Sw_risetime = self.params['MW_switch_risetime'],
        #     length = self.params['fast_pi_duration'],
        #     amplitude = self.params['fast_pi_amp'],
        #     phase =  self.params['Y_phase'])
       

    def _mY_elt(self):
        '''
        mY element that is used in different measurement child classes
        '''
        choose_source=self.params['multiple_source']

        if not choose_source:
            Y = ps.mY_pulse(self)
            return Y          
        else:
            if self.params['electron_transition'] == self.params['mw1_transition']:
                Y = ps.mY_pulse(self)
                return Y 
            elif self.params['electron_transition'] == self.params['mw2_transition']:
                Y = ps.mw2_mY_pulse(self)
                return Y
            else:
                print 'Please define the used transition: transition is (%s)' %self.params['electron_transition']
        # Y = pulselib.MW_IQmod_pulse('electron X-Pi-pulse',
        #     I_channel='MW_Imod', Q_channel='MW_Qmod',
        #     PM_channel='MW_pulsemod', Sw_channel=self.params['MW_switch_channel'],
        #     frequency = self.params['AWG_MBI_MW_pulse_mod_frq'],
        #     PM_risetime = self.params['MW_pulse_mod_risetime'],
        #     Sw_risetime = self.params['MW_switch_risetime'],
        #     length = self.params['fast_pi_duration'],
        #     amplitude = self.params['fast_pi_amp'],
        #     phase =  self.params['Y_phase']+180)

       

    def _comp_pi2_pi_pi2_elt(self):
        '''
        Composite pi2 (0 deg) - pi (90 deg) - pi2 (0 deg) pulse
        '''
        comp_pi2_pi_pi2 = pulse.cp(ps.comp_pi2_pi_pi2_pulse(self))

        return comp_pi2_pi_pi2

    def _Trigger_element(self,duration = 10e-6, name='Adwin_trigger', outputChannel='adwin_sync'):
        '''
        Trigger element that is used in different measurement child classes
        '''
        if outputChannel == 'adwin_sync':
            Trig = pulse.SquarePulse(channel = outputChannel,
                length = duration, amplitude = 2)
            Trig_element = element.Element(name, pulsar=qt.pulsar,
                global_time = True)
            Trig_element.append(Trig)
        else:
            #Output channels for lasers are defined on AWG marker channels. Therefore, amplitue=1.=HIGH!
            Trig = pulse.SquarePulse(channel = outputChannel,
                length = duration, amplitude = 1.)
            Trig_element = element.Element(name, pulsar=qt.pulsar,
                global_time = True)
            Trig_element.append(Trig)

        return Trig_element

    ### functions for determining timing and what kind of elements to generate

    def get_gate_parameters(self,gate,resonance =0 ):
        '''
        Takes the gate_sequence as input and uses the carbon index and the operation to
        determine tau and N from the msmt params.
        Currently can only do single type of gate. Always does same amount of pulses
        ''' 
        if gate.Gate_type == 'electron_decoupling':
            if ~hasattr(gate,'tau_cut_after'):
                gate.tau_cut_after = 0
            if ~hasattr(gate,'tau_cut_before'):
                gate.tau_cut_before =0
            self.determine_connection_element_parameters(gate)
            self.determine_decoupling_scheme(gate)

        ind = gate.Carbon_ind
        if ind ==0:
                #Don't take arguments from a list if it is not acting on a
                #carbon (i.e. electron decoupling)
                return

              
        if self.params['multiple_source']:
            self.params['electron_transition_used']=self.params['C'+str(ind)+'_dec_trans']
            self.params['electron_transition']=self.params['electron_transition_used']
        
        if gate.comp == False:   
            if gate.N==None:
                # print 'this is N',self.params['C'+str(ind)+'_Ren_N'+self.params['electron_transition']][0]
                gate.N = self.params['C'+str(ind)+'_Ren_N'+self.params['electron_transition']][0]
            if gate.tau==None:
                gate.tau = self.params['C'+str(ind)+'_Ren_tau'+self.params['electron_transition']][0]
            
        if gate.comp==True:
            if gate.N==None:
                gate.N = self.params['C'+str(ind)+'_Ren_N2'+self.params['electron_transition']][resonance]
            if gate.tau==None:
                gate.tau = self.params['C'+str(ind)+'_Ren_tau2'+self.params['electron_transition']][resonance]

    def decompose_composite_gates(self,Gate_sequence_in,resonance = 0):
        """
        loops over the gate list and decomposes composite carbon gates where found.
        Inserts phase gates, single electron flips and decoupling sequences with specified tau and N on it's own.
        Necessary to define the following in the msmt params:
        Ns (list of number of pulses in a decoupling sequence, e.g. [14,14])
        taus (list of interpulse spacing, e.g. [7.2e-6,8.5e-6])
        phases (determines phaseshifts between decoupling elements e.g. [0,180]). First element of this list is never taken into account.
        flip electron for comp gates (inserts single pi pulses and therefore inverts the electron. e.g. [False, True]). First element of this list is never taken into account
        The given example values construct the following phase gate: decoupling_(electronflip_Rz)_decoupling
        """


        index_sequence_out = 0
        Gate_sequence_out = copy.deepcopy(Gate_sequence_in) ### will insert single carbon gates into gate sequence out.

        for g in Gate_sequence_in:
            ## only change the composition of a carbon gate if it was not predefined.

            if g.Gate_type =='Carbon_Gate' and g.N == None and g.tau == None:
                #found a carbon gate. Is it a composite gate?
                
                if len(self.params['C'+str(g.Carbon_ind)+'_Ren_N'+self.params['electron_transition']]) != 1:

                    ### yes, it is a composite gate! need to insert more gates into Gate_sequence.

                    #prepare parameters

                    c = 'C'+str(g.Carbon_ind)
                    el_trans = self.params['electron_transition']

                    name = g.name #unique naming! we need this atm.
                    Ns =self.params[c+'_Ren_N'+el_trans]
                    taus =self.params[c+'_Ren_tau'+el_trans]
                    phases = self.params[c+'_Ren_comp_phase'+el_trans]
                    flips = self.params[c+'_Ren_flip_electron_for_comp_gate_list'+el_trans]
                    inherent_phase = g.phase
                    specific_transition = self.params['C'+str(carbon_ind)+'_dec_trans']

                    
                    for i,N,tau,phase,flip in zip(range(len(Ns)),Ns,taus,phases,flips):

                        if i == 0:
                            #need to use deepcopy here in case there was a jump event or wait for trigger assigned to the gate!
                            g_insert = copy.deepcopy(g) ### one could write a deepcopy method for the gate classe to use keyword arguments for copying. Such as N=N tau=tau etc.
                            g_insert.N = N
                            g_insert.tau = tau

                            # print 'index of substitution',index_sequence_out

                            Gate_sequence_out[index_sequence_out] = g_insert  #overwrite the composite gate place holder!
                            
                        else:
                            if flip: ### the electron has to be inverted between the carbon gates
                                e_gate = Gate(name+'_invert_electron_'+str(i),'electron_Gate',
                                                                Gate_operation ='pi',
                                                                phase = self.params['X_phase'],
                                                                specific_transition = specific_transition)

                                Gate_sequence_out.insert(index_sequence_out,e_gate)
                                index_sequence_out += 1

                            if not (type(inherent_phase) is float):
                                inherent_phase = 0. #resets are only applicable to the first applied carbon gate. afterwards phase must be tracked

                            Gate_sequence_out.insert(index_sequence_out,Gate(name+'_'+str(i),'Carbon_Gate',N=N,tau=tau,phase=inherent_phase+phase,Carbon_ind =g.Carbon_ind))


                        index_sequence_out +=1
            else:
                index_sequence_out += 1


        # for g in Gate_sequence_in:
        #     print g.name, g.Gate_type

        # print '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
        # for g in Gate_sequence_out:
        #     print g.name, g.Gate_type
        return Gate_sequence_out




    def find_gate_index(self,name,gate_seq):
        '''
        Returns index of gate with gate.name == name in gate sequence
        '''
        for i, gate in enumerate(gate_seq):
            if gate.name == name:
                return i
        print 'Name (%s )  not found in gate sequence' %name
        return

    def insert_phase_gates(self,gate_seq,pt=0):
        ext_gate_seq = [] # this is the list that also contains the connection elements
        gates_in_need_of_connecting_elts1 = ['Carbon_Gate','electron_decoupling','passive_elt','RF_pulse']
        gates_in_need_of_connecting_elts2 = ['Carbon_Gate','electron_decoupling']
        #TODO_MAR: Insert a different type of phase gate in the case of a passive element.
        #TODO_THT: What  does this mean??? Clearly it does not work...

        for i in range(len(gate_seq)-1):
            ext_gate_seq.append(gate_seq[i])

            # skip if connection elts are explicitly not wanted.
            if gate_seq[i].no_connection_elt or gate_seq[i+1].no_connection_elt:
                # print 'continue',gate_seq[i].name
                continue

            if ((gate_seq[i].Gate_type in gates_in_need_of_connecting_elts1) and
                    (gate_seq[i+1].Gate_type in gates_in_need_of_connecting_elts1)):
                ext_gate_seq.append(Gate('phase_gate_'+ gate_seq[i+1].name + str(i)+'_'+str(pt),'Connection_element'))

            if gate_seq[i].Gate_type =='Trigger' :
                if (gate_seq[i+1].Gate_type in gates_in_need_of_connecting_elts2):
                    ext_gate_seq.append(Gate('phase_gate_' + gate_seq[i+1].name+str(i)+'_'+str(pt),'Connection_element'))

        ext_gate_seq.append(gate_seq[-1])
        gate_seq = ext_gate_seq
        return gate_seq

    def insert_transfer_gates(self,gate_seq,pt=0):
        ext_gate_seq = [] # this is the list that also contains the connection elements
        gates_in_need_of_transfer_elts = ['Carbon_Gate','electron_decoupling','passive_elt','RF_pulse','electron_Gate']

        for i in range(len(gate_seq)-1):
            
            ext_gate_seq.append(gate_seq[i])
            if ((gate_seq[i].Gate_type in gates_in_need_of_transfer_elts) and
                    (gate_seq[i+1].Gate_type in gates_in_need_of_transfer_elts)):
                if (gate_seq[i].specific_transition != gate_seq[i+1].specific_transition) and (gate_seq[i].el_state_after_gate == 'sup'):
                     if not ((gate_seq[i+1].Gate_operation== 'pi') and ((gate_seq[i+2].Gate_type =='Trigger') or gate_seq[i+2].Gate_operation=='pi2')):
                        if ~(gate_seq[i+1].name[0:4] !='Tomo' and  gate_seq[i+1].name[5] != gate_seq[i].name[5]):              
                            print 'These gates need a connection element in transition:%s and %s'%(gate_seq[i].name,gate_seq[i+1].name)
                            ext_gate_seq.append(Gate('Transfer_gate'+ gate_seq[i+1].name + str(i)+'_'+str(pt),'Transfer_element',
                                specific_transition=gate_seq[i+1].specific_transition
                                ))

        
        ext_gate_seq.append(gate_seq[-1])
        gate_seq = ext_gate_seq
        return gate_seq   

    def calc_and_gen_connection_elts(self,Gate_sequence):
        t = 0
        t_start = np.zeros(20) # don't expect to have more than 19 carbons, ind 0 represents electron, other indices the carbons
        
        for i,g in enumerate(Gate_sequence):
            #Note for Gate_type electron_decoupling nothing has to be done
            if g.Gate_type == 'Carbon_Gate': #set start times for tracking carbon evolution
                if t_start[g.Carbon_ind] == 0:
                    t_start[g.Carbon_ind] = t-g.tau_cut+g.N*g.tau*2 #Note this is the time the Carbon gate starts, this is not identical to the time where the AWG element starts
            elif g.Gate_type == 'Connection_element' or g.Gate_type == 'electron_Gate':
                print g.dec_duration
                ## if connection element determine parameters and track clock
                if i == len(Gate_sequence)-1: #at end of sequence no decoupling neccesarry for electron gate
                    g.dec_duration = 0

                else:# Determine
                    C_ind = Gate_sequence[i+1].Carbon_ind
                    if t_start[C_ind] == 0: #If not addresed before phase is arbitrary
                        g.dec_duration = 0
                    else:
                        desired_phase = Gate_sequence[i+1].phase/180.*np.pi #convert degrees to radians
                        precession_freq = self.params['C'+str(C_ind)+'_freq'+self.params['electron_transition']]*2*np.pi #convert to radians/s
                        if precession_freq == 0:
                            g.dec_duration = 0
                        else:
                            evolution_time = (t+Gate_sequence[i-1].tau_cut) - t_start[C_ind] # NB corrected for difference between time where the gate starts and where the AWG element starts
                            current_phase = evolution_time*precession_freq
                            phase_dif = (desired_phase-current_phase)%(2*np.pi)
                            dec_duration =(round( phase_dif/precession_freq
                                    *1e9/(self.params['dec_pulse_multiple']*2))
                                    *(self.params['dec_pulse_multiple']*2)*1e-9)
                            min_dec_duration= self.params['min_dec_tau']*self.params['dec_pulse_multiple']*2

                            while dec_duration <= min_dec_duration:
                                phase_dif = phase_dif+2*np.pi
                                dec_duration = (round( phase_dif/precession_freq
                                        *1e9/(self.params['dec_pulse_multiple']*2))
                                        *(self.params['dec_pulse_multiple']*2)*1e-9)

                            g.dec_duration = dec_duration

                #Connection element can never be the first or last element in the sequence
                if i ==0 or (i!=0 and Gate_sequence[i-1].Gate_type=='MBI'):
                    g.tau_cut_before = Gate_sequence[i+1].tau_cut
                    g.tau_cut_after= Gate_sequence[i+1].tau_cut
                elif (i== len(Gate_sequence)-1 or (
                            i ==len(Gate_sequence)-2) and Gate_sequence[i+1].Gate_type =='Trigger'):
                    g.tau_cut_before = Gate_sequence[i-1].tau_cut
                    g.tau_cut_after= Gate_sequence[i-1].tau_cut

                elif Gate_sequence[i+1].Gate_type == 'Trigger' :
                    g.tau_cut_before = Gate_sequence[i-1].tau_cut
                    g.tau_cut_after =Gate_sequence[i+2].tau_cut


                else:
                    g.tau_cut_before = Gate_sequence[i-1].tau_cut
                    g.tau_cut_after =Gate_sequence[i+1].tau_cut

                g.elements_duration = g.tau_cut_before+g.dec_duration+g.tau_cut_after
                self.determine_connection_element_parameters(g)
                self.generate_connection_element(g)
            t = t+g.elements_duration #tracks total time elapsed of elements NOTE THIS IS INCLUDES THE TAU CUT

        return Gate_sequence

    def determine_connection_element_parameters(self,g):
        '''
        Takes a decoupling duration and returns the 'optimal' tau and N to decouple it
        NOTE: N of decoupling for connection elements must be multiple of 4 pulses.
            This is correct by default. If you want to change it be cautious.
            If N is a multiple of 2 pulses this will create a 180 degree phase offset in the electron pulses because it ends in XY.
            '''

        if g.dec_duration == 0:
            g.N = 0
            g.tau = 0
            return


        ### if the electron is in an eigenstate before the phase gate we add a short wait_time later on.
        elif g.el_state_before_gate in ['0','1']:
            g.N = 0
            g.tau = 0
            return

        elif (g.dec_duration + g.tau_cut_after+g.tau_cut_before)<1e-6:
            print 'Error: connection element (%s )decoupling duration is too short g.dec_duration = %s, tau_cut_before = %s, tau_cut after = %s, must be atleast 1us' %(g.name, g.dec_duration,g.tau_cut_before,g.tau_after)
            return
        elif (g.dec_duration/(2*self.params['dec_pulse_multiple']))<self.params['min_dec_tau']:
            print 'Warning: connection element decoupling duration is too short. Not decoupling in time interval. \n dec_duration = %s, min dec_duration = %s, gate name = %s' %(g.dec_duration,2*self.params['min_dec_tau']*self.params['dec_pulse_multiple'],g.name)
            g.N=0
            g.tau = 0
            return g

        for k in range(40):
            #Sweep over possible tau's
            tau = g.dec_duration/(2*(k+1)*self.params['dec_pulse_multiple'])
            if tau == 0:
                g.N = 0
                g.tau = 0
            elif tau < self.params['min_dec_tau']:
                print g.name
                print g.dec_duration
                print k
                print 'Error: decoupling tau: (%s) smaller than minimum value(%s), decoupling duration (%s)' %(tau,self.params['min_dec_tau'],g.dec_duration )
                break
            elif tau > self.params['min_dec_tau'] and tau< self.params['max_dec_tau']:

                g.tau = tau
                g.N = int((k+1)*self.params['dec_pulse_multiple'])
                # print 'found the following decoupling tau: %s, N: %s' %(tau,g.N)
                break
            elif k == 39 and tau>self.params['max_dec_tau']:
                print 'Error: decoupling duration (%s) to large, for %s pulses decoupling tau (%s) larger than max decoupling tau (%s)' %(g.dec_duration,k,tau,self.params['max_dec_tau'])

        return g


    def determine_decoupling_scheme(self,Gate):
        '''
        Function used by generate_decoupling_sequence_elements
        Takes the first few lines of code that determine what kind of decoupling scheme is being used and puts it in a  function
        TODO_MAR: Document limitations and advantages of different decoupling schemes (multiples of 4ns?, lots of elements, very long elements)

        '''
        if self.params['multiple_source']:
            if Gate.specific_transition != None:
                self.params['electron_transition']=Gate.specific_transition
                if self.params['electron_transition'] == '_m1':
                    self.params['fast_pi_duration']=self.params['mw2_fast_pi_duration']
                    self.params['fast_pi2_duration']=self.params['mw2_fast_pi2_duration']
                if self.params['electron_transition'] == '_p1':
                    self.params['fast_pi_duration']=self.params['mw1_fast_pi_duration']
                    self.params['fast_pi2_duration']=self.params['mw1_fast_pi2_duration']

            elif Gate.Carbon_ind!=0:
                self.params['electron_transition_used']=self.params['C'+str(Gate.Carbon_ind)+'_dec_trans']
                self.params['electron_transition']=self.params['electron_transition_used']
                if self.params['C'+str(Gate.Carbon_ind)+'_dec_trans'] == '_m1':
                    self.params['fast_pi_duration']=self.params['mw2_fast_pi_duration']
                    self.params['fast_pi2_duration']=self.params['mw2_fast_pi2_duration']
                if self.params['C'+str(Gate.Carbon_ind)+'_dec_trans'] == '_p1':
                    self.params['fast_pi_duration']=self.params['mw1_fast_pi_duration']
                    self.params['fast_pi2_duration']=self.params['mw1_fast_pi2_duration']
       
        pi_pulse_duration= self.params['fast_pi_duration']
        if Gate.N == 0:
            ### For N==0, select a different scheme without pulses
            Gate.scheme = 'NO_Pulses'
        elif Gate.tau > 2.5e-6 :           ## ERROR?
            Gate.scheme = 'repeating_T_elt'
        elif Gate.tau<= self.params['fast_pi_duration']+20e-9: ## ERROR? shouldn't this be 1/2*pi_dur + 10?
            print 'Error: Gate(%s), tau (%s) too small: Pulses will overlap! \n Min tau = %s' %(Gate.name,Gate.tau,self.params['fast_pi_duration']+20e-9)
            return
        elif Gate.tau<0.5e-6:
            Gate.scheme = 'single_block'
        elif Gate.N%8:           ## ERROR? Should be N%8 == 0: ?
            Gate.scheme = 'XY8'
        elif Gate.N%2:           ## ERROR?
            Gate.scheme = 'XY4' #Might be outdated in functionality
        return Gate

    def load_C_freqs_in_radians_sec(self):
        '''
        loads carbon frequencies to a handy array
        '''
        C_freq_0 =[]
        C_freq_1=[]
        C_freq=[]
        for i in range(10):
            C0str = 'C'+str(i)+'_freq_0'
            C1str = 'C'+str(i)+'_freq_1'+self.params['electron_transition']
            Cdecstr = 'C'+str(i)+'_freq'+self.params['electron_transition']
            try:
                C_freq_0.append(self.params[C0str]*2*np.pi)
                C_freq_1.append(self.params[C1str]*2*np.pi)
                C_freq.append (self.params[Cdecstr]*2*np.pi)
            except:
                C_freq_1.append(None)
                C_freq_0.append(None)
                C_freq.append (None)

        return C_freq_0, C_freq_1, C_freq

    def load_extra_phase_correction_lists(self, Gate):
        '''
        loads extra phase corrections that are not covered by the precession frquency
        '''

        Gate.LDE_phase_correction_list = self.params['Carbon_LDE_phase_correction_list']/180.*np.pi
        Gate.LDE_phase_correction_list_init = self.params['Carbon_LDE_init_phase_correction_list']/180.*np.pi
        if self.params['multiple_source']:
            self.params['electron_transition']=self.params['C'+str(Gate.Carbon_ind)+'_dec_trans']


        if Gate.Carbon_ind != 0:
            Gate.extra_phase_correction_list = self.params['C' + str(Gate.Carbon_ind) + '_Ren_extra_phase_correction_list'+self.params['electron_transition']]/180.*np.pi

    def get_tau_cut_for_connecting_elts(self,Gate_sequence):
        '''
        Loops over all elements in the gate sequence and adds g.tau_cut_before and g.tau_cut_after to connection and
            electron gate elements.
        If there is only a trigger element between two electron gates the trigger elements_duration is extended twice by 1e-6 and
            that duration is added to the tau_cut_before and after of the respective electron gates.

        '''

        for i,g in enumerate(Gate_sequence):
            found_trigger = False
            if g.Gate_type == 'Connection_element' or g.Gate_type == 'electron_Gate':

                for g_b in Gate_sequence[i-1::-1]:  # Count back from current pos
                    g.tau_cut_before = 1e-6         # Default value in case it is the first element
                    if g_b.Gate_type =='Trigger':   # Checks if there is a trigger between the
                        found_trigger = True
                        g_t = g_b
                    elif (g_b.Gate_type =='Connection_element' or g_b.Gate_type=='electron_Gate') and found_trigger ==True:
                        g_t.elements_duration = g_t.elements_duration + 1e-6
                        g.tau_cut_before = 1e-6
                        break #break statement was set by NK and THT 22102014 to make sure that g.tau_cut_before is not overwitten below

                    elif g_b.Gate_type =='Connection_element' or g_b.Gate_type=='electron_Gate':
                        print ( 'Error: There is no decoupling gate or trigger between %s and %s.') %(g.name,g_b.name)
                        break

                    elif hasattr(g_b, 'tau_cut'):           #if Ren like gate is found
                        g.tau_cut_before = g_b.tau_cut
                        break

                for g_b in Gate_sequence[i+1::]:
                    g.tau_cut_after = 1e-6          # Default value in case it is the first element
                    if g_b.Gate_type =='Trigger':   # Checks if there is a trigger between the
                        found_trigger = True
                        g_t = g_b
                    elif (g_b.Gate_type =='Connection_element' or g_b.Gate_type=='electron_Gate') and found_trigger ==True:
                        g_t.elements_duration = g_t.elements_duration +1e-6
                        g.tau_cut_after = 1e-6
                        break
                        # This is the duration for the phase calculation, 1us is virtually added to compensate for the tau cut added to the electron gate
                    elif g_b.Gate_type =='Connection_element' or g_b.Gate_type=='electron_Gate':
                        print ( 'Error: There is no decoupling gate or trigger between %s and %s.') %(g.name,g_b.name)
                    elif hasattr(g_b, 'tau_cut'):
                        g.tau_cut_after = g_b.tau_cut
                        break #break statement was set by NK and THT 22102014
        return Gate_sequence

    def track_and_calc_phase(self,Gate_sequence):
        '''
        This function keeps track of phases in a Gate sequence.
        It differs from the version in the parent class DynamicalDecoupling in that it
        tracks the evolved phase per gate based on the electron state.
        This allows for mid gate changing of precession frequency.
        It requires three variables in the msmt params to be stored for each carbon
        C*_freq_0_^, C*_freq_1, C*_freq. where *is a carbon index (1,2 etc) and ^ is the used electron transition (m1 or p1).

        The following attributes are added to each gate
        C_phases_after_gate [phase_C1, phase_C2, ... ]
        el_state_after_gate:  Possibilities are '0', '1' and 'sup' ('sup is for superposition, a misnomer for dynamical decoupling).
        NOTE: 'sup'  is currently used to signify decoupling sequences. This is used when calculating phase gates on the carbons.
                some phase gates are then substituted for simple waiting times if the electron is in an eigenstate before the phase gate is applied.

        If g.C_phases_after_gate[i]  is specified for the gate before the function is called this takes priority
        over the phase calculated. This can be used if one wants to reset phase for example in the case of readouts.
        If 'g.phase = None' no phase correction using dynamical decoupling is applied.

        NOTE: All phases used are in radians. Input phases are in degrees because of convention.
        NOTE: Phases and electron states are with respect to the IDEAL gate.
        This does not correspond to the length of AWG elements.
        NOTE: g.el_state_after_gate has to be explicitly stated when it changes.
        No automatic bookkeeping done for you.
        NOTE: If you want to use this for complicated subsequences with jump statements the electron phase
            after the RO trigger must be set in the element that comes after it using g.el_state_before_gate.
            All different sequences must be sent trough this track and calc phase function in order to make this.

        '''
        # Load Carbon phases into handy array
        C_freq_0, C_freq_1, C_freq = self.load_C_freqs_in_radians_sec()

        for i,g in enumerate(Gate_sequence):

            

            ###########################################
            ### Keeping track of the electron state ###
            ###########################################

            if g.el_state_before_gate == None:
                if i == 0:                         # At first element, start initialised
                    g.el_state_before_gate = 'sup' # if nothing added g.el_state_before_gate it defaults to sup.
                else:
                    g.el_state_before_gate =Gate_sequence[i-1].el_state_after_gate

            if g.el_state_after_gate == None:
                g.el_state_after_gate = g.el_state_before_gate
                
                # if g.Gate_type == 'electron_Gate':
                #     print 'this is the electron state after',g.name, g.el_state_after_gate    


            if i!= 0:
                g.C_phases_before_gate = Gate_sequence[i-1].C_phases_after_gate


            ### MW pi/2 pulses need special attention for tracking the electron state.


            if g.el_state_before_gate in ['0','1'] and g.Gate_operation == 'pi2':
                g.el_state_after_gate = 'sup' ### this signifies the begin of a decoupling sequence.

     
            ### we also care about the electron state if we apply pi pulses.
            if g.el_state_before_gate in ['0','1'] and g.Gate_operation == 'pi':

                if g.el_state_before_gate == '0':
                    g.el_state_after_gate = '1'

                else:
                    g.el_state_after_gate = '0'
            # if g.Gate_type == 'electron_Gate':
            #     print 'this is the gate operation',g.name, g.Gate_operation,g.el_state_before_gate,g.el_state_after_gate     
            #     print '****************' 

            ###############################################
            ### Keeping track of the electron transition###
            ###############################################

            if self.params['multiple_source']:                
                if g.specific_transition != None:
                    # print
                    # print 'for this gate i have chosen this transition',g.name,g.specific_transition,g.el_state_before_gate,g.el_state_after_gate
                    # print
                    self.params['electron_transition']=g.specific_transition
                    C_freq_0, C_freq_1, C_freq = self.load_C_freqs_in_radians_sec()
                   
                elif g.Carbon_ind != 0:
                    self.params['electron_transition_used']=self.params['C'+str(g.Carbon_ind)+'_dec_trans']
                    self.params['electron_transition']=self.params['electron_transition_used']
                    # print
                    # print 'for this gate i have chosen this transition based on Carb ind',g.name,g.specific_transition,g.el_state_before_gate,g.el_state_after_gate
                    # print
                    C_freq_0, C_freq_1, C_freq = self.load_C_freqs_in_radians_sec()
                else:
                #print 'this gate does not have a carbon ind or spec freq',g.name
                    C_freq_0, C_freq_1, C_freq = self.load_C_freqs_in_radians_sec()       

            
            ###########################
            ### Decoupling elements ###
            ###########################
            # print 'Gate type', g.Gate_type
            if g.Gate_type == 'Carbon_Gate':

                ### load the extra phase corrections for specific C13 crosstalks
                ### (note that this could in principle be done with a list of frequencies
                self.load_extra_phase_correction_lists(g)

                for iC in range(len(g.C_phases_before_gate)):
                    if g.C_phases_before_gate[iC] == None and g.C_phases_after_gate[iC] == None :
                        if iC == g.Carbon_ind:
                            g.C_phases_after_gate[iC] = 0

                    elif g.C_phases_after_gate[iC] == 'reset':
                        g.C_phases_after_gate[iC] = 0
                        # print g.name


                    elif g.C_phases_after_gate[iC] == None:
                        g.C_phases_after_gate[iC] = np.mod(g.C_phases_before_gate[iC]+(2*g.tau*g.N)*C_freq[iC],  2*np.pi)
                        
                    if g.C_phases_after_gate[iC] != None:

                        g.C_phases_after_gate[iC] += g.extra_phase_correction_list[iC]
                    #if (iC==1) and (g.C_phases_before_gate[iC] != None):
                        #print g.name,iC,g.C_phases_before_gate[iC], g.C_phases_after_gate[iC],(g.C_phases_after_gate[iC]-g.extra_phase_correction_list[iC])

            elif g.Gate_type =='electron_decoupling':

                 #print 'I need help here with this gate',g.name,g.tau,g.N,g.C_phases_before_gate,g.C_phases_after_gate
                for iC in range(len(g.C_phases_before_gate)):
                    if g.C_phases_after_gate[iC] == 'reset':
                        g.C_phases_after_gate[iC] = 0
                    elif g.C_phases_after_gate[iC] == None and g.C_phases_before_gate[iC] != None:
                        #print 'I need help here with this gate',g.name,g.tau,g.N,g.C_phases_before_gate[iC],g.C_phases_after_gate[iC],C_freq[iC]

                        g.C_phases_after_gate[iC] = (g.C_phases_before_gate[iC]+ (2*g.tau*g.N)*C_freq[iC])%(2*np.pi)

            #######################
            # Connecting elements #
            #######################

            elif g.Gate_type == 'Connection_element' or g.Gate_type == 'electron_Gate':

                if i == len(Gate_sequence)-1:
                    g.dec_duration = 0
                elif g.dec_duration > 0:
                    pass
                elif Gate_sequence[i+1].phase == None or Gate_sequence[i+1].phase == 'reset' or Gate_sequence[i-1].no_connection_elt:
                    g.dec_duration =0
                else:
                    desired_phase = Gate_sequence[i+1].phase/180.*np.pi
                    Carbon_index  = Gate_sequence[i+1].Carbon_ind

                    if g.C_phases_before_gate[Carbon_index] == None:
                        g.dec_duration = 0

                    ### check for the electron in an eigenstate

                    else:
                        phase_diff =(desired_phase - g.C_phases_before_gate[Carbon_index])%(2*np.pi)
                        #print 'Phase_difference: ',phase_diff, g.name
                        if ( (phase_diff <= (self.params['min_phase_correct']/180.*np.pi)) or
                                (abs(phase_diff -2*np.pi) <=  (self.params['min_phase_correct']/180.*np.pi)) ):
                        # For very small phase differences correcting phase with decoupling introduces a larger error
                        #  than the phase difference error.
                            g.dec_duration = 0
                        else:

                            ### check if the electron is in an eigenstate before the phase gate
                            if g.el_state_before_gate in ['0','1']:
                                
                                if g.el_state_before_gate == '0':
                                    g.dec_duration = round(phase_diff/C_freq_0[Carbon_index]*1e9)*1e-9
                                    # print 'i calculated the dec duration', g.dec_duration*1e6,g.name
                                else:
                                    g.dec_duration = round(phase_diff/C_freq_1[Carbon_index]*1e9)*1e-9

                            ### electron is not in an eigenstate we need to decouple. write new/smart function for this.
                            else:
   
                                # print Carbon_index,C_freq[Carbon_index],phase_diff,self.params['dec_pulse_multiple']
                                g.dec_duration =(round( phase_diff/C_freq[Carbon_index]
                                        *1e9/(self.params['dec_pulse_multiple']*2))
                                        *(self.params['dec_pulse_multiple']*2)*1e-9)
                                # print 'decoupling duration: ',g.dec_duration
                                while g.dec_duration <= self.params['min_dec_duration']:
                                    phase_diff = phase_diff +2*np.pi
                                    g.dec_duration =(round( phase_diff/C_freq[Carbon_index]
                                            *1e9/(self.params['dec_pulse_multiple']*2))
                                            *(self.params['dec_pulse_multiple']*2)*1e-9)
                                g.dec_duration = g.dec_duration

                # print 'phases before ',g.C_phases_before_gate
                for iC in range(len(g.C_phases_before_gate)):
                    if (g.C_phases_after_gate[iC] == None) and (g.C_phases_before_gate[iC] !=None) :
                        #print 'C_phases_before_gate', g.C_phases_before_gate
                        #print 'dec_duration', g.dec_duration
                        #print 'C_freq', C_freq
                        #print 'iC',iC
                        if g.el_state_before_gate == '0':
                            g.C_phases_after_gate[iC] = (g.C_phases_before_gate[iC]+ g.dec_duration*C_freq_0[iC])%(2*np.pi)
                        elif g.el_state_before_gate == '1':
                            g.C_phases_after_gate[iC] = (g.C_phases_before_gate[iC]+ g.dec_duration*C_freq_1[iC])%(2*np.pi)
                        else:
                            g.C_phases_after_gate[iC] = (g.C_phases_before_gate[iC]+ g.dec_duration*C_freq[iC])%(2*np.pi)
                # if 'Tomo_y_pi2_in' in g.name:
                #     print g.name, g.C_phases_before_gate[iC],g.C_phases_after_gate[iC],g.dec_duration 
            #########
            # Special elements
            #########

            elif g.Gate_type =='passive_elt' or g.Gate_type =='RF_pulse': #MB: added RF pulse temporary, now RF pulses cant be phase tracked

                for iC in range(len(g.C_phases_before_gate)):
                    if (g.C_phases_after_gate[iC] == None) and (g.C_phases_before_gate[iC] !=None):
                        if g.el_state_before_gate == '0':
                            # print 'Calculating phase for gate %s for el_state == 0' %g.name
                            g.C_phases_after_gate[iC] = (g.C_phases_before_gate[iC] + g.wait_time*C_freq_0[iC])%(2*np.pi)
                        elif g.el_state_before_gate == '1':
                            # print 'Carbon ',iC
                            # print 'Calculating phase for gate %s for el_state == 1' %g.name
                            # print 'Phase before: ', g.C_phases_before_gate[iC]
                            # print g.wait_time
                            g.C_phases_after_gate[iC] = (g.C_phases_before_gate[iC] + g.wait_time*C_freq_1[iC])%(2*np.pi)
                            # print 'Phase without taking the modulus: ',(g.C_phases_before_gate[iC] + g.wait_time*C_freq_1[iC])
                            # print 'Phase after: ',g.C_phases_after_gate[iC]
                        elif g.el_state_before_gate == 'sup':
                            g.C_phases_after_gate[iC] = (g.C_phases_before_gate[iC])%(2*np.pi)
                            # print 'Warning: %s, el state in sup for passive elt' %g.name

            elif g.Gate_type=='Trigger':
                for iC in range(len(g.C_phases_before_gate)):
                    if (g.C_phases_after_gate[iC] == None) and (g.C_phases_before_gate[iC] !=None):
                        if g.el_state_before_gate == '0':# and g.C_phases_after_gate[iC]!=None:
                            # print 'Calculating phase for gate %s for el_state == 0 ' %g.name
                            g.C_phases_after_gate[iC] = (g.C_phases_before_gate[iC] + g.elements_duration*C_freq_0[iC])%(2*np.pi)
                        elif g.el_state_before_gate == '1':
                            # print 'Calculating phase for gate %s for el_state == 1 ' %g.name
                            g.C_phases_after_gate[iC] = (g.C_phases_before_gate[iC] + g.elements_duration*C_freq_1[iC])%(2*np.pi)
                        elif g.el_state_before_gate == 'sup':
                            g.C_phases_before_gate[iC]%(2*np.pi)
                            print 'Warning: %s, el state in sup for Trigger elt' %g.name
                            # raise ValueError('El state is in sup during trigger. makes no sense!')

            elif g.Gate_type =='MBI':
                for iC in range(len(g.C_phases_before_gate)):
                    # The MBI element is always first and should not have anything to do with C_phases
                    if g.C_phases_after_gate[iC] ==None:
                        g.C_phases_after_gate[iC] = g.C_phases_before_gate[iC]

            elif g.Gate_type == 'Transfer_element':
                for iC in range(len(g.C_phases_before_gate)):
                    # This element needs to be calibrated before an experiment
                    extra_transfer_phase = [0]*20
                    extra_transfer_phase[2]= (0*np.pi)/180
                    extra_transfer_phase[4]= ((5.4)*np.pi)/180
                    # print g.C_phases_before_gate[iC],g.C_phases_after_gate[iC] 
                    
                    if g.C_phases_before_gate[iC]!=None:
                        g.C_phases_after_gate[iC] = (g.C_phases_before_gate[iC] + extra_transfer_phase[iC])%(2*np.pi)

            elif g.Gate_type =='LDE':
                self.load_extra_phase_correction_lists(g)

                # print g.el_state_after_gate
                for iC in range(len(g.C_phases_before_gate)):
                    if g.C_phases_before_gate[iC] != None:
                        # print "repump_duration {:.2}, t {:.2}, duration_initial {:.2}, t_rep {:.2}, AOM_delay {:.2}".format(g.repump_duration,g.t,g.duration_initial,g.t_rep,g.AOM_delay) 
                        if Gate_sequence[i-1].Gate_type == 'LDE':
                            g.C_phases_after_gate[iC] = (g.C_phases_before_gate[iC] + g.LDE_phase_correction_list[iC]*(g.reps))%(2*np.pi)
                        else:    
                            g.C_phases_after_gate[iC] = (g.C_phases_before_gate[iC] + g.LDE_phase_correction_list_init[iC]+g.LDE_phase_correction_list[iC]*(g.reps))%(2*np.pi)                

            elif g.Gate_type == 'single_element':
                pass


            else: # I want the program to spit out an error if I messed up i.e. forgot a gate type
                print 'Error: %s, Gate type not recognized %s' %(g.name,g.Gate_type)
        
        # for g in Gate_sequence:
        #     if 'inal' in g.name:
        #         print g.name, 
        #         print 'before',g.C_phases_before_gate[4]
        #         print 'after',g.C_phases_after_gate[4]
        # if hasattr(g,'scheme'):
        #     print 'scheeeeme'
        #     if g.scheme == 'carbon_phase_feedback':
        #         print g.name,g.reps,g.C_phases_after_gate[4],g.C_phases_before_gate[4]  

        return Gate_sequence

    ### functions for making the composite elements
    def generate_MBI_elt(self,Gate):
        '''
        adds MBI_element to Gate object
        '''
        Gate.scheme = 'mbi'
        Gate.event_jump='next'
        Gate.go_to = 'self'
        Gate.elements = [self._MBI_element(Gate.prefix)]
        Gate.elements_duration = 0 # Clock should start counting at start of the next element

    def generate_trigger_elt(self,Gate):
        '''
        adds trigger element to Gate object
        '''
        Gate.scheme ='trigger'

        #implement output of the awg on a laser channel.
        if hasattr(Gate,'channel'):
            Gate.elements = [self._Trigger_element(Gate.elements_duration,Gate.prefix,outputChannel=Gate.channel)]
        else:
            if Gate.wait_time!= None:
                Gate.elements_duration = Gate.wait_time
            else:
                Gate.elements_duration = 10e-6
            Gate.elements = [self._Trigger_element(Gate.elements_duration,Gate.prefix)]

    def generate_decoupling_sequence_elements(self,Gate):
        '''
        This function takes a carbon (decoupling) gate as input, the gate must have tau and
        N as paramters. It returns the object with the parameters relevant
        to make an AWG sequence added to it.
        These are: the AWG_elements, the number of repetitions N,
        number of wait reps n,  tau_cut and the total sequence time
        scheme selects the decoupling scheme
        '''
        #TODO_THT: for single elements add that if multiple of 2 the last pulses are XX instead of XY
        tau       = Gate.tau
        N         = Gate.N
        
        prefix    = Gate.prefix

        if self.params['multiple_source']:
            if Gate.specific_transition != None:
                #print 'I am putting the transition of this gate to this',Gate.name,Gate.specific_transition
                self.params['electron_transition']=Gate.specific_transition
                if self.params['electron_transition'] == '_m1':
                    self.params['fast_pi_duration']=self.params['mw2_fast_pi_duration']
                    self.params['fast_pi2_duration']=self.params['mw2_fast_pi2_duration']
                if self.params['electron_transition'] == '_p1':
                    self.params['fast_pi_duration']=self.params['mw1_fast_pi_duration']
                    self.params['fast_pi2_duration']=self.params['mw1_fast_pi2_duration']
            
            elif Gate.Carbon_ind!=0:                
                self.params['electron_transition_used']=self.params['C'+str(Gate.Carbon_ind)+'_dec_trans']
                self.params['electron_transition']=self.params['electron_transition_used']
                #print 'I am putting the transition of this gate to this using carbon ind',Gate.name,Gate.specific_transition
                if self.params['C'+str(Gate.Carbon_ind)+'_dec_trans'] == '_m1':
                    self.params['fast_pi_duration']=self.params['mw2_fast_pi_duration']
                    self.params['fast_pi2_duration']=self.params['mw2_fast_pi2_duration']
                if self.params['C'+str(Gate.Carbon_ind)+'_dec_trans'] == '_p1':
                    self.params['fast_pi_duration']=self.params['mw1_fast_pi_duration']
                    self.params['fast_pi2_duration']=self.params['mw1_fast_pi2_duration']

        ### Generate the basic X and Y pulses
        X = self._X_elt()
        Y = self._Y_elt()
        mX = self._mX_elt()
        mY = self._mY_elt()


        ### Select scheme for generating decoupling elements
        if N==0 or Gate.scheme =='auto':
            Gate = self.determine_decoupling_scheme(Gate)

        ###################
        ## Set paramters ##
        ###################

        tau_cut                 = 0             #initial value unless overwritten
        minimum_AWG_elementsize = 1e-6          #AWG elements/waveforms have to be 1 mu s
        fast_pi_duration        = self.params['fast_pi_duration'] # TODO make this depend on the X/Y_pi_pulse length ()for example from self._X_elt()
        pulse_tau               = tau - fast_pi_duration/2.0
        tau_prnt                = int(tau*1e9)  #Converts tau to ns for printing
        # if np.mod(tau_prnt,4)!=0:
        #     print 'TAU_PRNT NOT MOD 4 ns!!'
        #     print 'current tau = ', tau
        n_wait_reps             = 0             #this is the default value. Script returns this unless overwritten (as is the case for tau>2e-6)

        ### Initial checks to see if sequence is possible
        if (N%2!=0) and (tau <= 2e-6):
            print 'Error: odd number of pulses, impossible to do decoupling control sequence'

        if pulse_tau<0:
            print 'Error: tau is smaller than pi-pulse duration. Cannot generate decoupling element'
            return

        #elif tau <0.5e-6:
        #    print '''Error: total element duration smaller than 1 mu s.
        #    Requires more coding to implement
        #    '''
        #    return

        #################################
        ## Genereate the pulse elements #
        #################################

        list_of_elements = []

        ###########################
        ### Single Block Scheme ###
        ###########################

        if Gate.scheme == 'single_block':
            # print 'using single block'

            tau_cut = 0
            Gate.reps = 1

            if self.params['Initial_Pulse'] =='-x':
                initial_phase = self.params['X_phase']+180
            else:
                initial_phase = self.params['X_phase']

            if self.params['Final_Pulse'] =='-x':
                final_phase   = self.params['X_phase']+180
            else:
                final_phase = self.params['X_phase']

            pulse_tau_pi2 = tau - self.params['fast_pi2_duration']/2.0-self.params['fast_pi_duration']/2.0
            if pulse_tau_pi2 < 31e-9:
                print 'tau too short !!!, tau = ' +str(tau) +'min tau = ' +str(self.params['fast_pi2_duration']/2.0-self.params['fast_pi_duration']/2.0+30e-9)

            if self.params['Initial_Pulse'] == '-x':
                initial_pulse = self._mpi2_elt()
            else:
                initial_pulse = self._pi2_elt()

            if self.params['Final_Pulse'] == '-x':
                final_pulse = self._mpi2_elt()
            else:
                final_pulse = self._pi2_elt()


            T_around_pi2    = pulse.SquarePulse(channel='MW_Imod', name='Wait: tau_pi2',
                length      = pulse_tau_pi2, amplitude = 0.)
            T = pulse.SquarePulse(channel='MW_Imod', name='Wait: tau',
                length      = pulse_tau, amplitude = 0.)

            x_list = [0,2,5,7]

            decoupling_elt = element.Element('Single_%s _DD_elt_tau_%s_N_%s' %(prefix,tau_prnt,N),
                    pulsar = qt.pulsar, global_time=True)
            
            decoupling_elt.append(T_around_pi2)
            decoupling_elt.append(initial_pulse)
            decoupling_elt.append(T_around_pi2)
            for n in range(N-1) :
                if n !=0:
                    decoupling_elt.append(T)
                if n%8 in x_list:
                    decoupling_elt.append(X)
                else:
                    decoupling_elt.append(Y)
                if n !=N-1:
                    decoupling_elt.append(T)

            # ### append the final pulse
            if N%8 == 2:
                final_pi_pulse = mX
                P_type = 'mX'
                print 'yes, we ate 2 pulses with mX!'
            elif N%8 in [3,4,5]:
                final_pi_pulse = Y
                P_type = 'Y'
                # final_pi_pulse = X
                # P_type = 'X'
            elif N%8 == 6:
                final_pi_pulse = mY
                P_type = 'mY'
            elif N%8 in [0,1,7]:
                final_pi_pulse = X
                P_type = 'X'

            decoupling_elt.append(T)
            decoupling_elt.append(final_pi_pulse)


            ## finish off with a pi/2 pulse.

            decoupling_elt.append(T_around_pi2)
            decoupling_elt.append(final_pulse)
            decoupling_elt.append(T_around_pi2)
            list_of_elements.append(decoupling_elt)

        elif 'single_block_repeating_elements' in Gate.scheme:
            '''MAB:4-5-15 
            Made to repeat one single eleemnt of X, XY, XY4, xY8 or XY16 in one element
            Gate.N has to be 1,2,4,8 or 16
            Pulse sequences with N>16 can be constructed with Gate.reps
            ''' 
            # ### Correct for part that is cut off when combining to sequence
            # if n_wait_reps %2 == 0:
            #     tau_cut = 1e-6
            # else:
            #     tau_cut = 1.5e-6

            tau_cut = 1e-6
            Gate.tau_cut = 1e-6
            pulse_tau_pi2 = tau - self.params['fast_pi2_duration']/2.0-self.params['fast_pi_duration']/2.0

            if pulse_tau_pi2 < 31e-9:
                print 'tau too short !!!, tau = ' +str(tau) +'min tau = ' +str(self.params['fast_pi2_duration']/2.0-self.params['fast_pi_duration']/2.0+30e-9)

            T_around_pi2    = pulse.SquarePulse(channel='MW_Imod', name='Wait: tau_pi2',
                length      = pulse_tau_pi2, amplitude = 0.)
            T = pulse.SquarePulse(channel='MW_Imod', name='Wait: tau',
                length      = pulse_tau, amplitude = 0.)
            T_twice = pulse.SquarePulse(channel='MW_Imod', name='Wait: tau',
                length      = pulse_tau*2., amplitude = 0.)

            T_out = pulse.SquarePulse(channel='MW_Imod', name='Wait: tau',
                length      = 5e-6-self.params['fast_pi2_duration']/2.0, amplitude = 0.)

            x_list = [0,2,5,7]
            y_list = [1,3,4,6]
            mx_list = [8,10,13,15]
            my_list = [9,11,12,14]

            decoupling_elt = element.Element('Single_%s _DD_elt_tau_%s_N_%s' %(prefix,tau_prnt,N),
                    pulsar = qt.pulsar, global_time=True)
            
            if 'start' in Gate.scheme: 
                if self.params['Initial_Pulse'] == '-x':

                    initial_phase = self.params['X_phase']+180 
                    initial_pulse = self._mpi2_elt()
                else:
                    initial_phase = self.params['X_phase']
                    initial_pulse = self.pi2_elt()
                    

                decoupling_elt.append(T_out)
                decoupling_elt.append(pulse.cp(initial_pulse))
                decoupling_elt.append(T_around_pi2)
            
            if N not in [1,2,4,8,16]:
                raise Exception('Gate.N has to be 1,2,4,8 or 16 and then repeated by Gate.reps')
            print N
            
            for n in range(N):
                if ('end' in Gate.scheme or 'middle' in Gate.scheme) and n==0:
                    decoupling_elt.append(T)
                elif n != 0:
                    decoupling_elt.append(T_twice)

                if n%16 in x_list:
                    decoupling_elt.append(pulse.cp(X))
                    # print 'X'
                elif n%16 in y_list:
                    decoupling_elt.append(pulse.cp(Y))
                    # print 'Y'
                elif n%16 in mx_list:
                    decoupling_elt.append(pulse.cp(mX))
                    # print 'mX'
                elif n%16 in my_list:
                    decoupling_elt.append(pulse.cp(mY))
                    # print 'mY'
                else:
                    raise Exception('Error in pulse sequence')

                if ('start' in Gate.scheme or 'middle' in Gate.scheme) and n==N-1:
                    decoupling_elt.append(T)

            ### finish off with a pi/2 pulse.
            if 'end' in Gate.scheme: 
                if self.params['Final_Pulse'] == '-x':
                    final_pulse = self._mpi2_elt()
                else:
                    final_pulse = self.pi2_elt()
                decoupling_elt.append(T_around_pi2)
                decoupling_elt.append(pulse.cp(final_pulse))
                decoupling_elt.append(T_out)

            list_of_elements.append(decoupling_elt)
        ################################
        ### XYn with repeating T elt ###
        ################################
        elif Gate.scheme == 'repeating_T_elt':

            Gate.reps = N # Overwrites reps parameter that is used in sequencing 
            ### Calculate durations
            

            n_wait_reps, tau_remaind = divmod(round(2*pulse_tau*1e9),1e3) #multiplying and round is to prevent rounding errors in divmod
            tau_remaind              = tau_remaind*1e-9
            # print 'pulse_tau in us = ',  pulse_tau*1e6
            # print 'n_wait_reps = ', n_wait_reps
            if tau_remaind/2. < X.risetime: ## The tau_remaind calculation now depends on the overall risetime of the pulse. NK 20150323
            # NOTE: with MW switch (risetime = 500 ns) pulse_tau must be longer than (2.5 + fast_pi_duration/2) us, otherwise: n_wait_reps = 4 - 4 = 0 --> red_wait_reps = 0 --> AWG cannot program 0 element repetitions
                ''' to make sure that the time before the pulse is not shorther than the pulse mod'''
                n_wait_reps              = n_wait_reps -4
                tau_shortened            = tau_remaind/2.0 + 1e-6
                t_around_pulse           = 2e-6 + tau_remaind/2.0
            else:
                n_wait_reps              = n_wait_reps -2
                tau_shortened            = tau_remaind/2.0
                t_around_pulse           = 1e-6 + tau_remaind/2.0


            Tus =pulse.SquarePulse(channel='MW_Imod', name='Wait: tau',
                length = 1e-6, amplitude = 0.)
            T = pulse.SquarePulse(channel='MW_Imod', name='Wait: tau',
                length = t_around_pulse, amplitude = 0.)
            T_shortened = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = tau_shortened, amplitude = 0.)

            ### Correct for part that is cut off when combining to sequence
            if n_wait_reps %2 == 0:
                tau_cut = 1e-6
            else:
                tau_cut = 1.5e-6

            ### Combine the pulses to elements/waveforms and add to list of elements
            e_X_start = element.Element('%s_X_Initial_DD_El_tau_N_ %s_%s' %(prefix,tau_prnt,N),  pulsar=qt.pulsar,
                    global_time = True)
            e_X_start.append(T_shortened)

            e_X_start.append(pulse.cp(X))
            e_X_start.append(T)
            list_of_elements.append(e_X_start)

            e_X =  element.Element('%s_X_Rep_DD_El_tau_N_ %s_%s' %(prefix,tau_prnt,N),  pulsar=qt.pulsar,
                    global_time = True)
            e_X.append(T)
            e_X.append(pulse.cp(X))
            e_X.append(T)
            list_of_elements.append(e_X)

            e_Y =  element.Element('%s_Y_Rep_DD_El_tau_N_ %s_%s' %(prefix,tau_prnt,N),  pulsar=qt.pulsar,
                    global_time = True)
            e_Y.append(T)
            e_Y.append(pulse.cp(Y))

            e_Y.append(T)
            list_of_elements.append(e_Y)

            # commented out because XX rotations lower the fidelity of the electron state RO.
            # NK & THT 01.12.2014
            # final_x_list = [0,1,2,7]
            # if N%8 in final_x_list:
            #     final_pulse = X
            #     P_type = 'X'
            # else:
            #     final_pulse = Y
                # P_type = 'Y'

            if N%8 == 2:
                final_pulse = pulse.cp(mX)
                P_type = 'mX'
            elif N%8 in [3,4,5]:
                final_pulse = Y
                P_type = 'Y'
            elif N%8 == 6:
                final_pulse = mY
                P_type = 'mY'
            elif N%8 in [0,1,7]:
                final_pulse = X
                P_type = 'X'


            e_end = element.Element('%s_%s_Final_DD_El_tau_N_%s_%s' %(prefix,P_type,tau_prnt,N),  pulsar=qt.pulsar,
                    global_time = True)
            e_end.append(T)
            e_end.append(pulse.cp(final_pulse))
            e_end.append(T_shortened)
            list_of_elements.append(e_end)

            T_us_rep = element.Element('%s_Rep_elt_DD_tau_%s_N_%s'%(prefix,tau_prnt,N),pulsar=qt.pulsar, global_time =True)
            T_us_rep.append(Tus)
            list_of_elements.append(T_us_rep)

        elif Gate.scheme == 'repeating_T_elt_XY16':
            Gate.reps = N # Overwrites reps parameter that is used in sequencing 
            ### MAB 010615
            # Similar to repeating_T_elt but now also supporting XY16

            n_wait_reps, tau_remaind = divmod(round(2*pulse_tau*1e9),1e3) #multiplying and round is to prevent rounding errors in divmod
            tau_remaind              = tau_remaind*1e-9

            if tau_remaind/2. < X.risetime: ## The tau_remaind calculation now depends on the overall risetime of the pulse. NK 20150323
                ''' to make sure that the time before the pulse is not shorther than the pulse mod'''
                n_wait_reps              = n_wait_reps -4
                tau_shortened            = tau_remaind/2.0 + 1e-6
                t_around_pulse           = 2e-6 + tau_remaind/2.0
            else:
                n_wait_reps              = n_wait_reps -2
                tau_shortened            = tau_remaind/2.0
                t_around_pulse           = 1e-6 + tau_remaind/2.0


            Tus =pulse.SquarePulse(channel='MW_Imod', name='Wait: tau',
                length = 1e-6, amplitude = 0.)
            T = pulse.SquarePulse(channel='MW_Imod', name='Wait: tau',
                length = t_around_pulse, amplitude = 0.)
            T_shortened = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = tau_shortened, amplitude = 0.)

            ### Correct for part that is cut off when combining to sequence
            if n_wait_reps %2 == 0:
                tau_cut = 1e-6
            else:
                tau_cut = 1.5e-6

            ### Combine the pulses to elements/waveforms and add to list of elements
            e_X_start = element.Element('%s_X_Initial_DD_El_tau_N_ %s_%s' %(prefix,tau_prnt,N),  pulsar=qt.pulsar,
                    global_time = True)
            e_X_start.append(T_shortened)
            e_X_start.append(pulse.cp(X))
            e_X_start.append(T)
            list_of_elements.append(e_X_start)

            e_X =  element.Element('%s_X_Rep_DD_El_tau_N_ %s_%s' %(prefix,tau_prnt,N),  pulsar=qt.pulsar,
                    global_time = True)
            e_X.append(T)
            e_X.append(pulse.cp(X))
            e_X.append(T)
            list_of_elements.append(e_X)

            e_Y =  element.Element('%s_Y_Rep_DD_El_tau_N_ %s_%s' %(prefix,tau_prnt,N),  pulsar=qt.pulsar,
                    global_time = True)
            e_Y.append(T)
            e_Y.append(pulse.cp(Y))
            e_Y.append(T)
            list_of_elements.append(e_Y)

            e_mX =  element.Element('%s_mX_Rep_DD_El_tau_N_ %s_%s' %(prefix,tau_prnt,N),  pulsar=qt.pulsar,
                    global_time = True)
            e_mX.append(T)
            e_mX.append(pulse.cp(mX))
            e_mX.append(T)
            list_of_elements.append(e_mX)

            e_mY =  element.Element('%s_mY_Rep_DD_El_tau_N_ %s_%s' %(prefix,tau_prnt,N),  pulsar=qt.pulsar,
                    global_time = True)
            e_mY.append(T)
            e_mY.append(pulse.cp(mY))
            e_mY.append(T)
            list_of_elements.append(e_mY)

            if N%8 == 2:
                final_pulse = mX
                P_type = 'mX'
            elif N%8 in [3,4,5]:
                final_pulse = Y
                P_type = 'Y'
            elif N%8 == 6:
                final_pulse = mY
                P_type = 'mY'
            elif N%8 in [0,1,7]:
                final_pulse = X
                P_type = 'X'


            e_end = element.Element('%s_%s_Final_DD_El_tau_N_%s_%s' %(prefix,P_type,tau_prnt,N),  pulsar=qt.pulsar,
                    global_time = True)
            e_end.append(T)
            e_end.append(pulse.cp(final_pulse))
            e_end.append(T_shortened)
            list_of_elements.append(e_end)

            T_us_rep = element.Element('%s_Rep_elt_DD_tau_%s_N_%s'%(prefix,tau_prnt,N),pulsar=qt.pulsar, global_time =True)
            T_us_rep.append(Tus)
            list_of_elements.append(T_us_rep)


        elif Gate.scheme == 'XY8':
            # print 'Using non-repeating delay elements XY8 decoupling method'
            Gate.reps = N # Overwrites reps parameter that is used in sequencing 
            ###########
            ### XY8 ###
            ###########

            element_duration_without_edge = 3*tau + fast_pi_duration/2.0
            if element_duration_without_edge  > (minimum_AWG_elementsize+36e-9): #+20 ns is to make sure that elements always have a minimal size
                tau_shortened = np.ceil((element_duration_without_edge+ 36e-9)/4e-9)*4e-9 -element_duration_without_edge
            else:
                tau_shortened = minimum_AWG_elementsize - element_duration_without_edge
                tau_shortened = np.ceil(tau_shortened/(4e-9))*(4e-9)
            tau_cut = tau - tau_shortened - fast_pi_duration/2.0

            ### Make the delay pulses
            T = pulse.SquarePulse(channel='MW_Imod', name='Wait: tau',
                length = pulse_tau, amplitude = 0.)
            T_before_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = tau_shortened, amplitude = 0.)
            T_after_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = tau_shortened, amplitude = 0.)

            ### Combine pulses to elements/waveforms and add to list of elements
            e_XY_start = element.Element('%s_XY_Init_XY8-DD_El_tau_N_%s_%s' %(prefix,tau_prnt,N),  pulsar=qt.pulsar,
                    global_time = True)
            e_XY_start.append(T_before_p)
            e_XY_start.append(pulse.cp(X))
            e_XY_start.append(T)
            e_XY_start.append(T)
            e_XY_start.append(pulse.cp(Y))
            e_XY_start.append(T)
            list_of_elements.append(e_XY_start)

            e_XY = element.Element('%s_XY_Rep_XY8-DD_El_tau_N_%s_%s' %(prefix,tau_prnt,N),  pulsar=qt.pulsar,
                    global_time = True)
            e_XY.append(T)
            e_XY.append(pulse.cp(X))
            e_XY.append(T)
            e_XY.append(T)
            e_XY.append(pulse.cp(Y))
            e_XY.append(T)
            list_of_elements.append(e_XY)

            e_YX = element.Element('%s_YX_Rep_XY8-DD_El_tau_N_%s_%s' %(prefix,tau_prnt,N),  pulsar=qt.pulsar,
                    global_time = True)
            e_YX.append(T)
            e_YX.append(pulse.cp(Y))
            e_YX.append(T)
            e_YX.append(T)
            e_YX.append(pulse.cp(X))
            e_YX.append(T)
            list_of_elements.append(e_YX)

            e_YX_end = element.Element('%s_YX_Final_XY-8 DD_El_tau_N_ %s_%s' %(prefix,tau_prnt,N),  pulsar=qt.pulsar,
                    global_time = True)
            e_YX_end.append(T)
            e_YX_end.append(pulse.cp(Y))
            e_YX_end.append(T)
            e_YX_end.append(T)
            e_YX_end.append(pulse.cp(X))
            e_YX_end.append(T_after_p)
            list_of_elements.append(e_YX_end)

        elif Gate.scheme == 'XY4':
            # print 'Using non-repeating delay elements XY4 decoupling method'
            Gate.reps = N # Overwrites reps parameter that is used in sequencing 
            ###########
            ### XY4 ###
            ###########
            element_duration_without_edge = tau + fast_pi_duration/2.0
            if element_duration_without_edge  > (minimum_AWG_elementsize+36e-9): #+20 ns is to make sure that elements always have a minimal size
                tau_shortened = np.ceil((element_duration_without_edge+ 36e-9)/4e-9)*4e-9 -element_duration_without_edge
            else:
                tau_shortened = minimum_AWG_elementsize - element_duration_without_edge
                tau_shortened = np.ceil(tau_shortened/(4e-9))*(4e-9)
            tau_cut = tau - tau_shortened - fast_pi_duration/2.0

            T = pulse.SquarePulse(channel='MW_Imod', name='Wait: tau',
                length = pulse_tau, amplitude = 0.)
            T_before_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = tau_shortened, amplitude = 0.) #the unit waittime is 10e-6 s
            T_after_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = tau_shortened, amplitude = 0.) #the length of this time should depends on the pi-pulse length/.

            ### Combine pulses to elements/waveforms and add to list of elements
            e_start = element.Element('%s_X_Initial_DD_El_tau_N_ %s_%s' %(prefix,tau_prnt,N),  pulsar=qt.pulsar,
                    global_time = True)
            e_start.append(T_before_p)
            e_start.append(pulse.cp(X))
            e_start.append(T)
            list_of_elements.append(e_start)
            ### Currently middle is XY2 with an if statement based on the value of N this can be optimised
            e_middle = element.Element('%s_YX_Rep_DD_El_tau_N_ %s_%s' %(prefix,tau_prnt,N),  pulsar=qt.pulsar,
                    global_time = True)
            e_middle.append(T)
            e_middle.append(pulse.cp(Y))
            e_middle.append(T)
            e_middle.append(T)
            e_middle.append(pulse.cp(X))
            e_middle.append(T)
            list_of_elements.append(e_middle)
            e_end = element.Element('%s_Y_Final_DD_El_tau_N_ %s_%s' %(prefix,tau_prnt,N),  pulsar=qt.pulsar,
                    global_time = True)
            e_end.append(T)
            e_end.append(pulse.cp(Y))
            e_end.append(T_after_p)
            list_of_elements.append(e_end)

        elif Gate.scheme == 'NO_Pulses':
            ############################
            ### Calibration NO Pulse ###
            ############################
            '''
            Pulse scheme specifically created for calibration
            Applies no pulses but instead waits for 1us
            '''
            Gate.reps = N # Overwrites reps parameter that is used in sequencing 
            T = pulse.SquarePulse(channel='MW_Imod', name='Wait: tau',
                length = 1e-6, amplitude = 0.)
            wait = element.Element('%s_NO_Pulse' %(prefix),  pulsar=qt.pulsar,
                    global_time = True)
            wait.append(T)
            list_of_elements.append(wait)

        elif 'carbon_phase_feedback' in Gate.scheme:

            '''

            Special decoupling sequence that provides adwin-controlled adaptive phase gates on carbons.
            
            These gates make use of an attribute called: Gate.no_connection_elt.
            If true then this attribute hinders the automatic insertion of carbon phase gates.
            
            Needs the definition of two consecutive gates to function properly.
            First gate (Gate.scheme contains carbon_phase_feedback): 
                decouple in sets of N pulses on the larmor revival. We employ XY8. 
                Has repetitions according to g.reps.
                Gives an adwin trigger for every repetition. 
                Idea: The adwin counts the carbon phase and jumps out of this element as soon as the right time has elapsed.
            Second element (Gate.scheme also contains 'end'):
                is repeated once 
                has one X pulse with the same timing.
                has tau_cut of 1e-6 such that the follow up pi/2 pulse comes in on an echo

            NOTE: DOES NOT CONTAIN pi/2 PULSES
            NK 2016-03-22
            ''' 
            # ### Correct for part that is cut off when combining to sequence

            # Gate.no_connection_elt = True
            tau_cut = 1e-6
            Gate.tau_cut = 1e-6

            T = pulse.SquarePulse(channel='MW_Imod', name='Wait: tau',
                length      = pulse_tau, amplitude = 0.)
            T_twice = pulse.SquarePulse(channel='MW_Imod', name='Wait: tau',
                length      = pulse_tau*2., amplitude = 0.)

            T_out = pulse.SquarePulse(channel='MW_Imod', name='Wait: tau',
                length      = pulse_tau-tau_cut, amplitude = 0.)

            x_list = [0,2,5,7]
            y_list = [1,3,4,6]
            mx_list = [8,10,13,15]
            my_list = [9,11,12,14]

            decoupling_elt = element.Element('Single_%s_DD_elt_tau_%s_N_%s' %(prefix,tau_prnt,N),
                    pulsar = qt.pulsar, global_time=True)

            if N not in [1,2,4,8,16]:
                raise Exception('Gate.N has to be 1,2,4,8 or 16 and then repeated by Gate.reps')

            if 'start' in Gate.scheme:
                decoupling_elt.append(T_out)
            else:
                decoupling_elt.append(T)  

            for n in range(N-1):

                if n != 0:
                    decoupling_elt.append(T)

                if n%16 in x_list:
                    decoupling_elt.append(pulse.cp(X))
                    # print 'X'
                elif n%16 in y_list:
                    decoupling_elt.append(pulse.cp(Y))
                    # print 'Y'
                elif n%16 in mx_list:
                    decoupling_elt.append(pulse.cp(mX))
                    # print 'mX'
                elif n%16 in my_list:
                    decoupling_elt.append(pulse.cp(mY))
                    # print 'mY'
                else:
                    raise Exception('Error in pulse sequence')

                decoupling_elt.append(T_twice)


            #### need to adapt for final pulse and the number of pulses
            if N%8 == 2:
                final_pulse = Y
                P_type = 'Y'
            elif N%8 in [3,4,5]:
                final_pulse = Y
                P_type = 'Y'
            elif N%8 == 6:
                final_pulse = mY
                P_type = 'mY'
            elif N%8 in [0,1,7]:
                final_pulse = X
                P_type = 'X'

            decoupling_elt.append(pulse.cp(final_pulse))

            if (not 'end' in Gate.scheme):
                decoupling_elt.append(T)
                adwin_sync =  pulse.SquarePulse(channel='adwin_count', name='adwin_sync_counter',
                    length = 2.5e-6, amplitude = 2)
                decoupling_elt.add(adwin_sync,start=2000e-9)
            else:
                decoupling_elt.append(T_out)  


                


            list_of_elements.append(decoupling_elt)
        
        else:
            print 'Scheme = '+Gate.scheme
            print 'Error!: selected scheme does not exist for generating decoupling elements.'

            return

        ########################################################
        ### adding all the relevant parameters to the object ###
        ########################################################

        Gate.elements = list_of_elements
        if N == 0: #in order to correctly calc evolution time for 0 pulses case
            Gate.elements_duration = 1e-6
        else:
            Gate.elements_duration = 2*tau*N - 2* tau_cut
        Gate.n_wait_reps= n_wait_reps
        # print here
        Gate.tau_cut = tau_cut #is 0 when not overwritten (i.e. N=0)
        return Gate

    def generate_passive_wait_element(self,g):
        '''
        a 1us wait element that is repeated a lot of times
        Because there are connection elts on both sides of the wait gates the minimum duration
        of the wait is 3us.
        This is because tau cut is 1e-6 on both sides.
        This condition could be defined stricter when going trough all the files
        '''
        duration = 1e-6
        if g.wait_time<3e-6:
            print 'Error: g.wait_time of %s is smaller than 3e-6 for passive wait element' %g.name

        n_wait_reps, tau_remaind = divmod(round(g.wait_time*1e9),duration*1e9) #Rounding to ns
        while n_wait_reps > 50000: #allows for longer durations than max reps in AWG
            duration = duration *10
            n_wait_reps, tau_remaind = divmod(round(g.wait_time*1e9),duration*1e9)

        tau_remaind = tau_remaind *1e-9 #convert back to seconds
        g.reps = n_wait_reps -2
        g.tau_cut = duration + tau_remaind/2.0
        T = pulse.SquarePulse(channel='MW_Imod', name='Wait: tau',
                length = duration, amplitude = 0.)
        rep_wait_elt = element.Element('%s' %(g.prefix), pulsar = qt.pulsar, global_time=True)
        rep_wait_elt.append(T)

        g.elements = [rep_wait_elt]
        g.elements_duration = duration *g.reps

    def generate_connection_element(self,Gate):
        '''
        Creates a single element that does only decoupling
        requires Gate to have the following attributes
        N, prefix, tau, tau_cut_before, tau_cut_after
        Function also works for N =0
        '''

        N       = Gate.N
        prefix  = Gate.prefix

        tau     = Gate.tau

        tau_prnt= int(tau*1e9)
        tau_cut_before  = Gate.tau_cut_before
        tau_cut_after   = Gate.tau_cut_after

        if self.params['multiple_source']:
            if Gate.specific_transition != None:
                #print 'I am putting the transition of this gate to this',Gate.name,Gate.specific_transition
                self.params['electron_transition']=Gate.specific_transition
                if self.params['electron_transition'] == '_m1':
                    self.params['fast_pi_duration']=self.params['mw2_fast_pi_duration']
                    self.params['fast_pi2_duration']=self.params['mw2_fast_pi2_duration']
                if self.params['electron_transition'] == '_p1':
                    self.params['fast_pi_duration']=self.params['mw1_fast_pi_duration']
                    self.params['fast_pi2_duration']=self.params['mw1_fast_pi2_duration']

            
            elif Gate.Carbon_ind!=0:                
                self.params['electron_transition_used']=self.params['C'+str(Gate.Carbon_ind)+'_dec_trans']
                self.params['electron_transition']=self.params['electron_transition_used']
                #print 'I am putting the transition of this gate to this using carb ind',Gate.name,Gate.specific_transition
                if self.params['C'+str(Gate.Carbon_ind)+'_dec_trans'] == '_m1':
                    self.params['fast_pi_duration']=self.params['mw2_fast_pi_duration']
                    self.params['fast_pi2_duration']=self.params['mw2_fast_pi2_duration']
                if self.params['C'+str(Gate.Carbon_ind)+'_dec_trans'] == '_p1':
                    self.params['fast_pi_duration']=self.params['mw1_fast_pi_duration']
                    self.params['fast_pi2_duration']=self.params['mw1_fast_pi2_duration']


        ### the NV is in an eigenstate before we apply the phase gate add this time as additional waiting.
        if N == 0 and Gate.dec_duration != 0 and Gate.el_state_before_gate in ['0','1']:
            tau_cut_before += Gate.dec_duration

        pulse_tau       = tau-self.params['fast_pi_duration']/2.0

        X = self._X_elt()
        Y = self._Y_elt()
        mX = self._mX_elt()
        mY = self._mY_elt()


        # print '*************'
        # print 'name and el state before',Gate.name,Gate.el_state_before_gate, Gate.el_state_after_gate
        # print 'dec duration',Gate.dec_duration
        # print 'tau and N', tau, N

        T = pulse.SquarePulse(channel='MW_Imod', name='Wait: tau',
            length = pulse_tau, amplitude = 0.)
        T_final = pulse.SquarePulse(channel='MW_Imod', name='wait fin T',
            length = tau_cut_after, amplitude = 0.)

        if Gate.Gate_type =='electron_Gate':
            #in this an element should be added in before
            if Gate.Gate_operation == 'pi2':
                eP = self._pi2_elt()
            elif Gate.Gate_operation == 'special_pi2': #NOTE: For testing purposes only !!!
                eP = self._spec_pi2_elt()
            elif Gate.Gate_operation == 'pi':
                eP = self._X_elt()
            elif Gate.Gate_operation == 'comp_pi2_pi_pi2':
                eP = self._comp_pi2_pi_pi2_elt()
            elif Gate.Gate_operation == 'general':      ### Added to make possible electron pulses with different amplitudes and phases
                eP = self._electron_pulse_elt(length = Gate.length, amplitude = Gate.amplitude)
            eP.phase = Gate.phase

            T_initial = pulse.SquarePulse(channel='MW_Imod', name='wait in T',
                length = tau_cut_before-(eP.length-2*eP.risetime)/2.0, amplitude = 0.)
            T_dec_initial = pulse.SquarePulse(channel='MW_Imod', name='wait in T',
                length = pulse_tau-(eP.length-2*eP.risetime)/2.0, amplitude = 0.)
        else:
            T_initial = pulse.SquarePulse(channel='MW_Imod', name='wait in T',
                length = tau_cut_before, amplitude = 0.)

        #######################################
        # _______________          :            (____|____)^N_____________
        # |tau_cut_before|(electronPulse)|(|tau|pi|tau|)^N|tau_cut_after|
        #######################################

        decoupling_elt = element.Element('%s_tau_%s_N_%s' %(prefix,tau_prnt,N), pulsar = qt.pulsar, global_time=True)

        if N == 0 and Gate.Gate_type == 'electron_Gate':

            T_final = pulse.SquarePulse(channel='MW_Imod', name='wait fin T',
                length = tau_cut_after-(eP.length-2*eP.risetime)/2.0, amplitude = 0.) #Overwrite length of T_final element
            
            decoupling_elt.append(T_initial)
            decoupling_elt.append(eP)
            decoupling_elt.append(T_final)

        else:
            if Gate.Gate_type == 'electron_Gate':
                decoupling_elt.append(T_initial)
                decoupling_elt.append(eP)
                decoupling_elt.append(T_dec_initial)
            else:
                decoupling_elt.append(T_initial)
                if N != 0:
                    decoupling_elt.append(T) #THT: commented this out, but not sure how it should be

            x_list = [0,2,5,7]


            ### Commented out to allow for phase gates with 'XY-4'-type sequences and  a pulse number N%2=0.
            ### So sequences with 2, 6, 10 etc. pulses are allowed as well.
            ### In this case the last pulse might have to be altered to correct for pulse errors.
            ############################################
            ###     ###
            ### old ###
            ###     ###

            # for n in range(N) :

            #     if n%8 in x_list:
            #         decoupling_elt.append(X)
            #     else:
            #         decoupling_elt.append(Y)
            #     decoupling_elt.append(T)
            #     if n !=(N-1):
            #         decoupling_elt.append(T)
            ##########################################
            ###     ###
            ### new ### 20150324
            ###     ###
            for n in range(N-1) :

                if n%8 in x_list:
                    decoupling_elt.append(X)
                else:
                    decoupling_elt.append(Y)
                decoupling_elt.append(T)
                if n !=(N-1):
                    decoupling_elt.append(T)

            ### determine the type of the final pulse.

            if N%8 == 2:
                final_pulse = mX
            elif N%8 in [3,4,5]:
                final_pulse = Y
            elif N%8 == 6:
                final_pulse = mY
            elif N%8 in [0,1,7]:
                final_pulse = X

            if N!=0:
                decoupling_elt.append(final_pulse)
                decoupling_elt.append(T)

            ##########################################



            decoupling_elt.append(T_final)
        
        Gate.elements = [decoupling_elt]

    def generate_transfer_element(self,Gate,pt=1):
        '''
        Creates a single element that does only the swapping of a superposition of
        the electron state from one transition to specific_transition.
        requires Gate to have the following attributes
        specific_transition,el_state_before_gate,second_pi_phase
        '''
        Gate.scheme = 'LDE'
        prefix=Gate.prefix

        print prefix
        if Gate.specific_transition == self.params['mw1_transition']:
            first_pi = ps.X_pulse(self)            
            second_pi = ps.mw2_X_pulse(self)
            first_mw_duration = self.params['Hermite_pi_length']
            second_mw_duration =self.params['mw2_Hermite_pi_length']
            


        elif Gate.specific_transition==self.params['mw2_transition']:
            first_pi = ps.mw2_X_pulse(self)                
            second_pi = ps.X_pulse(self)
            first_mw_duration = self.params['mw2_Hermite_pi_length']
            second_mw_duration =self.params['Hermite_pi_length']

        else:
            print 'Please select a valid transition for the transfer pulse to start with'

        second_pi.phase=Gate.second_pi_phase #120+36-180 Degrees

        # Gate.delay = self.params['delay']
        
        # tau_cut_before  = self.params['shorten_factor']*Gate.tau_cut_before
        # tau_cut_after   = self.params['shorten_factor']*Gate.tau_cut_after
          
        T_start = pulse.SquarePulse(channel='MW_Imod', name='Wait befor 1st pulse',
            length =3*Gate.delay-first_mw_duration/2, amplitude = 0.)

        T_first = pulse.SquarePulse(channel='MW_Imod', name='wait after 1st pulse',
            length = Gate.delay -(first_mw_duration/2+second_mw_duration/2), amplitude = 0.)

        T_second = pulse.SquarePulse(channel='MW_Imod', name='wait after 2nd pulse',
            length = Gate.delay -(first_mw_duration/2+second_mw_duration/2), amplitude = 0.)

        T_third = pulse.SquarePulse(channel='MW_Imod', name='wait after 3rd pulse',
            length = Gate.delay -(first_mw_duration/2+second_mw_duration/2), amplitude = 0.)

        T_fourth = pulse.SquarePulse(channel='MW_Imod', name='wait after 4th pulse',
            length = 2*Gate.delay -(first_mw_duration/2+first_mw_duration/2), amplitude = 0.)

        T_fifth = pulse.SquarePulse(channel='MW_Imod', name='wait after 5th pulse',
            length = 1*Gate.delay -(second_mw_duration/2), amplitude = 0.)

       

        decoupling_elt = element.Element('%s_transfer_pulse_%s' %(prefix,Gate.specific_transition), pulsar = qt.pulsar, global_time=True)


        # decoupling_elt.append(T_start)
        # decoupling_elt.append(first_pi)
        # decoupling_elt.append(T_delay)
        # decoupling_elt.append(second_pi)
        # decoupling_elt.append(T_final)

        decoupling_elt.append(T_start)
        decoupling_elt.append(first_pi)
        decoupling_elt.append(T_first)
        decoupling_elt.append(second_pi)
        decoupling_elt.append(T_second)
        decoupling_elt.append(first_pi)
        decoupling_elt.append(T_third)
        decoupling_elt.append(second_pi)
        decoupling_elt.append(T_fourth)
        decoupling_elt.append(second_pi)
        decoupling_elt.append(T_fifth)

        Gate.elements = [decoupling_elt]
        Gate.duration = 2*Gate.delay-first_mw_duration/2 + 3*(Gate.delay -(first_mw_duration/2+second_mw_duration/2)) + 2*Gate.delay -(first_mw_duration/2+second_mw_duration/2) 

    def generate_electron_gate_element(self,Gate):
        '''
        Generates an element that connects to decoupling elements
        It can be at the start, the end or between sequence elements
        time_before_pulse,time_after_pulse, Gate_type,prefix,tau,N
        '''
        time_before_pulse = Gate.time_before_pulse
        # print time_before_pulse
        time_after_pulse = Gate.time_after_pulse
        Gate_operation = Gate.Gate_operation
        prefix = Gate.prefix

        if Gate_operation == 'x':
            time_before_pulse = time_before_pulse  -self.params['fast_pi2_duration']/2.0
            time_after_pulse = time_after_pulse  -self.params['fast_pi2_duration']/2.0


            X = self._pi2_elt()

            T_before_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = time_before_pulse, amplitude = 0.)
            T_after_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = time_after_pulse, amplitude = 0.)

            e = element.Element('%s_Pi_2_pulse' %(prefix),  pulsar=qt.pulsar,
                    global_time = True)
            e.append(T_before_p)
            e.append(pulse.cp(X))
            e.append(T_after_p)


        elif Gate_operation == '-x':
            time_before_pulse = time_before_pulse  -self.params['fast_pi2_duration']/2.0
            time_after_pulse = time_after_pulse  -self.params['fast_pi2_duration']/2.0

            X = self._mpi2_elt()

            T_before_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = time_before_pulse, amplitude = 0.)
            T_after_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = time_after_pulse, amplitude = 0.)

            e = element.Element('%s_Pi_2_pulse' %(prefix),  pulsar=qt.pulsar,
                    global_time = True)
            e.append(T_before_p)
            e.append(pulse.cp(X))
            e.append(T_after_p)

        elif Gate_operation == 'pi':
            time_before_pulse = time_before_pulse  -self.params['fast_pi_duration']/2.0
            time_after_pulse = time_after_pulse  -self.params['fast_pi_duration']/2.0

            X = self._X_elt()
            T_before_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = time_before_pulse, amplitude = 0.)
            T_after_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = time_after_pulse, amplitude = 0.)

            e = element.Element('%s_Pi_pulse' %(prefix),  pulsar=qt.pulsar,
                    global_time = True)
            e.append(T_before_p)
            e.append(pulse.cp(X))
            e.append(T_after_p)

        elif Gate_operation == 'no_pulse':
            time_before_pulse = time_before_pulse  -self.params['fast_pi_duration']/2.0
            time_after_pulse = time_after_pulse  -self.params['fast_pi_duration']/2.0

            X = pulselib.MW_IQmod_pulse('electron Pi-pulse',
                I_channel='MW_Imod', Q_channel='MW_Qmod',
                PM_channel='MW_pulsemod', Sw_channel=self.params['MW_switch_channel'],
                frequency = self.params['fast_pi_mod_frq'],
                PM_risetime = self.params['MW_pulse_mod_risetime'],
                Sw_risetime = self.params['MW_switch_risetime'],
                length = self.params['fast_pi_duration'],
                amplitude = 0)
            T_before_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = time_before_pulse+20e-6, amplitude = 0.)
            T_after_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = time_after_pulse, amplitude = 0.)

            e = element.Element('%s_Pi_pulse' %(prefix),  pulsar=qt.pulsar,
                    global_time = True)
            e.append(T_before_p)
            e.append(pulse.cp(X))
            e.append(T_after_p)

        elif Gate_operation == 'y':
            time_before_pulse = time_before_pulse  -self.params['fast_pi2_duration']/2.0
            time_after_pulse = time_after_pulse  -self.params['fast_pi2_duration']/2.0


            X = self._Ypi2_elt()
            T_before_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = time_before_pulse, amplitude = 0.)
            T_after_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = time_after_pulse, amplitude = 0.)

            e = element.Element('%s_Pi_2_pulse' %(prefix),  pulsar=qt.pulsar,
                    global_time = True)
            e.append(T_before_p)
            e.append(pulse.cp(X))
            e.append(T_after_p)


        elif Gate_operation == '-y':
            time_before_pulse = time_before_pulse  -self.params['fast_pi2_duration']/2.0
            time_after_pulse = time_after_pulse  -self.params['fast_pi2_duration']/2.0

            X = self._mYpi2_elt()
            T_before_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = time_before_pulse, amplitude = 0.)
            T_after_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = time_after_pulse, amplitude = 0.)

            e = element.Element('%s_Pi_2_pulse' %(prefix),  pulsar=qt.pulsar,
                    global_time = True)
            e.append(T_before_p)
            e.append(pulse.cp(X))
            e.append(T_after_p)

        else:
            print 'this is not programmed yet '
            return

        Gate.elements = [e]

    def generate_RF_pulse_element(self,Gate):
        '''
        Written by MB. 
        Generate arbitrary RF pulse gate, so a pulse that is directly created by the AWG.
        Pulse is build up out of a starting element, a repeated middle element and an end
        element to save the memory of the AWG.
        '''

        ###################
        ## Set paramters ##
        ###################

        Gate.scheme = 'RF_pulse'

        length     = Gate.length
        freq       = Gate.RFfreq
        amplitude  = Gate.amplitude
        prefix     = Gate.prefix
        phase      = Gate.phase

        #We choose a max length for pulse block of

        # Freq_Res = 5 #Needed freq res in Hz
        # multiplier = freq / Freq_Res
        # periods_in_pulse = int(1e-6 * freq) + 1

        # while (periods_in_pulse / freq) % 1e-9 != 0:
        #     periods_in_pulse += 1
        #     if periods_in_pulse / freq > 1e-3:
        #         print periods_in_pulse
        #         raise Exception('Choose different freq')
        # print periods_in_pulse / freq
        

        #Determine the number of periods that fit in one repeated middle element and if its dividable by 4 ns. 
        # periods_in_pulse = int(1e-6 * freq) + 1

        # # while round(periods_in_pulse * 1e9 / freq) % 4 != 0:
        # #     print periods_in_pulse * 1e9 / freq
        # #     periods_in_pulse *= 2

        # print periods_in_pulse
        # #Determine the length of the rise element based on the amplitude you want the Erf to have when cutting off
        # MinErfAmp = 0.999 #99.9% of full amplitude when cutting off error function
        # rise_length = max(0.5 * 0.5e-6 * (2+erfinv(0.99)),1e-6) #0.5e-6 is the risetime of the pulse


        # #RF pulses are limited due to structure, but this shouldnt be conflicting if one wants to perform a gate 
        # if length <= periods_in_pulse/freq + 2e-6:
        #     raise Exception('RF pulse is too short')

        # print periods_in_pulse
        #Determine number of repeated elements
        # Gate.reps, tau_remaind = divmod(round(1e9*(length-2*rise_length)),periods_in_pulse/freq*1e9)
        # tau_remaind *= 1e-9 
        list_of_elements = []

        X = pulselib.RF_erf_envelope(
            channel = 'RF',
            length = length,
            frequency = freq,
            amplitude = amplitude,
            phase = phase)
        # Env_start_p = pulselib.RF_erf_rise_element(
        #     channel = 'RF',
        #     length = rise_length + tau_remaind / 2,
        #     frequency = freq,
        #     amplitude = amplitude,
        #     phase = phase,
        #     startorend = 'start')
        # Env_end_p = pulselib.RF_erf_rise_element(
        #     channel = 'RF',
        #     length = rise_length + tau_remaind / 2,
        #     frequency = freq,
        #     amplitude = amplitude,
        #     phase = phase,
        #     startorend = 'end')

        # e_start = element.Element('%s_RF_pulse_start' %(prefix),  pulsar=qt.pulsar,
        #         global_time = True)
        # e_start.append(pulse.cp(Env_start_p))
        # list_of_elements.append(e_start)

        e_middle = element.Element('%s_RF_pulse_middle' %(prefix),  pulsar=qt.pulsar,
                global_time = True)
        e_middle.append(pulse.cp(X))
        list_of_elements.append(e_middle)

        # e_end = element.Element('%s_RF_pulse_end' %(prefix),  pulsar=qt.pulsar,
        #         global_time = True)
        # e_end.append(pulse.cp(Env_end_p))
        # list_of_elements.append(e_end)

        Gate.tau_cut = 1e-6
        Gate.wait_time = Gate.length + 2e-6
        Gate.elements= list_of_elements
        
        return Gate

    def generate_RF_pulse_element_repeated_middle(self,Gate):
        '''
        Written by MB. 
        Generate arbitrary RF pulse gate, so a pulse that is directly created by the AWG.
        Pulse is build up out of a starting element, a repeated middle element and an end
        element to save the memory of the AWG.
        '''

        ###################
        ## Set paramters ##
        ###################

        Gate.scheme = 'RF_pulse'

        length     = Gate.length
        freq       = Gate.RFfreq
        amplitude  = Gate.amplitude
        prefix     = Gate.prefix
        phase      = Gate.phase

        #We choose a max length for pulse block of

        Freq_Res = 5 #Needed freq res in Hz
        multiplier = freq / Freq_Res
        periods_in_pulse = int(1e-6 * freq) + 1

        while (periods_in_pulse / freq) % 1e-9 != 0:
            periods_in_pulse += 1
            if periods_in_pulse / freq > 1e-3:
                print periods_in_pulse
                raise Exception('Choose different freq')
        print periods_in_pulse / freq
        

        #Determine the number of periods that fit in one repeated middle element and if its dividable by 4 ns. 
        # periods_in_pulse = int(1e-6 * freq) + 1

        # # while round(periods_in_pulse * 1e9 / freq) % 4 != 0:
        # #     print periods_in_pulse * 1e9 / freq
        # #     periods_in_pulse *= 2

        print periods_in_pulse
        #Determine the length of the rise element based on the amplitude you want the Erf to have when cutting off
        MinErfAmp = 0.999 #99.9% of full amplitude when cutting off error function
        rise_length = max(0.5 * 0.5e-6 * (2+erfinv(0.99)),1e-6) #0.5e-6 is the risetime of the pulse


        #RF pulses are limited due to structure, but this shouldnt be conflicting if one wants to perform a gate 
        if length <= periods_in_pulse/freq + 2e-6:
            raise Exception('RF pulse is too short')

        print periods_in_pulse
        #Determine number of repeated elements
        Gate.reps, tau_remaind = divmod(round(1e9*(length-2*rise_length)),periods_in_pulse/freq*1e9)
        tau_remaind *= 1e-9 
        list_of_elements = []

        X = pulse.SinePulse(
            channel = 'RF',
            length = periods_in_pulse / freq,
            frequency = freq,
            amplitude = amplitude,
            phase = phase)
        Env_start_p = pulselib.RF_erf_rise_element(
            channel = 'RF',
            length = rise_length + tau_remaind / 2,
            frequency = freq,
            amplitude = amplitude,
            phase = phase,
            startorend = 'start')
        Env_end_p = pulselib.RF_erf_rise_element(
            channel = 'RF',
            length = rise_length + tau_remaind / 2,
            frequency = freq,
            amplitude = amplitude,
            phase = phase,
            startorend = 'end')

        e_start = element.Element('%s_RF_pulse_start' %(prefix),  pulsar=qt.pulsar,
                global_time = True)
        e_start.append(pulse.cp(Env_start_p))
        list_of_elements.append(e_start)

        e_middle = element.Element('%s_RF_pulse_middle' %(prefix),  pulsar=qt.pulsar,
                global_time = True)
        e_middle.append(pulse.cp(X))
        list_of_elements.append(e_middle)

        e_end = element.Element('%s_RF_pulse_end' %(prefix),  pulsar=qt.pulsar,
                global_time = True)
        e_end.append(pulse.cp(Env_end_p))
        list_of_elements.append(e_end)

        Gate.tau_cut = 1e-6
        Gate.wait_time = Gate.length + 2e-6
        Gate.elements= list_of_elements
        return Gate

    def generate_LDE_element(self,Gate):
        '''
        Generates the primitive of an LDE element.
        Optical pi pulses are implemented AR 2016 04
        NK
        '''

        ### Possible TODO:
        ### Add an AOM delay time at the end! then there is no overlap between the following pi/2 and the repumper.
        ### note that this is not strictly necessary if the Switch risetime at the beginning of the element is long enough.
        ### and it is at te moment


        ###################
        ## Set paramters ##
        ###################

        Gate.scheme = 'LDE'

        t           = Gate.t
        t_rep       = Gate.t_rep

        repump_duration      = Gate.repump_duration

        ### whether or not you want to do a pi/BB1 pulse during the sequence is determined by this bool.
        if not hasattr(Gate,'do_pi'):
            Gate.do_pi = False
        if not hasattr(Gate,'do_BB1'):
            Gate.do_BB1 = False
        
        ### define necessary pulses
        #MW pulses
        pi2 = self._pi2_elt()
        X = self._X_elt()
        mX = self._mX_elt()
        Y = self._Y_elt()
        # pi2 = pulse.cp(pi2,phase = self.params['Y_phase'])

        #### gives the possiblity to sweep the amplitude of this specific pi pulse.
        RepumpX = pulse.cp(X, amplitude = Gate.pi_amp)


        ### delay of the MW channel
        Gate.MW_delay = qt.pulsar.channels['MW_Imod']['delay']


        #wait times
        # print 'X risetime {}'.format(X.risetime*1e9)
        duration_initial = X.risetime + self.params['fast_pi2_duration']/2 + 400e-9 + Gate.MW_delay ## because MW switch and MW delay and AOM delay. Used to be 35ns
        Gate.duration_initial = duration_initial -  Gate.MW_delay


        # not implemented. See below #XXXXXXX
        duration_final = 2e-9 ### give some space after the laser pulse.
        Gate.duration_final = duration_final

        do_optical_pi_pulses=self.params['do_optical_pi']

        T_init =  pulse.SquarePulse(channel='adwin_sync', name='init_pi2',
                    length = duration_initial - self.params['fast_pi2_duration']/2, amplitude = 0.)
        T_final =  pulse.SquarePulse(channel='adwin_sync', name='Wait t',
                    length = duration_final, amplitude = 0.)
        
        ### necessary length definitions if you do a regular pi pulse.
        if Gate.do_pi:
            T =  pulse.SquarePulse(channel='adwin_sync', name='Wait t', refpulse='init_pi2', refpoint ='end',
                    length = t-self.params['fast_pi_duration']/2-self.params['fast_pi2_duration']/2, amplitude = 0.)
            
            T_rep = pulse.SquarePulse(channel='adwin_sync',name='Wait t-trep',
                    length = (t-t_rep)-self.params['fast_pi_duration']/2, amplitude = 0.)
        
        ### necessary definitions if you do BB1
        elif Gate.do_BB1:
            T =  pulse.SquarePulse(channel='adwin_sync', name='Wait t', refpulse=T_init, refpoint ='end',
                    length = t-5*self.params['fast_pi_duration']/2-self.params['fast_pi2_duration']/2, amplitude = 0.)
            T_rep = pulse.SquarePulse(channel='adwin_sync',name='Wait t-trep',
                    length = t-t_rep-5*self.params['fast_pi_duration']/2, amplitude = 0.)

            ### overwrite with BB1 pulse definition.
            RepumpX = pulse.cp(RepumpX,length = self.params['BB1_fast_pi_duration'],amplitude = self.params['BB1_fast_pi_amp'])
            BB1_phase1 = pulse.cp(RepumpX,phase = self.params['X_phase']+104.5)
            BB1_phase2 = pulse.cp(RepumpX,phase = self.params['X_phase']+313.4)
        else:
            T_rep = pulse.SquarePulse(channel='adwin_sync',name='Wait t-trep',
                    length = (t-t_rep)-self.params['fast_pi2_duration']/2, amplitude = 0.)
        #defined on a marker channel, amp has to be 1 in order to switch on.
        AWG_repump = pulse.SquarePulse(channel = Gate.channel,name = 'repump',
            length = repump_duration,amplitude = 1)

        

        # print 'T duration', t-5*self.params['fast_pi_duration']/2-self.params['fast_pi2_duration']/2
        # print 'T_rep duration', (t-t_rep)-5*self.params['fast_pi_duration']/2
        
        #create element
        rep_LDE_elt = element.Element('%s' %(Gate.prefix), pulsar = qt.pulsar, global_time=True)

        rep_LDE_elt.append(T_init)
        if self.params['initial_MW_pulse'] == 'pi2':
            print 'Repumping: Initial pulse is pi2'
            rep_LDE_elt.append(pi2)
        elif self.params['initial_MW_pulse'] == 'pi':
            print 'Repumping: Initial pulse is pi'
            rep_LDE_elt.append(RepumpX)

        if Gate.do_pi:
            rep_LDE_elt.append(T)
            rep_LDE_elt.append(RepumpX)

        elif Gate.do_BB1:
            rep_LDE_elt.append(T)
            rep_LDE_elt.append(BB1_phase1)
            rep_LDE_elt.append(BB1_phase2)
            rep_LDE_elt.append(BB1_phase2)
            rep_LDE_elt.append(BB1_phase1)
            rep_LDE_elt.append(RepumpX)
        
        if do_optical_pi_pulses:

            optical_pi_pulse = eom_pulses.OriginalEOMAOMPulse('Eom Aom Pulse', 
                eom_channel = 'EOM_Matisse',
                aom_channel = 'EOM_AOM_Matisse',
                eom_pulse_duration      = self.params['eom_pulse_duration'],
                eom_off_duration        = self.params['eom_off_duration'],
                eom_off_amplitude       = self.params['eom_off_amplitude'],
                eom_pulse_amplitude     = self.params['eom_pulse_amplitude'],
                eom_overshoot_duration1 = self.params['eom_overshoot_duration1'],
                eom_overshoot1          = self.params['eom_overshoot1'],
                eom_overshoot_duration2 = self.params['eom_overshoot_duration2'],
                eom_overshoot2          = self.params['eom_overshoot2'],
                aom_risetime            = self.params['aom_risetime'],
                aom_amplitude           = self.params['aom_amplitude'])
            
            T_back_to_optical =  pulse.SquarePulse(channel='adwin_sync', name='T_before_optical',
                length = -self.params['optical_pi_pulse_sep']/2, amplitude = 0.) #Go back in time
            T_optical_pulse_sep =  pulse.SquarePulse(channel='adwin_sync', name='T_optical_pulse_sep',
                length = self.params['optical_pi_pulse_sep'], amplitude = 0.) #Go back in time

            rep_LDE_elt.append(T_back_to_optical)
            rep_LDE_elt.append(optical_pi_pulse)
            rep_LDE_elt.append(T_optical_pulse_sep)
            rep_LDE_elt.append(optical_pi_pulse)
            rep_LDE_elt.append(T_back_to_optical)

        rep_LDE_elt.append(T_rep)
        rep_LDE_elt.append(AWG_repump)
        # rep_LDE_elt.append(T_final)

        Gate.elements =  [rep_LDE_elt]
        Gate.elements_duration = (duration_initial +  2*t-t_rep+repump_duration+duration_final)*Gate.reps





    ### function for making sequences out of elements
    def combine_to_AWG_sequence(self,gate_seq,explicit = False):
        '''
        Used as last step before uploading, combines all the gates to a sequence the AWG can understand.
        Requires the gates to already have the elements and repetitions and stuff added as arguments.
        NOTE: 'event_jump', 'goto' and 'wait' options only available for certain types of elements
        explicit is a statement that is introduced to maintain backwards compatibility,
        explicit is also required when using jump and goto statements.
        '''
        list_of_elements=[]
        seq = pulsar.Sequence('Decoupling Sequence')
        if explicit == False:  # explicit means that MBI and trigger elements must be given explicitly to the combine to AWG sequence function
            mbi_elt = self._MBI_element()
            list_of_elements.append(mbi_elt)
            seq.append(name=str(mbi_elt.name+gate_seq[0].elements[0].name),#This is to make sequence name unique, but eventual name is a bit confusing. maybe only add data_point nr -MBlok 28-05-'15'
                    wfname=mbi_elt.name, trigger_wait=True,repetitions = 1,
                    goto_target =str(mbi_elt.name+gate_seq[0].elements[0].name),
                    jump_target = gate_seq[0].elements[0].name)

        for i, gate in enumerate(gate_seq):
            # Determine where jump events etc
            if hasattr(gate, 'go_to'):
                if gate.go_to == None:
                    pass
                elif gate.go_to == 'next':
                    gate.go_to = gate_seq[i+1].elements[0].name
                elif gate.go_to == 'second_next':

                    gate.go_to = gate_seq[i+2].elements[0].name
                elif gate.go_to == 'self': 
                    gate.go_to = gate.elements[0].name
                elif gate.go_to =='start':
                    gate.go_to = gate_seq[0].elements[0].name
                else:
                    ind = self.find_gate_index(gate.go_to,gate_seq)
                    gate.go_to = gate_seq[ind].elements[0].name


            if hasattr(gate, 'event_jump'):
                if gate.event_jump == None:
                    pass
                elif gate.event_jump == 'next':
                    gate.event_jump = gate_seq[i+1].elements[0].name
                elif gate.event_jump == 'second_next':
                    gate.event_jump = gate_seq[i+2].elements[0].name
                elif gate.event_jump =='self':
                    gate.elements[0].name
                elif gate.event_jump == 'start' :
                    gate.event_jump = gate_seq[0].elements[0].name
                else:
                    ind = self.find_gate_index(gate.event_jump,gate_seq)
                    gate.event_jump = gate_seq[ind].elements[0].name
            # Debug print statement:
            # print 'Gate %s, \n  %s \n goto %s, \n jump %s' %(gate.name,gate.elements[0].name,gate.go_to,gate.event_jump)

            single_elements_list = ['NO_Pulses','single_block','single_element','carbon_phase_feedback','carbon_phase_feedback_end_elt','carbon_phase_feedback_start_elt']
            #####################
            ### 'special' elements ###
            #####################

            if gate.scheme == 'mbi':
                e = gate.elements[0]
                list_of_elements.append(e)
                seq.append(name =e.name, wfname =e.name,
                        trigger_wait = True,
                        repetitions = 1,
                        goto_target =gate.go_to ,
                        jump_target =gate.event_jump)
            elif gate.scheme =='trigger' :
                e = gate.elements[0]
                list_of_elements.append(e)

                seq.append(name = e.name, wfname =e.name,
                        trigger_wait = gate.wait_for_trigger,
                        repetitions = gate.reps,
                        goto_target = gate.go_to,
                        jump_target= gate.event_jump )

            elif gate.scheme == 'LDE' :

                if len(gate.elements) == 1: # this implies a single setup sequence!
                    list_of_elements.extend(gate.elements)
                    e = gate.elements[0]
                    seq.append(name=e.name,wfname =e.name,
                                trigger_wait=gate.wait_for_trigger,
                                repetitions=gate.reps,
                                goto_target = gate.go_to,
                                jump_target= gate.event_jump)

                


            #########################
            ###  single elements  ###
            #########################
            elif gate.scheme in single_elements_list :
                # if 'rephasing' in gate.name:
                #     print 'i did the thing', gate.name
                #     gate.elements[0].print_overview()
                e = gate.elements[0]
                list_of_elements.append(e)
                if gate.reps ==0:
                    gate.reps = 1
                if (i == 0 and explicit == False ):  #need to check for modularity
                    seq.append(name=e.name, wfname=e.name,
                        trigger_wait=True,repetitions = gate.reps)

                else:
                    seq.append(name=e.name,wfname =e.name,
                            trigger_wait=gate.wait_for_trigger,
                            repetitions=gate.reps,
                            goto_target = gate.go_to,
                            jump_target= gate.event_jump )

            ####################
            ###  RF elements ###
            ####################
            elif gate.scheme == 'RF_pulse':
                list_of_elements.extend(gate.elements)
                # starting envelope element
                # seq.append(name=gate.elements[0].name, wfname=gate.elements[0].name,
                #     trigger_wait=False,repetitions = 1)
                # repeating period element
                gate.reps = 1
                seq.append(name=gate.elements[0].name, wfname=gate.elements[0].name,
                    trigger_wait=False,repetitions = gate.reps)
                 # ending envelope element
                # seq.append(name=gate.elements[2].name, wfname=gate.elements[2].name,
                #     trigger_wait=False,repetitions = 1)
            ######################
            ### XY4 elements
            ######################
            elif gate.scheme == 'XY4':
                #TODO_THT: (Possibly) fix that last element is XX instead of XY if only 2 final elements
                list_of_elements.extend(gate.elements)
                # initial element
                seq.append(name=gate.elements[0].name, wfname=gate.elements[0].name,
                    trigger_wait=gate.wait_for_trigger,repetitions = 1)
                # repeating element
                seq.append(name=gate.elements[1].name, wfname=gate.elements[1].name,
                    trigger_wait=False,repetitions = gate.reps/2-1)
                # final element
                seq.append(name=gate.elements[2].name, wfname=gate.elements[2].name,
                    trigger_wait=False,
                    goto_target = gate.go_to,
                    jump_target = gate.event_jump,
                    repetitions = 1)
            ######################
            ### XY8 elements
            #-a-b-(c^2-b^2)^(N/8-1)-c-d-
            ######################
            elif gate.scheme =='XY8':
                #TODO_THT: fix that last element is XX instead of XY if only 2 final elements
                list_of_elements.extend(gate.elements)
                a = gate.elements[0]
                b= gate.elements[1]
                c = gate.elements[2]
                d = gate.elements[3]
                seq.append(name=a.name, wfname=a.name,
                    trigger_wait=gate.wait_for_trigger,
                    repetitions = 1)
                seq.append(name=b.name, wfname=b.name,
                    trigger_wait=False,repetitions = 1)
                for i in range(gate.reps/8-1):
                    seq.append(name=(c.name+str(i)), wfname=c.name,
                        trigger_wait=False,repetitions = 2)
                    seq.append(name=(b.name+str(i)), wfname=b.name,
                        trigger_wait=False,repetitions = 2)
                seq.append(name=c.name, wfname=c.name,
                    trigger_wait=False,repetitions = 1)
                seq.append(name=d.name, wfname=d.name,
                    trigger_wait=False,
                    goto_target = gate.go_to,
                    jump_target = gate.event_jump,
                    repetitions = 1)
            ######################
            ### XYn, tau > 2 mus
            # t^n a t^n b t^n
            ######################
            elif gate.scheme =='repeating_T_elt':
                list_of_elements.extend(gate.elements)
                wait_reps = gate.n_wait_reps
                st  = gate.elements[0]
                x   = gate.elements[1]
                y   = gate.elements[2]
                fin = gate.elements[3]
                t   = gate.elements[4]

                #Start elements
                pulse_ct = 0
                red_wait_reps = wait_reps//2
                if red_wait_reps != 0: #Note st.name is name of the repeating t element here because of references
                    seq.append(name=st.name, wfname=t.name, # this naming is very confusing when you first read it. Unless there is a deep reason, I suggest this gets changed to something more intuitive -MB 28-05-15
                        trigger_wait=gate.wait_for_trigger,
                        repetitions = red_wait_reps)#floor divisor
               # print 'wait_reps = ', wait_reps
               # print 'red_wait_reps = ',red_wait_reps
                seq.append(name=st.name+'_', wfname=st.name,
                    trigger_wait=False,repetitions = 1)
                pulse_ct+=1
                #Repeating centre elements
                x_list = [0,2,5,7]
                while pulse_ct < (gate.reps-1):
                    seq.append(name=t.name+'_'+str(pulse_ct), wfname=t.name,
                        trigger_wait=False,repetitions = wait_reps)
                    if pulse_ct%8 in x_list:
                        seq.append(name=x.name+str(pulse_ct), wfname=x.name,
                            trigger_wait=False,repetitions = 1)
                    else:
                        seq.append(name=y.name+str(pulse_ct), wfname=y.name,
                            trigger_wait=False,repetitions = 1)
                    pulse_ct +=1
                #Final elements
                if gate.reps== 1:
                    if red_wait_reps!=0 and red_wait_reps!=1 :
                        seq.append(name=t.name+str(pulse_ct+1), wfname=t.name,
                           trigger_wait=False,
                           goto_target = gate.go_to,
                           jump_target = gate.event_jump,
                           repetitions = red_wait_reps-1) #floor divisor
                else:
                    seq.append(name=t.name+'_'+str(pulse_ct), wfname=t.name,
                        trigger_wait=False,repetitions = wait_reps)
                    if red_wait_reps == 0:
                        seq.append(name=fin.name, wfname=fin.name,
                            trigger_wait=False,
                            goto_target = gate.go_to,
                            jump_target = gate.event_jump,
                            repetitions = 1)
                    else:
                        seq.append(name=fin.name, wfname=fin.name,
                            trigger_wait=False,
                            goto_target = gate.go_to,
                            jump_target = gate.event_jump,
                            repetitions = 1)
                        seq.append(name=t.name+str(pulse_ct+1), wfname=t.name,
                           trigger_wait=False,repetitions = red_wait_reps) #floor divisor
            ######################
            ### XYn, tau > 2 mus, now also supporting XY16
            # MAB 010615
            # t^n a t^n b t^n
            ######################
            elif gate.scheme =='repeating_T_elt_XY16':
                list_of_elements.extend(gate.elements)
                wait_reps = gate.n_wait_reps
                st  = gate.elements[0]
                x   = gate.elements[1]
                y   = gate.elements[2]
                mx  = gate.elements[3]
                my  = gate.elements[4]
                fin = gate.elements[5]
                t   = gate.elements[6]

                #Start elements
                pulse_ct = 0
                red_wait_reps = wait_reps//2
                if red_wait_reps != 0: #Note st.name is name of the repeating t element here because of references
                    seq.append(name=st.name, wfname=t.name,
                        trigger_wait=gate.wait_for_trigger,
                        repetitions = red_wait_reps)#floor divisor
                seq.append(name=st.name+'_', wfname=st.name,
                    trigger_wait=False,repetitions = 1)
                pulse_ct+=1
                #Repeating centre elements
                x_list = [0,2,5,7]
                y_list = [1,3,4,6]
                mx_list = [8,10,13,15]
                my_list = [9,11,12,14]
                while pulse_ct < (gate.reps-1):
                    seq.append(name=t.name+'_'+str(pulse_ct), wfname=t.name,
                        trigger_wait=False,repetitions = wait_reps)
                    if pulse_ct%16 in x_list:
                        seq.append(name=x.name+str(pulse_ct), wfname=x.name,
                            trigger_wait=False,repetitions = 1)
                    elif pulse_ct%16 in y_list:
                        seq.append(name=y.name+str(pulse_ct), wfname=y.name,
                            trigger_wait=False,repetitions = 1)
                    elif pulse_ct%16 in mx_list:
                        seq.append(name=mx.name+str(pulse_ct), wfname=mx.name,
                            trigger_wait=False,repetitions = 1)
                    elif pulse_ct%16 in my_list:
                        seq.append(name=my.name+str(pulse_ct), wfname=my.name,
                            trigger_wait=False,repetitions = 1)
                    else:
                        raise Exception('Error in creating combine to AWG sequence for using repeating T XY16')
                    pulse_ct +=1
                #Final elements
                if gate.reps== 1:
                    if red_wait_reps!=0 and red_wait_reps!=1 :
                        seq.append(name=t.name+str(pulse_ct+1), wfname=t.name,
                           trigger_wait=False,
                           goto_target = gate.go_to,
                           jump_target = gate.event_jump,
                           repetitions = red_wait_reps-1) #floor divisor
                else:
                    seq.append(name=t.name+'_'+str(pulse_ct), wfname=t.name,
                        trigger_wait=False,repetitions = wait_reps)
                    if red_wait_reps == 0:
                        seq.append(name=fin.name, wfname=fin.name,
                            trigger_wait=False,
                            goto_target = gate.go_to,
                            jump_target = gate.event_jump,
                            repetitions = 1)
                    else:
                        seq.append(name=fin.name, wfname=fin.name,
                            trigger_wait=False,
                            goto_target = gate.go_to,
                            jump_target = gate.event_jump,
                            repetitions = 1)
                        seq.append(name=t.name+str(pulse_ct+1), wfname=t.name,
                           trigger_wait=False,repetitions = red_wait_reps) #floor divisor

            else:
                print 'Gate %s not added, scheme = %s' %(gate.name,gate.scheme)
        if explicit == False:
            trig_elt = self._Trigger_element()
            list_of_elements.append(trig_elt)
            seq.append(name=str(trig_elt.name+gate_seq[0].elements[0].name), wfname=trig_elt.name, #see comment at MBI el
                            trigger_wait=False,repetitions = 1)


        return list_of_elements, seq

    ### elements generation
    def generate_AWG_elements(self,Gate_sequence,pt = 1):

        Gate_sequence = self.decompose_composite_gates(Gate_sequence)


        for g in Gate_sequence:

            if len(g.name) >= 30:
                print "Gate " + g.name + "has a name longer than 30 characters. This will probably"
                + "break the AWG"

            if g.Gate_type =='Carbon_Gate' or g.Gate_type =='electron_decoupling':
                self.get_gate_parameters(g)
                self.generate_decoupling_sequence_elements(g)
                #print 'I am a carbon gate on this carbon %d' %g.Carbon_ind
            elif g.Gate_type =='passive_elt':
                self.generate_passive_wait_element(g)
            elif g.Gate_type == 'MBI':
                self.generate_MBI_elt(g)
            elif g.Gate_type == 'Trigger':
                self.generate_trigger_elt(g)
            elif g.Gate_type == 'electron_repump':
                self.generate_electron_repump_element(g)
            elif g.Gate_type == 'RF_pulse':
                self.generate_RF_pulse_element(g)
            elif g.Gate_type == 'LDE':
                self.generate_LDE_element(g)
        
        Gate_sequence = self.insert_transfer_gates(Gate_sequence,pt)
        for g in Gate_sequence:
            if (g.Gate_type == 'Transfer_element'):
                self.generate_transfer_element(g)

        Gate_sequence = self.insert_phase_gates(Gate_sequence,pt)

    
        self.get_tau_cut_for_connecting_elts(Gate_sequence)
        self.track_and_calc_phase(Gate_sequence)
        for g in Gate_sequence:
            # if hasattr(g,'tau_cut'):   
            #     print g.name, g.tau_cut
            if (g.Gate_type == 'Connection_element' or g.Gate_type == 'electron_Gate'):

                # print 'i am connecting or an electron gate',g.name
                self.determine_connection_element_parameters(g)

                self.generate_connection_element(g)
                #print 'I am a %s connection element: on this carbon %d' %g.Gate_type%g.Carbon_ind,g.name

        return Gate_sequence


class NuclearRamsey(DynamicalDecoupling):


    '''
    The NuclearRamsey class performs a ramsey experiment on a nuclear spin that is
    resonantly controlled using a decoupling sequence.
    ---|pi/2| - |Ren| - |Rz| - |Ren| - |pi/2| ---
    '''
    mprefix = 'CarbonRamsey'

    def generate_sequence(self, upload= True, debug = False):
        pts = self.params['pts']
        free_evolution_time = self.params['free_evolution_times']

        # #initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Nuclear Ramsey Sequence')

        for pt in range(pts):

            ###########################################
            #####    Generating the sequence elements      ######
            ###########################################
            initial_Pi2 = Gate('initial_pi2','electron_Gate')
            Ren_a = Gate('Ren_a', 'Carbon_Gate')
            Rz = Gate('Rz','Connection_element')
            Ren_b = Gate('Ren_b', 'Carbon_Gate')
            final_Pi2 = Gate('final_pi2','electron_Gate')

            ############
            gate_seq = [initial_Pi2,Ren_a,Rz,Ren_b,final_Pi2]
            ############

            Ren_a.N = self.params['C_Ren_N'+self.params['electron_transition']]
            Ren_a.tau = self.params['C_Ren_tau'+self.params['electron_transition']]
            Ren_a.scheme = self.params['Decoupling_sequence_scheme']
            Ren_a.prefix = 'Ren_a'+str(pt)

            Ren_b.N = self.params['C_Ren_N'+self.params['electron_transition']]
            Ren_b.tau = self.params['C_Ren_tau'+self.params['electron_transition']]
            Ren_b.scheme = self.params['Decoupling_sequence_scheme']
            Ren_b.prefix = 'Ren_b'+str(pt)

            #Generate sequence elements for all Carbon gates
            self.generate_decoupling_sequence_elements(Ren_a)
            self.generate_decoupling_sequence_elements(Ren_b)

            #Use information about duration of carbon gates to calculate
            #use function for this in more fancy meass class
            initial_Pi2.time_before_pulse =max(1e-6 - Ren_a.tau_cut + 36e-9,44e-9)
            initial_Pi2.time_after_pulse = Ren_a.tau_cut
            initial_Pi2.Gate_operation = self.params['Initial_Pulse']
            initial_Pi2.prefix = 'init_pi2'+str(pt)

            final_Pi2.time_before_pulse =Ren_a.tau_cut
            final_Pi2.time_after_pulse = initial_Pi2.time_before_pulse
            final_Pi2.Gate_operation = self.params['Final_Pulse']
            final_Pi2.prefix = 'fin_pi2'+str(pt)

            #Generate the start and end pulse
            self.generate_electron_gate_element(initial_Pi2)
            self.generate_electron_gate_element(final_Pi2)

            # Generate Rz element (now we explicitly set tau, N and time before and after final)
            Rz.prefix = 'phase_gate'+str(pt)
            Rz.dec_duration = self.params['free_evolution_times'][pt]
            Rz.tau_cut_before = Ren_a.tau_cut
            Rz.tau_cut_after = Ren_a.tau_cut

            self.determine_connection_element_parameters(Rz)
            self.generate_connection_element(Rz)

            # Combine to AWG sequence that can be uploaded #
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq)
            combined_list_of_elements.extend(list_of_elements)
            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)




        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)
        else:
            print 'upload = false, no sequence uploaded to AWG'

class NuclearRamsey_v2(DynamicalDecoupling):
    '''
    Supercedes the Nuclear Ramsey class
    The NuclearRamsey class performs a ramsey experiment on a nuclear spin that is
    resonantly controlled using a decoupling sequence.
    Decoupling between Ren gates is required to prevent electron dephasing.
    ---|pi/2| - |Ren| - |Rz| - |Ren| - |pi/2| ---
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
            mbi = Gate('MBI_'+str(pt),'MBI')
            # mbi_seq = [mbi]

            initial_Pi2 = Gate('initial_pi2_'+str(pt),'electron_Gate',
                    Gate_operation ='pi2',
                    wait_for_trigger = True,
                    phase = self.params['X_phase'])
            Ren_a = Gate('Ren_a_'+str(pt), 'Carbon_Gate',
                    Carbon_ind =self.params['addressed_carbon'])
            Ren_a.el_state_after_gate = 'sup'
            Rz = Gate('Rz_'+str(pt),'Connection_element',
                    dec_duration = self.params['free_evolution_times'][pt])
            Ren_b = Gate('Ren_b'+str(pt), 'Carbon_Gate',
                    Carbon_ind =self.params['addressed_carbon'])
            final_Pi2 = Gate('final_pi2_'+str(pt),'electron_Gate',
                    Gate_operation ='pi2',
                    wait_for_trigger = False,
                    phase = self.params['X_phase']+180)

            RO_Trigger = Gate('RO_Trigger_'+str(pt),'Trigger',el_state_before_gate = '0')

            ############
            gate_seq = [mbi,initial_Pi2,Ren_a,Rz,Ren_b,final_Pi2,RO_Trigger]
            ############
            gate_seq = self.generate_AWG_elements(gate_seq,pt)
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq, explicit=True)
            combined_list_of_elements.extend(list_of_elements)
            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)


        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)
        else:
            print 'upload = false, no sequence uploaded to AWG'

class NuclearRamsey_no_elDD(DynamicalDecoupling):
    '''
    Supercedes the Nuclear Ramsey no el DD class
    The NuclearRamsey class performs a ramsey experiment on a nuclear spin that is
    resonantly controlled using a decoupling sequence.
    MBI---|y| - |Ren| - |x|--|Wait| -- |y|- |Ren| - |x| ---RO
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
            mbi = Gate('MBI_'+str(pt),'MBI')
            # mbi_seq = [mbi]

            initial_Pi2 = Gate('initial_pi2_'+str(pt),'electron_Gate',
                    Gate_operation ='pi2',
                    wait_for_trigger = True,
                    phase = self.params['Y_phase'])
            Ren_a = Gate('Ren_a_'+str(pt), 'Carbon_Gate',
                    Carbon_ind =self.params['addressed_carbon'],
                    phase = None)

            pi2_a = Gate('pi2_a_'+str(pt),'electron_Gate',
                    Gate_operation ='pi2',
                    wait_for_trigger = False,
                    phase = self.params['X_phase'])
            wait_gate = Gate('Wait_gate_'+str(pt),'passive_elt',
                    wait_time = self.params['free_evolution_times'][pt])

            pi2_b = Gate('pi2_b_'+str(pt),'electron_Gate',
                    Gate_operation ='pi2',
                    wait_for_trigger = False,
                    phase = self.params['Y_phase'])
            Ren_b = Gate('Ren_b'+str(pt), 'Carbon_Gate',
                    Carbon_ind =self.params['addressed_carbon'],
                    phase = None)
            final_Pi2 = Gate('final_pi2_'+str(pt),'electron_Gate',
                    Gate_operation ='pi2',
                    wait_for_trigger = False,
                    phase = self.params['X_phase']+180)

            RO_Trigger = Gate('RO_Trigger_'+str(pt),'Trigger',el_state_before_gate = '0')

            ############
            gate_seq = [mbi,initial_Pi2,Ren_a,pi2_a,wait_gate,pi2_b,Ren_b,final_Pi2,RO_Trigger]
            ############
            gate_seq = self.generate_AWG_elements(gate_seq,pt)
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq, explicit=True)
            combined_list_of_elements.extend(list_of_elements)
            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)

            if debug:
                print '*'*10
                for g in gate_seq:
                    '-'*5
                    print g.name
                    print g.C_phases_before_gate
                    print g.C_phases_after_gate

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)
        else:
            print 'upload = false, no sequence uploaded to AWG'


class SimpleDecoupling(DynamicalDecoupling):
    '''
    The most simple version of a decoupling sequence
    Contains initial pulse, decoupling sequence and final pulse.
    ---|pi/2| - |DD| - |pi/2| ---
    '''
    def generate_sequence(self,upload=True, debug=False,return_combined_seq=False):
        '''
        The function that is executed when a measurement script is executed
        It calls the different functions in this class
        For now it is simplified and can only do one type of decoupling sequence
        '''
        print 'simple_decoupling generate sequence'
        pts = self.params['pts']
        tau_list = self.params['tau_list']
        Number_of_pulses = self.params['Number_of_pulses']
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Simple Decoupling Sequence')

        for pt in range(pts):
            ###########################################
            #####    Generating the sequence elements      ######

            ###########################################

            initial_Pi2 = Gate('initial_pi2','electron_Gate')
            simple_el_dec = Gate('electron_decoupling', 'Carbon_Gate')
            final_Pi2 = Gate('final_pi2','electron_Gate')
            # mbi = Gate('MBI_'+str(pt),'MBI')
            if self.params['use_shutter'] == 1:
                wait_gate = Gate('Wait_for_shutter_close'+str(pt),'passive_elt',
                                              wait_time = 20e-3)

                gate_seq= self.generate_AWG_elements([wait_gate],pt)
            else:
                gate_seq = []
            # if self.params['use_shutter'] == 1:
            #     wait_gate = (Gate('Wait_for_shutter_close'+str(pt),'passive_elt',
            #                  wait_time = 15e-3))
            
            
            gate_seq.extend([initial_Pi2,simple_el_dec,final_Pi2])
            
            #############

            simple_el_dec.N = Number_of_pulses[pt]
            simple_el_dec.tau = tau_list[pt]
            simple_el_dec.prefix = 'electron'
            simple_el_dec.scheme = self.params['Decoupling_sequence_scheme']


            ## Generate the decoupling elements
            self.generate_decoupling_sequence_elements(simple_el_dec)


            #In case single block used inital and final pulse no
            if simple_el_dec.scheme == 'single_block':
                gate_seq = [simple_el_dec]
                # gate_seq = [simple_el_dec,final_pi]

                # initial_Pi.Gate_operation = self.params['Initial_Pulse']
                # initial_Pi.time_before_pulse = max(1e-6 -  simple_el_dec.tau_cut + 36e-9,44e-9)
                # initial_Pi.time_after_pulse = simple_el_dec.tau_cut
                # initial_Pi.prefix = 'init_pi2_'+str(pt)

            else:
                #Generate the start and end pulse
                initial_Pi2.Gate_operation = self.params['Initial_Pulse']
                
                #if np.mod(pt,2)==1:
                #   initial_Pi2.Gate_operation = '-x'
                #else:    
                #initial_Pi2.Gate_operation = 'x'
                
                initial_Pi2.time_before_pulse = 600e-9 # = MW switch risetime of 500 ns + 100 ns --> makes sure MW output = low when waiting for trigger #max(1e-6 -  simple_el_dec.tau_cut + 36e-9,44e-9)
                # print 'time_before_pulse'
                # print initial_Pi2.time_before_pulse
                initial_Pi2.time_after_pulse = simple_el_dec.tau_cut
                initial_Pi2.prefix = 'init_pi2_'+str(pt)#to ensure unique naming


                final_Pi2.time_before_pulse =simple_el_dec.tau_cut
                final_Pi2.time_after_pulse = initial_Pi2.time_before_pulse
                final_Pi2.Gate_operation = self.params['Final_Pulse']
                final_Pi2.prefix = 'fin_pi2_'+str(pt) #to ensure unique naming
                # print 'final_pulse'
                # print self.params['Final_Pulse']
                #Generate the start and end pulse
                self.generate_electron_gate_element(initial_Pi2)
                self.generate_electron_gate_element(final_Pi2)

            if self.params['DD_in_eigenstate']:
                simple_el_dec.wait_for_trigger = True
                # wait_gate = Gate('Sample_cooldown_'+str(pt),'passive_elt',wait_time = 50e-3)
                # self.generate_passive_wait_element(wait_gate)
                gate_seq = [simple_el_dec,wait_gate]

            ## Combine to AWG sequence that can be uploaded #
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq,explicit=False)

            combined_list_of_elements.extend(list_of_elements)
            for seq_el in seq.elements:
                # print 'added to combined_seq = ', seq_el['name']
                combined_seq.append_element(seq_el)

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)
        else:
            print 'upload = false, no sequence uploaded to AWG'
    
        if return_combined_seq:
            return combined_seq,combined_list_of_elements
            
class SimpleDecoupling_Single_Block(DynamicalDecoupling):
    '''
    Use this version of SimpleDecoupling only when having a large amount of decoupling pulses so 
    MAB 4-5-15
    ---|pi/2| - |DD| - |pi/2| ---

    Can handle following pulse sequences
    X (x)^n
    XmX (x mx)^n
    XY-4 (xyxy)**n
    XY-8 (xyxy yxyx)**n
    XY-16 (xyxy yxyx mxmymxmy mymxmymx)**n
    '''
    # adwin_process = 'MBI_shutter'

    def generate_sequence(self,upload=True, debug=False):
        '''
        The function that is executed when a measurement script is executed
        It calls the different functions in this class
        For now it is simplified and can only do one type of decoupling sequence
        '''
        pts = self.params['pts']
        tau_list = self.params['tau_list']
        Number_of_pulses = self.params['Number_of_pulses']

        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Simple Decoupling Sequence')

        XY_pulses = self.params['Number of pulses in XY scheme']
        print XY_pulses
        for pt in range(pts):
            if self.params['DD_in_eigenstate']:
                if Number_of_pulses[pt] % XY_pulses != 0:
                    raise Exception('Error: Number of pulses should be a multiple of ' + str(XY_pulses))
            else:
                if Number_of_pulses[pt] % XY_pulses != 0 or Number_of_pulses[pt] < XY_pulses*3:
                    raise Exception('Error: Number of pulses should be a multiple of' + str(XY_pulses) + 'and more pulses than ' + str(XY_pulses*3))

            simple_el_dec_start = Gate('electron_decoupling', 'Carbon_Gate')
            simple_el_dec_middle = Gate('electron_decoupling', 'Carbon_Gate')
            simple_el_dec_end = Gate('electron_decoupling', 'Carbon_Gate')

            if self.params['DD_in_eigenstate']:
                gate_seq = [simple_el_dec_middle]
            else:
                gate_seq = [simple_el_dec_start,simple_el_dec_middle,simple_el_dec_end]

            #Start element
            simple_el_dec_start.N = XY_pulses
            simple_el_dec_start.tau = tau_list[pt]
            simple_el_dec_start.scheme = 'single_block_repeating_elements_start'
            simple_el_dec_start.prefix = 'start_element_pt' +  str(pt)
            self.generate_decoupling_sequence_elements(simple_el_dec_start)
            simple_el_dec_start.reps = 1

            #Middle element
            simple_el_dec_middle.N = XY_pulses
            simple_el_dec_middle.tau = tau_list[pt]
            simple_el_dec_middle.scheme = 'single_block_repeating_elements_middle'
            simple_el_dec_middle.prefix = 'middle_element_pt' +  str(pt)
            self.generate_decoupling_sequence_elements(simple_el_dec_middle)
            if self.params['DD_in_eigenstate']:
                simple_el_dec_middle.reps = divmod(Number_of_pulses[pt],XY_pulses)[0]
            else:
                simple_el_dec_middle.reps = divmod(Number_of_pulses[pt],XY_pulses)[0]-2
                print simple_el_dec_middle.reps
            
            #End element
            simple_el_dec_end.N = XY_pulses
            simple_el_dec_end.tau = tau_list[pt]
            simple_el_dec_end.scheme = 'single_block_repeating_elements_end'
            simple_el_dec_end.prefix = 'end_element_pt' +  str(pt)
            self.generate_decoupling_sequence_elements(simple_el_dec_end)
            simple_el_dec_end.reps = 1

            simple_el_dec_start.scheme = 'single_block'
            simple_el_dec_middle.scheme = 'single_block'
            simple_el_dec_end.scheme = 'single_block'
        

            ## Combine to AWG sequence that can be uploaded #
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq)

            combined_list_of_elements.extend(list_of_elements)
            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)

        if upload:
            print 'uploading list of elements'
            # qt.pulsar.upload(*combined_list_of_elements)
            print ' uploading sequence'
            # qt.pulsar.program_sequence(combined_seq)
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)
        else:
            print 'upload = false, no sequence uploaded to AWG'

class Electrontransfercalibration_V2(DynamicalDecoupling):
    ''' 
    This class is used to calibrate the electron state transfer gate from m1 to p1 and vice versa. It does a simple electron experiment where the electron is
    initializec, put in a superposition on one transition, transferred to the other transition, and then readout while sweeping the phase. This script is used
    to calibrate the gate.dely and gate.second_pi_phase of the transfer gate.

    Invert_pop_ro can be used to measure all 3 of the populations instead of only 1.
    '''
    mprefix = 'E_tranfer_calib_V2'
    
    def generate_sequence(self, upload = True, debug = False):

        pts= self.params['pts']

        #initialize empty list of elements and sequence.
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('E_tranfer_calib_V2')
      
        for pt in range(pts):
            gate_seq=[]
            ###start with N mbi to initialize electron in eigenstate 0###
            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]; gate_seq.extend(mbi_seq)
            #define the pulses
            ### Wait for MBI to initialize electron####

            wait_after_mbi = Gate('Wait_after_mbi'+str(pt),'passive_elt',
                    wait_time=0.0003,go_to_element = mbi,
                    specific_transition = self.params['transfer_begin'])
           
            init_y = Gate('Initial_y_pt'+str(pt),'electron_Gate',
                    Gate_operation ='pi2',
                    phase = 0,
                    specific_transition = self.params['transfer_begin'],
                    el_state_after_gate = 'sup')

            final_y = Gate('Final_y_pt'+str(pt),'electron_Gate',
                    Gate_operation ='pi2',
                    phase = self.params['sweep_pts'][pt],
                    specific_transition = self.params['transfer_end'])

            invert_RO = Gate('final_pi_pulse'+str(pt),'electron_Gate',
                    Gate_operation = 'pi',
                    specific_transition = None)

            RO_Trigger = Gate('RO_trig_pt'+str(pt),'Trigger',
                    wait_time=10e-6,
                    el_state_before_gate = self.params['electron_readout_orientation'],
                    specific_transition = self.params['transfer_end'])
            

            
            gate_seq.extend([wait_after_mbi,init_y,final_y])
            
            ### cHECK ALL THREE POPULATIONS ###

            if self.params['invert_pop_ro'] == True:
                if self.params['readout_pop']=='_0':
                    print 'im not inverting anything'
                elif self.params['readout_pop']=='_m1':
                    invert_RO.specific_transition='_m1'
                    gate_seq.extend([invert_RO])
                elif self.params['readout_pop']=='_p1':
                    invert_RO.specific_transition='_p1'
                    gate_seq.extend([invert_RO])

                

            #### Add the readout trigger and make sequence ###

            gate_seq.extend([RO_Trigger])
            gate_seq = self.generate_AWG_elements(gate_seq,pt)

            ###Upload to AWG###

            list_of_elements, seq=self.combine_to_AWG_sequence(gate_seq,explicit=True)

            combined_list_of_elements.extend(list_of_elements)

            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)
        
        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

################################################################
##########   Carbon intialization and control classes   ########
################################################################

class MBI_C13(DynamicalDecoupling):
    mprefix = 'single_carbon_initialised'
    adwin_process = 'MBI_multiple_C13' 
    '''
    Class specifies a different adwin script to be used.
    gate sequence functions that use carbon initialisation are located in this class
    '''
    def autoconfig(self):

        #Convervting laser powers to AOM voltages
        self.params['A_SP_voltage_after_C13_MBI'] = (self.A_aom.power_to_voltage(
                    self.params['A_SP_amplitude_after_C13_MBI']))
        self.params['E_SP_voltage_after_C13_MBI'] = (self.E_aom.power_to_voltage(
                    self.params['E_SP_amplitude_after_C13_MBI']))
        self.params['E_C13_MBI_RO_voltage'] = (self.E_aom.power_to_voltage(
                    self.params['E_C13_MBI_RO_amplitude']))

        self.params['A_SP_voltage_after_MBE'] = (self.A_aom.power_to_voltage(
                    self.params['A_SP_amplitude_after_MBE']))
        self.params['E_SP_voltage_after_MBE'] = (self.E_aom.power_to_voltage(
                    self.params['E_SP_amplitude_after_MBE']))
        self.params['E_MBE_RO_voltage'] = (self.E_aom.power_to_voltage(
                    self.params['E_MBE_RO_amplitude']))

        self.params['E_Parity_RO_voltage'] = (self.E_aom.power_to_voltage(
                    self.params['E_Parity_RO_amplitude']))

        self.params['min_dec_duration'] = self.params['min_dec_tau']*self.params['dec_pulse_multiple']*2

        self.params['Carbon_init_RO_wait'] = (self.params['C13_MBI_RO_duration']+self.params['SP_duration_after_C13'])*1e-6+20e-6

        ### necessary if your setup does not have two microwave sources. NK 12-05-2016
        ### this gives all carbons the same specific transition.
        if not self.params['multiple_source']:
            for i in range(10):
                self.params['C'+str(i+1)+'_dec_trans'] = self.params['electron_transition']



        DynamicalDecoupling.autoconfig(self)

        self.physical_adwin.Set_Data_Long(
                np.array(self.params['C13_MBI_threshold_list'], dtype=int), 40, 1, self.params['Nr_C13_init'])

    def save(self, name='adwindata'):
        reps = self.adwin_var('completed_reps')
        sweeps = self.params['pts'] * self.params['reps_per_ROsequence']
        if self.params['Nr_parity_msmts'] == 0:
            parity_reps = 1
        else:
            parity_reps =  reps*self.params['Nr_parity_msmts']


        self.save_adwin_data(name,
                [   ('CR_before', sweeps),
                    ('CR_after', sweeps),
                    ('N_MBI_attempts', sweeps),
                    ('statistics', 10),
                    ('ssro_results', reps),
                    ('N_MBI_starts', 1),
                    ('N_MBI_success', 1),
                    ('C13_MBI_starts', 20),
                    ('C13_MBI_success', 20),
                    ('C13_MBE_starts', 20),
                    ('C13_MBE_success', 20),
                    ('parity_RO_results', parity_reps)
                    ])
        return

    def print_carbon_phases(self,gate,carbon_list,verbose=False):
        """
        Prints the phases of all involved carbons before and after a gate object
        Commonly used for debugging
        """
        if not verbose:
            return

        else:
            print_string = '[ '

            ### handle the before phases
            for c in carbon_list:
                if gate.C_phases_before_gate[c] is None:
                    addendum =  'None ,'
                else:
                    addendum =  " %.3f ," %(gate.C_phases_before_gate[c]/np.pi*180)
                print_string = print_string + addendum
            print print_string[:-2]+" ]"
            

            print_string = '[ '
            for c in carbon_list:
                if gate.C_phases_after_gate[c] is None:
                    addendum =  'None ,'
                else:
                    addendum =  " %.3f ," %(gate.C_phases_after_gate[c]/np.pi*180)
                print_string = print_string + addendum
            print print_string[:-2]+" ]"



    def initialize_carbon_echogate(self,
            prefix                  = 'init_C',
            go_to_element           = 'MBI_1',
            wait_for_trigger        = True,
            pt                      = 1,
            addressed_carbon        = 1,
            C_init_state            = 'up',
            el_RO_result            = '0',
            el_after_init           = '0',
            wait_time = 4e-6):

        """
        Class to intialize a carbon spin with the 'Echo Gate'
        """

        if type(go_to_element) != str:
            go_to_element = go_to_element.name

        ### Generate sequence    
        ################################
        carbon_init_seq=[]

        # f0=self.params['C'+str(addressed_carbon)+'_freq_0']
        # f1=self.params['C'+str(addressed_carbon)+'_freq_1']
        # HalfWaittime=round((1/np.abs(f1-f0))/4.,9)

        HalfWaittime=wait_time/2.
        print 'Wait: ', 2*HalfWaittime
        #the two wait gates to be put in the beginning and end

        wait_gate1 = Gate(prefix+'_Wait_gate1_'+str(pt),'passive_elt',
                             wait_time = round(HalfWaittime,9))
        wait_gate2 = Gate(prefix+'_Wait_gate2_'+str(pt),'passive_elt',
                             wait_time = round(HalfWaittime,9))

        ###
        ## unconditional rotations on the two spins
        C_uncond_Pi = Gate(prefix+'_uncond_Pi'+str(pt), 'Carbon_Gate',
                Carbon_ind = self.params['Carbon_nr'],
                N = self.params['C'+str(addressed_carbon)+'_uncond_pi_N'][0],
                tau = self.params['C'+str(addressed_carbon)+'_uncond_tau'][0],
                phase = self.params['C13_X_phase'])

        print 'N: ', self.params['C'+str(addressed_carbon)+'_uncond_pi_N'][0]
        print 'tau: ', self.params['C'+str(addressed_carbon)+'_uncond_tau'][0]
        #wait_gate1.C_phases_after_gate=10*[0]


        E_Pi=Gate(prefix+'E_Pi'+str(pt),'electron_Gate',
                                    Gate_operation='pi',
                                    phase = self.params['X_phase'])

        C_init_RO_Trigger = Gate(prefix+str(addressed_carbon)+'_RO_trig_pt'+str(pt),'Trigger',
                wait_time= self.params['Carbon_init_RO_wait'],
                event_jump = 'next',
                go_to = go_to_element,
                el_state_before_gate = el_RO_result)

        ###Before piecing the sequence together, two pi/2 pulses on the elctronic state need to be defined
        E_init_y = Gate(prefix+'E'+str(addressed_carbon)+'_y_pt'+str(pt),'electron_Gate',
            Gate_operation ='pi2',
            wait_for_trigger = wait_for_trigger,
            phase =self.params['Y_phase'])

        if C_init_state == 'down':
            RO_phase=self.params['X_phase']+180
        else:
            RO_phase=self.params['X_phase']


        E_RO_x = Gate(prefix+'E'+str(addressed_carbon)+'_x_pt'+str(pt),'electron_Gate',
            Gate_operation ='pi2',
            phase =RO_phase)

        ### Piece the sequence together.
        carbon_init_seq=[E_init_y,wait_gate1,C_uncond_Pi,E_Pi,wait_gate2,E_RO_x,C_init_RO_Trigger]


        C_init_elec_X = Gate(prefix+str(addressed_carbon)+'_elec_X_pt'+str(pt),'electron_Gate',
                Gate_operation='pi',
                phase = self.params['X_phase'],
                el_state_after_gate = '1')

        if el_after_init =='1':
            carbon_init_seq.append(C_init_elec_X)

        return carbon_init_seq

    def readout_single_carbon_echogate(self,
        prefix              = 'C_RO',
        pt                  =  1,
        addressed_carbon              =  3,
        RO_trigger_duration = 116e-6,
        el_RO_result        = '0',
        go_to_element       = 'next', event_jump_element = 'next',
        readout_orientation = 'positive',
        el_state_in         = 0,
        wait_time           = 3e-6
        ):

        '''
        Function to create a AWG sequence for Carbon spin measurements with the EchoGate.
        carbon                  gives the carbon_nr which is read-out
        el_RO_result            the electron state for the final trigger element (i.e. the electron measurement outcome)
        readout_orientation     sets the orientation of the electron readout (positive or negative)
        el_state_in             the state of the electron before the measurement
        wait_times              the evolution before and after the unconditional pi-pulse.
        '''

        ##############################
        ### Check input parameters ###
        ##############################

        if (type(go_to_element) != str) and (go_to_element != None):
            go_to_element = go_to_element.name

        #######################
        ### Create sequence ###
        #######################

        carbon_RO_seq = []

        ### Add initial pi/2 pulse (always) ###
        carbon_RO_seq.append(
                Gate(prefix+'_y_pi2_init'+str(pt),'electron_Gate',
                Gate_operation='pi2',
                phase = self.params['Y_phase']))

        # f0=self.params['C'+str(addressed_carbon)+'_freq_0']
        # f1=self.params['C'+str(addressed_carbon)+'_freq_1']
        #HalfWaittime=(1/np.abs(f1-f0))/4.

        HalfWaittime=wait_time/2.
        print 'Wait: ', 2*HalfWaittime
        ##the two wait gates to be put in the beginning and end

        wait_gate1 = Gate(prefix+'_Wait_gate1_'+str(pt),'passive_elt',
                             wait_time = round(HalfWaittime,9))
        wait_gate2 = Gate(prefix+'_Wait_gate2_'+str(pt),'passive_elt',
                             wait_time = round(HalfWaittime,9))

        ###
        ## unconditional rotations on the two spins
        C_uncond_Pi = Gate(prefix+'_uncond_Pi'+str(pt), 'Carbon_Gate',
                Carbon_ind = self.params['Carbon_nr'],
                N = self.params['C'+str(addressed_carbon)+'_uncond_pi_N'][0],
                tau = self.params['C'+str(addressed_carbon)+'_uncond_tau'][0],
                phase = self.params['C13_X_phase'])

        print 'N: ', self.params['C'+str(addressed_carbon)+'_uncond_pi_N'][0]
        print 'tau: ', self.params['C'+str(addressed_carbon)+'_uncond_tau'][0]
        #wait_gate1.C_phases_after_gate=10*[0]


        E_Pi=Gate(prefix+'E_Pi'+str(pt),'electron_Gate',
                                    Gate_operation='pi',
                                    phase = self.params['X_phase'])

        C_init_RO_Trigger = Gate(prefix+str(addressed_carbon)+'_RO_trig_pt'+str(pt),'Trigger',
                wait_time= self.params['Carbon_init_RO_wait'],
                event_jump = 'next',
                go_to = go_to_element,
                el_state_before_gate = el_RO_result)

        ###Before assembling the sequence together, two pi/2 pulses on the elctronic state need to be defined
        E_init_y = Gate(prefix+'E'+str(addressed_carbon)+'_y_pt'+str(pt),'electron_Gate',
            Gate_operation ='pi2',
            phase =self.params['Y_phase'])

        ### Piece the sequence together.
        carbon_RO_seq=[E_init_y,wait_gate1,C_uncond_Pi,E_Pi,wait_gate2]


        ### Add final pi/2 and Trigger ###
            ### set the final electron pi2 pulse phase depending on the number of qubits RO (4 options)
        Final_pi2_pulse_phase = np.mod((self.params['X_phase']),360)
        Final_pi2_pulse_phase_negative = np.mod(Final_pi2_pulse_phase+180,360)

        if (readout_orientation == 'positive' and el_state_in == 0) or (readout_orientation == 'negative' and el_state_in == 1):
            carbon_RO_seq.append(
                    Gate(prefix+'_pi2_final_phase=' +str(Final_pi2_pulse_phase) + '_' +str(pt),'electron_Gate',
                    Gate_operation='pi2',
                    phase = Final_pi2_pulse_phase))

        elif (readout_orientation == 'negative' and el_state_in == 0) or (readout_orientation == 'positive' and el_state_in == 1):
            carbon_RO_seq.append(
                    Gate(prefix+'_-pi2_final_phase=' +str(Final_pi2_pulse_phase) + '_' +str(pt),'electron_Gate',
                    Gate_operation='pi2',
                    phase = Final_pi2_pulse_phase_negative))


        carbon_RO_seq.append(
            Gate(prefix+'_Trigger_'+str(pt),'Trigger',
            wait_time = RO_trigger_duration,
            go_to = go_to_element, event_jump = event_jump_element,
            el_state_before_gate = el_RO_result))

        return carbon_RO_seq

    # def initialize_carbon_sequence(self,
    #         prefix                  = 'init_C',
    #         go_to_element           = 'MBI_1',
    #         wait_for_trigger        = True,
    #         initialization_method   = 'swap',
    #         pt                      = 1,
    #         addressed_carbon        = 1,
    #         C_init_state            = 'up',
    #         el_RO_result            = '0',
    #         el_after_init           = '0',
    #         do_wait_after_pi        = False,
    #         swap_phase              = 0
    #         ):
    #     '''
    #     By THT
    #     Supports Swap or MBI initialization
    #     state can be 'up' or 'down'
    #     Swap init: up -> 0, down ->1
    #     MBI init: up -> +X, down -> -X
    #     '''
       
    #     if type(go_to_element) != str:
    #         go_to_element = go_to_element.name

   
    #     if C_init_state ==    'up':            
    #         C_init_y_phase = self.params['Y_phase']

    #     elif C_init_state ==  'down':           
    #         C_init_y_phase = self.params['Y_phase']+180


    #     ### Define elements and gates
    #     C_init_y = Gate(prefix+str(addressed_carbon)+'_y_pt'+str(pt),'electron_Gate',
    #             Gate_operation ='pi2',
    #             wait_for_trigger = wait_for_trigger,
    #             phase = C_init_y_phase)

    #     C_init_Ren_a = Gate(prefix+str(addressed_carbon)+'_Ren_a_pt'+str(pt), 'Carbon_Gate',
    #             Carbon_ind = addressed_carbon,
    #             phase = self.params['C13_X_phase'])

    #     C_init_x = Gate(prefix+str(addressed_carbon)+'_x_pt'+str(pt),'electron_Gate',
    #             Gate_operation='pi2',
    #             phase = self.params['X_phase'])

    #     C_init_Ren_b = Gate(prefix+str(addressed_carbon)+'_Ren_b_pt'+str(pt), 'Carbon_Gate',
    #             Carbon_ind = addressed_carbon,
    #             phase = self.params['C13_Y_phase']+180+swap_phase)

    #     C_init_RO_Trigger = Gate(prefix+str(addressed_carbon)+'_RO_trig_pt'+str(pt),'Trigger',
    #             wait_time= self.params['Carbon_init_RO_wait'],
    #             event_jump = 'next',
    #             go_to = go_to_element,
    #             el_state_before_gate = el_RO_result)

    #     ## TODO: THT, temporary fix that removed pi-puls that is bugged
    #     C_init_elec_X = Gate(prefix+str(addressed_carbon)+'_elec_X_pt'+str(pt),'electron_Gate',
    #             Gate_operation='pi',
    #             phase = self.params['X_phase'],
    #             el_state_after_gate = '1')
    #     wait_gate = (Gate('Wait_gate_after_el_pi_pt'+str(pt),'passive_elt',
    #                  wait_time = 3e-6))

    #     ### Set sequence
    #     if initialization_method == 'swap':  ## Swap initializes into 1 or 0
    #         carbon_init_seq = [C_init_y, C_init_Ren_a, C_init_x, C_init_Ren_b, C_init_RO_Trigger]
    #     elif initialization_method == 'MBI': ## MBI initializes into +/-X
    #         carbon_init_seq = [C_init_y, C_init_Ren_a, C_init_x, C_init_RO_Trigger]
    #     elif initialization_method == 'mixed': ## initializes into a mixed state
    #         carbon_init_seq = [C_init_Ren_a, C_init_x, C_init_Ren_b, C_init_RO_Trigger] #Can the first C_init_Ren be removed?

    #     else:
    #         print 'Error initialization method (%s) not recognized, supported methods are "swap", "MBI", None' %initialization_method
    #         return False

    #     ### TODO: THT, temporary fix for pi-pulse in Trigger, later redo trigger element workings
    #     ### I uncommented this part of the initialization for the Carbon T1 measurements. Norbert 20141104
    #     if el_after_init =='1':
    #         carbon_init_seq.append(C_init_elec_X)
    #         if do_wait_after_pi:
    #             carbon_init_seq.append(wait_gate)

    #     return carbon_init_seq

    def initialize_carbon_sequence(self,
            prefix                  = 'init_C',
            go_to_element           = 'MBI_1',
            wait_for_trigger        = True,
            initialization_method   = 'swap',
            pt                      = 1,
            addressed_carbon        = 1,
            C_init_state            = 'up',
            el_RO_result            = '0',
            el_after_init           = '0',
            do_wait_after_pi        = False,
            swap_phase              = 0,
            wait_time               = 0
            ):
        
        '''
        By THT
        Supports Swap or MBI initialization
        state can be 'up' or 'down'
        Swap init: up -> 0, down ->1
        MBI init: up -> +X, down -> -X
        '''
        '''
        Modified by SK

        Changed old version to allow for a wait gate after 
        the second conditional gate for swap 

        '''
        if type(go_to_element) != str:
            go_to_element = go_to_element.name
   
        if C_init_state ==    'up':            
            C_init_y_phase = self.params['Y_phase']

        elif C_init_state ==  'down':           
            C_init_y_phase = self.params['Y_phase']+180


        ### Define elements and gates
        C_init_y = Gate(prefix+str(addressed_carbon)+'_y_pt'+str(pt),'electron_Gate',
                Gate_operation ='pi2',
                wait_for_trigger = wait_for_trigger,
                phase = C_init_y_phase,
                specific_transition = self.params['C'+str(addressed_carbon)+'_dec_trans'])

        C_init_Ren_a = Gate(prefix+str(addressed_carbon)+'_Ren_a_pt'+str(pt), 'Carbon_Gate',
                Carbon_ind = addressed_carbon,
                phase = self.params['C13_X_phase'],
                specific_transition = self.params['C'+str(addressed_carbon)+'_dec_trans'])

        C_init_Ren_a_y_init = Gate(prefix+str(addressed_carbon)+'_Ren_a_pt'+str(pt), 'Carbon_Gate',
                Carbon_ind = addressed_carbon,
                phase = self.params['C13_Y_phase'],
                specific_transition = self.params['C'+str(addressed_carbon)+'_dec_trans'])

        C_init_x = Gate(prefix+str(addressed_carbon)+'_x_pt'+str(pt),'electron_Gate',
                Gate_operation='pi2',
                phase = self.params['X_phase'],
                specific_transition = self.params['C'+str(addressed_carbon)+'_dec_trans'])

        C_init_Ren_b = Gate(prefix+str(addressed_carbon)+'_Ren_b_pt'+str(pt), 'Carbon_Gate',
                Carbon_ind = addressed_carbon,
                phase = self.params['C13_Y_phase']+180+swap_phase,
                specific_transition = self.params['C'+str(addressed_carbon)+'_dec_trans'])


        C_init_RO_Trigger = Gate(prefix+str(addressed_carbon)+'_RO_trig_pt'+str(pt),'Trigger',
                wait_time= self.params['Carbon_init_RO_wait'],
                event_jump = 'next',
                go_to = go_to_element,
                el_state_before_gate = el_RO_result,
                specific_transition = self.params['C'+str(addressed_carbon)+'_dec_trans'])



        ## TODO: THT, temporary fix that removed pi-puls that is bugged
        C_init_elec_X = Gate(prefix+str(addressed_carbon)+'_elec_X_pt'+str(pt),'electron_Gate',
                Gate_operation='pi',
                phase = self.params['X_phase'],
                el_state_after_gate = '1',
                specific_transition = self.params['C'+str(addressed_carbon)+'_dec_trans'])
        wait_gate = Gate('Wait_gate_after_el_pi_pt'+str(pt),'passive_elt',
                     wait_time = 3e-6,specific_transition = self.params['C'+str(addressed_carbon)+'_dec_trans'])
        # above is dirty hack


        ### Set sequence
        if initialization_method == 'swap':  ## Swap initializes into 1 or 0
            if wait_time != 0:
                # Gets rid of connection and phase DD elements and replaces them by a wait gate. By default this is not done
                wait_gate2 = (Gate('wait_gate_before_Ren_B'+str(pt),'passive_elt',
                             wait_time = wait_time, no_connection_elt = True))
                C_init_Ren_b.phase              = self.params['C13_X_phase']
                C_init_Ren_b.no_connection_elt  = True
                wait_gate2.C_phases_after_gate[addressed_carbon] = 'reset'

                carbon_init_seq = [C_init_y, C_init_Ren_a, C_init_x, wait_gate2, C_init_Ren_b,  C_init_RO_Trigger]
            else: 
                carbon_init_seq = [C_init_y, C_init_Ren_a, C_init_x, C_init_Ren_b, C_init_RO_Trigger]
        elif initialization_method == 'MBI': ## MBI initializes into +/-X
            carbon_init_seq = [C_init_y, C_init_Ren_a, C_init_x, C_init_RO_Trigger]

        elif initialization_method == 'MBI_y': ## MBI initializes into +/-X

            carbon_init_seq = [C_init_y, C_init_Ren_a_y_init, C_init_x, C_init_RO_Trigger]

        elif initialization_method == 'MBI_w_gate': ## MBI then gate initializes into 1 or 0 
            carbon_init_seq = [C_init_y, C_init_Ren_a, C_init_x, C_init_RO_Trigger, C_init_Ren_b]

        elif initialization_method == 'mixed': ## initializes into a mixed state
            carbon_init_seq = [C_init_Ren_a, C_init_x, C_init_Ren_b, C_init_RO_Trigger] #Can the first C_init_Ren be removed?

        else:
            print 'Error initialization method (%s) not recognized, supported methods are "swap", "MBI", "MBI_then_gate", "mixed"' %initialization_method
            return False

        ### TODO: THT, temporary fix for pi-pulse in Trigger, later redo trigger element workings
        ### I uncommented this part of the initialization for the Carbon T1 measurements. Norbert 20141104
        if self.params['multiple_source']:
            ##check wether the electron state needs to be inverted at the end of readout. The transition is specified by fid_transition, 
            if el_after_init!='_0' and el_after_init != '0':
                print 'adding pulse for electron state excited in', el_after_init

                carbon_init_seq.append(Gate(prefix+str(addressed_carbon)+'_aftergate'+'_elec_X_'+el_after_init+str(pt),'electron_Gate',
                    Gate_operation='pi',
                    phase = self.params['X_phase'],
                    el_state_after_gate = '1',
                    specific_transition = self.params['fid_transition']))
                wait_gate = Gate('Wait_gate_after_el_pi_pt'+str(pt),'passive_elt',
                    wait_time = 3e-6,specific_transition = el_after_init)
                if do_wait_after_pi:
                    carbon_init_seq.append(wait_gate)

        elif el_after_init =='1':
            carbon_init_seq.append(C_init_elec_X)
            if do_wait_after_pi:
                carbon_init_seq.append(wait_gate)

        return carbon_init_seq


    def initialize_electron_sequence(self,
        prefix                  = 'init_e',
        el_after_c_init         ='0',
        wait_for_trigger        = False,
        elec_init_state         = 'Z',
        pt                      = 1,):
        '''
        By SK
        Method to apply electron gates
        States can be X, -X, Y, -Y, Z, -Z
        '''

        ### Define elements and gates
        # init_el_y = Gate(prefix+str(addressed_carbon)+'_y_pt'+str(pt),'electron_Gate',
        #     Gate_operation ='pi2',
        #     wait_for_trigger = wait_for_trigger,
        #     phase = self.params['Y_phase'])

        #Define gates

        elec_minZ = Gate(prefix+'_elec_X_pt'+str(pt),'electron_Gate',
            Gate_operation='pi',
            phase = self.params['X_phase'],
            el_state_after_gate = '1')
        ## el_state_after_gate

        elec_toX = Gate(prefix+'_y_pt'+str(pt),'electron_Gate',
            Gate_operation='pi2',
            phase = self.params['Y_phase'])

        elec_minX = Gate(prefix+'_-y_pt'+str(pt),'electron_Gate',
            Gate_operation='pi2',
            phase = self.params['Y_phase'] + 180)

        elec_toY = Gate(prefix+'_x_pt'+str(pt),'electron_Gate',
            Gate_operation='pi2',
            phase = self.params['X_phase'] + 180)

        elec_minY = Gate(prefix+'_-x_pt'+str(pt),'electron_Gate',
            Gate_operation='pi2',
            phase = self.params['X_phase'])

        wait = Gate(prefix+'_wait_pt'+str(pt),'passive_elt',
            wait_time=3e-6)

        ### THIS!
        # elec_toX =  pulse.cp(init_el_x, phase = self.params['Y_phase']       ) ### X
        # elec_toY =  pulse.cp(iRnit_el_x, phase = self.params['X_phase']       ) ### Y

        # elec_minX = pulse.cp(init_el_x, phase = self.params['Y_phase'] + 180) ###-X
        # elec_minY = pulse.cp(init_el_x, phase = self.params['X_phase'] + 180) ###-Y
        # elec_minZ = pulse.cp(init_elec_X, phase = self.params['X_phase']    ) ### -Z

        ### Apply electron gate
        electron_init_seq = []
        # check electron state
        if elec_init_state in ['Z','mZ','X','mX','Y','mY']:
            # electron either in 0 or 1, so rotate in one way or the opposite direction
            if el_after_c_init == '0':
                if elec_init_state    == 'mZ': ## -Z gate, i.e. rotation around X of pi
                    electron_init_seq.append(elec_minZ)
                elif elec_init_state  == 'Z': ## Z is pass
                    electron_init_seq.append(wait)
                elif elec_init_state  == 'X': ## y pi/2 gate
                    electron_init_seq.append(elec_toX)
                elif elec_init_state  == 'mX': ## -y pi/2 gate
                    electron_init_seq.append(elec_minX)
                elif elec_init_state  == 'Y': ##  pi/2 around x gate
                    electron_init_seq.append(elec_toY)
                elif elec_init_state  == 'mY': ## -pi/2 around x gate
                    electron_init_seq.append(elec_minY)

            elif el_after_c_init == '1':
                if elec_init_state    == 'Z':  #Do nothing
                    electron_init_seq.append(elec_minZ)
                elif elec_init_state  == 'mZ': ## -Z gate, i.e. rotation around X of pi
                    electron_init_seq.append(wait)
                elif elec_init_state  == 'X': ## y pi/2 gate
                    electron_init_seq.append(elec_minX)
                elif elec_init_state  == 'mX': ## -y pi/2 gate
                    electron_init_seq.append(elec_toX)
                elif elec_init_state  == 'Y': ##  pi/2 around x gate
                    electron_init_seq.append(elec_minY)
                elif elec_init_state  == 'mY': ## -pi/2 around x gate
                    electron_init_seq.append(elec_toY)
            else:
                print 'Incorrect initial electron state'
        else:
            print 'Error, electron state (%s) not recognized, supported states are "X, mX, Y, mY, Z, mZ"' %elec_init_state
            return False

        # prints
        # print '@ end of initialize elec sequence part, state: ' + str(elec_init_state)
        electron_init_seq[0].wait_for_trigger = wait_for_trigger
        return electron_init_seq  

    def carbon_swap_gate(self,
            prefix                  = 'swap_C',
            go_to_element           = 'MBI_1',
            pt                      = 1,
            addressed_carbon        = 1,
            el_RO_result            = '0',
            do_wait_after_pi        = False,
            RO_after_swap           = True):
        #el_RO_result, not important.. only for RO trigger. Just as el_after_init is not important and do_wait_after_pi.
        '''
        By SK
        Gate performs swap operation between electron and carbon state
        Possible states: X, -X, Y, -Y, Z, -Z
        '''


        if type(go_to_element) != str:
            go_to_element = go_to_element.name


        ### Define elements and gates
        C_init_y = Gate(prefix+str(addressed_carbon)+'_y_pt'+str(pt),'electron_Gate',
                Gate_operation ='pi2',
                phase = self.params['Y_phase'])

        C_init_y2 = Gate(prefix+str(addressed_carbon)+'_y2_pt'+str(pt),'electron_Gate',
                Gate_operation ='pi2',
                phase = self.params['Y_phase']+180)

        # Removed 180 phase here
        C_init_Ren_y = Gate(prefix+str(addressed_carbon)+'_Ren_a_pt'+str(pt), 'Carbon_Gate',
                Carbon_ind = addressed_carbon,
                phase = self.params['C13_Y_phase']+180)

        C_init_Ren_x = Gate(prefix+str(addressed_carbon)+'_Ren_a2_pt'+str(pt), 'Carbon_Gate',
                Carbon_ind = addressed_carbon,
                phase = self.params['C13_X_phase'])

        carbon_swap_seq = [C_init_Ren_y, C_init_y, C_init_Ren_x, C_init_y2]
        if RO_after_swap == True:
            #### Includes repump###
            RO_electron = Gate(prefix+str(addressed_carbon)+'swap_RO_trig_pt'+str(pt),'Trigger',
                wait_time = self.params['Carbon_init_RO_wait'],
                event_jump = 'next',
                go_to = go_to_element,
                el_state_before_gate = '0')
            carbon_swap_seq.append(RO_electron)
        else:
            ### Seperate repumper. Repump can also be done by adding RO step in carbon_swap_seq ###
            Laser = Gate('Repump_to_0'+str(pt),'Trigger')
            Laser.channel = 'AOM_Newfocus'
            Laser.elements_duration = self.params['Repump_duration']
            # Laser.el_state_before_gate ='0' ### this is used in the carbon RO sequence generator.
            carbon_swap_seq.append(Laser)


        return carbon_swap_seq

    # PH - unconditional carbon gates need different phase offsets to work. This adds these offsets in to make things work nicely.
    # To use this, the carbon must first be calibrated using carbon_calibration.py
    def unconditional_carbon_gate(self,
        name,
        Carbon_ind = 1,
        phase = 0,
        **kw):

        el_trans = self.params['electron_transition']
    
        phase_offset = self.params['C'+str(Carbon_ind)+'_unc_phase_offset'+el_trans]
        extra_phase = (self.params['C'+str(Carbon_ind)+'_unc_extra_phase_correction_list'+el_trans][Carbon_ind] 
            + phase_offset)

        # Need phase offset to adjust phase, plus extra phase to bring it back! 
        return Gate(name, 'Carbon_Gate',
            Carbon_ind  = Carbon_ind,
            N           = self.params['C' + str(Carbon_ind) + '_unc_N' + el_trans][0],
            tau         = self.params['C' + str(Carbon_ind) + '_unc_tau'+el_trans][0],
            phase       = phase-phase_offset,
            extra_phase_after_gate = extra_phase,**kw)

    def carbon_swap_gate_multi_options(self,
            prefix                  = 'swap_eC',
            go_to_element           = 'MBI_1',
            pt                      = 1,
            addressed_carbon        = 1,
            el_RO_result            = '0',
            do_wait_after_pi        = False,
            RO_after_swap           = True,
            swap_type               = 'swap_w_init'):
        #el_RO_result, not important.. only for RO trigger. Just as el_after_init is not important and do_wait_after_pi.
        '''
        By SK and PeeeeeH
        Gate performs swap operation between electron and carbon state
        Possible states: X, -X, Y, -Y, Z, -Z
        Does one of two types of swaps:
            1) swap_w_init:  C13 has been initialised in |Z|, swap sequence requires less gates
                |Ren_-y| - |y| - |Ren_x| - |-y| 
            2) swap_wo_init: C13 in mixed state, put C13 in rotated basis after swap. The full sequence
                |Ren_y| - |ym| - |Ren_x| - |xm, y_c| - |Ren_x|
                 
        '''

        if type(go_to_element) != str:
            go_to_element = go_to_element.name


        #####################
        # 1q electron gates #
        #####################
        e_y = Gate(prefix+str(addressed_carbon)+'_y_pt'+str(pt),'electron_Gate',
                Gate_operation ='pi2',
                phase = self.params['Y_phase'])

        e_ym = Gate(prefix+str(addressed_carbon)+'_ym_pt'+str(pt),'electron_Gate',
                Gate_operation ='pi2',
                phase = self.params['Y_phase']+180)

        e_x = Gate(prefix+str(addressed_carbon)+'_x_pt'+str(pt),'electron_Gate',
                Gate_operation ='pi2',
                phase = self.params['X_phase'])

        e_xm = Gate(prefix+str(addressed_carbon)+'_xm_pt'+str(pt),'electron_Gate',
                Gate_operation ='pi2',
                phase = self.params['X_phase']+180)

        #bitching about uniqueness
        #e_x2 = Gate(prefix+str(addressed_carbon)+'_x2_pt'+str(pt),'electron_Gate',
        #        Gate_operation ='pi2',
        #        phase = self.params['X_phase'])


        #####################
        # Conditional gates #
        #####################
        C_Ren_ym = Gate(prefix+str(addressed_carbon)+'_Ren_ym_pt'+str(pt), 'Carbon_Gate',
                Carbon_ind = addressed_carbon,
                phase = self.params['C13_Y_phase']+180)

        C_Ren_y = Gate(prefix+str(addressed_carbon)+'_Ren_y_pt'+str(pt), 'Carbon_Gate',
                Carbon_ind = addressed_carbon,
                phase = self.params['C13_Y_phase'])

        C_Ren_x = Gate(prefix+str(addressed_carbon)+'_Ren_x_pt'+str(pt), 'Carbon_Gate',
                Carbon_ind = addressed_carbon,
                phase = self.params['C13_X_phase'])

        # bitching about uniqueness
        C_Ren_x_2 = Gate(prefix+str(addressed_carbon)+'_Ren_x_2_pt'+str(pt), 'Carbon_Gate',
                Carbon_ind = addressed_carbon,
                phase = self.params['C13_X_phase'])

        C_Ren_xm = Gate(prefix+str(addressed_carbon)+'_Ren_xm_pt'+str(pt), 'Carbon_Gate',
                Carbon_ind = addressed_carbon,
                phase = self.params['C13_X_phase']+180)

        ########################
        # Un-conditional gates #
        ########################

        C_unc_y = self.unconditional_carbon_gate(prefix+str(addressed_carbon)+'_unc_y_pt'+str(pt),
            Carbon_ind  = addressed_carbon,
            phase       = self.params['C13_Y_phase'])

        C_unc_x = self.unconditional_carbon_gate(prefix+str(addressed_carbon)+'_unc_y_pt'+str(pt),
            Carbon_ind  = addressed_carbon,
            phase       = self.params['C13_X_phase'])

        #print 'swap_type = ' + swap_type 
        if swap_type    == 'swap_w_init':
            carbon_swap_seq = [C_Ren_y,e_x,C_Ren_x,e_ym]
            
        elif swap_type  ==  'swap_wo_init':
            carbon_swap_seq = [C_Ren_y, e_ym, C_Ren_x, C_unc_y, e_xm, C_Ren_x_2] #for actual swap, need zm rotation on both electron and carbon at the end

        elif swap_type == 'prob_init':
            carbon_swap_seq = [C_Ren_ym, e_ym]

        else: 
            return 'Unsupported swap type (location: DD_2.carbon_swap_gate)'
       
        if RO_after_swap == True:
            #### Includes repump###
            RO_electron = Gate(prefix+str(addressed_carbon)+'swap_RO_trig_pt'+str(pt),'Trigger',
                wait_time = self.params['Carbon_init_RO_wait'],
                event_jump = 'next',
                go_to = go_to_element,
                el_state_before_gate = '0')
            carbon_swap_seq.append(RO_electron)
        else:

            ### Seperate repumper. Repump can also be done by adding RO step in carbon_swap_seq ###
            Laser = Gate('Repump_to_0'+str(pt),'Trigger')
            Laser.channel = 'AOM_Newfocus'
            Laser.elements_duration = self.params['Repump_duration']
            Laser.el_state_before_gate ='0' ### this is used in the carbon RO sequence generator.
            carbon_swap_seq.append(Laser)


        return carbon_swap_seq

    def readout_carbon_sequence(self,
        prefix              = 'C_RO',
        pt                  =  1,
        carbon_list         = [1, 4],
        RO_basis_list       = ['X','X'],
        RO_trigger_duration = 116e-6,
        el_RO_result        = '0',
        go_to_element       = 'next', event_jump_element = 'next',
        readout_orientation = 'positive',
        el_state_in         = 0,
        Zeno_RO             = False,
        phase_error         = 10*[0],
        add_wait_to_Zeno    = 0,
        do_init_pi2         = True,
        flip_RO             = False,
        do_RO_electron      = False,
        wait_for_trigger    = False,
        addressed_carbon    = 1
        ):
        
        '''
        Function to create a general AWG sequence for Carbon spin measurements.
        carbon_list             gives the order of the carbons that the measurement will be performed on
        RO_basis_list           gives the basis in wich each Carbon spin will be measured
        el_RO_result            the electron state for the final trigger element (i.e. the electron measurement outcome)
        readout_orientation     sets the orientation of the electron readout (positive or negative)
        el_state_in             the state of the electron before the measurement
        Zeno_RO                 boolean, if true: Turns a laser via the AWG on. Circumvents the ADWIN.
        phase_error             to apply an extra phase BEFORE this gate (can be used for phase errors and phase correction) 
        add_wait_to_Zeno        time in seconds, if unequal to 0 --> puts a wait gate into the Zeno measurement.
        do_init_pi2             if the readoutsequence follows an invert_ro_sequence, do not start with a pi/2 pulse
        flip_RO                 flip the final pi2 pulse if you want to flip the readout result
        do_RO_electron          if do_RO_electron is true, and carbon list empty, readout the electron only
        wait_for_trigger        put a wait for trigger in the first element of the sequence
        '''


        # print 'el_state_in for the RO',el_state_in
        ##############################
        ### Check input parameters ###
        ##############################

        if (type(go_to_element) != str) and (go_to_element != None):
            go_to_element = go_to_element.name

        if len(carbon_list) != len(RO_basis_list):
            print 'Warning: #carbons does not match #RO bases'
            print 'carbon list: ',carbon_list
            print 'RO basis list: ',RO_basis_list

        if len(carbon_list) == 0 and do_RO_electron==False:
            print 'Warning: No Carbons selected for readout'
            return []

        # elif len(carbon_list) == 0 and do_RO_electron==True:
        #     print 'No Carbons selected for readout; reading out electron'
        carbons_to_RO = []
        number_of_carbons_to_RO = 0

        for jj, basis in enumerate(RO_basis_list):
            #checks how many carbons to read out and adds those in a list (in order of readout)
            if basis != 'I':   
                number_of_carbons_to_RO += 1
                carbons_to_RO.append(carbon_list[jj])

        if number_of_carbons_to_RO == 0 and do_RO_electron == False:
            return []
        
        #######################
        ### Create sequence ###
        #######################

        carbon_RO_seq = []

        ### Add basis rotations in case of Z-RO ###
        for kk, carbon_nr in enumerate(carbon_list):

            if RO_basis_list[kk] == 'Z' or RO_basis_list[kk] == '-Z':
                carbon_RO_seq.append( Gate(prefix + str(carbon_nr) + '_Ren_a_' + str(pt), 'Carbon_Gate',
                        Carbon_ind = carbon_nr, phase = 'reset',specific_transition = self.params['C'+str(carbon_nr)+'_dec_trans']))

        if do_init_pi2:           
         
            ### Add initial pi/2 pulse (always) with mw transition of first carbon to RO ###
            ### except when an invert RO sequence was done just before 
            ### (in that case the electron is still in a superposition)
            ### The mw freq of this pulse is determined by the first carbon to readout.
            carbon_RO_seq.append(
                Gate(prefix+'_y_pi2_init'+str(pt),'electron_Gate',
                Gate_operation='pi2',
                phase = self.params['Y_phase'],
                wait_for_trigger=wait_for_trigger,
                specific_transition=self.params['C'+str(carbons_to_RO[0])+'_dec_trans']))

        ### Add RO rotations ###
        for kk, carbon_nr in enumerate(carbon_list):


            if RO_basis_list[kk] != 'I':
                

                ### Set the RO_phase
                if RO_basis_list[kk] == 'X':
                    RO_phase = self.params['C13_X_phase'] - phase_error[kk]
                elif RO_basis_list[kk] == '-X':
                    RO_phase = self.params['C13_X_phase']+180 - phase_error[kk]
                elif RO_basis_list[kk] == 'Y':
                    RO_phase = self.params['C13_Y_phase'] - phase_error[kk]
                elif RO_basis_list[kk] == '-Y':
                    RO_phase = self.params['C13_Y_phase']+180 - phase_error[kk]
                elif RO_basis_list[kk] == '-Z':
                    RO_phase = np.mod(self.params['C13_Y_phase']+180*el_state_in,360)
                elif RO_basis_list[kk] == 'Z':
                    RO_phase = np.mod(self.params['C13_Y_phase']+180*(1-el_state_in),360)

                else:
                    RO_phase = RO_basis_list[kk]
                # print 'my readout basis is this so I will readout this carbon',RO_basis_list[kk],RO_phase 
                
                carbon_RO_seq.append(
                        Gate(prefix + str(carbon_nr) + '_Ren_b_' + str(pt), 'Carbon_Gate',
                        specific_transition      = self.params['C'+str(carbon_nr)+'_dec_trans'],
                        phase           = RO_phase, 
                        extra_phase_after_gate = phase_error[kk],
                        Carbon_ind=carbon_nr))

        if do_RO_electron != True:
            carbon_nr=carbons_to_RO[-1] 
            ### Add final pi/2 and Trigger with the mw transition of the last carbon ###
            ### set the final electron pi2 pulse phase depending on the number of qubits RO (4 options)
            ### The mw freq of this pulse is determined by the last carbon to readout.

            Final_pi2_pulse_phase = np.mod((180+self.params['Y_phase']) - np.mod(number_of_carbons_to_RO, 4) * 90, 360)
            Final_pi2_pulse_phase_negative = np.mod(Final_pi2_pulse_phase+180,360)

            #if you want an additional flip of the RO bases:        
            if flip_RO:
                Final_pi2_pulse_phase = np.mod(Final_pi2_pulse_phase+180,360)
                Final_pi2_pulse_phase_negative = np.mod(Final_pi2_pulse_phase_negative+180,360)

            if (readout_orientation == 'positive' and el_state_in == 0) or (readout_orientation == 'negative' and el_state_in == 1):
                carbon_RO_seq.append(
                        Gate(prefix+'_pi2_final_phase=' +str(Final_pi2_pulse_phase) + '_' +str(pt),'electron_Gate',
                        Gate_operation='pi2',
                        phase = Final_pi2_pulse_phase,
                        specific_transition = self.params['C'+str(carbon_nr)+'_dec_trans']))

            elif (readout_orientation == 'negative' and el_state_in == 0) or (readout_orientation == 'positive' and el_state_in == 1):
                # print 'RO negative or el state in =1!'
                carbon_RO_seq.append(
                        Gate(prefix+'_-pi2_final_phase=' +str(Final_pi2_pulse_phase) + '_' +str(pt),'electron_Gate',
                        Gate_operation='pi2',
                        phase = Final_pi2_pulse_phase_negative,
                        specific_transition=self.params['C'+str(carbon_nr)+'_dec_trans']))
        else:
            #carbon_nr=carbons_to_RO[-1] 
            #carbon_RO_seq.append(Gate(prefix+'Wait_gate_'+str(pt),'passive_elt',
            #    wait_time = 20e-6,specific_transition = self.params['C'+str(carbon_nr)+'_dec_trans']))      
            pass

        #if Zeno parity measurement then shoot a laser at the nv. don't bother the adwin with it.
        if Zeno_RO:
            Laser=Gate(prefix+'pump'+str(pt),'Trigger',
                duration=RO_trigger_duration,
                )
            Laser.channel='AOM_Newfocus'
            Laser.elements_duration=RO_trigger_duration
            Laser.el_state_before_gate='0'
            if add_wait_to_Zeno != 0:
                carbon_RO_seq.extend([Gate(prefix+'_msmt_wait'+str(pt),'passive_elt',
                                     wait_time = add_wait_to_Zeno)])
            carbon_RO_seq.append(Laser)

        else:
            carbon_nr=carbons_to_RO[-1] 
            carbon_RO_seq.append(
                Gate(prefix+'_Trigger_'+str(pt),'Trigger',
                wait_time = RO_trigger_duration,
                go_to = go_to_element, event_jump = event_jump_element,
                el_state_before_gate = el_RO_result,
                specific_transition = self.params['C'+str(carbon_nr)+'_dec_trans']))

        return carbon_RO_seq

    def readout_carbon_sequence_COMP(self,
        prefix              = 'C_RO',
        pt                  =  1,
        carbon_list         = [1, 4],
        RO_basis_list       = ['X','X'],
        RO_trigger_duration = 116e-6,
        el_RO_result        = '0',
        go_to_element       = 'next', event_jump_element = 'next',
        readout_orientation = 'positive',
        el_state_in         = 0,
        Zeno_RO             = False,
        phase_error         = 10*[0],
        add_wait_to_Zeno    = 0,
        do_init_pi2         = True,
        flip_RO             = False,
        do_RO_electron      = False,
        wait_for_trigger    = False,
        ):
        '''
        Modified version of readout carbon sequence to also use Composite gates for readout. This is dirty coding and should be properly implemented in the future
        if we want to use it more reguraly
        '''
        '''
        Function to create a general AWG sequence for Carbon spin measurements.
        carbon_list             gives the order of the carbons that the measurement will be performed on
        RO_basis_list           gives the basis in wich each Carbon spin will be measured
        el_RO_result            the electron state for the final trigger element (i.e. the electron measurement outcome)
        readout_orientation     sets the orientation of the electron readout (positive or negative)
        el_state_in             the state of the electron before the measurement
        Zeno_RO                 boolean, if true: Turns a laser via the AWG on. Circumvents the ADWIN.
        phase_error             to apply an extra phase BEFORE this gate (can be used for phase errors and phase correction) 
        add_wait_to_Zeno        time in seconds, if unequal to 0 --> puts a wait gate into the Zeno measurement.
        do_init_pi2             if the readoutsequence follows an invert_ro_sequence, do not start with a pi/2 pulse
        flip_RO                 flip the final pi2 pulse if you want to flip the readout result
        do_RO_electron          if do_RO_electron is true, and carbon list empty, readout the electron only
        wait_for_trigger        put a wait for trigger in the first element of the sequence
        '''

        ##############################
        ### Check input parameters ###
        ##############################

        if (type(go_to_element) != str) and (go_to_element != None):
            go_to_element = go_to_element.name

        if len(carbon_list) != len(RO_basis_list):
            print 'Warning: #carbons does not match #RO bases'
            print 'carbon list: ',carbon_list
            print 'RO basis list: ',RO_basis_list

        if len(carbon_list) == 0 and do_RO_electron==False:
            print 'Warning: No Carbons selected for readout'
            return []

        elif len(carbon_list) == 0 and do_RO_electron==True:
            print 'No Carbons selected for readout; reading out electron'

        number_of_carbons_to_RO = 0
        for jj, basis in enumerate(RO_basis_list):
            if basis != 'I':
                number_of_carbons_to_RO += 1
        if number_of_carbons_to_RO == 0 and do_RO_electron == False:
            return []

        #######################
        ### Create sequence ###
        #######################

        carbon_RO_seq = []

        ### Add basis rotations in case of Z-RO ###
        for kk, carbon_nr in enumerate(carbon_list):

            if RO_basis_list[kk] == 'Z' or RO_basis_list[kk] == '-Z':

                carbon_RO_seq.append( Gate(prefix + str(carbon_nr) + '_Ren_a_' + str(pt), 'Carbon_Gate',
                        Carbon_ind = carbon_nr, phase = 'reset', N = self.params['N1_list'][pt],
                    tau = self.params['tau1_list'][pt]))
                carbon_RO_seq.append( Gate(prefix + str(carbon_nr) + '_Ren_b_' + str(pt), 'Carbon_Gate',
                        Carbon_ind = carbon_nr, phase = 'reset', N = self.params['N2_list'][pt],
                    tau = self.params['tau2_list'][pt]))

        if do_init_pi2:
            ### Add initial pi/2 pulse (always) ###
            ### except when an invert RO sequence was done just before 
            ### (in that case the electron is still in a superposition)
            carbon_RO_seq.append(
                Gate(prefix+'_y_pi2_init'+str(pt),'electron_Gate',
                Gate_operation='pi2',
                phase = self.params['Y_phase'],wait_for_trigger=wait_for_trigger))

        ### Add RO rotations ###
        for kk, carbon_nr in enumerate(carbon_list):


            if RO_basis_list[kk] != 'I':

                ### Set the RO_phase
                if RO_basis_list[kk] == 'X':
                    RO_phase = 0 - phase_error[kk]
                elif RO_basis_list[kk] == '-X':
                    RO_phase = 180 - phase_error[kk]
                elif RO_basis_list[kk] == 'Y':
                    RO_phase = 90 - phase_error[kk]
                elif RO_basis_list[kk] == '-Y':
                    RO_phase = 270 - phase_error[kk]
                elif RO_basis_list[kk] == '-Z':
                    RO_phase = np.mod(self.params['C13_Y_phase']+180*el_state_in,360)
                elif RO_basis_list[kk] == 'Z':
                    RO_phase = np.mod(self.params['C13_Y_phase']+180*(1-el_state_in),360)

                else:
                    RO_phase = RO_basis_list[kk]

                carbon_RO_seq.append(
                        Gate(prefix + str(carbon_nr) + '_Ren_a_' + str(pt), 'Carbon_Gate',
                        Carbon_ind      = carbon_nr,
                        phase           = RO_phase,
                        N = self.params['N1_list'][pt],
                        tau = self.params['tau1_list'][pt], 
                        extra_phase_after_gate = phase_error[kk]))
                        
                               
                carbon_RO_seq.append(
                    Gate(prefix + str(carbon_nr) + '_Ren_b_' + str(pt), 'Carbon_Gate',
                        Carbon_ind      = carbon_nr,
                        phase = RO_phase+self.params['extra_phase_list'][pt], 
                        N = self.params['N2_list'][pt],
                        tau = self.params['tau2_list'][pt],
                        extra_phase_after_gate = phase_error[kk]))
                



        if do_RO_electron != True:
            ### Add final pi/2 and Trigger ###
                ### set the final electron pi2 pulse phase depending on the number of qubits RO (4 options)
            Final_pi2_pulse_phase = np.mod((180+self.params['Y_phase']) - np.mod(number_of_carbons_to_RO, 4) * 90, 360)
            Final_pi2_pulse_phase_negative = np.mod(Final_pi2_pulse_phase+180,360)

            #if you want an additional flip of the RO bases:        
            if flip_RO:
                Final_pi2_pulse_phase = np.mod(Final_pi2_pulse_phase+180,360)
                Final_pi2_pulse_phase_negative = np.mod(Final_pi2_pulse_phase_negative+180,360)

            if (readout_orientation == 'positive' and el_state_in == 0) or (readout_orientation == 'negative' and el_state_in == 1):
                carbon_RO_seq.append(
                        Gate(prefix+'_pi2_final_phase=' +str(Final_pi2_pulse_phase) + '_' +str(pt),'electron_Gate',
                        Gate_operation='pi2',
                        phase = Final_pi2_pulse_phase))

            elif (readout_orientation == 'negative' and el_state_in == 0) or (readout_orientation == 'positive' and el_state_in == 1):
                print 'RO negative or el state in =1!'
                carbon_RO_seq.append(
                        Gate(prefix+'_-pi2_final_phase=' +str(Final_pi2_pulse_phase) + '_' +str(pt),'electron_Gate',
                        Gate_operation='pi2',
                        phase = Final_pi2_pulse_phase_negative))
        else:
            carbon_RO_seq.append(Gate(prefix+'Wait_gate_'+str(pt),'passive_elt',
                wait_time = 20e-6))      

        #if Zeno parity measurement then shoot a laser at the nv. don't bother the adwin with it.
        if Zeno_RO:
            Laser=Gate(prefix+'pump'+str(pt),'Trigger',
                duration=RO_trigger_duration,
                )
            Laser.channel='AOM_Newfocus'
            Laser.elements_duration=RO_trigger_duration
            Laser.el_state_before_gate='0'
            if add_wait_to_Zeno != 0:
                carbon_RO_seq.extend([Gate(prefix+'_msmt_wait'+str(pt),'passive_elt',
                                     wait_time = add_wait_to_Zeno)])
            carbon_RO_seq.append(Laser)

        else:
            carbon_RO_seq.append(
                Gate(prefix+'_Trigger_'+str(pt),'Trigger',
                wait_time = RO_trigger_duration,
                go_to = go_to_element, event_jump = event_jump_element,
                el_state_before_gate = el_RO_result))

        return carbon_RO_seq


    def invert_readout_carbon_sequence(self,
        prefix              = 'C_invRO',
        pt                  =  1,
        carbon_list         = [1, 4],
        RO_basis_list       = ['X','X'],
        go_to_element       = 'next', event_jump_element = 'next',
        readout_orientation = 'positive',
        inv_el_state_in     = 0,
        el_state_in         = 0,
        phase_error         = 10*[0],
        did_undo_RO_phases  = False,
        do_final_pi2        = False
        ):
        '''
        Function to create a general AWG sequence that inverts the phase on the carbon states due to a carbon readout.
        carbon_list             gives the order of the carbons that the measurement will be performed on
        RO_basis_list           gives the basis in wich each Carbon spin was measured - the sequence will invert this
        readout_orientation     sets the orientation of the electron readout (positive or negative)
        el_state_in             the state of the electron before the sequence
        inv_el_state_in         the state of the electron before the sequence you are inverting
        phase_error             to apply an extra phase BEFORE this gate (can be used for phase errors and phase correction)
        did_undo_RO_phases      if did the undo-RO-phase pi, add 180 to the initial pi2 pulse to compensate
        do_final_pi2            do the final pi2 pulse on the electron
                                do not do the pulse when followed by a RO sequence, except when RO seq contains 'Z' RO 
        '''

        ##############################
        ### Check input parameters ###
        ##############################

        if (type(go_to_element) != str) and (go_to_element != None):
            go_to_element = go_to_element.name

        if len(carbon_list) != len(RO_basis_list):
            print 'Warning: #carbons does not match #invert-RO bases'

        if len(carbon_list) == 0:
            print 'Warning: No Carbons selected for invert-readout'
            return []

        number_of_carbons_to_RO = 0
        for jj, basis in enumerate(RO_basis_list):
            if basis != 'I':
                number_of_carbons_to_RO += 1
        if number_of_carbons_to_RO == 0:
            return []

        #######################
        ### Create sequence ###
        #######################

        carbon_invertRO_seq = []

        ### Add basis rotations in case of Z-RO ###
        for kk, carbon_nr in enumerate(carbon_list):

            if RO_basis_list[kk] == 'Z' or RO_basis_list[kk] == '-Z':

                carbon_invertRO_seq.append( Gate(prefix + str(carbon_nr) + '_Ren_a_' + str(pt), 'Carbon_Gate',
                        Carbon_ind = carbon_nr, phase = 'reset'))

        ### Add initial pi/2 ###
        ### It should be the inverse of the final pi/2 in the readout_carbon_sequence. Thus add a phase of 180.
        ### set the initial electron pi2 pulse phase depending on the number of qubits RO (4 options)
        ### If I did an undo_RO_phases sequence, I want to merge the pi/2 pulse with the last pi pulse. Thus add a phase of 180

        Init_pi2_pulse_phase = np.mod((self.params['Y_phase']) - np.mod(number_of_carbons_to_RO, 4) * 90, 360)
        Init_pi2_pulse_phase_negative = np.mod(Init_pi2_pulse_phase+180,360)

        if did_undo_RO_phases:
            Init_pi2_pulse_phase=np.mod(Init_pi2_pulse_phase+180,360)
            Init_pi2_pulse_phase_negative=np.mod(Init_pi2_pulse_phase_negative+180,360)

        if (readout_orientation == 'positive' and inv_el_state_in == 0) or (readout_orientation == 'negative' and inv_el_state_in == 1):
            carbon_invertRO_seq.append(
                    Gate(prefix+'_pi2_init_phase=' +str(Init_pi2_pulse_phase) + '_' +str(pt),'electron_Gate',
                    Gate_operation='pi2',
                    phase = Init_pi2_pulse_phase))

        elif (readout_orientation == 'negative' and inv_el_state_in == 0) or (readout_orientation == 'positive' and inv_el_state_in == 1):
            carbon_invertRO_seq.append(
                    Gate(prefix+'_-pi2_init_phase=' +str(Init_pi2_pulse_phase) + '_' +str(pt),'electron_Gate',
                    Gate_operation='pi2',
                    phase = Init_pi2_pulse_phase_negative))


        ### Add invert-RO rotations ###
        for kk, carbon_nr in enumerate(carbon_list):


            if RO_basis_list[kk] != 'I':

                ### Set the invert-RO_phase
                ### It is the RO_phase+180, for +-X and +-Y. For Z and -Z the phases are switched ###CHECK this -SvD
                if RO_basis_list[kk] == 'X':
                    invertRO_phase = self.params['C13_X_phase'] - phase_error[kk] + 180
                elif RO_basis_list[kk] == '-X':
                    invertRO_phase = self.params['C13_X_phase']+180 - phase_error[kk] +180
                elif RO_basis_list[kk] == 'Y':
                    invertRO_phase = self.params['C13_Y_phase'] - phase_error[kk] +180
                elif RO_basis_list[kk] == '-Y':
                    invertRO_phase = self.params['C13_Y_phase']+180 - phase_error[kk] +180
                elif RO_basis_list[kk] == '-Z':
                    invertRO_phase = np.mod(self.params['C13_Y_phase']+180*(1-el_state_in),360)
                elif RO_basis_list[kk] == 'Z':
                    invertRO_phase = np.mod(self.params['C13_Y_phase']+180*el_state_in,360)

                else:
                    invertRO_phase = RO_basis_list[kk]

                carbon_invertRO_seq.append(
                    Gate(prefix + str(carbon_nr) + '_Ren_b_' + str(pt), 'Carbon_Gate',
                    Carbon_ind      = carbon_nr,
                    phase           = invertRO_phase, 
                    extra_phase_after_gate = phase_error[kk]))

         # ### DO NOT add a final min y pi/2 pulse: it is not needed as we follow the inversion with a readout sequence ###
        # ### This is the inverse of the initial y pi/2 pulse from readout_carbon_sequence
        if do_final_pi2:
            carbon_invertRO_seq.append(
                Gate(prefix+'_miny_pi2_final'+str(pt),'electron_Gate',
                Gate_operation='pi2',
                phase = np.mod(self.params['Y_phase']+180,360)))

        return carbon_invertRO_seq

    def undo_ROphases(self,
        prefix              = 'undo_ROphases',
        pt                  = 1,
        RO_trigger_duration = 116e-6,
        conditional_pi      = True,
        conditional_pi2     = False,
        pi2_phase           = None,
        composite_pi        = False,
        el_state_in         = 0):

        '''
        Function that by means of a pi-pulse undoes the phases on the carbons that accumulated during a RO
        RO_trigger_duration     The duration of the wait element after the pi pulse should equal the duration of the RO element 
        conditional_pi          It is possible to not do the second pi, even if electron in is 0, in case a pi/2 pulse follows.
        conditional_pi2         This incorporates the conditional pi pulse with a pi2 pulse that follows
        pi2_phase               The phase of the pi2 pulse that is merged with the pi pulse. Default is Y phase (i.e. X or Y RO).
        composite_pi            If true, do a pi2-pi-pi2 sequence as pi pulse
        el_state_in             The electron state after the RO
        '''
        
        undo_ROphases_seq=[]

        first_pi_phase=self.params['X_phase']

        if composite_pi:
            undo_ROphases_seq.append(
                Gate(prefix+'_composite_pi2_pi_pi2_' +str(pt),'electron_Gate',
                    Gate_operation='comp_pi2_pi_pi2',
                    phase = ['Y_phase'],
                    el_state_before_gate='0',
                    el_state_after_gate='1'))
            # first_pi2_phase = self.params['Y_phase']
            # undo_ROphases_seq.append(
            #     Gate(prefix+'_first_pi2_a_phase=' +str(first_pi2_phase) + '_' +str(pt),'electron_Gate',
            #         Gate_operation='pi2',
            #         phase = first_pi2_phase,
            #         el_state_before_gate='0',
            #         el_state_after_gate='0'))#Since the time before and after the gate are the same, before=0 and after=1 or vice versa gives the same phase
            # undo_ROphases_seq.append(
            #     Gate(prefix+'_first_pi_b_phase=' +str(first_pi_phase) + '_' +str(pt),'electron_Gate',
            #         Gate_operation='pi',
            #         phase = first_pi_phase,
            #         el_state_before_gate='0',
            #         el_state_after_gate='1'))#Since the time before and after the gate are the same, before=0 and after=1 or vice versa gives the same phase
            # undo_ROphases_seq.append(
            #     Gate(prefix+'_first_pi2_c_phase=' +str(first_pi2_phase) + '_' +str(pt),'electron_Gate',
            #         Gate_operation='pi2',
            #         phase = first_pi2_phase,
            #         el_state_before_gate='1',
            #         el_state_after_gate='1'))#Since the time before and after the gate are the same, before=0 and after=1 or vice versa gives the same phase

        else:
            undo_ROphases_seq.append(
                Gate(prefix+'_first_pi_phase=' +str(first_pi_phase) + '_' +str(pt),'electron_Gate',
                    Gate_operation='pi',
                    phase = first_pi_phase,
                    el_state_before_gate='0',
                    el_state_after_gate='1'))#Since the time before and after the gate are the same, before=0 and after=1 or vice versa gives the same phase
     
        # add 2 us to the wait gate, since these are corrected for in the surrounding electron pulses
        undo_ROphases_seq.append(
            Gate(prefix+'Wait_gate_dur='+str(RO_trigger_duration+2.e-6)+'_'+str(pt),'passive_elt',
                wait_time = RO_trigger_duration+2.e-6))

        if conditional_pi:
            second_pi_phase = first_pi_phase+180
            ### The electron state in = 0 is rotated to 1 by the pi pulse, so this one needs an additional pulse
            if el_state_in == 0:
                undo_ROphases_seq.append(
                    Gate(prefix+'_second_pi_phase=' +str(second_pi_phase) + '_' +str(pt),'electron_Gate',
                        Gate_operation='pi',
                        phase = second_pi_phase,
                        el_state_after_gate='0'))

        if conditional_pi2:
            if pi2_phase == None:
                second_pi2_phase0 = np.mod(self.params['Y_phase']+180,360)
                second_pi2_phase1 = self.params['Y_phase']
            else:
                second_pi2_phase0 = np.mod(pi2_phase+180,360)
                second_pi2_phase1 = pi2_phase

            if el_state_in == 1:
                undo_ROphases_seq.append(
                    Gate(prefix+'_second_pi2_phase=' +str(second_pi2_phase1) + '_' +str(pt),'electron_Gate',
                        Gate_operation='pi2',
                        phase = second_pi2_phase1))                
            
            elif el_state_in == 0:
                undo_ROphases_seq.append(
                    Gate(prefix+'_second_pi2_phase=' +str(second_pi2_phase0) + '_' +str(pt),'electron_Gate',
                        Gate_operation='pi2',
                        phase = second_pi2_phase0))                

        return undo_ROphases_seq

    def readout_and_invert_carbons_sequence(self, 
        prefix                  = 'RO_and_invert_',
        pt                      = 1,
        RO_trigger_duration     = 150e-6,
        carbon_list             = [1,2],
        inv_carbon_list         = None,
        RO_basis_list           = ['X','X'],
        inv_RO_basis_list       = None,
        readout_orientation     = ['positive','postive'],
        do_init_pi2             = False,
        do_final_pi2            = False,
        wait_for_trigger        = False,
        composite_pi            = False
        ): 
        '''
        This combines the readout_sequence, the undo_RO_phases sequence and the Invert_readout_sequence into 1
        '''
        #######################
        ### Parity msmt XYY ###
        #######################

        RO_and_invert_seq = []

        Readout_seq = self.readout_carbon_sequence(
                    prefix              = 'RO_'+prefix ,
                    pt                  = pt,
                    RO_trigger_duration = RO_trigger_duration,
                    carbon_list         = carbon_list,
                    RO_basis_list       = RO_basis_list,
                    readout_orientation = readout_orientation,
                    do_init_pi2         = do_init_pi2,
                    wait_for_trigger    = wait_for_trigger,
                    el_RO_result        = '0',
                    el_state_in         = 0)

        RO_and_invert_seq.extend(Readout_seq)

        ######################
        ### Undo RO phase Parity YXY ###
        ######################

        undo_RO_phases_seq = self.undo_ROphases(
                    prefix              = 'Undo_phases_'+prefix,
                    pt                  = pt,
                    RO_trigger_duration = RO_trigger_duration,
                    conditional_pi      = False,
                    conditional_pi2     = False,
                    composite_pi        = composite_pi)

        RO_and_invert_seq.extend(undo_RO_phases_seq)

        ######################
        ### Parity msmt YXY ###
        ######################

        if inv_carbon_list == None:
            inv_carbon_list = carbon_list

        ### make sure that the invert_RO_basis_list gives the right rotation to the right carbon
        if inv_RO_basis_list == None:
            inv_RO_basis_list = RO_basis_list

        print 'carbon list: ',carbon_list, 'inv carbon list: ', inv_carbon_list
        print 'RO list: ',RO_basis_list, 'inv RO list: ', inv_RO_basis_list

        Invert_readout_seq = self.invert_readout_carbon_sequence(
                    prefix              = 'Invert_'+prefix,
                    pt                  = pt,
                    carbon_list         = inv_carbon_list,
                    RO_basis_list       = inv_RO_basis_list,
                    readout_orientation = readout_orientation,
                    do_final_pi2        = do_final_pi2,
                    did_undo_RO_phases  = True,
                    inv_el_state_in     = 0,
                    el_state_in         = 0)

        RO_and_invert_seq.extend(Invert_readout_seq)

        return(RO_and_invert_seq)

    def get_tomography_bases(self, nr_of_carbons):
        '''
        function that returns a full tomography basis/Pauli set for
        the given number of qubits
        '''
        if nr_of_carbons == 1:
            Tomo_bases = ([['X'],['Y'],['Z']])
        elif nr_of_carbons == 2:
            Tomo_bases = ([
            ['X','I'],['Y','I'],['Z','I'],
            ['I','X'],['I','Y'],['I','Z'],
            ['X','X'],['X','Y'],['X','Z'],
            ['Y','X'],['Y','Y'],['Y','Z'],
            ['Z','X'],['Z','Y'],['Z','Z']])
        elif nr_of_carbons == 3:
            Tomo_bases == ([
            ['X','I','I'],['Y','I','I'],['Z','I','I'],
            ['I','X','I'],['I','Y','I'],['I','Z','I'],
            ['I','I','X'],['I','I','Y'],['I','I','Z'],

            ['X','X','I'],['X','Y','I'],['X','Z','I'],
            ['Y','X','I'],['Y','Y','I'],['Y','Z','I'],
            ['Z','X','I'],['Z','Y','I'],['Z','Z','I'],

            ['X','I','X'],['Y','I','X'],['Z','I','X'],
            ['X','I','Y'],['Y','I','Y'],['Z','I','Y'],
            ['X','I','Z'],['Y','I','Z'],['Z','I','Z'],

            ['I','X','X'],['I','Y','X'],['I','Z','X'],
            ['I','X','Y'],['I','Y','Y'],['I','Z','Y'],
            ['I','X','Z'],['I','Y','Z'],['I','Z','Z'],

            ['X','X','X'],['X','Y','X'],['X','Z','X'],
            ['Y','X','X'],['Y','Y','X'],['Y','Z','X'],
            ['Z','X','X'],['Z','Y','X'],['Z','Z','X'],

            ['X','X','Y'],['X','Y','Y'],['X','Z','Y'],
            ['Y','X','Y'],['Y','Y','Y'],['Y','Z','Y'],
            ['Z','X','Y'],['Z','Y','Y'],['Z','Z','Y'],

            ['X','X','Z'],['X','Y','Z'],['X','Z','Z'],
            ['Y','X','Z'],['Y','Y','Z'],['Y','Z','Z'],
            ['Z','X','Z'],['Z','Y','Z'],['Z','Z','Z']])

        return Tomo_bases

    def logic_init_seq(self,
        prefix              = 'C3_init',
        pt                  =  1,
        carbon_list         = [1, 2, 5],
        RO_basis_list       = ['Y','Y','Y'],
        RO_trigger_duration = 116e-6,
        el_RO_result        = '0',
        logic_state         = 'Z',
        go_to_element       = 'next',
        event_jump_element = 'next',
        readout_orientation = 'positive',
        phase_error         = [0,0,0]):
        '''
        Function to create a general AWG sequence for Carbon spin measurements.
        '''

        ##############################
        ### Check input parameters ###
        ##############################

        if (type(go_to_element) != str) and (go_to_element != None):
            go_to_element = go_to_element.name

        if len(carbon_list) != len(RO_basis_list):
            print 'Warning: #carbons does not match #RO bases'

        if len(carbon_list) == 0:
            print 'Warning: No Carbons selected for readout'
            return []

        number_of_carbons_to_RO = 0
        for jj, basis in enumerate(RO_basis_list):
            if basis != 'I':
                number_of_carbons_to_RO += 1
        if number_of_carbons_to_RO == 0:
            return []
        #######################
        ### Create sequence ###
        #######################

        carbon_RO_seq = []

        ### Add basis rotations in case of Z-RO ###
        for kk, carbon_nr in enumerate(carbon_list):

            if RO_basis_list[kk] == 'Z' or RO_basis_list[kk] == '-Z':

                carbon_RO_seq.append( Gate(prefix + str(carbon_nr) + '_Ren_a_' + str(pt), 'Carbon_Gate',
                        Carbon_ind = carbon_nr, phase = 'reset'))

        ### Add electron pulse, dependent on logical state ###

        if logic_state == 'Z':
            pass
        elif logic_state == 'mZ':
            carbon_RO_seq.append(
                    Gate(prefix+'_X_pi_init_pt'+str(pt),'electron_Gate',
                    Gate_operation='pi',
                    phase = self.params['X_phase']))
        elif logic_state == 'X':
            carbon_RO_seq.append(
                    Gate(prefix+'_-y_pi2_init_pt'+str(pt),'electron_Gate',
                    Gate_operation='pi2',
                    phase = self.params['Y_phase']+180))
        elif logic_state == 'mX':
            carbon_RO_seq.append(
                    Gate(prefix+'_y_pi2_init_pt'+str(pt),'electron_Gate',
                    Gate_operation='pi2',
                    phase = self.params['Y_phase']))
        elif logic_state == 'Y':
            carbon_RO_seq.append(
                    Gate(prefix+'_x_pi2_init_pt'+str(pt),'electron_Gate',
                    Gate_operation='pi2',
                    phase = self.params['X_phase']))
        elif logic_state == 'mY':
            carbon_RO_seq.append(
                    Gate(prefix+'_-x_pi2_init_pt'+str(pt),'electron_Gate',
                    Gate_operation='pi2',
                    phase = self.params['X_phase']+180))

        ### Add RO rotations ###
        for kk, carbon_nr in enumerate(carbon_list):


            if RO_basis_list[kk] != 'I':

                ### Determine the RO_phase
                if RO_basis_list[kk] == 'X':
                    RO_phase = self.params['C13_X_phase']+phase_error[kk]
                elif RO_basis_list[kk] == '-X':
                    RO_phase = self.params['C13_X_phase']+180+phase_error[kk]
                elif RO_basis_list[kk] == 'Y' or RO_basis_list[kk] == '-Z':
                    RO_phase = self.params['C13_Y_phase']+phase_error[kk]
                elif RO_basis_list[kk] == '-Y' or RO_basis_list[kk] == 'Z':
                    RO_phase = self.params['C13_Y_phase']+180+phase_error[kk]
                else:
                    RO_phase = RO_basis_list[kk]

                carbon_RO_seq.append(
                        Gate(prefix + str(carbon_nr) + '_Ren_b_' + str(pt), 'Carbon_Gate',
                        Carbon_ind = carbon_nr,
                        phase = RO_phase))

        ### Add final pi/2 and Trigger ###

        if readout_orientation == 'positive':
            carbon_RO_seq.append(
                    Gate(prefix+'_y_pi2_final' + '_pt' +str(pt),'electron_Gate',
                    Gate_operation='pi2',
                    phase = self.params['Y_phase']))
        elif readout_orientation == 'negative':
            carbon_RO_seq.append(
                    Gate(prefix+'_-y_pi2_final' + '_pt' +str(pt),'electron_Gate',
                    Gate_operation='pi2',
                    phase = self.params['Y_phase']+180))

        carbon_RO_seq.append(
                Gate(prefix+'_Trigger_'+str(pt),'Trigger',
                wait_time = RO_trigger_duration,
                go_to = go_to_element, event_jump = event_jump_element,
                el_state_before_gate = el_RO_result))

        return carbon_RO_seq



    def initialize_carbon_sequence_COMP(self,
                prefix                  = 'init_C',
                go_to_element           = 'MBI_1',
                wait_for_trigger        = True,
                initialization_method   = 'swap',
                pt                      = 1,
                addressed_carbon        = 1,
                C_init_state            = 'up',
                el_RO_result            = '0',
                el_after_init           = '0',
                do_wait_after_pi        = False):
        '''
        By THT
        Supports Swap or MBI initialization
        state can be 'up' or 'down'
        Swap init: up -> 0, down ->1
        MBI init: up -> +X, down -> -X
        '''

        if type(go_to_element) != str:
            go_to_element = go_to_element.name

        if C_init_state == 'up':
            C_init_y_phase = self.params['Y_phase']
        elif C_init_state == 'down':
            C_init_y_phase = self.params['Y_phase']+180

        ### Define elements and gates
        C_init_y = Gate(prefix+str(addressed_carbon)+'_y_pt'+str(pt),'electron_Gate',
                Gate_operation ='pi2',
                wait_for_trigger = wait_for_trigger,
                phase = C_init_y_phase)

        C_init_Ren_a = Gate(prefix+str(addressed_carbon)+'_Ren_a_pt'+str(pt), 'Carbon_Gate',
                Carbon_ind = addressed_carbon,
                phase = self.params['C13_X_phase'],
                N=self.params['N1_list'][pt],
                tau=self.params['tau1_list'][pt])

        C_init_x = Gate(prefix+str(addressed_carbon)+'_x_pt'+str(pt),'electron_Gate',
                Gate_operation='pi2',
                phase = self.params['X_phase'])

        C_init_Ren_b = Gate(prefix+str(addressed_carbon)+'_Ren_b_pt'+str(pt), 'Carbon_Gate',
                Carbon_ind = addressed_carbon,
                phase = self.params['C13_Y_phase']+180)
        
        C_init_Ren_c = Gate(prefix+str(addressed_carbon)+'_Ren_c_pt'+str(pt), 'Carbon_Gate',
                Carbon_ind = addressed_carbon,
                N = self.params['N2_list'][pt],
                tau = self.params['tau2_list'][pt],
                phase = self.params['C13_X_phase']+self.params['extra_phase_list'][pt])

        C_init_RO_Trigger = Gate(prefix+str(addressed_carbon)+'_RO_trig_pt'+str(pt),'Trigger',
                wait_time= self.params['Carbon_init_RO_wait'],
                event_jump = 'next',
                go_to = go_to_element,
                el_state_before_gate = el_RO_result)

        ## TODO: THT, temporary fix that removed pi-puls that is bugged
        C_init_elec_X = Gate(prefix+str(addressed_carbon)+'_elec_X_pt'+str(pt),'electron_Gate',
                Gate_operation='pi',
                phase = self.params['X_phase'],
                el_state_after_gate = '1')
        wait_gate = (Gate('Wait_gate_after_el_pi_pt'+str(pt),'passive_elt',
                     wait_time = 3e-6))

        ### Set sequence
        if initialization_method == 'swap':  ## Swap initializes into 1 or 0
            carbon_init_seq = [C_init_y, C_init_Ren_a, C_init_x, C_init_Ren_b, C_init_RO_Trigger]
        elif initialization_method == 'MBI': ## MBI initializes into +/-X
            carbon_init_seq = [C_init_y, C_init_Ren_a, C_init_x, C_init_RO_Trigger]
        elif initialization_method == 'MBI_then_gate': ## MBI then gate initializes into 1 or 0 
            carbon_init_seq = [C_init_y, C_init_Ren_a, C_init_x, C_init_RO_Trigger, C_init_Ren_b]    
        elif initialization_method == 'COMP': ## MBI initializes into +/-X
             carbon_init_seq = [C_init_y, C_init_Ren_a, C_init_Ren_c, C_init_x, C_init_RO_Trigger]
        elif initialization_method == 'mixed': ## initializes into a mixed state
            carbon_init_seq = [C_init_Ren_a, C_init_x, C_init_Ren_b, C_init_RO_Trigger] #Can the first C_init_Ren be removed?

        else:
            print 'Error initialization method (%s) not recognized, supported methods are "swap", "MBI", "COMP" None' %initialization_method
            return False

        ### TODO: THT, temporary fix for pi-pulse in Trigger, later redo trigger element workings
        ### I uncommented this part of the initialization for the Carbon T1 measurements. Norbert 20141104
        if el_after_init =='1':
            carbon_init_seq.append(C_init_elec_X)
            if do_wait_after_pi:
                carbon_init_seq.append(wait_gate)

        return carbon_init_seq


### Single Carbon initialization classes ###
class Transfer_gate_calibration(MBI_C13):
    '''
    This class is used to calibrate the extra phase Carbons pick up during the execution of an electron transfer gate. It initializes a carbon in X,
    brings the electron in a superposition and transfers this superposition to the other transition. After this reads out the carbon while sweeping the phase.
    '''
    mprefix = 'CarbonRamseyInitialised'
    adwin_process = 'MBI_multiple_C13'

    def generate_sequence(self, upload=True, debug=False):
        pts = self.params['pts']
        
        ### initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Initialized Nuclear Ramsey Sequence')

        for pt in range(pts): ### Sweep over trigger time (= wait time)
            gate_seq = []

            ### Nitrogen MBI
            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]; gate_seq.extend(mbi_seq)

            ### Carbon initialization
            carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                prefix = 'C_MBI_',
                wait_for_trigger      = True, pt =pt,
                initialization_method = 'MBI',#self.params['C13_init_method'],
                C_init_state          = self.params['init_state'],
                addressed_carbon      = self.params['carbon_nr'],
                el_RO_result          = str(self.params['C13_MBI_RO_state']),
                el_after_init       = self.params['electron_after_init'])
            gate_seq.extend(carbon_init_seq)
                         
               ###After carbon initialization, perform the transfer gate with electron in superposition

   
            first_wait_gate = Gate('Wait_gate_before'+str(pt),'passive_elt',
                            wait_time =3e-6,
                            specific_transition=self.params['first_transition'])
            first_pi2 =Gate('Pi_pulse_before_transfer_'+str(pt),'electron_Gate',
                            pt=pt,
                            Gate_operation='pi2',
                            phase = self.params['X_phase'],
                            el_state_after_gate = 'sup',
                            specific_transition = self.params['first_transition'])

            second_pi2 =Gate('Pi_pulse_after_transfer_'+str(pt),'electron_Gate',
                            pt=pt,
                            Gate_operation='pi2',
                            phase = self.params['X_phase']+180,
                            el_state_after_gate = '0',
                            specific_transition = self.params['second_transition'])

            second_wait_gate = Gate('Wait_gate_after'+str(pt),'passive_elt',
                            wait_time =3e-6,
                            specific_transition=self.params['second_transition'],
                            el_state_after_gate = '0')

             
            gate_seq.extend([first_wait_gate,first_pi2,second_pi2,second_wait_gate])     

            ### Readout
            carbon_tomo_seq = self.readout_carbon_sequence(
                    prefix              = 'Tomo',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = [self.params['carbon_nr']],
                    RO_basis_list       = [self.params['C_RO_phase'][pt]],
                    readout_orientation = self.params['electron_readout_orientation'])
            gate_seq.extend(carbon_tomo_seq)

            gate_seq = self.generate_AWG_elements(gate_seq,pt)

            ### Convert elements to AWG sequence and add to combined list
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq, explicit=True)
            combined_list_of_elements.extend(list_of_elements)

            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)

            # if not debug:
            #     print '*'*10
            #     for g in gate_seq:
            #         print g.name

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

        
        if not debug:
            print '*'*10
            for g in gate_seq:
                print g.name

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'

class ElectronRamseyWithNuclearInit(MBI_C13):
    '''
    This class generates the AWG sequence for a electronic ramsey experiment with previous carbon initialisation.
    1. Nitrogen MBI initialisation
    2. Carbon initialisation into +Z or -Z
    3. Pi/2 pulse on the electronic state2
    4. Darktime of some us
    5. Pi/2 pulse on the electronic state and read-out
    '''

    mprefix='E_Ramsey_withC13Init'
    adwin_process='MBI_multiple_C13'

    def generate_sequence(self, upload=True, debug=False):
        pts= self.params['pts']

        #initialize empty list of elements and sequence.
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('E_Ramsey_withC13Init')



        #Define the necessary pulses for the ramsey sequence

        X = pulselib.MW_IQmod_pulse('Pi_2-pulse',
            I_channel='MW_Imod', Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod', Sw_channel=self.params['MW_switch_channel'],
            frequency = self.params['fast_pi2_mod_frq'],
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            Sw_risetime = self.params['MW_switch_risetime'],
            length = self.params['fast_pi2_duration'],
            amplitude = self.params['fast_pi2_amp'])


        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = 10e-6,
            amplitude = 2)
        T = pulse.SquarePulse(channel='MW_Imod', name='delay',
            length = 200e-9, amplitude = 0.)

        T_ramsey = pulse.SquarePulse(channel='MW_Imod', name='delay',
            length = 200e-9, amplitude = 0.)



        #this is used to read-out the electron upside-down.

        if self.params['electron_readout_orientation']=='negative':
            extra_phase=0
        else:
            extra_phase=180

        for pt in range(pts):



            #####################################################
            #####    Generating the sequence elements      ######
            #####################################################
            #Elements for the nitrogen and carbon initialisation
            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]

            carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                    initialization_method = 'swap', pt =pt,
                    addressed_carbon= self.params['Addressed_Carbon'],
                    C_init_state = self.params['C13_init_state'],
                    el_RO_result = str(self.params['C13_MBI_RO_state']))

            #This element is needed for hard coding the remaining part of the sequence into the AWG
            #And for having the function combine_to_AWG_sequence work.

            wait_gate = Gate('Wait_gate_'+ str(pt),'passive_elt',
                    wait_time = 5e-6)

            C_evol_seq =[wait_gate]

            # Gate seq consits of 3 sub sequences [MBI] [Carbon init]  [RO and evolution]
            gate_seq = []

            if self.params['no_carbon_init']==True:
                NMBI_wait_gate = Gate('Wait_MBI_Trigger_'+ str(pt),'passive_elt',
                    wait_time = (self.params['MBI_duration']+self.params['repump_after_MBI_duration'][0]+20)*1e-6)
                NMBI_wait=[NMBI_wait_gate]
                gate_seq.extend(mbi_seq)
                gate_seq.extend(NMBI_wait)
                gate_seq.extend(C_evol_seq)
            else:
                gate_seq.extend(mbi_seq), gate_seq.extend(carbon_init_seq)
                gate_seq.extend(C_evol_seq)
            ############

            gate_seq = self.generate_AWG_elements(gate_seq,pt)
            #Convert elements to AWG sequence and add to combined list
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq, explicit=True)
            combined_list_of_elements.extend(list_of_elements)

            ############################################
            #       Create the ramsey sequence         #
            ############################################



            elements=[]
            e = element.Element('ElectronRamsey_pt-%d' % pt, pulsar=qt.pulsar,
                global_time = True)

            e.append(T)

            if self.params['wait_times'][pt]-self.params['fast_pi2_duration'] < 20e-9:
                pass

            else:
                e.append(pulse.cp(X, phase = 0.0))

                e.append(pulse.cp(T_ramsey,
                        length = self.params['wait_times'][pt]-self.params['fast_pi2_duration']))

                e.append(pulse.cp(X,
                    phase = self.params['pi2_phases2'][pt]+extra_phase))

            e.append(T)
            e.append(T)
            e.append(T)
            e.append(T)
            e.append(adwin_sync)
            elements.append(e)

 

            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)

            # combine carbon_init with ramsey sequence

            for el in elements:
                combined_list_of_elements.append(el)
                combined_seq.append(name=el.name, wfname=el.name, trigger_wait=False)

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'

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

class NuclearRamseyWithInitializationModified(MBI_C13):
    '''
    update description still
    This class is to test multiple carbon initialization and Tomography.
    Sequence: |N-MBI| -|CinitA|-|CinitB|-|Tomography|
    '''
    mprefix = 'CarbonRamseyInitialised'
    adwin_process = 'MBI_multiple_C13'

    def generate_sequence(self, upload=True, debug=False):
        pts = self.params['pts']

        ### initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Initialized Nuclear Ramsey Sequence')

        for pt in range(pts): ### Sweep over trigger time (= wait time)
            gate_seq = []

            ### Nitrogen MBI
            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]; gate_seq.extend(mbi_seq)

            ### Carbon initializations
            init_wait_for_trigger = True

            for ii in range(self.params['Nr_C13_init']):
                carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                    prefix = 'C_' + str(self.params['C13_init_method'][ii]) + '_',
                    wait_for_trigger      = init_wait_for_trigger, 
                    pt =pt,
                    initialization_method = self.params['C13_init_method'][ii],
                    C_init_state          = self.params['init_state'][ii],
                    addressed_carbon      = self.params['carbon_list'][ii],
                    el_RO_result          = str(self.params['C13_MBI_RO_state']),
                    el_after_init       = str(self.params['el_after_init'][ii]))
                gate_seq.extend(carbon_init_seq)
                init_wait_for_trigger = False
            
            # print 'EL PI AFTER MBI HAS BEEN COMMENTED OUT, NK 150825'
            #XXXXXXXXXXXXXXXXXXXXXXXXXXXX
            # if self.params['el_pi_after_mbi'] == True:
            #     El_Pi = Gate('El_Pi_'+str(pt),'electron_Gate',Gate_operation='pi')
                
            #     gate_seq.extend([El_Pi])
            ### Free evolution_time

                ### Check if free evolution time is larger than the RO time (it can't be shorter)
            if self.params['add_wait_gate'] == True:
                if self.params['free_evolution_time'][pt]< (self.params['Carbon_init_RO_wait']+3e-6): # because min length is 3e-6
                    print ('Error: carbon evolution time (%s) is shorter than Initialisation RO duration (%s)'
                            %(self.params['free_evolution_time'][pt],self.params['Carbon_init_RO_wait']))
                    qt.msleep(5)
                    ### Add waiting time
                wait_gate = Gate('Wait_gate_'+str(pt),'passive_elt',
                         wait_time = self.params['free_evolution_time'][pt]-self.params['Carbon_init_RO_wait'])
                wait_seq = [wait_gate]; gate_seq.extend(wait_seq)

            ### Readout
            carbon_tomo_seq = self.readout_carbon_sequence(
                    prefix              = 'Tomo',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = [self.params['C13_MBI_nr']],
                    RO_basis_list       = [self.params['C_RO_phase'][pt]],
                    readout_orientation = self.params['electron_readout_orientation'])
            gate_seq.extend(carbon_tomo_seq)

            gate_seq = self.generate_AWG_elements(gate_seq,pt)

            ###  elements to AWG sequence and add to combined list
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq, explicit=True)
            combined_list_of_elements.extend(list_of_elements)

            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)

            if debug:
                for g in gate_seq:
                    print g.name
                    self.print_carbon_phases(g,[self.params['carbon_list']])

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'

class NuclearRamseyWithInitialization(MBI_C13):
    '''
    update description still
    This class is to test multiple carbon initialization and Tomography.
    Sequence: |N-MBI| -|CinitA|-|CinitB|-|Tomography|
    '''
    mprefix = 'CarbonRamseyInitialised'
    adwin_process = 'MBI_multiple_C13'

    def generate_sequence(self, upload=True, debug=False):
        pts = self.params['pts']

        ### initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Initialized Nuclear Ramsey Sequence')

        for pt in range(pts): ### Sweep over trigger time (= wait time)
            gate_seq = []

            ### Nitrogen MBI
            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]; gate_seq.extend(mbi_seq)

            ### Carbon initialization
            carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                prefix = 'C_MBI_',
                wait_for_trigger      = True, pt =pt,
                initialization_method = 'MBI',#self.params['C13_init_method'],
                C_init_state          = self.params['init_state'],
                addressed_carbon      = self.params['carbon_nr'],
                el_RO_result          = str(self.params['C13_MBI_RO_state']),
                el_after_init       = self.params['electron_after_init'])
            gate_seq.extend(carbon_init_seq)
            
            # print 'EL PI AFTER MBI HAS BEEN COMMENTED OUT, NK 150825'
            #XXXXXXXXXXXXXXXXXXXXXXXXXXXX
            # if self.params['el_pi_after_mbi'] == True:
            #     El_Pi = Gate('El_Pi_'+str(pt),'electron_Gate',Gate_operation='pi')
                
            #     gate_seq.extend([El_Pi])
            ### Free evolution_time

                ### Check if free evolution time is larger than the RO time (it can't be shorter)
            if self.params['add_wait_gate'] == True:
                if self.params['free_evolution_time'][pt]< (self.params['Carbon_init_RO_wait']+3e-6): # because min length is 3e-6
                    print ('Error: carbon evolution time (%s) is shorter than Initialisation RO duration (%s)'
                            %(self.params['free_evolution_time'][pt],self.params['Carbon_init_RO_wait']))
                    qt.msleep(5)
                    ### Add waiting time
                wait_gate = Gate('Wait_gate_'+str(pt),'passive_elt',
                         wait_time = self.params['free_evolution_time'][pt]-self.params['Carbon_init_RO_wait'])
                wait_seq = [wait_gate]; gate_seq.extend(wait_seq)

            ### Readout
            carbon_tomo_seq = self.readout_carbon_sequence(
                    prefix              = 'Tomo',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = [self.params['carbon_nr']],
                    RO_basis_list       = [self.params['C_RO_phase'][pt]],
                    readout_orientation = self.params['electron_readout_orientation'])
            gate_seq.extend(carbon_tomo_seq)

            gate_seq = self.generate_AWG_elements(gate_seq,pt)

            ### Convert elements to AWG sequence and add to combined list
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq, explicit=True)
            combined_list_of_elements.extend(list_of_elements)

            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)

            if debug:
                for g in gate_seq:
                    print g.name
                    self.print_carbon_phases(g,[self.params['carbon_nr']])

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'

class NuclearRamseyWithInitializationUncondCGate(MBI_C13):
    '''
    This class is to test carbon initialization, followed by an unconditional carbon gate and then tomography.
    Sequence: |N-MBI| -|CinitA|-|GateA|-|Tomography|
    '''
    mprefix = 'CarbonRamseyInitialisedUncondCGate'
    adwin_process = 'MBI_multiple_C13'

    def generate_sequence(self, upload=True, debug=False):
        pts = self.params['pts']

        ### initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Initialized Nuclear Ramsey Sequence')

        for pt in range(pts): ### Sweep over trigger time (= wait time)
            gate_seq = []

            ### Nitrogen MBI
            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]; gate_seq.extend(mbi_seq)

            #First of all we use the gate to rotation from z into the x/y plane, and scan the 
            # phase of the tomography until they are aligned
            if self.params['check_phase_or_offset'] == 'phase':
                ### Carbon initialization
                carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                    prefix = 'C_MBI_',
                    wait_for_trigger      = True, pt =pt,
                    initialization_method = 'MBI',#self.params['C13_init_method'],
                    C_init_state          = self.params['init_state'],
                    addressed_carbon      = self.params['carbon_nr'],
                    el_RO_result          = str(self.params['C13_MBI_RO_state']),
                    el_after_init       = self.params['electron_after_init'])
                gate_seq.extend(carbon_init_seq)

                addressed_carbon = self.params['carbon_nr']
                el_trans = self.params['electron_transition']

               
                if self.params['check_phase'] == False:
                    phase_offset = self.params['C'+str(addressed_carbon)+'_unc_phase_offset'+el_trans]

                    ### Un-conditional gate 
                    C_unc = Gate('C_unc_pt'+str(pt), 'Carbon_Gate',
                        Carbon_ind  = addressed_carbon,
                        N           = self.params['C' + str(addressed_carbon) + '_unc_N' + el_trans][0],
                        tau         = self.params['C' + str(addressed_carbon) + '_unc_tau'+el_trans][0],
                        phase       = -phase_offset,
                        extra_phase_after_gate = self.params['C_unc_phase'][pt] + phase_offset)

                else: # Used afterwards to check everything works.
  
                    C_unc = self.unconditional_carbon_gate('C_unc_pt'+str(pt),
                        Carbon_ind  = addressed_carbon,
                        phase       =  self.params['C_unc_phase'][pt])
                    # phase_offset = self.params['C'+str(addressed_carbon)+'_unc_phase_offset'+el_trans]
                    # extra_phase = (self.params['C'+str(addressed_carbon)+'_unc_extra_phase_correction_list'+el_trans][addressed_carbon] 
                    #     + phase_offset)
                    # # Need phase offset to adjust phase, plus extra phase to bring it back! 
                    # C_unc = Gate('C_unc_pt'+str(pt), 'Carbon_Gate',
                    #     Carbon_ind  = addressed_carbon,
                    #     N           = self.params['C' + str(addressed_carbon) + '_unc_N' + el_trans][0],
                    #     tau         = self.params['C' + str(addressed_carbon) + '_unc_tau'+el_trans][0],
                    #     phase       = -phase_offset,
                    #     extra_phase_after_gate = self.params['C_unc_phase'][pt] + extra_phase)

                gate_seq.append(C_unc)


                    ### Check if free evolution time is larger than the RO time (it can't be shorter)
                if self.params['add_wait_gate'] == True:
                    if self.params['free_evolution_time'][pt]< (self.params['Carbon_init_RO_wait']+3e-6): # because min length is 3e-6
                        print ('Error: carbon evolution time (%s) is shorter than Initialisation RO duration (%s)'
                                %(self.params['free_evolution_time'][pt],self.params['Carbon_init_RO_wait']))
                        qt.msleep(5)
                        ### Add waiting time
                    wait_gate = Gate('Wait_gate_'+str(pt),'passive_elt',
                             wait_time = self.params['free_evolution_time'][pt]-self.params['Carbon_init_RO_wait'])
                    wait_seq = [wait_gate]; gate_seq.extend(wait_seq)

                ### Readout
                if self.params['check_phase'] == False:
                    carbon_tomo_seq = self.readout_carbon_sequence(
                            prefix              = 'Tomo',
                            pt                  = pt,
                            go_to_element       = None,
                            event_jump_element  = None,
                            RO_trigger_duration = 10e-6,
                            carbon_list         = [self.params['carbon_nr']],
                            RO_basis_list       = ['X'],
                            readout_orientation = self.params['electron_readout_orientation'])
                else:
                    carbon_tomo_seq = self.readout_carbon_sequence(
                            prefix              = 'Tomo',
                            pt                  = pt,
                            go_to_element       = None,
                            event_jump_element  = None,
                            RO_trigger_duration = 10e-6,
                            carbon_list         = [self.params['carbon_nr']],
                            RO_basis_list       = ['Z'],
                            readout_orientation = self.params['electron_readout_orientation'])  
                gate_seq.extend(carbon_tomo_seq)

            else:
                # print 'this is the phase_offset', self.params['C_unc_phase'][pt]
                ### Carbon initialization
                carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                    prefix = 'C_MBI_',
                    wait_for_trigger      = True, pt =pt,
                    initialization_method = 'MBI',#self.params['C13_init_method'],
                    C_init_state          = self.params['init_state'],
                    addressed_carbon      = self.params['carbon_nr'],
                    el_RO_result          = str(self.params['C13_MBI_RO_state']),
                    el_after_init       = self.params['electron_after_init'])
                gate_seq.extend(carbon_init_seq)

                addressed_carbon = self.params['carbon_nr']
                el_trans = self.params['electron_transition']

                if self.params['check_phase'] == False:
                    ### Un-conditional gate 
                     C_unc = self.unconditional_carbon_gate('C_unc_pt'+str(pt),
                        Carbon_ind  = addressed_carbon,
                        phase       = self.params['C_unc_phase'][pt])
                else:
                     C_unc = self.unconditional_carbon_gate('C_unc_pt'+str(pt),
                        Carbon_ind  = addressed_carbon,
                        phase       =  self.params['C_unc_phase'][pt])


                gate_seq.append(C_unc)


                    ### Check if free evolution time is larger than the RO time (it can't be shorter)
                if self.params['add_wait_gate'] == True:
                    if self.params['free_evolution_time'][pt]< (self.params['Carbon_init_RO_wait']+3e-6): # because min length is 3e-6
                        print ('Error: carbon evolution time (%s) is shorter than Initialisation RO duration (%s)'
                                %(self.params['free_evolution_time'][pt],self.params['Carbon_init_RO_wait']))
                        qt.msleep(5)
                        ### Add waiting time
                    wait_gate = Gate('Wait_gate_'+str(pt),'passive_elt',
                             wait_time = self.params['free_evolution_time'][pt]-self.params['Carbon_init_RO_wait'])
                    wait_seq = [wait_gate]; gate_seq.extend(wait_seq)

                ### Readout
                carbon_tomo_seq = self.readout_carbon_sequence(
                        prefix              = 'Tomo',
                        pt                  = pt,
                        go_to_element       = None,
                        event_jump_element  = None,
                        RO_trigger_duration = 10e-6,
                        carbon_list         = [self.params['carbon_nr']],
                        #RO_basis_list       = [-self.params['C' + str(self.params['carbon_nr']) + '_unc_extra_phase_correction_list'+self.params['electron_transition']][self.params['carbon_nr']]],
                        RO_basis_list       = ['Z'],
                        readout_orientation = self.params['electron_readout_orientation'])
                gate_seq.extend(carbon_tomo_seq)


            gate_seq = self.generate_AWG_elements(gate_seq,pt)

            ### Convert elements to AWG sequence and add to combined list
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq, explicit=True)
            combined_list_of_elements.extend(list_of_elements)

            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)

            if debug:
                for g in gate_seq:
                    print g.name
                    self.print_carbon_phases(g,[self.params['carbon_nr']])

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'

class NuclearInitializationWithRemoteInitialization(MBI_C13):
    '''
    update description still
    This class is to test multiple carbon initialization and Tomography.
    Sequence: |C1 MBI| - |wait time: beating freq*2 = pi| - |M C1 X|(require X) - |C1 MBI| - |Tomography|
    '''
    mprefix = 'CarbonRamseyInitialised'
    adwin_process = 'MBI_multiple_C13'

    def generate_sequence(self, upload=True, debug=False):
        pts = self.params['pts']

        ### initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Initialized Nuclear Ramsey Sequence')

        for pt in range(pts): ### Sweep over trigger time (= wait time)
            gate_seq = []

            ### Nitrogen MBI
            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]; gate_seq.extend(mbi_seq)

            ### MBI1
            carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                prefix = 'C_MBI1_',
                wait_for_trigger      = True, pt =pt,
                initialization_method = 'MBI',#self.params['C13_init_method'],
                C_init_state          = self.params['init_state'],
                addressed_carbon      = self.params['carbon_nr'],
                el_RO_result          = str(self.params['C13_MBI_RO_state']),
                el_after_init       = self.params['electron_after_init'])
            gate_seq.extend(carbon_init_seq)
            
            if self.params['add_wait_gate'] == True:
                ### Check if free evolution time is larger than the RO time (it can't be shorter)
                if self.params['beating_wait_time']< (self.params['Carbon_init_RO_wait']+3e-6): # because min length is 3e-6
                    print ('Error: carbon evolution time (%s) is shorter than Initialisation RO duration (%s)'
                            %(self.params['beating_wait_time'],self.params['Carbon_init_RO_wait']))
                    qt.msleep(5)
                    ### Add waiting time
                wait_gate = Gate('Wait_gate_max_ent_carbons_' + str(pt),'passive_elt',
                         wait_time = self.params['beating_wait_time'])
                wait_seq = [wait_gate]; gate_seq.extend(wait_seq)


            ### MBI2 to initalize the guy
            carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                prefix = 'C_MBI2_',
                wait_for_trigger      = False, pt =pt,
                initialization_method = 'MBI',#self.params['C13_init_method'],
                C_init_state          = self.params['init_state'],
                addressed_carbon      = self.params['carbon_nr'],
                el_RO_result          = str(self.params['C13_MBI_RO_state']),
                el_after_init       = self.params['electron_after_init'])
            gate_seq.extend(carbon_init_seq)


            # Should add to rotational frequency here

            ### Carbon Initialisation, finish with SWAP or MBI          
            ### SOOOOO DIRTY!
            if False:
                C_init_Ren_b = Gate('Cx_C'+str(self.params['carbon_nr'])+'_Ren_b_pt'+str(pt), 'Carbon_Gate',
                    Carbon_ind = self.params['carbon_nr'],
                    phase = self.params['C13_Y_phase']+180)
                gate_seq.extend([C_init_Ren_b])
                print 'second +-x is on'


            carbon_tomo_seq = self.readout_carbon_sequence(
                    prefix              = 'Tomo_C',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = [self.params['carbon_nr']],
                    RO_basis_list       = self.params['Tomography Bases'][pt],
                    readout_orientation = self.params['electron_readout_orientation'])
            gate_seq.extend(carbon_tomo_seq)


            gate_seq = self.generate_AWG_elements(gate_seq,pt)

            ### Convert elements to AWG sequence and add to combined list
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq, explicit=True)
            combined_list_of_elements.extend(list_of_elements)

            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)

            if debug:
                for g in gate_seq:
                    print g.name
                    self.print_carbon_phases(g,[self.params['carbon_nr']])

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'

class Crosstalk(MBI_C13):
    '''
    This class is used to emasure the evolution of CarbonA during gates on CarbonB
    1. MBI initialisation
    2. CarbonA initialisation
    3. CarbonB Rabi evolution
    4. CarbonA Readout
    '''
    mprefix = 'CarbonRabiInitialised_Crosstalk'
    adwin_process = 'MBI_multiple_C13'

    def generate_sequence(self,upload=True,debug = False):
        pts = self.params['pts']

        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Initialized Nuclear Rabi Sequence')
        

        for pt in range(pts):
            
            gate_seq = []

            ###########################################
            #####    Generating the sequence elements      ######
            ###########################################
            #Elements for the carbon initialisation

            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]; gate_seq.extend(mbi_seq)

            init_wait_for_trigger = True
            ### C_Init
            carbon_init_seq = self.initialize_carbon_sequence(
                go_to_element = mbi,
                prefix = 'C_' + self.params['C13_init_method'] + str(pt) + '_C',
                wait_for_trigger      = init_wait_for_trigger, pt =pt,
                initialization_method = self.params['C13_init_method'],
                C_init_state          = self.params['C13_init_state'],
                addressed_carbon      = self.params['carbon_nr'],
                el_after_init       = self.params['el_after_init'])
            gate_seq.extend(carbon_init_seq)
            init_wait_for_trigger = False
            
            ### Crosstalk/rabi on same or other C13
            carbon_rabi_seq = Gate('C_Rabi_Ren'+str(pt), 'Carbon_Gate',
                    Carbon_ind  = self.params['Carbon_B'],
                    N           = self.params['Rabi_N_Sweep'][pt],
                    tau         = self.params['Rabi_tau_Sweep'][pt],
                    phase       = self.params['C13_X_phase'])
            gate_seq.extend([carbon_rabi_seq])

  
            ### Tomo
            carbon_tomo_seq = self.readout_carbon_sequence(
                    prefix              = 'Tomo',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = [self.params['carbon_nr']],
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
                pass
                # print '*'*10
                # for g in gate_seq:
                #     print g.name

            if debug:
                for g in gate_seq:
                    print g.name
                    self.print_carbon_phases(g,[self.params['carbon_nr']])

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)
        else:
            print 'upload = false, no sequence uploaded to AWG'

class NuclearRamseyWithRemoteInitialization(MBI_C13):
    '''
    update description still
    This class is to test multiple carbon initialization and Tomography.
    Sequence: |C1 MBI| - |wait time: beating freq*2 = pi| - |M C1 X|(require X) - |C1 ramsey| - |Tomography|
    '''
    mprefix = 'CarbonRamseyInitialised'
    adwin_process = 'MBI_multiple_C13'

    def generate_sequence(self, upload=True, debug=False):
        pts = self.params['pts']

        ### initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Initialized Nuclear Ramsey Sequence')

        for pt in range(pts): ### Sweep over trigger time (= wait time)
            gate_seq = []

            ### Nitrogen MBI
            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]; gate_seq.extend(mbi_seq)

            ### MBI1
            carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                prefix = 'C_MBI1_',
                wait_for_trigger      = True, pt =pt,
                initialization_method = 'MBI',#self.params['C13_init_method'],
                C_init_state          = self.params['init_state'],
                addressed_carbon      = self.params['carbon_nr'],
                el_RO_result          = str(self.params['C13_MBI_RO_state']),
                el_after_init       = self.params['electron_after_init'])
            gate_seq.extend(carbon_init_seq)
            
            if self.params['add_wait_gate'] == True:
                ### Check if free evolution time is larger than the RO time (it can't be shorter)
                if self.params['beating_wait_time']< (self.params['Carbon_init_RO_wait']+3e-6): # because min length is 3e-6
                    print ('Error: carbon evolution time (%s) is shorter than Initialisation RO duration (%s)'
                            %(self.params['beating_wait_time'],self.params['Carbon_init_RO_wait']))
                    qt.msleep(5)
                    ### Add waiting time
                wait_gate = Gate('Wait_gate_max_ent_carbons_' + str(pt),'passive_elt',
                         wait_time = self.params['beating_wait_time'])
                wait_seq = [wait_gate]; gate_seq.extend(wait_seq)


            ### MBI2
            carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                prefix = 'C_MBI2_',
                wait_for_trigger      = False, pt =pt,
                initialization_method = 'MBI',#self.params['C13_init_method'],
                C_init_state          = self.params['init_state'],
                addressed_carbon      = self.params['carbon_nr'],
                el_RO_result          = str(self.params['C13_MBI_RO_state']),
                el_after_init       = self.params['electron_after_init'])
            gate_seq.extend(carbon_init_seq)

            if self.params['add_wait_gate'] == True:
                if self.params['free_evolution_time'][pt]< (self.params['Carbon_init_RO_wait']+3e-6): # because min length is 3e-6
                    print ('Error: carbon evolution time (%s) is shorter than Initialisation RO duration (%s)'
                            %(self.params['free_evolution_time'][pt],self.params['Carbon_init_RO_wait']))
                    qt.msleep(5)
                    ### Add waiting time
                wait_gate = Gate('Wait_gate_'+str(pt),'passive_elt',
                         wait_time = self.params['free_evolution_time'][pt]-self.params['Carbon_init_RO_wait'])
                wait_seq = [wait_gate]; gate_seq.extend(wait_seq)

            ### Readout
            carbon_tomo_seq = self.readout_carbon_sequence(
                    prefix              = 'Tomo',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = [self.params['carbon_nr']],
                    RO_basis_list       = [self.params['C_RO_phase'][pt]],
                    readout_orientation = self.params['electron_readout_orientation'])
            gate_seq.extend(carbon_tomo_seq)

            gate_seq = self.generate_AWG_elements(gate_seq,pt)

            ### Convert elements to AWG sequence and add to combined list
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq, explicit=True)
            combined_list_of_elements.extend(list_of_elements)

            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)

            if debug:
                for g in gate_seq:
                    print g.name
                    self.print_carbon_phases(g,[self.params['carbon_nr']])

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'

class NuclearRabiWithInitialization(MBI_C13):
    '''
    Runs a rabi oscillation on a initialized carbon spin.
    Sequence: |C-init| -|Ren|^(2n)-|Tomography|
    '''
    mprefix = 'CarbonPiCal'
    adwin_process = 'MBI_multiple_C13'

    def generate_sequence(self, upload=True, debug=False):
        pts = self.params['pts']

        ### initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Initialized Nuclear Rabi Sequence')

        for pt in range(pts): ### Sweep over trigger time (= wait time)
            gate_seq = []

            ### Nitrogen MBI
            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]; gate_seq.extend(mbi_seq)

            ### Carbon initialization
            if int(self.params['nr_of_pulses_list'][pt]) == 0:
                el_after_init = '0'
            else:
                el_after_init = self.params['el_after_init']

            carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                prefix = 'C_MBI_',
                wait_for_trigger      = True, pt =pt,
                initialization_method = self.params['C13_init_method'],
                C_init_state          = self.params['init_state'],
                addressed_carbon      = self.params['carbon_nr'],
                el_RO_result          = str(self.params['C13_MBI_RO_state']),
                el_after_init         = el_after_init)

            gate_seq.extend(carbon_init_seq)

            ### number of pulses


            Rabi_pulses = Gate('C' + str(self.params['carbon_nr']) + 'Rabi_'+ str(self.params['nr_of_pulses_list'][pt]) +'_pt'+str(pt)+'_', 'Carbon_Gate',
                    Carbon_ind = self.params['carbon_nr'],
                    N = self.params['nr_of_pulses_list'][pt],
                    tau = self.params['C1_unc_tau_p1'][0],
                    phase = self.params[self.params['gate_phase']])


            gate_seq.extend([Rabi_pulses])
      

            ### Readout
            carbon_tomo_seq = self.readout_carbon_sequence(
                    prefix              = 'Tomo',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = [self.params['carbon_nr']],
                    RO_basis_list       = self.params['C_RO_basis'],
                    el_state_in         = int(el_after_init),
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
                    self.print_carbon_phases(g,[self.params['carbon_nr']])

                    if debug and hasattr(g,'el_state_before_gate'):

                        print 'el state before and after (%s,%s)'%(g.el_state_before_gate, g.el_state_after_gate)
                    elif debug:
                        print 'does not have attribute el_state_before_gate'
        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'            

class NuclearT1(MBI_C13):
    '''
    MAB 14-3-15
    New script replacing NuclearT1_Old which allows to initialize multiple carbons
    1. MBI initialisation
    2. Carbon initialisation into Z or initialization of several carbons.
    3. Carbon T1 evolution
    4. Carbon Z-Readout
    '''
    mprefix = 'NuclearT1'
    adwin_process = 'MBI_multiple_C13'

    def generate_sequence(self, upload=True, debug=False):
        pts = self.params['pts']

        ### initialize empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Nuclear T1')

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
                    el_after_init         = self.params['el_after_init'])
                gate_seq.extend(carbon_init_seq)
                init_wait_for_trigger = False

            ### MBE - measurement based entanglement
            for kk in range(self.params['Nr_MBE']):

                probabilistic_MBE_seq = self.readout_carbon_sequence(
                        prefix              = 'MBE' + str(kk+1),
                        pt                  = pt,
                        go_to_element       = mbi,
                        event_jump_element  = 'next',
                        RO_trigger_duration = 150e-6,
                        carbon_list         = self.params['carbon_list'],
                        RO_basis_list       = self.params['MBE_bases'],
                        el_RO_result         = '0')

                gate_seq.extend(probabilistic_MBE_seq)


            if self.params['add_wait_gate'] == True:
                wait_gate = Gate('Wait_gate_'+str(pt),'passive_elt',
                         wait_time = self.params['free_evolution_time'][pt])
                wait_seq = [wait_gate]; gate_seq.extend(wait_seq)

            ### Readout

            carbon_tomo_seq = self.readout_carbon_sequence(
                    prefix              = 'Tomo',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomography Bases'][pt],
                    readout_orientation = self.params['electron_readout_orientation'])
            gate_seq.extend(carbon_tomo_seq)

            gate_seq = self.generate_AWG_elements(gate_seq,pt)

            ### Convert elements to AWG sequence and add to combined list`
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
                    self.print_carbon_phases(g,self.params['carbon_list'])

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'

class NuclearRamseyWithInitialization_v2(MBI_C13):
    '''
    Very flexible C13 Ramsey script, usefull to calibrate ms = +1,0,-1 frequencies. The el_state that will be calibrated is independent of the gates used
    to initialize the carbon atom. The free induction decay transition is denoted by fid_transition
    '''
    mprefix = 'CarbonRamseyInitialised'
    adwin_process = 'MBI_multiple_C13'

    def generate_sequence(self, upload=True, debug=False):
        pts = self.params['pts']
        
        ### initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Initialized Nuclear Ramsey Sequence')

        for pt in range(pts): ### Sweep over trigger time (= wait time)
            gate_seq = []

            ### Nitrogen MBI
            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]; gate_seq.extend(mbi_seq)

            ### Carbon initialization
            carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                prefix = 'C_MBI_',
                wait_for_trigger      = True, pt =pt,
                initialization_method = 'MBI',#self.params['C13_init_method'],
                C_init_state          = self.params['init_state'],
                addressed_carbon      = self.params['carbon_nr'],
                el_RO_result          = str(self.params['C13_MBI_RO_state']),
                el_after_init       = self.params['electron_after_init'])
            gate_seq.extend(carbon_init_seq)
        

                ### Check if free evolution time is larger than the RO time (it can't be shorter)
            if self.params['add_wait_gate'] == True:
                if self.params['multiple_source']:
                    
                    ##check if the electron state =/= 0 and the electron transition during FID is different from the gate, if so, then add in extra pi pulse to 
                    ## get te electron in the 0 state again for readout to start.
                    ### Make sure the electron is in 0 after the free evolution time ###
                    if self.params['C'+str(self.params['carbon_nr'])+'_dec_trans'] != self.params['fid_transition'] and self.params['electron_after_init']!='0':
                        print 'I see that these are not the same so I am adding an extra pi pulse', self.params['C'+str(self.params['carbon_nr'])+'_dec_trans'],self.params['electron_after_init']
                        wait_gate = Gate('Wait_gate_'+str(pt),'passive_elt',
                                        wait_time = self.params['free_evolution_time'][pt]-self.params['Carbon_init_RO_wait'],
                                        specific_transition=self.params['fid_transition'])

                        
                   
                        reset_pi=Gate('Pi_pulse_before_readout_pt_'+str(pt),'electron_Gate',
                                        pt=pt,
                                        Gate_operation='pi',
                                        phase = self.params['X_phase'],
                                        el_state_after_gate = '0',
                                        specific_transition = self.params['fid_transition'])
                       
                        
                        ###This extra gate is added as a fix to bridge between the two transitions when the electron is in an eigenstate###
                        extra_wait=Gate('Wait_gate_next_transition'+str(pt),'passive_elt',
                                        wait_time = 3e-6,specific_transition=self.params['C'+str(self.params['carbon_nr'])+'_dec_trans'])

                        
                        gate_seq.extend([wait_gate, reset_pi, extra_wait]) 
                    

                    else:
                        wait_gate = Gate('Wait_gate_'+str(pt),'passive_elt',
                                        wait_time = self.params['free_evolution_time'][pt]-self.params['Carbon_init_RO_wait'],
                                        specific_transition=self.params['C'+str(self.params['carbon_nr'])+'_dec_trans'])
                        wait_gate_seq=[wait_gate];gate_seq.extend(wait_gate_seq)

                  

              
                elif self.params['free_evolution_time'][pt]< (self.params['Carbon_init_RO_wait']+3e-6): # because min length is 3e-6
                    print ('Error: carbon evolution time (%s) is shorter than Initialisation RO duration (%s)'
                            %(self.params['free_evolution_time'][pt],self.params['Carbon_init_RO_wait']))
                    qt.msleep(5)

                ### Add waiting time
                ###To keep backwards compatibility this function is still here
                else:
                    wait_gate = Gate('Wait_gate_'+str(pt),'passive_elt',
                                    wait_time = self.params['free_evolution_time'][pt]-self.params['Carbon_init_RO_wait'],
                                    specific_transition=self.params['C'+str(self.params['carbon_nr'])+'_dec_trans'])
                    wait_gate_seq=[wait_gate];gate_seq.extend(wait_gate_seq)               

            ### Readout
            carbon_tomo_seq = self.readout_carbon_sequence(
                    prefix              = 'Tomo',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = [self.params['carbon_nr']],
                    RO_basis_list       = [self.params['C_RO_phase'][pt]],
                    readout_orientation = self.params['electron_readout_orientation'])
            gate_seq.extend(carbon_tomo_seq)

            gate_seq = self.generate_AWG_elements(gate_seq,pt)

            ### Convert elements to AWG sequence and add to combined list
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq, explicit=True)
            combined_list_of_elements.extend(list_of_elements)

            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)

            # if not debug:
            #     print '*'*10
            #     for g in gate_seq:
            #         print g.name

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

class NuclearRamseyWithInitialization_v2_DD(MBI_C13):
    '''
    update description still
    This class is to test multiple carbon initialization and Tomography.
    Sequence: |N-MBI| -|CinitA|-|CinitB|-|Tomography|
    '''
    mprefix = 'CarbonRamseyInitialised_DD'
    adwin_process = 'MBI_multiple_C13'

    def generate_sequence(self, upload=True, debug=False):
        pts = self.params['pts']
        
        ### initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Initialized Nuclear Ramsey Sequence')

        for pt in range(pts): ### Sweep over trigger time (= wait time)
            gate_seq = []

            ### Nitrogen MBI
            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]; gate_seq.extend(mbi_seq)

            ### Carbon initialization
            carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                prefix = 'C_MBI_',
                wait_for_trigger      = True, pt =pt,
                initialization_method = 'MBI',#self.params['C13_init_method'],
                C_init_state          = self.params['init_state'],
                addressed_carbon      = self.params['carbon_nr'],
                el_RO_result          = str(self.params['C13_MBI_RO_state']),
                el_after_init       = '0')
            gate_seq.extend(carbon_init_seq)
            
    
                ### Check if free evolution time is larger than the RO time (it can't be shorter)
            if self.params['add_wait_gate'] == True:
                if self.params['multiple_source']:
              
                        ###put the electron in a superposition during the waittime and use DD to keep electron coherence###
                        ####The decoupling sequence can be at a different transition than the C gate###
                        extra_wait_0=Gate('Wait_gate_before_pi2_'+str(pt),'passive_elt',
                                            wait_time = 20e-6,specific_transition=self.params['fid_transition'])

                        # initial_pi2_gate=Gate('Pi2_pulse_before_fid_pt_'+str(pt),'electron_Gate',
                        #                     pt=pt,
                        #                     Gate_operation='pi2',
                        #                     phase = self.params['X_phase'],
                        #                     el_state_after_gate = 'sup',
                        #                     specific_transition = self.params['fid_transition'])
                       
                       #### The actual connection element doing the FID##
                        wait_gate_DD = Gate('El_decoupling_'+str(pt),'electron_decoupling',
                                            dec_duration = self.params['free_evolution_time'][pt],
                                            specific_transition=self.params['fid_transition'],
                                            fixed_dec_duration = True,C_phases_after_gate='reset')
                        self.params['Initial_Pulse']='x'
                        self.params['Final_Pulse']='-x'
                                 
                        # #### pi2 puls back into eigenstate#########
                        # final_pi2_br=Gate('Pi2_pulse_before_readout_pt_'+str(pt),'electron_Gate',
                        #                     pt=pt,
                        #                     Gate_operation='pi2',
                        #                     el_state_after_gate = '0',
                        #                     specific_transition = self.params['fid_transition'],
                        #                     Carbon_ind=self.params['carbon_nr'],
                        #                     phase = self.params['X_phase']+180)

                        ###This extra gate is added as a fix to bridge between this elec pulse and readout###
                        extra_wait_1=Gate('Wait_gate_after_pi2_back'+str(pt),'passive_elt',
                                            wait_time = 3e-6,specific_transition=self.params['C'+str(self.params['carbon_nr'])+'_dec_trans'])
                        

                        wait_seq=[extra_wait_0,wait_gate_DD,extra_wait_1]
                        gate_seq.extend(wait_seq)            

                  

              
                elif self.params['free_evolution_time'][pt]< (self.params['Carbon_init_RO_wait']+3e-6): # because min length is 3e-6
                    print ('Error: carbon evolution time (%s) is shorter than Initialisation RO duration (%s)'
                            %(self.params['free_evolution_time'][pt],self.params['Carbon_init_RO_wait']))
                    qt.msleep(5)
                ### Add waiting time
                else:
                    wait_gate = Gate('Wait_gate_'+str(pt),'passive_elt',
                                    wait_time = self.params['free_evolution_time'][pt]-self.params['Carbon_init_RO_wait'],
                                    specific_transition=self.params['C'+str(self.params['carbon_nr'])+'_dec_trans'])
                    wait_gate_seq=[wait_gate];gate_seq.extend(wait_gate_seq) 
   

            ### Readout
            carbon_tomo_seq = self.readout_carbon_sequence(
                    prefix              = 'Tomo',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = [self.params['carbon_nr']],
                    RO_basis_list       = ['reset'],
                    readout_orientation = self.params['electron_readout_orientation'])
            gate_seq.extend(carbon_tomo_seq)

            gate_seq = self.generate_AWG_elements(gate_seq,pt)

            ### Convert elements to AWG sequence and add to combined list
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq, explicit=True)
            combined_list_of_elements.extend(list_of_elements)

            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)

            # if not debug:
            #     print '*'*10
            #     for g in gate_seq:
            #         print g.name

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



class NuclearT1_OLD(MBI_C13):
    '''
    This class generates the AWG sequence for a C13 T1 experiment.
    1. MBI initialisation
    2. Carbon initialisation into Z or initialization of several carbons.
    3. Carbon T1 evolution
    4. Carbon Z-Readout
    '''
    mprefix = 'CarbonT1'
    adwin_process = 'MBI_multiple_C13'

    def generate_sequence(self,upload=True,debug = False):
        pts = self.params['pts']
        # #initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Carbon T1')

        for pt in range(pts):
            gate_seq = []
            #####################################################
            #####    Generating the sequence elements      ######
            #####################################################
            #Elements for the nitrogen and carbon initialisation

            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]; gate_seq.extend(mbi_seq)

            carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                    initialization_method = 'swap', pt =pt,
                    addressed_carbon= self.params['carbon_nr'],
                    C_init_state = self.params['C13_init_state'],
                    el_RO_result = str(self.params['C13_MBI_RO_state']),
                    el_after_init = str(self.params['el_after_init']))
            gate_seq.extend(carbon_init_seq)
            #Elements for T1 evolution
            print self.params['Carbon_init_RO_wait']
            wait_gate = Gate('Wait_gate_'+str(pt),'passive_elt',
                    wait_time = self.params['wait_times'][pt]-self.params['Carbon_init_RO_wait'])

            C_evol_seq =[wait_gate]; gate_seq.extend(C_evol_seq)

            #############################
            #Readout in the Z basis
            # print 'ro phase = ' + str( self.params['C_RO_phase'][pt])

            #TODO make the read-out use the general Carbon RO sequencer function NK 20141104

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

            # if self.params['electron_readout_orientation'] == 'positive':
            #     extra_phase = 0
            # elif self.params['electron_readout_orientation'] == 'negative':
            #      extra_phase = 180

            # C_basis_Ren = Gate('C_basis_Ren'+str(pt), 'Carbon_Gate',
            #         Carbon_ind = self.params['Addressed_Carbon'][0],
            #         phase = 'reset')

            # C_RO_y = Gate('C_ROy_'+str(pt),'electron_Gate',
            #         Gate_operation='pi2',
            #         phase = self.params['Y_phase']+extra_phase)
            # C_RO_Ren = Gate('C_RO_Ren_'+str(pt), 'Carbon_Gate',
            #         Carbon_ind = self.params['Addressed_Carbon'][0],
            #         phase = self.params['C13_Y_phase']+180)
            # C_RO_x = Gate('C_RO_x_'+str(pt),'electron_Gate',
            #         Gate_operation='pi2',
            #         phase = self.params['X_phase'])
            # C_RO_Trigger = Gate('C_RO_Trigger_'+str(pt),'Trigger')

            # carbon_RO_seq =[C_basis_Ren, C_RO_y, C_RO_Ren, C_RO_x, C_RO_Trigger]

            # Gate seq consits of 3 sub sequences [MBI] [Carbon init]  [RO and evolution]
            # gate_seq = []
            # gate_seq.extend(mbi_seq), gate_seq.extend(carbon_init_seq)
            # gate_seq.extend(C_evol_seq), gate_seq.extend(carbon_RO_seq)
            ############

            gate_seq = self.generate_AWG_elements(gate_seq,pt)
            #Convert elements to AWG sequence and add to combined list
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq, explicit=True)
            combined_list_of_elements.extend(list_of_elements)

            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'

class NuclearT1_repumping(MBI_C13):

    '''
    This class generates the AWG sequence for a C13 T1 experiment under repetitive repumping of the electornic spin to ms=0.
    1. MBI initialisation
    2. Carbon initialisation
    3. Carbon T1 evolution under repetitive repumping to a desired NV spin-state (atm only ms=0 possible)
    4. Carbon Z-Readout

    Additionally offers the possibility to flip the electronic state to ms=-1 with a mw Pi pulse after repumping.
    '''

    mprefix = 'CarbonT1_repumping'
    adwin_process = 'MBI_multiple_C13'

    def generate_sequence(self, upload=True,debug=False):
        pts = self.params['pts']
        # #initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('CarbonT1_rep')


        # set the output power of the repumping AOM to the desired
        qt.pulsar.set_channel_opt('AOM_Newfocus','high', qt.instruments['NewfocusAOM'].power_to_voltage(self.params['repetitive_SP_A_power'],controller='sec'))
        #
        #########################################################################################################################
        #TODO before running this sequence:
        # - check the validity of the while loop which reduces the number of repump repetitions (exit condition ever fulfilled?)#
        # - upload simple sequence and check the correct placement of the waiting times, repumping and electron pi pulses.
        #########################################################################################################################


        for pt in range(pts):

            gate_seq = []


            #####################################################
            #####    Generating the sequence elements      ######
            #####################################################
            #Elements for the nitrogen and carbon initialisation


            #omit the nitrogen initialization comepletely? Will this cause trouble with the ADWIN?

            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]
            gate_seq.extend(mbi_seq)

            carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                    initialization_method = 'swap', pt =pt,
                    addressed_carbon= self.params['Addressed_Carbon'],
                    C_init_state = self.params['C13_init_state'],
                    el_RO_result = str(self.params['C13_MBI_RO_state']),
                    el_after_init = str(self.params['el_after_init']))


            gate_seq.extend(carbon_init_seq)

            #########################################################
            #Apply repumping scheme/ interleave with waiting gates! #
            #########################################################


            # This while statement reduces the repump repetitions until...
            # every repumping event will be interleaved by a wait time of at least 10 us.

            # while (self.params['wait_times'][pt]-self.params['Carbon_init_RO_wait']-self.params['repetitive_SP_A_duration']*self.params['repump_repetitions'][0]*1e-6)/self.params['repump_repetitions'][0] < 10e-6:
            #     self.params['repump_repetitions'][0]-=1 #decrement repump repetitions. Too much repumping for a decent spacing.


            #wait_time between every repumping cycle, if additional e- gate, subtract that time as well.
            cycle_wait = (self.params['wait_times'][pt]-self.params['Carbon_init_RO_wait']-self.params['repetitive_SP_A_duration']*(self.params['repump_repetitions'][0]+1)*1e-6)/self.params['repump_repetitions'][0]

            electron_repump_seq=[]


            C_rep_pump=Gate('C_rep_pump'+str(pt),'Trigger',
                duration=self.params['repetitive_SP_A_duration']*1e-6, #needs to be in us?? or in s??
                )
            C_rep_pump.channel='AOM_Newfocus'
            C_rep_pump.elements_duration=self.params['repetitive_SP_A_duration']*1e-6

            C_rep_Pi=Gate('C_rep_pi'+str(pt),'electron_Gate',
                Gate_operation='pi')

            # if additional e- gate, subtract that time as well.
            if self.params['el_after_init'] == 1:
                cycle_wait = cycle_wait-C_rep_Pi.duration


            C_rep_wait=Gate('C_rep_wait'+str(pt),'passive_elt',
                wait_time=cycle_wait)


            electron_repump_seq.extend([C_rep_wait,C_rep_pump,C_rep_Pi])


            gate_seq.extend(electron_repump_seq)


            # wait_gate = Gate('Wait_gate_'+str(pt),'passive_elt',
            #         wait_time = self.params['wait_times'][pt]-self.params['Carbon_init_RO_wait'])

            ###########################
            # Readout  in the Z basis #
            ###########################


            carbon_RO_seq = self.readout_carbon_sequence(
                    prefix= 'C_RO',
                    pt=pt,
                    carbon_list=[self.params['Addressed_Carbon']],
                    RO_basis_list = ['Z'],
                    RO_trigger_duration = 10e-6, #is this a good value? Always used in TOMO measurements. Norbert
                    go_to_element = None,
                    event_jump_element = None,
                    readout_orientation = self.params['electron_readout_orientation'])

            gate_seq.extend(carbon_RO_seq)


            gate_seq = self.generate_AWG_elements(gate_seq,pt)
            #Convert elements to AWG sequence and add to combined list
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq, explicit=True)
            combined_list_of_elements.extend(list_of_elements)

            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'

class NuclearRabiWithDirectRF(MBI_C13):
    '''
    Made by Michiel 
    This class tests an RF pulse on a nuclear spin
    1. Nitrogen MBI initialisation
    2. Carbon init (MBI or SWAP)
    3. Pulse on single nuclear spin using RF
    4. Carbon Full Tomo

    Sequence: |N-MBI| -|CinitA|-|RF-Pulse|-|Tomography|
    '''
    mprefix = 'NuclearRFRabi' #Changed
    adwin_process = 'MBI_multiple_C13'

    def generate_sequence(self, upload=True, debug=False):
        pts = self.params['pts']

        ### initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Carbon Rabi Direct RF')

        for pt in range(pts): ### Sweep over trigger time (= wait time)
            gate_seq = []





            ### Nitrogen MBI
            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]; gate_seq.extend(mbi_seq)

            ### Carbon initialization 
            carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                prefix = 'C_MBI_',
                wait_for_trigger      = True, pt =pt,
                initialization_method = self.params['C13_init_method'],
                C_init_state          = self.params['init_state'],
                addressed_carbon      = self.params['carbon_nr'],
                el_RO_result          = str(self.params['C13_MBI_RO_state']),
                el_after_init         = self.params['el_after_init'])
            gate_seq.extend(carbon_init_seq)

            ### Carbon RF pulse
            if self.params['RF_pulse_durations'][pt] > 3e-6:
                rabi_pulse = Gate('Rabi_pulse_'+str(pt),'RF_pulse',
                    length      = self.params['RF_pulse_durations'][pt],
                    RFfreq      = self.params['RF_pulse_frqs'][pt],
                    amplitude   = self.params['RF_pulse_amps'][pt])
                gate_seq.extend([rabi_pulse])

            ### Readout
            carbon_tomo_seq = self.readout_carbon_sequence(
                    prefix              = 'Tomo',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = [self.params['carbon_nr']],
                    RO_basis_list       = [self.params['C_RO_phase'][pt]],
                    readout_orientation = self.params['electron_readout_orientation'])
            gate_seq.extend(carbon_tomo_seq)

            # #Add wait gate to test RF influence
            # if self.params['add_wait_gate'] == True:
            #     if self.params['free_evolution_time'][pt]< (3e-6):
            #         print ('Error: carbon evolution time is too small')
            #         qt.msleep(5)
            #         ### Add waiting time
            #     wait_gate = Gate('Wait_gate_'+str(pt),'passive_elt',
            #              wait_time = self.params['free_evolution_time'][pt])
            #     wait_seq = [wait_gate]; gate_seq.extend(wait_seq)




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

class Nuclear_Crosstalk(MBI_C13):
    '''
    update description still
    This class is to test multiple carbon initialization and Tomography.
    Sequence: |N-MBI| -|CinitA|-|CinitB|-|MBE|-|Tomography|
    '''
    mprefix = 'CarbonRamseyInitialised'
    adwin_process = 'MBI_multiple_C13'

    def generate_sequence(self, upload=True, debug=False):
        pts = self.params['pts']

        ### initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Initialized Nuclear Ramsey Sequence')

        try:
            self.params['nr_of_gates']  
        except:
            self.params['nr_of_gates'] = 1
        

        for pt in range(pts): ### Sweep over trigger time (= wait time)
            gate_seq = []

            ### Nitrogen MBI
            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]; gate_seq.extend(mbi_seq)

            ### Carbon initialization
            carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                prefix = 'C_MBI_',
                wait_for_trigger      = True, pt =pt,
                initialization_method = 'MBI',#self.params['C13_init_method'],
                C_init_state          = self.params['init_state'],
                addressed_carbon      = self.params['carbon_nr'],
                el_RO_result          = str(self.params['C13_MBI_RO_state']))
            gate_seq.extend(carbon_init_seq)

            ### Add gate to other carbon spin

            for gate_nr in range(1,self.params['nr_of_gates']+1):
                carbon_gate = Gate('C'+str(self.params['Carbon_B'])+'_unconditional_gate_' + str(gate_nr) + '_pt_' +str(pt),
                                    'Carbon_Gate',
                                    Carbon_ind = self.params['Carbon_B'],
                                    phase = 'reset')
                gate_seq.extend([carbon_gate])

            ### Readout
            carbon_tomo_seq = self.readout_carbon_sequence(
                    prefix              = 'Tomo',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = [self.params['carbon_nr']],
                    RO_basis_list       = [self.params['C_RO_phase'][pt]],
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
                # for g in gate_seq:
                #     print g.name

            if debug:
                for g in gate_seq:
                    print g.name
                    self.print_carbon_phases(g,[self.params['carbon_nr']])

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'

class Nuclear_gate_characterization(MBI_C13):
    '''
    update description still
    This class is to determine the effect of many carbon gates
    Sequence: |C-init| -|Ren|^(2n)-|Tomography|
    '''
    mprefix = 'CarbonPiCal'
    adwin_process = 'MBI_multiple_C13'

    def generate_sequence(self, upload=True, debug=False):
        pts = self.params['pts']

        ### initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Initialized Nuclear Rabi Sequence')

        for pt in range(pts): ### Sweep over trigger time (= wait time)
            gate_seq = []

            ### Nitrogen MBI
            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]; gate_seq.extend(mbi_seq)

            ### Carbon initialization
            if int(self.params['nr_of_gates_list'][pt]) == 0:
                el_after_init = '0'
            else:
                el_after_init = self.params['el_after_init']

            carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                prefix = 'C_MBI_',
                wait_for_trigger      = True, pt =pt,
                initialization_method = self.params['C13_init_method'],
                C_init_state          = self.params['init_state'],
                addressed_carbon      = self.params['carbon_nr'],
                el_RO_result          = str(self.params['C13_MBI_RO_state']),
                el_after_init         = el_after_init)

            gate_seq.extend(carbon_init_seq)

            if self.params['el_during_experiment'] == 'sup' and int(self.params['nr_of_gates_list'][pt]) != 0:
                pi2_electron =    Gate(prefix+'_init_pi2_el_'+str(pt),'electron_Gate',
                Gate_operation ='pi2',
                wait_for_trigger = True,
                phase = m.params['Y_phase'])
                gate_seq.extend(pi2_electron)

            self.params['Carbon_pi_duration'] = 4 * self.params['C'+str(self.params['carbon_nr'])+
                                            '_Ren_N'+self.params['electron_transition']][0] * self.params['C'+str(self.params['carbon_nr'])
                                            +'_Ren_tau'+self.params['electron_transition']][0]

            self.params['total_time'] = self.params['nr_of_gates_list'][pts-1]*self.params['Carbon_pi_duration']

            ### Free evolution_time/ number of gates

            for gate_nr in range(int(self.params['nr_of_gates_list'][pt])):

                Pi_part_1 = Gate('C' + str(self.params['carbon_nr']) + '_pi' +  '1_' + str(gate_nr) +'_pt'+str(pt)+'_', 'Carbon_Gate',
                        Carbon_ind = self.params['carbon_nr'],
                        phase = self.params[self.params['gate_phase']])

                Pi_part_2 = Gate('C' + str(self.params['carbon_nr']) + '_pi' +  '2_' + str(gate_nr) +'_pt'+str(pt)+'_', 'Carbon_Gate',
                        Carbon_ind = self.params['carbon_nr'],
                        phase = self.params[self.params['gate_phase']])

                gate_seq.extend([Pi_part_1, Pi_part_2])

            # add waittime
            if self.params['constant_time'] == True and pt != pts-1:
                self.params['waittime'] = self.params['total_time'] - self.params['nr_of_gates_list'][pt]*self.params['Carbon_pi_duration']
                print 'test'
                print pt
                print self.params['total_time']
                print self.params['waittime']
                wait_gate = Gate('Wait_gate_'+str(pt),'passive_elt',
                         wait_time = self.params['waittime'])

                wait_seq = [wait_gate]; gate_seq.extend(wait_seq)              

            ### Readout
            carbon_tomo_seq = self.readout_carbon_sequence(
                    prefix              = 'Tomo',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = [self.params['carbon_nr']],
                    RO_basis_list       = self.params['C_RO_basis'],
                    el_state_in         = int(el_after_init),
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
                    self.print_carbon_phases(g,[self.params['carbon_nr']])
                    if debug and hasattr(g,'el_state_before_gate'):# != None:
                        # print g.el_state_before_gate
                        print '                        el state before and after (%s,%s)'%(g.el_state_before_gate, g.el_state_after_gate)
                    elif debug:
                        print 'does not have attribute el_state_before_gate'
        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'

class EchoGateInit(MBI_C13):
    """
    Performs an initialisation via the Echo gate of the Carbon in 'up' or 'down'.
    Afterwards the quality of the gate is analyzed via tomography in Z with conventional gates.
    AR & NK 
    """
    mprefix = 'EchoGate'
    adwin_process = 'MBI_multiple_C13'

    def generate_sequence(self,upload=True,debug=False):

        pts = self.params['pts']
        # #initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Initialized Nuclear-gate sequence')

        #self.get_tau_larmor()

        for pt in range(pts):

            ###########################################
            #### Generating the sequence elements #####
            ###########################################
            #Elements for the carbon initialisation
            print self.params['Carbon_init_RO_wait']
            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]


            carbon_init_seq = self.initialize_carbon_echogate(go_to_element = mbi, pt =pt,
                    addressed_carbon= self.params['Carbon_nr'],
                    C_init_state = self.params['C13_init_state'],
                    el_RO_result = '0',
                    wait_time=self.params['waiting_times'][pt])
            

            # carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi, pt =pt,
            #         addressed_carbon= self.params['Carbon_nr'],
            #         C_init_state = self.params['C13_init_state'],
            #         initialization_method   = 'swap',
            #         el_RO_result = '0' )

            
            ###############################
            ### generate the RO         ###
            ###############################


            if self.params['use_Echo_gate_RO']:
                carbon_RO_seq =  self.readout_single_carbon_echogate(
                    prefix              = 'C_RO',
                    pt                  =  pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    addressed_carbon    = self.params['Carbon_nr'],
                    RO_trigger_duration = 10e-6,
                    el_RO_result        = '0',
                    readout_orientation = self.params['electron_readout_orientation'],
                    wait_time=self.params['waiting_times'][pt]
                    )

            else:
                carbon_RO_seq =  self.readout_carbon_sequence(
                    prefix              = 'C_RO',
                    pt                  =  pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    carbon_list         = [self.params['Carbon_nr']],
                    RO_basis_list       = ['Z'],
                    RO_trigger_duration = 10e-6,
                    el_RO_result        = '0',
                    readout_orientation = self.params['electron_readout_orientation'],
                    )


            # Piece the gate sequence together.
            gate_seq = []
            gate_seq.extend(mbi_seq)
            gate_seq.extend(carbon_init_seq)
            gate_seq.extend(carbon_RO_seq)
            ############

            gate_seq = self.generate_AWG_elements(gate_seq,pt)
            #Convert elements to AWG sequence and add to combined list
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq, explicit=True)
            combined_list_of_elements.extend(list_of_elements)

            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'


        if debug:
            for g in gate_seq:
                print '----------'
                print g.name
                print '----------'
                self.print_carbon_phases(g,[self.params['Carbon_nr']])

class EchoGate(MBI_C13):
    '''
    This class is used to determine the effectiveness of a new type of gate.
    The sequence consists of the following steps:

    1. MBI initialisation
    2. Carbon initialisation (Swap or MBI)
    2a. optional pi/2 pulse on the electronic state.
    3. wait some time (this will entangle the two particles)
    4a. Unconditional pi rotation on the carbon
    4b. Pi pulse on the electronic state
    5. wait some time (this will entangle the two particles)
    5a. optional pi/2 pulse on the electornic state
    6. RO of the electronic state.
    '''

    mprefix = 'Carbon_Echo_Gate'
    adwin_process = 'MBI_multiple_C13'

    def generate_sequence(self,upload=True,debug = False):
        pts = self.params['pts']
        # #initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Initialized Nuclear-gate sequence')

        #self.get_tau_larmor()

        for pt in range(pts):

            ###########################################
            #### Generating the sequence elements #####
            ###########################################
            #Elements for the carbon initialisation

            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]

            carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                    initialization_method = self.params['C13_init_method'], pt =pt,
                    addressed_carbon= self.params['Carbon_nr'],
                    C_init_state = self.params['C13_init_state'],
                    el_RO_result = '0' )
            ################################
            ##the two wait gates to be put in the beginning and end
            wait_gate1 = Gate('Wait_gate1_'+str(pt),'passive_elt',
                                 wait_time = self.params['waiting_times'][pt])
            wait_gate2 = Gate('Wait_gate2_'+str(pt),'passive_elt',
                                 wait_time = self.params['waiting_times'][pt])

            ###
            ## unconditional rotations on the two spins
            if self.params['do_carbon_pi'] == True:
                C_uncond_Pi = Gate('C_uncond_Pi'+str(pt), 'Carbon_Gate',
                        Carbon_ind = self.params['Carbon_nr'],
                        N = self.params['C'+str(self.params['Carbon_nr'])+'_uncond_pi_N'][0],
                        tau = self.params['C'+str(self.params['Carbon_nr'])+'_uncond_tau'][0],
                        phase = self.params['C13_X_phase'])
                print 'N: ', self.params['C'+str(self.params['Carbon_nr'])+'_uncond_pi_N'][0]
                print 'tau: ', self.params['C'+str(self.params['Carbon_nr'])+'_uncond_tau'][0]
            #wait_gate1.C_phases_after_gate=10*[0]

            else:
                C_uncond_Pi = Gate('C_uncond_rot'+str(pt), 'Carbon_Gate',
                        Carbon_ind = self.params['Carbon_nr'],
                        N = self.params['Number_of_pulses'][pt],
                        tau = self.params['C'+str(self.params['Carbon_nr'])+'_uncond_tau'][0],
                        phase = self.params['C13_X_phase'])


            E_Pi=Gate('E_Pi'+str(pt),'electron_Gate',
                                        Gate_operation='pi',
                                        phase = self.params['X_phase'])

            ###Before piecing the sequence together, two pi/2 pulses on the elctronic state need to be defined
            E_init_y = Gate('E'+str(self.params['Carbon_nr'])+'_init_y_pt'+str(pt),'electron_Gate',
                Gate_operation ='pi2',
                phase =self.params['Y_phase'])

            if self.params['e_ro_orientation'] == 'negative':
                RO_phase=self.params['Y_phase']+180
            else:
                RO_phase=self.params['Y_phase']


            E_RO_y = Gate('E'+str(self.params['Carbon_nr'])+'_RO_y_pt'+str(pt),'electron_Gate',
                Gate_operation ='pi2',
                phase =RO_phase)

            

            ## put this part of the sequence together.
            if self.params['E_superposition']:
                C_pi_seq =[E_init_y,wait_gate1,C_uncond_Pi,E_Pi,wait_gate2,E_RO_y]
            else:
                C_pi_seq =[wait_gate1,C_uncond_Pi,E_Pi,wait_gate2]


            RO_Trigger = Gate('C'+str(self.params['Carbon_nr'])+'_Trigger_'+str(pt),'Trigger',
                elements_duration= 10e-6,
                el_state_before_gate = '0')



            # Piece the gate sequence together.
            gate_seq = []
            gate_seq.extend(mbi_seq), gate_seq.extend(carbon_init_seq)
            gate_seq.extend(C_pi_seq), gate_seq.extend([RO_Trigger])
            ############

            gate_seq = self.generate_AWG_elements(gate_seq,pt)
            #Convert elements to AWG sequence and add to combined list
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq, explicit=True)
            combined_list_of_elements.extend(list_of_elements)

            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'


        if debug:
            for g in gate_seq:
                print '----------'
                print g.name
                print '----------'
                self.print_carbon_phases(g,[self.arams['Carbon_nr']])

class Sweep_Carbon_Gate(MBI_C13):
    """
    Performs MBI on a carbon and allows for varying gate parameters.
    """

    mprefix = 'Sweep_carbon_Gate'
    adwin_process = 'MBI_multiple_C13'

    def generate_sequence(self, upload=True, debug=False):
        pts = self.params['pts']

        ### initialize empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('SweepCarbonInit')

        for pt in range(pts): ### Sweep over RO basis
            gate_seq = []

            ### Nitrogen MBI
            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]; gate_seq.extend(mbi_seq)

            ### Carbon initialization
            init_wait_for_trigger = True
            
            for kk in range(self.params['Nr_C13_init']):
                print self.params['init_method_list'][kk]
                print self.params['init_state_list'][kk]
                print self.params['carbon_init_list'][kk]
                print 

                carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                    prefix = 'C_MBI' + str(kk+1) + '_C',
                    wait_for_trigger      = init_wait_for_trigger, pt =pt,
                    initialization_method = self.params['init_method_list'][kk],
                    C_init_state          = self.params['init_state_list'][kk],
                    addressed_carbon      = self.params['carbon_init_list'][kk],
                    el_after_init         = self.params['el_after_init'],
                    swap_phase            = self.params['init_phase_list'][pt])
                gate_seq.extend(carbon_init_seq)
                init_wait_for_trigger = False



            carbon_tomo_seq = self.readout_carbon_sequence(
                    prefix              = 'Tomo',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomography Bases'][pt],
                    el_state_in         = int(self.params['el_after_init']),
                    readout_orientation = self.params['electron_readout_orientation'])            


            gate_seq.extend(carbon_tomo_seq)

            ### sweep carbon gates!
            for i,g in enumerate(gate_seq):
                if g.Gate_type == 'Carbon_Gate':
                    g.N = self.params['N_list'][pt]
                    g.tau = self.params['tau_list'][pt]

            gate_seq = self.generate_AWG_elements(gate_seq,pt)

            ### Convert elements to AWG sequence and add to combined list`
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq, explicit=True)
            combined_list_of_elements.extend(list_of_elements)

            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)

            if not debug:
                print '*'*10
                # for g in gate_seq:
                #     print g.name

            # if debug:
                # for g in gate_seq:
                #     print g.name
                #     self.print_carbon_phases(g,self.params['carbon_list'])

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'
            
class Sweep_Uncond_Carbon_Gate(MBI_C13):
    """
    Performs MBI on a carbon and allows for varying gate parameters.
    """

    mprefix = 'Sweep_uncond_carbon_Gate'
    adwin_process = 'MBI_multiple_C13'

    def generate_sequence(self, upload=True, debug=False):
        pts = self.params['pts']

        ### initialize empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('SweepCarbonInit')

        for pt in range(pts): ### Sweep over RO basis
            gate_seq = []

            ### Nitrogen MBI
            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]; gate_seq.extend(mbi_seq)

            ### Carbon initialization
            init_wait_for_trigger = True
            
            for kk in range(self.params['Nr_C13_init']):
               
                print self.params['init_state_list'][kk]
                print self.params['carbon_init_list'][kk]
                print 

                carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                    prefix = 'C_MBI' + str(kk+1) + '_C',
                    wait_for_trigger      = init_wait_for_trigger, pt =pt,
                    initialization_method = 'swap',
                    C_init_state          = self.params['init_state_list'][kk],
                    addressed_carbon      = self.params['carbon_init_list'][kk],
                    el_after_init         = self.params['el_after_init'],
                    swap_phase            = self.params['init_phase_list'][pt])
                gate_seq.extend(carbon_init_seq)
                init_wait_for_trigger = False

            C_unc = self.unconditional_carbon_gate('C_unc_pt'+str(pt),
                        Carbon_ind  = self.params['carbon_init_list'][kk],
                        phase       =  0)

            C_unc.N = self.params['N_list'][pt]
            C_unc.tau = self.params['tau_list'][pt]

            gate_seq.append(C_unc)



            carbon_tomo_seq = self.readout_carbon_sequence(
                    prefix              = 'Tomo',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomography Bases'][pt],
                    el_state_in         = int(self.params['el_after_init']),
                    readout_orientation = self.params['electron_readout_orientation'])            


            gate_seq.extend(carbon_tomo_seq)

            
            gate_seq = self.generate_AWG_elements(gate_seq,pt)

            ### Convert elements to AWG sequence and add to combined list`
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq, explicit=True)
            combined_list_of_elements.extend(list_of_elements)

            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)

            if not debug:
                print '*'*10
                # for g in gate_seq:
                #     print g.name

            # if debug:
                # for g in gate_seq:
                #     print g.name
                #     self.print_carbon_phases(g,self.params['carbon_list'])

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'
    

class Sweep_Z_init_phase(MBI_C13):
    """
    Performs MBI on a carbon and allows for varying gate parameters.
    """

    mprefix = 'Sweep_carbon_Gate'
    adwin_process = 'MBI_multiple_C13'

    def generate_sequence(self, upload=True, debug=False):
        pts = self.params['pts']

        ### initialize empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('SweepCarbonInit')

        for pt in range(pts): ### Sweep over RO basis
            gate_seq = []

            ### Nitrogen MBI
            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]; gate_seq.extend(mbi_seq)

            ### Carbon initialization
            init_wait_for_trigger = True
            
            for kk in range(self.params['Nr_C13_init']):
                # print self.params['init_method_list'][kk]
                # print self.params['init_state_list'][kk]
                # print self.params['carbon_init_list'][kk]
                # print 

                carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                    prefix = 'C_MBI' + str(kk+1) + '_C',
                    wait_for_trigger      = init_wait_for_trigger, pt =pt,
                    initialization_method = self.params['init_method_list'][kk],
                    C_init_state          = self.params['init_state_list'][kk],
                    addressed_carbon      = self.params['carbon_init_list'][kk],
                    el_after_init         = self.params['el_after_init'],
                    swap_phase            = self.params['init_phase_list'][pt])
                gate_seq.extend(carbon_init_seq)
                init_wait_for_trigger = False



            carbon_tomo_seq = self.readout_carbon_sequence(
                    prefix              = 'Tomo',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomography Bases'][pt],
                    el_state_in         = int(self.params['el_after_init']),
                    readout_orientation = self.params['electron_readout_orientation'])            


            gate_seq.extend(carbon_tomo_seq)

            gate_seq = self.generate_AWG_elements(gate_seq,pt)

            ### Convert elements to AWG sequence and add to combined list`
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq, explicit=True)
            combined_list_of_elements.extend(list_of_elements)

            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)

            if not debug:
                print '*'*10
                for g in gate_seq:
                    print g.name

            # if debug:
                # for g in gate_seq:
                #     print g.name
                #     self.print_carbon_phases(g,self.params['carbon_list'])

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'

class Sweep_Z_init_phase_v2(MBI_C13):
    """
    Performs MBI on a carbon and allows for varying gate parameters.
    """

    mprefix = 'Sweep_carbon_Gate'
    adwin_process = 'MBI_multiple_C13'

    def generate_sequence(self, upload=True, debug=False):
        pts = self.params['pts']

        ### initialize empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('SweepCarbonInit')

        for pt in range(pts): ### Sweep over RO basis
            gate_seq = []

            ### Nitrogen MBI
            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]; gate_seq.extend(mbi_seq)

            ### Carbon initialization
            init_wait_for_trigger = True
            
            for kk in range(self.params['Nr_C13_init']):
                # print self.params['init_method_list'][kk]
                # print self.params['init_state_list'][kk]
                # print self.params['carbon_init_list'][kk]
                # print 

                carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                    prefix = 'C_MBI' + str(kk+1) + '_C',
                    wait_for_trigger      = init_wait_for_trigger, pt =pt,
                    initialization_method = self.params['init_method_list'][kk],
                    C_init_state          = self.params['init_state_list'][kk],
                    addressed_carbon      = self.params['carbon_init_list'][kk],
                    el_after_init         = self.params['el_after_init'],
                    wait_time             = self.params['wait_time_list'][pt])
                gate_seq.extend(carbon_init_seq)
                init_wait_for_trigger = False


            carbon_tomo_seq = self.readout_carbon_sequence(
                    prefix              = 'Tomo',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomography Bases'][pt],
                    el_state_in         = int(self.params['el_after_init']),
                    readout_orientation = self.params['electron_readout_orientation'])            


            gate_seq.extend(carbon_tomo_seq)

            gate_seq = self.generate_AWG_elements(gate_seq,pt)

            ### Convert elements to AWG sequence and add to combined list`
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq, explicit=True)
            combined_list_of_elements.extend(list_of_elements)

            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)

            if not debug:
                pass
                # print '*'*10
                # for g in gate_seq:
                #     # print g.name

            # if debug:
                # for g in gate_seq:
                #     print g.name
                #     self.print_carbon_phases(g,self.params['carbon_list'])

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'

### Multiple carbon initialization classes ###
class elec_to_carbon_swap(MBI_C13):
    '''
    Sequence: |Initialize Carbons| - |Prepare NV1| - |SWAP NV1-C1| -|Tomography|
    '''
    mprefix         = 'Swap_gate'
    adwin_process   = 'MBI_multiple_C13'


    def generate_sequence(self, upload=True, debug=False):

        pts = self.params['pts']

        ### initialize empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Two Qubit SWAP')


        for pt in range(pts): ### Sweep over RO basis
            gate_seq = []

            ### Nitrogen MBI
            # Doesn't do anything?
            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]; gate_seq.extend(mbi_seq)

            ### Carbon initialization
            init_wait_for_trigger = True
            
            #SWAP kk = 1
            
            # print self.params['init_method_list']
            # print self.params['init_state_list']
            # print self.params['carbon_init_list']
            # print 
            
            if self.params['el_after_init']           == '1':
                self.params['do_wait_after_pi']            = True
            else: 
                self.params['do_wait_after_pi']            = False

            if self.params['SWAP_type'] == 'swap_w_init' or self.params['SWAP_type'] == 'prob_init':
                init_carbon = True
            else:
                init_carbon = False

            #######################
            ## INITIALIZE CARBON ##
            #######################
            if init_carbon:
                carbon_init_seq = self.initialize_carbon_sequence(
                    go_to_element         = mbi,
                    prefix                = 'init_C',
                    wait_for_trigger      = init_wait_for_trigger, 
                    pt                    = pt,
                    initialization_method = self.params['init_method_list'][0],
                    C_init_state          = self.params['init_state_list'][0],
                    addressed_carbon      = self.params['carbon_init_list'][0],
                    do_wait_after_pi      = self.params['do_wait_after_pi'])
                gate_seq.extend(carbon_init_seq)

                init_wait_for_trigger = False

            ###############################################################
            # ELECTRON STATE PREPARE it is already in 0 after INIT carbon #
            ###############################################################
            electron_init_seq = self.initialize_electron_sequence(
                prefix                  = 'init_E',
                elec_init_state         = self.params['elec_init_state'],
                pt                      = pt,
                el_after_c_init         = self.params['el_after_init'],
                wait_for_trigger        = init_wait_for_trigger)
            gate_seq.extend(electron_init_seq)

            # gate_seq.append(Gate('Wait_gate'+str(pt),'passive_elt',wait_time = 5e-6))

            # # # print "gate_seq after electron_init", gate_seq

            ########################
            ## SWAP + el reset/RO ##
            ########################
            carbon_swap_seq = self.carbon_swap_gate_multi_options(
                go_to_element         = mbi,
                prefix                = 'swap_C', 
                pt                    = pt,
                addressed_carbon      = self.params['carbon_init_list'][0],
                RO_after_swap         = self.params['RO_after_swap'],
                swap_type             = self.params['SWAP_type'])
            gate_seq.extend(carbon_swap_seq)

            # # # print "gate_seq after swap", gate_seq


            ####################
            ## READOUT CARBON ##
            ####################
            carbon_tomo_seq = self.readout_carbon_sequence(
                prefix              = 'Tomo',
                pt                  = pt,
                go_to_element       = None,
                event_jump_element  = None,
                RO_trigger_duration = 10e-6,
                carbon_list         = self.params['carbon_list'],
                RO_basis_list       = self.params['Tomography Bases'][pt],
                el_state_in         = int(self.params['el_after_init']),
                readout_orientation = self.params['electron_readout_orientation'])
            gate_seq.extend(carbon_tomo_seq)



            gate_seq = self.generate_AWG_elements(gate_seq,pt)

            ### Convert elements to AWG sequence and add to combined list`
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq, explicit=True)
            combined_list_of_elements.extend(list_of_elements)

            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)

            if not debug:
                pass
                # print '*'*10
                # for g in gate_seq:
                #     print g.name####
        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'

class Two_QB_Probabilistic_MBE(MBI_C13):
    '''
    Sequence: |N-MBI| -|Cinit|^N2-|MBE|^N1-|Tomography|
    ''' 
    mprefix = 'probabablistic_MBE_Tomography'
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
                # print self.params['init_method_list'][kk]
                # print self.params['init_state_list'][kk]
                # print self.params['carbon_init_list'][kk]
                # print 

                if self.params['el_after_init']                == '1':
                    self.params['do_wait_after_pi']            = True
                else: 
                    self.params['do_wait_after_pi']            = False

                carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                    prefix = 'C_' + self.params['init_method_list'][kk] + str(kk+1) + '_C',
                    wait_for_trigger      = init_wait_for_trigger, pt =pt,
                    initialization_method = self.params['init_method_list'][kk],
                    C_init_state          = self.params['init_state_list'][kk],
                    addressed_carbon      = self.params['carbon_init_list'][kk],
                    el_after_init         = self.params['el_after_init'],
                    do_wait_after_pi      = self.params['do_wait_after_pi'])
                gate_seq.extend(carbon_init_seq)
                init_wait_for_trigger = False


            ### MBE - measurement based entanglement
            for kk in range(self.params['Nr_MBE']):

                probabilistic_MBE_seq = self.logic_init_seq(
                        prefix              = 'Ent_state_init_' + str(kk+1),
                        pt                  =  pt,
                        carbon_list         = self.params['carbon_list'],
                        RO_basis_list       = self.params['MBE_bases'],
                        RO_trigger_duration = 150e-6,
                        el_RO_result        = '0',
                        logic_state         = self.params['logical_state'] ,
                        go_to_element       = mbi,
                        event_jump_element   = 'next',
                        readout_orientation = 'positive')
                gate_seq.extend(probabilistic_MBE_seq)


            carbon_tomo_seq = self.readout_carbon_sequence(
                    prefix              = 'Tomo',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomography Bases'][pt],
                    readout_orientation = self.params['electron_readout_orientation'])
            gate_seq.extend(carbon_tomo_seq)

            gate_seq = self.generate_AWG_elements(gate_seq,pt)

            ### Convert elements to AWG sequence and add to combined list`
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq, explicit=True)
            combined_list_of_elements.extend(list_of_elements)

            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)


            if debug:
                for g in gate_seq:
                    print g.name
                    self.print_carbon_phases(g,self.params['carbon_list'])
        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'

class Two_QB_Det_MBE(MBI_C13):
    '''
    #Sequence
                               --|Tomo A|
    |N-MBI| -|Cinits|-|Parity|
                               --|Tomo B|

    '''
    mprefix = 'Deterministic_MBE_Tomography'
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

            ### Nitrogen MBI
            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]
            gate_seq.extend(mbi_seq)

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

            ### Parity msmt - here deterministic MBE
            Parity_seq = self.readout_carbon_sequence(
                        prefix              = 'Parity' + str(kk+1),
                        pt                  = pt,
                        RO_trigger_duration = 150e-6,
                        carbon_list         = self.params['carbon_list'],
                        RO_basis_list       = self.params['MBE_bases'],
                        el_RO_result         = '0')

            gate_seq.extend(Parity_seq)

            #############################
            gate_seq0 = copy.deepcopy(gate_seq)
            gate_seq1 = copy.deepcopy(gate_seq)

            carbon_tomo_seq0 = self.readout_carbon_sequence(
                    prefix              = 'Tomo0',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomography Bases_0'][pt],
                    readout_orientation = self.params['electron_readout_orientation'],
                    el_state_in         = 0)
            gate_seq0.extend(carbon_tomo_seq0)

            carbon_tomo_seq1 = self.readout_carbon_sequence(
                    prefix              = 'Tomo1',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomography Bases_1'][pt],
                    readout_orientation = self.params['electron_readout_orientation'],
                    el_state_in         = 1)
            gate_seq1.extend(carbon_tomo_seq1)

            # Make jump statements for branching to two different ROs
            Parity_seq[-1].go_to       = carbon_tomo_seq0[0].name
            Parity_seq[-1].event_jump  = carbon_tomo_seq1[0].name

            # In the end all roads lead to Rome
            Rome = Gate('Rome_'+str(pt),'passive_elt',
                    wait_time = 3e-6)
            gate_seq1.append(Rome)
            gate_seq0[-1].go_to     = gate_seq1[-1].name

            ################################################################
            ### Generate the AWG_elements, including all the phase gates for all branches###
            ################################################################

            gate_seq  = self.generate_AWG_elements(gate_seq,pt)

            print 'generating elements for seq 0'
            gate_seq0[len(gate_seq)-2].el_state_before_gate = '0' #Element -2, because MBI was added in generate AWG elements
            gate_seq0 = self.generate_AWG_elements(gate_seq0,pt)
            # print 'generating elements for seq 01'
            print 'This is the element that we change the electron for'
            print gate_seq0[len(gate_seq)-2].name
            print gate_seq[len(gate_seq)-2].name
            print 'generating elements for seq 1'
            gate_seq1[len(gate_seq)-2].el_state_before_gate = '1' #Element -2, because MBI was added in generate AWG elements
            gate_seq1 = self.generate_AWG_elements(gate_seq1,pt)

            # Merge the bracnhes into one AWG sequence
            merged_sequence = []
            merged_sequence.extend(gate_seq)                  #TODO: remove gate_seq and add gate_seq1 to gate_seq0 without common part
            merged_sequence.extend(gate_seq0[len(gate_seq):])
            merged_sequence.extend(gate_seq1[len(gate_seq):])

            print '*'*10
            print 'seq_merged'
            for g in merged_sequence:
                print g.name
                if debug and hasattr(g,'el_state_before_gate'):# != None:
                    # print g.el_state_before_gate
                    print 'el state before and after (%s,%s)'%(g.el_state_before_gate, g.el_state_after_gate)
                elif debug:
                    print 'does not have attribute el_state_before_gate'

                self.print_carbon_phases(g,self.params['carbon_list'])

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

### Composite gates AS 11092015 ###

class Sweep_Carbon_Gate_COMP(MBI_C13):
    """
    Performs MBI on a carbon and allows for varying gate parameters.
    """

    mprefix = 'Sweep_carbon_Gate'
    adwin_process = 'MBI_multiple_C13'

    def generate_sequence(self, upload=True, debug=False):
        pts = self.params['pts']

        ### initialize empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('SweepCarbonInit')

        for pt in range(pts): ### Sweep over RO basis
            gate_seq = []

            ### Nitrogen MBI
            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]; gate_seq.extend(mbi_seq)

            ### Carbon initialization
            init_wait_for_trigger = True
            
            for kk in range(self.params['Nr_C13_init']):
                print self.params['init_method_list'][kk]
                print self.params['init_state_list'][kk]
                print self.params['carbon_init_list'][kk]
                print self.params['sweep_pts'][pt]
                

                carbon_init_seq = self.initialize_carbon_sequence_COMP(go_to_element = mbi,
                    prefix = 'C_MBI' + str(kk+1) + '_C',
                    wait_for_trigger      = init_wait_for_trigger, pt =pt,
                    initialization_method = self.params['init_method_list'][kk],
                    C_init_state          = self.params['init_state_list'][kk],
                    addressed_carbon      = self.params['carbon_init_list'][kk],
                    el_after_init         = self.params['el_after_init'])
                gate_seq.extend(carbon_init_seq)
                init_wait_for_trigger = False



            carbon_tomo_seq = self.readout_carbon_sequence_COMP(
                    prefix              = 'Tomo',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomography Bases'][pt],
                    el_state_in         = int(self.params['el_after_init']),
                    readout_orientation = self.params['electron_readout_orientation'])            


            gate_seq.extend(carbon_tomo_seq)

            gate_seq = self.generate_AWG_elements(gate_seq,pt)

            ### Convert elements to AWG sequence and add to combined list`
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq, explicit=True)
            combined_list_of_elements.extend(list_of_elements)

            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)

            if not debug:
                print '*'*10
                for g in gate_seq:
                    print g.name

            # if debug:
                # for g in gate_seq:
                #     print g.name

                    

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG' 