import numpy as np
import qt

#reload all parameters and modules
execfile(qt.reload_current_setup)

import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt
from measurement.lib.measurement2.adwin_ssro import pulsar_pq
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

class ElectronRabi_Square(pulsar_msmt.PulsarMeasurement):
    mprefix = 'ElectronRabi'

    def autoconfig(self):
        self.params['sequence_wait_time'] = \
            int(np.ceil(np.max(self.params['MW_pulse_durations'])*1e6)+10)


        pulsar_msmt.PulsarMeasurement.autoconfig(self)

    def generate_sequence(self, upload=True):
        #print 'test'
        # define the necessary pulses

        X = pulselib.MW_pulse('Weak pi-pulse',
            MW_channel='MW_1',
            PM_channel='MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'])

        T = pulse.SquarePulse(channel='MW_2', name='delay',
            length = 200e-9, amplitude = 0.)

        # make the elements - one for each ssb frequency
        elements = []
        for i in range(self.params['pts']):

            e = element.Element('ElectronRabi_pt-%d' % i, pulsar=qt.pulsar)

            e.append(T)
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
            qt.pulsar.program_awg(seq,*elements)
            #qt.pulsar.upload(*elements)

        # program the AWG
        #qt.pulsar.program_sequence(seq)

        # some debugging:
        # elements[-1].print_overview()




class ElectronRabi_Imod(pulsar_msmt.PulsarMeasurement):
    mprefix = 'ElectronRabi_Imod'

    def autoconfig(self):
        self.params['sequence_wait_time'] = \
            int(np.ceil(np.max(self.params['MW_pulse_durations'])*1e6)+10)


        pulsar_msmt.PulsarMeasurement.autoconfig(self)

    def generate_sequence(self, upload=True):
        #print 'test'
        # define the necessary pulses

        X = pulselib.MW_IQmod_pulse('Weak pi-pulse',
            I_channel='MW_1', 
            Q_channel='dummy',
            PM_channel='MW_pulsemod',
            frequency = self.params['MW_pulse_frequency'],
            PM_risetime = self.params['MW_pulse_mod_risetime'])
        X.channels.remove('dummy')

        T = pulse.SquarePulse(channel='MW_1', name='delay',
            length = 200e-9, amplitude = 0.)

        # make the elements - one for each ssb frequency
        elements = []
        for i in range(self.params['pts']):

            e = element.Element('ElectronRabi_pt-%d' % i, pulsar=qt.pulsar)

            e.append(T)
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
            qt.pulsar.program_awg(seq,*elements)



class ElectronPulse_Random(pulsar_pq.PQPulsarMeasurement):
    mprefix = 'ElectronRabi_Random'

    def autoconfig(self):
        self.params['sequence_wait_time'] = \
            int(self.params['SSRO_duration']+10)
        
        self.params['E_RO_voltage_AWG'] = \
                    self.E_aom.power_to_voltage(
                            self.params['Ex_RO_amplitude'], controller='sec')

        pulsar_pq.PQPulsarMeasurement.autoconfig(self)

    def generate_sequence(self, upload=True):
        #print 'test'
        # define the necessary pulses

        X1 = pulselib.MW_CORPSE_pulse('CORPSE pi-pulse',
        MW_channel = 'MW_1', 
        PM_channel = 'MW_pulsemod',
        #second_MW_channel = 'MW_Qmod',
        PM_risetime = self.params['MW_pulse_mod_risetime'],
        amplitude = self.params['CORPSE_pi_amp'],
        rabi_frequency = self.params['CORPSE_pi_frq'],
        eff_rotation_angle = 180)

        X2 = pulselib.MW_CORPSE_pulse('CORPSE 2pi-pulse',
        MW_channel = 'MW_2', 
        PM_channel = 'MW_pulsemod',
        #second_MW_channel = 'MW_Qmod',
        PM_risetime = self.params['MW_pulse_mod_risetime'],
        amplitude = self.params['CORPSE_2pi_amp'],
        rabi_frequency = self.params['CORPSE_2pi_frq'],
        eff_rotation_angle = 360)

        RND_halt = pulse.SquarePulse(channel = 'RND_halt', amplitude = 1.0, 
                                    length = 400e-9)
        sync = pulse.SquarePulse(channel = 'sync', length = 50e-9, amplitude = 1.0)
        T = pulse.SquarePulse(channel='MW_1', name='delay',
            length = 200e-9, amplitude = 0.)
        RO_pulse = pulse.SquarePulse(channel = 'AOM_Matisse', 
                                     amplitude = self.params['E_RO_voltage_AWG'], 
                                     length = self.params['SSRO_duration']*1e-6)

        # make the elements - one for each ssb frequency
        elements = []
        for i in range(self.params['pts']):

            e = element.Element('ElectronRandom_pt-%d' % i, pulsar=qt.pulsar)

            e.append(T)
            e.append(sync)
            e.append(T)
            e.append(RND_halt)
            ref=e.append(T)
            e.add(X1, refpulse=ref)
            e.add(X2, refpulse=ref)
            e.append(pulse.cp(T, length = 1e-6))
            e.append(RO_pulse)
            e.append(T)

            elements.append(e)


        # create a sequence from the pulses
        seq = pulsar.Sequence('ElectronRandom sequence')
        for e in elements:
            seq.append(name=e.name, wfname=e.name, trigger_wait=True)

        # upload the waveforms to the AWG
        if upload:
            qt.pulsar.program_awg(seq,*elements)
            #qt.pulsar.upload(*elements)

        # program the AWG
        #qt.pulsar.program_sequence(seq)

        # some debugging:
        # elements[-1].print_overview()


