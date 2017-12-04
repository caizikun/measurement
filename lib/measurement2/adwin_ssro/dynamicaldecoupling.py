'''
Measurement classes
File made by Adriaan Rol
Edited by THT
'''
import numpy as np
from scipy.special import erfinv
import qt
import copy
from measurement.lib.pulsar import pulse, pulselib, element, pulsar
reload(pulsar)
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
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
        special gates: 'mbi', 'Trigger'
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

        self.specific_transition = kw.pop('specific_transition',None) # used to specify the mw transition 
        self.fixed_dec_duration = kw.pop('fixed_dec_duration',False)
        self.t                  = kw.pop('t',None)
        self.t_rep               = kw.pop('t_rep',1)

        self.second_pi_phase    = kw.pop('second_pi_phase',102.8) # parameter for the transfer gate
        self.delay              =kw.pop('delay',230e-9) # parameter for the transfer gate
  

        self.wait_time  = kw.pop('wait_time',None)
        self.reps = kw.pop('reps',1) # only overwritten in case of Carbon decoupling elements or RF elements
        self.dec_duration = kw.pop('dec_duration', None)  # can be specified if a custom dec duration is desired

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
                       Currently possible channel names: 'AOM_newfocus'
        If there are any attributes being used frequently that are still missing here please add them for documentation
        '''

class DynamicalDecoupling(pulsar_msmt.MBI):

    '''
    This is a general class for decoupling gate sequences used in addressing Carbon -13 atoms. It contains functions needed for generating the pulse sequences for the AWG.
    It makes extensive use of the Gate class also found in this file.
    It is a child of PulsarMeasurment.MBI
    '''
    mprefix = 'DecouplingSequence'

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
        Takes a gate object as input and uses the carbon index and the operation to
        determine tau and N from the msmt params
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
                gate.N = self.params['C'+str(ind)+'_Ren_N'+self.params['electron_transition']][resonance]
            if gate.tau==None:
                gate.tau = self.params['C'+str(ind)+'_Ren_tau'+self.params['electron_transition']][resonance]
            
        if gate.comp==True:
            if gate.N==None:
                gate.N = self.params['C'+str(ind)+'_Ren_N2'+self.params['electron_transition']][resonance]
            if gate.tau==None:
                gate.tau = self.params['C'+str(ind)+'_Ren_tau2'+self.params['electron_transition']][resonance]


    def find_gate_index(self,name,gate_seq):
        '''
        Returns index of gate with gate.name == name in gate sequence
        '''
        for i, gate in enumerate(gate_seq):
            if gate.name == name:
                return i
        print 'Name (%s )  not found in gate sequence' %name
        return

    def insert_transfer_gates(self,gate_seq,pt=0):
        ext_gate_seq = [] # this is the list that also contains the trasnfer elements
        gates_in_need_of_transfer_elts = ['Carbon_Gate','electron_decoupling','passive_elt','RF_pulse','electron_Gate']

        for i in range(len(gate_seq)-1):
            
            ext_gate_seq.append(gate_seq[i])
            if ((gate_seq[i].Gate_type in gates_in_need_of_transfer_elts) and
                    (gate_seq[i+1].Gate_type in gates_in_need_of_transfer_elts)):
                if (gate_seq[i].specific_transition != gate_seq[i+1].specific_transition) and (gate_seq[i+1].el_state_before_gate == 'sup'):
                    if not ((gate_seq[i+1].Gate_operation== 'pi') and ((gate_seq[i+2].Gate_type =='Trigger') or gate_seq[i+2].Gate_operation=='pi2')):
                        if ~(gate_seq[i+1].name[0:4] !='Tomo' and  gate_seq[i+1].name[5] != gate_seq[i].name[5]):              
                            print 'These gates need a connection element in transition:%s and %s'%(gate_seq[i].name,gate_seq[i+1].name)
                            ext_gate_seq.append(Gate('Transfer_gate'+ gate_seq[i+1].name + str(i)+'_'+str(pt),'Transfer_element',
                                specific_transition=gate_seq[i+1].specific_transition
                                ))

        
        ext_gate_seq.append(gate_seq[-1])
        gate_seq = ext_gate_seq
        return gate_seq   
        

    def insert_phase_gates(self,gate_seq,pt=0):
        ext_gate_seq = [] # this is the list that also contains the connection elements
        gates_in_need_of_connecting_elts1 = ['Carbon_Gate','electron_decoupling','passive_elt','RF_pulse']
        gates_in_need_of_connecting_elts2 = ['Carbon_Gate','electron_decoupling']

        #TODO_MAR: Insert a different type of phase gate in the case of a passive element.
        #TODO_THT: What  does this mean??? Clearly it does not work...

        for i in range(len(gate_seq)-1):
            ext_gate_seq.append(gate_seq[i])
            if ((gate_seq[i].Gate_type in gates_in_need_of_connecting_elts1) and
                    (gate_seq[i+1].Gate_type in gates_in_need_of_connecting_elts1)):

                ext_gate_seq.append(Gate('phase_gate_'+ gate_seq[i+1].name + str(i)+'_'+str(pt),'Connection_element',specific_transition=gate_seq[i+1].specific_transition))
            
            if gate_seq[i].Gate_type =='Trigger' :
                if (gate_seq[i+1].Gate_type in gates_in_need_of_connecting_elts2):
                    ext_gate_seq.append(Gate('phase_gate_' + gate_seq[i+1].name+str(i)+'_'+str(pt),'Connection_element',specific_transition=gate_seq[i+1].specific_transition))

            # if gate_seq[i].Gate_type =='Transfer_element' and (gate_seq[i+1].Gate_type in gates_in_need_of_connecting_elts1):
            #         ext_gate_seq.append(Gate('phase_gate_' + gate_seq[i+1].name+str(i)+'_'+str(pt),'Connection_element',specific_transition=gate_seq[i+1].specific_transition))
        
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
        #print 'Is this happening at all for:',g.name,g.dec_duration
        #print 'this is what i have',g.name,g.dec_duration,g.N,g.tau

        if g.dec_duration == 0:
            g.N = 0
            g.tau = 0
            return
            #make sure thate electron pulses where the electron is in a eigenstate do not get decoupled
        
        elif (g.el_state_before_gate in ['0','1']):
            #print'For these gates N and tau are 0',g.name
            g.N = 0
            g.tau = 0
            
            return

        elif (g.dec_duration + g.tau_cut_after+g.tau_cut_before)<1e-6:
            print 'Error: connection element (%s )decoupling duration is too short g.dec_duration = %s, tau_cut_before = %s, tau_cut after = %s, must be atleast 1us' %(g.name, g.dec_duration,g.tau_cut_before,g.tau_after)
            return
        elif (g.dec_duration/(2*self.params['dec_pulse_multiple']))<self.params['min_dec_tau']:
            print 'Warning: connection element decoupling duration is too short. Not decoupling in time interval. \n dec_duration = %s, min dec_duration = %s' %(g.dec_duration,2*self.params['min_dec_tau']*self.params['dec_pulse_multiple'])
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
                # print 'found the following decoupling tau: %s, N: %s' %(tau,g.N),2*tau*g.N,g.dec_duration
                break
            elif k == 39 and tau>self.params['max_dec_tau']:
                print 'Error: decoupling duration (%s) to large, for %s pulses decoupling tau (%s) larger than max decoupling tau (%s)' %(g.dec_duration,k,tau,self.params['max_dec_tau'])
        
        return g


    def determine_decoupling_scheme(self,Gate):
        '''
        Function used by generate_decoupling_sequence_elements
        Takes the first few lines of code that determine what kind of decoupling scheme is being used and puts it in a  function
        TODO_MAR: Document limitations and advantages of different decoupling schemes (multiples of 4ns?, lots of elements, very long elements)
        AS Added a check for the used mmw transition, which looks up the pulse durations

        '''
        #print 'this gate got sent to determine dec scheme',Gate.name,Gate.dec_duration,Gate.N,Gate.tau
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
        elif Gate.tau<=  pi_pulse_duration+20e-9: ## ERROR? shouldn't this be 1/2*pi_dur + 10?
            print 'Error: Gate(%s), tau (%s) too small: Pulses will overlap! \n Min tau = %s' %(Gate.name,Gate.tau,self.params['fast_pi_duration']+20e-9)
            return
        elif Gate.tau< 0.5e-6 :
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

        #print 'im loading the parameters for this transition:',self.params['electron_transition']
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
        loads extra phase corrections that are not covered by the3 precession frquency
        '''

        Gate.LDE_phase_correction_list = self.params['Carbon_LDE_phase_correction_list']/180.*np.pi
        Gate.LDE_init_phase_correction_list = self.params['Carbon_LDE_init_phase_correction_list']/180.*np.pi

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
                    
                    elif g_b.Gate_type == 'Transfer_element':
                        g_b.tau_cut_after = g.tau_cut_before
                        break 

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

                    elif g_b.Gate_type == 'Transfer_element':
                        g_b.tau_cut_before = g.tau_cut_after
                        break

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
            # if g.Gate_type == 'Transfer_element':
            #     if Gate_sequence[i+1].Gate_type == 'Connection_element':
            #         Gate_sequence[i+1].tau_cut_before= 0.5e-6
            #         g.tau_cut_after = 0.5e-6

        return Gate_sequence

    def track_and_calc_phase(self,Gate_sequence):
        '''
        This function keeps track of phases in a Gate sequence.
        It differs from the version in the parent class DynamicalDecoupling in that it
        tracks the evolved phase per gate based on the electron state.
        This allows for mid gate changing of precession frequency.
        It requires three variables in the msmt params to be stored for each carbon
        C*_freq_0, C*_freq_1, C*_freq. where *is a carbon index (1,2 etc).

        The following attributes are added to each gate
        C_phases_after_gate [phase_C1, phase_C2, ... ]
        el_state_after_gate:  Possibilities are '0', '1' and 'sup' ('sup is for superposition, a misnomer for dynamical decoupling).
        NOTE: 'sup'  is currently not actively used could be removed from code but label is useful to make things explicit.
        el_state_before_gate

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
        # if ~self.params['multiple_source']==True:
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


            if i!= 0:
                g.C_phases_before_gate = Gate_sequence[i-1].C_phases_after_gate

                 ### MW pi/2 pulses need special attention for tracking the electron state.
            if g.el_state_before_gate in ['0','1'] and g.Gate_operation == 'pi2':
                g.el_state_after_gate = 'sup' ### this signifies the begin of a decoupling sequence.
            
            # if g.el_state_before_gate in ['sup'] and g.Gate_operation == 'pi2':
            #     g.el_state_after_gate = ['0'] ### this signifies the begin of a decoupling sequence.       
     
            ### we also care about the electron state if we apply pi pulses.
            if g.el_state_before_gate in ['0','1'] and g.Gate_operation == 'pi':


                if g.el_state_before_gate == '0':
                    g.el_state_after_gate = '1'

                else:
                    g.el_state_after_gate = '0'
            

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
                # print 'I am connection with el in',g.name,g.el_state_before_gate,g.specific_transition,g.dec_duration
                
                if i == len(Gate_sequence)-1:
                    g.dec_duration = 0
                elif Gate_sequence[i+1].phase == None or Gate_sequence[i+1].phase == 'reset':
                    if g.dec_duration !=  None:
                        pass# print 'i am passing',g.name,g.dec_duration
                    else:
                        g.dec_duration =0
                else:
                    desired_phase = Gate_sequence[i+1].phase/180.*np.pi
                    Carbon_index  = Gate_sequence[i+1].Carbon_ind
                    # print 'I want this phase for this carbon',g.name,desired_phase,Carbon_index

                    if g.C_phases_before_gate[Carbon_index] == None:

                        g.dec_duration = 0

                    else:
                        phase_diff =(desired_phase - g.C_phases_before_gate[Carbon_index])%(2*np.pi)

                        # print 'I want this phase for this carbon',desired_phase,Carbon_index
                        # print 'Phase_difference: ',phase_diff,g.name

                        if ( (phase_diff <= (self.params['min_phase_correct']/180.*np.pi)) or
                                (abs(phase_diff -2*np.pi) <=  (self.params['min_phase_correct']/180.*np.pi)) ):
                        # For very small phase differences correcting phase with decoupling introduces a larger error
                        #  than the phase difference error.

                            g.dec_duration = 0
                        else:                                    
                            self.params['electron_transition_used']=self.params['C'+str(Carbon_index)+'_dec_trans']
                            self.params['electron_transition']=self.params['electron_transition_used']
                            #print
                            #print 'for this gate i have chosen this transition based on Carb ind',g.name,g.specific_transition,g.el_state_before_gate,g.el_state_after_gate
                            #print
                            C_freq_0, C_freq_1, C_freq = self.load_C_freqs_in_radians_sec()
                            ### check if the electron is in an eigenstate before the phase gate
                            if g.el_state_before_gate in ['0','1']:
                                if g.el_state_before_gate == '0':
                                    g.dec_duration = round(phase_diff/C_freq_0[Carbon_index]*1e9)*1e-9
                                    # print 'i calculated the dec duration', g.dec_duration*1e6,g.name
                                else:
                                    g.dec_duration = round(phase_diff/C_freq_1[Carbon_index]*1e9)*1e-9

                            g.dec_duration =(round( phase_diff/C_freq[Carbon_index]
                                    *1e9/(self.params['dec_pulse_multiple']*2))
                                    *(self.params['dec_pulse_multiple']*2)*1e-9)
                            
                            while g.dec_duration <= self.params['min_dec_duration']:
                                phase_diff = phase_diff +2*np.pi
                                g.dec_duration =(round( phase_diff/C_freq[Carbon_index]
                                        *1e9/(self.params['dec_pulse_multiple']*2))
                                        *(self.params['dec_pulse_multiple']*2)*1e-9)
                            g.dec_duration = g.dec_duration
                            
                # print 'phases before ',g.C_phases_before_gate                
                for iC in range(len(g.C_phases_before_gate)):
                    if (g.C_phases_after_gate[iC] == None) and (g.C_phases_before_gate[iC] !=None):
                        #print 'iC',iC
                        if g.el_state_before_gate == '0':
                            g.C_phases_after_gate[iC] = (g.C_phases_before_gate[iC]+ g.dec_duration*C_freq_0[iC])%(2*np.pi)
                        elif g.el_state_before_gate == '1':
                            g.C_phases_after_gate[iC] = (g.C_phases_before_gate[iC]+ g.dec_duration*C_freq_1[iC])%(2*np.pi)
                        else:
                            g.C_phases_after_gate[iC] = (g.C_phases_before_gate[iC]+ g.dec_duration*C_freq[iC])%(2*np.pi)
                    # print 'So im adding this decoupling duration: ',g.name,g.dec_duration,Carbon_index,g.C_phases_after_gate[Carbon_index]
            #########
            # Special elements
            #########

            elif g.Gate_type =='passive_elt' or g.Gate_type =='RF_pulse': #MB: added RF pulse temporary, now RF pulses cant be phase tracked
                
                for iC in range(len(g.C_phases_before_gate)):
                    if (g.C_phases_after_gate[iC] == None) and (g.C_phases_before_gate[iC] !=None):
                        #print 'I am passive with el in',g.name,g.el_state_before_gate,g.specific_transition
                        if g.el_state_before_gate == '0':
                            #print 'Calculating phase for gate %s for el_state == 0' %g.name
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
                        if g.el_state_before_gate == '0':
                            #print 'Calculating phase for gate %s for el_state == 0 ' %g.name
                            g.C_phases_after_gate[iC] = (g.C_phases_before_gate[iC] + g.elements_duration*C_freq_0[iC])%(2*np.pi)
                        elif g.el_state_before_gate == '1':
                            #print 'Calculating phase for gate %s for el_state == 1 ' %g.name
                            g.C_phases_after_gate[iC] = (g.C_phases_before_gate[iC] + g.elements_duration*C_freq_1[iC])%(2*np.pi)
                        elif g.el_state_before_gate == 'sup':
                            g.C_phases_before_gate[iC]%(2*np.pi)
                            print 'Warning: %s, el state in sup for Trigger elt' %g.name

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

                # print g.repump_duration,g.t_rep,g.reps,g.t
                for iC in range(len(g.C_phases_before_gate)):
                    if g.C_phases_before_gate[iC] != None:
                        # print "repump_duration {:.2}, t {:.2}, duration_initial {:.2}, t_rep {:.2}, AOM_delay {:.2}".format(g.repump_duration,g.t,g.duration_initial,g.t_rep,g.AOM_delay) 
                        g.C_phases_after_gate[iC] = (g.LDE_init_phase_correction_list[iC] + g.LDE_phase_correction_list[iC]*g.reps + g.C_phases_before_gate[iC] + (g.duration_initial+g.repump_duration-2e-9-g.t_rep-(g.AOM_delay-g.MW_delay))*g.reps*C_freq_0[iC]+g.reps*(C_freq_0[iC]+C_freq_1[iC])*g.t)%(2*np.pi)
                # print 'phase before LDE ', g.C_phases_before_gate
                # print 'phase after LDE ', g.C_phases_after_gate                    


            else: # I want the program to spit out an error if I messed up i.e. forgot a gate type
                print 'Error: %s, Gate type not recognized %s' %(g.name,g.Gate_type)
            # print g.name,g.C_phases_before_gate[1],g.C_phases_after_gate[1]
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
        ###TEST to see if we could find a more elegant way to implement lone decoupling sequences###
        # if Gate.N== None and Gate.tau == None:
        #     print 'I am going to use determine con el param now',Gate.name 
        #     self.determine_connection_element_parameters(Gate)

        #TODO_THT: for single elements add that if multiple of 2 the last pulses are XX instead of XY
        tau       = Gate.tau
        N         = Gate.N
        Gate.reps = N # Overwrites reps parameter that is used in sequencing
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

        # if self.params['pulse_shape'] = 'Hermite':
        #     self.params['Hermite_fast_pi_duration'] = self.params['Hermite_fast_pi_duration']
        # print 'I have this scheme',Gate.name,Gate.scheme
        ### Select scheme for generating decoupling elements
        if N== 0 or Gate.scheme =='auto':
            Gate = self.determine_decoupling_scheme(Gate)

        ### if it encounters a electron decoupling gate for a certain duration it needs to know the N and tau

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
            elif self.params['Initial_Pulse'] =='y':  #######
                initial_phase = self.params['Y_phase']
            elif self.params['Initial_Pulse'] =='-y':  #######
                initial_phase = self.params['Y_phase']+180
            else:
                initial_phase = self.params['X_phase']

            if self.params['Final_Pulse'] =='-x':
                final_phase   = self.params['X_phase']+180
            elif self.params['Final_Pulse'] =='y':  #######
                final_phase = self.params['Y_phase']
            elif self.params['Final_Pulse'] =='-y':  #######
                 final_phase = self.params['Y_phase']+180

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

            # initial_pulse = pulselib.MW_IQmod_pulse('electron Pi/2-pulse',
            #     I_channel   ='MW_Imod', Q_channel='MW_Qmod',
            #     PM_channel  ='MW_pulsemod', Sw_channel=self.params['MW_switch_channel'],
            #     frequency   = self.params['fast_pi2_mod_frq'],
            #     PM_risetime = self.params['MW_pulse_mod_risetime'],
            #     Sw_risetime = self.params['MW_switch_risetime'],
            #     length      = self.params['fast_pi2_duration'], # previously: self.params['fast_R_pi2_duration'], changed by NK 20150310
            #     amplitude   = self.params['fast_pi2_amp'],
            #     phase       = initial_phase)
            # final_pulse = pulselib.MW_IQmod_pulse('electron Pi/2-pulse',
            #     I_channel   ='MW_Imod', Q_channel='MW_Qmod',
            #     PM_channel  ='MW_pulsemod', Sw_channel=self.params['MW_switch_channel'],
            #     frequency   = self.params['fast_pi2_mod_frq'],
            #     PM_risetime = self.params['MW_pulse_mod_risetime'],
            #     Sw_risetime = self.params['MW_switch_risetime'],
            #     length      = self.params['fast_pi2_duration'],
            #     amplitude   = self.params['fast_pi2_amp'],
            #     phase       = final_phase)
            # initial_pulse = self._pi2_elt()
            # final_pulse = self._mpi2_elt()

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
            
            # print 'using single block repeating elements'


            tau_cut = 1e-6

            if self.params['Initial_Pulse'] =='-x':
                initial_phase = self.params['X_phase']+180
            elif self.params['Initial_Pulse'] =='y':  #######
                initial_phase = self.params['Y_phase']
            elif self.params['Initial_Pulse'] =='-y':  #######
                initial_phase = self.params['Y_phase']+180
            else:
                initial_phase = self.params['X_phase']

            if self.params['Final_Pulse'] =='-x':
                final_phase   = self.params['X_phase']+180
            elif self.params['Final_Pulse'] =='y':  #######
                final_phase = self.params['Y_phase']
            elif self.params['Final_Pulse'] =='-y':  #######
                 final_phase = self.params['Y_phase']+180

            else:
                final_phase = self.params['X_phase']

            pulse_tau_pi2 = tau - self.params['fast_pi2_duration']/2.0-self.params['fast_pi_duration']/2.0
            print 'not', int(1e9*self.params['fast_pi_duration']/2.0)
            print 'floor', int(np.floor(self.params['fast_pi_duration']*1e9/2.0))
            if pulse_tau_pi2 < 31e-9:
                print 'tau too short !!!, tau = ' +str(tau) +'min tau = ' +str(self.params['fast_pi2_duration']/2.0-self.params['fast_pi_duration']/2.0+30e-9)

            if self.params['Initial_Pulse'] == '-x':
                initial_pulse = self._mpi2_elt()
            elif self.params['Initial_Pulse'] == '-y':
                initial_pulse = self._mYpi2_elt()
            elif self.params['Initial_Pulse'] == 'y':
                initial_pulse = self._mpi2_elt()
            else:
                initial_pulse = self._pi2_elt()

            if self.params['Final_Pulse'] == '-x':
                final_pulse = self._mpi2_elt()
            else:
                final_pulse = self._pi2_elt()
            # initial_pulse = pulselib.MW_IQmod_pulse('electron Pi/2-pulse',
            #     I_channel   ='MW_Imod', Q_channel='MW_Qmod',
            #     PM_channel  ='MW_pulsemod', Sw_channel=self.params['MW_switch_channel'],
            #     frequency   = self.params['fast_pi2_mod_frq'],
            #     PM_risetime = self.params['MW_pulse_mod_risetime'],
            #     Sw_risetime = self.params['MW_switch_risetime'],
            #     length      = self.params['fast_pi2_duration'], # previously: self.params['fast_R_pi2_duration'], changed by NK 20150310
            #     amplitude   = self.params['fast_pi2_amp'],
            #     phase       =initial_phase)
            # final_pulse = pulselib.MW_IQmod_pulse('electron Pi/2-pulse',
            #     I_channel   ='MW_Imod', Q_channel='MW_Qmod',
            #     PM_channel  ='MW_pulsemod', Sw_channel=self.params['MW_switch_channel'],
            #     frequency   = self.params['fast_pi2_mod_frq'],
            #     PM_risetime = self.params['MW_pulse_mod_risetime'],
            #     Sw_risetime = self.params['MW_switch_risetime'],
            #     length      = self.params['fast_pi2_duration'],
            #     amplitude   = self.params['fast_pi2_amp'],
            #     phase       = final_phase)
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

            if 'start' in Gate.scheme or 'end' in Gate.scheme:
                print 'THIS IS THE TIME', (16*tau + 5e-6) % 4
            else:
                print 'THIS IS THE TIME', 16*tau
            ### finish off with a pi/2 pulse.
            if 'end' in Gate.scheme: 
                decoupling_elt.append(T_around_pi2)
                decoupling_elt.append(pulse.cp(final_pulse))
                decoupling_elt.append(T_out)

            list_of_elements.append(decoupling_elt)
        ################################
        ### XYn with repeating T elt ###
        ################################
        elif Gate.scheme == 'repeating_T_elt':
            ### Calculate durations
            
            n_wait_reps, tau_remaind = divmod(round(2*pulse_tau*1e9),1e3) #multiplying and round is to prevent rounding errors in divmod
            tau_remaind              = tau_remaind*1e-9
            #print 'pulse_tau in us = ',  pulse_tau*1e6
            #print 'n_wait_reps = ', n_wait_reps


            if tau_remaind/2. < X.risetime: ## The tau_remaind calculation now depends on the overall risetime of the pulse. NK 20150323
            # NOTE: with MW switch (risetime = 500 ns) pulse_tau must be longer than (2.5 + fast_pi_duration/2) us, otherwise: n_wait_reps = 4 - 4 = 0 --> red_wait_reps = 0 --> AWG cannot program 0 element repetitions
                ''' to make sure that the time before the pulse is not shorther than the pulse mod'''
                n_wait_reps              = n_wait_reps -4
                tau_shortened            = tau_remaind/2.0 + 1e-6
                t_around_pulse           = 2e-6 + tau_remaind/2.0
            else:
                n_wait_reps              = n_wait_reps -4
                tau_shortened            = tau_remaind/2.0+1e-6
                t_around_pulse           = 2e-6 + tau_remaind/2.0


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


            #             if tau_remaind/2. < X.risetime: ## The tau_remaind calculation now depends on the overall risetime of the pulse. NK 20150323
            # # NOTE: with MW switch (risetime = 500 ns) pulse_tau must be longer than (2.5 + fast_pi_duration/2) us, otherwise: n_wait_reps = 4 - 4 = 0 --> red_wait_reps = 0 --> AWG cannot program 0 element repetitions
            #     ''' to make sure that the time before the pulse is not shorther than the pulse mod'''
            #     n_wait_reps              = n_wait_reps -14
            #     tau_shortened            = tau_remaind/2.0 + 4e-6
            #     t_around_pulse           = 7e-6 + tau_remaind/2.0
            # else:
            #     n_wait_reps              = n_wait_reps -14
            #     tau_shortened            = tau_remaind/2.0+4e-6
            #     t_around_pulse           = 7e-6 + tau_remaind/2.0


            # Tus =pulse.SquarePulse(channel='MW_Imod', name='Wait: tau',
            #     length = 1e-6, amplitude = 0.)
            # T = pulse.SquarePulse(channel='MW_Imod', name='Wait: tau',
            #     length = t_around_pulse, amplitude = 0.)
            # T_shortened = pulse.SquarePulse(channel='MW_Imod', name='delay',
            #     length = tau_shortened, amplitude = 0.)

            # ### Correct for part that is cut off when combining to sequence
            # if n_wait_reps %2 == 0:
            #     tau_cut = 3e-6
            # else:
            #     tau_cut = 3.5e-6

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

            ## trial stimulated echo ##
            final_pulse=X
            ####

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
                n_wait_reps              = n_wait_reps -4
                tau_shortened            = tau_remaind/2.0 +1e-6
                t_around_pulse           = 2e-6 + tau_remaind/2.0


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
            T = pulse.SquarePulse(channel='MW_Imod', name='Wait: tau',
                length = 1e-6, amplitude = 0.)
            wait = element.Element('%s_NO_Pulse' %(prefix),  pulsar=qt.pulsar,
                    global_time = True)
            wait.append(T)
            list_of_elements.append(wait)

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

        #print 'This is the gate index i have',Gate.prefix,Gate.Carbon_ind
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



        tau_prnt= int(tau*1e9)
        tau_cut_before  = Gate.tau_cut_before
        tau_cut_after   = Gate.tau_cut_after

        if tau_cut_before != tau_cut_after:
            print 'The tau cuts of the transfer gate are not equal!!!'
        # print 'these are the tau cuts for these gates',Gate.name,tau_cut_before,tau_cut_after,Gate.dec_duration

        ### the NV is in an eigenstate before we apply the phase gate add this time as additional waiting.
        if N == 0 and Gate.dec_duration != 0 and Gate.el_state_before_gate in ['0','1']:
            tau_cut_before += Gate.dec_duration
        
        pulse_tau       = tau-self.params['fast_pi_duration']/2.0

        X = self._X_elt()
        Y = self._Y_elt()
        mX = self._mX_elt()
        mY = self._mY_elt()


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
        
        elif Gate.Gate_type == 'Connection_element':
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

        Gate.delay = self.params['delay']
        
        tau_cut_before  = Gate.tau_cut_before
        tau_cut_after   = Gate.tau_cut_after
          
        T_start = pulse.SquarePulse(channel='MW_Imod', name='Wait befor 1st pulse',
            length =3*Gate.delay-first_mw_duration/2-tau_cut_before+1e-6, amplitude = 0.)

        T_first = pulse.SquarePulse(channel='MW_Imod', name='wait after 1st pulse',
            length = Gate.delay -(first_mw_duration/2+second_mw_duration/2), amplitude = 0.)

        T_second = pulse.SquarePulse(channel='MW_Imod', name='wait after 2nd pulse',
            length = Gate.delay -(first_mw_duration/2+second_mw_duration/2), amplitude = 0.)

        T_third = pulse.SquarePulse(channel='MW_Imod', name='wait after 3rd pulse',
            length = Gate.delay -(first_mw_duration/2+second_mw_duration/2), amplitude = 0.)

        T_fourth = pulse.SquarePulse(channel='MW_Imod', name='wait after 4th pulse',
            length = 2*Gate.delay -(first_mw_duration/2+first_mw_duration/2), amplitude = 0.)

        T_fifth = pulse.SquarePulse(channel='MW_Imod', name='wait after 5th pulse',
            length = 1*Gate.delay -(second_mw_duration/2)-tau_cut_after+1e-6, amplitude = 0.)

       

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
        time_after_pulse = Gate.time_after_pulse
        Gate_operation = Gate.Gate_operation
        prefix = Gate.prefix

        if Gate_operation == 'x':
            time_before_pulse = time_before_pulse  -self.params['fast_pi2_duration']/2.0
            time_after_pulse = time_after_pulse  -self.params['fast_pi2_duration']/2.0

            # X = pulselib.MW_IQmod_pulse('electron Pi/2-pulse',
            #     I_channel='MW_Imod', Q_channel='MW_Qmod',
            #     PM_channel='MW_pulsemod', Sw_channel=self.params['MW_switch_channel'],
            #     frequency = self.params['fast_pi2_mod_frq'],
            #     PM_risetime = self.params['MW_pulse_mod_risetime'],
            #     Sw_risetime = self.params['MW_switch_risetime'],
            #     length = self.params['fast_pi2_duration'],
            #     amplitude = self.params['fast_pi2_amp'],
            #     phase=self.params['X_phase'])
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
            # X = pulselib.MW_IQmod_pulse('electron Pi/2-pulse',
            #     I_channel='MW_Imod', Q_channel='MW_Qmod',
            #     PM_channel='MW_pulsemod', Sw_channel=self.params['MW_switch_channel'],
            #     frequency = self.params['fast_pi2_mod_frq'],
            #     PM_risetime = self.params['MW_pulse_mod_risetime'],
            #     Sw_risetime = self.params['MW_switch_risetime'],
            #     length = self.params['fast_pi2_duration'],
            #     amplitude = self.params['fast_pi2_amp'],
            #     phase = self.params['X_phase']+180)
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

            # X = pulselib.MW_IQmod_pulse('electron Pi-pulse',
            #     I_channel='MW_Imod', Q_channel='MW_Qmod',
            #     PM_channel='MW_pulsemod', Sw_channel=self.params['MW_switch_channel'],
            #     frequency = self.params['fast_pi_mod_frq'],
            #     PM_risetime = self.params['MW_pulse_mod_risetime'],
            #     Sw_risetime = self.params['MW_switch_risetime'],
            #     length = self.params['fast_pi_duration'],
            #     amplitude = self.params['fast_pi_amp'])
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

            # X = pulselib.MW_IQmod_pulse('electron Pi/2-pulse',
            #     I_channel='MW_Imod', Q_channel='MW_Qmod',
            #     PM_channel='MW_pulsemod', Sw_channel=self.params['MW_switch_channel'],
            #     frequency = self.params['fast_pi2_mod_frq'],
            #     PM_risetime = self.params['MW_pulse_mod_risetime'],
            #     Sw_risetime = self.params['MW_switch_risetime'],
            #     length = self.params['fast_pi2_duration'],
            #     amplitude = self.params['fast_pi2_amp'],
            #     phase = self.params['Y_phase'])
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

            # X = pulselib.MW_IQmod_pulse('electron Pi/2-pulse',
            #     I_channel='MW_Imod', Q_channel='MW_Qmod',
            #     PM_channel='MW_pulsemod', Sw_channel=self.params['MW_switch_channel'],
            #     frequency = self.params['fast_pi2_mod_frq'],
            #     PM_risetime = self.params['MW_pulse_mod_risetime'],
            #     Sw_risetime = self.params['MW_switch_risetime'],
            #     length = self.params['fast_pi2_duration'],
            #     amplitude = self.params['fast_pi2_amp'],
            #     phase = self.params['Y_phase']+180)
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

    def generate_electron_repump_element(self,Gate):
        '''
        Generate a laser pulse on the marker channel for the newfocus_AOM
        this additionally adds a dead time afterwards for the AOM delay.
        Requires Gate to have the following attributes:
        Gate_type, duration
        NOTE: Power needs to be assigned in the sequence. For an example, see NuclearT1_repumping
        '''

        Gate_type = Gate.Gate_type
        duration= Gate.duration

        repump_pulse=pulse.SquarePulse(channel='AOM_Newfocus', length=duration-qt.pulsar.channels['AOM_Newfocus']['delay'], name='electron_repump', amplitude=1.)
        AOM_delay=pulse.SquarePulse(channel='AOM_Newfocus', length=qt.pulsar.channels['AOM_Newfocus']['delay'], name='wait_AOM_delay', amplitude=0.)

        e = element.Element('%s_electron_repump' %(Gate_type),  pulsar=qt.pulsar, global_time = True)
        e.append(repump_pulse)
        e.append(AOM_delay)

        Gate.elements=[e]

        #qt.pulsar.define_channel(id='ch2_marker1', name='AOM_Newfocus', type='marker',
        #high=0.4, low=0.0, offset=0., delay=466e-9, active=True)

        #TODO for other functions in the DD class:
        # - figure out what DELAY actually does when configuring the sequence for the AWG!!
        # - add this gate type in track_and_calc_phase such that the phase get's accurately detected.
        # - add calculation for the repump power and put it into the generation of the marker trigger.

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
        Optical pi pulses are implemented as dirty hack AR 12-15
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
        
        

        # ###Determine pulses for the different mw sources###
        # if self.params['do_elec_transfer']:
        #     if Gate.specific_transition == self.params['mw1_transition']:
        #         first_pi = ps.mw2_X_elt(self)                
        #         second_pi = ps.X_pulse(self)

        #     elif Gate.specific_transition==self.params['mw2_transition']:
        #         first_pi = ps.X_pulse(self)
        #         second_pi = ps.mw2_X_pulse(self) 
        #     else:
        #         print 'Please select a valid transition for the transfer pulse to start with'

            

        # pi2 = pulse.cp(pi2,phase = self.params['Y_phase'])

        ### gives the possiblity to sweep the amplitude of this specific pi pulse.
    
        RepumpX = pulse.cp(X, amplitude = Gate.pi_amp)
        epump_duration      = Gate.repump_duration

        ### delay of the MW channel
        Gate.MW_delay = qt.pulsar.channels['MW_Imod']['delay']


        # wait times
        print 'X risetime {}'.format(X.risetime*1e9)
        duration_initial = X.risetime + self.params['fast_pi2_duration']/2 + 300e-9 + Gate.MW_delay ## because MW switch and MW delay and AOM delay. Used to be 35ns
        Gate.duration_initial = duration_initial -  Gate.MW_delay


        # not implemented. See below #XXXXXXX
        duration_final = 2e-9 ### give some space after the laser pulse.
        Gate.duration_final = duration_final

        do_optical_pi_pulses=False #self.params['do_optical_pi']
        do_elec_transfer=self.params['do_elec_transfer']
        if do_optical_pi_pulses:
            T_init =  pulse.SquarePulse(channel='adwin_sync', name='Wait t',
                        length = duration_initial - self.params['fast_pi2_duration']/2, amplitude = 0.)
            T_final =  pulse.SquarePulse(channel='adwin_sync', name='Wait t',
                        length = duration_final, amplitude = 0.)
            T_before_optical =  pulse.SquarePulse(channel='adwin_sync', name='Wait t',
                    length = self.params['optical_pi_AOM_delay'], amplitude = 0.)

        if do_optical_pi_pulses:
            t = t - self.params['optical_pi_AOM_delay'] - self.params['optical_pi_AOM_duration']
        ### Determine pulses for an electron transfer gate ###

        if do_elec_transfer:
            T_init =  pulse.SquarePulse(channel='adwin_sync', name='Wait t',
                        length = 20e-9, amplitude = 0.)

            T =  pulse.SquarePulse(channel='adwin_sync', name='Wait t',
                    length = Gate.delay, amplitude = 0.)
            
            second_pi.phase=Gate.second_pi_phase
        
        ### necessary length definitions if you do a regular pi pulse.
        if Gate.do_pi:
            T =  pulse.SquarePulse(channel='adwin_sync', name='Wait t',
                    length = t-self.params['fast_pi_duration']/2-self.params['fast_pi2_duration']/2, amplitude = 0.)
            
            T_rep = pulse.SquarePulse(channel='adwin_sync',name='Wait t-trep',
                    length = (t-t_rep)-self.params['fast_pi_duration']/2, amplitude = 0.)
        
        ### necessary definitions if you do BB1
        elif Gate.do_BB1:
            T =  pulse.SquarePulse(channel='adwin_sync', name='Wait t',
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
        # #defined on a marker channel, amp has to be 1 in order to switch on.
        # AWG_repump = pulse.SquarePulse(channel = Gate.channel,name = 'repump',
        #     length = repump_duration,amplitude = 1)

        

        # print 'T duration', t-5*self.params['fast_pi_duration']/2-self.params['fast_pi2_duration']/2
        # print 'T_rep duration', (t-t_rep)-5*self.params['fast_pi_duration']/2
        
        #create element
        rep_LDE_elt = element.Element('%s' %(Gate.prefix), pulsar = qt.pulsar, global_time=True)

        rep_LDE_elt.append(T_init)

        if do_optical_pi_pulses:
            if self.params['initial_MW_pulse'] == 'pi2':
                print 'Repumping: Initial pulse is pi2'
                rep_LDE_elt.append(pi2)
            elif self.params['initial_MW_pulse'] == 'pi':
                print 'Repumping: Initial pulse is pi'
                rep_LDE_elt.append(RepumpX)
            
        if do_optical_pi_pulses:

            optical_pi = pulse.SquarePulse(channel = 'AOM_Matisse', 
                    name = 'optical_pi',
                    length = self.params['optical_pi_AOM_duration'], 
                    amplitude = self.params['optical_pi_AOM_amplitude'], 
                    delay = self.params['optical_pi_AOM_delay' ])
            rep_LDE_elt.append(T_before_optical)
            rep_LDE_elt.append(optical_pi)

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
            rep_LDE_elt.append(T_before_optical)
            rep_LDE_elt.append(optical_pi)

        # if  do_elec_transfer:            
        #     rep_LDE_elt.append(first_pi)
        #     rep_LDE_elt.append(T)
        #     rep_LDE_elt.append(second_pi)
        #     Gate.elements_duration = 2*20e-9+Gate.delay+self.params['mw2_fast_pi_duration']+self.params['fast_pi_duration']
 

        Gate.elements =  [rep_LDE_elt]
        Gate.elements_duration = (duration_initial +  2*t-t_rep+repump_duration+duration_final)*Gate.reps


        ### used in phase calculation
        # Gate.AOM_delay = qt.pulsar.channels[Gate.channel]['delay']

        # print 'AOM_delay {}'.format(Gate.AOM_delay)
        print 'the duration of this pulse is',Gate.name,Gate.elements_duration


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
                elif gate.event_jump =='self':
                    gate.elements[0].name
                elif gate.event_jump == 'start' :
                    gate.event_jump = gate_seq[0].elements[0].name
                else:
                    ind = self.find_gate_index(gate.event_jump,gate_seq)
                    gate.event_jump = gate_seq[ind].elements[0].name
            # Debug print statement:
            # print 'Gate %s, \n  %s \n goto %s, \n jump %s' %(gate.name,gate.elements[0].name,gate.go_to,gate.event_jump)

            single_elements_list = ['NO_Pulses','single_block','single_element']
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
                
                list_of_elements.extend(gate.elements)
                e = gate.elements[0]
                seq.append(name=e.name,wfname =e.name,
                            trigger_wait=gate.wait_for_trigger,
                            repetitions=gate.reps,
                            goto_target = gate.go_to,
                            jump_target= gate.event_jump )


            ####################
            ###  single elements  ###
            ####################
            elif gate.scheme in single_elements_list :
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

        for g in Gate_sequence:
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
        Gate_sequence = self.insert_phase_gates(Gate_sequence,pt)
        self.get_tau_cut_for_connecting_elts(Gate_sequence)
        self.track_and_calc_phase(Gate_sequence)
        for g in Gate_sequence:
            if (g.Gate_type == 'Connection_element' or g.Gate_type == 'electron_Gate'):
                self.determine_connection_element_parameters(g)
                self.generate_connection_element(g)
                #print 'I am a %s connection element: on this carbon %d' %g.Gate_type%g.Carbon_ind,g.name

        for g in Gate_sequence:
            if (g.Gate_type == 'Transfer_element'):
                self.generate_transfer_element(g)

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
                    Carbon_ind =self.params['addressed_carbon'],
                    phase = None)
            Rz = Gate('Rz_'+str(pt),'Connection_element',
                    dec_duration = self.params['free_evolution_times'][pt])
            Ren_b = Gate('Ren_b'+str(pt), 'Carbon_Gate',
                    Carbon_ind =self.params['addressed_carbon'],
                    phase = None)
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

            # if debug:
            #     print '*'*10
            #     for g in gate_seq:
            #         '-'*5
            #         print g.name
            #         print g.C_phases_before_gate
            #         print g.C_phases_after_gate

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)
        else:
            print 'upload = false, no sequence uploaded to AWG'

class LongNuclearRamsey(DynamicalDecoupling):
    '''
    The NuclearRamsey class performs a ramsey experiment on a nuclear spin that is resonantly controlled using a decoupling sequence.
    This version varies the duration of the DynamicalDecoupling wait time and then tries to keep the phase fixed based on the Carbon
        precession_freq found in the msm
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
            #    ---|pi/2| - |Ren| - |DD| - |Ren| - |pi/2| ---
            ###########################################
            initial_Pi2 = Gate('initial_pi2_'+str(pt),'electron_Gate')
            Ren_a = Gate('Ren_a_'+str(pt), 'Carbon_Gate')
            DD_gate = Gate('DD_gate_'+str(pt),'electron_decoupling')
            Ren_b = Gate('Ren_b_'+str(pt), 'Carbon_Gate')
            final_Pi2 = Gate('final_pi2_'+str(pt),'electron_Gate')

            gate_seq = [initial_Pi2,Ren_a,DD_gate, Ren_b,final_Pi2]
            ############

            Ren_a.Carbon_ind = self.params['Addressed_Carbon']
            Ren_b.Carbon_ind = self.params['Addressed_Carbon'] #Default phase = 0
            Ren_a.scheme = self.params['Ren_Decoupling_scheme']
            Ren_b.scheme = self.params['Ren_Decoupling_scheme']
            Ren_b.phase = self.params['Phases_of_Ren_B'][pt]

            ###########
            # Set parameters for and generate the main DD element
            ###########
            DD_gate.N = self.params['N_list'][pt]#int(N2*2) #N2 because N must be even
            DD_gate.tau = self.params['tau_list'][pt]
            DD_gate.scheme = self.params['DD_wait_scheme']

            initial_Pi2.Gate_operation = 'pi2'
            final_Pi2.Gate_operation = 'pi2'
            if DD_gate.N%4==0:
                final_Pi2.phase = 0 #default phase
            else:
                final_Pi2.phase = 180

            for g in gate_seq:
                if g.Gate_type =='Carbon_Gate' or g.Gate_type =='electron_decoupling':
                    self.get_gate_parameters(g)
                    self.generate_decoupling_sequence_elements(g)
            #Insert connection elements in sequence
            gate_seq = self.insert_phase_gates(gate_seq,pt)
            #generate connection elements with proper phases, also includes electron pulses
            self.calc_and_gen_connection_elts(gate_seq)
            #Convert elements to AWG sequence and add to combined list
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq)
            combined_list_of_elements.extend(list_of_elements)

            if self.params['sweep_name']== 'Free Evolution time (s)':
                #This should correctly
                self.params['sweep_pts'][pt]= DD_gate.N*DD_gate.tau*2+gate_seq[gate_seq.index(DD_gate)+1].dec_duration
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
        
            ## MAB 20150331 Implemented to do DD starting with electron in eigenstate.
            ## TODO Find a better way to implement it? Better script?
            try:
                self.params['DD_in_eigenstate']
            except:
                pass
            else:
                if self.params['DD_in_eigenstate']:
                    simple_el_dec.N = 32
                    simple_el_dec.prefix = 'electron_'+ str(Number_of_pulses[pt])
                else:
                    pass


            ## Generate the decoupling elements
            self.generate_decoupling_sequence_elements(simple_el_dec)

            ## MAB 20150331 Implemented to do DD starting with electron in eigenstate.
            try:
                self.params['DD_in_eigenstate']
            except:
                pass
            else:
                if self.params['DD_in_eigenstate']:
                    simple_el_dec.reps = divmod(Number_of_pulses[pt],simple_el_dec.N)[0]
                else:
                    pass

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
                # print 'Initial_pulse'
                # print self.params['Initial_Pulse']
                #initial_Pi2.Gate_operation = self.params['Initial_Pulse']
                
                #if np.mod(pt,2)==1:
                #   initial_Pi2.Gate_operation = '-x'
                #else:    
                initial_Pi2.Gate_operation = self.params['Initial_Pulse']
                
                initial_Pi2.time_before_pulse = 6000e-9 # = MW switch risetime of 500 ns + 100 ns --> makes sure MW output = low when waiting for trigger #max(1e-6 -  simple_el_dec.tau_cut + 36e-9,44e-9)
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

            ## Combine to AWG sequence that can be uploaded #
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq,explicit=False)

            combined_list_of_elements.extend(list_of_elements)
            for seq_el in seq.elements:
                # print 'added to combined_seq = ', seq_el['name']
                combined_seq.append_element(seq_el)

        if upload:
            # print 'uploading list of elements'
            # qt.pulsar.upload(*combined_list_of_elements)
            print ' uploading sequence'
            # qt.pulsar.program_sequence(combined_seq)
            # print 'combined_list_of_elements'
            # for i in np.arange(len(combined_list_of_elements)):
            #     print str(i),' = ',combined_list_of_elements[i].name
            # print 'combined_seq'
            # for i in np.arange(len(combined_seq.elements)):
            #     print str(i),' = ',combined_seq.elements[i]['wfname'] 
            #print 'combined_seq', combined_list_of_elements
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
                    wait_time=3e-6,go_to_element = mbi,
                    specific_transition = self.params['transfer_begin'])

            init_y = Gate('Initial_y_pt'+str(pt),'electron_Gate',
                    Gate_operation ='pi2',
                    phase = 0,
                    specific_transition = self.params['transfer_begin'],
                    el_state_after_gate = 'sup')           

            final_y = Gate('Final_y_pt'+str(pt),'electron_Gate',
                    Gate_operation ='pi2',
                    phase = self.params['sweep_pts'][pt],
                    specific_transition = self.params['transfer_end'],
                    el_state_before_gate = 'sup')

            wait_before_RO = Gate('wait_before_RO'+str(pt),'passive_elt',
                    wait_time=3e-6, specific_transition = self.params['transfer_end'])

            invert_RO = Gate('final_pi_pulse'+str(pt),'electron_Gate',
                    Gate_operation = 'pi',
                    specific_transition = None)

            RO_Trigger = Gate('RO_trig_pt'+str(pt),'Trigger',
                    wait_time=10e-6,
                    el_state_before_gate = self.params['electron_readout_orientation'],
                    specific_transition = self.params['transfer_end'])
            

            
            gate_seq.extend([wait_after_mbi,init_y,final_y,wait_before_RO])
            
            ### cHECK ALL THREE POPULATIONS ###

            if self.params['invert_pop_ro']:
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
    adwin_process = 'MBI_single_C13' #Can be overwritten in childclasses if multiple C13's are addressed
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


        self.params['min_dec_duration']= self.params['min_dec_tau']*self.params['dec_pulse_multiple']*2

        self.params['Carbon_init_RO_wait'] = (self.params['C13_MBI_RO_duration']+self.params['SP_duration_after_C13'])*1e-6+20e-6

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

    ### Sub sequence functions, TODO:THT delet all the superfluous functions
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

        C_init_x = Gate(prefix+str(addressed_carbon)+'_x_pt'+str(pt),'electron_Gate',
                Gate_operation='pi2',
                phase = self.params['X_phase'],
                specific_transition = self.params['C'+str(addressed_carbon)+'_dec_trans'])

        C_init_Ren_b = Gate(prefix+str(addressed_carbon)+'_Ren_b_pt'+str(pt), 'Carbon_Gate',
                Carbon_ind = addressed_carbon,
                phase = self.params['C13_Y_phase']+180,
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

        C_init_elec_X_test = Gate(prefix+str(addressed_carbon)+'_elec_X_pt_test'+str(pt),'electron_Gate',
                Gate_operation='pi',
                phase = self.params['X_phase'],
                el_state_after_gate = '1',
                specific_transition = self.params['C'+str(addressed_carbon)+'_dec_trans'])

        wait_gate = Gate('Wait_gate_after_el_pi_pt'+str(pt),'passive_elt',
                     wait_time = 3e-6,specific_transition = self.params['C'+str(addressed_carbon)+'_dec_trans'])
        wait_gate_test = Gate('Wait_gate_after_el_pi_pt'+str(pt),'passive_elt',
                     wait_time =113.8e-6,specific_transition = self.params['C'+str(addressed_carbon)+'_dec_trans'])

        ### Set sequence
        if initialization_method == 'swap':  ## Swap initializes into 1 or 0
            carbon_init_seq = [C_init_y, C_init_Ren_a, C_init_x, C_init_Ren_b, C_init_RO_Trigger]
        elif initialization_method == 'MBI': ## MBI initializes into +/-X
            carbon_init_seq = [C_init_y, C_init_Ren_a, C_init_x, C_init_RO_Trigger]
        elif initialization_method == 'mixed': ## initializes into a mixed state
            carbon_init_seq = [C_init_Ren_a, C_init_x, C_init_Ren_b, C_init_RO_Trigger] #Can the first C_init_Ren be removed?

        else:
            print 'Error initialization method (%s) not recognized, supported methods are "swap", "MBI", None' %initialization_method
            return False

        ### TODO: THT, temporary fix for pi-pulse in Trigger, later redo trigger element workings
        ### I uncommented this part of the initialization for the Carbon T1 measurements. Norbert 20141104
        #print ('el_after_init'+str(el_after_init))
        cluster_y_init ='0'
        
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

        elif cluster_y_init =='1':  # Test
            carbon_init_seq.append(wait_gate_test)
            carbon_init_seq.append(C_init_elec_X) 
            

        # elif cluster_y_init =='0':  # Test     #commented out to remove additional pi pulse - Joe
        #     carbon_init_seq.append(C_init_elec_X)
            # carbon_init_seq.append(wait_gate_test)
            # carbon_init_seq.append(C_init_elec_X_test) 
            

        return carbon_init_seq


    
    def initialize_cluster_sequence(self,
            prefix                  = 'init_Cluster',
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

   
        if C_init_state ==    'up':            
            C_init_y_phase = self.params['Y_phase']

        elif C_init_state ==  'down':           
            C_init_y_phase = self.params['Y_phase']+180


        ### Define elements and gates
        Clu_init_y = Gate(prefix+str(addressed_carbon)+'cl_y_pt'+str(pt),'electron_Gate',
                Gate_operation ='pi2',
                wait_for_trigger = False,
                phase = C_init_y_phase,
                specific_transition = self.params['C'+str(addressed_carbon)+'_dec_trans'])

       
        Clu_init_y1 = Gate(prefix+str(addressed_carbon)+'cl_y1_pt'+str(pt),'electron_Gate',
                Gate_operation ='pi2',
                wait_for_trigger = True,
                phase = C_init_y_phase,
                specific_transition = self.params['C'+str(addressed_carbon)+'_dec_trans'])

        Clu_init_y2 = Gate(prefix+str(addressed_carbon)+'cl_y2_pt'+str(pt),'electron_Gate',
                Gate_operation ='pi2',
                wait_for_trigger = False,
                phase = C_init_y_phase,
                specific_transition = self.params['C'+str(addressed_carbon)+'_dec_trans'])

        
        Clu_init_Ren_a1 = Gate(prefix+str(addressed_carbon)+'cl_Ren_a1_pt'+str(pt), 'Carbon_Gate',
                Carbon_ind = addressed_carbon,
                phase = self.params['C13_X_phase'],
                specific_transition = self.params['C'+str(addressed_carbon)+'_dec_trans'])

        Clu_init_Ren_a2 = Gate(prefix+str(addressed_carbon)+'cl_Ren_a2_pt'+str(pt), 'Carbon_Gate',
            Carbon_ind = addressed_carbon,
            phase = self.params['C13_X_phase'],
            specific_transition = self.params['C'+str(addressed_carbon)+'_dec_trans'])

        Clu_init_Ren_a3 = Gate(prefix+str(addressed_carbon)+'cl_Ren_a3_pt'+str(pt), 'Carbon_Gate',
            Carbon_ind = addressed_carbon,
            phase = self.params['C13_X_phase'],
            specific_transition = self.params['C'+str(addressed_carbon)+'_dec_trans'])

        Clu_init_Ren_a4 = Gate(prefix+str(addressed_carbon)+'cl_Ren_a4_pt'+str(pt), 'Carbon_Gate',
            Carbon_ind = 6,
            phase = self.params['C13_X_phase'],
            specific_transition = self.params['C'+str(addressed_carbon)+'_dec_trans'])

        
        Clu_init_x1 = Gate(prefix+str(addressed_carbon)+'_cl_x1_pt'+str(pt),'electron_Gate',
                Gate_operation='pi2',
                wait_for_trigger = wait_for_trigger,
                phase = self.params['X_phase'],
                specific_transition = self.params['C'+str(addressed_carbon)+'_dec_trans'])

        Clu_init_x2 = Gate(prefix+str(addressed_carbon)+'_cl_x2_pt'+str(pt),'electron_Gate',
                Gate_operation='pi2',
                phase = self.params['X_phase'],
                specific_transition = self.params['C'+str(addressed_carbon)+'_dec_trans'])

        Clu_init_x3 = Gate(prefix+str(addressed_carbon)+'_cl_x3_pt'+str(pt),'electron_Gate',
                Gate_operation='pi2',
                phase = self.params['X_phase'],
                specific_transition = self.params['C'+str(addressed_carbon)+'_dec_trans'])


        Clu_init_x4 = Gate(prefix+str(addressed_carbon)+'_cl_x4_pt'+str(pt),'electron_Gate',
                Gate_operation='pi2',
                phase = self.params['X_phase'],
                specific_transition = self.params['C'+str(addressed_carbon)+'_dec_trans'])

        Clu_init_x5 = Gate(prefix+str(addressed_carbon)+'_cl_x5_pt'+str(pt),'electron_Gate',
                Gate_operation='pi2',
                phase = self.params['X_phase'],
                specific_transition = self.params['C'+str(addressed_carbon)+'_dec_trans'])

        
        Clu_init_Ren_b = Gate(prefix+str(addressed_carbon)+'cl_Ren_b_pt'+str(pt), 'Carbon_Gate',
                Carbon_ind = addressed_carbon,
                phase = self.params['C13_Y_phase'],
                specific_transition = self.params['C'+str(addressed_carbon)+'_dec_trans'])

        Clu_init_RO_Trigger = Gate(prefix+str(addressed_carbon)+'cl_RO_trig_pt'+str(pt),'Trigger',
                wait_time= self.params['Carbon_init_RO_wait'],
                event_jump = 'next',
                go_to = go_to_element,
                el_state_before_gate = el_RO_result,
                specific_transition = self.params['C'+str(addressed_carbon)+'_dec_trans'])

        Clu_init_RO_Trigger_2 = Gate(prefix+str(addressed_carbon)+'cl_RO_trig_2_pt'+str(pt),'Trigger',
                wait_time= self.params['Carbon_init_RO_wait'],
                event_jump = 'next',
                go_to = go_to_element,
                el_state_before_gate = el_RO_result,
                specific_transition = self.params['C'+str(addressed_carbon)+'_dec_trans'])

        Clu_init_RO_Trigger_3 = Gate(prefix+str(addressed_carbon)+'cl_RO_trig_3_pt'+str(pt),'Trigger',
                wait_time= self.params['Carbon_init_RO_wait'],
                event_jump = 'next',
                go_to = go_to_element,
                el_state_before_gate = el_RO_result,
                specific_transition = self.params['C'+str(addressed_carbon)+'_dec_trans'])



        Clu_init_elec_X = Gate(prefix+str(addressed_carbon)+'cl_elec_X_pt'+str(pt),'electron_Gate',
                Gate_operation='pi',
                phase = self.params['X_phase'],
                el_state_after_gate = '1',
                specific_transition = self.params['C'+str(addressed_carbon)+'_dec_trans'])

        Clu_init_elec_X_2 = Gate(prefix+str(addressed_carbon)+'cl_elec_X_pt_test'+str(pt),'electron_Gate',
                Gate_operation='pi',
                phase = self.params['X_phase'],
                el_state_after_gate = '1',
                specific_transition = self.params['C'+str(addressed_carbon)+'_dec_trans'])
     
        wait_gate_test = Gate('Wait_gate_test'+str(pt),'passive_elt',
                wait_time = 88.78e-6,specific_transition = self.params['C'+str(addressed_carbon)+'_dec_trans'])

        ### Set sequence
        if initialization_method == 'project_into_subspace':
            cluster_init_seq = [Clu_init_x1,Clu_init_Ren_a1,Clu_init_Ren_a2, Clu_init_x2, Clu_init_RO_Trigger]
        elif initialization_method == 'No_subspace_projection':
            cluster_init_seq =  [Clu_init_y1,Clu_init_Ren_a1,Clu_init_x3,Clu_init_RO_Trigger_2,Clu_init_elec_X]

        elif initialization_method == 'Full_initialization':
            cluster_init_seq =  [Clu_init_x1,Clu_init_Ren_a1,Clu_init_Ren_a2, Clu_init_x2, Clu_init_RO_Trigger,Clu_init_y,Clu_init_Ren_a3,Clu_init_x3,Clu_init_RO_Trigger_2,Clu_init_elec_X]

        elif initialization_method == 'Full_initialization_coupling':
            cluster_init_seq =  [Clu_init_x1,Clu_init_Ren_a1,Clu_init_Ren_a2, Clu_init_x2, Clu_init_RO_Trigger,Clu_init_y,Clu_init_Ren_a3,Clu_init_x3,Clu_init_RO_Trigger_2,Clu_init_elec_X,wait_gate_test,Clu_init_elec_X_2]

 
       
        # elif initialization_method == 'cluster_beating':
        #     cluster_init_seq = [Clu_init_x4,Clu_init_Ren_a4, Clu_init_x5, Clu_init_RO_Trigger_3]


        # cluster_init_seq = [Clu_init_x1,Clu_init_Ren_a1,Clu_init_Ren_a2, Clu_init_x2, Clu_init_RO_Trigger,Clu_init_y,Clu_init_Ren_a3,Clu_init_x3,Clu_init_RO_Trigger_2,Clu_init_elec_X]
        # 
        # cluster_init_seq = [Clu_init_y,Clu_init_Ren_a1, Clu_init_x2, Clu_init_RO_Trigger,Clu_init_elec_X]
        

        ### TODO: THT, temporary fix for pi-pulse in Trigger, later redo trigger element workings
        ### I uncommented this part of the initialization for the Carbon T1 measurements. Norbert 20141104
        #print ('el_after_init'+str(el_after_init))
        cluster_y_init ='0'
        
        if self.params['multiple_source']:
            ##check wether the electron state needs to be inverted at the end of readout. The transition is specified by fid_transition, 
            if el_after_init!='_0' and el_after_init != '0':
                print 'adding pulse for electron state excited in', el_after_init

                cluster_init_seq.append(Gate(prefix+str(addressed_carbon)+'_aftergate'+'_elec_X_'+el_after_init+str(pt),'electron_Gate',
                    Gate_operation='pi',
                    phase = self.params['X_phase'],
                    el_state_after_gate = '1',
                    specific_transition = self.params['fid_transition']))
                wait_gate = Gate('Wait_gate_after_el_pi_pt'+str(pt),'passive_elt',
                    wait_time = 3e-6,specific_transition = el_after_init)
                if do_wait_after_pi:
                    carbon_init_seq.append(wait_gate)

        # elif el_after_init =='1':
        #     cluster_init_seq.append(Clu_init_elec_X)
        #     if do_wait_after_pi:
        #         cluster_init_seq.append(wait_gate)

        # cluster_init_seq.append(Clu_init_elec_X)

        
        return cluster_init_seq


    def initialize_electron_sequence(self,
        prefix                  = 'init_e',
        el_after_c_init         ='0',
        wait_for_trigger        = True,
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

        'Define gates'
        # Pi/2 pulse. By default around X
        # init_elec_x = Gate(prefix+str(addressed_carbon)+'_x_pt'+str(pt),'electron_Gate',
        #     Gate_operation='pi2',
        #     phase = self.params['Y_phase'])

        # # Pi pulse. By default around X
        # init_elec_X = Gate(prefix+str(addressed_carbon)+'_elec_X_pt'+str(pt),'electron_Gate',
        #     Gate_operation='pi',
        #     phase = self.params['X_phase'],
        #     el_state_after_gate = '1')

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
            phase = self.params['X_phase'])

        elec_minY = Gate(prefix+'_-x_pt'+str(pt),'electron_Gate',
            Gate_operation='pi2',
            phase = self.params['X_phase'] + 180)

        ### THIS!
        # elec_toX =  pulse.cp(init_el_x, phase = self.params['Y_phase']       ) ### X
        # elec_toY =  pulse.cp(init_el_x, phase = self.params['X_phase']       ) ### Y

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
                    pass
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
                    pass
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
        print elec_init_state

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
            Laser = Gate('Zeno_repumper1_'+str(pt),'Trigger')
            Laser.channel = 'AOM_Newfocus'
            Laser.elements_duration = self.params['Repump_duration']
            # Laser.el_state_before_gate ='0' ### this is used in the carbon RO sequence generator.
            carbon_swap_seq.append(Laser)


        return carbon_swap_seq


    def readout_single_carbon_sequence(self,
            prefix = 'C_RO_',
            go_to_element ='next',event_jump_element = 'next',
            RO_duration = 10e-6,
            pt = 1, addressed_carbon =1,
            RO_Z=False,RO_phase = 0,
            el_RO_result = '0' ):
        ''' Old, replaced by readout_carbon_sequence, remove and upgrade measurements that use this'''

        C_RO_Ren_a = Gate(prefix+str(addressed_carbon)+'_Ren_a_'+str(pt), 'Carbon_Gate',
                Carbon_ind = addressed_carbon, phase = RO_phase)

        C_RO_y = Gate(prefix+str(addressed_carbon)+'y_'+str(pt),
                'electron_Gate',
                Gate_operation='pi2',
                phase = self.params['Y_phase'])

        C_RO_Ren_b = Gate(prefix+str(addressed_carbon)+'_Ren_b_'+str(pt),
                'Carbon_Gate',
                Carbon_ind = addressed_carbon, phase =( RO_phase+90))

        C_RO_x = Gate(prefix+str(addressed_carbon)+'_x_'+str(pt),'electron_Gate',
                Gate_operation='pi2',
                phase = self.params['X_phase'])


        C_RO_Trigger = Gate(prefix+str(addressed_carbon)+'_Trigger_'+str(pt),'Trigger',
                elements_duration= RO_duration,
                el_state_before_gate = el_RO_result)


        if RO_Z == True:
            carbon_RO_seq =[C_RO_Ren_a, C_RO_y, C_RO_Ren_b, C_RO_x, C_RO_Trigger]

        else:
            C_RO_Ren_b.phase = RO_phase
            carbon_RO_seq =[C_RO_y, C_RO_Ren_a, C_RO_x, C_RO_Trigger]

        return carbon_RO_seq
   

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



        # for clusters

        C_RO_elec_X = Gate(prefix+str(addressed_carbon)+'_elec_X_pt'+str(pt),'electron_Gate',
                Gate_operation='pi',
                phase = self.params['X_phase'],
                el_state_after_gate = '1',
                specific_transition = self.params['C'+str(addressed_carbon)+'_dec_trans'])

        C_RO_elec_X_test = Gate(prefix+str(addressed_carbon)+'_elec_X_pt_RO_test'+str(pt),'electron_Gate',
                Gate_operation='pi',
                phase = self.params['X_phase'],
                el_state_after_gate = '1',
                specific_transition = self.params['C'+str(addressed_carbon)+'_dec_trans'])

        wait_gate = Gate('Wait_gate_after_el_pi_pt'+str(pt),'passive_elt',
                     wait_time = 3e-6,specific_transition = self.params['C'+str(addressed_carbon)+'_dec_trans'])
        
        wait_gate_RO_test = Gate('Wait_gate_after_el_pi_pt_RO'+str(pt),'passive_elt',
                     wait_time = 88.78e-6,specific_transition = self.params['C'+str(addressed_carbon)+'_dec_trans'])





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
        carbons_to_RO=[]
        for jj, basis in enumerate(RO_basis_list):
            #checks how many carbons to read out and adds those in a list (in order of readout)
            if basis != 'I':    
                number_of_carbons_to_RO += 1
                carbons_to_RO.append(carbon_list[jj])
        if number_of_carbons_to_RO == 0 and do_RO_electron == False:
            return []
        print carbons_to_RO
        #######################
        ### Create sequence ###
        #######################

        carbon_RO_seq = []

        # for clusters
        
        # carbon_RO_seq.append(C_RO_elec_X)
        # carbon_RO_seq.append(wait_gate_RO_test)
        # carbon_RO_seq.append(C_RO_elec_X_test) 

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

            # carbon_RO_seq.append(
            #     Gate(prefix+'_x_pi2_init'+str(pt),'electron_Gate',
            #     Gate_operation='pi2',
            #     phase = self.params['X_phase'],
            #     wait_for_trigger=wait_for_trigger,
            #     specific_transition=self.params['C'+str(carbons_to_RO[0])+'_dec_trans']))

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

                # carbon_RO_seq.append(
                #         Gate(prefix + str(carbon_nr) + '_Ren_b_2' + str(pt), 'Carbon_Gate',
                #         specific_transition      = self.params['C'+str(carbon_nr)+'_dec_trans'],
                #         phase           = RO_phase, 
                #         extra_phase_after_gate = phase_error[kk],
                #         Carbon_ind=carbon_nr))

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
                print 'RO negative or el state in =1!'
                carbon_RO_seq.append(
                        Gate(prefix+'_-pi2_final_phase=' +str(Final_pi2_pulse_phase) + '_' +str(pt),'electron_Gate',
                        Gate_operation='pi2',
                        phase = Final_pi2_pulse_phase_negative,
                        specific_transition=self.params['C'+str(carbon_nr)+'_dec_trans']))
        else:
            carbon_nr=carbons_to_RO[-1] 
            carbon_RO_seq.append(Gate(prefix+'Wait_gate_'+str(pt),'passive_elt',
                wait_time = 20e-6,specific_transition = self.params['C'+str(carbon_nr)+'_dec_trans']))      

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
                el_RO_result          = str(self.params['C13_MBI_RO_state']))#,
                # el_after_init       = self.params['electron_after_init'])
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

                        
                        gate_seq.extend([wait_gate_seq, reset_pi, extra_wait_gate]) 
                    

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
                                    wait_time = self.params['free_evolution_time'][pt],
                                    specific_transition=self.params['C'+str(self.params['carbon_nr'])+'_dec_trans'])
                    wait_gate_seq=[wait_gate];gate_seq.extend(wait_gate_seq)  
                    # print 'wait time is' + str(self.params['free_evolution_time'][pt])             

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

