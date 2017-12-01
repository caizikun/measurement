# reload all parameters and modules, import classes
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
reload(pulsar_msmt)
from measurement.scripts.espin import espin_funcs
reload(espin_funcs)
from measurement.lib.measurement2.adwin_ssro import pulse_select as ps
reload(ps)
from measurement.lib.pulsar import pulselib
reload(pulselib)
execfile(qt.reload_current_setup)
import msvcrt
SAMPLE= qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']


class GeneralPiCalibrationSingleElement(pulsar_msmt.GeneralPiCalibration):

    def generate_sequence(self, upload=True, **kw):
        # electron manipulation pulses
        try:
            length = self.params['wait_time_pulses']
        except:
            length =  15000e-9
            
        T = pulse.SquarePulse(channel='MW_Imod',
            length = length, amplitude = 0)

        # T2 = pulse.SquarePulse(channel='MW_Imod',
        #     length = 15000e-9, amplitude = 0)

        TIQ = pulse.SquarePulse(channel='MW_Imod',
            length = 10e-9, amplitude = 0)

        X=kw.get('pulse_pi', None)

        pulse_pi2=kw.get('pulse_pi2', None)

        if X==None:
            print 'WARNING: No valid X Pulse'
        if pulse_pi2==None:
            print 'WARNING: No valid pi2 Pulse'
        if hasattr(X,'Sw_channel'):
            print 'this is the MW switch channel: ', X.Sw_channel
        else:
            print 'no switch found'
        wait_1us = element.Element('1us_delay', pulsar=qt.pulsar)
        wait_1us.append(pulse.cp(T, length=1e-6))

        sync_elt = element.Element('adwin_sync', pulsar=qt.pulsar)
        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = 10e-6, amplitude = 2)
        sync_elt.append(adwin_sync)
        if type(self.params['multiplicity']) ==int:
            self.params['multiplicity'] = np.ones(self.params['pts'])*self.params['multiplicity']

        elements = []
        for i in range(self.params['pts']):
            e = element.Element('pulse-{}'.format(i), pulsar=qt.pulsar)
            for j in range(int(self.params['multiplicity'][i])):
                e.append(T,
                    pulse.cp(X,
                        amplitude=self.params['MW_pulse_amplitudes'][i]
                        ))
    
            try:
                RO_basis = self.params['RO_basis']
            except:
                RO_basis = None
                e.append(T)
            
            if RO_basis == 'Z':
                e.append(T)
                # e.append(pulse.cp(TIQ, length=100e-9))

            elif RO_basis == '-Z':
                e.append(T,
                    pulse.cp(X,
                        amplitude=self.params['fast_pi_amp']
                        ))
                e.append(pulse.cp(TIQ, length=100e-9))
            elif RO_basis == 'X':
                e.append(T,pulse.cp(pulse_pi2, amplitude = self.params['Hermite_pi2_amp'], phase = 90))
                e.append(pulse.cp(TIQ, length=100e-9))
            elif RO_basis == '-X':
                e.append(T,pulse.cp(pulse_pi2, amplitude = self.params['Hermite_pi2_amp'], phase = 270))
                e.append(pulse.cp(TIQ, length=100e-9))
            elif RO_basis == 'Y':
                e.append(T,pulse.cp(pulse_pi2, amplitude = self.params['Hermite_pi2_amp'], phase = 0))
                e.append(pulse.cp(TIQ, length=100e-9))
            elif RO_basis == '-Y':
                e.append(T,pulse.cp(pulse_pi2, amplitude = self.params['Hermite_pi2_amp'], phase = 180))
                e.append(pulse.cp(TIQ, length=100e-9))              
            
            elements.append(e)

        # sequence
        seq = pulsar.Sequence('{} pi calibration'.format(self.params['pulse_shape']))
        for i,e in enumerate(elements):           
            # for j in range(self.params['multiplicity']):
            seq.append(name = e.name+'-{}'.format(j), 
                wfname = e.name,
                trigger_wait = True)
            if self.params['delay_reps'] != 0:
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


