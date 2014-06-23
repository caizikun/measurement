"""
Work in progress :)
Anais
"""

# reload all parameters and modules, import classes
from measurement.scripts.espin import espin_funcs as funcs
reload(funcs)






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

        else : 
            CORPSE_pi = pulselib.MW_CORPSE_pulse('CORPSE pi-pulse',
                MW_channel = self.params['cur_MW_channel'],     
                PM_channel = 'MW_pulsemod',
                PM_risetime = self.params['MW_pulse_mod_risetime'],
                rabi_frequency = self.params['CORPSE_rabi_frequency'],
                amplitude = self.params['CORPSE_amp'],
                pulse_delay = 2e-9,
                eff_rotation_angle = 180)

            CORPSE_pi2 = pulselib.MW_CORPSE_pulse('CORPSE pi-pulse',
                MW_channel = self.params['cur_MW_channel'],    
                PM_channel = 'MW_pulsemod',
                PM_risetime = self.params['MW_pulse_mod_risetime'],
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


class ZerothRevival(pulsar_msmt.PulsarMeasurement):
    """
    This class is for measuring on the 'zeroth' revival: without spin echo thus.
    """
    mprefix = 'DynamicalDecoupling'

    def generate_sequence(self, upload=True, **kw):

        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 10e-9, amplitude = 0)
        CORPSE_pi = self.CORPSE_pi
        CORPSE_pi2 = self.CORPSE_pi2

        sync_elt = element.Element('adwin_sync', pulsar=qt.pulsar)
        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = 10e-6, amplitude = 2)
        sync_elt.append(adwin_sync)

        elts = []
        seq = pulsar.Sequence('Zeroth revival sequence')

        for i in range(self.params['pts']):
            e = element.Element('pi2_pi_pi2-{}'.format(i), pulsar= qt.pulsar,
            global_time = True, time_offset = 0.)
            e.append(T)
            e.append(CORPSE_pi2)
            e.append(pulse.cp(T,
                length = self.params['free_evolution_times'][i]))
            e.append(CORPSE_pi)
            e.append(pulse.cp(T,
                length = self.params['free_evolution_times'][i]))
            e.append(pulse.cp(CORPSE_pi2,
                phase = self.params['pi2_phases'][i]))
            e.append(T)

            elts.append(e)

            seq.append(name='pi2_pi_pi2-{}'.format(i),
                wfname = e.name,
                trigger_wait = True )

            seq.append(name='sync-{}'.format(i),
                wfname = sync_elt.name)


        if upload:
            qt.pulsar.upload(sync_elt, *elts)
        qt.pulsar.program_sequence(seq)





### called at stage 2.0
def rabi(name, IQmod=True):

    if IQmod :
        m = pulsar_msmt.ElectronRabi(name)
    else
        m = pulsar_msmt.ElectronRabi_Square(name)

    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])


    m.params['pts'] = 21
    pts = m.params['pts']
    m.params['repetitions'] = 1000


    m.params['Ex_SP_amplitude']=0

    if IQmod :
        m.params['MW_pulse_frequency'] = 43e6
        m.params['mw_frq'] = m.params['ms-1_cntr_frq']-m.params['MW_pulse_frequency'] 
    else
        m.params['mw_frq'] = m.params['ms-1_cntr_frq'] 

    #m.params['MW_pulse_durations'] =  np.ones(pts)*100e-9 #np.linspace(0, 10, pts) * 1e-6
    m.params['MW_pulse_durations'] =  np.linspace(0, 200, pts) * 1e-9

    m.params['MW_pulse_amplitudes'] = np.ones(pts)*0.27
    #m.params['MW_pulse_amplitudes'] = np.linspace(0,0.8,pts)#0.55*np.ones(pts)

    # for autoanalysis
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


