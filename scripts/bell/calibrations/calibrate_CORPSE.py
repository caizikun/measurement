import qt
import numpy as np
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
from measurement.lib.pulsar import pulse, pulselib, element, pulsar
reload(pulselib)

from measurement.scripts.espin import espin_funcs as funcs
reload(funcs)


### msmt class
class CORPSECalibration(pulsar_msmt.PulsarMeasurement):
    mprefix = 'CORPSECalibration'

    def generate_sequence(self, upload=True):
        # electron manipulation pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 10e-9, amplitude = 0)

        CORPSE = pulselib.MW_CORPSE_pulse('CORPSE pi-pulse',
        MW_channel = self.params['cur_MW_channel'], 
        PM_channel = 'MW_pulsemod',
        #second_MW_channel = 'MW_Qmod',
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

# class CORPSEPiCalibration

class CORPSEPi2Calibration(pulsar_msmt.PulsarMeasurement):
    """
    Do a pi/2 pulse, followed by a pi-pulse; sweep the time between them.
    """
    mprefix = 'CORPSEPi2Calibration'

    def generate_sequence(self, upload=True):
        # electron manipulation pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 100e-9, amplitude = 0)
        TIQ = pulse.SquarePulse(channel='MW_Imod',
            length = 10e-9, amplitude = 0)

        CORPSE_pi = pulselib.IQ_CORPSE_pulse('CORPSE pi-pulse',
            I_channel = 'MW_Imod', 
            Q_channel = 'MW_Qmod',    
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            frequency = self.params['CORPSE_mod_frq'],
            rabi_frequency = self.params['CORPSE_rabi_frequency'],
            amplitude = self.params['CORPSE_amp'],
            pulse_delay = 2e-9,
            eff_rotation_angle = 180)

        CORPSE_pi2 = pulselib.IQ_CORPSE_pulse('CORPSE pi-pulse',
            I_channel = 'MW_Imod', 
            Q_channel = 'MW_Qmod',    
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            frequency = self.params['CORPSE_mod_frq'],
            rabi_frequency = self.params['CORPSE_rabi_frequency'],
            amplitude = self.params['CORPSE_amp'],
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
            e.append(pulse.cp(TIQ, length=200e-9))
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
            e.append(pulse.cp(TIQ, length=200e-9))
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

class CORPSE_Imod_Calibration(pulsar_msmt.PulsarMeasurement):
    mprefix = 'CORPSE_Imod_Calibration'

    def generate_sequence(self, upload=True):
        # electron manipulation pulses
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 10e-9, amplitude = 0)

        CORPSE = pulselib.IQ_CORPSE_pulse('CORPSE pi-pulse',
        I_channel = self.params['cur_MW_channel'], 
        Q_channel='dummy',
        PM_channel = 'MW_pulsemod',
        #second_MW_channel = 'MW_Qmod',
        PM_risetime = self.params['MW_pulse_mod_risetime'],
        amplitude = self.params['CORPSE_pi_amp'],
        frequency = self.params['frq_mod'],
        rabi_frequency = self.params['CORPSE_rabi_frequency'],
        pulse_delay = self.params['CORPSE_pulse_delay'],
        eff_rotation_angle = self.params['CORPSE_eff_rotation_angle'])
        CORPSE.channels.remove('dummy')


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




def calibrate(name):
    m = CORPSECalibration(name)
    #m = CORPSE_Imod_Calibration(name)
    funcs.prepare(m)

    pts = 21
    CORPSE_frq = 10e6
    m.params['CORPSE_rabi_frequency'] = CORPSE_frq

    m.params['Ex_SP_amplitude']=0
    m.params['frq_mod'] = 0e6
    m.params['mw_frq'] = m.params['ms-1_cntr_frq'] - m.params['frq_mod'] 

    m.params['pts'] = pts
    m.params['repetitions'] = 1000

    # sweep params
    m.params['CORPSE_pi_amp']=0.5
    m.params['CORPSE_pi_sweep_amps'] = np.linspace(0.50, 0.8, pts) #0.872982*np.ones(pts)#
    m.params['CORPSE_pulse_delay']=0e-9
    m.params['CORPSE_pulse_delays']=0.*np.ones(pts)#np.linspace(0,10e-9,pts)
    m.params['CORPSE_eff_rotation_angle'] = 180
    m.params['multiplicity'] = 11
    m.params['delay_reps'] = 1
    m.params['cur_MW_channel'] = 'MW_1'

    # for the autoanalysis
    m.params['sweep_name'] = 'CORPSE amplitude (V)'
    m.params['sweep_pts'] = m.params['CORPSE_pi_sweep_amps']
    m.params['wait_for_AWG_done'] = 1
    
    funcs.finish(m, debug=False)

if __name__ == '__main__':
    #sweep_amplitude('sil4_test')
    calibrate('CORPSE_Calib_180_mult11_n123_121_MW1')
