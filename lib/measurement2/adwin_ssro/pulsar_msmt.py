import msvcrt
import numpy as np
import qt
import hdf5_data as h5
import logging

import measurement.lib.measurement2.measurement as m2
from measurement.lib.measurement2.adwin_ssro import ssro
reload(ssro)
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

class PulsarMeasurement(ssro.IntegratedSSRO):
    mprefix = 'PulsarMeasurement'
    awg = None
    mwsrc = None

    def __init__(self, name):
        ssro.IntegratedSSRO.__init__(self, name)

        self.params['measurement_type'] = self.mprefix

    def setup(self, wait_for_awg=True, mw=True, **kw):
        ssro.IntegratedSSRO.setup(self)

        if mw:
            self.mwsrc.set_iq('on')
            self.mwsrc.set_pulm('on')
            self.mwsrc.set_frequency(self.params['mw_frq'])
            self.mwsrc.set_power(self.params['mw_power'])
            self.mwsrc.set_status('on')

        print 'AWG state before start'
        print self.awg.get_state()
        self.awg.start()
        if not wait_for_awg:
            print 'NOT WAIING FOR AWG!!!!'
        if wait_for_awg:
            i=0
            awg_ready = False
            while not awg_ready and i<100:
                #print '( not awg_ready and i < 100 ) == True'
                #print 'awg state: '+str(self.awg.get_state())

                if (msvcrt.kbhit() and (msvcrt.getch() == 'x')):
                    raise Exception('User abort while waiting for AWG')

                try:
                    if self.awg.get_state() == 'Waiting for trigger':
                        qt.msleep(1)
                        awg_ready = True
                        print 'AWG Ready!'
                    else:
                        print 'AWG not in wait for trigger state but in state:', self.awg.get_state()
                except:
                    print 'waiting for awg: usually means awg is still busy and doesnt respond'
                    print 'waiting', i, '/ 100'
                    self.awg.clear_visa()
                    i=i+1

                qt.msleep(0.5)

            if not awg_ready:
                raise Exception('AWG not ready')

    def generate_sequence(self):
        pass

    def stop_sequence(self):
        self.awg.stop()

    def save(self,**kw):
        ssro.IntegratedSSRO.save(self, **kw)

        grp=self.h5basegroup.create_group('pulsar_settings')
        pulsar = kw.pop('pulsar', qt.pulsar)

        for k in pulsar.channels:
            grpc=grp.create_group(k)
            for ck in pulsar.channels[k]:
                grpc.attrs[ck] = pulsar.channels[k][ck]

        grpa=grp.create_group('AWG_sequence_cfg')
        for k in pulsar.AWG_sequence_cfg:
            grpa.attrs[k] = pulsar.AWG_sequence_cfg[k]


        self.h5data.flush()

    def finish(self,**kw):
        ssro.IntegratedSSRO.finish(self,**kw)
        
        self.awg.stop()
        self.awg.set_runmode('CONT')
        self.mwsrc.set_status('off')
        self.mwsrc.set_iq('off')
        self.mwsrc.set_pulm('off')

# class PulsarMeasurement

class SSRO_calibration_msp1(PulsarMeasurement):
    mprefix = 'SSRO_calib_msp1'

    def autoconfig(self):
        PulsarMeasurement.autoconfig(self)

    def generate_sequence(self, upload=True):

        # define the necessary pulses
        X = pulselib.MW_IQmod_pulse('pi-pulse-on-p1',
            I_channel='MW_Imod', Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod',
            amplitude = self.params['MW_pi_msp1_amp'],
            length = self.params['MW_pi_msp1_dur'],
            frequency = self.params['ms+1_mod_frq'],
            PM_risetime = self.params['MW_pulse_mod_risetime'])
        Trig = pulse.SquarePulse(channel = 'adwin_sync', length = 5e-6, amplitude = 2)

        T = pulse.SquarePulse(channel='MW_Imod', name='delay')
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
        #Dark esr element
        e = element.Element('pi_pulse_msp1', pulsar=qt.pulsar)
        e.append(T, length = 1e-6)
        e.append(X)
        e.append(Trig)
        elements.append(e)
        for e in elements:
            seq.append(name=e.name, wfname=e.name, trigger_wait=True)

         # upload the waveforms to the AWG
        qt.pulsar.program_awg(seq,*elements)


class Multiple_SP_SSRO(PulsarMeasurement):
    mprefix = 'Multiple_SP_SSRO'

    def autoconfig(self):
        self.params['sequence_wait_time'] = 15
        self.params['A_SP_AWG_voltage']=self.A_aom.power_to_voltage(self.params['A_SP_amplitude'],controller='sec')    
        self.params['Ex_RO_AWG_voltage']=self.A_aom.power_to_voltage(self.params['Ex_RO_amplitude'],controller='sec')    
        PulsarMeasurement.autoconfig(self)

        self.params['sweep_name'] = 'Number of SP-SSRO repetitions'
        
        # why make this array here, assuming you want equally spaced points?
        # Just define sweep_pts in the script, and measure those points.

        #self.params['sweep_pts'] = (np.linspace(self.params['ssbmod_frq_start'],
        #    self.params['ssbmod_frq_stop'], self.params['pts']) + \
        #        self.params['mw_frq'])*1e-9

    def generate_sequence(self, upload=True):

        # define the necessary pulses

        SP = pulse.SquarePulse(channel='AOM_Newfocus', name='SP')
        
        SP.amplitude = self.params['A_SP_AWG_voltage']
        SP.length = self.params['SP_duration']*1e-6

        RO = pulse.SquarePulse(channel='AOM_Matisse', name='RO')
        
        RO.amplitude = self.params['Ex_RO_AWG_voltage']
        RO.length = self.params['SSRO_duration']*1e-6

        FM = pulse.SquarePulse(channel='FM', name='modulation')
        FM.amplitude=0
        FM.length=20e-6
        
        T = pulse.SquarePulse(channel='MW_Imod', name='delay')
        T.amplitude = 0.
        T.length = 2e-6
        
        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = self.params['AWG_to_adwin_ttl_trigger_duration'],
            amplitude = 2)

        # make the elements - one for each ssb frequency
        elements = []
        seq = pulsar.Sequence('Multpiple_SP_SSRO_sequence')

        for i, f in enumerate(self.params['sweep_pts']):

            e = element.Element('Mult_SP_SSRO-%d' % i, pulsar=qt.pulsar)
            e.add(T, name='wait')
            e.add(SP,name='SP',refpulse='wait')
            e.add(T, name='wait2',refpulse='SP')
            e.add(RO,name='RO',refpulse='wait2')

            elements.append(e)
            seq.append(name=e.name, wfname=e.name, trigger_wait=True,repetitions=f)
            e = element.Element('Trigger-%d' % i, pulsar=qt.pulsar)
            e.add(T, name='wait')
            e.add(SP,name='SP',refpulse='wait')
            e.add(adwin_sync, name='sync',refpulse='SP')

            elements.append(e)
            seq.append(name=e.name, wfname=e.name, trigger_wait=False)
        # create a sequence from the pulses

         # upload the waveforms to the AWG
        if upload:
            if upload=='old_method':
                qt.pulsar.upload(*elements)
                qt.pulsar.program_sequence(seq)
            else:
                qt.pulsar.program_awg(seq,*elements)

class DarkESR(PulsarMeasurement):
    mprefix = 'PulsarDarkESR'

    def autoconfig(self):
        self.params['sequence_wait_time'] = \
            int(np.ceil(self.params['pulse_length']*1e6)+15)

        PulsarMeasurement.autoconfig(self)

        self.params['sweep_name'] = 'MW frq (GHz)'
        
        # why make this array here, assuming you want equally spaced points?
        # Just define sweep_pts in the script, and measure those points.
        #self.params['sweep_pts'] = (np.linspace(self.params['ssbmod_frq_start'],
        #    self.params['ssbmod_frq_stop'], self.params['pts']) + \
        #        self.params['mw_frq'])*1e-9

    def generate_sequence(self, upload=True):

        # define the necessary pulses
        X = pulselib.MW_IQmod_pulse('Weak pi-pulse',
            I_channel='MW_Imod', Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod',
            amplitude = self.params['ssbmod_amplitude'],
            length = self.params['pulse_length'],
            PM_risetime = self.params['MW_pulse_mod_risetime'])

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

