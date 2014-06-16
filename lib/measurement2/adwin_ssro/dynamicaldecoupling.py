'''
Measurement class
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
        misc gates: 'Wait gate', 'mbi'
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

        # Information on how to combine the gates in the AWG.
        self.wait_for_trigger = kw.pop('wait_for_trigger',False)
        self.event_jump = kw.pop('event_jump',None)
        self.go_to = kw.pop('go_to',None)

        #Description of other attributes that get added by functions
        # self.elements = elements
        # self.repetitions = repetitions
        # self.wait_reps = wait_reps
        #self.elements_duration  # this is the duration of the AWG element corresponding to this gate.
        #   Note the difference with the gate duration (tau_cut)
        #self.tau_cut # time removed from a decoupling sequence in final and initial element.
        #self.tau_cut_before # this is the tau_cut of the previous element, gets added to connection type elements to calculate dec times
        #self.tau_cut_after # this is the tau_cut of the following element
        #self.dec_duration # this is the calculated decoupling duration for connection elements, this is used to correct for phases

        #If there are any attributes being used frequently that are still missing here please add them for documentation

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
    def get_gate_parameters(self,Gate,resonance =0 ):
        '''
        Takes a gate object as input and uses the carbon index and the operation to determine tau and N from the msmt params
        Currently can only do single type of gate. Always does same amount of pulses
        '''
        ind = Gate.Carbon_ind
        if ind ==0:
            #Don't take arguments from a list if it is not acting on a carbon (i.e. electron decoupling)
            return
        Gate.N = self.params['C'+str(ind)+'_Ren_N'][resonance] #Needs to be added to msmt params
        Gate.tau = self.params['C'+str(ind)+'_Ren_tau'][resonance]


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
        for i in range(len(gate_seq)-1):
            ext_gate_seq.append(gate_seq[i])
            if ((gate_seq[i].Gate_type =='Carbon_Gate' or
                    gate_seq[i].Gate_type =='electron_decoupling') and
                    (gate_seq[i+1].Gate_type =='Carbon_Gate' or
                        gate_seq[i+1].Gate_type =='electron_decoupling' )):
                ext_gate_seq.append(Gate('phase_gate_'+str(i)+'_'+str(pt),'Connection_element'))
            if gate_seq[i].Gate_type =='Trigger' :
                # ext_gate_seq[-1].tau_cut = ext_gate_seq[-2].tau_cut
                if (gate_seq[i+1] =='Carbon_Gate' or
                        gate_seq[i+1] == 'electron_decoupling'):
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
                # print 'Carbon_Gate'
                if t_start[g.Carbon_ind] == 0:
                    t_start[g.Carbon_ind] = t-g.tau_cut+g.N*g.tau*2 #Note this is the time the Carbon gate starts, this is not identical to the time where the AWG element starts
            elif g.Gate_type == 'Connection_element' or g.Gate_type == 'electron_Gate':
                # print 'con_gate'
                ## if connection element determine parameters and track clock
                if i == len(Gate_sequence)-1: #at end of sequence no decoupling neccesarry for electron gate
                    g.dec_duration = 0

                else:# Determine
                    C_ind = Gate_sequence[i+1].Carbon_ind
                    if t_start[C_ind] ==0: #If not addresed before phase is arbitrary
                        g.dec_duration = 0
                    else:
                        desired_phase = Gate_sequence[i+1].phase
                        precession_freq = self.params['C'+str(C_ind)+'_freq']*2*np.pi #needs to be added to msmst params
                        if precession_freq == 0:
                            g.dec_duration = 0
                        else:
                            evolution_time = (t+Gate_sequence[i-1].tau_cut) - t_start[C_ind] # NB corrected for difference between time where the gate starts and where the AWG element starts
                            current_phase = evolution_time*precession_freq%(2*np.pi) # shouldnt this modulo be in the next line? - JULIA
                            phase_dif = desired_phase-current_phase

                            dec_duration = round( phase_dif/precession_freq *1e9/(self.params['dec_pulse_multiple']*2))*(self.params['dec_pulse_multiple']*2)*1e-9
                            min_dec_duration= self.params['min_dec_tau']*self.params['dec_pulse_multiple']*2

                            while dec_duration <= min_dec_duration:
                                phase_dif = phase_dif+2*np.pi
                                dec_duration = round( phase_dif/precession_freq *1e9/(self.params['dec_pulse_multiple']*2))*(self.params['dec_pulse_multiple']*2)*1e-9

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

    def determine_connection_element_parameters(self,Gate):
        '''
        Takes a decoupling duration and returns the 'optimal' tau and N to decouple it
        '''
        # Pulses must be multiple of
        dec_duration = Gate.dec_duration
        if dec_duration == 0:
            Gate.N = 0
            Gate.tau = 0
            return
        elif (dec_duration + Gate.tau_cut_after+Gate.tau_cut_before)<1e-6:
            print 'Error: connection element decoupling duration is too short dec_duration = %s, tau_cut_before = %s, tau_cut after = %s, must be atleast 1us' %(dec_duration,Gate.tau_cut_before,Gate.tau_after)
            return
        elif (dec_duration/(2*self.params['dec_pulse_multiple']))<self.params['min_dec_tau']:
            print 'Warning: connection element decoupling duration is too short. Not decoupling in time interval. \n dec_duration = %s, min dec_duration = %s' %(dec_duration,2*self.params['min_dec_tau']*self.params['dec_pulse_multiple'])
            Gate.N=0
            Gate.tau = 0
            return Gate


        for k in range(40):
            #Sweep over possible tau's
            tau =dec_duration/(2*(k+1)*self.params['dec_pulse_multiple'])
            if tau == 0:
                Gate.N = 0
                Gate.tau = 0
            elif tau < self.params['min_dec_tau']:
                print 'Error: decoupling tau: (%s) smaller than minimum value(%s), decoupling duration (%s)' %(tau,self.params['min_dec_tau'],dec_duration )
                break
            #If the found tau is allowed (bigger than min and smaller than max loop is done)
            elif tau > self.params['min_dec_tau'] and tau< self.params['max_dec_tau']:
                Gate.tau = tau
                Gate.N = int((k+1)*self.params['dec_pulse_multiple'])
                # print 'found the following decoupling tau: %s, N: %s' %(tau,Gate.N)
                break
            elif k == 79 and tau>self.params['max_dec_tau']:
                print 'Error: decoupling duration (%s) to large, for %s pulses decoupling tau (%s) larger than max decoupling tau (%s)' %(dec_duration,k,tau,self.params['max_dec_tau'])

        return Gate

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
            print 'Error! tau too small: Pulses will overlap!' ## ADD return "minimum tau = X" This should also be more general
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

    def generate_passive_wait_element(self,Gate):
        '''
        a 1us wait element that is repeated a lot of times
        '''
        # Because there are connection elts on both sides of the wait gates the minimum duration of the wait is 3us. This is because tau cut is 1e-6 on both sides.
        # This condition could be defined stricter when going trough all the files

        n_wait_reps, tau_remaind = divmod(round(Gate.wait_time*1e9),1e3) #multiplying and round is to prevent weird rounding error going two ways in divmod function
        tau_remaind = tau_remaind *1e-9 #convert back to seconds
        Gate.reps = n_wait_reps -2 #because tau_cut must be atleast 1 us
        Gate.tau_cut = 1e-6 + tau_remaind/2.0

        T = pulse.SquarePulse(channel='MW_Imod', name='Wait: tau',
            length = 1e-6, amplitude = 0.)
        rep_wait_elt = element.Element('%s' %(Gate.prefix), pulsar = qt.pulsar, global_time=True)
        rep_wait_elt.append(T)

        Gate.elements = [rep_wait_elt]
        Gate.elements_duration = 1e-6 *Gate.reps


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
            elif Gate.Gate_operation == 'pi':
                eP = self._X_elt()
            eP.phase = Gate.phase
            T_initial = pulse.SquarePulse(channel='MW_Imod', name='wait in T',
                length = tau_cut_before-eP.length/2.0, amplitude = 0.)
            T_dec_initial = pulse.SquarePulse(channel='MW_Imod', name='wait in T',
                length = pulse_tau-eP.length/2.0, amplitude = 0.)
        else:
            T_initial = pulse.SquarePulse(channel='MW_Imod', name='wait in T',
                length = tau_cut_before, amplitude = 0.)

        #######################################
        # _______________          :            (____|____)^N_____________
        # |tau_cut_before|(electronPulse)|(|tau|pi|tau|)^N|tau_cut_after|
        #######################################

        x_list = [0,2,5,7]
        decoupling_elt = element.Element('%s_tau_%s_N_%s' %(prefix,tau_prnt,N), pulsar = qt.pulsar, global_time=True)

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
        Used as last step before uploading, combines all the gates to a sequence the AWG can understand. Requires the gates to already have the elements and repetitions and stuff added as arguments
        NOTE: 'event_jump', 'goto' and 'wait' options only available for certain types of elements
        explicit is a statement that is introduced to maintain backwards compatibility.
        '''
        list_of_elements=[]
        seq = pulsar.Sequence('Decoupling Sequence')
        if explicit == False:  # explicit means that MBI and trigger elements must be given explicitly to the combine to AWG sequence function
            mbi_elt = self._MBI_element()
            list_of_elements.append(mbi_elt)
            seq.append(name=str(mbi_elt.name+gate_seq[0].elements[0].name), wfname=mbi_elt.name, trigger_wait=True,repetitions = 1, goto_target =str(mbi_elt.name+gate_seq[0].elements[0].name), jump_target = gate_seq[0].elements[0].name)

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

            single_elements_list = ['NO_Pulses','single_block','single_element']#,'trigger']
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