def calibrate_pi_pulse(name, multiplicity=1,RO_basis = 'Z', debug=False, mw2=False, wait_time_pulses=15000e-9, **kw):

    
    m = GeneralPiCalibrationSingleElement(name+str(multiplicity))
    
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    pulse_shape = m.params['pulse_shape']
    pts = 20

    m.params['pts'] = pts
    
    ps.X_pulse(m) #### update the pulse params depending on the chosen pulse shape.

    m.params['repetitions'] = 1600 if multiplicity == 1 else 2000
    rng = 0.15 if multiplicity == 1 else 0.04


    ### comment NK: the previous parameters for MW_duration etc. were not used anywhere in the underlying measurement class.
    ###             therefore, I removed them
    if mw2:
        m.params['MW_pulse_amplitudes'] = m.params['mw2_fast_pi_amp'] + np.linspace(-rng, rng, pts)
    else: 
        m.params['MW_pulse_amplitudes'] = m.params['fast_pi_amp'] + np.linspace(-rng, rng, pts)  
            
    print m.params['MW_pulse_amplitudes'] 
    
    m.params['multiplicity'] = np.ones(pts)*multiplicity
    m.params['wait_time_pulses']=wait_time_pulses
    m.params['RO_basis'] = RO_basis
    m.params['delay_reps'] = 0
    # for the autoanalysis
    m.params['sweep_name'] = 'MW amplitude (V)'
   
    m.params['sweep_pts'] = m.params['MW_pulse_amplitudes']
    m.params['wait_for_AWG_done'] = 1

    m.MW_pi=ps.X_pulse(m)
    m.MW_pi2=ps.Xpi2_pulse(m)

    # m.MW_pi = pulse.cp(ps.mw2_X_pulse(m), phase = 0) if mw2 else pulse.cp(ps.X_pulse(m), phase = 0)
    # m.MW_pi = pulse.cp(ps.mw2_X_pulse(m), phase = 0) if mw2 else pulse.cp(ps.X_pulse(m), phase = 0)
    espin_funcs.finish(m, debug=debug, pulse_pi=m.MW_pi,pulse_pi2=m.MW_pi2)

if __name__ == '__main__':


    # for RO_basis in ['Z','-Z','Y','-Y','X','-X']:
    #     breakst = show_stopper()
    #     if breakst:
    #         break
    #     calibrate_pi_pulse(SAMPLE_CFG + 'Pi'+RO_basis+'0', multiplicity =1,RO_basis = RO_basis, debug = False, mw2=False, wait_time_pulses=15000e-9)
    #     calibrate_pi_pulse(SAMPLE_CFG + 'Pi'+RO_basis, multiplicity =5,RO_basis = RO_basis, debug = False, mw2=False, wait_time_pulses=15000e-9)
    #     calibrate_pi_pulse(SAMPLE_CFG + 'Pi'+RO_basis, multiplicity =11,RO_basis = RO_basis, debug = False, mw2=False, wait_time_pulses=15000e-9)

    

    # calibrate_pi_pulse(SAMPLE_CFG + 'Pi0', multiplicity =1, debug = False, mw2=False, wait_time_pulses=15000e-9)
    # calibrate_pi_pulse(SAMPLE_CFG + 'Pi', multiplicity =3, debug = False, mw2=False,wait_time_pulses=15000e-9)
    # calibrate_pi_pulse(SAMPLE_CFG + 'Pi', multiplicity =5, debug = False, mw2=False,wait_time_pulses=15000e-9)
    # calibrate_pi_pulse(SAMPLE_CFG + 'Pi', multiplicity =7, debug = False, mw2=False,wait_time_pulses=15000e-9)
    # calibrate_pi_pulse(SAMPLE_CFG + 'Pi', multiplicity =11, debug = False, mw2=False,wait_time_pulses=15000e-9)
    # calibrate_theta_pulse(SAMPLE_CFG + 'theta',rng = 0.05)
   