class DarkESR_FM(PulsarMeasurement):
    mprefix = 'PulsarDarkESR_FM'

    def autoconfig(self):
        self.params['sequence_wait_time'] = \
            int(np.ceil((self.params['pulse_length']+self.params['FM_delay'])*1e6)+15)

        PulsarMeasurement.autoconfig(self)

        self.params['sweep_name'] = 'MW frq (GHz)'
        
        # why make this array here, assuming you want equally spaced points?
        # Just define sweep_pts in the script, and measure those points.

        #self.params['sweep_pts'] = (np.linspace(self.params['ssbmod_frq_start'],
        #    self.params['ssbmod_frq_stop'], self.params['pts']) + \
        #        self.params['mw_frq'])*1e-9

    def generate_sequence(self, upload=True):

        # define the necessary pulses
        X = pulselib.MW_IQmod_pulse('Weak pi-pulse',
            I_channel='MW_Imod', Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod',
            amplitude = self.params['ssbmod_amplitude'],
            length = self.params['pulse_length'],
            PM_risetime = self.params['MW_pulse_mod_risetime'])

        T = pulse.SquarePulse(channel='MW_Imod', name='delay')
        
        T.amplitude = 0.
        T.length = 2e-6

        FM = pulse.SquarePulse(channel='FM', name='modulation')
        FM.amplitude=0
        FM.length=20e-6
        
        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = self.params['AWG_to_adwin_ttl_trigger_duration'],
            amplitude = 2)

        # make the elements - one for each ssb frequency
        elements = []

        for i, f in enumerate(1e9*self.params['sweep_pts']-self.params['mw_frq']):

            e = element.Element('DarkESR_frq-%d' % i, pulsar=qt.pulsar)
            e.add(T, name='wait')
            e.add(X(frequency=self.params['ssmod_detuning']),name='MW_pulse' ,refpulse='wait')
            e.add(FM(amplitude=self.params['FM_amplitude'][i],length=self.params['FM_delay']+self.params['pulse_length']+1e-6), name='FM',start=-1*self.params['FM_delay'],refpulse='MW_pulse',refpoint='start')
            last=e.add(T, name='wait2',start=-100e-9,refpulse='FM',refpoint='end')
            last=e.add(adwin_sync,name='adwin_sync',refpulse=last)

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


class ElectronRabi(PulsarMeasurement):
    mprefix = 'ElectronRabi'

    def autoconfig(self):
        self.params['sequence_wait_time'] = \
            int(np.ceil(np.max(self.params['MW_pulse_durations'])*1e6)+10)


        PulsarMeasurement.autoconfig(self)

    def generate_sequence(self, upload=True):
        #print 'test'
        # define the necessary pulses

        X = pulselib.MW_IQmod_pulse('Weak pi-pulse',
            I_channel='MW_Imod',
            Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod',
            frequency = self.params['MW_pulse_frequency'],
            PM_risetime = self.params['MW_pulse_mod_risetime'])

        T = pulse.SquarePulse(channel='MW_Imod', name='delay',
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
            if upload=='old_method':
                print 'using old method of uploading'
                qt.pulsar.upload(*elements)
                qt.pulsar.program_sequence(seq)
            else:
                qt.pulsar.program_awg(seq,*elements)
        

class ElectronRabi_Square(PulsarMeasurement):
    mprefix = 'ElectronRabi_square'

    def autoconfig(self):
        self.params['sequence_wait_time'] = \
            int(np.ceil(np.max(self.params['MW_pulse_durations'])*1e6)+10)


        PulsarMeasurement.autoconfig(self)

    def generate_sequence(self, upload=True):
        #print 'test'
        # define the necessary pulses

        X = pulselib.MW_pulse('Weak pi-pulse',
            MW_channel='MW_Imod',
            PM_channel='MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'])

        T = pulse.SquarePulse(channel='MW_Qmod', name='delay',
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
            if upload=='old_method':
                qt.pulsar.upload(*elements)
                qt.pulsar.program_sequence(seq)
            else:
                qt.pulsar.program_awg(seq,*elements)




class ElectronRamseyCORPSE(PulsarMeasurement):
    mprefix = 'ElectronRamsey'

    def autoconfig(self):
        self.params['sequence_wait_time'] = \
            int(np.ceil(np.max(self.params['evolution_times'])*1e6)+10)


        PulsarMeasurement.autoconfig(self)

    def generate_sequence(self, upload=True):

        # define the necessary pulses
        X = pulselib.IQ_CORPSE_pi2_pulse('CORPSE pi2-pulse',
            I_channel='MW_Imod',
            Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            frequency = self.params['CORPSE_pi2_mod_frq'],
            amplitude = self.params['CORPSE_pi2_amp'],
            length_24p3 = self.params['CORPSE_pi2_24p3_duration'],
            length_m318p6 = self.params['CORPSE_pi2_m318p6_duration'],
            length_384p3 = self.params['CORPSE_pi2_384p3_duration'])

        T = pulse.SquarePulse(channel='MW_Imod', name='delay',
            length = 200e-9, amplitude = 0.)

        # make the elements - one for each ssb frequency
        elements = []
        for i in range(self.params['pts']):

            e = element.Element('ElectronRamsey_pt-%d' % i, pulsar=qt.pulsar,
                global_time = True)
            e.append(T)

            e.append(pulse.cp(X,
                amplitude = self.params['CORPSE_pi2_amps'][i],
                phase = self.params['CORPSE_pi2_phases1'][i]))

            e.append(pulse.cp(T,
                length = self.params['evolution_times'][i]))

            e.append(pulse.cp(X,
                amplitude = self.params['CORPSE_pi2_amps'][i],
                phase = self.params['CORPSE_pi2_phases2'][i]))

            elements.append(e)
        return_e=e
        # create a sequence from the pulses
        seq = pulsar.Sequence('ElectronRamsey sequence')
        for e in elements:
            seq.append(name=e.name, wfname=e.name, trigger_wait=True)

        # upload the waveforms to the AWG
        if upload:
            if upload=='old_method':
                qt.pulsar.upload(*elements)
                qt.pulsar.program_sequence(seq)
            else:
                qt.pulsar.program_awg(seq,*elements)


class ElectronRamsey(PulsarMeasurement):
    mprefix = 'ElectronRamsey'

    def autoconfig(self):
        self.params['sequence_wait_time'] = \
            int(np.ceil(np.max(self.params['evolution_times'])*1e6)+10)

        PulsarMeasurement.autoconfig(self)


    def generate_sequence(self, upload=True):

        # define the necessary pulses
        X = pulselib.MW_IQmod_pulse('Pi_2-pulse',
            I_channel='MW_Imod', Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod',
            frequency = self.params['MW_pulse_frequency'],
            PM_risetime = self.params['MW_pulse_mod_risetime'])
        ##This is a temp solution, I cant find the awgchannels def for lt3 -Machiel
        qt.pulsar.define_channel(id='ch3_marker2', name='adwin_sync', type='marker',
            high=2.0, low=0, offset=0., delay=0., active=True)
        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = self.params['AWG_to_adwin_ttl_trigger_duration'],
            amplitude = 2)
        T = pulse.SquarePulse(channel='MW_Imod', name='delay',
            length = 200e-9, amplitude = 0.)
        T_us = pulse.SquarePulse(channel='MW_Imod', name='delay',
            length = 1000e-9, amplitude = 0.)
        # make the elements - one for each ssb frequency
        elements = []
        seq = pulsar.Sequence('ElectronRamsey sequence')
        for i in range(self.params['pts']):

            e = element.Element('ElectronRamsey_pt-%d' % i, pulsar=qt.pulsar,
                global_time = True)
            e.append(T)

            e.append(pulse.cp(X,
                amplitude = self.params['pi2_amps'][i],
                phase = self.params['pi2_phases1'][i],
                length=self.params['pi2_lengths'][i]))

            if (self.params['evolution_times'][i]>1e-6):

                elements.append(e)
                seq.append(name=e.name, wfname=e.name, trigger_wait=True)

                e = element.Element('ElectronRamsey_wait_pt-%d' % i, pulsar=qt.pulsar,
                    global_time = True)

                e.append(T_us)
                N=int(self.params['evolution_times'][i]*1e6)
                seq.append(name=e.name, wfname=e.name, trigger_wait=False,repetitions=N)

                #I would think this pulse should be in the next element! - Machiel
                e.append(pulse.cp(T,
                    length = self.params['evolution_times'][i]-(N*1e-6)))
                elements.append(e)
                e = element.Element('ElectronRamsey_second_pi2_pt-%d' % i, pulsar=qt.pulsar,
                global_time = True)

            else:
                e.append(pulse.cp(T,
                    length = self.params['evolution_times'][i]))

            e.append(pulse.cp(X,
                amplitude = self.params['pi2_amps'][i],
                phase = self.params['pi2_phases2'][i],
                length=self.params['pi2_lengths'][i]))
            e.append(T)
            e.append(T)
            e.append(T)
            e.append(T)
            e.append(adwin_sync)
            elements.append(e)
            if (self.params['evolution_times'][i]>1e-6):
                seq.append(name=e.name, wfname=e.name, trigger_wait=False)
            else:
                seq.append(name=e.name, wfname=e.name, trigger_wait=True)

         # upload the waveforms to the AWG
        if upload:
            if upload=='old_method':
                qt.pulsar.upload(*elements)
                qt.pulsar.program_sequence(seq)
            else:
                qt.pulsar.program_awg(seq,*elements)

