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
                - self.params['minimal_delay_time']
            ) 
            / self.params['delay_clock_cycle_time'] 
            + self.params['minimal_delay_cycles']
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


class ElectronT2NoTriggers(pulsar_msmt.PulsarMeasurement):
    """
    Class to generate an electron Hahn echo sequence with a single refocussing pulse.
    generate_sequence needs to be supplied with a pi2_pulse as kw.
    """
    mprefix = 'ElectronT2NoTriggers'

    def autoconfig(self):
        self.params['sequence_wait_time'] = \
            int(np.ceil(np.max(self.params['evolution_times'])*1e6)+10)


        PulsarMeasurement.autoconfig(self)

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
        empty_pulse = pulse.SquarePulse(channel='MW_Qmod', name='delay',
            length = 1000e-9, amplitude = 0.)

        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = self.params['AWG_to_adwin_ttl_trigger_duration'],
            amplitude = 2)

        self_trigger = pulse.SquarePulse(channel='self_trigger',
            length = self.params['self_trigger_duration'],
            amplitude = 2)

        initial_pulse_delay = 3e-6

        # make the elements, one for each evolution time
        elements = []
        for i in range(self.params['pts']):

            e = element.Element('ElectronT2_triggered_pt-%d_A' % i, pulsar=qt.pulsar)
            e.add(pulse.cp(empty_pulse,
                length = initial_pulse_delay))

            first_pulse_id = e.append(pulse.cp(pulse_pi2))

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
                        - self.params['delayed_element_run_up_time']
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
                        - self.params['delayed_element_run_up_time']
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
                        - self.params['minimal_delay_time']
                    ) 
                    / self.params['delay_clock_cycle_time'] 
                    + self.params['minimal_delay_cycles']
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