class ElectronPulse_I_CORPSE_Random(pulsar_pq.PQPulsarMeasurement):
    mprefix = 'ElectronRabi_IQ+CORPSE_Random'

    def autoconfig(self):
        self.params['sequence_wait_time'] = \
            int(self.params['SSRO_duration']+10)
        
        self.params['E_RO_voltage_AWG'] = \
                    self.E_aom.power_to_voltage(
                            self.params['Ex_RO_amplitude'], controller='sec')

        pulsar_pq.PQPulsarMeasurement.autoconfig(self)

    def generate_sequence(self, upload=True):
        #print 'test'
        # define the necessary pulses

        X1 = pulselib.IQ_CORPSE_pulse('CORPSE pi-pulse',
        I_channel = 'MW_1', 
        Q_channel='dummy',
        PM_channel = 'MW_pulsemod',
        #second_MW_channel = 'MW_Qmod',
        PM_risetime = self.params['MW_pulse_mod_risetime'],
        amplitude = self.params['CORPSE_pi_amp'],

        rabi_frequency = self.params['CORPSE_pi_frq'],
        eff_rotation_angle = 180)
        X1.channels.remove('dummy')
        X2 = pulselib.IQ_CORPSE_pulse('CORPSE 2pi-pulse',
        I_channel = 'MW_2', 
        PM_channel = 'MW_pulsemod',
        #second_MW_channel = 'MW_Qmod',
        PM_risetime = self.params['MW_pulse_mod_risetime'],
        amplitude = self.params['CORPSE_2pi_amp'],
        rabi_frequency = self.params['CORPSE_2pi_frq'],
        eff_rotation_angle = 360)
        X2.channels.remove('dummy')

        RND_halt = pulse.SquarePulse(channel = 'RND_halt', amplitude = 1.0, 
                                    length = 400e-9)
        sync = pulse.SquarePulse(channel = 'sync', length = 50e-9, amplitude = 1.0)
        T = pulse.SquarePulse(channel='MW_1', name='delay',
            length = 200e-9, amplitude = 0.)
        RO_pulse = pulse.SquarePulse(channel = 'AOM_Matisse', 
                                     amplitude = self.params['E_RO_voltage_AWG'], 
                                     length = self.params['SSRO_duration']*1e-6)

        # make the elements - one for each ssb frequency
        elements = []
        for i in range(self.params['pts']):

            e = element.Element('ElectronRandom_pt-%d' % i, pulsar=qt.pulsar)

            e.append(T)
            e.append(sync)
            e.append(T)
            e.append(RND_halt)
            ref=e.append(T)
            e.add(X1, refpulse=ref)
            e.add(X2, refpulse=ref)
            e.append(pulse.cp(T, length = 1e-6))
            e.append(RO_pulse)
            e.append(T)

            elements.append(e)


        # create a sequence from the pulses
        seq = pulsar.Sequence('ElectronRandom sequence')
        for e in elements:
            seq.append(name=e.name, wfname=e.name, trigger_wait=True)

        # upload the waveforms to the AWG
        if upload:
            qt.pulsar.program_awg(seq,*elements)
            #qt.pulsar.upload(*elements)

        # program the AWG
        #qt.pulsar.program_sequence(seq)

        # some debugging:
        # elements[-1].print_overview()