class ElectronT1Switch(PulsarMeasurement):

    mprefix = 'ElectronT1Switch'

    def autoconfig(self):
        self.params['wait_for_AWG_done'] = 1
        PulsarMeasurement.autoconfig(self)

        #Add initial and readout state options (ms=1, ms=0, ms=-1)
        #self.params['T1_initial_state'] = 'ms=0'
        #self.params['T1_readout_state'] = 'ms=0'

    def generate_sequence(self, upload=True, debug = False):

        ### define basic pulses/times ###
        # pi-pulse, needs different pulses for ms=-1 and ms=+1 transitions in the future.
        X = pulselib.MW_IQmod_Switch_pulse('Pi-pulse',
            I_channel='MW_Imod', Q_channel='MW_Qmod',
            Sw_channel='MW_switch', Sw_Inv_channel='MW_invswitch'
            PM_channel='MW_pulsemod',
            frequency = self.params['MW_modulation_frequency'],
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            length = self.params['fast_pi_duration'],
            amplitude = self.params['fast_pi_amp'])
        # Wait-times
        T = pulse.SquarePulse(channel='MW_Imod', name='delay',
            length = self.params['wait_time_repeat_element']*1e-6, amplitude = 0.)
        T_before_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
            length = 100e-9, amplitude = 0.) #the unit waittime is 10e-6 s
        T_after_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
            length = 850e-9, amplitude = 0.) #the length of this time should depends on the pi-pulse length/.
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
                elif self.params['T1_readout_state'] == 'ms=-1' and self.params['T1_initial_state'] == 'ms=0':
                    seq.append(name='Readout_Pi_pulse_%d'%i,wfname='Pi_pulse',trigger_wait=True)
                    seq.append(name='ElectronT1_ADwin_trigger_%d'%i, wfname='ADwin_trigger', trigger_wait=False)
                #elif self.params['T1_initial_state'] == 'ms=+1' and self.params['T1_readout_state'] == 'ms=0':
                #elif self.params['T1_readout_state'] == 'ms=+1' and self.params['T1_initial_state'] == 'ms=0':
                else:
                    seq.append(name='ElectronT1_ADwin_trigger_%d'%i, wfname='ADwin_trigger', trigger_wait=True)

         # upload the waveforms to the AWG
        if upload:
            qt.pulsar.program_awg(seq,*list_of_elements, debug = debug)


class ElectronT1(PulsarMeasurement):

    mprefix = 'ElectronT1'

    def autoconfig(self):
        self.params['wait_for_AWG_done'] = 1
        PulsarMeasurement.autoconfig(self)

        #Add initial and readout state options (ms=1, ms=0, ms=-1)
        #self.params['T1_initial_state'] = 'ms=0'
        #self.params['T1_readout_state'] = 'ms=0'

    def generate_sequence(self, upload=True, debug = False):

        ### define basic pulses/times ###
        # pi-pulse, needs different pulses for ms=-1 and ms=+1 transitions in the future.
        X = pulselib.MW_IQmod_pulse('Pi-pulse',
            I_channel='MW_Imod', Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod',
            frequency = self.params['MW_modulation_frequency'],
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            length = self.params['fast_pi_duration'],
            amplitude = self.params['fast_pi_amp'])
        # Wait-times
        T = pulse.SquarePulse(channel='MW_Imod', name='delay',
            length = self.params['wait_time_repeat_element']*1e-6, amplitude = 0.)
        T_before_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
            length = 100e-9, amplitude = 0.) #the unit waittime is 10e-6 s
        T_after_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
            length = 850e-9, amplitude = 0.) #the length of this time should depends on the pi-pulse length/.
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
                elif self.params['T1_readout_state'] == 'ms=-1' and self.params['T1_initial_state'] == 'ms=0':
                    seq.append(name='Readout_Pi_pulse_%d'%i,wfname='Pi_pulse',trigger_wait=True)
                    seq.append(name='ElectronT1_ADwin_trigger_%d'%i, wfname='ADwin_trigger', trigger_wait=False)
                #elif self.params['T1_initial_state'] == 'ms=+1' and self.params['T1_readout_state'] == 'ms=0':
                #elif self.params['T1_readout_state'] == 'ms=+1' and self.params['T1_initial_state'] == 'ms=0':
                else:
                    seq.append(name='ElectronT1_ADwin_trigger_%d'%i, wfname='ADwin_trigger', trigger_wait=True)

         # upload the waveforms to the AWG
        if upload:
            qt.pulsar.program_awg(seq,*list_of_elements, debug = debug)



class RepElectronRamseys(ElectronRamsey):
    mprefix = 'RepElectronRamsey'
    adwin_process='ssro_multiple_RO'

    def autoconfig(self):
        self.params['sequence_wait_time'] = \
            int(np.ceil(np.max(self.params['evolution_times'])*1e3)+1)
        PulsarMeasurement.autoconfig(self)

    def save(self, name='ssro'):
        reps = self.adwin_var('completed_reps')
        self.save_adwin_data(name,
                [   ('CR_before', reps),
                    ('CR_after', reps),
                    ('SP_hist', self.params['SP_duration']),
                    ('RO_data', reps),
                    ('statistics', 10),
                    'completed_reps',
                    'total_CR_counts'])

class RepElectronRamseysCORPSE(ElectronRamseyCORPSE):
    mprefix = 'RepElectronRamseyCORPSE'
    adwin_process='ssro_multiple_RO'

    def autoconfig(self):
        self.params['sequence_wait_time'] = \
            int(np.ceil(np.max(self.params['evolution_times'])*1e3)+2)
        self.params['A_SP_repump_voltage']=self.A_aom.power_to_voltage(self.params['A_SP_repump_amplitude'])
        #print 'HERE!!!'
        PulsarMeasurement.autoconfig(self)

    def save(self, name='ssro'):
        reps = self.adwin_var('completed_reps')
        self.save_adwin_data(name,
                [   ('CR_before', reps),
                    ('CR_after', reps),
                    ('SP_hist', self.params['SP_duration']),
                    ('RO_data', reps),
                    ('statistics', 10),
                    'completed_reps',
                    'total_CR_counts'])
        