class NuclearRamsey(DynamicalDecoupling):
    '''
    The NuclearRamsey class performs a ramsey experiment on a nuclear spin that is resonantly controlled using a decoupling sequence.
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
            #    ---|pi/2| - |Ren| - |Rz| - |Ren| - |pi/2| ---
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

            print Rz.dec_duration
            print Rz.tau_cut_after
            print Rz.tau_cut_before
            print Rz.dec_duration+Rz.tau_cut_before+Rz.tau_cut_after
            self.determine_connection_element_parameters(Rz)
            self.generate_connection_element(Rz)
            print Rz.dec_duration

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


class CarbonGateSequence(DynamicalDecoupling):
    '''
    This is an example of an arbitrary gate sequence. Using this class any and all sequences should be easy to create
    '''
    mprefix = 'CarbonGateSeq'

    def generate_sequence(self,upload=True,debug=False):
        pts = self.params['pts']

        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('CarbonGateSeq')

        for pt in range(pts):
            #########################
            ## Define the sequence here
            # NB this is an arbitrary test example
            #########################

            initial_Pi2 = Gate('initial_pi2'+str(pt),'electron_Gate')
            Ren_a = Gate('Ren_a'+str(pt), 'Carbon_Gate')
            DD_gate = Gate('DD_gate'+str(pt),'electron_decoupling') #NB not strictly a Carbon Gate
            Ren_b = Gate('Ren_b'+str(pt),'Carbon_Gate')
            middle_pi = Gate('middle_pi2'+str(pt),'electron_Gate')
            Ren_c = Gate('Ren_c'+str(pt), 'Carbon_Gate')
            final_Pi2 = Gate('final_pi2'+str(pt),'electron_Gate')

            gate_seq = [initial_Pi2,Ren_a,DD_gate,Ren_b,middle_pi,Ren_c,final_Pi2]

            #############
            # Set parameters of gates
            # This sequence has arbitrary parameters but could have anything
            #############
            Ren_a.Carbon_ind = 1 #acts on carbon #1
            Ren_a.phase = 0*np.pi  # the desired phase in radians
            Ren_b.Carbon_ind = 1 #acts on carbon #1
            Ren_b.phase = 0*np.pi  # the desired phase in radians
            Ren_c.Carbon_ind = 1 #acts on carbon #1
            Ren_c.phase = 0*np.pi  # the desired phase in radians

            Ren_a.scheme = self.params['Decoupling_sequence_scheme']
            Ren_b.scheme = self.params['Decoupling_sequence_scheme']
            Ren_c.scheme = self.params['Decoupling_sequence_scheme']


            ###########
            # Calculate parameters for and generate the main DD element
            ###########
            DD_gate.Carbon_ind = 0 #Not acting on a carbon
            self.params['tau_larmor'] = self.get_tau_larmor()
            self.params['free_evolution_times'][pt]
            N2, tau_left = divmod(self.params['free_evolution_times'][pt],4*self.params['tau_larmor'])

            DD_gate.N = int(N2*2) #N2 because N must be even
            DD_gate.tau = self.params['tau_larmor']
            DD_gate.scheme = 'auto'


            initial_Pi2.Gate_operation = 'pi2'
            initial_Pi2.phase = 0
            middle_pi.Gate_operation ='pi'
            middle_pi.phase = np.pi

            final_Pi2.Gate_operation = 'pi2'
            final_Pi2.phase = np.pi

            for g in gate_seq:
                if g.Gate_type =='Carbon_Gate' or g.Gate_type =='electron_decoupling':
                    self.get_gate_parameters(g)
                    self.generate_decoupling_sequence_elements(g)

            #Insert connection elements in sequence
            #Function inserts (empty) phase gates in the sequence
            for g in gate_seq:
                print g.prefix
            print
            gate_seq = self.insert_phase_gates(gate_seq,pt)
            for g in gate_seq:
                print g.prefix
            print
            #generate connection elements with proper phases, also includes electron pulses
            self.calc_and_gen_connection_elts(gate_seq)

            #Convert elements to AWG sequence and add to combined list
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq)
            combined_list_of_elements.extend(list_of_elements)
            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)


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
    The NuclearRamsey class performs a ramsey experiment on a nuclear spin that is resonantly controlled using a decoupling sequence.
    The no DD variant does not decouple the electronic spin while the nuclear spin evolves. Instead it applies a pi/2 pulse to bring the
        electronic spin in a mixed state, let the nucleus evolve and then applies a second pi/2 pulse before the second Ren gate to read out.
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
            #    ---|pi/2| - |Ren| - |pi/2|--|Wait| -- |pi/2|- |Ren| - |pi/2| ---
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

class SimpleDecoupling(DynamicalDecoupling):
    '''
    The most simple version of a decoupling sequence
    Contains initial pulse, decoupling sequence and final pulse.
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
            #               ---|pi/2| - |DD| - |pi/2| ---
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

        # set time that the adwin maximally does MBI equal to the duration of the AWG trigger where it expects an event jump
        self.params['C13_MBI_duration']= int(self.params['Carbon_init_RO_wait'] *1e6 -5)
        if  self.params['C13_MBI_duration'] < 0 :
            print 'Error: C13_MBI duration <0 duration is : %s us' % self.params['C13_MBI_duration']
            return
        DynamicalDecoupling.autoconfig(self)

    def initialize_carbon_sequence(self, go_to_element ='MBI_1', initialization_method ='swap', pt = 1, addressed_carbon =1):
        '''
        Supports Swap or MBI initialization, does not yet support initalizing in different bases.
        '''

        if type(go_to_element) != str:
            go_to_element = go_to_element.name

        C_int_y = Gate('C_int_y_'+str(pt),'electron_Gate',
                Gate_operation='pi2',
                wait_for_trigger = True,
                phase = self.params['Y_phase'])

        C_int_Ren_a = Gate('C_int_Ren_a_'+str(pt), 'Carbon_Gate',
                Carbon_ind = addressed_carbon,
                phase = self.params['C13_X_phase'])

        C_int_x = Gate('C_int_x_'+str(pt),'electron_Gate',
                Gate_operation='pi2',
                phase = self.params['X_phase'])

        C_int_Ren_b = Gate('C_int_Ren_b_'+str(pt), 'Carbon_Gate',
                Carbon_ind = addressed_carbon,
                phase = self.params['C13_Y_phase'])

        C_int_RO_Trigger = Gate('C_int_RO_trig_'+str(pt),'Trigger',
                wait_time= self.params['Carbon_init_RO_wait'],
                event_jump = 'next',
                go_to = go_to_element)

        if initialization_method == 'swap':
            #Swap initializes into 1 or 0 and contains extra Ren gate
            carbon_init_seq = [C_int_y, C_int_Ren_a, C_int_x,
                    C_int_Ren_b,
                    C_int_RO_Trigger]
            # Normal MBI initializes into +/-X
        elif initialization_method == 'MBI':
            carbon_init_seq = [C_int_y, C_int_Ren_a, C_int_x,
                    C_int_RO_Trigger]
        else:
            print 'Error initialization method (%s) not recognized, supported methods are "swap" and "MBI"' %initialization_method
            return False
        return carbon_init_seq

    def readout_carbon_sequence(self, RO_phase = 0,pt = 1, addressed_carbon =1 ):
        C_RO_y = Gate('C_ROy_'+str(pt),'electron_Gate',
                Gate_operation='pi2',
                phase = self.params['Y_phase'])
        C_RO_Ren = Gate('C_RO_Ren_'+str(pt), 'Carbon_Gate',
                Carbon_ind = self.params['Addressed_Carbon'], phase = RO_phase)
        C_RO_x = Gate('C_RO_x_'+str(pt),'electron_Gate',
                Gate_operation='pi2',
                phase = self.params['X_phase'])
        C_RO_fin_Trigger = Gate('C_RO_fin_Trigger_'+str(pt),'Trigger')

        carbon_RO_seq =[C_RO_y, C_RO_Ren, C_RO_x,C_RO_fin_Trigger]
        return carbon_RO_seq

    def generate_AWG_elements(self,gate_seq,pt = 1):

        for g in gate_seq:
            if g.Gate_type =='Carbon_Gate' or g.Gate_type =='electron_decoupling':
                self.get_gate_parameters(g)
                self.generate_decoupling_sequence_elements(g)
            elif g.Gate_type =='passive_elt':
                self.generate_passive_wait_element(g)
            elif g.Gate_type == 'MBI':
                self.generate_MBI_elt(g)
            elif g.Gate_type == 'Trigger':
                self.generate_trigger_elt(g)
        #Insert connection elements in sequence
        gate_seq = self.insert_phase_gates(gate_seq,pt)
        #generate connection elements with proper phases, also includes electron pulses
        self.calc_and_gen_connection_elts(gate_seq)
        return gate_seq


