import numpy as np
import qt

from measurement.lib.pulsar import pulse, pulselib, element, pulsar
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
import measurement.lib.measurement2.measurement as m2
import pulse_select as ps
import sys

class DelayTimedPulsarMeasurement(pulsar_msmt.PulsarMeasurement):
    adwin_process = "integrated_ssro_tico_delay_timing"
    mprefix = "DelayTiming"

    def autoconfig(self):
        pulsar_msmt.PulsarMeasurement.autoconfig(self)

        if self.params['do_tico_delay_control']:
            if not 'delay_cycles' in self.params:
                self.calculate_delay_cycles()
                
            self.set_delay_cycles(self.params['delay_cycles'])

    def calculate_delay_cycles(self):
        # convert delay times into number of cycles
        delay_cycles = (
            (
                np.array(self.params['delay_times']) 
                - self.params['delay_time_offset']
            ) 
            / self.params['delay_clock_cycle_time']
        )
        self.params['delay_cycles'] = delay_cycles
        if np.min(delay_cycles) < self.params['minimal_delay_cycles']:
            raise Exception("Desired delay times are too short")

    def set_delay_cycles(self, delay_cycles):
        int_delay_cycles = np.array(delay_cycles, dtype=np.int32)
        # print(int_delay_cycles)
        self.adwin.set_dummy_tico_selftrigger_var(delay_cycles=int_delay_cycles)

class GeneralElectronRamseySelfTriggered(pulsar_msmt.PulsarMeasurement):
    """
    General class to implement Ramsey sequence. 
    generate_sequence needs to be supplied with a pi2_pulse as kw.
    """
    mprefix = 'GeneralElectronRamseySelfTriggered'

    def autoconfig(self):
        self.params['sequence_wait_time'] = \
            int(np.ceil(np.max(self.params['evolution_times'])*1e6)+10)


        pulsar_msmt.PulsarMeasurement.autoconfig(self)

    def generate_sequence(self, upload=True, **kw):

        # define the necessary pulses
        
        X=kw.get('pulse_pi2', None)

        T = pulse.SquarePulse(channel='MW_Imod', name='delay',
            length = 200e-9, amplitude = 0.)

        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = self.params['AWG_to_adwin_ttl_trigger_duration'],
            amplitude = 2)

        self_trigger = pulse.SquarePulse(channel='self_trigger',
            length = self.params['self_trigger_duration'],
            amplitude = 2)

        # make the elements - one for each ssb frequency
        elements = []
        for i in range(self.params['pts']):

            e1 = element.Element('ElectronRamsey_pt-%d_A' % i, pulsar=qt.pulsar,
                global_time = True)
            e1.append(pulse.cp(T,
                length = 1000e-9))

            e1.append(pulse.cp(X,
                phase = self.params['pulse_sweep_pi2_phases1'][i]))

            e1.append(pulse.cp(T,
                length = self.params['evolution_times'][i] - self.params['self_trigger_delay']))

            e1.append(pulse.cp(self_trigger))
            elements.append(e1)

            e2 = element.Element('ElectronRamsey_pt-%d_B' % i, pulsar=qt.pulsar,
                global_time = True)

            e2.append(pulse.cp(X,
                phase = self.params['pulse_sweep_pi2_phases2'][i]))

            e2.append(T)
            e2.append(adwin_sync)

            elements.append(e2)
        # return_e=e
        # create a sequence from the pulses
        seq = pulsar.Sequence('ElectronRamsey self-triggered sequence with {} pulses'.format(self.params['pulse_type']))
        for e in elements:
            seq.append(name=e.name, wfname=e.name, trigger_wait=True)

        # upload the waveforms to the AWG
        if upload:
            if upload=='old_method':
                qt.pulsar.upload(*elements)
                qt.pulsar.program_sequence(seq)
            else:
                qt.pulsar.program_awg(seq,*elements)

