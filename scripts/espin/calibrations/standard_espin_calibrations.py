"""
Work in progress :)
Anais
"""
#reload all parameters and modules
execfile(qt.reload_current_setup)

# reload all parameters and modules, import classes
from measurement.scripts.espin import espin_funcs as funcs
reload(funcs)


SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']


class CORPSECalibration(pulsar_msmt.PulsarMeasurement):
    """
    This is a CORPSE calibration for sweeping the amplitude and effective rotation angle
    It can thus be used for any CORPSE pulse (e.g. pi/2, 109.5 degrees etc).
    """
    mprefix = 'CORPSECalibration'

    def __init__(self, name, **kw):
        pulsar_msmt.PulsarMeasurement.__init__(self, name)

        self.params['IQmod'] = kw.pop('IQmod', True)


    def generate_sequence(self, upload=True):
        # electron manipulation pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 10e-9, amplitude = 0)

        if self.params['IQmod'] :
            CORPSE = pulselib.IQ_CORPSE_pulse('CORPSE pi-pulse',
            I_channel = 'MW_Imod', 
            Q_channel = 'MW_Qmod',    
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            amplitude = self.params['CORPSE_pi_amp'],
            frequency = self.params['frq_mod'],
            rabi_frequency = self.params['CORPSE_rabi_frequency'],
            pulse_delay = self.params['CORPSE_pulse_delay'],
            eff_rotation_angle = self.params['CORPSE_eff_rotation_angle'])  
        else :
            CORPSE = pulselib.MW_CORPSE_pulse('CORPSE pi-pulse',
            MW_channel = 'MW_Imod', 
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            amplitude = self.params['CORPSE_pi_amp'],
            rabi_frequency = self.params['CORPSE_rabi_frequency'],
            pulse_delay = self.params['CORPSE_pulse_delay'],
            eff_rotation_angle = self.params['CORPSE_eff_rotation_angle'])



        wait_1us = element.Element('1us_delay', pulsar=qt.pulsar)
        wait_1us.append(pulse.cp(T, length=1e-6))

        sync_elt = element.Element('adwin_sync', pulsar=qt.pulsar)
        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = 10e-6, amplitude = 2)
        sync_elt.append(adwin_sync)

        elts = []
        for i in range(self.params['pts']):
            e = element.Element('CORPSE-{}'.format(i), pulsar=qt.pulsar)
            e.append(T,
                pulse.cp(CORPSE,
                    amplitude=self.params['CORPSE_pi_sweep_amps'][i],
                    pulse_delay=self.params['CORPSE_pulse_delays'][i]
                    ))
            elts.append(e)

        # sequence
        seq = pulsar.Sequence('CORPSE pi calibration')
        for i,e in enumerate(elts):           
            for j in range(self.params['multiplicity']):
                seq.append(name = e.name+'-{}'.format(j), 
                    wfname = e.name,
                    trigger_wait = (j==0))
                seq.append(name = 'wait-{}-{}'.format(i,j), 
                    wfname = wait_1us.name, 
                    repetitions = self.params['delay_reps'])
            seq.append(name='sync-{}'.format(i),
                 wfname = sync_elt.name)

        # program AWG
        if upload:
            #qt.pulsar.upload(sync_elt, wait_1us, *elts)
            qt.pulsar.program_awg(seq, sync_elt, wait_1us, *elts )
        #qt.pulsar.program_sequence(seq)


