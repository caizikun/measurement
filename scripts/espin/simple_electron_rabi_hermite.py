"""
Performs Rabi oscillation using Hermite pulses 
(largely copied from simple_electron_rabi.py)
-- KvB (2015)
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

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

class ElectronRabiHermite(pulsar_msmt.PulsarMeasurement):
    mprefix = 'ElectronRabiHermite'

    def autoconfig(self):
        self.params['sequence_wait_time'] = \
            int(np.ceil(np.max(self.params['MW_pulse_durations'])*1e6)+10)

        pulsar_msmt.PulsarMeasurement.autoconfig(self)

    def generate_sequence(self, upload=True):
        #print 'test'
        # define the necessary pulses

        # X = pulselib.MW_IQmod_pulse('Weak pi-pulse',
        #     I_channel='MW_Imod',
        #     Q_channel='MW_Qmod',
        #     PM_channel='MW_pulsemod',
        #     frequency = self.params['MW_pulse_frequency'],
        #     PM_risetime = self.params['MW_pulse_mod_risetime'])
        print 'mod freq =', self.params['Hermite_fast_pi_mod_frq']
        X = pulselib.HermitePulse_Envelope_IQ('Hermite pi-pulse',
                         'MW_Imod',
                         'MW_Qmod',
                         'MW_pulsemod',
                         Sw_channel = 'MW_switch',
                         frequency = self.params['Hermite_fast_pi_mod_frq'],
                         PM_risetime = self.params['MW_pulse_mod_risetime'],
                         Sw_risetime = self.params['MW_switch_risetime'],
                         phase = self.params['X_phase'],
                         pi2_pulse = False)

        T = pulse.SquarePulse(channel='MW_Imod', name='delay',
            length = 200e-9, amplitude = 0.)

        # make the elements - one for each ssb frequency
        elements = []
        for i in range(self.params['pts']):

            e = element.Element('ElectronRabi_pt-%d' % i, pulsar=qt.pulsar)

            e.append(T)
            # Skip pulse if its duration = 0 (yields divide by zero in Hermite envelope)
            if self.params['MW_pulse_durations'][i] > 0:
                e.append(pulse.cp(X,
                    length = self.params['MW_pulse_durations'][i],
                    amplitude = self.params['MW_pulse_amplitudes'][i]))

            elements.append(e)


        # create a sequence from the pulses
        seq = pulsar.Sequence('ElectronRabi sequence')
        for e in elements:
            seq.append(name=e.name, wfname=e.name, trigger_wait=True)

        # upload the waveforms to the AWG
        if upload:
            if upload=='old_method':
                print 'using old method of uploading'
                qt.pulsar.upload(*elements)
                qt.pulsar.program_sequence(seq)
            else:
                qt.pulsar.program_awg(seq,*elements)

def erabi_hermite(name):
    m = ElectronRabiHermite(name)

    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])
    #m.params.from_dict(qt.exp_params['protocols']['Hans_sil1']['Magnetometry'])
    
    m.params['pts'] = 18
    pts = m.params['pts']
    m.params['repetitions'] = 300
    m.params['reps_per_ROsequence'] = m.params['repetitions']
    m.params['Ex_SP_amplitude']=0

    sweep_param = 'length'

    # m.params['mw_power']=20 
    #m.params['mw_frq'] = m.params['ms-1_cntr_frq']-m.params['MW_modulation_frequency']  
    #print m.params['ms+1_cntr_frq']    #for ms=-1   'ms-1_cntr_frq'
    #m.params['mw_frq'] = 3.45e9      #for ms=+1

    if sweep_param == 'length':
        m.params['MW_pulse_durations'] =  np.linspace(0, 4*m.params['fast_pi_duration'], pts) #* 1e-9
        m.params['MW_pulse_amplitudes'] = np.ones(pts) *m.params['fast_pi_amp'] # * 0.05 #*0.49
        m.params['sweep_name'] = 'Pulse durations (ns)'
        m.params['sweep_pts'] = m.params['MW_pulse_durations']*1e9
        
        print m.params['fast_pi_amp']
        print m.params['MW_pulse_durations']
    elif sweep_param == 'amplitude':    
        m.params['MW_pulse_durations'] =  np.ones(pts)*490e-9 
        m.params['MW_pulse_amplitudes'] = np.linspace(0.0,0.9,pts) #0.02
        m.params['sweep_name'] = 'MW_pulse_amplitudes (V)'
        m.params['sweep_pts'] = m.params['MW_pulse_amplitudes']

    # for autoanalysis
    #m.params['sweep_name'] = 'Pulse duration (ns)' #'Pulse amps (V)'
    #m.params['sweep_pts'] = m.params['MW_pulse_durations']*1e9

    print m.params['sweep_pts']

    m.autoconfig() #Redundant because executed in m.run()? Tim
    m.generate_sequence(upload=True)
    if True:
        m.run()
        qt.msleep(2)
        m.save()
        qt.msleep(2)
        m.finish()

if __name__ == '__main__':
    erabi_hermite(SAMPLE+'_'+'msp1')