# class GateSetNoTriggers(pulsar_msmt.PulsarMeasurement):
class GateSetWithDecoupling(pulsar_msmt.MBI):
    """
    Class used to generate a gate set tomography sequence. 
    generate_sequence needs to be supplied with a xpi2_pulse and a ypi2_pulse as kw.
    """
    mprefix = 'GateSetTomography'

    def autoconfig(self):
        pulsar_msmt.MBI.autoconfig(self)

    def generate_decoupling_list(self, pos):
        """
        This function is used to generate the decoupling sequence that we want to use
        """

        N = self.params['N_decoupling'][pos]

        decoupling_list = []

        #Determine how many multiples of 8 pulses we have since we want to use xy8 here
        fractions = int(N/8)

        if fractions>=1:
            for i in range(fractions):
                decoupling_list.extend(['x', 'y', 'x', 'y', 'y', 'x', 'y', 'x'])
                N -=8

        if N == 1:
            decoupling_list.extend(['x'])

        for i in range(3):

            if N == 0:
                break
            elif int(N/6) == 1:
                decoupling_list.extend(['x', 'y', 'x', 'y', 'x', 'mx'])
                N -=6

            elif int(N/4) == 1:
                decoupling_list.extend(['x', 'y', 'x', 'y'])
                N -=4

            elif int(N/2) == 1:
                decoupling_list.extend(['x', 'mx'])
                N -=2

            elif N == 1:

                # print decoupling_list[-1]

                if decoupling_list[-1] == 'x':
                    decoupling_list.extend(['mx'])
                    break

                elif decoupling_list[-1] == 'mx':
                    decoupling_list.extend(['x'])
                    break

                elif decoupling_list[-1] == 'y':
                    decoupling_list.extend(['my'])
                    break

                else: 
                    sys.exit("There was a problem generating your decoupling list, last pulse not x, mx, y.")


            else:
                sys.exit("There was a problem generating your decoupling list.")

                ### HOW TO BREAK THE WHOLE THINGY???

        return decoupling_list


    def pulse_caller(self, pulsetype , refpoint = 'end', refpoint_new = 'start' , start= 0 ):

        self.e1.add(pulse.cp(pulsetype),
                            refpulse        = 'pulse%d' % (self.n-1),
                            refpoint        = refpoint,
                            refpoint_new    = refpoint_new,
                            name            = 'pulse%d' % self.n,
                            start           = start)

        self.n +=1


    def generate_pi(self, pulse_type):
        """
        This function builds pi pulses from pi/2 pulses around x and y.

        Note this is currently adapted to generate pi pulses directly for debugging.
        """

        if self.pi_name == 'Hermite_pi_length':
            if pulse_type == 'x':
                dec_pls = self.pulse_xpi

            if pulse_type == 'mx':
                dec_pls = self.pulse_mxpi

            if pulse_type == 'y':
                dec_pls = self.pulse_ypi

            if pulse_type == 'my':
                dec_pls = self.pulse_mypi
         
            self.pulse_caller(pulsetype = dec_pls, start = self.start_time)

        elif self.pi_name == 'Hermite_pi2_length':

            if pulse_type == 'x':
                dec_pls = self.pulse_xpi2

            if pulse_type == 'mx':
                dec_pls = self.pulse_mxpi2

            if pulse_type == 'y':
                dec_pls = self.pulse_ypi2

            if pulse_type == 'my':
                dec_pls = self.pulse_mypi2


            self.pulse_caller(pulsetype = dec_pls, start = self.start_time)
                    
            self.pulse_caller(pulsetype = dec_pls, start = 0)

        else:
            sys.exit("Problem in the decoupling pulse builidng.")
       

    def generate_subsequence(self, first_fiducial = False, seq='x'):
        """
        This function is used to create the subsequences we need, i.e. fiducials and germs

        NEEDED CHANGE: MAKE S.T. WE CAN DISTINGUISH BETWEEN XYXY AND MXY E.G.
        """

        ## NEED TO CODE IN THE DIFFERENCE BETWEEN FIRST FIDUCIAL AND GERM AND LAST FIDUCIAL. REALLY?
        #In case we have the null fiducial, just return a wait pulse
        if seq == 'e':
            self.start_time = 2*self.params['tau_larmor']-self.params[self.pi_name]
            if self.pi_name == 'Hermite_pi2_length':
                self.start_time -=self.params[self.pi_name]

        else:
            #First we should try and see how we need to do the spacing. What is the sequence length itself?
            #Need to subtract one wait time here since 2 pulses only have one wait step in between
            t_total_subseq = len(seq)*(self.params['Hermite_pi2_length']+self.params['wait_time'])-self.params['wait_time']

            #From this we can fiure out how much time we can have before and after a sequence to space 
            #everything symmetric around the center of a sequence
            t_around_subseq = (2*self.params['tau_larmor'] - t_total_subseq-self.params[self.pi_name])/2

            if self.pi_name == 'Hermite_pi2_length':
                t_around_subseq -=self.params[self.pi_name]/2

            self.start_time = t_around_subseq
            
            if first_fiducial:
                # self.start_time = self.params[self.pi_name]/2
                self.start_time = 0

            for i in range(len(seq)):

                if seq[i] == 'x':
                    self.pulse_caller(pulsetype = self.pulse_xpi2, start = self.start_time)
                    self.start_time = self.params['wait_time']
                    
                elif seq[i] == 'y':
                    self.pulse_caller(pulsetype = self.pulse_ypi2, start = self.start_time)
                    self.start_time = self.params['wait_time']

                elif seq[i] == 'm':
                    self.pulse_caller(pulsetype = self.pulse_mxpi2, start = self.start_time)
                    self.start_time = self.params['wait_time']
                    

                elif seq[i] == 'e': 
                    self.start_time += self.params['wait_time']
                    self.start_time += self.params[self.pi_name]


                else:
                    print "Seq exception", seq[i]
                    sys.exit("A horrible mistake happened. Check you subsequence building routine.")

            #At the end we need to add the time around the sequence
            self.start_time = t_around_subseq 


    def generate_sequence(self, pi = True, upload=True, **kw):

        #Variable to count pulse names up
        self.n = 1

        ###
        # First let us define the necessary pulses.
        ###

        # rotations pi2
        self.pulse_xpi2  =   kw.get('x_pulse_pi2', None)
        self.pulse_ypi2  =   kw.get('y_pulse_pi2', None)
        self.pulse_mxpi2 =   kw.get('x_pulse_mpi2', None)
        self.pulse_mypi2 =   kw.get('y_pulse_mpi2', None)

        # rotations pi
        self.pulse_xpi  =   kw.get('x_pulse_pi', None)
        self.pulse_ypi  =   kw.get('y_pulse_pi', None)
        self.pulse_mxpi =   kw.get('x_pulse_mpi', None)
        self.pulse_mypi =   kw.get('y_pulse_mpi', None)

        # waiting element        
        self.T = pulse.SquarePulse(channel='MW_Imod', name='delay',
            length = 3000e-9, amplitude = 0.)

        # Adwin sync plse that we need to send out after each sequence
        self.adwin_sync = pulse.SquarePulse(channel='adwin_sync',
           length = self.params['AWG_to_adwin_ttl_trigger_duration'],
           amplitude = 2)

        ###
        # Now let us create the decoupling sequence, including the germs. 
        ###
        elements = []

        ###
        #Apply the right name for spacing the pulses correctly
        ###
        if pi: self.pi_name = 'Hermite_pi_length'
        else: self.pi_name = 'Hermite_pi2_length'
        
        for k in range(self.params['pts']):
            # print self.params['run_numbers'][k]
            self.e1 = element.Element('Germ_sequence_%d' % self.params['run_numbers'][k], pulsar=qt.pulsar,
                    global_time = True)

            #Make the decoupling list. Idea is to put a full xy8 sequence between subsequent germs.
            decoupling_seq = self.generate_decoupling_list(k)

            #Initialize the C13 spin
            elements.append(pulsar_msmt.MBI._MBI_element(self, name='CNOT%d' % k))

            for i in range(self.params['N_decoupling'][k]+1):
                if i == 0:
                    self.e1.add(pulse.cp(self.T, 
                                        length = self.params['initial_msmt_delay']), 
                                        name='pulse%d' % self.n, 
                                        refpoint_new = 'start')
                    self.n +=1
                
                    #Generate the first fiducial and decoupling pulse
                    self.generate_subsequence(first_fiducial = True, seq=self.params['fid_1'][k])
                    self.generate_pi(decoupling_seq[i])

                #If we are at the last position then build the second fiducial
                elif i == self.params['N_decoupling'][k]:

                    self.generate_subsequence(seq=self.params['fid_2'][k])

                #If it is a germ sequence with germs everywhere then go here
                elif self.params['sequence_type']== 'all':
                    self.generate_subsequence(seq=self.params['germ'][k])
                    self.generate_pi(decoupling_seq[i])

                else:
                    self.start_time = 2*self.params['tau_larmor']-self.params[self.pi_name]
                    self.generate_pi(decoupling_seq[i])


            self.pulse_caller(pulsetype = self.adwin_sync, start=0)

            elements.append(self.e1)

        # create a sequence from the pulses
        seq = pulsar.Sequence('Single germ sequence with AWG timing with {} pulses'.format(self.params['pulse_type']))

        for e in elements:
            seq.append(name=e.name, wfname=e.name, trigger_wait=True)

        # upload the waveforms to the AWG
        if upload:
            if upload=='old_method':
                qt.pulsar.upload(*elements)
                qt.pulsar.program_sequence(seq)
            else:
                qt.pulsar.program_awg(seq,*elements)


