'''
Measurement classes
File made by Adriaan Rol
'''
import numpy as np
import qt
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


        self.name = name
        self.prefix = name     # Default prefix is identical to name, can be overwritten
        self.Gate_type = Gate_type
        '''
        Supported gate types in the scripts are
        connection/phase gates: 'Connection_element' , 'electron_Gate',
        decoupling gates:  'Carbon_Gate', 'electron_decoupling'
        misc gates: 'passive_elt', (also has tau_cut)
        special gates: 'mbi', 'Trigger'
        '''
        # Information on what type of gate to implement
        self.Carbon_ind = kw.pop('Carbon_ind',0)  #0 is the electronic spin, higher indices are the carbons
        self.phase = kw.pop('phase',0)

        #Scheme is used both for generating decoupling elements aaswell as the combine to sequence command
        if self.Gate_type in ['Connection_element','electron_Gate','passive_elt','mbi']:
            self.scheme = 'single_element'
        else:
            self.scheme = kw.pop('scheme','auto')

        #Information on how to implement the gate (times, repetitions etc)

        self.N = kw.pop('N',None)
        self.tau = kw.pop('tau',None)
        self.wait_time = kw.pop('wait_time',None)
        self.Gate_operation=kw.pop('Gate_operation',None)

        self.reps = kw.pop('reps',1) # only overwritten in case of Carbon decoupling elements

        self.dec_duration = kw.pop('dec_duration', None)  # can be specified if a custom dec duration is desired 

        # Information on how to combine the gates in the AWG.
        self.wait_for_trigger = kw.pop('wait_for_trigger',False)
        self.event_jump = kw.pop('event_jump',None)
        self.go_to = kw.pop('go_to',None)

        # Empty list of C_phases before gate
        self.C_phases_before_gate = [None]*10
        self.C_phases_after_gate = [None]*10
        self.el_state_before_gate = kw.pop('el_state_before_gate',None)
        self.el_state_after_gate = kw.pop('el_state_after_gate',None)
        if self.Gate_type =='Carbon_Gate' and self.C_phases_after_gate[self.Carbon_ind]!=None: 
            self.C_phases_after_gate[self.Carbon_ind] = self.phase/180.*np.pi 



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

        print 'Printing length of actual pi2 pulse %s' %pi2.length 
        print self.params['fast_pi2_duration']
        return pi2

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

    #functions for determining timing and what kind of elements to generate
    def get_gate_parameters(self,gate,resonance =0 ):
        '''
        Takes a gate object as input and uses the carbon index and the operation to determine tau and N from the msmt params
        Currently can only do single type of gate. Always does same amount of pulses
        '''
        ind = gate.Carbon_ind
        if ind ==0:
            #Don't take arguments from a list if it is not acting on a carbon (i.e. electron decoupling)
            return
        if gate.N==None:
            gate.N = self.params['C'+str(ind)+'_Ren_N'][resonance] #Needs to be added to msmt params
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
        gates_in_need_of_connecting_elts = ['Carbon_Gate','electron_decoupling','passive_elt']
        #TODO_MAR: Insert a different type of phase gate in the case of a passive element.

        for i in range(len(gate_seq)-1):
            ext_gate_seq.append(gate_seq[i])
            if ((gate_seq[i].Gate_type in gates_in_need_of_connecting_elts) and
                    (gate_seq[i+1].Gate_type in gates_in_need_of_connecting_elts)):
                ext_gate_seq.append(Gate('phase_gate_'+str(i)+'_'+str(pt),'Connection_element'))

            if gate_seq[i].Gate_type =='Trigger' :
                if ((gate_seq[i-1].Gate_type in gates_in_need_of_connecting_elts) and
                        (gate_seq[i+1].Gate_type in gates_in_need_of_connecting_elts)):
                    ext_gate_seq.append(Gate('phase_gate_'+str(i)+'_'+str(pt),'Connection_element'))

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

    #functions for making the elements


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
        This function takes a carbon (decoupling) gate as input, the gate must have tau and N as paramters
        It returns the object with the parameters relevant to make an AWG sequence added to it.
        These are: the AWG_elements, the number of repetitions N, number of wait reps n,  tau_cut and the total sequence time
        scheme selects the decoupling scheme
        '''
        tau = Gate.tau
        N = Gate.N
        Gate.reps = N # Overwrites reps parameter that is used in sequencing
        prefix = Gate.prefix

        #Generate the basic X and Y pulses
        X = self._X_elt()
        Y = self._Y_elt()

        ## Select scheme for generating decoupling elements  ##
        if N==0 or Gate.scheme =='auto':
            Gate = self.determine_decoupling_scheme(Gate)

        ###################
        ## Set paramters ##
        ###################

        tau_cut = 0 #initial value unless overwritten
        minimum_AWG_elementsize = 1e-6 #AWG elements/waveforms have to be 1 mu s
        fast_pi_duration = self.params['fast_pi_duration']
        pulse_tau = tau - fast_pi_duration/2.0 #To correct for pulse duration
        tau_prnt = int(tau*1e9) #Converts tau to ns for printing (removes the dot)
        n_wait_reps = 0 #this is the default value. Script returns this unless overwritten (as is the case for tau>2e-6)

        # initial checks to see if sequence is possible
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
        ###########################
        ## Genereate the pulse elements #
        ###########################
        list_of_elements = []
        ###########################
        ##### Single Block Scheme #####
        ###########################
        if Gate.scheme == 'single_block':
            # print 'using single block'
            tau_cut = 0

            if self.params['Initial_Pulse'] =='-x':
                initial_phase = self.params['X_phase'] +180
            else:
                initial_phase = self.params['X_phase']
            if self.params['Final_Pulse'] =='-x':
                final_phase = self.params['X_phase'] +180
            else:
                initial_phase = self.params['X_phase']

            pulse_tau_pi2 = tau - self.params['fast_pi2_duration']/2.0-self.params['fast_pi_duration']/2.0
            if pulse_tau_pi2 < 31e-9:
                print 'tau too short !!!, tau = ' +str(tau) +'min tau = ' +str(self.params['fast_pi2_duration']/2.0-self.params['fast_pi_duration']/2.0+30e-9)


            initial_pulse = pulselib.MW_IQmod_pulse('electron Pi/2-pulse',
                I_channel='MW_Imod', Q_channel='MW_Qmod',
                PM_channel='MW_pulsemod',
                frequency = self.params['fast_pi2_mod_frq'],
                PM_risetime = self.params['MW_pulse_mod_risetime'],
                length = self.params['fast_pi2_duration'],
                amplitude = self.params['fast_pi2_amp'],
                phase=initial_phase)
            final_pulse = pulselib.MW_IQmod_pulse('electron Pi/2-pulse',
                I_channel='MW_Imod', Q_channel='MW_Qmod',
                PM_channel='MW_pulsemod',
                frequency = self.params['fast_pi2_mod_frq'],
                PM_risetime = self.params['MW_pulse_mod_risetime'],
                length = self.params['fast_pi2_duration'],
                amplitude = self.params['fast_pi2_amp'],
                phase=final_phase)
            T_around_pi2 = pulse.SquarePulse(channel='MW_Imod', name='Wait: tau_pi2',
                length = pulse_tau_pi2, amplitude = 0.)
            T = pulse.SquarePulse(channel='MW_Imod', name='Wait: tau',
                length = pulse_tau, amplitude = 0.)

            x_list = [0,2,5,7]

            decoupling_elt = element.Element('Single_%s _DD_elt_tau_%s_N_%s' %(prefix,tau_prnt,N), pulsar = qt.pulsar, global_time=True)

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



        elif Gate.scheme == 'repeating_T_elt':
            # print 'Using repeating delay elements XY decoupling method'
            #######################
            ## XYn with repeating T elt #
            #######################

            #calculate durations
            n_wait_reps, tau_remaind = divmod(round(2*pulse_tau*1e9),1e3) #multiplying and round is to prevent weird rounding error going two ways in divmod function
            tau_remaind = tau_remaind *1e-9
            n_wait_reps = n_wait_reps -2
            tau_shortened = tau_remaind/2.0
            t_around_pulse = 1e-6 + tau_remaind/2.0


            Tus =pulse.SquarePulse(channel='MW_Imod', name='Wait: tau',
                length = 1e-6, amplitude = 0.)
            T = pulse.SquarePulse(channel='MW_Imod', name='Wait: tau',
                length = t_around_pulse, amplitude = 0.)
            T_shortened = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = tau_shortened, amplitude = 0.)

            #correct for part that is cut of when combining to sequence
            if n_wait_reps %2 == 0:
                tau_cut =1e-6
            else:
                tau_cut = 1.5e-6


            # combine the pulses to elements/waveforms and add to list of elements
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


            final_x_list = [0,1,3,6]
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
            ########
            ## XY8 ##
            ########
            element_duration_without_edge = 3*tau + fast_pi_duration/2.0
            if element_duration_without_edge  > (minimum_AWG_elementsize+36e-9): #+20 ns is to make sure that elements always have a minimal size
                tau_shortened = np.ceil((element_duration_without_edge+ 36e-9)/4e-9)*4e-9 -element_duration_without_edge
            else:
                tau_shortened = minimum_AWG_elementsize - element_duration_without_edge
                tau_shortened = np.ceil(tau_shortened/(4e-9))*(4e-9)
            tau_cut = tau - tau_shortened - fast_pi_duration/2.0
            # Make the delay pulses
            T = pulse.SquarePulse(channel='MW_Imod', name='Wait: tau',
                length = pulse_tau, amplitude = 0.)
            T_before_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = tau_shortened, amplitude = 0.)
            T_after_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = tau_shortened, amplitude = 0.)

            #Combine pulses to elements/waveforms and add to list of elements
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
            ########
            ## XY4 ##
            ########
            # print 'Using non-repeating delay elements XY4 decoupling method'
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

            #Combine pulses to elements/waveforms and add to list of elements
            e_start = element.Element('%s_X_Initial_DD_El_tau_N_ %s_%s' %(prefix,tau_prnt,N),  pulsar=qt.pulsar,
                    global_time = True)
            e_start.append(T_before_p)
            e_start.append(pulse.cp(X))
            e_start.append(T)
            list_of_elements.append(e_start)
            #Currently middle is XY2 with an if statement based on the value of N this can be optimised
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
            ######################
            ## Calibration NO Pulse ###
            ######################
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

        Number_of_pulses  = N



        ##########################################
        # adding all the relevant parameters to the object  ##
        ##########################################
        Gate.elements = list_of_elements
        if N == 0: #in order to correctly calc evolution time for 0 pulses case
            Gate.elements_duration= 1e-6
        else:
            Gate.elements_duration=2*tau*N - 2* tau_cut
        Gate.n_wait_reps= n_wait_reps
        Gate.tau_cut = tau_cut #is 0 when not overwritten (i.e. N=0)
        return Gate

    def generate_passive_wait_element(self,g):
        '''
        a 1us wait element that is repeated a lot of times

        Because there are connection elts on both sides of the wait gates the minimum duration of the wait is 3us.
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

        N = Gate.N
        prefix = Gate.prefix

        tau = Gate.tau
        tau_prnt = int(tau*1e9)

        tau_cut_before = Gate.tau_cut_before
        tau_cut_after = Gate.tau_cut_after
        pulse_tau= tau-self.params['fast_pi_duration']/2.0

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

        x_list = [0,2,5,7]
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
                decoupling_elt.append(T)

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

    #function for making sequences out of elements
    def combine_to_AWG_sequence(self,gate_seq,explicit = False):
        '''
        Used as last step before uploading, combines all the gates to a sequence the AWG can understand.
        Requires the gates to already have the elements and repetitions and stuff added as arguments.
        NOTE: 'event_jump', 'goto' and 'wait' options only available for certain types of elements
        explicit is a statement that is introduced to maintain backwards compatibility, explicit is also required when using jump and goto statements.
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
                st = gate.elements[0]
                x = gate.elements[1]
                y = gate.elements[2]
                fin = gate.elements[3]
                t = gate.elements[4]

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

    # elements generation 

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

        Gate_sequence = self.insert_phase_gates(Gate_sequence,pt)
        self.get_tau_cut_for_connecting_elts(Gate_sequence)
        self.track_and_calc_phase(Gate_sequence)
        for g in Gate_sequence:
            if (g.Gate_type == 'Connection_element' or g.Gate_type == 'electron_Gate'):
                self.determine_connection_element_parameters(g)
                self.generate_connection_element(g)

        return Gate_sequence

    def load_C_freqs_in_radians_sec(self):
        '''
        loads carbon frequencies to a handy array
        '''
        C_freq_0 =[]
        C_freq_1=[]
        C_freq_dec=[]
        for i in range(10):
            C0str = 'C'+str(i)+'_freq_0'
            C1str = 'C'+str(i)+'_freq_1'
            Cdecstr = 'C'+str(i)+'_freq_dec'
            try: 
                C_freq_0.append(self.params[C0str]*2*np.pi)
                C_freq_1.append(self.params[C1str]*2*np.pi)
                C_freq_dec.append (self.params[Cdecstr]*2*np.pi)
            except: 
                C_freq_1.append(None)
                C_freq_0.append(None)
                C_freq_dec.append (None)
        return C_freq_0, C_freq_1, C_freq_dec

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

                for g_b in Gate_sequence[i-1::-1]:
                    g.tau_cut_before = 1e-6 # Default value in case it is the first element
                    if g_b.Gate_type =='Trigger':  #Checks if there is a trigger between the 
                        found_trigger = True 
                        g_t = g_b 
                    elif (g_b.Gate_type =='Connection_element' or g_b.Gate_type=='electron_Gate') and found_trigger ==True:
                        g_t.elements_duration = g_t.elements_duration +1e-6 
                        g.tau_cut_before = 1e-6 

                    elif g_b.Gate_type =='Connection_element' or g_b.Gate_type=='electron_Gate':
                        print ( 'Error: There is no decoupling gate or trigger between %s and %s.') %(g.name,g_b.name)
                    elif hasattr(g_b, 'tau_cut'):
                        g.tau_cut_before = g_b.tau_cut
                        break
                for g_b in Gate_sequence[i+1::]:
                    g.tau_cut_after = 1e-6 # Default value in case it is the first element
                    if g_b.Gate_type =='Trigger':  #Checks if there is a trigger between the 
                        found_trigger = True 
                        g_t = g_b 
                    elif (g_b.Gate_type =='Connection_element' or g_b.Gate_type=='electron_Gate') and found_trigger ==True:
                        g_t.elements_duration = g_t.elements_duration +1e-6 
                        g.tau_cut_after = 1e-6 
                    elif g_b.Gate_type =='Connection_element' or g_b.Gate_type=='electron_Gate':
                        print ( 'Error: There is no decoupling gate or trigger between %s and %s.') %(g.name,g_b.name)
                    elif hasattr(g_b, 'tau_cut'):
                        g.tau_cut_after = g_b.tau_cut
                        break
        return Gate_sequence

    def track_and_calc_phase(self,Gate_sequence,Ren_phase_offset = False):
        '''
        This function keeps track of phases in a Gate sequence.
        It differs from the version in the parent class DynamicalDecoupling in that it
        tracks the evolved phase per gate based on the electron state.
        This allows for mid gate changing of precession frequency.
        It requires three variables in the msmt params to be stored for each carbon
        C*_freq_0, C*_freq_1, C*_freq_dec. where *is a carbon index (1,2 etc).

        The following attributes are added to each gate
        C_phases_after_gate [phase_C1, phase_C2, ... ]
        el_state_after_gate:  Possibilities are '0', '1' and 'sup'
        el_state_before_gate

        If g.C_phases_after_gate[i]  is specified for the gate before the function is called this takes priority
        over the phase calculated. This can be used if one wants to reset phase for example in the case of readouts.
        If 'g.phase = None' no phase correction using dynamical decoupling is aplied.
        if Ren_phase_offset == True: Carbon gates get an extre phase offset 

        NOTE: All phases used are in radians. Input phases are in degrees because of convetion.
        NOTE: Phases and electron states are with respect to the IDEAL gate.
        This does not correspond to the length of AWG elements.
        NOTE: g.el_state_after_gate has to be explicitly stated when it changes.
        No automatic bookkeeping done for you.
        NOTE: If you want to use this for complicated subsequences with jump statements the electron phase
            after the RO trigger must be set in the element that comes after it using g.el_state_before_gate.
            All different sequences must be sent trough this track and calc phase function in order to make this.

        '''
        #Load Carbon phases into handy array
        C_freq_0, C_freq_1, C_freq_dec = self.load_C_freqs_in_radians_sec()
        for i,g in enumerate(Gate_sequence):
            if g.el_state_before_gate ==None:
                if i == 0: #At first element, start initialised
                    g.el_state_before_gate = 'sup' # if nothing added g.el_state_before it defaults to sup.
                else:
                    g.el_state_before_gate =Gate_sequence[i-1].el_state_after_gate
            
            if i!= 0: 
                g.C_phases_before_gate = Gate_sequence[i-1].C_phases_after_gate

            if g.el_state_after_gate ==None:
                g.el_state_after_gate = g.el_state_before_gate


            #############
            # Decoupling elements
            #############
            if g.Gate_type == 'Carbon_Gate':
                for iC in range(len(g.C_phases_before_gate)):
                    if g.C_phases_before_gate[iC] == None and g.C_phases_after_gate[iC] == None:
                        if iC == g.Carbon_ind:
                            g.C_phases_after_gate[iC] = 0
                        else:
                            g.C_phases_after_gate[iC] = g.C_phases_before_gate[iC]
                    elif g.C_phases_after_gate[iC] == None:
                        g.C_phases_after_gate[iC] = g.C_phases_before_gate[iC]+ (2*g.tau*g.N)*C_freq_dec[iC]
                    elif g.C_phases_after_gate[iC] !=None and Ren_phase_offset == True: 
                        g.C_phases_after_gate[iC] =g.C_phases_after_gate[iC] + self.params['C'+str(iC)+'_Ren_phase_offset']/180.*np.pi  

            elif g.Gate_type =='electron_decoupling':

                for iC in range(len(g.C_phases_before_gate)):
                    if g.C_phases_after_gate[iC] == None:
                        g.C_phases_after_gate[iC] = (g.C_phases_before_gate[iC]+ (2*g.tau*g.N)*C_freq_dec[iC])%(2*np.pi)

            #################
            # Connecting elements
            #################

            elif g.Gate_type == 'Connection_element' or g.Gate_type == 'electron_Gate':
                if i == len(Gate_sequence)-1:
                    g.dec_duration = 0
                elif Gate_sequence[i+1].phase == None :
                    g.dec_duration =0 
                else:
                    desired_phase = Gate_sequence[i+1].phase/180.*np.pi #Convert degrees to radian
                    Carbon_index = Gate_sequence[i+1].Carbon_ind
                    if g.C_phases_before_gate[Carbon_index] ==None :
                        g.dec_duration = 0 #
                    else:
                        phase_diff =(desired_phase - g.C_phases_before_gate[Carbon_index])%(2*np.pi) 
                        if ( (phase_diff <= (self.params['min_phase_correct']/180.*np.pi)) or 
                                (abs(phase_diff -2*np.pi) <=  (self.params['min_phase_correct']/180.*np.pi)) ): 
                        # For very small phase differences correcting phase with decoupling introduces a larger error
                        #  than the phase difference error.

                            g.dec_duration = 0
                        else:
                            g.dec_duration =(round( phase_diff/C_freq_dec[Carbon_index]
                                    *1e9/(self.params['dec_pulse_multiple']*2))
                                    *(self.params['dec_pulse_multiple']*2)*1e-9)
                            while g.dec_duration <= self.params['min_dec_duration']:
                                phase_diff = phase_diff +2*np.pi
                                g.dec_duration =(round( phase_diff/C_freq_dec[Carbon_index]
                                        *1e9/(self.params['dec_pulse_multiple']*2))
                                        *(self.params['dec_pulse_multiple']*2)*1e-9)
                            g.dec_duration = g.dec_duration
                for iC in range(len(g.C_phases_before_gate)):
                    if (g.C_phases_after_gate[iC] == None) and (g.C_phases_before_gate[iC] !=None) :
                        g.C_phases_after_gate[iC] = (g.C_phases_before_gate[iC]+ g.dec_duration*C_freq_dec[iC])%(2*np.pi)
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
                            # print 'Warning: %s, el state in sup for passive elt' %g.name
            elif g.Gate_type=='Trigger':
                #NOTE Trigger element phase calc seems to work 
                for iC in range(len(g.C_phases_before_gate)):
                    if (g.C_phases_after_gate[iC] == None) and (g.C_phases_before_gate[iC] !=None):
                        if g.el_state_before_gate == '0':
                            g.C_phases_after_gate[iC] = (g.C_phases_before_gate[iC] + g.elements_duration*C_freq_0[iC])%(2*np.pi)
                        elif g.el_state_before_gate == '1':
                            g.C_phases_after_gate[iC] = (g.C_phases_before_gate[iC] + g.elements_duration*C_freq_1[iC])%(2*np.pi)
                        elif g.el_state_before_gate == 'sup':
                            g.C_phases_before_gate[iC]%(2*np.pi)
                            print 'Warning: %s, el state in sup for Trigger elt' %g.name
            elif g.Gate_type =='MBI':
                for iC in range(len(g.C_phases_before_gate)):
                    # The MBI element is always first and should not have anything to do with C_phases
                    if g.C_phases_after_gate[iC] ==None:
                        g.C_phases_after_gate[iC] = g.C_phases_before_gate[iC]

            else: # I want the program to spit out an error if I messed up i.e. forgot a gate type
                print 'Error: %s, Gate type not recognized %s' %(g.name,g.Gate_type)
          

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

####################################################
##########   Carbon Initialisated classes   ########
####################################################

class MBI_C13(DynamicalDecoupling):
    mprefix = 'single_carbon_initialised'
    adwin_process = 'MBI_single_C13' #Can be overwritten in childclasses if multiple C13's are addressed
    '''
    Class specifies a different adwin script to be used.
    gate sequence functions that use carbon initialisation are located in this class
    '''
    def autoconfig(self):
        self.params['A_SP_voltage_after_C13_MBI'] = \
            self.A_aom.power_to_voltage(
                    self.params['A_SP_amplitude_after_C13_MBI'])

        self.params['E_SP_voltage_after_C13_MBI'] = \
            self.E_aom.power_to_voltage(
                    self.params['E_SP_amplitude_after_C13_MBI'])

        self.params['E_C13_MBI_voltage'] = \
            self.E_aom.power_to_voltage(
                    self.params['E_C13_MBI_amplitude'])

        self.params['min_dec_duration']= self.params['min_dec_tau']*self.params['dec_pulse_multiple']*2

        self.params['Carbon_init_RO_wait'] = (self.params['C13_MBI_RO_duration']+self.params['SP_duration_after_C13'])*1.2e-6+20e-6
        # print 'carbon init ro wait %s' %self.params['Carbon_init_RO_wait']
        DynamicalDecoupling.autoconfig(self)


    # sub sequence functions 
    def initialize_carbon_sequence(self, 
            prefix = 'C_init',
            go_to_element ='MBI_1',
            initialization_method ='swap', 
            pt = 1, 
            addressed_carbon =1, 
            C_init_state='up', 
            el_after_init = '0' ):
        '''
        Supports Swap or MBI initialization, does not yet support initalizing in different bases.
        state can be 'up' or 'down'
        Swap init: up -> 0, down ->1
        MBI init: up -> +X, down -> -X

        Supports leaving the electron state in '0' or '1' after the gate by applying an extra X-pulse.
        Electron state after gate = '1'

        NOTE: There is a limitation if the electron is left in the '1' state the sequence ends with an electron pulse.
            This means that the first element after this sequence cannot be an electron pulse. If this is desired choose
            to initialize into '0' (ms=0) and then add the electron gate.
        '''

        if type(go_to_element) != str:
            go_to_element = go_to_element.name

        if C_init_state == 'up':
            C_init_y_phase = self.params['Y_phase']
        elif C_init_state == 'down':
            C_init_y_phase = self.params['Y_phase']+180


        C_init_y = Gate(prefix+str(addressed_carbon)+'_y_'+str(pt),'electron_Gate',
                Gate_operation='pi2',
                wait_for_trigger = True,
                phase = C_init_y_phase)

        C_init_Ren_a = Gate(prefix+str(addressed_carbon)+'_Ren_a_'+str(pt), 'Carbon_Gate',
                Carbon_ind = addressed_carbon,
                phase = self.params['C13_X_phase'])
        #TODO_MAR: Remove C_init_Ren statement 
        C_init_Ren_a.C_phases_after_gate[addressed_carbon] = self.params['C'+str(addressed_carbon)+'_Ren_phase_offset']/180.*np.pi 

        C_init_x = Gate(prefix+str(addressed_carbon)+'_x_'+str(pt),'electron_Gate',
                Gate_operation='pi2',
                phase = self.params['X_phase'])

            # INSERT Gate_operation 'special_pi2'

        C_init_Ren_b = Gate(prefix+str(addressed_carbon)+'_Ren_b_'+str(pt), 'Carbon_Gate',
                Carbon_ind = addressed_carbon,
                phase = self.params['C13_Y_phase'])


        C_init_RO_Trigger = Gate(prefix+str(addressed_carbon)+'_RO_trig_'+str(pt),'Trigger',
                wait_time= self.params['Carbon_init_RO_wait'],
                event_jump = 'next',
                go_to = go_to_element,
                el_state_before_gate = '0') #NOTE: If RO gets a click then the electron state has always been 0 since before the click

        C_init_elec_X = Gate(prefix+str(addressed_carbon)+'_elec_X'+str(pt),'electron_Gate',
                Gate_operation='pi',
                phase = self.params['X_phase'],
                el_state_after_gate = '1')

        if initialization_method == 'swap':
            #Swap initializes into 1 or 0 and contains extra Ren gate
            carbon_init_seq = [C_init_y, C_init_Ren_a, C_init_x,
                    C_init_Ren_b,
                    C_init_RO_Trigger]
            # Normal MBI initializes into +/-X
        elif initialization_method == 'MBI':
            carbon_init_seq = [C_init_y, C_init_Ren_a, C_init_x,
                    C_init_RO_Trigger]
        else:
            print 'Error initialization method (%s) not recognized, supported methods are "swap" and "MBI"' %initialization_method
            return False

        if el_after_init =='1':
            carbon_init_seq.append(C_init_elec_X)

        return carbon_init_seq

    def readout_single_carbon_sequence(self, 
            prefix = 'C_RO_', 
            go_to_element ='next',event_jump_element = 'next', 
            RO_duration = 10e-6, 
            pt = 1, addressed_carbon =1,  
            RO_Z=False,RO_phase = 0, 
            el_after_RO = '0' ):
        '''
        Creates a single carbon readout gate sequence. 
        Does a readout an a single Carbon. 

        Base to readout can be specified by 
        RO_Z True or False 
        RO_phase  in degress 

        In the case where this function is used to do conditional feed forward the following parameters have to be specified
        RO_duration:  this is the lenght of the trigger and states how long the trigger waits for a 'click' from the adwin 
        go_to_element: determines where to go when no 'click' comes from the adwin. 
        event_jump_element: determines where to jump to when a 'click' comes from the adwin. 

        NOTE: If used for branching, el_after_RO has to be manually overwritten when generating phase correction for different branches. 
        '''

        C_RO_Ren_a = Gate(prefix+str(addressed_carbon)+'_Ren_a_'+str(pt), 'Carbon_Gate',
                Carbon_ind = addressed_carbon, phase = RO_phase) 
        
        C_RO_y = Gate(prefix+str(addressed_carbon)+'y_'+str(pt),
                'electron_Gate',
                Gate_operation='pi2',
                phase = self.params['Y_phase'])
        if RO_phase!=None: 
            C_RO_Ren_b = Gate(prefix+str(addressed_carbon)+'_Ren_b_'+str(pt), 
                    'Carbon_Gate',
                    Carbon_ind = addressed_carbon, phase =( RO_phase+90))
        else: 
            C_RO_Ren_b = Gate(prefix+str(addressed_carbon)+'_Ren_b_'+str(pt), 
                    'Carbon_Gate',
                    Carbon_ind = addressed_carbon, phase =( RO_phase))
        C_RO_x = Gate(prefix+str(addressed_carbon)+'_x_'+str(pt),'electron_Gate',
                Gate_operation='pi2',
                phase = self.params['X_phase'])
        C_RO_Trigger = Gate(prefix+str(addressed_carbon)+'_Trigger_'+str(pt),'Trigger',
                elements_duration= RO_duration,
                el_state_before_gate = el_after_RO)


        if RO_Z == True: 
            carbon_RO_seq =[C_RO_Ren_a,C_RO_y, C_RO_Ren_b, C_RO_x,C_RO_Trigger]
        else: 
            C_RO_Ren_b.phase = RO_phase 
            carbon_RO_seq =[C_RO_y, C_RO_Ren_b, C_RO_x,C_RO_Trigger]

        return carbon_RO_seq

    def readout_multiple_carbon_sequence(self, 
            prefix = 'C_pRO',
            go_to_element ='next',event_jump_element = 'next', 
            RO_duration = 10e-6, 
            pt = 1, 
            addressed_carbon =[1,2], 
            RO_Z=[False,True],
            RO_phase = [0,0], 
            el_after_RO = '0' ):
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

        NOTE: If used for branching, el_after_RO has to be manually overwritten when generating phase correction for different branches. 
        '''
        if  RO_phase[0] == None and  RO_phase[1] == None: 
            print 'NO Carbon selected for readout, No sequence could be generated. in function: readout_multiple_carbon_sequence '
        elif RO_phase[0] == None: 
            carbon_RO_seq = self.readout_single_carbon_sequence(prefix=prefix, 
            go_to_element =go_to_element,event_jump_element = event_jump_element, 
            RO_duration = RO_duration, 
            pt = pt, addressed_carbon =addressed_carbon[1], 
            RO_Z=RO_Z[1],RO_phase =RO_phase[1], 
            el_after_RO = el_after_RO )
            return carbon_RO_seq

        elif RO_phase[1] == None: 
            carbon_RO_seq = self.readout_single_carbon_sequence(prefix = prefix, 
            go_to_element =go_to_element,event_jump_element = event_jump_element, 
            RO_duration = RO_duration, 
            pt = pt, addressed_carbon =addressed_carbon[0], 
            RO_Z=RO_Z[0],RO_phase =RO_phase[0], 
            el_after_RO = el_after_RO )
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
        
        C_pRO_fin_pi2 = Gate(prefix+'_pi2_b'+str(pt),'electron_Gate',
                Gate_operation='pi2',
                phase = self.params['X_phase'])
        C_pRO_Trigger = Gate(prefix+'_Trigger_'+str(pt),'Trigger',
                elements_duration= RO_duration,
                el_state_after_gate = el_after_RO)

        if RO_Z[0] == True and RO_Z[1] ==True: 
            C_pRO_Ren_a.phase = RO_phase[0]+90
            C_pRO_Ren_b.phase = RO_phase[1]+90 
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
            el_after_RO = '0'):
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
               
            elif RO_bases[i] == 'Y': 
                RO_Z[i] = False
                RO_phase[i] = self.params['C13_Y_phase']

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
            el_after_RO = el_after_RO)
        return carbon_tomo_seq