class CORPSEPi2Calibration(pulsar_msmt.PulsarMeasurement):
    """
    Do a pi/2 pulse, followed by a pi-pulse; sweep the time between them.
    """
    mprefix = 'CORPSEPi2Calibration'

    def __init__(self, name, **kw):
        pulsar_msmt.PulsarMeasurement.__init__(self, name)

        self.params['IQmod'] = kw.pop('IQmod', True)



    def generate_sequence(self, upload=True):
        # electron manipulation pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 100e-9, amplitude = 0)
        TIQ = pulse.SquarePulse(channel='MW_Imod',
            length = 10e-9, amplitude = 0)

        if self.params['IQmod'] :
            CORPSE_pi = pulselib.IQ_CORPSE_pulse('CORPSE pi-pulse',
                I_channel = 'MW_Imod', 
                Q_channel = 'MW_Qmod',    
                PM_channel = 'MW_pulsemod',
                PM_risetime = self.params['MW_pulse_mod_risetime'],
                frequency = self.params['frq_mod'],
                rabi_frequency = self.params['CORPSE_rabi_frequency'],
                amplitude = self.params['CORPSE_pi_amp'],
                pulse_delay = 2e-9,
                eff_rotation_angle = 180)

            CORPSE_pi2 = pulselib.IQ_CORPSE_pulse('CORPSE pi/2-pulse',
                I_channel = 'MW_Imod', 
                Q_channel = 'MW_Qmod',    
                PM_channel = 'MW_pulsemod',
                PM_risetime = self.params['MW_pulse_mod_risetime'],
                frequency = self.params['frq_mod'],
                rabi_frequency = self.params['CORPSE_rabi_frequency'],
                amplitude = self.params['CORPSE_pi2_amp'],
                pulse_delay = 2e-9,
                eff_rotation_angle = 90)

        else : 
            CORPSE_pi = pulselib.MW_CORPSE_pulse('CORPSE pi-pulse',
                MW_channel = self.params['cur_MW_channel'],     
                PM_channel = 'MW_pulsemod',
                PM_risetime = self.params['MW_pulse_mod_risetime'],
                rabi_frequency = self.params['CORPSE_rabi_frequency'],
                amplitude = self.params['CORPSE_pi_amp'],
                pulse_delay = 2e-9,
                eff_rotation_angle = 180)

            CORPSE_pi2 = pulselib.MW_CORPSE_pulse('CORPSE pi/2-pulse',
                MW_channel = self.params['cur_MW_channel'],    
                PM_channel = 'MW_pulsemod',
                PM_risetime = self.params['MW_pulse_mod_risetime'],
                rabi_frequency = self.params['CORPSE_rabi_frequency'],
                amplitude = self.params['CORPSE_pi2_amp'],
                pulse_delay = 2e-9,
                eff_rotation_angle = 90)

        wait_1us = element.Element('1us_delay', pulsar=qt.pulsar)
        wait_1us.append(pulse.cp(T, length=1e-6))

        sync_elt = element.Element('adwin_sync', pulsar=qt.pulsar)
        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = 10e-6, amplitude = 2)
        sync_elt.append(adwin_sync)

        elts = []
        seq = pulsar.Sequence('CORPSE Pi2 Calibration')

        for i in range(self.params['pts_awg']):
            e = element.Element('CORPSE_Pi2_Pi-{}'.format(i), 
                pulsar = qt.pulsar,
                global_time=True)
            e.append(T)
            e.append(pulse.cp(CORPSE_pi2, amplitude = self.params['CORPSE_pi2_sweep_amps'][i]))
            e.append(pulse.cp(TIQ, length=2e-9))
            e.append(pulse.cp(CORPSE_pi))
            e.append(T)
            elts.append(e)
            seq.append(name='CORPSE_Pi2_Pi-{}'.format(i),
                wfname = e.name,
                trigger_wait=True)
            seq.append(name='synca-{}'.format(i),
                wfname = sync_elt.name)
            
            e = element.Element('CORPSE_Pi2-{}'.format(i), 
                pulsar = qt.pulsar,
                global_time=True)
            e.append(T)
            e.append(pulse.cp(CORPSE_pi2, amplitude = self.params['CORPSE_pi2_sweep_amps'][i]))
            e.append(pulse.cp(TIQ, length=2e-9))
            e.append(T)
            elts.append(e)
            seq.append(name='CORPSE_Pi2-{}'.format(i),
                wfname = e.name,
                trigger_wait=True)
            seq.append(name='syncb-{}'.format(i),
                wfname = sync_elt.name)

        # program AWG
        if upload:
            #qt.pulsar.upload(sync_elt, wait_1us, *elts)
            qt.pulsar.program_awg(seq, sync_elt, wait_1us, *elts )
        #qt.pulsar.program_sequence(seq)


class DarkESR_CORPSE(pulsar_msmt.PulsarMeasurement):
    mprefix = 'PulsarDarkESR_CORP'

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
        X = pulselib.IQ_CORPSE_pulse('IQ CORPSE pi-pulse',
            I_channel='MW_Imod', 
            Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            amplitude = self.params['CORPSE_pi_amp'],
            length = self.params['pulse_length'],
            rabi_frequency = self.params['CORPSE_rabi_frequency'],
            pulse_delay = self.params['CORPSE_pulse_delay'],
            eff_rotation_angle = self.params['CORPSE_eff_rotation_angle']) 
 

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
        seq = pulsar.Sequence('DarkESR sequence')
        for e in elements:
            seq.append(name=e.name, wfname=e.name, trigger_wait=True)

        # upload the waveforms to the AWG
        if upload:
            #qt.pulsar.upload(*elements)
            qt.pulsar.program_awg(seq,*elements)


