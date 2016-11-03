'''
Generates AWG elements from locally stored parameters for the purifcation project.
Specifically contains the following output possiblities:
    - Barrett & Kok Entangling element
    - Single Optical Pi pulse entangling element

This setting is changed by merely adapting the local parameters adequately.

Norbert Kalb 2016
'''

from measurement.lib.pulsar import pulse, pulselib, element, pulsar, eom_pulses
import measurement.lib.measurement2.adwin_ssro.pulse_select as ps
import qt
import numpy as np

setup = qt.current_setup

def generate_sequence(self,upload=True,debug=False):
    """
    generate the sequence for the purification experiment.
    Tries to be as general as possible in order to suffice for multiple calibration measurements
    """


    ### initialize empty sequence and elements
    seq_elements = []
    combined_seq = pulsar.Sequence('PhaseCheck')

    ### create a list of gates according to the current sweep.
    for pt in range(self.params['pts']):

        # Trig = pulse.SquarePulse(channel = 'adwin_sync', length = 1.5e-6, amplitude = 2)

        T = pulse.SquarePulse(channel='EOM_AOM_Matisse', name='delay')
        T.amplitude = 0.
        T.length = 2e-6

        # make the elements - one for each ssb frequency
        elements = [] 
        seq = pulsar.Sequence('SSRO calibration (ms=0,+1 RO) sequence')

        #Nitrogen init element
        n = element.Element('wait_time', pulsar=qt.pulsar)
        n.append(pulse.cp(T,length=1e-6))
        n.append(Trig)
        elements.append(n)
        #Spin RO element.
        e = element.Element('pi_pulse_msm1', pulsar=qt.pulsar)
        e.append(pulse.cp(T, length = 2e-6))
        e.append(X)
        e.append(Trig)
        elements.append(e)
        for e in elements:
            seq.append(name=e.name, wfname=e.name, trigger_wait=True)

         # upload the waveforms to the AWG
        qt.pulsar.program_awg(seq,*elements)