# bug !!
class DarkESR_CORPSE_Imod(pulsar_msmt.PulsarMeasurement):
    mprefix = 'PulsarDarkESR_CORPSE_Imod'

    def autoconfig(self):
        self.params['sequence_wait_time'] = \
            int(np.ceil(self.params['pulse_length']*1e6)+15)

        pulsar_msmt.PulsarMeasurement.autoconfig(self)

        self.params['sweep_name'] = 'MW frq (GHz)'
        self.params['sweep_pts'] = (np.linspace(self.params['ssbmod_frq_start'],
            self.params['ssbmod_frq_stop'], self.params['pts']) + \
                self.params['mw_frq'])*1e-9

    def generate_sequence(self, upload=True):

        # define the necessary pulses
        X = pulselib.IQ_CORPSE_pulse('CORPSE Imod pi-pulse',
            I_channel='MW_1',
            Q_channel='dummy',
            PM_channel='MW_pulsemod',
            amplitude = self.params['ssbmod_amplitude'],
            length = self.params['pulse_length'],
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            frequency = self.params['ssmod_detuning'],
            rabi_frequency = self.params['CORPSE_rabi_frequency'],
            pulse_delay = self.params['CORPSE_pulse_delay'],
            eff_rotation_angle = self.params['CORPSE_eff_rotation_angle'])
        
        X.channels.remove('dummy')


        T = pulse.SquarePulse(channel='MW_1', name='delay')
        T.amplitude = 0.
        T.length = 2e-6

        # make the elements - one for each ssb frequency
        elements = []
        for i, f in enumerate(np.linspace(self.params['ssbmod_frq_start'],
            self.params['ssbmod_frq_stop'], self.params['pts'])):

            e = element.Element('DarkESR_CORPSE_Imod_frq-%d' % i, pulsar=qt.pulsar)
            e.add(T, name='wait')
            e.add(X(frequency=f), refpulse='wait')
            elements.append(e)

        # create a sequence from the pulses
        seq = pulsar.Sequence('DarkESR sequence')
        for e in elements:
            seq.append(name=e.name, wfname=e.name, trigger_wait=True)

        # upload the waveforms to the AWG
        if upload:
            #qt.pulsar.upload(*elements)
            qt.pulsar.program_awg(seq,*elements)

def erabi(name):
    m = ElectronRabi_Square(name)

    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])

   # m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['Magnetometry'])
    
    m.params['pts'] = 21
    pts = m.params['pts']
    m.params['repetitions'] = 1000

    #m.params['wait_after_pulse_duration']=0
    #m.params['wait_after_RO_pulse_duration']=0
    m.params['Ex_SP_amplitude']=0


    m.params['mw_frq'] = m.params['ms-1_cntr_frq'] 
    #print m.params['ms+1_cntr_frq']    #for ms=-1   'ms-1_cntr_frq'
    #m.params['mw_frq'] = 3.45e9      #for ms=+1

    #m.params['MW_pulse_frequency'] = 43e6

    #m.params['MW_pulse_durations'] =  np.ones(pts)*100e-9 #np.linspace(0, 10, pts) * 1e-6
    m.params['MW_pulse_durations'] =  np.linspace(0, 200, pts) * 1e-9

    m.params['MW_pulse_amplitudes'] = np.ones(pts)*0.27
    #m.params['MW_pulse_amplitudes'] = np.linspace(0,0.8,pts)#0.55*np.ones(pts)

    # for autoanalysis
    #m.params['sweep_name'] = 'Pulse duration (ns)' #'Pulse amps (V)'
    #m.params['sweep_pts'] = m.params['MW_pulse_durations']*1e9

    m.params['sweep_name'] = 'Pulse durations (ns)'
    #m.params['sweep_name'] = 'MW_pulse_amplitudes (V)'

    #m.params['sweep_pts'] = m.params['MW_pulse_amplitudes']
    m.params['sweep_pts'] = m.params['MW_pulse_durations']*1e9
    print m.params['sweep_pts']


    m.autoconfig() #Redundant because executed in m.run()? Tim
    m.generate_sequence(upload=True)
    
    m.run()
    m.save()
    m.finish()