# class GateSetNoTriggers(pulsar_msmt.PulsarMeasurement):
class GateSetNoDecoupling(pulsar_msmt.MBI):
    """
    Class used to generate a gate set tomography sequence without decoupling. 
    generate_sequence needs to be supplied with a xpi2_pulse and a ypi2_pulse as kw.
    """
    mprefix = 'GateSetTomographyNoDecoupling'

    def autoconfig(self):
        pulsar_msmt.MBI.autoconfig(self)

    def generate_subsequence(self, seq='x'):
        """
        This function is used to create the subsequences we need, i.e. fiducials and germs
        """

        ## NEED TO CODE IN THE DIFFERENCE BETWEEN FIRST FIDUCIAL AND GERM AND LAST FIDUCIAL. REALLY?
        #In case we have the null fiducial, just return a wait pulse
        if seq =='e':
            return

        else:
            for i in range(len(seq)):

                if seq[i] == 'x':
                    self.e1.add(pulse.cp(self.pulse_xpi2),
                                        refpulse = 'pulse%d' % (self.n-1),
                                        refpoint = 'end',
                                        refpoint_new = 'start',
                                        name = 'pulse%d' % self.n,
                                        start = 0)
                    self.n +=1
                    
                elif seq[i] == 'y':
                    self.e1.add(pulse.cp(self.pulse_ypi2),
                                        refpulse = 'pulse%d' % (self.n-1),
                                        refpoint = 'end',
                                        refpoint_new = 'start',
                                        name = 'pulse%d' % self.n,
                                        start = 0)
                    self.n +=1

                elif seq[i] == 'm':
                    self.e1.add(pulse.cp(self.pulse_mxpi2),
                                        refpulse = 'pulse%d' % (self.n-1),
                                        refpoint = 'end',
                                        refpoint_new = 'start',
                                        name = 'pulse%d' % self.n,
                                        start =0)
                    self.n +=1 

                elif seq[i] != 'e': 
                    print "Seq exception", seq[i]
                    sys.exit("A horrible mistake happened. Check you subsequence building routine.")



    def generate_sequence(self, upload=True, **kw):

        ###
        # First let us define the necessary pulses.
        ###

        # rotations pi2
        self.pulse_xpi2  =   kw.get('x_pulse_pi2', None)
        self.pulse_ypi2  =   kw.get('y_pulse_pi2', None)
        self.pulse_mxpi2 =   kw.get('x_pulse_mpi2', None)
        self.pulse_mypi2 =   kw.get('y_pulse_mpi2', None)

        # waiting element        
        self.T = pulse.SquarePulse(channel='MW_Imod', name='delay',
            length = 3000e-9, amplitude = 0.)

        # Adwin sync plse that we need to send out after each sequence
        self.adwin_sync = pulse.SquarePulse(channel='adwin_sync',
           length = self.params['AWG_to_adwin_ttl_trigger_duration'],
           amplitude = 2)

        ###
        # Now let us create the sequence, including the germs. 
        ###
        elements = []

        self.n = 0
        for k in range(self.params['pts']):

            self.e1 = element.Element('Single_germ_sequence_%d' % self.params['run_numbers'][k], pulsar=qt.pulsar,
                    global_time = True)

            #Some varibales I need to keep track of what we are doing
            last_germ = len(self.params['germ_position'])

            elements.append(pulsar_msmt.MBI._MBI_element(self, name='CNOT%d' % k))

            self.e1.add(pulse.cp(self.T, 
                                        length = self.params['initial_msmt_delay']), 
                                        name='pulse%d' % self.n, 
                                        refpoint_new = 'start')

            self.n +=1

            self.generate_subsequence(seq=self.params['fid_1'][k])

            for i in range(self.params['N_decoupling'][k]):
                self.generate_subsequence(seq=self.params['germ'][k])

            self.generate_subsequence(seq=self.params['fid_2'][k])
            self.e1.add(self.adwin_sync, refpulse = 'pulse%d' % (self.n-1),
                                        refpoint = 'end',
                                        refpoint_new = 'start')

            elements.append(self.e1)

        # create a sequence from the pulses
        seq = pulsar.Sequence('Single germ sequence with AWG timing with {} pulses'.format(self.params['pulse_type']))

        for e in elements:
            seq.append(name=e.name, wfname=e.name, trigger_wait=True)

        # upload the waveforms to the AWG
        if upload:
            if upload=='old_method':
                qt.pulsar.upload(*elements)
                qt.pulsar.program_sequence(seq)
            else:
                qt.pulsar.program_awg(seq,*elements)