class ElectronRamsey(pulsar_msmt.PulsarMeasurement):
    mprefix = 'ElectronRamsey'

    def autoconfig(self):
        self.params['sequence_wait_time'] = \
            int(np.ceil(np.max(self.params['evolution_times'])*1e6)+10)


        pulsar_msmt.PulsarMeasurement.autoconfig(self)

    def generate_sequence(self, upload=True):

        # define the necessary pulses
        if self.params['IQmod'] :
            if self.params['Corpse']:
                X = pulselib.IQ_CORPSE_pulse('CORPSE pi/2-pulse',
                    I_channel = 'MW_Imod', 
                    Q_channel = 'MW_Qmod',    
                    PM_channel = 'MW_pulsemod',
                    PM_risetime = self.params['MW_pulse_mod_risetime'],
                    frequency = self.params['mod_frq'],
                    rabi_frequency = self.params['CORPSE_rabi_frequency'],
                    #amplitude = self.params['CORPSE_pi2_amp'],
                    pulse_delay = 2e-9,
                    eff_rotation_angle = 90)
            else : 
                X = pulselib.MW_IQmod_pulse('pi/2-pulse',
                    I_channel='MW_Imod',
                    Q_channel='MW_Qmod',
                    PM_channel='MW_pulsemod',
                    frequency = self.params['mod_frq'],
                    PM_risetime = self.params['MW_pulse_mod_risetime'])


        else : 
            if self.params['Corpse']:
                X = pulselib.MW_CORPSE_pulse('CORPSE pi/2-pulse',
                    MW_channel = 'MW_Imod',    
                    PM_channel = 'MW_pulsemod',
                    PM_risetime = self.params['MW_pulse_mod_risetime'],
                    rabi_frequency = self.params['CORPSE_rabi_frequency'],
                    #amplitude = self.params['CORPSE_pi_amp'],
                    pulse_delay = 2e-9,
                    eff_rotation_angle = 90)
            else :
                X = pulselib.MW_pulse('pi/2-pulse',
                    MW_channel='MW_Imod',
                    PM_channel='MW_pulsemod',
                    PM_risetime = self.params['MW_pulse_mod_risetime'])

        T = pulse.SquarePulse(channel='MW_Imod', name='delay',
            length = 200e-9, amplitude = 0.)

        # make the elements - one for each ssb frequency
        elements = []
        for i in range(self.params['pts']):

            e = element.Element('ElectronRamsey_pt-%d' % i, pulsar=qt.pulsar,
                global_time = True)
            e.append(T)

            e.append(pulse.cp(X,
                amplitude = self.params['pi2_amps'][i],
                phase = self.params['pi2_phases1'][i]))

            e.append(pulse.cp(T,
                length = self.params['evolution_times'][i]))

            e.append(pulse.cp(X,
                amplitude = self.params['pi2_amps'][i],
                phase = self.params['pi2_phases2'][i]))

            elements.append(e)
        return_e=e
        # create a sequence from the pulses
        seq = pulsar.Sequence('ElectronRamsey sequence')
        for e in elements:
            seq.append(name=e.name, wfname=e.name, trigger_wait=True)


        qt.pulsar.program_awg(seq,*elements)




class DD_CORPSE_ZerothRevival(pulsar_msmt.PulsarMeasurement):
    """
    Class to implement dynamical decoupling sequence and look at the first revival. 
    """
    mprefix = 'DD_CORPSE'

    def autoconfig(self):
        self.params['sequence_wait_time'] = \
            int(np.ceil(np.max(self.params['evolution_times']*2*self.params['number_pulses'])*1e6)+10)

        pulsar_msmt.PulsarMeasurement.autoconfig(self)

    def generate_sequence(self, upload=True):

        # define the necessary pulses
        if self.params['IQmod'] :
            pulse_pi2 = pulselib.IQ_CORPSE_pulse('CORPSE pi/2-pulse',
                I_channel = 'MW_Imod', 
                Q_channel = 'MW_Qmod',    
                PM_channel = 'MW_pulsemod',
                PM_risetime = self.params['MW_pulse_mod_risetime'],
                frequency = self.params['frq_mod'],
                rabi_frequency = self.params['CORPSE_rabi_frequency'],
                amplitude = self.params['CORPSE_pi2_amp'],
                pulse_delay = 2e-9,
                eff_rotation_angle = 90)

            pulse_pi = pulselib.IQ_CORPSE_pulse('CORPSE pi/2-pulse',
                I_channel = 'MW_Imod', 
                Q_channel = 'MW_Qmod',    
                PM_channel = 'MW_pulsemod',
                PM_risetime = self.params['MW_pulse_mod_risetime'],
                frequency = self.params['frq_mod'],
                rabi_frequency = self.params['CORPSE_rabi_frequency'],
                amplitude = self.params['CORPSE_pi_amp'],
                pulse_delay = 2e-9,
                eff_rotation_angle = 180)

        else : 
            pulse_pi2 = pulselib.MW_CORPSE_pulse('CORPSE pi/2-pulse',
                MW_channel = self.params['cur_MW_channel'],    
                PM_channel = 'MW_pulsemod',
                PM_risetime = self.params['MW_pulse_mod_risetime'],
                rabi_frequency = self.params['CORPSE_rabi_frequency'],
                amplitude = self.params['CORPSE_pi2_amp'],
                pulse_delay = 2e-9,
                eff_rotation_angle = 90)

            pulse_pi = pulselib.MW_CORPSE_pulse('CORPSE pi/2-pulse',
                MW_channel = self.params['cur_MW_channel'],    
                PM_channel = 'MW_pulsemod',
                PM_risetime = self.params['MW_pulse_mod_risetime'],
                rabi_frequency = self.params['CORPSE_rabi_frequency'],
                amplitude = self.params['CORPSE_pi_amp'],
                pulse_delay = 2e-9,
                eff_rotation_angle = 180)



        T = pulse.SquarePulse(channel='MW_Imod', name='delay',
            length = 200e-9, amplitude = 0.)

        # make the elements - one for each ssb frequency
        elements = []
        for i in range(self.params['pts']):

            e = element.Element('DD_ZerothRevival_pt-%d' % i, pulsar=qt.pulsar,
                global_time = True)
            e.append(T)

            last = e.add(pulse.cp(pulse_pi2,
                        amplitude = self.params['CORPSE_pi2_amps'][i],
                        phase = self.params['CORPSE_pi2_phases1'][i]),
                    start = 200e-9,
                    name = 'pi2_1')

            #!!!!! careful, this pulse has only been added to test
            last = e.add(pulse.cp(pulse_pi,
                        amplitude = self.params['CORPSE_pi_amp']),
                    refpulse = last,
                    refpoint = 'start',
                    refpoint_new = 'start',
                    start = self.params['MW_1_separation'][i],
                    name = 'pi pulse')

                
            for j in range(self.params['number_pulses']):


                last = e.add(pulse.cp(pulse_pi,
                        amplitude = self.params['CORPSE_pi_amps'][i],
                        phase = self.params['CORPSE_pi_phases'][j]),
                    refpulse = last,
                    refpoint = 'end' if (j == 0) else 'center',
                    refpoint_new = 'center',
                    start = self.params['evolution_times'][i] + self.params['MW_1_separation'][i] - 243e-9 if (j == 0) else 2*self.params['evolution_times'][i],
                    name = 'pi_{}'.format(j))


            e.add(pulse.cp(pulse_pi2,
                    amplitude = self.params['CORPSE_pi2_amps'][i],
                    phase = self.params['CORPSE_pi2_phases2'][j]),
                refpulse = last,
                refpoint = 'center',
                refpoint_new = 'start',
                start = self.params['evolution_times'][i]+self.params['extra_wait_final_pi2'][i],
                name = 'pi2_2')
            
            elements.append(e)
        
        return_e=e
        # create a sequence from the pulses
        seq = pulsar.Sequence('DD_ZerothRevival sequence')
        for e in elements:
            seq.append(name=e.name, wfname=e.name, trigger_wait=True)

    
        qt.pulsar.program_awg(seq,*elements)


