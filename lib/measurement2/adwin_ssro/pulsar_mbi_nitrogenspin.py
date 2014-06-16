import numpy as np
import qt

from measurement.lib.pulsar import pulse, pulselib, element, pulsar
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt


class NitrogenRabi(pulsar_msmt.MBI):
    mprefix = 'PulsarMBINitrogenRabi'

    def generate_sequence(self, upload=True, debug=False):
        # MBI element
        mbi_elt = self._MBI_element()

        # electron manipulation pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 750e-9, amplitude = 0)

        X = pulselib.MW_IQmod_pulse('MW pulse',
            I_channel = 'MW_Imod',
            Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'] )
        N_pulse = pulselib.RF_erf_envelope(
            channel = 'RF',
            frequency = self.params['N_0-1_splitting_ms-1'])
        
        pi2pi_0 = pulselib.MW_IQmod_pulse('pi2pi pulse mI=0',
        I_channel = 'MW_Imod',
        Q_channel = 'MW_Qmod',
        PM_channel = 'MW_pulsemod',
        PM_risetime = self.params['MW_pulse_mod_risetime'],
        frequency = self.params['pi2pi_mI0_mod_frq'],
        amplitude = self.params['pi2pi_mI0_amp'],
        length = self.params['pi2pi_mI0_duration'])
        
        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = self.params['AWG_to_adwin_ttl_trigger_duration'],
            amplitude = 2)

        # electron manipulation elements
        elts = []
        for i in range(self.params['pts']):
            e = element.Element('NRabi_pt-%d' % i, pulsar=qt.pulsar,
                global_time = True)
            e.append(T)
            e.append(
                    pulse.cp(X,
                        frequency = self.params['MW_modulation_frequency'],
                        amplitude = self.params['MW_pi_pulse_amp'],
                        length = self.params['MW_pi_pulse_duration']))
            e.append(T)
            for j in range(self.params['RF_pulse_multiplicities'][i]):
                e.append(
                    pulse.cp(N_pulse,
                        frequency = self.params['RF_pulse_frqs'][i],
                        amplitude = self.params['RF_pulse_amps'][i],
                        length = self.params['RF_pulse_durations'][i]))

                e.append(
                    pulse.cp(T, length=self.params['RF_pulse_delays'][i]))
            
            e.append(pulse.cp(pi2pi_0)) 
            e.append(pulse.cp(T))   
            e.append(adwin_sync)
            elts.append(e)

        # sequence
        seq = pulsar.Sequence('MBI Nitrogen Rabi sequence')
        for i,e in enumerate(elts):
            seq.append(name = 'MBI-%d' % i, wfname = mbi_elt.name,
                trigger_wait = True, goto_target = 'MBI-%d' % i,
                jump_target = e.name)
            seq.append(name = e.name, wfname = e.name,
                trigger_wait = True)

        # program AWG
        if upload:
            #qt.pulsar.upload(mbi_elt, *elts)
            qt.pulsar.program_awg(seq, mbi_elt, *elts , debug=debug)
        #qt.pulsar.program_sequence(seq)