class ElectronT2NoTriggers(pulsar_msmt.PulsarMeasurement):
    """
    Class to generate an electron Hahn echo sequence with a single refocussing pulse.
    generate_sequence needs to be supplied with a pi2_pulse as kw.
    """
    mprefix = 'ElectronT2NoTriggers'

    def autoconfig(self):
        self.params['sequence_wait_time'] = \
            int(np.ceil(np.max(self.params['evolution_times'])*1e6)+10)

        pulsar_msmt.PulsarMeasurement.autoconfig(self)

    def generate_sequence(self, upload=True, **kw):

        # define the necessary pulses
        
        # rotations
        pulse_pi2 = kw.get('pulse_pi2', None)
        pulse_pi = kw.get('pulse_pi', None)

        # waiting element        
        T = pulse.SquarePulse(channel='MW_Imod', name='delay',
            length = 200e-9, amplitude = 0.)

        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = self.params['AWG_to_adwin_ttl_trigger_duration'],
            amplitude = 2)

        # self_trigger = pulse.SquarePulse(channel='self_trigger',
        #     length = self.params['self_trigger_duration'],
        #     amplitude = 2)

        # make the elements, one for each evolution time
        elements = []
        for i in range(self.params['pts']):

            e1 = element.Element('ElectronT2_notrigger_pt-%d_A' % i, pulsar=qt.pulsar,
                global_time = True)
            e1.append(pulse.cp(T,
                length = 3000e-9))

            e1.append(pulse.cp(pulse_pi2,
                phase = self.params['pulse_sweep_pi2_phases1'][i]))

            e1.append(pulse.cp(T,
                length = self.params['evolution_times'][i] / 2.))

            e1.append(pulse.cp(pulse_pi,
                phase = self.params['pulse_sweep_pi_phases'][i]))

            e1.append(pulse.cp(T,
                length = self.params['evolution_times'][i] / 2.))

            e1.append(pulse.cp(pulse_pi2,
                phase = self.params['pulse_sweep_pi2_phases2'][i]))

            e1.append(adwin_sync)

            elements.append(e1)
        # return_e=e
        # create a sequence from the pulses
        seq = pulsar.Sequence('Electron T2 with AWG timing with {} pulses'.format(self.params['pulse_type']))
        for e in elements:
            seq.append(name=e.name, wfname=e.name, trigger_wait=True)

        # upload the waveforms to the AWG
        if upload:
            if upload=='old_method':
                qt.pulsar.upload(*elements)
                qt.pulsar.program_sequence(seq)
            else:
                qt.pulsar.program_awg(seq,*elements)