class DD_ZerothRevival(pulsar_msmt.PulsarMeasurement):
    """
    Class to implement dynamical decoupling sequence and look at the first revival. 
    """
    mprefix = 'DD'

    def autoconfig(self):
        self.params['sequence_wait_time'] = \
            int(np.ceil(np.max(self.params['evolution_times']*2*self.params['number_pulses'])*1e6)+10)

        pulsar_msmt.PulsarMeasurement.autoconfig(self)

    def generate_sequence(self, upload=True):

        # define the necessary pulses
        if self.params['IQmod'] :
            pulse_pi2 = pulselib.MW_IQ_pulse('Normal IQ pi/2-pulse',
                I_channel = 'MW_Imod', 
                Q_channel = 'MW_Qmod',    
                PM_channel = 'MW_pulsemod',
                PM_risetime = self.params['MW_pulse_mod_risetime'],
                frequency = self.params['frq_mod'],
                length = self.params['pulse_pi2_duration'],
                amplitude = self.params['pulse_pi2_amp'])

            pulse_pi = pulselib.MW_IQ_pulse('Normal IQ pi-pulse',
                I_channel = 'MW_Imod', 
                Q_channel = 'MW_Qmod',    
                PM_channel = 'MW_pulsemod',
                PM_risetime = self.params['MW_pulse_mod_risetime'],
                frequency = self.params['frq_mod'],
                length = self.params['pulse_pi_duration'],
                amplitude = self.params['pulse_pi_amp'])

        else : 
            pulse_pi2 = pulselib.MW_pulse('Normal pi/2-pulse',
                MW_channel = 'MW_Imod',     
                PM_channel = 'MW_pulsemod',
                PM_risetime = self.params['MW_pulse_mod_risetime'],
                length = self.params['pulse_pi2_duration'],
                amplitude = self.params['pulse_pi2_amp'])

            pulse_pi = pulselib.MW_pulse('Normal pi-pulse',
                MW_channel = 'MW_Imod',   
                PM_channel = 'MW_pulsemod',
                PM_risetime = self.params['MW_pulse_mod_risetime'],
                length = self.params['pulse_pi_duration'],
                amplitude = self.params['pulse_pi_amp'])



        T = pulse.SquarePulse(channel='MW_Imod', name='delay',
            length = 200e-9, amplitude = 0.)

        # make the elements - one for each ssb frequency
        elements = []
        for i in range(self.params['pts']):

            e = element.Element('DD_ZerothRevival_pt-%d' % i, pulsar=qt.pulsar,
                global_time = True)
            e.append(T)

            last = e.add(pulse.cp(pulse_pi2,
                amplitude = self.params['pulse_pi2_amps'][i]),
                start = 200e-9,
                name = 'pi2_1')
                #phase = self.params['pulse_pi2_phases1'][i]))

            for j in range(self.params['number_pulses']):

                #.append(pulse.cp(T,
                #    length = self.params['evolution_times'][i]))
                

                last = e.add(pulse.cp(pulse_pi,
                    amplitude = self.params['pulse_pi_amps'][i]),
                    refpulse = last,
                    refpoint = 'end' if (j == 0) else 'center',
                    refpoint_new = 'center',
                    start = self.params['evolution_times'][i] if (j == 0) else 2*self.params['evolution_times'][i],
                    name = 'pi_{}'.format(j))
                    #phase = self.params['pulse_pi_phases'][j]))

                #e.append(pulse.cp(T,
                #    length = self.params['evolution_times'][i]))

            e.add(pulse.cp(pulse_pi2,
                amplitude = self.params['pulse_pi2_amps'][i]),
                refpulse = last,
                refpoint = 'center',
                refpoint_new = 'start',
                start = self.params['evolution_times'][i],
                name = 'pi2_2')
                #phase = self.params['pulse_pi2_phases2'][i]))


            elements.append(e)
        
        return_e=e
        # create a sequence from the pulses
        seq = pulsar.Sequence('DD sequence')
        for e in elements:
            seq.append(name=e.name, wfname=e.name, trigger_wait=True)

    
        qt.pulsar.program_awg(seq,*elements)


