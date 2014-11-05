'''
Measurement classes
File made by Adriaan Rol
Edited by THT
'''
import numpy as np
import qt
import copy
from measurement.lib.pulsar import pulse, pulselib, element, pulsar
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt


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
        special gates: 'mbi', 'Trigger', 'electron_repump'
        '''
        self.name       = name
        self.prefix     = name          ### Default prefix is identical to name, can be overwritten

        # Information on what type of gate to implement
        self.Gate_type  = Gate_type
        self.phase      = kw.pop('phase',0)             ### Both for electron and Carbon gates
        self.Carbon_ind = kw.pop('Carbon_ind',0)        ### 0 is the electronic spin, the rest are carbon spins

        self.N          = kw.pop('N',None)
        self.tau        = kw.pop('tau',None)

        self.wait_time  = kw.pop('wait_time',None)
        self.reps = kw.pop('reps',1) # only overwritten in case of Carbon decoupling elements
        self.dec_duration = kw.pop('dec_duration', None)  # can be specified if a custom dec duration is desired

        self.Gate_operation = kw.pop('Gate_operation',None) ### For electron gates,'pi2', 'pi', 'general'
        self.amplitude      = kw.pop('amplitude', 0)        ### For electron gates, sets amplitude in case of 'general'
        self.length         = kw.pop('length',0)            ### For electron gates, sets length in case of 'general'

        #Scheme is used both for generating decoupling elements aaswell as the combine to sequence command
        if self.Gate_type in ['Connection_element','electron_Gate','passive_elt','mbi','electron_repump']:
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
                self.C_phases_after_gate[self.Carbon_ind] =self.phase
            else :
                self.C_phases_after_gate[self.Carbon_ind] = self.phase/180.*np.pi

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

    def _X_elt(self):
        '''
        X element that is used in different measurement child classes
        '''
        X = pulselib.MW_IQmod_pulse('electron X-Pi-pulse',
            I_channel='MW_Imod', Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod',
            frequency = self.params['AWG_MBI_MW_pulse_mod_frq'],
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            length = self.params['fast_pi_duration'],
            amplitude = self.params['fast_pi_amp'],
            phase =  self.params['X_phase'])
        return X

    def _pi2_elt(self):
        '''
        xpi2 element that is used in different measurement child classes
        '''
        pi2 = pulselib.MW_IQmod_pulse('electron Pi/2-pulse',
            I_channel='MW_Imod', Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod',
            frequency = self.params['fast_pi2_mod_frq'],
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            length = self.params['fast_pi2_duration'],
            amplitude = self.params['fast_pi2_amp'],
            phase = self.params['X_phase'])
        return pi2

    def _electron_pulse_elt(self, length, amplitude):
        '''
        general electron pulse element that is used in different measurement child classes
        '''
        electron_pulse = pulselib.MW_IQmod_pulse('electron-pulse',
            I_channel='MW_Imod', Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod',
            frequency = self.params['fast_pi2_mod_frq'],
            PM_risetime = self.params['MW_pulse_mod_risetime'],
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
            PM_channel='MW_pulsemod',
            frequency = self.params['fast_pi2_mod_frq'],
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            length = self.params['cust_pi2_duration'],
            amplitude = self.params['cust_pi2_amp'],
            phase = self.params['X_phase'])
        return pi2

    def _Y_elt(self):
        '''
        Trigger element that is used in different measurement child classes
        '''
        Y = pulselib.MW_IQmod_pulse('electron X-Pi-pulse',
            I_channel='MW_Imod', Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod',
            frequency = self.params['AWG_MBI_MW_pulse_mod_frq'],
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            length = self.params['fast_pi_duration'],
            amplitude = self.params['fast_pi_amp'],
            phase =  self.params['Y_phase'])
        return Y

    def _Trigger_element(self,duration = 10e-6, name='Adwin_trigger'):
        '''
        Trigger element that is used in different measurement child classes
        '''
        Trig = pulse.SquarePulse(channel = 'adwin_sync',
            length = duration, amplitude = 2)
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
        ind = gate.Carbon_ind
        if ind ==0:
            #Don't take arguments from a list if it is not acting on a 
            #carbon (i.e. electron decoupling)
            return
        if gate.N==None:
            gate.N = self.params['C'+str(ind)+'_Ren_N'][resonance]
        if gate.tau==None:
            gate.tau = self.params['C'+str(ind)+'_Ren_tau'][resonance]


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
        gates_in_need_of_connecting_elts1 = ['Carbon_Gate','electron_decoupling','passive_elt']
        gates_in_need_of_connecting_elts2 = ['Carbon_Gate','electron_decoupling']
        #TODO_MAR: Insert a different type of phase gate in the case of a passive element.
        #TODO_THT: What the fuck does this mean??? Clearly it does not work...

        for i in range(len(gate_seq)-1):
            ext_gate_seq.append(gate_seq[i])
            if ((gate_seq[i].Gate_type in gates_in_need_of_connecting_elts1) and
                    (gate_seq[i+1].Gate_type in gates_in_need_of_connecting_elts1)):
                ext_gate_seq.append(Gate('phase_gate_'+ gate_seq[i+1].name + str(i)+'_'+str(pt),'Connection_element'))

            if gate_seq[i].Gate_type =='Trigger' :
                if (gate_seq[i+1].Gate_type in gates_in_need_of_connecting_elts2):
                    ext_gate_seq.append(Gate('phase_gate_' + gate_seq[i+1].name+str(i)+'_'+str(pt),'Connection_element'))

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
                        precession_freq = self.params['C'+str(C_ind)+'_freq']*2*np.pi #convert to radians/s
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
            tau =g.dec_duration/(2*(k+1)*self.params['dec_pulse_multiple'])
            if tau == 0:
                g.N = 0
                g.tau = 0
            elif tau < self.params['min_dec_tau']:
                print 'Error: decoupling tau: (%s) smaller than minimum value(%s), decoupling duration (%s)' %(tau,self.params['min_dec_tau'],g.dec_duration )
                break
            #If the found tau is allowed (bigger than min and smaller than max loop is done)
            elif tau > self.params['min_dec_tau'] and tau< self.params['max_dec_tau']:
                g.tau = tau
                g.N = int((k+1)*self.params['dec_pulse_multiple'])
                # print 'found the following decoupling tau: %s, N: %s' %(tau,g.N)
                break
            elif k == 79 and tau>self.params['max_dec_tau']:
                print 'Error: decoupling duration (%s) to large, for %s pulses decoupling tau (%s) larger than max decoupling tau (%s)' %(g.dec_duration,k,tau,self.params['max_dec_tau'])
        return g

    def determine_decoupling_scheme(self,Gate):
        '''
        Function used by generate_decoupling_sequence_elements
        Takes the first few lines of code that determine what kind of decoupling scheme is being used and puts it in a  function
        TODO_MAR: Document limitations and advantages of different decoupling schemes (multiples of 4ns?, lots of elements, very long elements)

        '''
        if Gate.N == 0:
            ### For N==0, select a different scheme without pulses
            Gate.scheme = 'NO_Pulses'
        elif Gate.tau>2e-6 :           ## ERROR?
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
            C1str = 'C'+str(i)+'_freq_1'
            Cdecstr = 'C'+str(i)+'_freq'
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
        if Gate.Carbon_ind != 0:
            Gate.extra_phase_correction_list = self.params['C' + str(Gate.Carbon_ind) + '_Ren_extra_phase_correction_list']/180.*np.pi

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

            if i!= 0:
                g.C_phases_before_gate = Gate_sequence[i-1].C_phases_after_gate

            if g.el_state_after_gate == None:
                g.el_state_after_gate = g.el_state_before_gate

            ###########################
            ### Decoupling elements ###
            ###########################

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

                    elif g.C_phases_after_gate[iC] == None:
                        g.C_phases_after_gate[iC] = np.mod(g.C_phases_before_gate[iC]+(2*g.tau*g.N)*C_freq[iC],  2*np.pi)
                        
                    if g.C_phases_after_gate[iC] != None:
                        g.C_phases_after_gate[iC] += g.extra_phase_correction_list[iC]

            elif g.Gate_type =='electron_decoupling':

                for iC in range(len(g.C_phases_before_gate)):
                    if g.C_phases_after_gate[iC] == None:
                        g.C_phases_after_gate[iC] = (g.C_phases_before_gate[iC]+ (2*g.tau*g.N)*C_freq[iC])%(2*np.pi)

            #######################
            # Connecting elements #
            #######################

            elif g.Gate_type == 'Connection_element' or g.Gate_type == 'electron_Gate':
                if i == len(Gate_sequence)-1:
                    g.dec_duration = 0
                elif Gate_sequence[i+1].phase == None or Gate_sequence[i+1].phase == 'reset':
                    g.dec_duration =0
                else:
                    desired_phase = Gate_sequence[i+1].phase/180.*np.pi
                    Carbon_index  = Gate_sequence[i+1].Carbon_ind
                    if g.C_phases_before_gate[Carbon_index] == None:
                        g.dec_duration = 0
                    else:
                        phase_diff =(desired_phase - g.C_phases_before_gate[Carbon_index])%(2*np.pi)
                        if ( (phase_diff <= (self.params['min_phase_correct']/180.*np.pi)) or
                                (abs(phase_diff -2*np.pi) <=  (self.params['min_phase_correct']/180.*np.pi)) ):
                        # For very small phase differences correcting phase with decoupling introduces a larger error
                        #  than the phase difference error.

                            g.dec_duration = 0
                        else:
                            g.dec_duration =(round( phase_diff/C_freq[Carbon_index]
                                    *1e9/(self.params['dec_pulse_multiple']*2))
                                    *(self.params['dec_pulse_multiple']*2)*1e-9)
                            while g.dec_duration <= self.params['min_dec_duration']:
                                phase_diff = phase_diff +2*np.pi
                                g.dec_duration =(round( phase_diff/C_freq[Carbon_index]
                                        *1e9/(self.params['dec_pulse_multiple']*2))
                                        *(self.params['dec_pulse_multiple']*2)*1e-9)
                            g.dec_duration = g.dec_duration

                for iC in range(len(g.C_phases_before_gate)):
                    if (g.C_phases_after_gate[iC] == None) and (g.C_phases_before_gate[iC] !=None) :
                        g.C_phases_after_gate[iC] = (g.C_phases_before_gate[iC]+ g.dec_duration*C_freq[iC])%(2*np.pi)

            #########
            # Special elements
            #########

            elif g.Gate_type =='passive_elt':
                for iC in range(len(g.C_phases_before_gate)):
                    if (g.C_phases_after_gate[iC] == None) and (g.C_phases_before_gate[iC] !=None):
                        if g.el_state_before_gate == '0':
                            g.C_phases_after_gate[iC] = (g.C_phases_before_gate[iC] + g.wait_time*C_freq_0[iC])%(2*np.pi)
                        elif g.el_state_before_gate == '1':
                            g.C_phases_after_gate[iC] = (g.C_phases_before_gate[iC] + g.wait_time*C_freq_1[iC])%(2*np.pi)
                        elif g.el_state_before_gate == 'sup':
                            g.C_phases_after_gate[iC] = (g.C_phases_before_gate[iC])%(2*np.pi)
                            print 'Warning: %s, el state in sup for passive elt' %g.name
            
            elif g.Gate_type=='Trigger':
                for iC in range(len(g.C_phases_before_gate)):
                    if (g.C_phases_after_gate[iC] == None) and (g.C_phases_before_gate[iC] !=None):
                        if g.el_state_before_gate == '0':
                            print 'Calculating phase for gate %s for el_state == 0 ' %g.name
                            g.C_phases_after_gate[iC] = (g.C_phases_before_gate[iC] + g.elements_duration*C_freq_0[iC])%(2*np.pi)
                        elif g.el_state_before_gate == '1':
                            print 'Calculating phase for gate %s for el_state == 1 ' %g.name
                            g.C_phases_after_gate[iC] = (g.C_phases_before_gate[iC] + g.elements_duration*C_freq_1[iC])%(2*np.pi)
                        elif g.el_state_before_gate == 'sup':
                            g.C_phases_before_gate[iC]%(2*np.pi)
                            print 'Warning: %s, el state in sup for Trigger elt' %g.name
            
            elif g.Gate_type =='MBI':
                for iC in range(len(g.C_phases_before_gate)):
                    # The MBI element is always first and should not have anything to do with C_phases
                    if g.C_phases_after_gate[iC] ==None:
                        g.C_phases_after_gate[iC] = g.C_phases_before_gate[iC]

            # elif g.Gate_type =='electron_repump':
            #     for iC in range(len(g.C_phases_before_gate)):
            #         if (g.C_phases_after_gate[iC]==None) and (g.C_phases_before_gate[iC] !=None):
            #             if g.el_state_before_gate =='0':
            #                 g.C_phases_after_gate[iC]=(g.C_phases_before_gate[iC]+g.elements_duration*C_freq_0[iC])%(2*np.pi)
            #             elif g.el_state_before_gate=='1':
            #                 print 'calculating repump correction for the electronic state in ms=-1'
            #                 g.C_phases_after_gate[iC]=(g.C_phases_before_gate[iC]+(g.elements_duration-g.)*C_freq_0[iC])%(2*np.pi)
            

            else: # I want the program to spit out an error if I messed up i.e. forgot a gate type
                print 'Error: %s, Gate type not recognized %s' %(g.name,g.Gate_type)


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
        Gate.reps = N # Overwrites reps parameter that is used in sequencing
        prefix    = Gate.prefix

        ### Generate the basic X and Y pulses
        X = self._X_elt()
        Y = self._Y_elt()

        ### Select scheme for generating decoupling elements
        if N==0 or Gate.scheme =='auto':
            Gate = self.determine_decoupling_scheme(Gate)

        ###################
        ## Set paramters ##
        ###################

        tau_cut                 = 0             #initial value unless overwritten
        minimum_AWG_elementsize = 1e-6          #AWG elements/waveforms have to be 1 mu s
        fast_pi_duration        = self.params['fast_pi_duration']
        pulse_tau               = tau - fast_pi_duration/2.0 
        tau_prnt                = int(tau*1e9)  #Converts tau to ns for printing
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


            initial_pulse = pulselib.MW_IQmod_pulse('electron Pi/2-pulse',
                I_channel   ='MW_Imod', Q_channel='MW_Qmod',
                PM_channel  ='MW_pulsemod',
                frequency   = self.params['fast_pi2_mod_frq'],
                PM_risetime = self.params['MW_pulse_mod_risetime'],
                length      = self.params['fast_pi2_duration'],
                amplitude   = self.params['fast_pi2_amp'],
                phase       =initial_phase)
            final_pulse = pulselib.MW_IQmod_pulse('electron Pi/2-pulse',
                I_channel   ='MW_Imod', Q_channel='MW_Qmod',
                PM_channel  ='MW_pulsemod',
                frequency   = self.params['fast_pi2_mod_frq'],
                PM_risetime = self.params['MW_pulse_mod_risetime'],
                length      = self.params['fast_pi2_duration'],
                amplitude   = self.params['fast_pi2_amp'],
                phase       = final_phase)
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
            for n in range(N) :
                if n !=0:
                    decoupling_elt.append(T)
                if n%8 in x_list:
                    decoupling_elt.append(X)
                else:
                    decoupling_elt.append(Y)
                if n !=N-1:
                    decoupling_elt.append(T)

            decoupling_elt.append(T_around_pi2)
            decoupling_elt.append(final_pulse)
            decoupling_elt.append(T_around_pi2)
            list_of_elements.append(decoupling_elt)

        ################################
        ### XYn with repeating T elt ###
        ################################
        elif Gate.scheme == 'repeating_T_elt':

            ### Calculate durations

            n_wait_reps, tau_remaind = divmod(round(2*pulse_tau*1e9),1e3) #multiplying and round is to prevent rounding errors in divmod
            tau_remaind              = tau_remaind*1e-9
            
            if tau_remaind/2 < 36e-9: ## TODO: This should really depend on the pulse mod length and offset
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

            ### Correct for part that is cut of when combining to sequence
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

            final_x_list = [0,1,2,7]
            if N%8 in final_x_list:
                final_pulse = X
                P_type = 'X'
            else:
                final_pulse = Y
                P_type = 'Y'

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
        
        pulse_tau       = tau-self.params['fast_pi_duration']/2.0

        X = self._X_elt()
        Y = self._Y_elt()
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
            elif Gate.Gate_operation == 'general':      ### Added to make possible electron pulses with different amplitudes and phases
                eP = self._electron_pulse_elt(length = Gate.length, amplitude = Gate.amplitude)
            eP.phase = Gate.phase

            T_initial = pulse.SquarePulse(channel='MW_Imod', name='wait in T',
                length = tau_cut_before-(eP.length-2*self.params['MW_pulse_mod_risetime'])/2.0, amplitude = 0.)
            T_dec_initial = pulse.SquarePulse(channel='MW_Imod', name='wait in T',
                length = pulse_tau-(eP.length-2*self.params['MW_pulse_mod_risetime'])/2.0, amplitude = 0.)
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
                length = tau_cut_after-(eP.length-2*self.params['MW_pulse_mod_risetime'])/2.0, amplitude = 0.) #Overwrite length of T_final element

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

            for n in range(N) :

                if n%8 in x_list:
                    decoupling_elt.append(X)
                else:
                    decoupling_elt.append(Y)
                decoupling_elt.append(T)
                if n !=(N-1):
                    decoupling_elt.append(T)
            decoupling_elt.append(T_final)
        Gate.elements = [decoupling_elt]

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

            X = pulselib.MW_IQmod_pulse('electron Pi/2-pulse',
                I_channel='MW_Imod', Q_channel='MW_Qmod',
                PM_channel='MW_pulsemod',
                frequency = self.params['fast_pi2_mod_frq'],
                PM_risetime = self.params['MW_pulse_mod_risetime'],
                length = self.params['fast_pi2_duration'],
                amplitude = self.params['fast_pi2_amp'],
                phase=self.params['X_phase'])

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

            X = pulselib.MW_IQmod_pulse('electron Pi/2-pulse',
                I_channel='MW_Imod', Q_channel='MW_Qmod',
                PM_channel='MW_pulsemod',
                frequency = self.params['fast_pi2_mod_frq'],
                PM_risetime = self.params['MW_pulse_mod_risetime'],
                length = self.params['fast_pi2_duration'],
                amplitude = self.params['fast_pi2_amp'],
                phase = self.params['X_phase']+180)
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

            X = pulselib.MW_IQmod_pulse('electron Pi-pulse',
                I_channel='MW_Imod', Q_channel='MW_Qmod',
                PM_channel='MW_pulsemod',
                frequency = self.params['fast_pi_mod_frq'],
                PM_risetime = self.params['MW_pulse_mod_risetime'],
                length = self.params['fast_pi_duration'],
                amplitude = self.params['fast_pi_amp'])
            T_before_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = time_before_pulse, amplitude = 0.)
            T_after_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = time_after_pulse, amplitude = 0.)

            e = element.Element('%s_Pi_pulse' %(prefix),  pulsar=qt.pulsar,
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
        Gate_type, duration, repump_power,
        '''

        Gate_type = Gate.Gate_type
        power= Gate.repump_power
        duration= Gate.duration

        repump_pulse=pulse.SquarePulse(channel='AOM_Newfocus', length=duration, name='electron_repump', amplitude=1.)
        AOM_delay=pulse.SquarePulse(channel='AOM_Newfocus', length=qt.pulsar.channels['AOM_Newfocus']['delay'], name='wait_AOM_delay', amplitude=0.)
        
        e = element.Element('%s_electron_repump' %(Gate_type),  pulsar=qt.pulsar, global_time = True)
        e.append(repump_pulse)
        e.append(AOM_delay)

        Gate.elements=[e]

        #qt.pulsar.define_channel(id='ch2_marker1', name='AOM_Newfocus', type='marker',
        #high=0.4, low=0.0, offset=0., delay=466e-9, active=True)

        #TODO for other functions in the DD class:
        # - add this gate type in track_and_calc_phase such that the phase get's accurately detected.
        # - add calculation for the repump power and put it into the generation of the marker trigger.

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
            seq.append(name=str(mbi_elt.name+gate_seq[0].elements[0].name),
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
                    seq.append(name=st.name, wfname=t.name,
                        trigger_wait=gate.wait_for_trigger,
                        repetitions = red_wait_reps)#floor divisor
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
            else:
                print 'Gate %s not added, scheme = %s' %(gate.name,gate.scheme)
        if explicit == False:
            trig_elt = self._Trigger_element()
            list_of_elements.append(trig_elt)
            seq.append(name=str(trig_elt.name+e.name), wfname=trig_elt.name,
                            trigger_wait=False,repetitions = 1)


        return list_of_elements, seq

    ### elements generation
    def generate_AWG_elements(self,Gate_sequence,pt = 1):

        for g in Gate_sequence:
            if g.Gate_type =='Carbon_Gate' or g.Gate_type =='electron_decoupling':
                self.get_gate_parameters(g)
                self.generate_decoupling_sequence_elements(g)
            elif g.Gate_type =='passive_elt':
                self.generate_passive_wait_element(g)
            elif g.Gate_type == 'MBI':
                self.generate_MBI_elt(g)
            elif g.Gate_type == 'Trigger':
                self.generate_trigger_elt(g)
            elif g.Gate_type == 'electron_repump':
                self.generate_electron_repump_element(g)

        Gate_sequence = self.insert_phase_gates(Gate_sequence,pt)
        self.get_tau_cut_for_connecting_elts(Gate_sequence)
        self.track_and_calc_phase(Gate_sequence)
        for g in Gate_sequence:
            if (g.Gate_type == 'Connection_element' or g.Gate_type == 'electron_Gate'):
                self.determine_connection_element_parameters(g)
                self.generate_connection_element(g)

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

            Ren_a.N = self.params['C_Ren_N']
            Ren_a.tau = self.params['C_Ren_tau']
            Ren_a.scheme = self.params['Decoupling_sequence_scheme']
            Ren_a.prefix = 'Ren_a'+str(pt)

            Ren_b.N = self.params['C_Ren_N']
            Ren_b.tau = self.params['C_Ren_tau']
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

class LongNuclearRamsey(DynamicalDecoupling):
    '''
    The NuclearRamsey class performs a ramsey experiment on a nuclear spin that is resonantly controlled using a decoupling sequence.
    This version varies the duration of the DynamicalDecoupling wait time and then tries to keep the phase fixed based on the Carbon
        precession_freq found in the msmt
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

        for pt in range(pts):


            ###########################################
            #####    Generating the sequence elements      ######

            ###########################################
            initial_Pi2 = Gate('initial_pi2','electron_Gate')
            simple_el_dec = Gate('electron_decoupling', 'Carbon_Gate')
            final_Pi2 = Gate('final_pi2','electron_Gate')

            gate_seq = [initial_Pi2,simple_el_dec,final_Pi2]
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
            else:
                #Generate the start and end pulse
                initial_Pi2.Gate_operation = self.params['Initial_Pulse']
                initial_Pi2.time_before_pulse = max(1e-6 -  simple_el_dec.tau_cut + 36e-9,44e-9)
                initial_Pi2.time_after_pulse = simple_el_dec.tau_cut
                initial_Pi2.prefix = 'init_pi2_'+str(pt)#to ensure unique naming


                final_Pi2.time_before_pulse =simple_el_dec.tau_cut
                final_Pi2.time_after_pulse = initial_Pi2.time_before_pulse
                final_Pi2.Gate_operation = self.params['Final_Pulse']
                final_Pi2.prefix = 'fin_pi2_'+str(pt) #to ensure unique naming

                #Generate the start and end pulse
                self.generate_electron_gate_element(initial_Pi2)
                self.generate_electron_gate_element(final_Pi2)

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
    def initialize_carbon_sequence(self,
            prefix                  = 'init_C',
            go_to_element           = 'MBI_1',
            wait_for_trigger        = True,
            initialization_method   = 'swap',
            pt                      = 1,
            addressed_carbon        = 1,
            C_init_state            = 'up',
            el_RO_result            = '0',
            el_after_init           = '0'):
        
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
        C_init_y = Gate(prefix+str(addressed_carbon)+'_y_'+str(pt),'electron_Gate',
                Gate_operation ='pi2',
                wait_for_trigger = wait_for_trigger,
                phase = C_init_y_phase)

        C_init_Ren_a = Gate(prefix+str(addressed_carbon)+'_Ren_a_'+str(pt), 'Carbon_Gate',
                Carbon_ind = addressed_carbon,
                phase = self.params['C13_X_phase'])

        C_init_x = Gate(prefix+str(addressed_carbon)+'_x_'+str(pt),'electron_Gate',
                Gate_operation='pi2',
                phase = self.params['X_phase'])
       
        C_init_Ren_b = Gate(prefix+str(addressed_carbon)+'_Ren_b_'+str(pt), 'Carbon_Gate',
                Carbon_ind = addressed_carbon,
                phase = self.params['C13_Y_phase']+180)

        C_init_RO_Trigger = Gate(prefix+str(addressed_carbon)+'_RO_trig_'+str(pt),'Trigger',
                wait_time= self.params['Carbon_init_RO_wait'],
                event_jump = 'next',
                go_to = go_to_element,
                el_state_before_gate = el_RO_result)

        ## TODO: THT, temporary fix that removed pi-puls that is bugged 
        C_init_elec_X = Gate(prefix+str(addressed_carbon)+'_elec_X'+str(pt),'electron_Gate',
                Gate_operation='pi',
                phase = self.params['X_phase'],
                el_state_after_gate = '1')

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
        if el_after_init =='1':
            carbon_init_seq.append(C_init_elec_X)

        return carbon_init_seq

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



    def readout_multiple_carbon_sequence(self,
            prefix = 'C_pRO',
            go_to_element ='next',event_jump_element = 'next',
            RO_duration = 10e-6,
            pt = 1,
            addressed_carbon =[1,4],
            RO_Z=[False,True],
            RO_phase = [0,0],
            el_RO_result = '0' ):
            #electron_RO_phase = 'positive',

        ''' Old, replaced by readout_carbon_sequence, remove and upgrade measurements that use this'''


        '''
        TODO_MAR: Finish readout multiple carbon sequence

        Creates a single carbon readout gate sequence.
        Does a readout an a single Carbon.

        Base to readout can be specified by
        RO_Z True or False
        RO_phase  in degress

        By setting RO_phase = None, for one of the two carbons to be None, that carbon will not be read out.
        Instead the fucntion readout_single_carbon_sequence is called to read out the other carbon. This allows to perform ex the IX parity measurement.

        In the case where this function is used to do conditional feed forward the following parameters have to be specified
        RO_duration:  this is the lenght of the trigger and states how long the trigger waits for a 'click' from the adwin
        go_to_element: determines where to go when no 'click' comes from the adwin.
        event_jump_element: determines where to jump to when a 'click' comes from the adwin.

        all elements for this sequence start with C_pRO_ as a prefix. where pRO stands for parity  Readout

        NOTE: If used for branching, el_RO_result has to be manually overwritten when generating phase correction for different branches.
        '''




        if (type(go_to_element) != str) and (go_to_element != None):
            go_to_element = go_to_element.name

        if  RO_phase[0] == None and  RO_phase[1] == None:
            print 'NO Carbon selected for readout, No sequence could be generated. in function: readout_multiple_carbon_sequence '

        elif RO_phase[0] == None:
            carbon_RO_seq = self.readout_single_carbon_sequence(prefix=prefix,
            go_to_element =go_to_element,event_jump_element = event_jump_element,
            RO_duration = RO_duration,
            pt = pt, addressed_carbon =addressed_carbon[1],
            RO_Z=RO_Z[1], RO_phase =RO_phase[1],
            el_RO_result = el_RO_result )
            return carbon_RO_seq

        elif RO_phase[1] == None:
            carbon_RO_seq = self.readout_single_carbon_sequence(prefix = prefix,
            go_to_element =go_to_element,event_jump_element = event_jump_element,
            RO_duration = RO_duration,
            pt = pt, addressed_carbon =addressed_carbon[0],
            RO_Z=RO_Z[0],RO_phase =RO_phase[0],
            el_RO_result = el_RO_result )
            return carbon_RO_seq


        C_pRO_x_a = Gate(prefix+str(addressed_carbon[0])+'_x_'+str(pt), 'Carbon_Gate',
            Carbon_ind = addressed_carbon[0], phase = RO_phase[0])
        C_pRO_x_b = Gate(prefix+str(addressed_carbon[1])+'_x_'+str(pt), 'Carbon_Gate',
            Carbon_ind = addressed_carbon[1], phase = RO_phase[1])

        C_pRO_init_pi2 = Gate(prefix+'_pi2_a'+str(pt),'electron_Gate',
                Gate_operation='pi2',
                phase = self.params['X_phase'])

        C_pRO_Ren_a = Gate(prefix+str(addressed_carbon[0])+'_Ren_'+str(pt), 'Carbon_Gate',
            Carbon_ind = addressed_carbon[0], phase = RO_phase[0])
        C_pRO_Ren_b = Gate(prefix+str(addressed_carbon[1])+'_Ren_'+str(pt), 'Carbon_Gate',
            Carbon_ind = addressed_carbon[1], phase = RO_phase[1])

        #if electron_RO_phase == 'positive':
        final_el_phase = self.params['X_phase']
        #elif electron_RO_phase == 'negative':
        #    final_el_phase = -1*self.params['X_phase']

        C_pRO_fin_pi2 = Gate(prefix+'_pi2_b'+str(pt),'electron_Gate',
                Gate_operation='pi2',
                phase = final_el_phase)

        C_pRO_Trigger = Gate(prefix+'_Trigger_'+str(pt),'Trigger',
                wait_time = RO_duration,
                go_to = go_to_element, event_jump = event_jump_element,
                el_state_before_gate = el_RO_result)

        if RO_Z[0] == True and RO_Z[1] ==True:
            C_pRO_Ren_a.phase = RO_phase[0]+90  #this is dangerous, because resetting the phase does not recalcuate phase_after_gate
            C_pRO_Ren_b.phase = RO_phase[1]+90  #this is dangerous, because resetting the phase does not recalcuate phase_after_gate
            carbon_pRO_seq = [C_pRO_x_a,C_pRO_x_b,C_pRO_init_pi2,C_pRO_Ren_a,C_pRO_Ren_b,C_pRO_fin_pi2,C_pRO_Trigger]
        elif RO_Z[0] == True:
            C_pRO_Ren_a.phase = RO_phase[0]+90
            carbon_pRO_seq = [C_pRO_x_a,C_pRO_init_pi2,C_pRO_Ren_a,C_pRO_Ren_b,C_pRO_fin_pi2,C_pRO_Trigger]
        elif RO_Z[1] == True:
            C_pRO_Ren_b.phase = RO_phase[1]+90
            carbon_pRO_seq = [C_pRO_x_b,C_pRO_init_pi2,C_pRO_Ren_a,C_pRO_Ren_b,C_pRO_fin_pi2,C_pRO_Trigger]
        elif RO_Z[0] == False and RO_Z[1] ==False:
            carbon_pRO_seq = [C_pRO_init_pi2,C_pRO_Ren_a,C_pRO_Ren_b,C_pRO_fin_pi2,C_pRO_Trigger]
        return carbon_pRO_seq

    def multi_qubit_tomography(self,
            prefix = 'Tomo',
            go_to_element='next',
            event_jump_element = 'next',
            RO_duration=10e-6,
            pt = 1,
            addressed_carbon = [1,2],
            RO_bases =['X','Y'],
            electron_RO_phase = 'positive',
            el_RO_result = '0'):
        
        ''' Old, replaced by readout_carbon_sequence, remove and upgrade measurements that use this'''


        '''
        Uses the readout_multiple_carbon_sequence function to generate a multi qubit tomography sequence
        NOTE: the multi_qubit_tomography function currently only supports 2 qubit tomography sequences
        '''
        RO_Z =[None] *len(addressed_carbon)
        RO_phase = [None] *len(addressed_carbon)
        len(addressed_carbon)

        for i in range(len(addressed_carbon)):


            if RO_bases[i] == 'I':
                RO_Z[i] =False
                RO_phase[i] = None

            elif RO_bases[i] =='X':
                RO_Z[i] = False
                RO_phase[i] = self.params['C13_X_phase']

            elif RO_bases[i] =='-X':
                RO_Z[i] = False
                RO_phase[i] = self.params['C13_X_phase'] + 180

            elif RO_bases[i] == 'Y':
                RO_Z[i] = False
                RO_phase[i] = self.params['C13_Y_phase']

            elif RO_bases[i] == '-Y':
                RO_Z[i] = False
                RO_phase[i] = self.params['C13_Y_phase'] + 180

            elif RO_bases[i] == 'Z':
                RO_Z[i] = True
                RO_phase[i] = 0

        carbon_tomo_seq=self.readout_multiple_carbon_sequence( prefix = prefix,
            go_to_element =go_to_element,
            event_jump_element =event_jump_element,
            RO_duration =RO_duration,
            pt = pt,
            addressed_carbon =addressed_carbon,
            RO_Z=RO_Z,
            RO_phase = RO_phase,
            el_RO_result = el_RO_result)
            # electron_RO_phase = electron_RO_phase,
        print 'Tomography function called on carbons %s to read out bases %s, using phase %s and Z-RO %s' %(addressed_carbon,RO_bases,RO_phase,RO_Z)

        return carbon_tomo_seq

    def readout_carbon_sequence(self,
        prefix              = 'C_RO',
        pt                  =  1,
        carbon_list         = [1, 4],
        RO_basis_list       = ['X','X'],
        RO_trigger_duration = 116e-6,
        el_RO_result         = '0',
        go_to_element       = 'next', event_jump_element = 'next',
        readout_orientation = 'positive'):

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
                        
        ### Add initial pi/2 pulse (always) ###
        carbon_RO_seq.append(
                Gate(prefix+'_y_pi2_init'+str(pt),'electron_Gate',
                Gate_operation='pi2',
                phase = self.params['Y_phase']))

        ### Add RO rotations ###
        for kk, carbon_nr in enumerate(carbon_list):

                     
            if RO_basis_list[kk] != 'I':
               
                ### Determine the RO_phase
                if RO_basis_list[kk] == 'X':
                    RO_phase = self.params['C13_X_phase']
                elif RO_basis_list[kk] == '-X':
                    RO_phase = self.params['C13_X_phase']+180
                elif RO_basis_list[kk] == 'Y' or RO_basis_list[kk] == '-Z':
                    RO_phase = self.params['C13_Y_phase']
                elif RO_basis_list[kk] == '-Y' or RO_basis_list[kk] == 'Z':
                    RO_phase = self.params['C13_Y_phase']+180
                else:
                    RO_phase = RO_basis_list[kk] 


                carbon_RO_seq.append(
                        Gate(prefix + str(carbon_nr) + '_Ren_b_' + str(pt), 'Carbon_Gate',
                        Carbon_ind = carbon_nr,
                        phase = RO_phase))

        ### Add final pi/2 and Trigger ###
            ### set the final electron pi2 pulse phase depending on the number of qubits RO (4 options)
        Final_pi2_pulse_phase = np.mod((180+self.params['Y_phase']) - np.mod(number_of_carbons_to_RO, 4) * 90, 360)
        Final_pi2_pulse_phase_negative = np.mod(Final_pi2_pulse_phase+180,360)
        
        print Final_pi2_pulse_phase
       
        if readout_orientation == 'positive':
            carbon_RO_seq.append(
                    Gate(prefix+'_pi2_final_phase=' +str(Final_pi2_pulse_phase) + '_' +str(pt),'electron_Gate',
                    Gate_operation='pi2',
                    phase = Final_pi2_pulse_phase))
        elif readout_orientation == 'negative':
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
        phase_error         = 0):
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
        print 'logic_init'
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
                    Gate(prefix+'_X_pi_init'+str(pt),'electron_Gate',
                    Gate_operation='pi',
                    phase = self.params['X_phase']))
        elif logic_state == 'X':
            carbon_RO_seq.append(
                    Gate(prefix+'_-y_pi2_init'+str(pt),'electron_Gate',
                    Gate_operation='pi2',
                    phase = self.params['Y_phase']+180))
        elif logic_state == 'mX':
            carbon_RO_seq.append(
                    Gate(prefix+'_y_pi2_init'+str(pt),'electron_Gate',
                    Gate_operation='pi2',
                    phase = self.params['Y_phase']))
        elif logic_state == 'Y':
            carbon_RO_seq.append(
                    Gate(prefix+'_x_pi2_init'+str(pt),'electron_Gate',
                    Gate_operation='pi2',
                    phase = self.params['X_phase']))
        elif logic_state == 'mY':
            carbon_RO_seq.append(
                    Gate(prefix+'_-x_pi2_init'+str(pt),'electron_Gate',
                    Gate_operation='pi2',
                    phase = self.params['X_phase']+180))

        ### Add RO rotations ###
        for kk, carbon_nr in enumerate(carbon_list):

                     
            if RO_basis_list[kk] != 'I':
               
                ### Determine the RO_phase
                if RO_basis_list[kk] == 'X':
                    RO_phase = self.params['C13_X_phase']+phase_error
                elif RO_basis_list[kk] == '-X':
                    RO_phase = self.params['C13_X_phase']+180+phase_error
                elif RO_basis_list[kk] == 'Y' or RO_basis_list[kk] == '-Z':
                    RO_phase = self.params['C13_Y_phase']+phase_error
                elif RO_basis_list[kk] == '-Y' or RO_basis_list[kk] == 'Z':
                    RO_phase = self.params['C13_Y_phase']+180+phase_error
                else:
                    RO_phase = RO_basis_list[kk] 
                print 'RO_phase'
                print RO_phase
                print phase_error

                carbon_RO_seq.append(
                        Gate(prefix + str(carbon_nr) + '_Ren_b_' + str(pt), 'Carbon_Gate',
                        Carbon_ind = carbon_nr,
                        phase = RO_phase))

        ### Add final pi/2 and Trigger ###
       
        if readout_orientation == 'positive':
            carbon_RO_seq.append(
                    Gate(prefix+'_y_pi2_final' + '_' +str(pt),'electron_Gate',
                    Gate_operation='pi2',
                    phase = self.params['Y_phase']))
        elif readout_orientation == 'negative':
            carbon_RO_seq.append(
                    Gate(prefix+'_-y_pi2_final' + '_' +str(pt),'electron_Gate',
                    Gate_operation='pi2',
                    phase = self.params['Y_phase']+180))    

        carbon_RO_seq.append(
                Gate(prefix+'_Trigger_'+str(pt),'Trigger',
                wait_time = RO_trigger_duration,
                go_to = go_to_element, event_jump = event_jump_element,
                el_state_before_gate = el_RO_result))

        return carbon_RO_seq
### Single Carbon initialization classes ###

class NuclearRamseyWithInitialization_v2(MBI_C13):
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

        for pt in range(pts): ### Sweep over trigger time (= wait time)
            gate_seq = []

            ### Nitrogen MBI
            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]; gate_seq.extend(mbi_seq)

            ### Carbon initialization
            carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                prefix = 'C_MBI_',
                wait_for_trigger      = True, pt =pt,
                initialization_method = 'MBI',
                C_init_state          = self.params['init_state'],
                addressed_carbon      = self.params['carbon_nr'],
                el_RO_result          = str(self.params['C13_MBI_RO_state']))
            gate_seq.extend(carbon_init_seq)

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

            carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                    initialization_method = 'swap', pt =pt,
                    addressed_carbon= self.params['Addressed_Carbon'],
                    C_init_state = self.params['C13_init_state'],
                    el_RO_result = '0' )
            ################################

            C_Rabi_Ren = Gate('C_Rabi_Ren'+str(pt), 'Carbon_Gate',
                    Carbon_ind = self.params['Addressed_Carbon'],
                    N = self.params['Rabi_N_Sweep'][pt],
                    phase = self.params['C13_X_phase'])

            C_evol_seq =[C_Rabi_Ren]
            #############################

            carbon_RO_seq = self.readout_single_carbon_sequence(self,
                    pt = pt, addressed_carbon =self.params['Addressed_Carbon'],
                    RO_Z=False,
                    RO_phase = self.params['C13_Y_phase'],
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

class NuclearT1(MBI_C13):
    '''
    This class generates the AWG sequence for a C13 T1 experiment.
    1. MBI initialisation
    2. Carbon initialisation into +Z
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
                    el_RO_result = str(self.params['C13_MBI_RO_state']),
                    el_after_init = str(self.params['el_after_init']))

            #Elements for T1 evolution

            wait_gate = Gate('Wait_gate_'+str(pt),'passive_elt',
                    wait_time = self.params['wait_times'][pt]-self.params['Carbon_init_RO_wait'])

            C_evol_seq =[wait_gate]

            #############################
            #Readout in the Z basis
            # print 'ro phase = ' + str( self.params['C_RO_phase'][pt])

            #TODO make the read-out use the general Carbon RO sequencer function NK 20141104

            if self.params['electron_readout_orientation'] == 'positive':
                extra_phase = 0
            elif self.params['electron_readout_orientation'] == 'negative':
                 extra_phase = 180

            C_basis_Ren = Gate('C_basis_Ren'+str(pt), 'Carbon_Gate',
                    Carbon_ind = self.params['Addressed_Carbon'],
                    phase = 'reset')

            C_RO_y = Gate('C_ROy_'+str(pt),'electron_Gate',
                    Gate_operation='pi2',
                    phase = self.params['Y_phase']+extra_phase)
            C_RO_Ren = Gate('C_RO_Ren_'+str(pt), 'Carbon_Gate',
                    Carbon_ind = self.params['Addressed_Carbon'],
                    phase = self.params['C13_Y_phase']+180)
            C_RO_x = Gate('C_RO_x_'+str(pt),'electron_Gate',
                    Gate_operation='pi2',
                    phase = self.params['X_phase'])
            C_RO_Trigger = Gate('C_RO_Trigger_'+str(pt),'Trigger')

            carbon_RO_seq =[C_basis_Ren, C_RO_y, C_RO_Ren, C_RO_x, C_RO_Trigger]

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