class initNitrogen_DarkESR(DarkESR):
    mprefix = 'PulsarinitNDarkESR'

    def generate_sequence(self, upload=True):

        # define the necessary pulses
        X = pulselib.MW_IQmod_pulse('Weak pi-pulse',
            I_channel='MW_Imod', Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod',
            amplitude = self.params['ssbmod_amplitude'],
            length = self.params['pulse_length'],
            PM_risetime = self.params['MW_pulse_mod_risetime'])
        N_pulse = pulselib.RF_erf_envelope(
            channel = 'RF',
            frequency = self.params['N_0-1_splitting_ms-1'],
            amplitude=0.5,
            duration=1e6)
        
        pi2pi_0 = pulselib.MW_IQmod_pulse('pi2pi pulse mI=0',
        I_channel = 'MW_Imod',
        Q_channel = 'MW_Qmod',
        PM_channel = 'MW_pulsemod',
        PM_risetime = self.params['MW_pulse_mod_risetime'],
        frequency = self.params['MW_modulation_frequency'],
        amplitude = self.params['pi2pi_mIp1_amp'],
        length = self.params['pi2pi_mI0_duration'])
        Trig = pulse.SquarePulse(channel = 'adwin_sync',
        length = 5e-6, amplitude = 2)
        SP = pulse.SquarePulse(channel = 'AOM_Newfocus', amplitude = 1.0,length=10e-6)

        T = pulse.SquarePulse(channel='MW_Imod', name='delay')
        T.amplitude = 0.
        T.length = 2e-6

        # make the elements - one for each ssb frequency
        elements = []
        seq = pulsar.Sequence('Init N - DarkESR sequence')

        #Nitrogen init element
        n = element.Element('Nitrogen-init', pulsar=qt.pulsar)
        n.append(pulse.cp(T,length=100e-9))
        n.append(pulse.cp(pi2pi_0,name='pi2pi_first',
                               frequency=self.params['MW_modulation_frequency']+2*self.params['N_HF_frq'],
                               amplitude=self.params['pi2pi_mIm1_amp']))
        #n.append(pulse.cp(T,length=1e-6))
        #n.append(pulse.cp(N_pulse,name='RF-first',
        #                         frequency=self.params['RF1_frq'],
        #                         amplitude=self.params['RF_amp'],
        #                         length=self.params['RF1_duration']))
        #n.append(pulse.cp(T,length=1e-6))
        n.append(SP)
        n.append(pulse.cp(T,length=1e-6))
        n.append(pulse.cp(pi2pi_0, name='pi2pi_second',
                                   frequency=self.params['MW_modulation_frequency']+self.params['N_HF_frq'],#-self.params['N_HF_frq'],
                                   amplitude=self.params['pi2pi_mI0_amp']))
        n.append(pulse.cp(T,length=1e-6))
        #n.append(pulse.cp(N_pulse,name='RF-second',
        #      frequency=self.params['RF2_frq'],
        #      amplitude=self.params['RF_amp'],
        #      length=self.params['RF2_duration']))
        n.append(pulse.cp(T,length=1e-6))
        n.append(SP)
        elements.append(n)
        for i, f in enumerate(np.linspace(self.params['ssbmod_frq_start'],
            self.params['ssbmod_frq_stop'], self.params['pts'])):
            
            seq.append(name='Nitrogen-init-%d' % i, wfname=n.name, trigger_wait=True,repetitions=self.params['init_repetitions'])

            #Dark esr element
            e = element.Element('DarkESR_frq-%d' % i, pulsar=qt.pulsar)
            e.append(T)
            e.append(X(frequency=f))
            e.append(Trig)
            elements.append(e)
            seq.append(name=e.name, wfname=e.name, trigger_wait=False)  

         # upload the waveforms to the AWG
        if upload:
            if upload=='old_method':
                qt.pulsar.upload(*elements)
                qt.pulsar.program_sequence(seq)
            else:
                qt.pulsar.program_awg(seq,*elements)


class MBI(PulsarMeasurement):
    mprefix = 'PulsarMBI'
    adwin_process = 'MBI'

    def autoconfig(self):
        self.params['sweep_length'] = self.params['pts']
        self.params['repetitions'] = \
                self.params['nr_of_ROsequences'] * \
                self.params['pts'] * \
                self.params['reps_per_ROsequence']

        self.params['Ex_MBI_voltage'] = \
            self.E_aom.power_to_voltage(
                    self.params['Ex_MBI_amplitude'])

        self.params['Ex_N_randomize_voltage'] = \
            self.E_aom.power_to_voltage(
                    self.params['Ex_N_randomize_amplitude'])

        self.params['A_N_randomize_voltage'] = \
            self.A_aom.power_to_voltage(
                    self.params['A_N_randomize_amplitude'])

        self.params['repump_N_randomize_voltage'] = \
            self.repump_aom.power_to_voltage(
                    self.params['repump_N_randomize_amplitude'])

        self.params['A_SP_voltage_before_MBI'] = \
            self.A_aom.power_to_voltage(
                    self.params['A_SP_amplitude_before_MBI'])

        # Calling autoconfig from sequence.SequenceSSRO and thus
        # from ssro.IntegratedSSRO after defining self.params['repetitions'],
        # since the autoconfig of IntegratedSSRO uses this parameter.

        PulsarMeasurement.autoconfig(self)



    def run(self, autoconfig=True, setup=True):
        if autoconfig:
            self.autoconfig()

        if setup:
            self.setup()

        for i in range(10):
            self.physical_adwin.Stop_Process(i+1)
            qt.msleep(0.1)
        qt.msleep(1)
        # self.adwin.load_MBI()   
        # New functionality, now always uses the adwin_process specified as a class variables 
        loadstr = 'self.adwin.load_'+str(self.adwin_process)+'()'   
        exec(loadstr)
        qt.msleep(1)
        # print loadstr 

        length = self.params['nr_of_ROsequences']

        self.physical_adwin.Set_Data_Long(
                np.array(self.params['repump_after_MBI_duration'], dtype=int), 33, 1, length)
        self.physical_adwin.Set_Data_Long(
                np.array(self.params['E_RO_durations'], dtype=int), 34, 1, length)

        v = [ self.A_aom.power_to_voltage(p) for p in self.params['repump_after_MBI_A_amplitude'] ]
        self.physical_adwin.Set_Data_Float(np.array(v), 35, 1, length)

        v = [ self.E_aom.power_to_voltage(p) for p in self.params['repump_after_MBI_E_amplitude'] ]
        self.physical_adwin.Set_Data_Float(np.array(v), 39, 1, length)

        v = [ self.E_aom.power_to_voltage(p) for p in self.params['E_RO_amplitudes'] ]
        self.physical_adwin.Set_Data_Float(np.array(v), 36, 1, length)

        self.physical_adwin.Set_Data_Long(
                np.array(self.params['send_AWG_start'], dtype=int), 37, 1, length)

        self.physical_adwin.Set_Data_Long(
                np.array(self.params['sequence_wait_time'], dtype=int), 38, 1, length)

        self.start_adwin_process(stop_processes=['counter'], load=False)
        qt.msleep(1)
        self.start_keystroke_monitor('abort')

        while self.adwin_process_running():

            if self.keystroke('abort') != '':
                print 'aborted.'
                self.stop_keystroke_monitor('abort')
                break

            reps_completed = self.adwin_var('completed_reps')
            print('completed %s / %s readout repetitions' % \
                    (reps_completed, self.params['repetitions']))
            qt.msleep(1)

        try:
            self.stop_keystroke_monitor('abort')
        except KeyError:
            pass # means it's already stopped

        self.stop_adwin_process()
        reps_completed = self.adwin_var('completed_reps')
        print('completed %s / %s readout repetitions' % \
                (reps_completed, self.params['repetitions']))


    def save(self, name='adwindata'):
        reps = self.adwin_var('completed_reps')
        sweeps = self.params['pts'] * self.params['reps_per_ROsequence']

        self.save_adwin_data(name,
                [   ('CR_before', sweeps),
                    ('CR_after', sweeps),
                    ('MBI_attempts', sweeps),
                    ('statistics', 10),
                    ('ssro_results', reps),
                    ('MBI_cycles', sweeps),
                    ('MBI_time', sweeps),  ])
        return

    def _MBI_element(self,name ='MBI CNOT'):
        # define the necessary pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 100e-9, amplitude = 0)

        X = pulselib.MW_IQmod_pulse('MBI MW pulse',
            I_channel = 'MW_Imod', Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            frequency = self.params['AWG_MBI_MW_pulse_ssbmod_frq'],
            amplitude = self.params['AWG_MBI_MW_pulse_amp'],
            length = self.params['AWG_MBI_MW_pulse_duration'],
            PM_risetime = self.params['MW_pulse_mod_risetime'])

        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = (self.params['AWG_to_adwin_ttl_trigger_duration'] \
                + self.params['AWG_wait_for_adwin_MBI_duration']),
            amplitude = 2)

        # the actual element
        mbi_element = element.Element(name, pulsar=qt.pulsar)
        mbi_element.append(T)
        mbi_element.append(X)
        mbi_element.append(adwin_sync)

        return mbi_element




