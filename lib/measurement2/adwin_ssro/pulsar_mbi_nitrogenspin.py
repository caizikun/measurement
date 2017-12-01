import numpy as np
import qt

from measurement.lib.pulsar import pulse, pulselib, element, pulsar
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
import pulse_select as ps
import sys


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

class NitrogenRabiDirectRF(pulsar_msmt.MBI):
    """
    MJD 201711
    Measurement class for a Rabi flop with direct RF
    Input:
        name(string): Name of the measurement you want to run
    
    Uploads a measurement sequence to the AWG

    Nitrogen init: weak e Pi pulse 


    """
    mprefix = 'PulsarMBINitrogenRabi'

    def generate_RF_pulse_element(self,Gate):
        '''
        Written by MB. 
        Generate arbitrary RF pulse gate, so a pulse that is directly created by the AWG.
        Pulse is build up out of a starting element, a repeated middle element and an end
        element to save the memory of the AWG.

        Copied by MJD 201711

        
        '''

        ###################
        ## Set paramters ##
        ###################

        Gate.scheme = 'RF_pulse'

        length     = Gate.length
        freq       = Gate.RFfreq
        amplitude  = Gate.amplitude
        prefix     = Gate.prefix
        phase      = Gate.phase


        list_of_elements = []

        X = pulselib.RF_erf_envelope(
            channel = 'RF',
            length = length,
            frequency = freq,
            amplitude = amplitude,
            phase = phase)

        e_middle = element.Element('%s_RF_pulse_middle' %(prefix),  pulsar=qt.pulsar,
                global_time = True)
        e_middle.append(pulse.cp(X))
        list_of_elements.append(e_middle)

        Gate.tau_cut = 1e-6
        Gate.wait_time = Gate.length + 2e-6
        Gate.elements= list_of_elements
        
        return Gate

    def generate_sequence(self, upload=True, debug=False):
        # MBI element
        mbi_elt = self._MBI_element()

        # electron manipulation pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 1000e-9, amplitude = 0)

        X = pulselib.MW_IQmod_pulse('MW pulse',
            I_channel = 'MW_Imod',
            Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'] )

        # X = pulselib.HermitePulse_Envelope_IQ('MW pulse',
        #     I_channel = 'MW_Imod',
        #     Q_channel = 'MW_Qmod',
        #     PM_channel = 'MW_pulsemod',
        #     PM_risetime = self.params['MW_pulse_mod_risetime'] )

        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = self.params['AWG_to_adwin_ttl_trigger_duration'],
            amplitude = 2)

        # electron manipulation elements
        elts = []
        for i in range(self.params['pts']):
            e = element.Element('ERabi_pt-%d' % i, pulsar=qt.pulsar,
                global_time = True)
            e.append(T)

            for j in range(self.params['MW_pulse_multiplicities'][i]):
                e.append(
                    pulse.cp(X,
                        frequency = self.params['MW_pulse_mod_frqs'][i],
                        amplitude = self.params['MW_pulse_amps'][i],
                        length = self.params['MW_pulse_durations'][i]))
                e.append(
                    pulse.cp(T, length=self.params['MW_pulse_delays'][i]))

            e.append(adwin_sync)
            elts.append(e)

        # sequence
        seq = pulsar.Sequence('MBI Electron Rabi sequence')
        for i,e in enumerate(elts):
            seq.append(name = 'MBI-%d' % i, wfname = mbi_elt.name,
                trigger_wait = True, goto_target = 'MBI-%d' % i,
                jump_target = e.name)
            seq.append(name = e.name, wfname = e.name,
                trigger_wait = True)
            # seq.append(name = 'RO-%d' % i, wfname = mbi_elt.name,
            #     trigger_wait = True, goto_target = 'MBI-%d' % i,
            #     jump_target = e.name)
        print 'MBI at', self.params['AWG_MBI_MW_pulse_ssbmod_frq']
        print 'MW rotations at', self.params['MW_pulse_mod_frqs'][i]
        # program AWG
        if upload:
            #qt.pulsar.upload(mbi_elt, *elts)
            qt.pulsar.program_awg(seq, mbi_elt, *elts , debug=debug)
        #qt.pulsar.program_sequence(seq)