### called at stage 2.0
def rabi(name, IQmod=True):

    if IQmod :
        m = pulsar_msmt.ElectronRabi(name)
    else :
        m = pulsar_msmt.ElectronRabi_Square(name)
    funcs.prepare(m)


    m.params['pts'] = 21
    pts = m.params['pts']
    m.params['repetitions'] = 1000


    m.params['Ex_SP_amplitude']=0

    if IQmod :
        m.params['MW_pulse_frequency'] = 43e6
        m.params['mw_frq'] = m.params['ms-1_cntr_frq']-m.params['MW_pulse_frequency'] 
    else :
        m.params['mw_frq'] = m.params['ms-1_cntr_frq'] 
        print IQmod
    print m.params['ms-1_cntr_frq'] 

    #m.params['MW_pulse_durations'] =  np.ones(pts)*200e-9 #np.linspace(0, 10, pts) * 1e-6
    m.params['MW_pulse_durations'] =  np.linspace(0, 50, pts) * 1e-9

    m.params['MW_pulse_amplitudes'] = np.ones(pts)*0.9
    #m.params['MW_pulse_amplitudes'] = np.linspace(0.0,0.2,pts)#0.55*np.ones(pts)

    # for autoanalysis
    m.params['sweep_name'] = 'Pulse durations (ns)'
    #m.params['sweep_name'] = 'MW_pulse_amplitudes (V)'

    #m.params['sweep_pts'] = m.params['MW_pulse_amplitudes']
    m.params['sweep_pts'] = m.params['MW_pulse_durations']*1e9
    print m.params['sweep_pts']


    funcs.finish(m, upload=True, debug=False)


    print "\nAnalysis suggestion : execfile(r'D:\measuring\\analysis\scripts\espin\electron_rabi_analysis.py')"


### called at stage 2.5
def dark_esr(name):
    '''
    dark ESR on the 0 <-> -1 transition. This function uses IQ mod pulses.
    '''

    m = pulsar_msmt.DarkESR(name)
    funcs.prepare(m)

    m.params['ssmod_detuning'] = 43e6
    m.params['mw_frq']       = m.params['ms-1_cntr_frq'] - m.params['ssmod_detuning'] #MW source frequency, detuned from the target
    m.params['repetitions']  = 1000
    m.params['range']        = 6e6
    m.params['pts'] = 131
    m.params['pulse_length'] = 1.78e-6
    m.params['ssbmod_amplitude'] = 0.008
    
    m.params['Ex_SP_amplitude']=0


    m.params['ssbmod_frq_start'] = m.params['ssmod_detuning'] - m.params['range']
    m.params['ssbmod_frq_stop']  = m.params['ssmod_detuning'] + m.params['range']


    funcs.finish(m, upload=True, debug=False)


def dark_esr_Corpse(name):
    '''
    dark ESR CORPSE + IQmod on the 0 <-> -1 transition
    '''

    m = DarkESR_CORPSE(name)
    funcs.prepare(m)


    CORPSE_frq = 4.5e6
    m.params['CORPSE_rabi_frequency'] = CORPSE_frq
    m.params['CORPSE_pi_amp'] = 0.752
    m.params['CORPSE_eff_rotation_angle'] = 180

    m.params['ssmod_detuning'] = 43e6
    m.params['mw_frq']       = m.params['ms-1_cntr_frq'] - m.params['ssmod_detuning'] #MW source frequency, detuned from the target
    m.params['repetitions']  = 1000
    m.params['range']        = 8e6
    m.params['pts'] = 101
    m.params['pulse_length'] = 2.e-6
    m.params['ssbmod_amplitude'] = 0.03
    

    m.params['CORPSE_pulse_delay']=0e-9
    m.params['Ex_SP_amplitude']=0


    m.params['ssbmod_frq_start'] = m.params['ssmod_detuning'] - m.params['range']
    m.params['ssbmod_frq_stop']  = m.params['ssmod_detuning'] + m.params['range']


    funcs.finish(m, upload=True, debug=False)