class Magnetometry(PulsarMeasurement):
    mprefix = 'PulsarMagnetometry'
    adwin_process = 'adaptive_magnetometry'

    def autoconfig(self):

        self.params['sweep_length'] = self.params['repetitions']*self.params['adptv_steps']*self.params['M']
        self.params['pts'] = self.params['repetitions']*self.params['adptv_steps']*self.params['M']
        
        self.params['Ex_MBI_voltage'] = \
            self.E_aom.power_to_voltage(
                    self.params['Ex_MBI_amplitude'])

        self.params['Ex_N_randomize_voltage'] = \
            self.E_aom.power_to_voltage(
                    self.params['Ex_N_randomize_amplitude'])

        self.params['A_N_randomize_voltage'] = \
            self.A_aom.power_to_voltage(
                    self.params['A_N_randomize_amplitude'])

        self.params['repump_N_randomize_voltage'] = \
            self.repump_aom.power_to_voltage(
                    self.params['repump_N_randomize_amplitude'])

        self.params['A_SP_voltage_before_MBI'] = \
            self.A_aom.power_to_voltage(
                    self.params['A_SP_amplitude_before_MBI'])

                # self.params['A_SP_voltage'] = \
        #     self.A_aom.power_to_voltage(
        #             self.params['A_SP_amplitude'])

        # Calling autoconfig from sequence.SequenceSSRO and thus
        # from ssro.IntegratedSSRO after defining self.params['repetitions'],
        # since the autoconfig of IntegratedSSRO uses this parameter.
        PulsarMeasurement.autoconfig(self)
        


    def run(self, autoconfig=True, setup=True):
        if autoconfig:
            self.autoconfig()

        if setup:
            self.setup()

        for i in range(10):
            self.physical_adwin.Stop_Process(i+1)
            qt.msleep(0.1)
        qt.msleep(1)
        # self.adwin.load_MBI()   
        # New functionality, now always uses the adwin_process specified as a class variables 
        print 'Load adwin process'
        loadstr = 'self.adwin.load_'+str(self.adwin_process)+'()'   
        exec(loadstr)
        qt.msleep(1)
        print 'Done loading adwin process'
        # print loadstr 

        length = self.params['repetitions']*self.params['adptv_steps']

        self.start_adwin_process(stop_processes=['counter'], load=False)
        qt.msleep(1)
        self.start_keystroke_monitor('abort')

        while self.adwin_process_running():

            if self.keystroke('abort') != '':
                print 'aborted.'
                self.stop_keystroke_monitor('abort')
                break

            reps_completed = self.adwin_var('completed_reps')
            print('completed %s / %s readout repetitions' % \
                    (reps_completed, self.params['repetitions']*self.params['adptv_steps']))
            qt.msleep(1)

        try:
            self.stop_keystroke_monitor('abort')
        except KeyError:
            pass # means it's already stopped

        self.stop_adwin_process()
        reps_completed = self.adwin_var('completed_reps')
        print('completed %s / %s readout repetitions' % \
                (reps_completed, self.params['repetitions']*self.params['adptv_steps']))


    def save(self, name='adwindata'):
        reps = self.adwin_var('completed_reps')
        sweeps = self.params['repetitions'] * self.params['adptv_steps']

        self.save_adwin_data(name,
                [   ('CR_before', sweeps),
                    ('CR_after', sweeps),
                    ('RO_data', sweeps),
                    ('set_phase', sweeps),
                    ('div_p_k_opt', sweeps),
                    ('real_p_tn', sweeps),
                    ('real_p_2tn', sweeps),
                    ('imag_p_tn', sweeps),
                    ('imag_p_2tn', sweeps),
                    'completed_reps'])

        return

    def _Ninit_element(self,name ='N_init'):
        # define the necessary pulses
        pi2pi_0 = pulselib.MW_IQmod_pulse('pi2pi pulse mI=0',
        I_channel = 'MW_Imod',
        Q_channel = 'MW_Qmod',
        PM_channel = 'MW_pulsemod',
        PM_risetime = self.params['MW_pulse_mod_risetime'],
        frequency = self.params['MW_modulation_frequency'],
        amplitude = self.params['pi2pi_mIp1_amp'],
        length = self.params['pi2pi_mI0_duration'])
        SP = pulse.SquarePulse(channel = 'AOM_Newfocus', amplitude = 1.0,length=10e-6)
        total_length = int((2*pi2pi_0.length + 2*SP.length + 2.1e-6)*0.25e9)
        clock_pulse = pulse.clock_train (channel = 'fpga_clock', amplitude = 4.0, nr_up_points=2, nr_down_points=2, cycles= total_length+100)

        T = pulse.SquarePulse(channel='MW_Imod', name='delay')
        T.amplitude = 0.
        T.length = 2e-6

        n = element.Element('Nitrogen-init', pulsar=qt.pulsar)
        n.append(pulse.cp(T,length=100e-9))
        n.append(pulse.cp(pi2pi_0,name='pi2pi_first',
                               frequency=self.params['MW_modulation_frequency']+2*self.params['N_HF_frq'],
                               amplitude=self.params['pi2pi_mIm1_amp']))
        n.append(SP)
        n.append(pulse.cp(T,length=1e-6))
        n.append(pulse.cp(pi2pi_0, name='pi2pi_second',
                                   frequency=self.params['MW_modulation_frequency']+self.params['N_HF_frq'],#-self.params['N_HF_frq'],
                                   amplitude=self.params['pi2pi_mI0_amp']))
        n.append(pulse.cp(T,length=1e-6))
        n.append(SP)
        total_length = int((2*pi2pi_0.length + 2*SP.length + 2.1e-6)*1e9)
        n.add(pulse.cp(clock_pulse, amplitude = 4.0))
        return n

    def _MBI_element(self,name='MBI_CNOT'):
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 100e-9, amplitude = 0)

    def _MBI_element(self,name ='MBI_CNOT'):
        # define the necessary pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 100e-9, amplitude = 0)

        X = pulselib.MW_IQmod_pulse('MBI MW pulse',
            I_channel = 'MW_Imod', Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            frequency = self.params['AWG_MBI_MW_pulse_ssbmod_frq'],
            amplitude = self.params['AWG_MBI_MW_pulse_amp'],
            length = self.params['AWG_MBI_MW_pulse_duration'],
            PM_risetime = self.params['MW_pulse_mod_risetime'])

        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = (self.params['AWG_to_adwin_ttl_trigger_duration'] \
                + self.params['AWG_wait_for_adwin_MBI_duration']),
            amplitude = 2)

        # the actual element
        mbi_element = element.Element(name, pulsar=qt.pulsar)
        mbi_element.append(T)
        mbi_element.append(X)
        mbi_element.append(adwin_sync)

        return mbi_element





