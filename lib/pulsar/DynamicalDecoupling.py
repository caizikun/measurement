'''
This is based on the ElectronT1 class from PULSAR.PY
Work in progress CHANGE LOCATION
File made by Adriaan Rol
'''
import numpy as np
import qt
from measurement.lib.pulsar import pulse, pulselib, element, pulsar
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt

class DynamicalDecoupling(pulsar_msmt.MBI):

    '''
    This is a general class for decoupling gate sequences used in addressing Carbon -13 atoms
    It is a child of PulsarMeasurment.MBI
    '''
    mprefix = 'DecouplingSequence'

    #def autoconfig(self):
    #    self.params['wait_for_AWG_done'] = 0
    #    pulsar_msmt.MBI.autoconfig(self)

    def retrieve_resonant_carbon_conditions(self,GateName):
        '''
        This function retrieves the corresponding tau and N values from the cfg
        aswell as the order of the resonance k that is required to calculate phase differences

        Currently This function just returns some fixed values. Ideally it should get them from the cfg where they are set in the experiment
        '''
        if GateName == 'StdDecoupling':
            tau = self.params['tau']
            N = self.params['Number_of_pulses']
        elif GateName == 'Carbon1' :
            tau = self.params['tau_C1'] #From the measurement script would be better if it comes from config file
            N = self.params['N_C1']

        else:
            print 'Gate not in database'
            print GateName
            return
        return tau, N

    def generate_decoupling_sequence_elements(self,tau,N,prefix):
        '''
        This function takes the wait time and the number of pulse-blocks(repetitions) as input
        It returns the elements, the number of repetitions N, number of wait reps n,  tau_cut and the total sequence time
        '''
        #Generate the basic pulses
        X = pulselib.MW_IQmod_pulse('electron X-Pi-pulse',
            I_channel='MW_Imod', Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod',
            frequency = self.params['AWG_MBI_MW_pulse_mod_frq'],
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            length = self.params['fast_pi_duration'],
            amplitude = self.params['fast_pi_amp'],
            phase =  self.params['X_phase'])

        Y = pulselib.MW_IQmod_pulse('electron Y-Pi-pulse',
            I_channel='MW_Imod', Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod',
            frequency = self.params['AWG_MBI_MW_pulse_mod_frq'],
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            length = self.params['fast_pi_duration'],
            amplitude = self.params['fast_pi_amp'],
            phase = self.params['Y_phase'])

        minimum_AWG_elementsize = 1e-6 #AWG elements/waveforms have to be 1 mu s
        fast_pi_duration = self.params['fast_pi_duration']
        pulse_tau = tau - fast_pi_duration/2.0 #To correct for pulse duration
        tau_prnt = tau*1e9 #Converts tau to ns for printing (removes the dot)
        n_wait_reps = 0 #this is the default value. Script returns this unless overwritten (as is the case for tau>2e-6)

        # initial checks to see if sequence is possible
        if (N%2!=0) and (tau <= 2e-6):
            print 'Error: odd number of pulses, impossible to do decoupling control sequence'
        if pulse_tau<0:
            print 'Error: tau is smaller than pi-pulse duration. Cannot generate decoupling element'
            return
        elif tau <0.5e-6:
            print '''Error: total element duration smaller than 1 mu s.
            Requires more coding to implement
            '''
            return
        ###########################
        ## Genereate the pulse elements #
        ###########################
        elif tau> 2e-6:
            print 'Using repeating delay elements XY decoupling method'
            #######################
            ## XYn with repeating T elt #
            #######################

            #calculate durations
            n_wait_reps, tau_remaind = divmod(2*pulse_tau,1e-6)
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
                print tau_cut
            else:
                tau_cut = 1.5e-6
                print tau_cut

            # combine the pulses to elements/waveforms and add to list of elements
            list_of_elements = []
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
            e_end = element.Element('%s Final %s DD_El_tau_N_ %s_%s' %(P_type,prefix,tau,N),  pulsar=qt.pulsar,
                    global_time = True)
            e_end.append(T)
            e_end.append(pulse.cp(final_pulse))
            e_end.append(T_shortened)
            list_of_elements.append(e_end)

            T_us_rep = element.Element('us Rep elt %s DD_El_tau_N_%s_%s'%(prefix,tau_prnt,N),pulsar=qt.pulsar, global_time =True)
            T_us_rep.append(Tus)
            list_of_elements.append(T_us_rep)

        elif N%8 == 0:
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
            list_of_elements = []
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

        else:
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
            list_of_elements = []
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

        total_sequence_time=2*tau*N - 2* tau_cut
        Number_of_pulses  = N

        return [list_of_elements, Number_of_pulses, n_wait_reps,tau_cut, total_sequence_time]

    def Determine_length_and_type_of_Connection_elements(self,GateSequence,TotalsequenceTimes,tau_cut) :
        '''
        Empty function, needs to be able to determine the length and type of glue gates in the future
        '''
        pass

    def generate_connection_element(self,time_before_pulse,time_after_pulse, Gate_type,prefix,tau,N):
        '''
        Generates an element that connects to decoupling elements
        It can be at the start, the end or between sequence elements
        '''
        tau_prnt = tau*1e9
        if Gate_type == 'x':
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
            return [e]

        if Gate_type == '-x':
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
            return [e]



        elif Gate_type == 'pi':
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
            return [e]

        elif Gate_type == 'Wait':
            T_wait = pulse.SquarePulse(channel='MW_Imod', name='delay',
                length = time_before_pulse+time_after_pulse, amplitude = 0.)
            e = element.Element('%s delay_at_tau_ %s_%s' %(prefix,tau_prnt,N),  pulsar=qt.pulsar,
                    global_time = True)
            e.append(T_wait)
            return [e]

        else:
            print 'this is not programmed yet '
            return

    def combine_to_sequence(self,Lst_lst_els,list_of_repetitions,list_of_wait_reps):
        '''
        Combines all the generated elements to a sequence for the AWG
        Needs to be changed to handle the dynamical decoupling elements

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
                    seq.append(name=t.name+str(pulse_ct), wfname=t.name,
                        trigger_wait=False,repetitions = red_wait_reps)#floor divisor
                seq.append(name=st.name, wfname=st.name,
                    trigger_wait=False,repetitions = 1)
                pulse_ct+=1

                #Repeating centre elements
                x_list = [0,2,5,7]
                while pulse_ct < (rep-1):
                    seq.append(name=t.name+str(pulse_ct), wfname=t.name,
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
                        seq.append(name=t.name, wfname=t.name,
                           trigger_wait=False,repetitions = red_wait_reps-1) #floor divisor
                else:
                    seq.append(name=t.name+str(pulse_ct), wfname=t.name,
                        trigger_wait=False,repetitions = wait_reps)
                    seq.append(name=fin.name, wfname=fin.name,
                        trigger_wait=False,repetitions = 1)
                    if red_wait_reps!=0:
                        seq.append(name=t.name, wfname=t.name,
                           trigger_wait=False,repetitions = red_wait_reps) #floor divisor

            else:
                print 'Size of element not understood Error!'
                return
        return list_of_elements, seq

class AdvancedDecouplingSequence(DynamicalDecoupling):
    '''
    The advanced decoupling sequence is a child class of the more general decoupling gate sequence class
    It contains a specific gate sequence with feedback loops and other stuff
    !NB: It is currently EMPTY
    '''
    pass

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


        ############################################
        #Generation of trigger and MBI element
        #############################################
        ##maybe put the trigger pulse in a funvtion to remove clutter.
        Trig = pulse.SquarePulse(channel = 'adwin_sync',
            length = 10e-6, amplitude = 2)
        Trig_element = element.Element('ADwin_trigger', pulsar=qt.pulsar,
            global_time = True)
        Trig_element.append(Trig)

        mbi_elt = self._MBI_element()


        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Simple Decoupling Sequence')
        i = 0
        for pt in range(pts):
            N = Number_of_pulses[pt]
            tau = tau_list[pt]
            prefix = 'electron'
            ## Generate the decoupling elements
            list_of_decoupling_elements, list_of_decoupling_reps, n_wait_reps, tau_cut, total_decoupling_time = DynamicalDecoupling.generate_decoupling_sequence_elements(self,tau,N,prefix)
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
            qt.pulsar.upload(*combined_list_of_elements)
            print ' uploading sequence'
            qt.pulsar.program_sequence(combined_seq)
            # qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)
        else:
            print 'upload = false, no sequence uploaded to AWG'