class NuclearRamseyWithInitialization(MBI_C13):
    '''
    This class generates the AWG sequence for a carbon ramsey experiment with nuclear initialization.

    Sequence is a combination of 4 subsequences
    1. MBI initialisation
    2. Carbon initialisation
    3. Carbon Ramsey evolution
    4. Carbon Readout
    '''
    mprefix = 'CarbonRamseyInitialised'

    def generate_sequence(self,upload=True,debug = False):
        pts = self.params['pts']
        # #initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Initialized Nuclear Ramsey Sequence')

        for pt in range(pts):
            ###########################################
            #####    Generating the sequence elements      ######
            ###########################################
            #Elements for the carbon initialisation

            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]

            carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                    initialization_method = self.params['C_init_method'], pt =pt,
                    addressed_carbon= self.params['Addressed_Carbon'],
                    C_init_state = self.params['C13_init_state'],
                    el_after_init = '0' ) 
            ################################

            if self.params['wait_times'][pt]< (self.params['Carbon_init_RO_wait']+3e-6): # because min length is 3e-6
                print ('Error: carbon evolution time (%s) is shorter than Initialisation RO duration (%s)'
                        %(self.params['wait_times'][pt],self.params['Carbon_init_RO_wait']))
            wait_gate = Gate('Wait_gate_'+str(pt),'passive_elt',
                    wait_time = self.params['wait_times'][pt]-self.params['Carbon_init_RO_wait'])

            C_evol_seq =[wait_gate]

            #############################
            carbon_RO_seq = self.readout_single_carbon_sequence(pt = pt, 
                    addressed_carbon =self.params['Addressed_Carbon'], 
                    RO_Z=self.params['C_RO_Z'] ,
                    RO_phase = self.params['C_RO_phase'][pt], 
                    el_after_RO = '0' )
            gate_seq = []
            gate_seq.extend(mbi_seq), gate_seq.extend(carbon_init_seq)
            gate_seq.extend(C_evol_seq), gate_seq.extend(carbon_RO_seq)
            ############

            gate_seq = self.generate_AWG_elements(gate_seq,pt)
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq, explicit=True)
            combined_list_of_elements.extend(list_of_elements)
            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)

            if debug: 
                print '*'*10 
                for g in gate_seq: 
                    print g.name 
                    print g.C_phases_before_gate
                    print g.C_phases_after_gate
                    print '-'*5 

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
                    el_after_init = '0' )
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
                    el_after_RO = '0' )

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
                    el_after_init = '0'  )

            #Elements for T1 evolution

            wait_gate = Gate('Wait_gate_'+str(pt),'passive_elt',
                    wait_time = self.params['wait_times'][pt]-self.params['Carbon_init_RO_wait'])

            C_evol_seq =[wait_gate]

            #############################
            #Readout in the Y basis
            # print 'ro phase = ' + str( self.params['C_RO_phase'][pt])

            C_basis_Ren = Gate('C_basis_Ren'+str(pt), 'Carbon_Gate',
                    Carbon_ind = self.params['Addressed_Carbon'],
                    phase = self.params['C13_X_phase'])

            C_RO_y = Gate('C_ROy_'+str(pt),'electron_Gate',
                    Gate_operation='pi2',
                    phase = self.params['Y_phase'])
            C_RO_Ren = Gate('C_RO_Ren_'+str(pt), 'Carbon_Gate',
                    Carbon_ind = self.params['Addressed_Carbon'],
                    phase = self.params['C13_Y_phase'])
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

