import numpy as np
import qt

from measurement.lib.pulsar import pulse, pulselib, element, pulsar
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
import measurement.lib.measurement2.measurement as m2
import pulse_select as ps
import sys

class DelayTimedPulsarMeasurement(pulsar_msmt.PulsarMeasurement):
    adwin_process = "integrated_ssro_delay_timing"
    mprefix = "DelayTiming"

    def autoconfig(self):
        pulsar_msmt.PulsarMeasurement.autoconfig(self)

        if self.params['do_delay_voltage_control']:
            if not 'delay_voltages' in self.params:
                fitfunc = self.params['delay_to_voltage_fitfunc']
                fitparams = self.params['delay_to_voltage_fitparams']
                self.params['delay_voltages'] = fitfunc(self.params['self_trigger_delay'], *fitparams)

                if (np.min(self.params['delay_voltages']) < 0 
                    or np.max(self.params['delay_voltages']) > 4 
                    or np.any(np.isnan(self.params['delay_voltages']))):
                    raise Exception("Delay voltages out of bound!")
            self.set_delay_voltages(self.params['delay_voltages'])

    def set_delay_voltages(self, voltage_list):
        self.adwin.set_integrated_ssro_delay_timing_var(delay_voltages = voltage_list)

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
        T = pulse.SquarePulse(channel='MW_Qmod', name='delay',
            length = 1000e-9, amplitude = 0.)

        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = self.params['AWG_to_adwin_ttl_trigger_duration'],
            amplitude = 2)

        self_trigger = pulse.SquarePulse(channel='self_trigger',
            length = self.params['self_trigger_duration'],
            amplitude = 3)

        initial_pulse_delay = 3e-6
        t_element_start_to_pulse_center = 200e-9

        # make the elements, one for each evolution time
        elements = []
        for i in range(self.params['pts']):

            e = element.Element('ElectronT2_triggered_pt-%d_A' % i, pulsar=qt.pulsar,
                global_time = True)
            e.append(pulse.cp(T,
                length = initial_pulse_delay))

            first_pulse_id = e.append(pulse.cp(pulse_pi2))

            if (evolution_1_self_trigger):
                # tie the self trigger pulse to the center of the pi/2 pulse
                e.add(pulse.cp(self_trigger), 
                    refpulse = first_pulse_id, 
                    refpoint = 'center', # used to be end during fixed delay runs
                    start = (
                        self.params['refocussing_time'][i] 
                        + self.params['defocussing_offset'][i] 
                        - self.params['self_trigger_delay'][i]
                        ))

                elements.append(e)
                # we need to tie the start of the pi-pulse element to the center of the pi-pulse
                # if we would do this naively by just starting the pi-pulse at the beginning of
                # the element, the effective delay would change for different pulse lengths
                # or pulsemod delays because they would shift the pi-pulse around with respect
                # to the start of the element
                e = element.Element('ElectronT2_triggered_pt-%d_B' % i, pulsar=qt.pulsar,
                    global_time = True)
                second_pulse_id = e.append(pulse.cp(pulse_pi))
                e.add(pulse.cp(T, length = 10e-9, amplitude = 0.),
                    refpulse = second_pulse_id,
                    refpoint = 'center',
                    start = -t_element_start_to_pulse_center)
            else:
                e.append(pulse.cp(T,
                    length = self.params['refocussing_time'][i] + self.params['defocussing_offset'][i]))
                second_pulse_id = e.append(pulse.cp(pulse_pi))

            if (evolution_2_self_trigger):
                e.add(pulse.cp(self_trigger),
                    refpulse = second_pulse_id,
                    refpoint = 'center', # used to be end during fixed delay runs
                    start = (
                        self.params['refocussing_time'][i]
                        - self.params['self_trigger_delay'][i]
                        ))
                elements.append(e)

                # same story about tieing the start of the element to the center of the pulse
                # applies here
                e = element.Element('ElectronT2_triggered_pt-%d_C' % i, pulsar=qt.pulsar,
                    global_time = True)
                final_pulse_id = e.append(pulse.cp(pulse_pi2))
                e.add(pulse.cp(T, length =10e-9, amplitude = 0.),
                    refpulse = final_pulse_id,
                    refpoint = 'center',
                    start = -t_element_start_to_pulse_center)

            else:
                e.append(pulse.cp(T,
                    length = self.params['refocussing_time'][i]))
                final_pulse_id = e.append(pulse.cp(pulse_pi2))


            e.append(adwin_sync)
            e.append(pulse.cp(T,
                length = 10e-9))
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
    adwin_process = "dummy_selftrigger"

    def autoconfig(self):
        self.params['sweep_length'] = self.params['pts']

        m2.AdwinControlledMeasurement.autoconfig(self)

        if self.params['do_delay_voltage_control'] > 0:
            if not 'delay_voltages' in self.params:
                fitfunc = self.params['delay_to_voltage_fitfunc']
                fitparams = self.params['delay_to_voltage_fitparams']
                self.params['delay_voltages'] = fitfunc(self.params['self_trigger_delay'], *fitparams)

                if (np.min(self.params['delay_voltages']) < 0 
                    or np.max(self.params['delay_voltages']) > 4 
                    or np.any(np.isnan(self.params['delay_voltages']))):
                    raise Exception("Delay voltages out of bound!")
            print(self.params['delay_voltages'])
            self.set_delay_voltages(self.params['delay_voltages'])

    def set_delay_voltages(self, voltage_list):
        self.adwin.set_dummy_selftrigger_var(delay_voltages = voltage_list)

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