class RTMagnetometry(Magnetometry):
    mprefix = 'PulsarMagnetometry'
    adwin_process = 'adaptive_magnetometry_realtime_swarm'

    def autoconfig(self):

        self.params['sweep_length'] = self.params['repetitions']*self.params['adptv_steps']*self.params['M']
        self.params['pts'] = self.params['repetitions']*self.params['adptv_steps']*self.params['M']
        
        # Calling autoconfig from sequence.SequenceSSRO and thus
        # from ssro.IntegratedSSRO after defining self.params['repetitions'],
        # since the autoconfig of IntegratedSSRO uses this parameter.
        PulsarMeasurement.autoconfig(self)

    def run(self, autoconfig=True, setup=True):
        if autoconfig:
            self.autoconfig()

        if setup:
            self.setup()

        for i in range(10):
            self.physical_adwin.Stop_Process(i+1)
            qt.msleep(0.1)
        qt.msleep(1)
        # self.adwin.load_MBI()   
        # New functionality, now always uses the adwin_process specified as a class variables 
        print 'Load adwin process: ', str(self.adwin_process)
        loadstr = 'self.adwin.load_'+str(self.adwin_process)+'()'   
        exec(loadstr)
        qt.msleep(1)
        print 'Done loading adwin process'
        # print loadstr 

        length = self.params['repetitions']*self.params['adptv_steps']

        self.start_adwin_process(stop_processes=['counter'], load=False)
        qt.msleep(1)
        self.start_keystroke_monitor('abort')

        while self.adwin_process_running():

            if self.keystroke('abort') != '':
                print 'aborted.'
                self.stop_keystroke_monitor('abort')
                break

            reps_completed = self.adwin_var('completed_reps')
            print('completed %s / %s readout repetitions' % \
                    (reps_completed, self.params['repetitions']*self.params['adptv_steps']))
            qt.msleep(1)

        try:
            self.stop_keystroke_monitor('abort')
        except KeyError:
            pass # means it's already stopped

        self.stop_adwin_process()
        reps_completed = self.adwin_var('completed_reps')
        print('completed %s / %s readout repetitions' % \
                (reps_completed, self.params['repetitions']*self.params['adptv_steps']))


    def save(self, name='adwindata'):
        reps = self.adwin_var('completed_reps')
        sweeps = self.params['repetitions'] * self.params['adptv_steps']
        #m_sweeps = self.params['repetitions'] * self.params['adptv_steps']*self.params['M']
        max_k_els = (self.params['G']+self.params['F']*self.params['adptv_steps']) + 10

        if self.params['swarm_opt']:
            m_sweeps = self.params['repetitions']*(self.params['adptv_steps']*self.params['G'] + self.params['adptv_steps']*self.params['F']*(self.params['adptv_steps']-1)/2)
            phase_sweeps = m_sweeps
        elif self.params['do_add_phase']:
            m_sweeps=self.params['repetitions']*(self.params['adptv_steps']*self.params['G'] + self.params['adptv_steps']*self.params['F']*(self.params['adptv_steps']-1)/2)
            phase_sweeps = sweeps
        else:
            m_sweeps=sweeps    

        self.save_adwin_data(name,
                [   ('CR_before', sweeps),
                    ('CR_after', sweeps),
                    ('RO_data', m_sweeps),
                    ('set_phase', sweeps),
                    ('theta', phase_sweeps),
                    ('timer', sweeps),
                    #('real_p_tn', sweeps),
                    #('real_p_2tn', sweeps),
                    #('imag_p_tn', sweeps),
                    #('imag_p_2tn', sweeps),
                    #('debug1', m_sweeps),
                    #('debug2', m_sweeps),
                    #('debug3', m_sweeps),
                    #('debug4', m_sweeps),                    
                    #('real_p_k', max_k_els),
                    #('imag_p_k', max_k_els),                    
                    'completed_reps'])

        return



class GeneralElectronRabi(PulsarMeasurement):
    '''
    This class generates a sequence of Rabi oscillations.
    You have to provide the type of pulse.
    '''
    mprefix = 'ElectronRabi'

    def autoconfig(self):
        self.params['sequence_wait_time'] = \
            int(np.ceil(np.max(self.params['pulse_sweep_durations'])*1e6)+10)


        PulsarMeasurement.autoconfig(self)

    def generate_sequence(self, upload=True, **kw):
        #print 'test'
        # define the necessary pulses

        X=kw.get('pulse_pi', None)

   
        T = pulse.SquarePulse(channel='MW_Qmod', name='delay',
            length = 200e-9, amplitude = 0.)

        # make the elements - one for each ssb frequency
        elements = []
        for i in range(self.params['pts']):

            e = element.Element('ElectronRabi_pt-%d' % i, pulsar=qt.pulsar)

            e.append(T)
            e.append(pulse.cp(X,
                length = self.params['pulse_sweep_durations'][i],
                amplitude = self.params['pulse_sweep_amps'][i]))

            elements.append(e)


        # create a sequence from the pulses
        seq = pulsar.Sequence('ElectronRabi sequence with {} pulses'.format(self.params['pulse_type']))
        for e in elements:
            seq.append(name=e.name, wfname=e.name, trigger_wait=True)

         # upload the waveforms to the AWG
        if upload:
            if upload=='old_method':
                qt.pulsar.upload(*elements)
                qt.pulsar.program_sequence(seq)
            else:
                qt.pulsar.program_awg(seq,*elements)



class GeneralDarkESR(PulsarMeasurement):
    '''
    This class is used to measure ESR in pulse mode.
    As it only supports IQmod, do not forget to calibrate your pulse with IQ modulation.  
    '''

    mprefix = 'GeneralDarkESR'

    def autoconfig(self):
        self.params['sequence_wait_time'] = \
            int(np.ceil(self.params['MW_pi_duration']*1e6)+15)

        PulsarMeasurement.autoconfig(self)

        self.params['sweep_name'] = 'MW frq (GHz)'
        self.params['sweep_pts'] = (np.linspace(self.params['ssbmod_frq_start'],
            self.params['ssbmod_frq_stop'], self.params['pts']) + \
                self.params['mw_frq'])*1e-9

    def generate_sequence(self, upload=True, **kw):

        # define the necessary pulses
        
        X=kw.get('pulse_pi', None)

        T = pulse.SquarePulse(channel='MW_Imod', name='delay')
        T.amplitude = 0.
        T.length = 2e-6

        # make the elements - one for each ssb frequency
        elements = []
        for i, f in enumerate(np.linspace(self.params['ssbmod_frq_start'],
            self.params['ssbmod_frq_stop'], self.params['pts'])):

            e = element.Element('DarkESR_frq-%d' % i, pulsar=qt.pulsar)
            e.add(T, name='wait')
            e.add(X(frequency=f), refpulse='wait')
            elements.append(e)

        # create a sequence from the pulses
        seq = pulsar.Sequence('DarkESR sequence with {} pulses'.format(self.params['pulse_type']))
        for e in elements:
            seq.append(name=e.name, wfname=e.name, trigger_wait=True)

        # upload the waveforms to the AWG
        if upload:
            #qt.pulsar.upload(*elements)
            qt.pulsar.program_awg(seq,*elements)

        # program the AWG
        #qt.pulsar.program_sequence(seq)\



