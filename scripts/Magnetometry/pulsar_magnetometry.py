import numpy as np
import qt

from measurement.lib.pulsar import pulse, pulselib, element, pulsar
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt


class AdaptivePhaseEstimation(pulsar_msmt.Magnetometry):
    mprefix = 'adptv_estimation'

    def generate_sequence(self, upload=True, debug=False):
        # MBI element
        Ninit_elt = self._Ninit_element()

        # electron manipulation pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 100e-9, amplitude = 0)

        X = pulselib.MW_IQmod_pulse('MW pulse',
            I_channel = 'MW_Imod',
            Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'] )

        fpga_gate = pulselib.MW_pulse(name = 'fpga_gate_pulse', MW_channel='fpga_gate', amplitude = 4.0, length = 10e-9,
            PM_channel = 'MW_pulsemod', PM_risetime = self.params['MW_pulse_mod_risetime'])

        clock_pulse = pulse.clock_train (channel = 'fpga_clock', amplitude = 1, nr_up_points=2, nr_down_points=2, cycles= 1000)

        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = self.params['AWG_to_adwin_ttl_trigger_duration'],
            amplitude = 2)

        
        # electron manipulation elements
        elts = []
        for i in np.arange(self.params['adptv_steps']):
            e = element.Element('adpt_step_nr-%d' % i, pulsar=qt.pulsar,
                global_time = True)
            e.add(pulse.cp(clock_pulse, amplitude = 1.0, cycles = 700+int(0.25e9*self.params['ramsey_time'][i])))

            e.add(pulse.cp(T, length=1e-6))

            e.append(pulse.cp(X,
                        frequency = self.params['MW_pulse_mod_frqs'][i],
                        amplitude = self.params['MW_pulse_amps'][i],
                        length = self.params['MW_pulse_durations'][i]))
            e.append(pulse.cp(T, length=self.params['ramsey_time'][i]))

            e.append(pulse.cp(fpga_gate, amplitude = 4.0, length=self.params['fpga_mw_duration'][i]))
            e.append(T)
            e.append(adwin_sync)

            e.append(pulse.cp(T, length=100e-9))        
            elts.append(e)

        print 'Elements created...'
        print 'N-spin init repetitions:', self.params['init_repetitions']
        # sequence
        seq = pulsar.Sequence('Adaptive phase-estimation sequence')
        for i,e in enumerate(elts):
            seq.append(name = 'Ninit-%d' % i, wfname = Ninit_elt.name,
                trigger_wait = True, repetitions=self.params['init_repetitions'])
            seq.append(name = e.name, wfname = e.name,
                trigger_wait = False)
        # program AWG
        if upload:
            qt.pulsar.program_awg(seq, Ninit_elt, *elts , debug=debug)
            print 'Done uploading!!'
        