class Two_QB_Tomography(MBI_C13):
    '''
    This class is to test multiple carbon initialization and Tomography.

    #Acutal sequence is a combination of multiple subsequences

    |elMBI| -|CinitA|-|CinitB|-|Tomography| 
    '''
    mprefix = 'single_carbon_initialised'
    adwin_process = 'MBI_multiple_C13'
    def generate_sequence(self,upload=True,debug = False):
        pts = self.params['pts']
        # #initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Two Qubit MBE')
        self.params['N_init_C']= 2
        self.params['N_MBE'] =1
        self.params['N_parity_msmts']=0

        for pt in range(pts):
            gate_seq = []

            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]
            gate_seq.extend(mbi_seq)

            carbon_init_seq_1 = self.initialize_carbon_sequence(go_to_element = mbi,
                    initialization_method = 'MBI', pt =pt,
                    addressed_carbon= self.params['Carbon A'])
            carbon_init_seq_2 = self.initialize_carbon_sequence(go_to_element = mbi,
                    initialization_method = 'MBI', pt =pt,
                    addressed_carbon= self.params['Carbon B'])
            gate_seq.extend(carbon_init_seq_1),gate_seq.extend(carbon_init_seq_2)

            carbon_tomo_seq = self.multi_qubit_tomography( go_to_element = 'next',
                    event_jump_element = 'next', 
                    RO_duration=10e-6, 
                    pt = pt, 
                    addressed_carbon = [self.params['Carbon A'],self.params['Carbon B']],
                    RO_bases =self.params['Tomography Bases'][pt])
            gate_seq.extend(carbon_tomo_seq)


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