class GeneralPiCalibration(PulsarMeasurement):
    """
    General Pi pulse calibration, generate_sequence needs to be supplied with a pi_pulse as kw.
    """
    mprefix = 'Pi_Calibration'

    def autoconfig(self):
        self.params['sequence_wait_time'] = 20

        PulsarMeasurement.autoconfig(self)


    def generate_sequence(self, upload=True, **kw):
        # electron manipulation pulses
        T = pulse.SquarePulse(channel='MW_Imod',
            length = 200e-9, amplitude = 0)

        X=kw.get('pulse_pi', None)

        wait_1us = element.Element('1us_delay', pulsar=qt.pulsar)
        wait_1us.append(pulse.cp(T, length=1e-6))

        sync_elt = element.Element('adwin_sync', pulsar=qt.pulsar)
        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = 10e-6, amplitude = 2)
        sync_elt.append(adwin_sync)

        elements = []
        for i in range(self.params['pts']):
            e = element.Element('pulse-{}'.format(i), pulsar=qt.pulsar)
            e.append(T,
                pulse.cp(X,
                    amplitude=self.params['MW_pulse_amplitudes'][i]
                    ))
            elements.append(e)

        # sequence
        seq = pulsar.Sequence('{} pi calibration'.format(self.params['pulse_type']))
        for i,e in enumerate(elements):           
            for j in range(self.params['multiplicity']):
                seq.append(name = e.name+'-{}'.format(j), 
                    wfname = e.name,
                    trigger_wait = (j==0))
                seq.append(name = 'wait-{}-{}'.format(i,j), 
                    wfname = wait_1us.name, 
                    repetitions = self.params['delay_reps'])
            seq.append(name='sync-{}'.format(i),
                 wfname = sync_elt.name)
        elements.append(wait_1us)
        elements.append(sync_elt)
        # upload the waveforms to the AWG
        if upload:
            if upload=='old_method':
                qt.pulsar.upload(*elements)
                qt.pulsar.program_sequence(seq)
            else:
                qt.pulsar.program_awg(seq,*elements)



class GeneralPi2Calibration(PulsarMeasurement):
    """
    Do a pi/2 pulse, compare to an element with pi/2 + pi-pulse; sweep the pi2 amplitude. 
    generate_sequence needs to be supplied with a pi_pulse and pi2_pulse as kw.
    """
    mprefix = 'Pi2_Calibration'

    def autoconfig(self):
        self.params['sequence_wait_time'] = 30

        PulsarMeasurement.autoconfig(self)


    def generate_sequence(self, upload=True, **kw):
        # electron manipulation pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 100e-9, amplitude = 0)
        TIQ = pulse.SquarePulse(channel='MW_Imod',
            length = 10e-9, amplitude = 0)

        pulse_pi=kw.get('pulse_pi', None)
        pulse_pi2=kw.get('pulse_pi2', None)

        wait_1us = element.Element('1us_delay', pulsar=qt.pulsar)
        wait_1us.append(pulse.cp(T, length=1e-6))

        sync_elt = element.Element('adwin_sync', pulsar=qt.pulsar)
        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = 10e-6, amplitude = 2)
        sync_elt.append(adwin_sync)

        elements = []

        seq = pulsar.Sequence('{} Pi2 Calibration'.format(self.params['pulse_type']))

        for i in range(self.params['pts_awg']):
            e = element.Element('{}_Pi2_Pi-{}'.format(self.params['pulse_type'],i), 
                pulsar = qt.pulsar,
                global_time=True)
            e.append(T)
            e.append(pulse.cp(pulse_pi2, amplitude = self.params['pulse_pi2_sweep_amps'][i]))
            e.append(pulse.cp(TIQ, length=2e-9))
            e.append(pulse.cp(pulse_pi))
            e.append(T)
            elements.append(e)
            seq.append(name='{}_Pi2_Pi-{}'.format(self.params['pulse_type'],i),
                wfname = e.name,
                trigger_wait=True)
            seq.append(name='synca-{}'.format(i),
                wfname = sync_elt.name)
            
            e = element.Element('{}_Pi2-{}'.format(self.params['pulse_type'],i), 
                pulsar = qt.pulsar,
                global_time=True)
            e.append(T)
            e.append(pulse.cp(pulse_pi2, amplitude = self.params['pulse_pi2_sweep_amps'][i]))
            e.append(pulse.cp(TIQ, length=2e-9))
            e.append(T)
            elements.append(e)
            seq.append(name='{}_Pi2-{}'.format(self.params['pulse_type'],i),
                wfname = e.name,
                trigger_wait=True)
            seq.append(name='syncb-{}'.format(i),
                wfname = sync_elt.name)
        elements.append(wait_1us)
        elements.append(sync_elt)
        # upload the waveforms to the AWG
        if upload:
            if upload=='old_method':
                qt.pulsar.upload(*elements)
                qt.pulsar.program_sequence(seq)
            else:
                qt.pulsar.program_awg(seq,*elements)

        self.params['sequence_wait_time'] = \
            int(np.ceil(np.max(np.array([e.length() for e in elements])*1e6))+10)



class GeneralElectronRamsey(PulsarMeasurement):
    """
    General class to implement Ramsey sequence. 
    generate_sequence needs to be supplied with a pi2_pulse as kw.
    """
    mprefix = 'GeneralElectronRamsey'

    def autoconfig(self):
        self.params['sequence_wait_time'] = \
            int(np.ceil(np.max(self.params['evolution_times'])*1e6)+10)


        PulsarMeasurement.autoconfig(self)

    def generate_sequence(self, upload=True, **kw):

        # define the necessary pulses
        
        X=kw.get('pulse_pi2', None)

        T = pulse.SquarePulse(channel='MW_Imod', name='delay',
            length = 200e-9, amplitude = 0.)

        # make the elements - one for each ssb frequency
        elements = []
        for i in range(self.params['pts']):

            e = element.Element('ElectronRamsey_pt-%d' % i, pulsar=qt.pulsar,
                global_time = True)
            e.append(T)

            e.append(pulse.cp(X,
                phase = self.params['pulse_sweep_pi2_phases1'][i]))

            e.append(pulse.cp(T,
                length = self.params['evolution_times'][i]))

            e.append(pulse.cp(X,
                phase = self.params['pulse_sweep_pi2_phases2'][i]))

            elements.append(e)
        return_e=e
        # create a sequence from the pulses
        seq = pulsar.Sequence('ElectronRamsey sequence with {} pulses'.format(self.params['pulse_type']))
        for e in elements:
            seq.append(name=e.name, wfname=e.name, trigger_wait=True)

        # upload the waveforms to the AWG
        if upload:
            if upload=='old_method':
                qt.pulsar.upload(*elements)
                qt.pulsar.program_sequence(seq)
            else:
                qt.pulsar.program_awg(seq,*elements)


        
class DD_GeneralSequence(PulsarMeasurement):
    """
    Class to implement dynamical decoupling sequence and look at the first revival. 
    """
    mprefix = 'DD_Sequence'

    def autoconfig(self):
        self.params['sequence_wait_time'] = \
            int(np.ceil(np.max(self.params['evolution_times']*2*self.params['number_pulses'])*1e6)+10)

        PulsarMeasurement.autoconfig(self)

    def generate_sequence(self, upload=True, **kw):

        pulse_pi=kw.get('pulse_pi', None)
        pulse_pi2=kw.get('pulse_pi2', None)

        T = pulse.SquarePulse(channel='MW_Imod', name='delay',
            length = 200e-9, amplitude = 0.)

        # make the elements - one for each ssb frequency
        elements = []
        for i in range(self.params['pts']):

            e = element.Element('DD_ZerothRevival_pt-%d' % i, pulsar=qt.pulsar,
                global_time = True)
            e.append(T)

            last = e.add(pulse.cp(pulse_pi2,
                        amplitude = self.params['pulse_pi2_sweep_amps'][i],
                        phase = self.params['pulse_pi2_sweep_phases1'][i]),
                    start = 200e-9,
                    name = 'pi2_1')
              
            for j in range(self.params['number_pulses']):


                last = e.add(pulse.cp(pulse_pi,
                        amplitude = self.params['pulse_pi_sweep_amps'][i],#*(-1)**np.mod(j+1,2),
                        phase = self.params['pulse_pi_sweep_phases'][j]),
                    refpulse = last,
                    refpoint = 'end' if (j == 0) else 'center',
                    refpoint_new = 'center',
                    start = self.params['evolution_times'][i] if (j == 0) else 2*self.params['evolution_times'][i],
                    name = 'pi_{}'.format(j))


            e.add(pulse.cp(pulse_pi2,
                    amplitude = self.params['pulse_pi2_sweep_amps'][i],
                    phase = self.params['pulse_pi2_sweep_phases2'][j]),
                refpulse = last,
                refpoint = 'center',
                refpoint_new = 'start',
                start = self.params['evolution_times'][i]+self.params['extra_wait_final_pi2'][i],
                name = 'pi2_2')
            
            elements.append(e)
        
        # create a sequence from the pulses
        seq = pulsar.Sequence('DD sequence with {} pulses'.format(self.params['pulse_type']))
        for e in elements:
            seq.append(name=e.name, wfname=e.name, trigger_wait=True)

        # upload the waveforms to the AWG
        if upload:
            if upload=='old_method':
                qt.pulsar.upload(*elements)
                qt.pulsar.program_sequence(seq)
            else:
                qt.pulsar.program_awg(seq,*elements)

