'''
Generates AWG elements for a phase measurement sequence
'''

import numpy as np
import qt
import msvcrt

#reload all parameters and modules
execfile(qt.reload_current_setup)

import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
from measurement.lib.pulsar import pulse, pulselib, element, pulsar


SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']


class PhaseCheckPulse(PulsarMeasurement):

    mprefix = 'PhaseCheckPulse'

    def autoconfig(self):

        PulsarMeasurement.autoconfig(self)

    def generate_sequence(self,upload=True,debug=False):
        """
        generate the sequence for the purification experiment.
        Tries to be as general as possible in order to suffice for multiple calibration measurements
        """
        # Trig = pulse.SquarePulse(channel = 'adwin_sync', length = 1.5e-6, amplitude = 2)

        T_pos = pulse.SquarePulse(channel='EOM_AOM_Matisse', name='delay')
        T.amplitude = 2.
        T.length = 1e-6

        T_neg = pulse.SquarePulse(channel='EOM_AOM_Matisse', name='delay')
        T.amplitude = -2.
        T.length = 1e-6

        elements = []
        e = element.Element('PhaseCheckPulse', pulsar=qt.pulsar)
        e.append(T_pos)
        e.append(T_neg)
        elements.append(e)


        # create a sequence from the pulses
        seq = pulsar.Sequence('PhaseCheck')
        for e in elements:
            seq.append(name=e.name, wfname=e.name, trigger_wait=True, repetitions = repetitions)

         # upload the waveforms to the AWG
        if upload:
            if upload=='old_method':
                qt.pulsar.upload(*elements)
                qt.pulsar.program_sequence(seq)
            else:
                qt.pulsar.program_awg(seq,*elements)


def RunPhaseCheck(name, debug = False):

    m =PhaseCheckPulse(name)
   
    m.autoconfig()

    '''generate sequence'''
    m.generate_sequence(upload=True, debug=debug)
    
    m.run()
    m.save()
    m.finish()
    

if __name__ == '__main__':

    RunPhaseCheck(SAMPLE+'_'+'phaseCheck', debug=True)
    