class Two_QB_MBE(MBI_C13):
    '''
    TODO_MAR: Multiple branches depending on outcome
    TODO_MAR: Double naming of Gates, check how this works

    This class is to test multiple carbon initialization, MBE and RO.

    #Acutal sequence is a combination of multiple subsequences
    1. MBI electron initialization
    2. Carbon initialization 2 times
    3. MBE parity msmt
    4. Carbon Tomography Readout


                                         --|Tomo A| 
    |elMBI| -|CinitA|-|CinitB|-|Parity|             --wait 
                                         --|Tomo B|

    '''
    mprefix = 'single_carbon_initialised'
    adwin_process = 'MBI_multiple_C13'

    def generate_sequence(self,upload=True,debug = False):
        pts = self.params['pts']
        # #initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Two Qubit MBE')
        self.params['N_init_C']= 2
        self.params['N_MBE'] =1
        self.params['N_parity_msmts']=0

        for pt in range(pts):


            ###########################################
            #####    Generating the sequence elements      ######
            ###########################################
            #Elements for the carbon initialisation into 0 

            gate_seq = []

            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]
            gate_seq.extend(mbi_seq)

            carbon_init_seq_1 = self.initialize_carbon_sequence(go_to_element = mbi,
                    initialization_method = 'MBI', pt =pt,
                    addressed_carbon= self.params['Carbon A'])
            carbon_init_seq_2 = self.initialize_carbon_sequence(go_to_element = mbi,
                    initialization_method = 'MBI', pt =pt,
                    addressed_carbon= self.params['Carbon B'])
            gate_seq.extend(carbon_init_seq_1),gate_seq.extend(carbon_init_seq_2)

            ################################
            # Parity measurements
            # TODO_MAR: goto and jump cannot jump to statements that do not exist yet... 
            carbon_pRO_seq = self.readout_multiple_carbon_sequence( 
                    pt = pt, 
                    addressed_carbon =[self.params['Carbon A'], self.params['Carbon B']], 
                    RO_Z=[self.params['measZ_C_A'][pt],self.params['measZ_C_B'][pt]],
                    RO_phase = [self.params['Phases_C_A'][pt],self.params['Phases_C_B'][pt]], 
                    el_after_RO = '0' )

            gate_seq.extend(carbon_pRO_seq)

            #############################
            #Readout Tomography
            # TODO_MAR: This is not branched yet.  
            # TODO_MAR: Determine correct bases for alternate (outcome el =1) tomography. Currently these are identical 
            # TODO_MAR: correct jump and goto statements 
            carbon_tomo_seq_click = self.multi_qubit_tomography( go_to_element = 'next',
                    event_jump_element = 'next', 
                    RO_duration=10e-6, 
                    pt = pt, 
                    addressed_carbon = [self.params['Carbon A'],self.params['Carbon B']],
                    RO_bases =self.params['Tomography Bases'][pt])
            
            carbon_tomo_seq_no_click = self.multi_qubit_tomography( prefix= 'Tomo_n_',
                    go_to_element = 'next',
                    event_jump_element = 'next', 
                    RO_duration=10e-6, 
                    pt = pt, 
                    addressed_carbon = [self.params['Carbon A'],self.params['Carbon B']],
                    RO_bases =self.params['Tomography Bases'][pt])

            # Make correct jump statements for branching 
            carbon_pRO_seq[-1].go_to = carbon_tomo_seq_no_click[0].name
            carbon_pRO_seq[-1].event_jump = carbon_tomo_seq_click[0].name

            gate_seq.extend(carbon_tomo_seq_click), gate_seq.extend(carbon_tomo_seq_no_click)

            ###########################
            ### Sequence generation ###
            ###########################
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