class GeneralNPi4Calibration(PulsarMeasurement):
    """
    Do a pi/2 pulse, compare to an element with a Npi/4 + pi-pulse + Npi/4 echo; sweep the Npi4 amplitude.
    generate_sequence needs to be supplied with a pi_pulse and pi2_pulse as kw.
    """
    mprefix = 'GeneralNPi4Calibration_1'

    def generate_sequence(self, upload=True, **kw):
        # electron manipulation pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 100e-9, amplitude = 0)
        TIQ = pulse.SquarePulse(channel='MW_Imod',
            length = 10e-9, amplitude = 0)

        pulse_pi=kw.get('pulse_pi', None)
        pulse_pi2=kw.get('pulse_pi2', None)

        wait_1us = element.Element('1us_delay', pulsar=qt.pulsar)
        wait_1us.append(pulse.cp(T, length=1e-6))

        sync_elt = element.Element('adwin_sync', pulsar=qt.pulsar)
        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = 10e-6, amplitude = 2)
        sync_elt.append(adwin_sync)

        elements = []
        seq = pulsar.Sequence('{} NPi4 Calibration 1'.format(self.params['pulse_type']))

        for i in range(self.params['pts_awg']):
            e = element.Element('{}-NPi4_Pi_NPi4-{}'.format(self.params['pulse_type'],i), 
                pulsar = qt.pulsar,
                global_time=True)

            e.append(T)

            last = e.add(pulse.cp(pulse_pi2,
                        length= self.params['pulse_Npi4_sweep_durations'][i],
                        amplitude = self.params['pulse_Npi4_sweep_amps'][i],
                        phase = self.params['pulse_Npi4_sweep_phases'][i]),
                    start = 200e-9,
                    name = 'pi2_1')
             
            j=0

            last = e.add(pulse_pi,
                refpulse = last,
                refpoint = 'end', #XXXX if (j == 0) else 'center',
                refpoint_new = 'center',
                start = self.params['evolution_times'][i],
                name = 'pi_{}'.format(j))

            e.add(pulse.cp(pulse_pi2,
                    length= self.params['pulse_Npi4_sweep_durations'][i],
                    amplitude = self.params['pulse_Npi4_sweep_amps'][i],
                    phase = self.params['pulse_Npi4_sweep_phases'][i]),
                refpulse = last,
                refpoint = 'center',
                refpoint_new = 'start',#'start',
                start = self.params['evolution_times'][i]+self.params['extra_wait_final_Npi4'][i],
                name = 'Npi4_2')

            elements.append(e)
            seq.append(name='{}-NPi4_Pi_NPi4-{}'.format(self.params['pulse_type'],i),
                wfname = e.name,
                trigger_wait=True)
            seq.append(name='synca-{}'.format(i),
                wfname = sync_elt.name)
            
            e = element.Element('{}_Pi2-{}'.format(self.params['pulse_type'],i),
                pulsar = qt.pulsar,
                global_time=True)
            e.append(T)
            e.append(pulse_pi2)
            e.append(pulse.cp(TIQ, length=2e-9))
            e.append(T)
            elements.append(e)
            seq.append(name='{}_Pi2-{}'.format(self.params['pulse_type'],i),
                wfname = e.name,
                trigger_wait=True)
            seq.append(name='syncb-{}'.format(i),
                wfname = sync_elt.name)
        elements.append(wait_1us)
        elements.append(sync_elt)
        # program AWG
        if upload:
            if upload=='old_method':
                qt.pulsar.upload(*elements)
                qt.pulsar.program_sequence(seq)
            else:
                qt.pulsar.program_awg(seq,*elements)

        self.params['sequence_wait_time'] = \
            int(np.ceil(np.max(np.array([e.length() for e in elements])*1e6))+10)



class GeneralPi4Calibration_2(PulsarMeasurement):
    """
    Do a pi/4 pulse, compare to an element with a pi/2 + pi-pulse + pi/4 echo; sweep the pi4 amplitude.
    generate_sequence needs to be supplied with a pi_pulse and pi2_pulse as kw.
    """
    mprefix = 'GeneralPi4Calibration_2'

    def generate_sequence(self, upload=True, **kw):
        # electron manipulation pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 100e-9, amplitude = 0)
        TIQ = pulse.SquarePulse(channel='MW_Imod',
            length = 10e-9, amplitude = 0)

        pulse_pi=kw.get('pulse_pi', None)
        pulse_pi2=kw.get('pulse_pi2', None)

        wait_1us = element.Element('1us_delay', pulsar=qt.pulsar)
        wait_1us.append(pulse.cp(T, length=1e-6))

        sync_elt = element.Element('adwin_sync', pulsar=qt.pulsar)
        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = 10e-6, amplitude = 2)
        sync_elt.append(adwin_sync)

        elements = []
        seq = pulsar.Sequence('{} Pi4 Calibration_2'.format(self.params['pulse_type']))

        for i in range(self.params['pts_awg']):
            e = element.Element('{}-Pi4_Pi-Pi4-{}'.format(self.params['pulse_type'],i), 
                pulsar = qt.pulsar,
                global_time=True)

            e.append(T)

            last = e.add(pulse_pi2,
                    start = 200e-9,
                    name = 'pi2_1')
             
            j=0

            last = e.add(pulse_pi,
                refpulse = last,
                refpoint = 'end', #XXXX if (j == 0) else 'center',
                refpoint_new = 'center',
                start = self.params['evolution_times'][i],
                name = 'pi_{}'.format(j))

            e.add(pulse.cp(pulse_pi2,
                    length= self.params['pulse_pi4_sweep_durations'][i],
                    amplitude = self.params['pulse_pi4_sweep_amps'][i],
                    phase = self.params['pulse_pi4_sweep_phases'][i]),
                refpulse = last,
                refpoint = 'center',
                refpoint_new = 'start',#'start',
                start = self.params['evolution_times'][i]+self.params['extra_wait_final_pi4'][i],
                name = 'pi4_2')

            elements.append(e)
            seq.append(name='{}-Pi4_Pi-Pi4-{}'.format(self.params['pulse_type'],i),
                wfname = e.name,
                trigger_wait=True)
            seq.append(name='synca-{}'.format(i),
                wfname = sync_elt.name)
            
            e = element.Element('{}_Pi4-{}'.format(self.params['pulse_type'],i),
                pulsar = qt.pulsar,
                global_time=True)
            e.append(T)
            e.append(pulse.cp(pulse_pi2,
                    length= self.params['pulse_pi4_sweep_durations'][i],
                    amplitude = self.params['pulse_pi4_sweep_amps'][i],
                    phase = self.params['pulse_pi4_sweep_phases'][i]))
            e.append(pulse.cp(TIQ, length=2e-9))
            e.append(T)
            elements.append(e)
            seq.append(name='{}_Pi2-{}'.format(self.params['pulse_type'],i),
                wfname = e.name,
                trigger_wait=True)
            seq.append(name='syncb-{}'.format(i),
                wfname = sync_elt.name)
        elements.append(wait_1us)
        elements.append(sync_elt)
        # program AWG
        if upload:
            if upload=='old_method':
                qt.pulsar.upload(*elements)
                qt.pulsar.program_sequence(seq)
            else:
                qt.pulsar.program_awg(seq,*elements)

        self.params['sequence_wait_time'] = \
            int(np.ceil(np.max(np.array([e.length() for e in elements])*1e6))+10)
