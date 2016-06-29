import qt
import numpy as np
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

### reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.scripts.mbi.mbi_funcs as funcs; reload(funcs)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

### msmt class
class NSpinflips(pulsar_msmt.MBI):
    mprefix = 'NSpinflips'

    def generate_sequence(self, upload=True,debug=False):
        # MBI element
        mbi_elt = self._MBI_element()

        # electron manipulation pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 2e-6, amplitude = 0)

        # CORPSE_pi = pulselib.IQ_CORPSE_pi_pulse('msm1 CORPSE pi-pulse',
        #     I_channel = 'MW_Imod',
        #     Q_channel = 'MW_Qmod',
        #     PM_channel = 'MW_pulsemod',
        #     PM_risetime = self.params['MW_pulse_mod_risetime'],
        #     frequency = self.params['msm1_CORPSE_pi_mod_frq'],
        #     amplitude = self.params['msm1_CORPSE_pi_amp'],
        #     length_60 = self.params['msm1_CORPSE_pi_60_duration'],
        #     length_m300 = self.params['msm1_CORPSE_pi_m300_duration'],
        #     length_420 = self.params['msm1_CORPSE_pi_420_duration'])

        SP = pulse.SquarePulse(channel = 'AOM_Newfocus',
            length = self.params['AWG_SP_duration'],
            amplitude = self.params['AWG_SP_amplitude'])

        pi2pi_m1 = pulselib.MW_IQmod_pulse('pi2pi pulse mI=-1',
            I_channel='MW_Imod', Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod', Sw_channel='MW_switch',
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            frequency = self.params['pi2pi_mIm1_mod_frq'],
            amplitude = self.params['pi2pi_mIm1_amp'],
            length = self.params['pi2pi_mIm1_duration'])

        X = pulselib.MW_IQmod_pulse('electron X-Pi-pulse',
            I_channel='MW_Imod', Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod', Sw_channel='MW_switch',
            frequency = self.params['AWG_MBI_MW_pulse_mod_frq'],
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            Sw_risetime = self.params['MW_switch_risetime'],
            length = self.params['fast_pi_duration'],
            amplitude = self.params['fast_pi_amp'],
            phase =  self.params['X_phase'])

        sync_elt = element.Element('adwin_sync', pulsar=qt.pulsar)
        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = 10e-6, amplitude = 2)
        sync_elt.append(adwin_sync)

        wait_1us = element.Element('1us_delay', pulsar=qt.pulsar)
        wait_1us.append(pulse.cp(T, length=1e-6))

        SP_elt = element.Element('SP_element', pulsar=qt.pulsar)
        SP_elt.append(T, X, T, SP, T)

        RO_elt = element.Element('RO_element', pulsar=qt.pulsar)
        RO_elt.append(T, pi2pi_m1)

        seq = pulsar.Sequence('N spin flips')
        for i,r in enumerate(self.params['AWG_sequence_repetitions']):

            seq.append(name = 'MBI-%d' % i,
                wfname = mbi_elt.name,
                trigger_wait = True,
                goto_target = 'MBI-%d' % i,
                jump_target = 'SP-{}'.format(i))

            if r > 0:
                seq.append(name = 'SP-{}'.format(i),
                    wfname = SP_elt.name,
                    trigger_wait = True,
                    repetitions = r)
            else:
                seq.append(name = 'SP-{}'.format(i),
                    wfname = wait_1us.name,
                    trigger_wait = True)

            seq.append(name = 'RO-{}'.format(i),
                wfname = RO_elt.name)
            seq.append(name = 'sync-{}'.format(i),
                wfname = sync_elt.name)


        combined_list_of_elements = [mbi_elt, sync_elt, wait_1us, SP_elt, RO_elt]
        # program AWG
        if upload:
            qt.pulsar.program_awg(seq, *combined_list_of_elements, debug=debug)

        #     qt.pulsar.upload()
        # qt.pulsar.program_sequence(seq)


def nspinflips(name):
    m = NSpinflips(name)
    funcs.prepare(m)

    SP_power = 200e-9
    m.params['AWG_SP_amplitude'] = qt.instruments['NewfocusAOM'].power_to_voltage(
        SP_power, controller='sec')
    m.params['AWG_SP_duration'] = 5e-6

    pts = 11
    step_size = 150
    m.params['pts'] = pts
    m.params['AWG_sequence_repetitions'] = np.arange(pts) * step_size
    m.params['reps_per_ROsequence'] = 1500

    # for testing
    m.params['pi2pi_mIm1_mod_frq'] = 250e6
    m.params['pi2pi_mIm1_amp'] = 0.0 #0.05
    m.params['pi2pi_mIm1_duration'] = 1e-6

    # for the autoanalysis
    m.params['sweep_name'] = 'SP cycles'
    m.params['sweep_pts'] = m.params['AWG_sequence_repetitions']

    funcs.finish(m, upload=True, debug=False)

if __name__ == '__main__':
    nspinflips('The111No1_Sil18')