def erabi_I(name):
    m=ElectronRabi_Imod(name)

    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])

   # m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['Magnetometry'])
    
    m.params['pts'] = 21
    pts = m.params['pts']
    m.params['repetitions'] = 1000

    #m.params['wait_after_pulse_duration']=0
    #m.params['wait_after_RO_pulse_duration']=0
    m.params['Ex_SP_amplitude']=0

    m.params['MW_pulse_frequency'] = 40e6
    m.params['mw_frq'] = m.params['ms-1_cntr_frq']- m.params['MW_pulse_frequency'] 

    m.params['MW_pulse_durations'] =  np.ones(pts)*200e-9 #np.linspace(0, 10, pts) * 1e-6
    #m.params['MW_pulse_durations'] =  np.linspace(0, 200, pts) * 1e-9

    #m.params['MW_pulse_amplitudes'] = np.ones(pts)*0.9
    m.params['MW_pulse_amplitudes'] = np.linspace(0,0.8,pts)#0.55*np.ones(pts)

    # for autoanalysis
    #m.params['sweep_name'] = 'Pulse duration (ns)' #'Pulse amps (V)'
    #m.params['sweep_pts'] = m.params['MW_pulse_durations']*1e9

    #m.params['sweep_name'] = 'Pulse durations (ns)'
    m.params['sweep_name'] = 'MW_pulse_amplitudes (V)'

    m.params['sweep_pts'] = m.params['MW_pulse_amplitudes']
    #m.params['sweep_pts'] = m.params['MW_pulse_durations']*1e9
    print m.params['sweep_pts']


    m.autoconfig() #Redundant because executed in m.run()? Tim
    m.generate_sequence(upload=True)
    
    m.run()
    m.save()
    m.finish()


def erandom(name):
    m = ElectronPulse_Random(name)

    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+PQ'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])

    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])
   # m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['Magnetometry'])

    m.params['pts'] = 1
    pts = m.params['pts']
    m.params['sweep_pts']=np.zeros(pts)
    m.params['sweep_name']='none'
    m.params['repetitions'] = 15000

    m.params['Ex_SP_amplitude']=0

    m.params['mw_frq'] = m.params['ms-1_cntr_frq'] 

    m.params['CORPSE_pi_frq'] = 4.8e6
    m.params['CORPSE_pi_amp'] = 0.511416

    m.params['CORPSE_2pi_frq']=6e6
    m.params['CORPSE_2pi_amp']=0.818344
    
    m.params['MIN_SYNC_BIN'] =       0 
    m.params['MAX_SYNC_BIN'] =       40000
    
    debug=True
    m.autoconfig() 
    m.generate_sequence(upload=True)
    m.setup(debug=debug)
    m.run(autoconfig=False, setup=False,debug=debug)
    m.save()
    m.finish()


def darkesr_CORPSE_Imod(name):
    '''dark ESR on the 0 <-> -1 transition
    '''

    m = pulsar_msmt.DarkESR_CORPSE_Imod(name)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['Hans_sil4']['Magnetometry'])

    m.params['ssmod_detuning'] = 80e6
    m.params['mw_frq']       = m.params['ms-1_cntr_frq'] - m.params['ssmod_detuning'] #MW source frequency, detuned from the target
    m.params['repetitions']  = 2000
    m.params['range']        = 20e6
    m.params['pts'] = 131
    m.params['pulse_length'] = 0.2-6
    m.params['ssbmod_amplitude'] = 0.384
    
    m.params['Ex_SP_amplitude']=0



    m.params['ssbmod_frq_start'] = m.params['ssmod_detuning'] - m.params['range']
    m.params['ssbmod_frq_stop']  = m.params['ssmod_detuning'] + m.params['range']

    m.autoconfig()
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()




if __name__ == '__main__':
    erabi(SAMPLE+'_'+'rabi')
    #darkesr_CORPSE_Imod(SAMPLE+'_'+'darkesr_CORPSE_Imod') # this does not work
    #erandom(SAMPLE+'_'+'rabi')
