"""
Script for T1 measurement using Hermite pulses, based on pulsar_msmt.ElectronT1
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

def electronT1hermite(name, T1_initial_state = 'ms=0', T1_readout_state = 'ms=0', start_time = None, end_time = None, pts = None):
    '''Electron T1 measurement using Hermite pulses
    '''

    m = ElectronT1Hermite(name)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    # Measurement settings
    if pts != None:
        m.params['pts'] = pts
    else:
        m.params['pts'] = 6

    # m.params['pts'] = 5
    m.params['wait_time_repeat_element'] = 1000 # in us
    # m.params['wait_times'] = np.linspace(0,200000,m.params['pts'])
    # m.params['wait_times'] = np.concatenate( (np.linspace(0,int(1e5), m.params['pts'] - 3), np.linspace(int(2e5), int(4e5),3))) # in us
    # m.params['wait_times'] = np.concatenate( (np.linspace(0,int(6e5), 3), np.linspace(int(1e6), int(15e6),m.params['pts'] - 3))) # in us
    if start_time != None:
        m.params['wait_times'] = np.linspace(start_time, end_time, m.params['pts'])
    else:
         m.params['wait_times'] = np.concatenate( (np.linspace(0,int(6e5), 4), np.linspace(int(1e6), int(2e6),m.params['pts'] - 4))) # in us

    m.params['repetitions'] = 500
    m.params['T1_initial_state'] = T1_initial_state
    m.params['T1_readout_state'] = T1_readout_state

    # Instrument settings
    m.params['MW_power'] = 20 # Hermite pi pulses are calibrated @ 20 dBm power
    m.params['Ex_SP_amplitude'] = 0
    # m.params['Ex_SP_amplitude']= 1e-9
   # m.params['A_SP_amplitude'] = 0

    # Parameters for analysis
    m.params['sweep_name'] = 'Waiting time (ms)'
    m.params['sweep_pts'] = m.params['wait_times'] * 1e-3

    # Run measurement
    m.autoconfig()
    m.generate_sequence(upload = True)
    m.run()
    m.save()
    m.finish()


def hermite_Xpi(msmt):
    
    MW_pi = pulselib.HermitePulse_Envelope_IQ('Hermite pi-pulse',
                         'MW_Imod',
                         'MW_Qmod',
                         'MW_pulsemod',
                         Sw_channel = 'MW_switch',
                         frequency = msmt.params['Hermite_fast_pi_mod_frq'],
                         amplitude = msmt.params['Hermite_fast_pi_amp'],
                         length = msmt.params['Hermite_fast_pi_duration'],
                         PM_risetime = msmt.params['MW_pulse_mod_risetime'],
                         Sw_risetime = msmt.params['MW_switch_risetime'],
                         pi2_pulse = False)

    return MW_pi 

class ElectronT1Hermite(pulsar_msmt.ElectronT1):

    def generate_sequence(self, upload = True, debug = False):

        ### define basic pulses/times ###
        # pi-pulse, needs different pulses for ms=-1 and ms=+1 transitions in the future.
        X = hermite_Xpi(self)
        # Wait-times
        T = pulse.SquarePulse(channel='MW_Imod', name='delay',
            length = self.params['wait_time_repeat_element']*1e-6, amplitude = 0.)
        T_before_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
            length = 100e-9, amplitude = 0.) #the unit waittime is 10e-6 s
        T_after_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
            length = (1000. - self.params['Hermite_fast_pi_duration'] * 1e9)*1e-9, amplitude = 0.) # waiting time chosen s.t. T_before_p + X + T_after_p = 1 us
        # Trigger pulse
        Trig = pulse.SquarePulse(channel = 'adwin_sync',
        length = 5e-6, amplitude = 2)

        ### create the elements/waveforms from the basic pulses ###
        list_of_elements = []

        #Pi-pulse element/waveform
        e = element.Element('Pi_pulse',  pulsar=qt.pulsar,
                global_time = True)
        e.append(T_before_p)
        e.append(pulse.cp(X))
        e.append(T_after_p)
        list_of_elements.append(e)

        #Wait time element/waveform
        e = element.Element('T1_wait_time',  pulsar=qt.pulsar,
                global_time = True)
        e.append(T)
        list_of_elements.append(e)

        #Trigger element/waveform
        e = element.Element('ADwin_trigger',  pulsar=qt.pulsar,
                global_time = True)
        e.append(Trig)
        list_of_elements.append(e)

        ### create sequences from the elements/waveforms ###
        seq = pulsar.Sequence('ElectronT1_sequence')

        for i in range(len(self.params['wait_times'])):

            if self.params['wait_times'][i]/self.params['wait_time_repeat_element'] !=0:
                if self.params['T1_initial_state'] == 'ms=-1':
                    seq.append(name='Init_Pi_pulse_%d'%i,wfname='Pi_pulse',trigger_wait=True)
                    seq.append(name='ElectronT1_wait_time_%d'%i, wfname='T1_wait_time', trigger_wait=False,repetitions=self.params['wait_times'][i]/self.params['wait_time_repeat_element'])
                    if self.params['T1_readout_state'] == 'ms=-1':
                        seq.append(name='Readout_Pi_pulse_%d'%i,wfname='Pi_pulse',trigger_wait=False)
                    seq.append(name='ElectronT1_ADwin_trigger_%d'%i, wfname='ADwin_trigger', trigger_wait=False)
                #elif self.params['T1_initial_state'] == 'ms=+1':

                else:
                    seq.append(name='ElectronT1_wait_time_%d'%i, wfname='T1_wait_time', trigger_wait=True,repetitions=self.params['wait_times'][i]/self.params['wait_time_repeat_element'])
                    if self.params['T1_readout_state'] == 'ms=-1':
                        seq.append(name='Readout_Pi_pulse_%d'%i,wfname='Pi_pulse',trigger_wait=False)
                    seq.append(name='ElectronT1_ADwin_trigger_%d'%i, wfname='ADwin_trigger', trigger_wait=False)
            else:
                if self.params['T1_initial_state'] == 'ms=-1' and self.params['T1_readout_state'] == 'ms=0':
                    seq.append(name='Init_Pi_pulse_%d'%i,wfname='Pi_pulse',trigger_wait=True)
                    seq.append(name='ElectronT1_ADwin_trigger_%d'%i, wfname='ADwin_trigger', trigger_wait=False)
                elif self.params['T1_initial_state'] == 'ms=0' and self.params['T1_readout_state'] == 'ms=-1':
                    seq.append(name='Readout_Pi_pulse_%d'%i,wfname='Pi_pulse',trigger_wait=True)
                    seq.append(name='ElectronT1_ADwin_trigger_%d'%i, wfname='ADwin_trigger', trigger_wait=False)
                #elif self.params['T1_initial_state'] == 'ms=+1' and self.params['T1_readout_state'] == 'ms=0':
                #elif self.params['T1_readout_state'] == 'ms=+1' and self.params['T1_initial_state'] == 'ms=0':
                else:
                    seq.append(name='ElectronT1_ADwin_trigger_%d'%i, wfname='ADwin_trigger', trigger_wait=True)

         # upload the waveforms to the AWG
        if upload:
            qt.pulsar.program_awg(seq,*list_of_elements, debug = debug)

if __name__ == '__main__':
    # electronT1hermite(SAMPLE_CFG, T1_initial_state = 'ms=0', T1_readout_state = 'ms=0', start_time = 0, end_time = 1.5e6, pts = 4)
    # qt.instruments['optimiz0r'].optimize(dims=['x','y','z','y','x'], cnt=1, int_time=50, cycles=3)
    # electronT1hermite(SAMPLE_CFG, T1_initial_state = 'ms=0', T1_readout_state = 'ms=0', start_time = 0.0e6, end_time = 4.0e5, pts = 5)
    # electronT1hermite(SAMPLE_CFG+'0to0', T1_initial_state = 'ms=0', T1_readout_state = 'ms=0', start_time = 1e3, end_time = 1000e3, pts = 8)
    #electronT1hermite(SAMPLE_CFG+'0top1', T1_initial_state = 'ms=0', T1_readout_state = 'ms=1', start_time = 1e3, end_time = 1000e3, pts = 8)
    electronT1hermite(SAMPLE_CFG+'m1to0', T1_initial_state = 'ms=-1', T1_readout_state = 'ms=0', start_time = 1e3, end_time = 1000e3, pts = 8)
    electronT1hermite(SAMPLE_CFG+'m1top1', T1_initial_state = 'ms=-1', T1_readout_state = 'ms=1', start_time = 1e3, end_time = 1000e3, pts = 8)