### called at stage = 3.0 
def calibrate_Pi_CORPSE(name,IQmod=True,multiplicity=1):

    m = CORPSECalibration(name)

    funcs.prepare(m)

    pts = 20
    
    
    m.params['IQmod'] = IQmod
    m.params['multiplicity'] = multiplicity
 
    m.params['Ex_SP_amplitude']=0

    if IQmod :
        m.params['frq_mod'] = 43e6
        CORPSE_frq = 4.5e6
        m.params['mw_frq'] = m.params['ms-1_cntr_frq']-m.params['frq_mod'] 
    else :
        CORPSE_frq = 4.5e6
        m.params['mw_frq'] = m.params['ms-1_cntr_frq'] 
    m.params['CORPSE_rabi_frequency'] = CORPSE_frq

    m.params['pts'] = pts
    m.params['repetitions'] = 1000

    # sweep params
    m.params['CORPSE_pi_sweep_amps'] =  np.linspace(0.0, 0.5, pts) #0.872982*np.ones(pts)#
    m.params['CORPSE_pulse_delays']=0.*np.ones(pts)#np.linspace(0,10e-9,pts)
    m.params['CORPSE_eff_rotation_angle'] = 180
    m.params['delay_reps'] = 1


    # for the autoanalysis
    m.params['sweep_name'] = 'CORPSE amplitude (V)'
    m.params['sweep_pts'] = m.params['CORPSE_pi_sweep_amps']
    m.params['wait_for_AWG_done'] = 1
    
    funcs.finish(m, debug=False)



### called at stage = 4.0 
def calibrate_Pi2_CORPSE(name,IQmod=True):
    
    m = CORPSEPi2Calibration(name)
    
    funcs.prepare(m)

    pts = 21    
    m.params['pts_awg'] = pts
    m.params['repetitions'] = 3000

    # we do actually two msmts for every sweep point, that's why the awg gets only half of the 
    # pts;
    m.params['pts'] = 2*pts 

    

    m.params['IQmod'] = IQmod

    m.params['Ex_SP_amplitude']=0

    if IQmod : 
        CORPSE_frq = 4.5e6
        m.params['frq_mod'] = 43e6
        m.params['mw_frq'] = m.params['ms-1_cntr_frq']-m.params['frq_mod'] 
        m.params['CORPSE_pi_amp'] = 0.750
    else :
        CORPSE_frq = 9e6
        m.params['mw_frq'] = m.params['ms-1_cntr_frq'] 
        m.params['CORPSE_pi_amp'] = 0.713
    print 'IQmod :', IQmod
    m.params['CORPSE_rabi_frequency'] = CORPSE_frq

    # sweep params
    #m.params['CORPSE_pi_amp']=
    m.params['cur_MW_channel'] = 'MW_Imod'


    m.params['wait_for_AWG_done'] = 1


    sweep_axis =  m.params['CORPSE_pi_amp']+linspace(-0.1,0.1,pts)
    m.params['CORPSE_pi2_sweep_amps'] = sweep_axis

    # for the autoanalysis
    m.params['sweep_name'] = 'MW pi/2 amp (V)'
    m.params['sweep_pts'] = np.sort(np.append(sweep_axis,sweep_axis))


    funcs.finish(m, debug=False)


def ramsey_Corpse(name, IQmod=True, Corpse = False) :
    m = ElectronRamsey(name)
    funcs.prepare(m)


    pts = 128
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    print 1/m.params['N_HF_frq']


    m.params['IQmod'] = IQmod
    m.params['Corpse'] = Corpse
    m.params['cur_MW_channel'] = 'MW_Imod'

    m.params['Ex_SP_amplitude']=0

    m.params['detuning']  = 3e3
    if IQmod :
        CORPSE_frq = 4.5e6
        m.params['mod_frq'] = 43e6 
        m.params['mw_frq'] = m.params['ms-1_cntr_frq']-m.params['mod_frq'] -m.params['detuning']
    else :
        CORPSE_frq = 9e6
        m.params['mw_frq'] = m.params['ms-1_cntr_frq'] -m.params['detuning']

    m.params['CORPSE_rabi_frequency'] = CORPSE_frq
    print IQmod


    
    #m.params['evolution_times'] = np.linspace(0,(pts-1)*1/m.params['N_HF_frq'],pts)
    m.params['evolution_times'] = np.linspace(0, 5000e-9,pts)
    #m.params['evolution_times'] = 5*np.ones (pts)*1e-9

    # MW pulses
    m.params['pi2_amps'] = np.ones(pts)*0.35#0.770#m.params['CORPSE_pi2_amp']
    m.params['pi2_phases1'] = np.ones(pts) * 0
    m.params['pi2_phases2'] = 0*np.ones(pts) #* (90.+15) ##np.linspace(0,360,pts) #np.ones(pts) * 0#

    # for the autoanalysis
    m.params['sweep_name'] = 'evolution time (ns)'
    m.params['sweep_pts'] = m.params['evolution_times']/1e-9
    #m.params['sweep_name'] = 'phase second pi2'
    #m.params['sweep_pts'] = m.params['CORPSE_pi2_phases2']

    funcs.finish(m)



