"""
Work in progress :)
Anais
"""
#reload all parameters and modules
import qt

# reload all parameters and modules, import classes
from measurement.scripts.espin import espin_funcs as funcs
reload(funcs)
from measurement.scripts.espin.calibrations import standard_espin_calibrations_v2 as calib
reload(calib)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']



class GeneralPi4Calibration(pulsar_msmt.PulsarMeasurement):
    """
    Do a pi/2 pulse, compare to an element with a pi/4 + pi-pulse + pi/4 echo; sweep the pi4 amplitude.
    generate_sequence needs to be supplied with a pi_pulse and pi2_pulse as kw.
    """
    mprefix = 'GeneralPi4Calibration'

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

        elts = []
        seq = pulsar.Sequence('{} Pi2 Calibration'.format(self.params['pulse_type']))

        for i in range(self.params['pts_awg']):
            e = element.Element('{}_Pi2_Pi-{}'.format(self.params['pulse_type'],i), 
                pulsar = qt.pulsar,
                global_time=True)

            e.append(T)

            last = e.add(pulse.cp(pulse_pi2,
                        length= self.params['pulse_pi4_sweep_durations'][i],
                        amplitude = self.params['pulse_pi4_sweep_amps'][i],
                        phase = self.params['pulse_pi4_sweep_phases'][i]),
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

            elts.append(e)
            seq.append(name='{}_Pi4_Pi_Pi4-{}'.format(self.params['pulse_type'],i),
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
            elts.append(e)
            seq.append(name='{}_Pi2-{}'.format(self.params['pulse_type'],i),
                wfname = e.name,
                trigger_wait=True)
            seq.append(name='syncb-{}'.format(i),
                wfname = sync_elt.name)

        # program AWG
        if upload:
            #qt.pulsar.upload(sync_elt, wait_1us, *elts)
            qt.pulsar.program_awg(seq, sync_elt, wait_1us, *elts )
        #qt.pulsar.program_sequence(seq)

        self.params['sequence_wait_time'] = \
            int(np.ceil(np.max(np.array([e.length() for e in elts])*1e6))+10)


class GeneralPi4Calibration_2(pulsar_msmt.PulsarMeasurement):
    """
    Do a pi/4 pulse, compare to an element with a pi/2 + pi-pulse + pi/4 echo; sweep the pi4 amplitude.
    generate_sequence needs to be supplied with a pi_pulse and pi2_pulse as kw.
    """
    mprefix = 'GeneralPi4Calibration'

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

        elts = []
        seq = pulsar.Sequence('{} Pi2 Calibration'.format(self.params['pulse_type']))

        for i in range(self.params['pts_awg']):
            e = element.Element('{}_Pi2_Pi-{}'.format(self.params['pulse_type'],i), 
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

            elts.append(e)
            seq.append(name='{}_Pi4_Pi_Pi4-{}'.format(self.params['pulse_type'],i),
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
            elts.append(e)
            seq.append(name='{}_Pi2-{}'.format(self.params['pulse_type'],i),
                wfname = e.name,
                trigger_wait=True)
            seq.append(name='syncb-{}'.format(i),
                wfname = sync_elt.name)

        # program AWG
        if upload:
            #qt.pulsar.upload(sync_elt, wait_1us, *elts)
            qt.pulsar.program_awg(seq, sync_elt, wait_1us, *elts )
        #qt.pulsar.program_sequence(seq)

        self.params['sequence_wait_time'] = \
            int(np.ceil(np.max(np.array([e.length() for e in elts])*1e6))+10)



def calibrate_pi4_pulse(name,IQmod=True, pulse_type = 'CORPSE', debug=False):
    

    #m = GeneralPi4Calibration(name)
    m = GeneralPi4Calibration_2(name)
    
    funcs.prepare(m)
    pulse_pi, pulse_pi2 = calib.pulse_defs(m,IQmod,pulse_type )

    m.params['pulse_type'] = pulse_type
    m.params['IQmod'] = IQmod
    
    pts = 11    
    m.params['pts_awg'] = pts
    m.params['repetitions'] = 5000

    # we do actually two msmts for every sweep point, that's why the awg gets only half of the 
    # pts;
    m.params['pts'] = 2*pts 

    
    m.params['Ex_SP_amplitude']=0

    m.params['wait_for_AWG_done'] = 1

    sweep_axis = np.linspace(0.25,0.5,pts)
    m.params['pulse_pi4_sweep_amps'] = sweep_axis

    m.params['pulse_pi4_sweep_durations']=np.ones(pts)*m.params['Hermite_pi4_length']
    m.params['pulse_pi4_sweep_phases'] = np.zeros(pts)
    m.params['evolution_times'] = np.ones(pts)*500e-9
    m.params['extra_wait_final_pi4'] = np.ones(pts)*0.

    # for the autoanalysis
    m.params['sweep_name'] = 'MW pi/4 amp (V)'
    m.params['sweep_pts'] = np.sort(np.append(sweep_axis,sweep_axis))

    
    funcs.finish(m, debug=debug, pulse_pi=pulse_pi, pulse_pi2=pulse_pi2)


if __name__ == '__main__':
    calibrate_pi4_pulse(SAMPLE_CFG, IQmod=False, pulse_type = 'Hermite', debug = False)