class NuclearRamseyWithInitialization(MBI_C13):
    '''
    This class generates the AWG sequence for a carbon ramsey experiment with nuclear initialization.
    '''
    mprefix = 'CarbonRamseyInitialised'
    # adwin_process = 'MBI_single_C13' Omitted, is inclued in MBI_single_C13 class
 # overwrites the name of the adwin_process
    def generate_sequence(self,upload=True,debug = False):
        pts = self.params['pts']
        # #initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Initialized Nuclear Ramsey Sequence')

        for pt in range(pts):

            #Acutal sequence is a combination of 3 subsequences
            # 1. MBI initialisation
            # 2. Carbon initialisation
            # 3. Carbon Ramsey evolution
            # 4. Carbon Readout

            ###########################################
            #####    Generating the sequence elements      ######
            ###########################################
            #Elements for the carbon initialisation

            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]

            carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                    initialization_method = 'swap', pt =pt,
                    addressed_carbon= self.params['Addressed_Carbon'])
            ################################
            if self.params['wait_times'][pt]< (self.params['Carbon_init_RO_wait']+3e-6): #because min length is 3e-6
                print ('Error: carbon evolution time (%s) is shorter than Initialisation RO duration (%s)'
                        %(self.params['wait_times'][pt],self.params['Carbon_init_RO_wait']))
            wait_gate = Gate('Wait_gate_'+str(pt),'passive_elt',
                    wait_time = self.params['wait_times'][pt]-self.params['Carbon_init_RO_wait'])

            C_evol_seq =[wait_gate]
            #############################
            #Readout in the x basis
            C_RO_y = Gate('C_ROy_'+str(pt),'electron_Gate',
                    Gate_operation='pi2',
                    phase = self.params['Y_phase'])
            C_RO_Ren = Gate('C_RO_Ren_'+str(pt), 'Carbon_Gate',
                    Carbon_ind = self.params['Addressed_Carbon'], phase = 0)
            C_RO_x = Gate('C_RO_x_'+str(pt),'electron_Gate',
                    Gate_operation='pi2',
                    phase = self.params['X_phase'])
            C_RO_fin_Trigger = Gate('C_RO_fin_Trigger_'+str(pt),'Trigger')

            carbon_RO_seq =[C_RO_y, C_RO_Ren, C_RO_x,C_RO_fin_Trigger]

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