def dd_Corpse_zerothrevival(name, IQmod=True) :
    m = DD_CORPSE_ZerothRevival(name)
    funcs.prepare(m)


    pts = 11
    m.params['pts'] = pts
    m.params['repetitions'] = 2000

    m.params['IQmod'] = IQmod
    m.params['cur_MW_channel'] = 'MW_Imod'

    m.params['Ex_SP_amplitude']=0


    if IQmod :
        CORPSE_frq = 4.5e6
        m.params['frq_mod'] = 43e6 
        m.params['mw_frq'] = m.params['ms-1_cntr_frq']-m.params['frq_mod']
        m.params['CORPSE_pi_amps'] = np.ones(pts)*0.750
        m.params['CORPSE_pi2_amps'] = np.ones(pts)*0.833
    else :
        CORPSE_frq = 9e6
        m.params['mw_frq'] = m.params['ms-1_cntr_frq']
        m.params['CORPSE_pi_amps'] = np.ones(pts)*0.713
        m.params['CORPSE_pi2_amps'] = np.ones(pts)*0.77


    m.params['CORPSE_rabi_frequency'] = CORPSE_frq
    m.params['number_pulses'] = 1

    
    if mod(m.params['number_pulses'],2) ==0 :
        m.params['extra_wait_final_pi2']=np.ones(pts)*m.params['extra_wait_final_pi2']
        #m.params['extra_wait_final_pi2'] = np.linspace(-100e-9,60e-9,pts)#np.ones(pts)*0
    else :
        m.params['extra_wait_final_pi2']=np.ones(pts)*0
        #m.params['extra_wait_final_pi2'] = np.linspace(-80e-9,80e-9,pts)

    

    m.params['evolution_times'] = np.linspace(50e-6, 100e-6,pts)/(2.*m.params['number_pulses']) #np.linspace(300e-9*2.*m.params['number_pulses'], 100e-6,pts)/(2.*m.params['number_pulses'])
    #np.linspace((2.2*1/CORPSE_frq)*2*m.params['number_pulses'], 40e-6,pts)/(2.*m.params['number_pulses'])

    # MW pulses
    #m.params['CORPSE_pi2_amps'] = np.ones(pts)*m.params['CORPSE_pi2_amp']#0.752#0.738
    m.params['CORPSE_pi2_phases1'] = np.ones(pts) * 0
    m.params['CORPSE_pi2_phases2'] = 0*np.ones(pts) #* (90.+15) ##np.linspace(0,360,pts) #np.ones(pts) * 0#
    #m.params['CORPSE_pi_amps'] = np.ones(pts)*m.params['CORPSE_pi_amp']#0.752#0.727
    
    m.params['MW_1_separation'] = np.ones(pts)*600e-9#np.linspace(280, 800, pts)*1e-9
    
    m.params['CORPSE_pi_phases'] = np.zeros(m.params['number_pulses'])
    if mod(m.params['number_pulses'],2) == 0 :
        for i in range(m.params['number_pulses']):
            m.params['CORPSE_pi_phases'][i]= 90*0**mod((mod(i,2)+i/4),2)
    else :
        for i in range(m.params['number_pulses']):
            m.params['CORPSE_pi_phases'][i]= 90*0**mod((mod(i+1,2)+(i+1)/4),2)
#
    m.params['first_CORPSE_pi_phase'] = 90
    if m.params['first_CORPSE_pi_phase'] != m.params['CORPSE_pi_phases'][0]:
        m.params['CORPSE_pi_phases'] = abs(m.params['CORPSE_pi_phases']- 90)

    m.params['CORPSE_pi_phases'] = np.ones(m.params['number_pulses'])*0

    print "Phases of the pi pulses : ",  m.params['CORPSE_pi_phases']


    # for the autoanalysis
    m.params['sweep_name'] = 'evolution time (us)' #'MW_1_separation (ns)'
    m.params['sweep_pts'] = m.params['evolution_times']*2*m.params['number_pulses']/1e-6
    #m.params['sweep_name'] = 'extra wait time before pi/2 (ns)'
    #m.params['sweep_pts'] = m.params['extra_wait_final_pi2']*1e9#m.params['evolution_times']*2*m.params['number_pulses']/1e-6
    #m.params['sweep_name'] = 'phase second pi2'
    #m.params['sweep_pts'] = m.params['CORPSE_pi2_phases2']

    funcs.finish(m, debug = False)