class ElectronRefocussingTriggered(DelayTimedPulsarMeasurement):
    """
    Class to generate an electron Hahn echo sequence with a single refocussing pulse.
    The first evolution time is timed using a fixed delay line and the marker is sweeped.
    generate_sequence needs to be supplied with a pi2_pulse as kw.
    """
    mprefix = 'ElectronRefocussingTriggered'

    def autoconfig(self):
        self.params['sequence_wait_time'] = \
            int(np.ceil(np.max(2*self.params['refocussing_time'])*1e6)+100)


        DelayTimedPulsarMeasurement.autoconfig(self)

    def generate_sequence(self, upload=True, **kw):

        # define the necessary pulses
        
        # rotations
        pulse_pi2 = kw.get('pulse_pi2', None)
        pulse_pi = kw.get('pulse_pi', None)
        evolution_1_self_trigger = kw.get('evolution_1_self_trigger', True)
        evolution_2_self_trigger = kw.get('evolution_2_self_trigger', True)

        # waiting element        
        empty_pulse = pulse.SquarePulse(channel='adwin_sync', name='delay',
            length = 1000e-9, amplitude = 0.)

        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = self.params['AWG_to_adwin_ttl_trigger_duration'],
            amplitude = 2.)

        self_trigger = pulse.SquarePulse(channel='self_trigger',
            length = self.params['self_trigger_duration'],
            amplitude = 2.)

        HH_sync = pulse.SquarePulse(
            channel='sync',
            length=self.params['delay_HH_sync_duration'],
            amplitude=2.
        )

        HH_trigger = pulse.SquarePulse(
            channel='self_trigger_sync',
            length=self.params['delay_HH_trigger_duration'],
            amplitude=2.
        )

        initial_pulse_delay = 3e-6

        # make the elements, one for each evolution time
        elements = []
        for i in range(self.params['pts']):

            e = element.Element('ElectronT2_triggered_pt-%d_A' % i, pulsar=qt.pulsar)
            initial_wait_id = e.add(pulse.cp(empty_pulse,
                length = initial_pulse_delay))

            if self.params['do_delay_HH_trigger'] > 0:
                e.add(
                    HH_sync,
                    refpulse=initial_wait_id,
                    refpoint='start',
                    refpoint_new='start',
                    start=self.params['delay_HH_sync_offset']
                )

            first_pulse_id = e.add(
                pulse.cp(pulse_pi2),
                refpulse=initial_wait_id,
                refpoint='end',
                start=0.0
            )

            if (evolution_1_self_trigger):
                # tie the self trigger pulse to the center of the pi/2 pulse
                e.add(pulse.cp(self_trigger), 
                    refpulse = first_pulse_id, 
                    refpoint = 'center', # used to be end during fixed delay runs
                    refpoint_new = 'start',
                    start = (
                        self.params['refocussing_time'][i] 
                        + self.params['defocussing_offset'][i] 
                        - self.params['self_trigger_delay'][i]
                        + self.params['self_trigger_pulse_timing_offset']
                        ))

                if self.params['do_delay_HH_trigger'] > 0:
                    e.add(pulse.cp(HH_trigger),
                          refpulse=first_pulse_id,
                          refpoint='center',  # used to be end during fixed delay runs
                          refpoint_new='start',
                          start=(
                              self.params['refocussing_time'][i]
                              + self.params['defocussing_offset'][i]
                              - self.params['self_trigger_delay'][i]
                              + self.params['self_trigger_pulse_timing_offset']
                          ))

                elements.append(e)
                # we need to tie the start of the element to the center of the pi-pulse
                # if we would do this naively by just starting the pi-pulse at the beginning of
                # the element, the effective delay would change for different pulse lengths
                # or pulsemod delays because they would shift the pi-pulse around with respect
                # to the start of the element
                e = element.Element('ElectronT2_triggered_pt-%d_B' % i, pulsar=qt.pulsar)

                dummy_start_pulse_1 = e.add(pulse.cp(empty_pulse, length=10e-9))
                second_pulse_id = e.add(pulse.cp(pulse_pi),
                    refpulse = dummy_start_pulse_1,
                    refpoint = 'start',
                    refpoint_new = 'center',
                    start = self.params['delayed_element_run_up_time']
                )
            else:
                second_pulse_id = e.add(pulse.cp(pulse_pi),
                    refpulse = first_pulse_id,
                    refpoint = 'center',
                    refpoint_new = 'center',
                    start = (
                        self.params['refocussing_time'][i]
                        + self.params['defocussing_offset'][i]
                        )
                    )

            if (evolution_2_self_trigger):
                e.add(pulse.cp(self_trigger),
                    refpulse = second_pulse_id,
                    refpoint = 'center', # used to be end during fixed delay runs
                    refpoint_new = 'start',
                    start = (
                        self.params['refocussing_time'][i]
                        - self.params['self_trigger_delay'][i]
                        + self.params['self_trigger_pulse_timing_offset']
                        ))
                if self.params['do_delay_HH_trigger'] > 0:
                    e.add(pulse.cp(HH_trigger),
                          refpulse=second_pulse_id,
                          refpoint='center',  # used to be end during fixed delay runs
                          refpoint_new='start',
                          start=(
                              self.params['refocussing_time'][i]
                              - self.params['self_trigger_delay'][i]
                              + self.params['self_trigger_pulse_timing_offset']
                          ))
                elements.append(e)

                # same story about tieing the start of the element to the center of the pulse
                # applies here
                e = element.Element('ElectronT2_triggered_pt-%d_C' % i, pulsar=qt.pulsar)

                dummy_start_pulse_2 = e.add(pulse.cp(empty_pulse, length=10e-9))
                final_pulse_id = e.add(pulse.cp(pulse_pi2),
                    refpulse = dummy_start_pulse_2,
                    refpoint = 'start',
                    refpoint_new = 'center',
                    start = self.params['delayed_element_run_up_time']
                )
            else:
                final_pulse_id = e.add(pulse.cp(pulse_pi2),
                    refpulse = second_pulse_id,
                    refpoint = 'center',
                    refpoint_new = 'center',
                    start = self.params['refocussing_time'][i]
                )


            adwin_sync_id = e.add(adwin_sync, refpulse=final_pulse_id)
            e.add(pulse.cp(adwin_sync, length=10e-9, amplitude = 0.), refpulse=adwin_sync_id)
            elements.append(e)
            
        # return_e=e
        # create a sequence from the pulses
        seq = pulsar.Sequence('Electron refocussing with delay trigger with {} pulses'.format(self.params['pulse_type']))
        for e in elements:
            seq.append(name=e.name, wfname=e.name, trigger_wait=True)

        # upload the waveforms to the AWG
        if upload:
            if upload=='old_method':
                qt.pulsar.upload(*elements)
                qt.pulsar.program_sequence(seq)
            else:
                qt.pulsar.program_awg(seq,*elements)