class ThreeQubitMeasurementBasedQuantumErrorCorrection(MBI_C13):
    '''
    This class is supposed to contain the complete QEC gate sequence. It still needs Adwin code to support it and to test it.
    '''
    mprefix = 'single_carbon_initialised'
    adwin_process = 'MBI_single_C13'

    def generate_sequence(self,upload=True,debug = False):
        pts = self.params['pts']
        # #initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Initialized Nuclear Ramsey Sequence')

        for pt in range(pts):

            #Acutal sequence is a combination of multiple subsequences
            # 1. MBI initialisation
            # 2. Carbon initialisation 3 times
            # 3. Carbon Ramsey evolution
            # 4. Carbon Readout

            ###########################################
            #####    Generating the sequence elements      ######
            ###########################################
            #Elements for the carbon initialisation

            gate_seq = []

            mbi = Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]
            gate_seq.extend(mbi_seq)

            carbon_init_seq_1 = self.initialize_carbon_sequence(go_to_element = mbi,
                    initialization_method = 'MBI', pt =pt,
                    addressed_carbon= 1)
            carbon_init_seq_2 = self.initialize_carbon_sequence(go_to_element = mbi,
                    initialization_method = 'MBI', pt =pt,
                    addressed_carbon= 2)
            carbon_init_seq_3 = self.initialize_carbon_sequence(go_to_element = mbi,
                    initialization_method = 'MBI', pt =pt,
                    addressed_carbon= 3)
            gate_seq.extend(carbon_init_seq_1),gate_seq.extend(carbon_init_seq_2)
            gate_seq.extend(carbon_init_seq_3)

            ################################
            # Encoding


            enc_Rx =  # IS THE ERROR HERE IN THE PHASE OR IN THE DURATION?
            '''
            Still need to determine what the initial state is that will be encoded and how
            dynamical this needs to be.
            '''


            enc_Ren_1 =Gate('enc_Ren_1'+str(pt), 'Carbon_Gate',
                Carbon_ind = 1,
                phase = self.params['C13_X_phase'])
            enc_Ren_2 =Gate('enc_Ren_2'+str(pt), 'Carbon_Gate',
                Carbon_ind = 2,
                phase = self.params['C13_X_phase'])
            enc_Ren_3 = Gate('enc_Ren_3'+str(pt), 'Carbon_Gate',
                Carbon_ind = 3,
                phase = self.params['C13_X_phase'])

            enc_x =Gate('enc_x'+str(pt),'electron_Gate',
                Gate_operation='pi2',
                phase = self.params['X_phase'])

            enc_RO = Gate('enc_RO_trig_'+str(pt),'Trigger',
                wait_time= self.params['Carbon_init_RO_wait'],
                event_jump = 'next',
                go_to = mbi)

            encoding_seq = [enc_Rx,enc_Ren_1,enc_Ren_2,enc_Ren_3,enc_x,enc_RO]
            gate_seq.extend(encoding_seq)
            ################################
            # Parity measurements

            par_1_y_1=Gate('par_1_y_1'+str(pt),'electron_Gate',
                Gate_operation='pi2',
                phase = self.params['Y_phase'])
            par_1_Ren_1 =Gate('par_1_Ren_1'+str(pt), 'Carbon_Gate',
                Carbon_ind = 1,
                phase = self.params['C13_X_phase'])
            par_1_Ren_2 =Gate('par_1_Ren_2'+str(pt), 'Carbon_Gate',
                Carbon_ind = 2,
                phase = self.params['C13_X_phase'])
            par_1_y_2=Gate('par_1_y_2'+str(pt),'electron_Gate',
                Gate_operation='pi2',
                phase = self.params['Y_phase'])
            parity_seq_1 =[par_1_y_1,par_1_Ren_1,par_1_Ren_2,par_1_y_2]

            par_2_y_1=Gate('par_2_y_1'+str(pt),'electron_Gate',
                Gate_operation='pi2',
                phase = self.params['Y_phase'])
            par_2_Ren_1 =Gate('par_2_Ren_1'+str(pt), 'Carbon_Gate',
                Carbon_ind = 2,
                phase = self.params['C13_X_phase'])
            par_2_Ren_2 =Gate('par_2_Ren_2'+str(pt), 'Carbon_Gate',
                Carbon_ind = 3,
                phase = self.params['C13_X_phase'])
            par_2_y_2=Gate('par_2_y_2'+str(pt),'electron_Gate',
                Gate_operation='pi2',
                phase = self.params['Y_phase'])
            parity_seq_2 =[par_2_y_1,par_2_Ren_1,par_2_Ren_2,par_2_y_2]

            gate_seq.extend(parity_seq_1),gate_seq.extend(parity_seq_2)

            ########################
            ##  Conditional Feedback
            '''
            This still needs to be coded and a good way needs to be found to work with the adwin. AWG probably does support jumping statements.
            '''



            #############################
            #Readout in the x basis
            '''
            Readout must be some fancy tomography like RO measurement on all qubits. Currently simple nuclear readout of 1 spin.
            '''

            C_RO_y = Gate('C_ROy_'+str(pt),'electron_Gate',
                    Gate_operation='pi2',
                    phase = self.params['Y_phase'])
            C_RO_Ren = Gate('C_RO_Ren_'+str(pt), 'Carbon_Gate',
                    Carbon_ind = self.params['Addressed_Carbon'], phase = 0)
            C_RO_x = Gate('C_RO_x_'+str(pt),'electron_Gate',
                    Gate_operation='pi2',
                    phase = self.params['X_phase'])
            C_RO_fin_Trigger = Gate('C_RO_fin_Trigger_'+str(pt),'Trigger')

            carbon_RO_seq =[C_RO_y, C_RO_Ren, C_RO_x,C_RO_fin_Trigger]



            ########################
            # All information that defines the sequence is now given.
            # We can now let the python code convert the gate seq to an AWG seq.
            ##################

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