def dd_zerothrevival(name, IQmod=True) :
    m = DD_ZerothRevival(name)
    funcs.prepare(m)


    pts = 60
    m.params['pts'] = pts
    m.params['repetitions'] = 2000

    m.params['IQmod'] = IQmod

    m.params['Ex_SP_amplitude']=0


    if IQmod :
        m.params['frq_mod'] = 43e6 
        m.params['mw_frq'] = m.params['ms-1_cntr_frq']-m.params['frq_mod']
        m.params['pulse_pi_amps'] = np.ones(pts)*0.9
        m.params['pulse_pi2_amps'] = np.ones(pts)*0.9
    else :
        m.params['mw_frq'] = m.params['ms-1_cntr_frq']
        m.params['pulse_pi_amps'] = np.ones(pts)*0.6#0.35
        m.params['pulse_pi2_amps'] = np.ones(pts)*0.6#0.35


    m.params['pulse_pi_duration'] = 91e-9
    m.params['pulse_pi2_duration'] = 40e-9
    m.params['pulse_pi_amp'] = 0.35
    m.params['pulse_pi2_amp'] = 0.35


    m.params['number_pulses'] = 2
    

    m.params['evolution_times'] = np.linspace(120e-9, 40e-6,pts)/(2.*m.params['number_pulses'])



    # for the autoanalysis
    m.params['sweep_name'] = 'evolution time (us)'
    m.params['sweep_pts'] = m.params['evolution_times']*2*m.params['number_pulses']/1e-6
    #m.params['sweep_name'] = 'phase second pi2'
    #m.params['sweep_pts'] = m.params['CORPSE_pi2_phases2']

    funcs.finish(m)


### master function
def run_calibrations(stage, IQmod): 


    if stage == 0 :
        print "\nFirst measure the resonance frequency with a continuous ESR : \n \
        execfile(r'D:/measuring/scripts/espin/esr.py') \n \
        Analysis suggestion : execfile(r'D:/measuring/analysis/scripts/espin/simple_esr_fit.py')"

    if stage == 1 :
        print "\nExecute SSRO calibration : execfile(r'D:/measuring/scripts/ssro/ssro_calibration.py')"

    if stage == 2.0 :
        rabi(SAMPLE+'_'+'rabi', IQmod=IQmod)

    if stage == 2.5 :
        print "Starting a dark ESR spectrum"
        dark_esr(SAMPLE_CFG)
        print "Analysis suggestion : execfile(r'D:/measuring/analysis/scripts/espin/dark_esr_analysis.py')"
 
    if stage == 3.0 :
        calibrate_Pi_CORPSE(SAMPLE_CFG, IQmod = IQmod )
    if stage == 3.5 :
        calibrate_Pi_CORPSE(SAMPLE_CFG, IQmod = IQmod, multiplicity = 8)
    if stage == 3.75:
        dark_esr_Corpse(SAMPLE_CFG)

    if stage == 4.0 :
        calibrate_Pi2_CORPSE(SAMPLE_CFG, IQmod = IQmod )

    if stage == 5.0 :
        #!!! change the Ramsey class to allow to choose between normal pulses
        # and CORPSE ones, issue with length of normal pulses
        Corpse = False
        ramsey_Corpse(SAMPLE_CFG, IQmod = IQmod, Corpse = Corpse)


    if stage == 6.0 :
        dd_Corpse_zerothrevival(SAMPLE_CFG, IQmod = IQmod)
    if stage == 6.5 :
        dd_zerothrevival(SAMPLE_CFG, IQmod = IQmod)



if __name__ == '__main__':
    run_calibrations(2.0, IQmod = False)

    """
    stage 0 : continuous ESR
            --> central resonance frequency to put in 'f_msm1_cntr' in qt.exp_params 

    stage 1 : SSRO calibration

    stage 2 : : Rabi oscillations
                --> if CORPSE rabi oscillations for 'CORPSE_rabi_frequency' in qt.exp_params
            CAUTION, a factor 1/2 remains between the definition of the Rabi frequency 
            that is used in the script and a common definition
            (eg. f_Rabi = pi/pi_pulse_duration)
    stage 2.5 : eventually perfom a dark ESR
            --> central resonance frequency to put in 'f_msm1_cntr' in qt.exp_params 

    stage 3.0 : coarse calibration of the pi CORPSE pulse 
    stage 3.5 : fine calibration of the pi CORPSE pulse
    		- with multiplicity != 1
    		--> 'CORPSE_pi_amp' in qt.exp_params

    stage 4.0 : calibration of the pi/2 CORPSE pulse

    stage 5.0 : ramsey 

    stage 6.0 : dynamical decoupling sequence
        + calibrate the 'extra_wait_final_pi2', ie the time between the last pi pulse_pi
        and pi/2 pulse_pi
    """