### called at stage 2.5
def dark_esr(name):
    '''
    dark ESR on the 0 <-> -1 transition
    '''

    m = pulsar_msmt.DarkESR(name)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])


    m.params['ssmod_detuning'] = 43e6
    m.params['mw_frq']       = m.params['ms-1_cntr_frq'] - m.params['ssmod_detuning'] #MW source frequency, detuned from the target
    m.params['repetitions']  = 2000
    m.params['range']        = 4e6
    m.params['pts'] = 131
    m.params['pulse_length'] = 1.6e-6
    m.params['ssbmod_amplitude'] = 0.05
    
    m.params['Ex_SP_amplitude']=0


    m.params['ssbmod_frq_start'] = m.params['ssmod_detuning'] - m.params['range']
    m.params['ssbmod_frq_stop']  = m.params['ssmod_detuning'] + m.params['range']

    debug=True

    m.autoconfig()
    m.generate_sequence(upload=True)
    m.run(debug=debug)
    m.save()
    m.finish()



### called at stage = 3.0 
def calibrate_Pi_CORPSE(name,IQmod=True,multiplicity=1):

    m = CORPSECalibration(name)

    funcs.prepare(m)

    pts = 21
    CORPSE_frq = 10e6
    m.params['CORPSE_rabi_frequency'] = CORPSE_frq
    m.params['IQmod'] = IQmod
 
    m.params['Ex_SP_amplitude']=0

    if IQmod :
        m.params['MW_pulse_frequency'] = 43e6
        m.params['mw_frq'] = m.params['ms-1_cntr_frq']-m.params['MW_pulse_frequency'] 
    else
        m.params['mw_frq'] = m.params['ms-1_cntr_frq'] 


    m.params['pts'] = pts
    m.params['repetitions'] = 1000

    # sweep params
    m.params['CORPSE_pi_amp']=0.5
    m.params['CORPSE_pi_sweep_amps'] = np.linspace(0.0, 0.9, pts) #0.872982*np.ones(pts)#
    m.params['CORPSE_pulse_delay']=0e-9
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
    
    m = CORPSEPi2Calibration(name, IQmod = IQmod)
    
    funcs.prepare(m)

    pts = 21
    CORPSE_frq = 10e6
    m.params['CORPSE_rabi_frequency'] = CORPSE_frq
    m.params['IQmod'] = IQmod

    m.params['Ex_SP_amplitude']=0

    if IQmod :
        m.params['MW_pulse_frequency'] = 43e6
        m.params['mw_frq'] = m.params['ms-1_cntr_frq']-m.params['MW_pulse_frequency'] 
    else
        m.params['mw_frq'] = m.params['ms-1_cntr_frq'] 


    m.params['pts'] = pts
    m.params['repetitions'] = 1000

    # sweep params
    m.params['CORPSE_pi_amp']=0.5
    m.params['CORPSE_pi2_sweep_amps'] = np.linspace(0.0, 0.9, pts) 
    m.params['cur_MW_channel'] = 'MW_Imod'

    # for the autoanalysis
    m.params['sweep_name'] = 'CORPSE amplitude (V)'
    m.params['sweep_pts'] = m.params['CORPSE_pi2_sweep_amps']
    m.params['wait_for_AWG_done'] = 1
    
    funcs.finish(m, debug=False)



### master function
def run_calibrations(stage): 
    if stage == 0 :
        print "Firstly measure the resonance frequency with a continuous ESR\
         : execfile(r'D:/measuring/scripts/espin/esr.py')"
        print "Analysis suggestion : execfile(r'D:/measuring/analysis/scripts/espin/simple_esr_fit.py')"

    if stage == 1 :
        print "execute SSRO calibration : execfile(r'D:/measuring/scripts/ssro/ssro_calibration.py')"

    if stage == 2.0 :
        rabi(SAMPLE+'_'+'rabi')

    if stage == 2.5 :
        print "Starting a dark ESR spectrum"
        dark_esr(SAMPLE_CFG)
        print "Analysis suggestion : execfile(r'D:/measuring/analysis/scripts/espin/dark_esr_analysis.py')"
 
    if stage == 3.0 :
        calibrate_Pi_CORPSE(SAMPLE, IQmod = False )
    if stage == 3.5 :
        calibrate_Pi_CORPSE(SAMPLE, IQmod = False, multiplicity = 11)

    if stage == 4.0 :
        calibrate_Pi2_CORPSE(SAMPLE, IQmod = False )






if __name__ == '__main__':
    run_calibration(0.0)

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
    """