### Multiple carbon initialization classes ###

class Two_QB_Probabilistic_MBE_v3(MBI_C13):
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
                    readout_orientation = self.params['electron_readout_orientation_0'])
            gate_seq0.extend(carbon_tomo_seq0)

            carbon_tomo_seq1 = self.readout_carbon_sequence(
                    prefix              = 'Tomo1',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomography Bases_1'][pt],
                    readout_orientation = self.params['electron_readout_orientation_1'])
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
                print '3C_init_'
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

class Three_QB_QEC(MBI_C13):
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
                print '3C_init_'
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
                        readout_orientation = 'positive',
                        phase_error         = self.params['phase_error'][pt])

                gate_seq.extend(probabilistic_MBE_seq)

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


            ### Create logical state 

            for kk in range(self.params['Nr_MBE']):
                print '3C_init_'
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
                        readout_orientation = 'positive',
                        phase_error         = self.params['phase_error'][pt])           

                gate_seq.extend(probabilistic_MBE_seq)

            ### Parity msmt 1
            Parity_seq_a = self.readout_carbon_sequence(
                        prefix              = 'Parity_a' + str(kk+1),
                        pt                  = pt,
                        RO_trigger_duration = 150e-6,
                        carbon_list         = self.params['Parity_a_carbon_list'],
                        RO_basis_list       = self.params['Parity_a_carbon_list'],
                        el_RO_result         = '0')

            gate_seq.extend(Parity_seq_a)

            #############################
            gate_seq0 = copy.deepcopy(gate_seq)
            gate_seq1 = copy.deepcopy(gate_seq)

             ### Parity msmt 1
            Parity_seq_b0 = self.readout_carbon_sequence(
                        prefix              = 'Parity_b0' + str(kk+1),
                        pt                  = pt,
                        RO_trigger_duration = 150e-6,
                        carbon_list         = self.params['Parity_b_carbon_list'],
                        RO_basis_list       = self.params['Parity_b_carbon_list'],
                        el_RO_result         = '0')

            Parity_seq_b1 = self.readout_carbon_sequence(
                        prefix              = 'Parity_b1' + str(kk+1),
                        pt                  = pt,
                        RO_trigger_duration = 150e-6,
                        carbon_list         = self.params['Parity_b_carbon_list'],
                        RO_basis_list       = self.params['Parity_b_carbon_list'],
                        el_RO_result         = '0')                                

            gate_seq0.extend(Parity_seq_b0)
            gate_seq1.extend(Parity_seq_b1)

            gate_seq00 = copy.deepcopy(gate_seq0)
            gate_seq01 = copy.deepcopy(gate_seq0)
            gate_seq10 = copy.deepcopy(gate_seq1)
            gate_seq11 = copy.deepcopy(gate_seq1)           

            carbon_tomo_seq00 = self.readout_carbon_sequence(
                    prefix              = 'Tomo00',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomography Bases_00'],
                    readout_orientation = self.params['electron_readout_orientation_00'])
            
            gate_seq00.extend(carbon_tomo_seq00)

            carbon_tomo_seq01 = self.readout_carbon_sequence(
                    prefix              = 'Tomo01',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomography Bases_01'],
                    readout_orientation = self.params['electron_readout_orientation_01'])
            gate_seq01.extend(carbon_tomo_seq01)

            carbon_tomo_seq10 = self.readout_carbon_sequence(
                    prefix              = 'Tomo10',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomography Bases_10'],
                    readout_orientation = self.params['electron_readout_orientation_10'])
            gate_seq10.extend(carbon_tomo_seq10)

            carbon_tomo_seq11 = self.readout_carbon_sequence(
                    prefix              = 'Tomo11',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomography Bases_11'],
                    readout_orientation = self.params['electron_readout_orientation_11'])
            gate_seq11.extend(carbon_tomo_seq11)

            # Make jump statements for branching to two different ROs
            Parity_seq_a[-1].go_to       = Parity_seq_b0[0].name
            Parity_seq_a[-1].event_jump  = Parity_seq_b1[0].name

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

            gate_seq  = self.generate_AWG_elements(gate_seq,pt)

            print 'generating elements for seq 00'
            gate_seq00[len(gate_seq)-2].el_state_before_gate =  '0' #Element -2, because MBI was added in generate AWG elements
            gate_seq00[len(gate_seq0)-2].el_state_before_gate = '0' #Element -2
            gate_seq00 = self.generate_AWG_elements(gate_seq00,pt)

            print 'generating elements for seq 01'
            gate_seq01[len(gate_seq)-2].el_state_before_gate =  '0' #Element -2, because MBI was added in generate AWG elements
            gate_seq01[len(gate_seq0)-2].el_state_before_gate = '1' #Element -2
            gate_seq01 = self.generate_AWG_elements(gate_seq01,pt)
            
            print 'generating elements for seq 10'
            gate_seq10[len(gate_seq)-2].el_state_before_gate =  '1' #Element -2, because MBI was added in generate AWG elements
            gate_seq10[len(gate_seq1)-2].el_state_before_gate = '0' #Element -2
            gate_seq10 = self.generate_AWG_elements(gate_seq00,pt)

            print 'generating elements for seq 11'
            gate_seq11[len(gate_seq)-2].el_state_before_gate =  '1' #Element -2, because MBI was added in generate AWG elements
            gate_seq11[len(gate_seq1)-2].el_state_before_gate = '1' #Element -2
            gate_seq11 = self.generate_AWG_elements(gate_seq00,pt)

            # Merge the bracnhes into one AWG sequence
            merged_sequence = []
            merged_sequence.extend(gate_seq)                  #TODO: remove gate_seq and add gate_seq1 to gate_seq0 without common part
            merged_sequence.extend(gate_seq00[len(gate_seq):])
            merged_sequence.extend(gate_seq01[len(gate_seq):])
            merged_sequence.extend(gate_seq10[len(gate_seq):])
            merged_sequence.extend(gate_seq11[len(gate_seq):])

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