class NuclearRabiWithDirectRF_v2(MBI_C13):
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
                el_RO_result          = str(self.params['C13_MBI_RO_state']))#,
                # el_after_init       = self.params['electron_after_init'])
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

                        
                        gate_seq.extend([wait_gate_seq, reset_pi, extra_wait_gate]) 
                    

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
                                    wait_time = self.params['free_evolution_time'][pt],
                                    specific_transition=self.params['C'+str(self.params['carbon_nr'])+'_dec_trans'])
                    wait_gate_seq=[wait_gate];gate_seq.extend(wait_gate_seq)  
                    # print 'wait time is' + str(self.params['free_evolution_time'][pt])             

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

class ClusterRamseyWithInitialization(MBI_C13):
   
    mprefix = 'ClusterRamseyInitialised'
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
            cluster_init_seq = self.initialize_cluster_sequence(go_to_element = mbi,
                prefix = 'Cluster_MBI_',
                wait_for_trigger      = True, pt =pt,
                initialization_method = 'Full_initialization',#'project_into_subspace',#'Full_initialization',##'###self.params['C13_init_method'],
                C_init_state          = self.params['init_state'],
                addressed_carbon      = self.params['carbon_nr'],
                el_RO_result          = str(self.params['C13_MBI_RO_state']))#,



            gate_seq.extend(cluster_init_seq)
            

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

                        
                        gate_seq.extend([wait_gate_seq, reset_pi, extra_wait_gate]) 
                    

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
                                    wait_time = self.params['free_evolution_time'][pt],
                                    specific_transition=self.params['C'+str(self.params['carbon_nr'])+'_dec_trans'])
                    wait_gate_seq=[wait_gate];gate_seq.extend(wait_gate_seq)  
                    # print 'wait time is' + str(self.params['free_evolution_time'][pt])             

            ### Readout
            carbon_tomo_seq = self.readout_carbon_sequence(
                    prefix              = 'Tomo',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 8e-6,
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
            
            # print 'EL PI AFTER MBI HAS BEEN COMMENTED OUT, NK 150825'
            #XXXXXXXXXXXXXXXXXXXXXXXXXXXX
            # if self.params['el_pi_after_mbi'] == True:
            #     El_Pi = Gate('El_Pi_'+str(pt),'electron_Gate',Gate_operation='pi')
                
            #     gate_seq.extend([El_Pi])
            ### Free evolution_time

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

class NuclearRabiWithInitialization(MBI_C13):
    '''
    This class generates the AWG sequence for a carbon Rabi experiment with nuclear initialization.
    Sequence is a combination of different subsequences
    1. MBI initialisation
    2. Carbon initialisation
    3. Carbon Rabi evolution
    4. Carbon Readout
    '''
    mprefix = 'CarbonRabiInitialised'

    def generate_sequence(self,upload=True,debug = False):
        pts = self.params['pts']
        # #initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Initialized Nuclear Rabi Sequence')

        for pt in range(pts):

            ###########################################
            #####    Generating the sequence elements      ######
            ###########################################
            #Elements for the carbon initialisation

            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]
            
            if int(self.params['Rabi_N_Sweep'][pt]) == 0:
                el_after_init = '0'
            else:
                el_after_init = self.params['el_after_init']

            ### Carbon initialization
            carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                prefix = 'C_MBI_',
                wait_for_trigger      = True, pt =pt,
                initialization_method = 'swap',
                C_init_state          = self.params['C13_init_state'],
                addressed_carbon      = self.params['Addressed_Carbon'],
                el_RO_result          = '0',
                el_after_init         = el_after_init)

            ################################

            C_Rabi_Ren = Gate('C_Rabi_Ren'+str(pt), 'Carbon_Gate',
                    Carbon_ind = self.params['Addressed_Carbon'],
                    N = self.params['Rabi_N_Sweep'][pt],
                    phase = self.params['C13_X_phase'])

            C_evol_seq =[C_Rabi_Ren]
            #############################

            ### Readout
            carbon_tomo_seq = self.readout_carbon_sequence(
                    prefix              = 'Tomo',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = [self.params['Addressed_Carbon']],
                    RO_basis_list       = ['Z'],
                    el_state_in         = int(el_after_init),
                    readout_orientation = self.params['electron_readout_orientation'])

            # Gate seq consits of 3 sub sequences [MBI] [Carbon init]  [RO and evolution]
            gate_seq = []
            gate_seq.extend(mbi_seq), gate_seq.extend(carbon_init_seq)
            gate_seq.extend(C_evol_seq), gate_seq.extend(carbon_tomo_seq)
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