class DummySelftriggerSequence(m2.LocalAdwinControlledMeasurement):
    """
    Class to upload a sequence that contains only self-trigger pulses, to be run in continuous mode by the AWG
    """
    adwin_process = "dummy_tico_selftrigger"

    def autoconfig(self):
        self.params['sweep_length'] = self.params['pts']

        m2.AdwinControlledMeasurement.autoconfig(self)

        if self.params['do_tico_delay_control']:
            if not 'delay_cycles' in self.params:
                # convert delay times into number of cycles
                delay_cycles = (
                    (
                        np.array(self.params['delay_times']) 
                        - self.params['delay_time_offset']
                    ) 
                    / self.params['delay_clock_cycle_time']
                )
                if np.min(delay_cycles) < self.params['minimal_delay_cycles']:
                    raise Exception("Desired delay times are too short")
                self.params['delay_cycles'] = delay_cycles

            self.set_delay_cycles(self.params['delay_cycles'])

    def set_delay_cycles(self, delay_cycles):
        int_delay_cycles = np.array(delay_cycles, dtype=np.int32)
        print(int_delay_cycles)
        self.adwin.set_dummy_tico_selftrigger_var(delay_cycles = int_delay_cycles)


    def run(self, autoconfig=True):
        if autoconfig:
            self.autoconfig()

        self.start_adwin_process(stop_processes=['counter'])
        qt.msleep(1)
        self.start_keystroke_monitor('abort',timer=False)

        while self.adwin_process_running():
            self._keystroke_check('abort')
            if self.keystroke('abort') in ['q','Q']:
                print 'aborted.'
                aborted = True
                self.stop_keystroke_monitor('abort')
                break

        self.stop_adwin_process()

    def generate_sequence(self, upload=True, period=200e-6, on_time=2e-6):

        self_trigger = pulse.SquarePulse(channel='self_trigger',
            length = on_time,
            amplitude = 2.)

        T = pulse.SquarePulse(channel='self_trigger', name='delay',
            length = period - on_time, amplitude = 0)

        elements = []
        period_element = element.Element('Dummy_selftrigger_element', pulsar=qt.pulsar, global_time=True)
        period_element.append(self_trigger)
        period_element.append(T)
        elements.append(period_element)

        seq = pulsar.Sequence("Dummy self-trigger sequence")
        seq.append(name=period_element.name, 
            wfname=period_element.name, 
            trigger_wait=True, 
            # goto_target=period_element.name
            )

        # upload the waveforms to the AWG
        if upload:
            if upload=='old_method':
                qt.pulsar.upload(*elements)
                qt.pulsar.program_sequence(seq)
            else:
                qt.pulsar.program_awg(seq,*elements)         

    def finish(self):
        m2.AdwinControlledMeasurement.finish(self, save_params = False, save_cfg_files = False, save_stack = False, save_ins_settings = False)