class Three_QB_MB_QEC(MBI_C13):
    '''
    TODO_MAR: Finish 3QB MB QEC class
    This class is supposed to contain the complete QEC gate sequence.
    It still needs Adwin code to support it and to test it.
    Underdevelopment
    '''
    mprefix = 'single_carbon_initialised'
    adwin_process = 'MBI_single_C13'

    def generate_sequence(self,upload=True,debug = False):
        pts = self.params['pts']
        # #initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Initialized Nuclear Ramsey Sequence')

        # for pt in range(pts):

        #     #Acutal sequence is a combination of multiple subsequences
        #     # 1. MBI initialisation
        #     # 2. Carbon initialisation 3 times
        #     # 3. Carbon Ramsey evolution
        #     # 4. Carbon Readout

        #     ###########################################
        #     #####    Generating the sequence elements      ######
        #     ###########################################
        #     #Elements for the carbon initialisation

        #     gate_seq = []

        #     mbi = Gate('MBI_'+str(pt),'MBI')
        #     mbi_seq = [mbi]
        #     gate_seq.extend(mbi_seq)

        #     carbon_init_seq_1 = self.initialize_carbon_sequence(go_to_element = mbi,
        #             initialization_method = 'MBI', pt =pt,
        #             addressed_carbon= 1)
        #     carbon_init_seq_2 = self.initialize_carbon_sequence(go_to_element = mbi,
        #             initialization_method = 'MBI', pt =pt,
        #             addressed_carbon= 2)
        #     carbon_init_seq_3 = self.initialize_carbon_sequence(go_to_element = mbi,
        #             initialization_method = 'MBI', pt =pt,
        #             addressed_carbon= 3)
        #     gate_seq.extend(carbon_init_seq_1),gate_seq.extend(carbon_init_seq_2)
        #     gate_seq.extend(carbon_init_seq_3)

        #     ################################
        #     # Encoding


        #     #enc_Rx =  #TO:  IS THE ERROR HERE IN THE PHASE OR IN THE DURATION?
        #     '''
        #     TODO_MAR: Definie initial state for 3QB MB QEC 
        #     '''


        #     enc_Ren_1 =Gate('enc_Ren_1'+str(pt), 'Carbon_Gate',
        #         Carbon_ind = 1,
        #         phase = self.params['C13_X_phase'])
        #     enc_Ren_2 =Gate('enc_Ren_2'+str(pt), 'Carbon_Gate',
        #         Carbon_ind = 2,
        #         phase = self.params['C13_X_phase'])
        #     enc_Ren_3 = Gate('enc_Ren_3'+str(pt), 'Carbon_Gate',
        #         Carbon_ind = 3,
        #         phase = self.params['C13_X_phase'])

        #     enc_x =Gate('enc_x'+str(pt),'electron_Gate',
        #         Gate_operation='pi2',
        #         phase = self.params['X_phase'])

        #     enc_RO = Gate('enc_RO_trig_'+str(pt),'Trigger',
        #         wait_time= self.params['Carbon_init_RO_wait'],
        #         event_jump = 'next',
        #         go_to = mbi)

        #     encoding_seq = [enc_Rx,enc_Ren_1,enc_Ren_2,enc_Ren_3,enc_x,enc_RO]
        #     gate_seq.extend(encoding_seq)
        #     ################################
        #     # Parity measurements

        #     par_1_y_1=Gate('par_1_y_1'+str(pt),'electron_Gate',
        #         Gate_operation='pi2',
        #         phase = self.params['Y_phase'])
        #     par_1_Ren_1 =Gate('par_1_Ren_1'+str(pt), 'Carbon_Gate',
        #         Carbon_ind = 1,
        #         phase = self.params['C13_X_phase'])
        #     par_1_Ren_2 =Gate('par_1_Ren_2'+str(pt), 'Carbon_Gate',
        #         Carbon_ind = 2,
        #         phase = self.params['C13_X_phase'])
        #     par_1_y_2=Gate('par_1_y_2'+str(pt),'electron_Gate',
        #         Gate_operation='pi2',
        #         phase = self.params['Y_phase'])
        #     parity_seq_1 =[par_1_y_1,par_1_Ren_1,par_1_Ren_2,par_1_y_2]

        #     par_2_y_1=Gate('par_2_y_1'+str(pt),'electron_Gate',
        #         Gate_operation='pi2',
        #         phase = self.params['Y_phase'])
        #     par_2_Ren_1 =Gate('par_2_Ren_1'+str(pt), 'Carbon_Gate',
        #         Carbon_ind = 2,
        #         phase = self.params['C13_X_phase'])
        #     par_2_Ren_2 =Gate('par_2_Ren_2'+str(pt), 'Carbon_Gate',
        #         Carbon_ind = 3,
        #         phase = self.params['C13_X_phase'])
        #     par_2_y_2=Gate('par_2_y_2'+str(pt),'electron_Gate',
        #         Gate_operation='pi2',
        #         phase = self.params['Y_phase'])
        #     parity_seq_2 =[par_2_y_1,par_2_Ren_1,par_2_Ren_2,par_2_y_2]

        #     gate_seq.extend(parity_seq_1),gate_seq.extend(parity_seq_2)

        #     ########################
        #     ##  Conditional Feedback
        #     '''
        #     TODO_MAR:  Code conditional feedback in adwin 
        #     This still needs to be coded and a good way needs to be found to work with the adwin. 
        #     AWG probably does support jumping statements.
        #     '''



        #     #############################
        #     #Readout Tomography
        #     '''
        #     TODO_MAR: Make RO Tomography 
        #     Readout must be some fancy tomography like RO measurement on all qubits. Currently simple nuclear readout of 1 spin.
        #     '''

        #     C_RO_y = Gate('C_ROy_'+str(pt),'electron_Gate',
        #             Gate_operation='pi2',
        #             phase = self.params['Y_phase'])
        #     C_RO_Ren = Gate('C_RO_Ren_'+str(pt), 'Carbon_Gate',
        #             Carbon_ind = self.params['Addressed_Carbon'], phase = 0)
        #     C_RO_x = Gate('C_RO_x_'+str(pt),'electron_Gate',
        #             Gate_operation='pi2',
        #             phase = self.params['X_phase'])
        #     C_RO_Trigger = Gate('C_RO_Trigger_'+str(pt),'Trigger')

        #     carbon_RO_seq =[C_RO_y, C_RO_Ren, C_RO_x,C_RO_Trigger]



        #     ########################
        #     # All information that defines the sequence is now given.
        #     # We can now let the python code convert the gate seq to an AWG seq.
        #     ##################

        #     gate_seq = self.generate_AWG_elements(gate_seq,pt)
        #     #Convert elements to AWG sequence and add to combined list
        #     list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq, explicit=True)
        #     combined_list_of_elements.extend(list_of_elements)

        #     for seq_el in seq.elements:
        #         combined_seq.append_element(seq_el)

        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'