class NuclearRabiWithInitialization_v2(MBI_C13):
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
                    if (g.C_phases_before_gate[self.params['carbon_nr']] == None):
                        print "[ None]"
                    else:
                        print "[ %.3f]" %(g.C_phases_before_gate[self.params['carbon_nr']]/np.pi*180)

                    if (g.C_phases_after_gate[self.params['carbon_nr']] == None):
                        print "[ None]"
                    else:
                        print "[ %.3f]" %(g.C_phases_after_gate[self.params['carbon_nr']]/np.pi*180)
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

class NuclearT1_2(MBI_C13):
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


class NuclearRabiWithDirectRF(MBI_C13):
    '''
    Made by Michiel 
    This class tests an RF pulse on a nuclear spin
    1. Nitrogen MBI initialisation
    2. Carbon init (MBI or SWAP)
    3. Pulse on single nuclear spin using RF
    4. Carbon Full Tomo

    Sequence: |N-MBI| -|CinitA|-|RF-Pulse|-|Tomography|

    Edited by Joe 07-11-17
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
            # if self.params['RF_pulse_durations'][pt] > 3e-6:
            #     rabi_pulse = Gate('Rabi_pulse_'+str(pt),'RF_pulse',
            #         length      = self.params['RF_pulse_durations'][pt],
            #         RFfreq      = self.params['RF_pulse_frqs'][pt],
            #         amplitude   = self.params['RF_pulse_amps'][pt])
            #     gate_seq.extend([rabi_pulse])

            ### Readout
            carbon_tomo_seq = self.readout_carbon_sequence(
                    prefix              = 'Tomo',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = [self.params['carbon_nr']],
                    RO_basis_list       = [self.params['C_RO_phase'][pt]],
                    readout_orientation = self.params['electron_readout_orientation'],
                    el_state_in = int(self.params['el_after_init']))
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
        # #initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Initialized Nuclear Rabi Sequence')
        # adwin_process = 'MBI_single_C13'  --> change this!

        self.get_tau_larmor()

        for pt in range(pts):

            ###########################################
            #####    Generating the sequence elements      ######
            ###########################################
            #Elements for the carbon initialisation

            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]

            carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                    initialization_method = self.params['C13_init_method'], pt =pt,
                    addressed_carbon= self.params['Carbon_A'],
                    C_init_state = self.params['C13_init_state'],
                    el_RO_result = '0' )
            ################################

            C_Rabi_Ren = Gate('C_Rabi_Ren'+str(pt), 'Carbon_Gate',
                    Carbon_ind = self.params['Carbon_B'],
                    N = self.params['Rabi_N_Sweep'][pt],
                    tau = self.params['Rabi_tau_Sweep'][pt],
                    phase = self.params['C13_X_phase'])

            C_evol_seq =[C_Rabi_Ren]
            #############################
            carbon_RO_seq = self.readout_single_carbon_sequence(
                    pt = pt, addressed_carbon =self.params['Carbon_A'],
                    RO_Z=self.params['C_RO_Z'],
                    RO_phase = self.params['C_RO_phase'],
                    el_RO_result = '0' )

            # Gate seq consits of 3 sub sequences [MBI] [Carbon init]  [RO and evolution]
            gate_seq = []
            gate_seq.extend(mbi_seq), gate_seq.extend(carbon_init_seq)
            gate_seq.extend(C_evol_seq), gate_seq.extend(carbon_RO_seq)
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
                if ((g.C_phases_before_gate[self.params['carbon_list'][0]] == None)):
                    print "[ None ]"
                elif g.C_phases_before_gate[self.params['carbon_list'][0]] != None:
                    print "[ %.3f ]" %(g.C_phases_before_gate[self.params['carbon_list'][0]]/np.pi*180)

                if ((g.C_phases_after_gate[self.params['carbon_list'][0]] == None)):
                    print "[ None ]"
                elif g.C_phases_after_gate[self.params['carbon_list'][0]] != None:
                    print "[ %.3f ]" %(g.C_phases_after_gate[self.params['carbon_list'][0]]/np.pi*180)

class Nuclear_Crosstalk_vs2(MBI_C13):
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
                carbon_gate = Gate('C'+str(self.params['Carbon_B'])+'_Crosstalk_gate_' + str(gate_nr) + '_pt_' +str(pt),
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
                    if (g.C_phases_before_gate[self.params['carbon_nr']] == None):
                        print "[ None]"
                    else:
                        print "[ %.3f]" %(g.C_phases_before_gate[self.params['carbon_nr']]/np.pi*180)

                    if (g.C_phases_after_gate[self.params['carbon_nr']] == None):
                        print "[ None]"
                    else:
                        print "[ %.3f]" %(g.C_phases_after_gate[self.params['carbon_nr']]/np.pi*180)
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
                if ((g.C_phases_before_gate[self.params['Carbon_nr']] == None)):
                    print "[ None ]"
                elif g.C_phases_before_gate[self.params['Carbon_nr']] != None:
                    print "[ %.3f ]" %(g.C_phases_before_gate[self.params['Carbon_nr']]/np.pi*180)

                if ((g.C_phases_after_gate[self.params['Carbon_nr']] == None)):
                    print "[ None ]"
                elif g.C_phases_after_gate[self.params['Carbon_nr']] != None:
                    print "[ %.3f ]" %(g.C_phases_after_gate[self.params['Carbon_nr']]/np.pi*180)

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
            #############################
            # carbon_RO_seq = self.readout_single_carbon_sequence(
            #         pt = pt, addressed_carbon =self.params['Carbon_nr'],
            #         RO_Z=self.params['C_RO_Z'],
            #         RO_phase = self.params['C_RO_phase'],
            #         el_RO_result = '0' )

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
                if ((g.C_phases_before_gate[self.params['Carbon_nr']] == None)):
                    print "[ None ]"
                elif g.C_phases_before_gate[self.params['Carbon_nr']] != None:
                    print "[ %.3f ]" %(g.C_phases_before_gate[self.params['Carbon_nr']]/np.pi*180)

                if ((g.C_phases_after_gate[self.params['Carbon_nr']] == None)):
                    print "[ None ]"
                elif g.C_phases_after_gate[self.params['Carbon_nr']] != None:
                    print "[ %.3f ]" %(g.C_phases_after_gate[self.params['Carbon_nr']]/np.pi*180)

class GeometricGate(MBI_C13):
    '''
    This class is used to determine the effectiveness of a new type of gate.
    The sequence consists of the following steps:

    1. MBI initialisation
    2. Carbon initialisation (Swap or MBI)
    2a. pi/2 pulse on the electronic state.
    3a. conditional gate on the carbon over angle theta (along x)
    3b. unconditional gate on the carbon over the same angle (along x)
    4. wait
    5a. Unconditional pi rotation on the carbon
    5b. Pi pulse on the electronic state
    6. wait
    7a. conditional gate on the carbon over angle theta (along -x)
    7b. unconditional gate on the carbon over the same angle (along -x)
    6c. pi/2 pulse on the electornic state
    8. RO of the electronic state.

    Nk 2015
    '''

    mprefix = 'Carbon_Geometric_Gate'
    adwin_process = 'MBI_multiple_C13'

    def generate_sequence(self,upload=True,debug = False):
        pts = self.params['pts']
        # #initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Initialized Nuclear-gate sequence')

        #self.get_tau_larmor()
        if (not self.params['calibrate_pulses'] and not self.params['no_unconditional_rotation']):
            self.params['Number_of_pulses_uncond'] = self.params['C'+str(self.params['Carbon_nr'])+'_geo_uncond_N']*pts
            self.params['Number_of_pulses_cond'] = self.params['C'+str(self.params['Carbon_nr'])+'_geo_cond_N']*pts

        elif (self.params['calibrate_pulses'] and not self.params['no_unconditional_rotation']):
            self.params['Number_of_pulses_cond'] = self.params['C'+str(self.params['Carbon_nr'])+'_geo_cond_N']*pts

        elif (not self.params['calibrate_pulses'] and self.params['no_unconditional_rotation']):
            self.params['Number_of_pulses_uncond'] = self.params['C'+str(self.params['Carbon_nr'])+'_geo_uncond_N']*pts
        else:
            print 'Master, you requested nonsense.'

        print self.params['Number_of_pulses_cond']
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

            C_geo_cond1=Gate('C_geo_cond_Pi1'+str(pt), 'Carbon_Gate',
                    Carbon_ind = self.params['Carbon_nr'],
                    N = self.params['Number_of_pulses_cond'][pt],
                    tau = self.params['C'+str(self.params['Carbon_nr'])+'_Ren_tau'+self.params['electron_transition']][0],
                    phase = self.params['C13_X_phase'])

            C_geo_uncond1=Gate('C_geo_uncond_Pi1'+str(pt), 'Carbon_Gate',
                    Carbon_ind = self.params['Carbon_nr'],
                    N = self.params['Number_of_pulses_uncond'][pt],
                    tau = self.params['C'+str(self.params['Carbon_nr'])+'_uncond_tau'][0],
                    phase = self.params['C13_X_phase'])


            ################################
            ##the two wait gates to be put in the beginning and end
            if not self.params['waiting_times'][pt]==0:
                wait_gate1 = Gate('Wait_gate1_'+str(pt),'passive_elt',
                                     wait_time = self.params['waiting_times'][pt])
                wait_gate2 = Gate('Wait_gate2_'+str(pt),'passive_elt',
                                     wait_time = self.params['waiting_times'][pt])

            ###
            ## unconditional rotations on the two spins
            C_uncond_Pi = Gate('C_uncond_Pi'+str(pt), 'Carbon_Gate',
                    Carbon_ind = self.params['Carbon_nr'],
                    N = self.params['C'+str(self.params['Carbon_nr'])+'_uncond_pi_N'][0],
                    tau = self.params['C'+str(self.params['Carbon_nr'])+'_uncond_tau'][0],
                    phase = self.params['C13_X_phase'])

            #wait_gate1.C_phases_after_gate=10*[0]

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


            C_geo_cond2 = Gate('C_geo_cond_Pi2'+str(pt), 'Carbon_Gate',
                    Carbon_ind = self.params['Carbon_nr'],
                    N = self.params['Number_of_pulses_cond'][pt],
                    tau = self.params['C'+str(self.params['Carbon_nr'])+'_Ren_tau'+self.params['electron_transition']][0],
                    phase = self.params['C13_X_phase'])

            C_geo_uncond2 = Gate('C_geo_uncond_Pi2'+str(pt), 'Carbon_Gate',
                    Carbon_ind = self.params['Carbon_nr'],
                    N = self.params['Number_of_pulses_uncond'][pt],
                    tau = self.params['C'+str(self.params['Carbon_nr'])+'_uncond_tau'][0],
                    phase = self.params['C13_X_phase']+180)

            ## put the geometric gate part of the sequence together.
            if not self.params['waiting_times'][pt]==0:
                if self.params['calibrate_pulses']:
                    C_pi_seq=[C_geo_cond1,C_geo_uncond1]
                elif self.params['no_unconditional_rotation']:
                    C_pi_seq =[E_init_y,C_geo_cond1,wait_gate1,C_uncond_Pi,E_Pi,wait_gate2,C_geo_cond2,E_RO_y]
                else:
                    C_pi_seq =[E_init_y,C_geo_cond1,C_geo_uncond1,wait_gate1,C_uncond_Pi,E_Pi,wait_gate2,C_geo_uncond2,C_geo_cond2,E_RO_y]
            else:
                if self.params['calibrate_pulses']:
                    C_pi_seq=[C_geo_cond1,C_geo_uncond1]
                elif self.params['no_unconditional_rotation']:
                    C_pi_seq =[E_init_y,C_geo_cond1,C_uncond_Pi,E_Pi,C_geo_cond2,E_RO_y]
                else:
                    C_pi_seq =[E_init_y,C_geo_cond1,C_geo_uncond1,C_uncond_Pi,E_Pi,C_geo_uncond2,C_geo_cond2,E_RO_y]

            #############################

            #In the case of pulse calibration we need to perform tomography on the carbon.
            if self.params['calibrate_pulses']:
                RO_seq = self.readout_single_carbon_sequence(
                        pt = pt, addressed_carbon =self.params['Carbon_nr'],
                        RO_Z=True,
                        RO_phase = 0,
                        el_RO_result = '0' )
            else:
                # for testing the actual geometric gate --> RO of the electronic state
                RO_seq = [Gate('C'+str(self.params['Carbon_nr'])+'_Trigger_'+str(pt),'Trigger',
                    elements_duration= 10e-6,
                    el_state_before_gate = '0')]



            # Piece the gate sequence together.
            gate_seq = []
            gate_seq.extend(mbi_seq), gate_seq.extend(carbon_init_seq)
            gate_seq.extend(C_pi_seq), gate_seq.extend(RO_seq)
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
                if ((g.C_phases_before_gate[self.params['Carbon_nr']] == None)):
                    print "[ None ]"
                elif g.C_phases_before_gate[self.params['Carbon_nr']] != None:
                    print "[ %.3f ]" %(g.C_phases_before_gate[self.params['Carbon_nr']]/np.pi*180)

                if ((g.C_phases_after_gate[self.params['Carbon_nr']] == None)):
                    print "[ None ]"
                elif g.C_phases_after_gate[self.params['Carbon_nr']] != None:
                    print "[ %.3f ]" %(g.C_phases_after_gate[self.params['Carbon_nr']]/np.pi*180)


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
                    el_after_init         = self.params['el_after_init'])
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

            # I don't want to see gate_seq every time SK
            # if not debug:
            #     print '*'*10
            #     for g in gate_seq:
            #         print g.name

            # if debug:
                # for g in gate_seq:
                #     print g.name

                    # if ((g.C_phases_before_gate[self.params['carbon_list'][0]] == None) and (g.C_phases_before_gate[self.params['carbon_list'][1]] == None)):
                    #     print "[ None , None ]"
                    # elif g.C_phases_before_gate[self.params['carbon_list'][0]] == None:
                    #     print "[ None , %.3f ]" %(g.C_phases_before_gate[self.params['carbon_list'][1]]/np.pi*180)
                    # elif g.C_phases_before_gate[self.params['carbon_list'][1]] == None:
                    #     print "[ %.3f, None ]" %(g.C_phases_before_gate[self.params['carbon_list'][0]]/np.pi*180)
                    # else:
                    #     print "[ %.3f , %.3f ]" %(g.C_phases_before_gate[self.params['carbon_list'][0]]/np.pi*180, g.C_phases_before_gate[self.params['carbon_list'][1]]/np.pi*180)


                    # if ((g.C_phases_after_gate[self.params['carbon_list'][0]] == None) and (g.C_phases_after_gate[self.params['carbon_list'][1]] == None)):
                    #     print "[ None , None ]"
                    # elif g.C_phases_after_gate[self.params['carbon_list'][0]] == None:
                    #     print "[ None , %.3f ]" %(g.C_phases_after_gate[self.params['carbon_list'][1]]/np.pi*180)
                    # elif g.C_phases_after_gate[self.params['carbon_list'][1]] == None:
                    #     print "[ %.3f, None ]" %(g.C_phases_after_gate[self.params['carbon_list'][0]]/np.pi*180)
                    # else:
                    #     print "[ %.3f , %.3f ]" %(g.C_phases_after_gate[self.params['carbon_list'][0]]/np.pi*180, g.C_phases_after_gate[self.params['carbon_list'][1]]/np.pi*180)

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'


### SWAP GATE CLASS
class Two_QB_Swap_Sten(MBI_C13):
    '''
    Sequence: |Initialize Carbons| - |Prepare NV1| - |SWAP NV1-C1| -|Tomography|
    '''
    mprefix         = 'Swap-gate'
    adwin_process   = 'MBI_multiple_C13'


    def generate_sequence(self, upload=True, debug=False):

        qt.pulsar.set_channel_opt('AOM_Newfocus','high', qt.instruments['NewfocusAOM'].power_to_voltage(self.params['after_swap_repump_power'],controller='sec'))
        pts = self.params['pts']

        ### initialize empty sequence and elements
        combined_list_of_elements =[]
        #!!!!!!!!!!!!# combined_seq = pulsar.Sequence('Two Qubit MBE')
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
            
            #######################
            ## INITIALIZE CARBON ##
            #######################

            # It is for one carbon now. Rewrite for extenstion. Also you supply this in script. Think about it
           
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
            ## CHECK THIS
            # init_wait_for_trigger = False

            # ###############################################################
            # # ELECTRON STATE PREPARE it is already in 0 after INIT carbon #
            # ###############################################################
            electron_init_seq = self.initialize_electron_sequence(
                prefix                  = 'init_E',
                elec_init_state         = self.params['elec_init_state'],
                pt                      = pt,
                el_after_c_init         = self.params['el_after_init'],
                wait_for_trigger        = init_wait_for_trigger)
            gate_seq.extend(electron_init_seq)

            # gate_seq.append(Gate('Wait_gate'+str(pt),'passive_elt',wait_time = 5e-6))

            # # # print "gate_seq after electron_init", gate_seq

            # # ##########
            # # ## SWAP ##
            # # ##########
            carbon_swap_seq = self.carbon_swap_gate(
                go_to_element         = mbi,
                prefix                = 'swap_C', 
                pt                    = pt,
                addressed_carbon      = self.params['carbon_init_list'][0],
                RO_after_swap         = self.params['RO_after_swap'])
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
                print '*'*10
                for g in gate_seq:
                    print g.name####
        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'

### Multiple carbon initialization classes ###
class Two_QB_Probabilistic_MBE_v3(MBI_C13):
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

        for pt in range(pts): ### Sweep over RO basis OR the MBI RO power!


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

                if self.params['el_after_init']                == '1':
                    self.params['do_wait_after_pi']            = True
                else: 
                    self.params['do_wait_after_pi']            = False

                carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                    prefix = 'C_MBI' + str(kk+1) + '_C',
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

                probabilistic_MBE_seq = self.readout_carbon_sequence(
                        prefix              = 'MBE' + str(kk+1),
                        pt                  = pt,
                        go_to_element       = mbi,
                        event_jump_element  = 'next',
                        RO_trigger_duration = 150e-6,
                        carbon_list         = self.params['carbon_list'],
                        RO_basis_list       = self.params['MBE_bases'],
                        el_RO_result         = '0',
                        addressed_carbon      = self.params['carbon_init_list'][kk])

                gate_seq.extend(probabilistic_MBE_seq)

            print self.params['Tomography Bases'][pt]
            carbon_tomo_seq = self.readout_carbon_sequence(
                    prefix              = 'Tomo',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomography Bases'][pt],
                    el_state_in         = int(self.params['el_after_init']),
                    readout_orientation = self.params['electron_readout_orientation'],
                    do_init_pi2         = True)
            
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
                print '*'*10
                for g in gate_seq:
                    print g.name,g.el_state_before_gate,g.el_state_after_gate,g.specific_transition
                    print 'for this gate i decided for carbon 2:',g.C_phases_before_gate[2],g.C_phases_after_gate[2]
                    print 'for this gate i decided for carbon 4:',g.C_phases_before_gate[4],g.C_phases_after_gate[4]
                    print


            # if debug:
                # for g in gate_seq:
                #     print g.name

                    # if ((g.C_phases_before_gate[self.params['carbon_list'][0]] == None) and (g.C_phases_before_gate[self.params['carbon_list'][1]] == None)):
                    #     print "[ None , None ]"
                    # elif g.C_phases_before_gate[self.params['carbon_list'][0]] == None:
                    #     print "[ None , %.3f ]" %(g.C_phases_before_gate[self.params['carbon_list'][1]]/np.pi*180)
                    # elif g.C_phases_before_gate[self.params['carbon_list'][1]] == None:
                    #     print "[ %.3f, None ]" %(g.C_phases_before_gate[self.params['carbon_list'][0]]/np.pi*180)
                    # else:
                    #     print "[ %.3f , %.3f ]" %(g.C_phases_before_gate[self.params['carbon_list'][0]]/np.pi*180, g.C_phases_before_gate[self.params['carbon_list'][1]]/np.pi*180)


                    # if ((g.C_phases_after_gate[self.params['carbon_list'][0]] == None) and (g.C_phases_after_gate[self.params['carbon_list'][1]] == None)):
                    #     print "[ None , None ]"
                    # elif g.C_phases_after_gate[self.params['carbon_list'][0]] == None:
                    #     print "[ None , %.3f ]" %(g.C_phases_after_gate[self.params['carbon_list'][1]]/np.pi*180)
                    # elif g.C_phases_after_gate[self.params['carbon_list'][1]] == None:
                    #     print "[ %.3f, None ]" %(g.C_phases_after_gate[self.params['carbon_list'][0]]/np.pi*180)
                    # else:
                    #     print "[ %.3f , %.3f ]" %(g.C_phases_after_gate[self.params['carbon_list'][0]]/np.pi*180, g.C_phases_after_gate[self.params['carbon_list'][1]]/np.pi*180)

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'



### Multiple carbon initialization classes ###

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
                    el_state_in         = 0,
                    addressed_carbon      = self.params['carbon_init_list'][kk])
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
                    el_state_in         = 1,
                    addressed_carbon      = self.params['carbon_init_list'][kk])
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
                if  debug==True:
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

class Three_QB_Probabilistic_MBE(MBI_C13):
    '''
    Sequence: |N-MBI| -|Cinit|^N-|MBE|^N-|Tomography|
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
                probabilistic_MBE_seq =     self.logic_init_seq(
                        prefix              = '3C_init_' + str(kk+1),
                        pt                  =  pt,
                        carbon_list         = self.params['carbon_list'],
                        RO_basis_list       = self.params['MBE_bases'],
                        RO_trigger_duration = 150e-6,
                        el_RO_result        = '0',
                        logic_state         = self.params['3qb_logical_state'] ,
                        go_to_element       = mbi,
                        event_jump_element   = 'next',
                        readout_orientation = 'positive')

                gate_seq.extend(probabilistic_MBE_seq)

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

            ### Convert elements to AWG sequence and add to combined list
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq, explicit=True)
            combined_list_of_elements.extend(list_of_elements)

            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)

            # if not debug:
            print '*'*10
            for g in gate_seq:
                print g.name

            # if debug:
            #     for g in gate_seq:
            #         print '----------'
            #         print g.name
            #         print '----------'
            #         if ((g.C_phases_before_gate[self.params['carbon_list'][0]] == None) and (g.C_phases_before_gate[self.params['carbon_list'][1]] == None)):
            #             print "[ None , None ]"
            #         elif g.C_phases_before_gate[self.params['carbon_list'][0]] == None:
            #             print "[ None , %.3f ]" %(g.C_phases_before_gate[self.params['carbon_list'][1]]/np.pi*180)
            #         elif g.C_phases_before_gate[self.params['carbon_list'][1]] == None:
            #             print "[ %.3f, None ]" %(g.C_phases_before_gate[self.params['carbon_list'][0]]/np.pi*180)
            #         else:
            #             print "[ %.3f , %.3f ]" %(g.C_phases_before_gate[self.params['carbon_list'][0]]/np.pi*180, g.C_phases_before_gate[self.params['carbon_list'][1]]/np.pi*180)


            #         if ((g.C_phases_after_gate[self.params['carbon_list'][0]] == None) and (g.C_phases_after_gate[self.params['carbon_list'][1]] == None)):
            #             print "[ None , None ]"
            #         elif g.C_phases_after_gate[self.params['carbon_list'][0]] == None:
            #             print "[ None , %.3f ]" %(g.C_phases_after_gate[self.params['carbon_list'][1]]/np.pi*180)
            #         elif g.C_phases_after_gate[self.params['carbon_list'][1]] == None:
            #             print "[ %.3f, None ]" %(g.C_phases_after_gate[self.params['carbon_list'][0]]/np.pi*180)
            #         else:
            #             print "[ %.3f , %.3f ]" %(g.C_phases_after_gate[self.params['carbon_list'][0]]/np.pi*180, g.C_phases_after_gate[self.params['carbon_list'][1]]/np.pi*180)
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
        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'

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
            
