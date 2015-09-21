"""
Script for e-spin manipulations using the pulsar sequencer
"""
import numpy as np
import qt

#reload all parameters and modules
execfile(qt.reload_current_setup)

import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
from measurement.lib.pulsar import pulse, pulselib, element, pulsar
# from measurement.scripts.lt1_scripts.quantum_memory import calibrate_quantum_memory as cqm

SAMPLE= qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def darkesrhermite(name):
    '''dark ESR on the 0 <-> -1 transition
    '''

    m = DarkESRHermite(name)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    m.params['ssmod_detuning'] = m.params['Hermite_fast_pi_mod_frq']#m.params['MW_modulation_frequency']
    m.params['mw_frq']       = m.params['ms-1_cntr_frq'] - m.params['ssmod_detuning'] #MW source frequency, detuned from the target
    m.params['repetitions']  = 1000
    m.params['range']        = 20e6
    m.params['pts'] = 21
    m.params['pulse_length'] =m.params['Hermite_fast_pi_duration'] #2.0e-6
    m.params['ssbmod_amplitude'] = m.params['Hermite_fast_pi_amp']#0.1 # 0.0388#0.017 * 2.
    m.params['mw_power']= 20 #20-6-6-6
    m.params['Ex_SP_amplitude']=0

    m.params['ssbmod_frq_start'] = m.params['ssmod_detuning'] - m.params['range']
    m.params['ssbmod_frq_stop']  = m.params['ssmod_detuning'] + m.params['range']
    list_swp_pts =np.linspace(m.params['ssbmod_frq_start'],m.params['ssbmod_frq_stop'], m.params['pts'])
    m.params['sweep_pts'] = (np.array(list_swp_pts) +  m.params['mw_frq'])*1e-9
    m.autoconfig()
    #m.params['sweep_pts']=m.params['pts']
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()

def darkesrp1(name):
    '''dark ESR on the 0 <-> +1 transition
    '''

    m = pulsar_msmt.DarkESR(name)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['Magnetometry'])

    m.params['ssmod_detuning'] = m.params['MW_modulation_frequency']
    m.params['mw_frq']         = m.params['ms+1_cntr_frq'] - m.params['ssmod_detuning'] # MW source frequency, detuned from the target
    m.params['mw_power'] = 20
    m.params['repetitions'] = 500
    m.params['range']        = 20e6
    m.params['pts'] = 151
    m.params['pulse_length'] = 2.1e-6
    m.params['ssbmod_amplitude'] = 0.025

    m.params['ssbmod_frq_start'] = m.params['ssmod_detuning'] #- m.params['range']
    m.params['ssbmod_frq_stop']  = m.params['ssmod_detuning'] + 2*m.params['range']

    m.params['sweep_pts'] =np.linspace(m.params['ssbmod_frq_start'],m.params['ssbmod_frq_stop'], m.params['pts'])
    m.autoconfig()
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()

def hermite_Xpi(msmt):
    
    MW_pi = pulselib.HermitePulse_Envelope_IQ('Hermite pi-pulse',
                         'MW_Imod',
                         'MW_Qmod',
                         'MW_pulsemod',
                         # frequency = msmt.params['fast_pi_mod_frq'],
                         amplitude = msmt.params['ssbmod_amplitude'],
                         length = msmt.params['pulse_length'],
                         PM_risetime = msmt.params['MW_pulse_mod_risetime'],
                         pi2_pulse = False)

    return MW_pi 


class DarkESRHermite(pulsar_msmt.DarkESR):
    def generate_sequence(self, upload=True):

        # define the necessary pulses
        X = hermite_Xpi(self)

        T = pulse.SquarePulse(channel='MW_Imod', name='delay')
        T.amplitude = 0.
        T.length = 2e-6

        # make the elements - one for each ssb frequency
        elements = []

        for i, f in enumerate(1e9*self.params['sweep_pts']-self.params['mw_frq']):

            e = element.Element('DarkESR_frq-%d' % i, pulsar=qt.pulsar)
            e.add(T, name='wait')
            e.add(X(frequency=f), refpulse='wait')
            elements.append(e)

        # create a sequence from the pulses
        seq = pulsar.Sequence('DarkESR sequence')
        for e in elements:
            seq.append(name=e.name, wfname=e.name, trigger_wait=True)

         # upload the waveforms to the AWG
        if upload:
            if upload=='old_method':
                qt.pulsar.upload(*elements)
                qt.pulsar.program_sequence(seq)
            else:
                qt.pulsar.program_awg(seq,*elements)

if __name__ == '__main__':
    darkesrhermite(SAMPLE_CFG)
    #raw_input ('Do the fitting...')
    #darkesrp1(SAMPLE_CFG)
