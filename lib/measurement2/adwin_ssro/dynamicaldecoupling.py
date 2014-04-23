'''
Measurement class
File made by Adriaan Rol
'''
import numpy as np
import qt
from measurement.lib.pulsar import pulse, pulselib, element, pulsar
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt

class DecouplingGate(object):
    def __init__(self,name,Gate_type):
        self.name = name
        self.Gate_type = Gate_type # can be electron, carbon or connection
        self.phase = 0 #default phase at which the gate should start
        self.reps = 1 # only overwritten in case of Carbon decoupling elements
        # self.elements = elements
        # self. repetitions = repetitions
        # self.wait_reps = wait_reps

class DynamicalDecoupling(pulsar_msmt.MBI):

    '''
    This is a general class for decoupling gate sequences used in addressing Carbon -13 atoms
    It is a child of PulsarMeasurment.MBI
    '''
    mprefix = 'DecouplingSequence'

    def _X_elt(self):
        '''
        Trigger element that is used in different measurement child classes
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

    def _Y_elt(self):
        '''
        Trigger element that is used in different measurement child classes
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

    def generate_decoupling_sequence_elements(self,DecouplingGate,scheme = 'auto'):
        '''
        This function takes a carbon (decoupling) gate as input, the gate must have tau and N as paramters
        It returns the object with the parameters relevant to make an AWG sequence added to it.
        These are: the AWG_elements, the number of repetitions N, number of wait reps n,  tau_cut and the total sequence time
        scheme selects the decoupling scheme
        '''
        tau = DecouplingGate.tau,N,prefix
        N = DecouplingGate.N
        DecouplingGate.reps = N # Overwrites reps parameter that is used in sequencing
        prefix = DecouplingGate.prefix

        #Generate the basic X and Y pulses
        X = self._X_elt()

        Y = self._Y_elt()

        #######################################################
        ## Select scheme for generating decoupling elements  ##
        #######################################################
        if N == 0:
            ### For N==0, select a different scheme without pulses
            scheme = 'calibration_NO_Pulses'
        elif scheme == 'auto':
            if tau>2e-6 and tau :           ## ERROR?
                scheme = 'repeating_T_elt'
            elif tau<= self.params['fast_pi_duration']+20e-9: ## ERROR? shouldn't this be 1/2*pi_dur + 10?
                print 'Error! tau too small: Pulses will overlap!' ## ADD return "minimum tau = X" This should also be more general
                return
            elif tau<0.5e-6:
                scheme = 'single_block'
            elif N%8:           ## ERROR? Should be N%8 == 0: ?
                scheme = 'XY8'
            elif N%2:           ## ERROR?
                scheme = 'XY4' #Might be outdated in functionality
        else:
            scheme = scheme

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
        if scheme == 'single_block':
            print 'using single block'
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
                print 'tau to short !!!, tau = ' +str(tau) +'min tau = ' +str(self.params['fast_pi2_duration']/2.0-self.params['fast_pi_duration']/2.0+30e-9)


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



        elif scheme == 'repeating_T_elt':
            print 'Using repeating delay elements XY decoupling method'
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
            e_X_start = element.Element('X Initial %s DD_El_tau_N_ %s_%s' %(prefix,tau_prnt,N),  pulsar=qt.pulsar,
                    global_time = True)
            e_X_start.append(T_shortened)
            e_X_start.append(pulse.cp(X))
            e_X_start.append(T)
            list_of_elements.append(e_X_start)

            e_X =  element.Element('X rep %s DD_El_tau_N_ %s_%s' %(prefix,tau_prnt,N),  pulsar=qt.pulsar,
                    global_time = True)
            e_X.append(T)
            e_X.append(pulse.cp(X))
            e_X.append(T)
            list_of_elements.append(e_X)

            e_Y =  element.Element('Y rep  %s DD_El_tau_N_ %s_%s' %(prefix,tau_prnt,N),  pulsar=qt.pulsar,
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
            e_end = element.Element('%s Final %s DD_El_tau_N_ %s_%s' %(P_type,prefix,tau_prnt,N),  pulsar=qt.pulsar,
                    global_time = True)
            e_end.append(T)
            e_end.append(pulse.cp(final_pulse))
            e_end.append(T_shortened)
            list_of_elements.append(e_end)

            T_us_rep = element.Element('us Rep elt %s DD_El_tau_N_%s_%s'%(prefix,tau_prnt,N),pulsar=qt.pulsar, global_time =True)
            T_us_rep.append(Tus)
            list_of_elements.append(T_us_rep)

        elif scheme == 'XY8':
            print 'Using non-repeating delay elements XY8 decoupling method'
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
            e_XY_start = element.Element('XY Initial %s XY8-DD_El_tau_N_ %s_%s' %(prefix,tau_prnt,N),  pulsar=qt.pulsar,
                    global_time = True)
            e_XY_start.append(T_before_p)
            e_XY_start.append(pulse.cp(X))
            e_XY_start.append(T)
            e_XY_start.append(T)
            e_XY_start.append(pulse.cp(Y))
            e_XY_start.append(T)
            list_of_elements.append(e_XY_start)

            e_XY = element.Element('XY Rep %s XY8-DD_El_tau_N_ %s_%s' %(prefix,tau_prnt,N),  pulsar=qt.pulsar,
                    global_time = True)
            e_XY.append(T)
            e_XY.append(pulse.cp(X))
            e_XY.append(T)
            e_XY.append(T)
            e_XY.append(pulse.cp(Y))
            e_XY.append(T)
            list_of_elements.append(e_XY)

            e_YX = element.Element('YX Rep %s XY8-DD_El_tau_N_ %s_%s' %(prefix,tau_prnt,N),  pulsar=qt.pulsar,
                    global_time = True)
            e_YX.append(T)
            e_YX.append(pulse.cp(Y))
            e_YX.append(T)
            e_YX.append(T)
            e_YX.append(pulse.cp(X))
            e_YX.append(T)
            list_of_elements.append(e_YX)

            e_YX_end = element.Element('YX Final %s XY-8 DD_El_tau_N_ %s_%s' %(prefix,tau_prnt,N),  pulsar=qt.pulsar,
                    global_time = True)
            e_YX_end.append(T)
            e_YX_end.append(pulse.cp(Y))
            e_YX_end.append(T)
            e_YX_end.append(T)
            e_YX_end.append(pulse.cp(X))
            e_YX_end.append(T_after_p)
            list_of_elements.append(e_YX_end)

        elif scheme == 'XY4':
            ########
            ## XY4 ##
            ########
            print 'Using non-repeating delay elements XY4 decoupling method'
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
            e_start = element.Element('X Initial %s DD_El_tau_N_ %s_%s' %(prefix,tau_prnt,N),  pulsar=qt.pulsar,
                    global_time = True)
            e_start.append(T_before_p)
            e_start.append(pulse.cp(X))
            e_start.append(T)
            list_of_elements.append(e_start)
            #Currently middle is XY2 with an if statement based on the value of N this can be optimised
            e_middle = element.Element('YX Rep %s DD_El_tau_N_ %s_%s' %(prefix,tau_prnt,N),  pulsar=qt.pulsar,
                    global_time = True)
            e_middle.append(T)
            e_middle.append(pulse.cp(Y))
            e_middle.append(T)
            e_middle.append(T)
            e_middle.append(pulse.cp(X))
            e_middle.append(T)
            list_of_elements.append(e_middle)
            e_end = element.Element('Y Final %s DD_El_tau_N_ %s_%s' %(prefix,tau_prnt,N),  pulsar=qt.pulsar,
                    global_time = True)
            e_end.append(T)
            e_end.append(pulse.cp(Y))
            e_end.append(T_after_p)
            list_of_elements.append(e_end)

        elif scheme == 'calibration_NO_Pulses':
            ######################
            ## Calibration NO Pulse ###
            ######################
            '''
            Pulse scheme specifically created for calibration
            Applies no pulses but instead waits for 1us
            '''
            T = pulse.SquarePulse(channel='MW_Imod', name='Wait: tau',
                length = 1e-6, amplitude = 0.)
            wait = element.Element('NO_Pulse_Calibration_N_%s' %(N),  pulsar=qt.pulsar,
                    global_time = True)
            wait.append(T)
            list_of_elements.append(wait)

        else:
            print 'Scheme = '+scheme
            print 'Error!: selected scheme does not exist for generating decoupling elements.'

            return
        total_sequence_time=2*tau*N - 2* tau_cut
        Number_of_pulses  = N

        ##########################################
        # adding all the relevant parameters to the object  ##
        ##########################################
        DecouplingGate.elements = list_of_elements
        DecouplingGate.total_sequence_time = total_sequence_time
        DecouplingGate.n_wait_reps= n_wait_reps
        DecouplingGate.tau_cut = tau_cut
        DecouplingGate.total_sequence_time = total_sequence_time
        return DecouplingGate

    def Determine_length_and_type_of_Connection_elements(self,GateSequence) :
        '''
        Empty function, needs to be able to determine the length and type of glue gates in the future
        '''
        pass

    def generate_connection_element(self,DecouplingGate):
        '''
        Creates a single element that does only decoupling
        requires DecouplingGate to have the following attributes
        N, prefix, tau, time_before_pulse, time_after_pulse
        '''

        N = DecouplingGate.N
        prefix = DecouplingGate.prefix

        tau = DecouplingGate.tau
        tau_prnt = int(tau*1e9)

        time_before_pulse = DecouplingGate.time_before_pulse
        time_after_pulse = DecouplingGate.time_after_pulse

        pulse_tau= tau-self.params['fast_pi_duration']/2.0
        init_pulse_T= time_before_pulse-self.params['fast_pi_duration']/2.0
        fin_pulse_T= time_after_pulse-self.params['fast_pi_duration']/2.0

        T = pulse.SquarePulse(channel='MW_Imod', name='Wait: tau',
            length = pulse_tau, amplitude = 0.)
        T_inital = pulse.SquarePulse(channel='MW_Imod', name='wait in T',
            length = init_pulse_T, amplitude = 0.)
        T_final = pulse.SquarePulse(channel='MW_Imod', name='wait fin T',
            length = fin_pulse_T, amplitude = 0.)

        x_list = [0,2,5,7]

        decoupling_elt = element.Element('Single_%s _DD_elt_tau_%s_N_%s' %(prefix,tau_prnt,N), pulsar = qt.pulsar, global_time=True)

        decoupling_elt.append(T_initial)
        for n in range(N) :
            if n !=0:
                decoupling_elt.append(T)
            if n%8 in x_list:
                decoupling_elt.append(X)
            else:
                decoupling_elt.append(Y)
            if n !=N-1:
                decoupling_elt.append(T)
        decoupling_elt.append(T_final)
        list_of_elements.append(decoupling_elt)

        DecouplingGate.elements = list_of_elements







    def generate_electron_gate_element(self,DecouplingGate):
        '''
        Generates an element that connects to decoupling elements
        It can be at the start, the end or between sequence elements
        time_before_pulse,time_after_pulse, Gate_type,prefix,tau,N
        '''
        time_before_pulse = DecouplingGate.time_before_pulse
        time_after_pulse = DecouplingGate.time_after_pulse
        Gate = DecouplingGate.Gate
        prefix = DecouplingGate.prefix

        tau_prnt = int(tau*1e9)
        if gate == 'x':
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

            e = element.Element('%s Pi_2_pulse_tau_ %s_%s' %(prefix,tau_prnt,N),  pulsar=qt.pulsar,
                    global_time = True)
            e.append(T_before_p)
            e.append(pulse.cp(X))
            e.append(T_after_p)


        elif gate == '-x':
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

            e = element.Element('%s Pi_2_pulse_tau_ %s_%s' %(prefix,tau_prnt,N),  pulsar=qt.pulsar,
                    global_time = True)
            e.append(T_before_p)
            e.append(pulse.cp(X))
            e.append(T_after_p)

        elif gate == 'pi':
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

            e = element.Element('%s Pi_pulse_tau_%s_%s' %(prefix,tau_prnt,N),  pulsar=qt.pulsar,
                    global_time = True)
            e.append(T_before_p)
            e.append(pulse.cp(X))
            e.append(T_after_p)

        else:
            print 'this is not programmed yet '
            return

        DecouplingGate.elements = [e]

    def generate_wait_element(self,DecouplingGate):
        '''
        Generates an element that connects to decoupling elements
        It can be at the start, the end or between sequence elements
        time_before_pulse,time_after_pulse, Gate_type,prefix,tau,N
        '''
        time_before_pulse = DecouplingGate.time_before_pulse
        time_after_pulse = DecouplingGate.time_after_pulse
        Gate = DecouplingGate.Gate
        prefix = DecouplingGate.prefix

        T_wait = pulse.SquarePulse(channel='MW_Imod', name='delay',
            length = time_before_pulse+time_after_pulse, amplitude = 0.)
        e = element.Element('%s delay_at_tau_ %s_%s' %(prefix,tau_prnt,N),  pulsar=qt.pulsar,
                global_time = True)
        e.append(T_wait)
        return [e]


    def combine_to_sequence(self,Lst_lst_els,list_of_repetitions,list_of_wait_reps):
        '''
        !NB Depreciated, delete if combine_to_awg_sequence is working properly

        Combines all the generated elements to a sequence for the AWG
        Needs to be changed to handle the dynamical decoupling elements

        Function should be depreciateda

        '''
        seq = pulsar.Sequence('Decoupling Sequence')
        list_of_elements=[]
        #Lst_lst_els means list of list of elements
        for ind, rep in enumerate(list_of_repetitions):

            list_of_elements.extend(Lst_lst_els[ind]) #this converts the list_of_list to an

            ######################
            ### single elements (trigger, connecting elements or single pulses)
            ######################
            if np.size(Lst_lst_els[ind]) ==1:
                e =Lst_lst_els[ind][0]
                if e.name == 'MBI CNOT':
                    seq.append(name=str(e.name+Lst_lst_els[ind+1][0].name), wfname=e.name, trigger_wait=True,repetitions = rep, goto_target =str(e.name+Lst_lst_els[ind+1][0].name), jump_target = Lst_lst_els[ind+1][0].name)
                elif ind == 1:
                    seq.append(name=e.name, wfname=e.name,
                        trigger_wait=True,repetitions = rep)
                elif e.name == 'ADwin_trigger':
                    seq.append(name=str(e.name+Lst_lst_els[ind-1][0].name), wfname=e.name,
                        trigger_wait=False,repetitions = rep)
                else:
                    seq.append(name=e.name, wfname=e.name,
                        trigger_wait=False,repetitions = rep)

            ######################
            ### XY4 elements
            ######################
            elif np.size(Lst_lst_els[ind]) == 3: #XY4 decoupling elements
                # print "lengt of list of list  == 3"
                seq.append(name=Lst_lst_els[ind][0].name, wfname=Lst_lst_els[ind][0].name,
                    trigger_wait=False,repetitions = 1)
                seq.append(name=Lst_lst_els[ind][1].name, wfname=Lst_lst_els[ind][1].name,
                    trigger_wait=False,repetitions = rep/2-1)
                seq.append(name=Lst_lst_els[ind][2].name, wfname=Lst_lst_els[ind][2].name,
                    trigger_wait=False,repetitions = 1)

            ######################
            ### XY8 elements
            #-a-b-(c^2-b^2)^(N/8-1)-c-d-
            ######################
            elif np.size(Lst_lst_els[ind]) == 4:
                a = Lst_lst_els[ind][0]
                b= Lst_lst_els[ind][1]
                c = Lst_lst_els[ind][2]
                d = Lst_lst_els[ind][3]
                seq.append(name=a.name, wfname=a.name,
                    trigger_wait=False,repetitions = 1)
                seq.append(name=b.name, wfname=b.name,
                    trigger_wait=False,repetitions = 1)
                for i in range(rep/8-1):
                    seq.append(name=(c.name+str(i)), wfname=c.name,
                        trigger_wait=False,repetitions = 2)
                    seq.append(name=(b.name+str(i)), wfname=b.name,
                        trigger_wait=False,repetitions = 2)
                seq.append(name=c.name, wfname=c.name,
                    trigger_wait=False,repetitions = 1)
                seq.append(name=d.name, wfname=d.name,
                    trigger_wait=False,repetitions = 1)

                ######################
                ### XYn, tau > 2 mus
                # t^n a t^n b t^n
                ######################
            elif np.size(Lst_lst_els[ind]) == 5:
                wait_reps = list_of_wait_reps[ind]
                st = Lst_lst_els[ind][0]
                x = Lst_lst_els[ind][1]
                y = Lst_lst_els[ind][2]
                fin = Lst_lst_els[ind][3]
                t = Lst_lst_els[ind][4]

                #Start elements
                pulse_ct = 0
                red_wait_reps = wait_reps//2
                if red_wait_reps != 0:
                    seq.append(name=t.name+'_'+str(pulse_ct), wfname=t.name,
                        trigger_wait=False,repetitions = red_wait_reps)#floor divisor
                seq.append(name=st.name, wfname=st.name,
                    trigger_wait=False,repetitions = 1)
                pulse_ct+=1

                #Repeating centre elements
                x_list = [0,2,5,7]
                while pulse_ct < (rep-1):
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
                if rep == 1:
                    if red_wait_reps!=0 and red_wait_reps!=1 :
                        seq.append(name=t.name+str(pulse_ct+1), wfname=t.name,
                           trigger_wait=False,repetitions = red_wait_reps-1) #floor divisor
                else:
                    seq.append(name=t.name+'_'+str(pulse_ct), wfname=t.name,
                        trigger_wait=False,repetitions = wait_reps)
                    seq.append(name=fin.name, wfname=fin.name,
                        trigger_wait=False,repetitions = 1)
                    if red_wait_reps!=0:
                        seq.append(name=t.name+str(pulse_ct+1), wfname=t.name,
                           trigger_wait=False,repetitions = red_wait_reps) #floor divisor

            else:
                print Lst_lst_els[ind]
                print 'Size of element not understood Error!'
                return
        return list_of_elements, seq

    def _Trigger_element(self):
        '''
        Trigger element that is used in different measurement child classes
        '''
        Trig = pulse.SquarePulse(channel = 'adwin_sync',
            length = 10e-6, amplitude = 2)
        Trig_element = element.Element('ADwin_trigger', pulsar=qt.pulsar,
            global_time = True)
        Trig_element.append(Trig)
        return Trig_element

    def combine_to_AWG_sequence(self,gate_seq):
        '''
        Used as last step before uploading, combines all the gates to a sequence the AWG can understand. Requires the gates to already have the elements and repetitions and stuff added as arguments
        '''
        list_of_elements=[]
        seq = pulsar.Sequence('Decoupling Sequence')

        mbi_elt = self._MBI_element()
        list_of_elements.append(mbi_elt)
        seq.append(name=str(mbi_elt.name+gate_seq[0].elements[0].name), wfname=mbi_elt.name, trigger_wait=True,repetitions = 1, goto_target =str(mbi_elt.name+gate_seq[0].elements[0].name), jump_target = gate_seq[0].elements[0].name)

        for i, gate in enumerate(gate_seq):
            ####################
            ###  single elements  ###
            ####################
            if np.size(gate.elements) ==1:
                e = gate.elements[0]
                list_of_elements.append(e)
                if i == 0:
                    seq.append(name=e.name, wfname=e.name,
                        trigger_wait=True,repetitions = gate.reps)
                else:
                    seq.append(name=e.name,wfname =e.name,trigger_wait=False,
                            repetitions=gate.reps)

            ######################
            ### XY4 elements
            ######################
            if np.size(gate.elements) ==3:
                list_of_elements.extend(gate.elements)
                seq.append(name=gate.elements[0].name, wfname=gate.elements[0].name,
                    trigger_wait=False,repetitions = 1)
                seq.append(name=gate.elements[1].name, wfname=gate.elements[1].name,
                    trigger_wait=False,repetitions = gate.reps/2-1)
                seq.append(name=gate.elements[2].name, wfname=gate.elements[2].name,
                    trigger_wait=False,repetitions = 1)
            ######################
            ### XY8 elements
            #-a-b-(c^2-b^2)^(N/8-1)-c-d-
            ######################
            elif np.size(gate.elements) == 4:
                list_of_elements.extend(gate.elements)
                a = gate.elements[0]
                b= gate.elements[1]
                c = gate.elements[2]
                d = gate.elements[3]
                seq.append(name=a.name, wfname=a.name,
                    trigger_wait=False,repetitions = 1)
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
                    trigger_wait=False,repetitions = 1)
            ######################
            ### XYn, tau > 2 mus
            # t^n a t^n b t^n
            ######################
            elif np.size(gate.elements) == 5:
                wait_reps = gate.n_wait_reps
                st = gate.elements[0]
                x = gate.elements[1]
                y = gate.elements[2]
                fin = gate.elements[3]
                t = gate.elements[4]

                #Start elements
                pulse_ct = 0
                red_wait_reps = wait_reps//2
                if red_wait_reps != 0:
                    seq.append(name=t.name+'_'+str(pulse_ct), wfname=t.name,
                        trigger_wait=False,repetitions = red_wait_reps)#floor divisor
                seq.append(name=st.name, wfname=st.name,
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
                           trigger_wait=False,repetitions = red_wait_reps-1) #floor divisor
                else:
                    seq.append(name=t.name+'_'+str(pulse_ct), wfname=t.name,
                        trigger_wait=False,repetitions = wait_reps)
                    seq.append(name=fin.name, wfname=fin.name,
                        trigger_wait=False,repetitions = 1)
                    if red_wait_reps!=0:
                        seq.append(name=t.name+str(pulse_ct+1), wfname=t.name,
                           trigger_wait=False,repetitions = red_wait_reps) #floor divisor


        trig_elt = self._Trigger_element()
        list_of_elements.append(trig_elt)
        seq.append(name=str(e.name+Lst_lst_els[ind-1][0].name), wfname=e.name,
                        trigger_wait=False,repetitions = 1)

        return list_of_elements, seq