class Zeno_TwoQB(MBI_C13):
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



class Zeno_TwoQB_classical(MBI_C13):
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
class Zeno_simplified(MBI_C13):
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

class Zeno_ErrDetection(MBI_C13):
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
class Zeno_OneQB(MBI_C13):
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

class Zeno_OneQB_Zmeasurement(MBI_C13):
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

class Zeno_ThreeQB(MBI_C13):

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

class GHZ_ThreeQB(MBI_C13):
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

class GHZ_ThreeQB_Unbranched(MBI_C13):
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

class GHZ_3mmts_Unbranched(MBI_C13):
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

class GHZ_Debug_ZZTomo(MBI_C13):
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

class test_undo_RO_phase_and_invert(MBI_C13):

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


class test_undo_RO_phase(MBI_C13):

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


class QMemory_repumping(MBI_C13):
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

class DFS_check(MBI_C13):
    '''
    Sequence: Sequence: |N-MBI| -|Cinit|^2-|MBE|^N-(|Wait|-|Parity-measurement|-|Wait|)^M-|Tomography|
    '''
    #mprefix='Zeno_TwoQubit'
    mprefix='DFS_init'
    adwin_process='MBI_multiple_C13'

    ##### TODO: Add AOM control from the AWG for arbitrary AOM channels.
    # def autoconfig(self):

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
                gate_seq.extend([Gate('2C_init_elec_X_pt'+str(pt),'electron_Gate',
                                        Gate_operation='pi',
                                        phase = self.params['X_phase'],
                                        el_state_after_gate = '1')])

            # gate_seq.extend([Gate('2C_init_wait_gate_'+str(pt),'passive_elt',
            #                  wait_time = 10e-6)])

            ### control the repumping laser with the AWG.

            if self.params['Repump_duration'][pt]!=0:
                Laser=Gate('pump'+str(pt),'Trigger',
                    duration=self.params['Repump_duration'][pt],
                    )
                Laser.channel='AOM_Newfocus'
                Laser.elements_duration=round(self.params['Repump_duration'][pt],9)
                if self.params['Zeno_SP_A_power'] != 0:
                    Laser.el_state_before_gate='0'
                    Laser.el_state_after_gate='0'
                else:
                    Laser.el_state_before_gate='1'
                    Laser.el_state_after_gate='1'

                gate_seq.append(Laser)



            ### waiting time without Zeno msmmts.

            # wait_gate = Gate('Wait_gate_'+str(pt),'passive_elt',
            #              wait_time = self.params['free_evolution_time']-self.params['2C_RO_trigger_duration']-self.params['Repump_duration'][pt])
            # gate_seq.extend([wait_gate])
            
            ### Readout

            carbon_tomo_seq = self.readout_carbon_sequence(
                    prefix              = 'Tomo',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    el_state_in         = 0,
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

                    # if ((g.C_phases_before_gate[self.params['carbon_list'][0]] == None) and (g.C_phases_before_gate[self.params['carbon_list'][1]] == None)):
                    #     print "[ None , None ]"
                    # elif g.C_phases_before_gate[self.params['carbon_list'][0]] == None:
                    #     print "[ None , %.3f ]" %(g.C_phases_before_gate[self.params['carbon_list'][1]]/np.pi*180)
                    # elif g.C_phases_before_gate[self.params['carbon_list'][1]] == None:
                    #     print "[ %.3f, None ]" %(g.C_phases_before_gate[self.params['carbon_list'][0]]/np.pi*180)
                    # else:
                    #     print "[ %.3f , %.3f ]" %(g.C_phases_before_gate[self.params['carbon_list'][0]]/np.pi*180, g.C_phases_before_gate[self.params['carbon_list'][1]]/np.pi*180)


                    # if ((g.C_phases_after_gate[self.params['carbon_list'][0]] == None) and (g.C_phases_after_gate[self.params['carbon_list'][1]] == None)):
                    #     print "[ None , None ]"
                    # elif g.C_phases_after_gate[self.params['carbon_list'][0]] == None:
                    #     print "[ None , %.3f ]" %(g.C_phases_after_gate[self.params['carbon_list'][1]]/np.pi*180)
                    # elif g.C_phases_after_gate[self.params['carbon_list'][1]] == None:
                    #     print "[ %.3f, None ]" %(g.C_phases_after_gate[self.params['carbon_list'][0]]/np.pi*180)
                    # else:
                    #     print "[ %.3f , %.3f ]" %(g.C_phases_after_gate[self.params['carbon_list'][0]]/np.pi*180, g.C_phases_after_gate[self.params['carbon_list'][1]]/np.pi*180)

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG' 