class NuclearRamsey(DynamicalDecoupling):
    '''
    The NuclearRamsey class performs a ramsey experiment on a nuclear spin that is resonantly controlled using a decoupling sequence.
    '''
    def generate_sequence(self, upload= True, debug = False):
        pts = self.params['pts']
        free_evolution_time = self.param['free_evolution_time']

        # #initialise empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Nuclear Ramsey Sequence')

        ###########################################
        #####    Generating the sequence elements      ######
        #    ---|pi/2| - |CNOT| - |Rz| - |CNOT| - |pi/2| ---
        ###########################################
        initial_Pi2 = DecouplingGate('initial_pi2','electron_Gate')
        Ren_CNOT = DecouplingGate('Ren_CNOT', 'Carbon_Gate')
        Rz = DecouplingGate('Rz','Connection_element')
        final_Pi2 = DecouplingGate('final_pi2','electron_Gate')

        ############
        gate_seq = [initial_Pi2,Ren_CNOT,Rz,Ren_CNOT,final_Pi2]
        ############


        Ren_CNOT.N = self.params['CNOT_Ren_N']
        Ren_CNOT.tau = self.params['C_Ren_tau']
        Ren_CNOT.prefix = 'CNOT'

        #Generate sequence elements for all Carbon gates
        generate_decoupling_sequence_elements(Ren_CNOT) #Ren_CNOT = gen... should not be neccesarry. Good to test

        #Use information about duration of carbon gates to calculate
        #use function for this in more fancy meass class
        initial_Pi2.time_before_pulse =max(1e-6 - Ren_CNOT.tau_cut + 36e-9,44e-9)
        initial_Pi2.time_after_pulse = Ren_CNOT.tau_cut
        initial_Pi2.Gate = self.params['Initial_Pulse']
        initial_Pi2.prefix = 'init_pi2'

        final_Pi2.time_before_pulse =Ren_CNOT.tau_cut
        final_Pi2.time_after_pulse = initial_Pi2.time_before_pulse
        final_Pi2.Gate = self.params['Final_Pulse']
        final_Pi2.prefix = 'fin_pi2'

        #Generate the start and end pulse
        generate_electron_gate_element(initial_Pi2)
        generate_electron_gate_element(final_Pi2)

        # Generate Rz element (now we explicitly set tau, N and time before and after final)
        Rz.prefix = 'phase_gate'
        Rz.N = 8
        Rz.tau = .2e-6
        #determine_tau_N_connection_gate(Rz)
        generate_phase_gate(Rz)
        #some function that creates a single element


        ## Combine to AWG sequence that can be uploaded #
        list_of_elements, seq = combine_to_AWG_sequence(gate_seq)

        ##########################################
        # Combine make final sequence for all loops
        # combined_list_of_elements.extend(list_of_elements)
        # for seq_el in seq.elements:
        #     combined_seq.append_element(seq_el)

        #
        combined_list_of_elements =list_of_elements
        combined_seq = seq


        if upload:
            print 'uploading list of elements'
            # qt.pulsar.upload(*combined_list_of_elements)
            print ' uploading sequence'
            # qt.pulsar.program_sequence(combined_seq)
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
        scheme = self.params['Decoupling_sequence_scheme']

        #Generation of trigger and MBI element
        Trig_element = self._Trigger_element()
        mbi_elt = self._MBI_element()

        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Simple Decoupling Sequence')
        i = 0
        for pt in range(pts):
            N = Number_of_pulses[pt]
            tau = tau_list[pt]
            prefix = 'electron'
            ## Generate the decoupling elements
            list_of_decoupling_elements, list_of_decoupling_reps, n_wait_reps, tau_cut, total_decoupling_time = DynamicalDecoupling.generate_decoupling_sequence_elements(self,tau,N,prefix,scheme)

            if np.size(list_of_decoupling_elements) ==1:#Size of 1 corresponds to the 'one-piece' decoupling sequence
                ###########################################
                ####   Final and initial pulses included in element####
                ###########################################
                list_of_list_of_elements = []
                list_of_list_of_elements.append([mbi_elt])
                list_of_list_of_elements.append(list_of_decoupling_elements)
                list_of_list_of_elements.append([Trig_element])
                list_of_repetitions = [1,1,1]
                list_of_wait_reps =[]
                list_of_wait_reps = [0,0,0]

                list_of_elements, seq = DynamicalDecoupling.combine_to_sequence(self,list_of_list_of_elements,list_of_repetitions,list_of_wait_reps)

            else:
                #Generate the start and end pulse
                Gate_type = self.params['Initial_Pulse']
                time_before_initial_pulse = max(1e-6 - tau_cut + 36e-9,44e-9)  #statement makes sure that time before initial pulse is not negative
                time_after_initial_pulse = tau_cut

                prefix = 'initial'
                initial_pulse = DynamicalDecoupling.generate_connection_element(self,time_before_initial_pulse,time_after_initial_pulse, Gate_type,prefix,tau,N)

                Gate_type = self.params['Final_Pulse']
                time_before_final_pulse = tau_cut
                time_after_final_pulse = time_before_initial_pulse

                prefix = 'final'
                final_pulse = DynamicalDecoupling.generate_connection_element(self,time_before_final_pulse,time_after_final_pulse, Gate_type,prefix,tau,N)

                ########################################
                #Combine all the elements to a sequence
                #very sequence specific
                ########################################
                list_of_list_of_elements = []
                list_of_list_of_elements.append([mbi_elt])
                list_of_list_of_elements.append(initial_pulse)
                list_of_list_of_elements.append(list_of_decoupling_elements)
                list_of_list_of_elements.append(final_pulse)
                list_of_list_of_elements.append([Trig_element])
                list_of_repetitions = [1,1]+[list_of_decoupling_reps]+[1,1]
                list_of_wait_reps =[]
                list_of_wait_reps = [0,0]+[n_wait_reps] +[0,0]

            #######
            #The combine to sequence takes a list_of_list_of_elements as input and returns it as a normal list and a sequence (example [[pi/2],[a,b,c,d],[pi/2],[trig]] and [1,16,1,1] as inputs returns the normal list of elements and the sequence)
            #######

            list_of_elements, seq = DynamicalDecoupling.combine_to_sequence(self,list_of_list_of_elements,list_of_repetitions,list_of_wait_reps)

            if i == 0:
                i=1
                combined_list_of_elements.extend(list_of_elements)
            else:
                combined_list_of_elements.extend(list_of_elements[:-1])
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
