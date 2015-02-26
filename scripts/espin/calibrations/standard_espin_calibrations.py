"""
Work in progress :)
Anais
"""
import qt
import numpy as np
#reload all parameters and modules
import qt
execfile(qt.reload_current_setup)

# reload all parameters and modules, import classes
from measurement.scripts.espin import espin_funcs as funcs
reload(funcs)


SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def pulse_defs(msmt, IQmod, pulse_type, Imod_channel = True):

    if pulse_type == 'CORPSE' :
        if IQmod : 
            CORPSE_frq = 4.5e6
            msmt.params['CORPSE_rabi_frequency'] = CORPSE_frq
            msmt.params['mw_frq'] = msmt.params['ms-1_cntr_frq']-msmt.params['MW_pulse_mod_frequency'] 
            msmt.params['pulse_pi_amp'] = 0.750
            IQ_CORPSE_pi = pulselib.IQ_CORPSE_pulse('CORPSE pi-pulse',
                    I_channel = 'MW_Imod', 
                    Q_channel = 'MW_Qmod',    
                    PM_channel = 'MW_pulsemod',
                    PM_risetime = msmt.params['MW_pulse_mod_risetime'],
                    frequency = msmt.params['MW_pulse_mod_frequency'],
                    rabi_frequency = msmt.params['CORPSE_rabi_frequency'],
                    amplitude = msmt.params['pulse_pi_amp'],
                    pulse_delay = 2e-9,
                    eff_rotation_angle = 180)
    
            IQ_CORPSE_pi2 = pulselib.IQ_CORPSE_pulse('CORPSE pi/2-pulse',
                    I_channel = 'MW_Imod', 
                    Q_channel = 'MW_Qmod',    
                    PM_channel = 'MW_pulsemod',
                    PM_risetime = msmt.params['MW_pulse_mod_risetime'],
                    frequency = msmt.params['MW_pulse_mod_frequency'],
                    rabi_frequency = msmt.params['CORPSE_rabi_frequency'],
                    amplitude = msmt.params['pulse_pi2_amp'],
                    pulse_delay = 2e-9,
                    eff_rotation_angle = 90)
            pulse_pi = IQ_CORPSE_pi
            pulse_pi2 = IQ_CORPSE_pi2
        else :
            CORPSE_frq = 9e6
            msmt.params['CORPSE_rabi_frequency'] = CORPSE_frq
            msmt.params['mw_frq'] = msmt.params['ms-1_cntr_frq'] 
            msmt.params['pulse_pi_amp'] = msmt.params['CORPSE_pi_amp'] #calib 2014-07-10
            msmt.params['pulse_pi2_amp'] = msmt.params['CORPSE_pi2_amp']
            CORPSE_pi = pulselib.MW_CORPSE_pulse('CORPSE pi-pulse',
                    MW_channel = 'MW_Imod',     
                    PM_channel = 'MW_pulsemod',
                    PM_risetime = msmt.params['MW_pulse_mod_risetime'],
                    rabi_frequency = msmt.params['CORPSE_rabi_frequency'],
                    amplitude = msmt.params['pulse_pi_amp'],
                    pulse_delay = 2e-9,
                    eff_rotation_angle = 180)
    
            CORPSE_pi2 = pulselib.MW_CORPSE_pulse('CORPSE pi/2-pulse',
                    MW_channel = 'MW_Imod',    
                    PM_channel = 'MW_pulsemod',
                    PM_risetime = msmt.params['MW_pulse_mod_risetime'],
                    rabi_frequency = msmt.params['CORPSE_rabi_frequency'],
                    amplitude = msmt.params['pulse_pi2_amp'],
                    pulse_delay = 2e-9,
                    eff_rotation_angle = 90)
            pulse_pi=CORPSE_pi
            pulse_pi2=CORPSE_pi2
        
    elif pulse_type == 'Square':
        msmt.params['MW_pi_duration'] = msmt.params['Square_pi_length']
        msmt.params['MW_pi2_duration'] = msmt.params['Square_pi2_length']
        if IQmod :
            msmt.params['mw_frq'] = msmt.params['ms-1_cntr_frq']-msmt.params['MW_pulse_mod_frequency'] 
            msmt.params['pulse_pi_amp'] = msmt.params['IQ_Square_pi_amp']
            msmt.params['pulse_pi2_amp'] = msmt.params['IQ_Square_pi2_amp']
            IQ_Square_pi = pulselib.MW_IQmod_pulse('Square pi-pulse',
                    I_channel='MW_Imod',
                    Q_channel='MW_Qmod',
                    PM_channel='MW_pulsemod',
                    length = msmt.params['MW_pi_duration'],
                    amplitude = msmt.params['pulse_pi_amp'],
                    frequency = msmt.params['MW_pulse_mod_frequency'],
                    PM_risetime = msmt.params['MW_pulse_mod_risetime'])
            IQ_Square_pi2 = pulselib.MW_IQmod_pulse('Square pi/2-pulse',
                    I_channel='MW_Imod',
                    Q_channel='MW_Qmod',
                    PM_channel='MW_pulsemod',
                    length = msmt.params['MW_pi2_duration'],
                    amplitude = msmt.params['pulse_pi2_amp'],
                    frequency = msmt.params['MW_pulse_mod_frequency'],
                    PM_risetime = msmt.params['MW_pulse_mod_risetime'])
            pulse_pi=IQ_Square_pi
            pulse_pi2=IQ_Square_pi2
        else :
            msmt.params['mw_frq'] = msmt.params['ms-1_cntr_frq'] 
            msmt.params['pulse_pi_amp'] = msmt.params['Square_pi_amp'] # calib. 2014-07-10
            msmt.params['pulse_pi2_amp'] = msmt.params['Square_pi2_amp']
            
            Square_pi = pulselib.MW_pulse('Square pi-pulse',
                    MW_channel='MW_Imod' if Imod_channel else 'MW_Qmod',
                    PM_channel='MW_pulsemod',
                    amplitude = msmt.params['pulse_pi_amp'],
                    length = msmt.params['MW_pi_duration'],
                    PM_risetime = msmt.params['MW_pulse_mod_risetime'])

            Square_pi2 = pulselib.MW_pulse('Square pi/2-pulse',
                    MW_channel='MW_Imod' if Imod_channel else 'MW_Qmod',
                    PM_channel='MW_pulsemod',
                    amplitude = msmt.params['pulse_pi2_amp'],
                    length = msmt.params['MW_pi2_duration'],
                    PM_risetime = msmt.params['MW_pulse_mod_risetime'])               
            pulse_pi=Square_pi
            pulse_pi2=Square_pi2


    elif pulse_type == 'Hermite':
        msmt.params['MW_pi_duration'] = msmt.params['Hermite_pi_length']
        msmt.params['MW_pi2_duration'] = msmt.params['Hermite_pi2_length']
        if IQmod :
            msmt.params['mw_frq'] = msmt.params['ms-1_cntr_frq']-msmt.params['MW_pulse_mod_frequency'] 
            msmt.params['pulse_pi_amp'] = msmt.params['IQ_Hermite_pi_amp']
            msmt.params['pulse_pi2_amp'] = msmt.params['IQ_Hermite_pi2_amp']
            IQ_Hermite_pi = pulselib.HermitePulse_Envelope_IQ('Hermite pi-pulse',
                    I_channel='MW_Imod',
                    Q_channel='MW_Qmod',
                    PM_channel='MW_pulsemod',
                    amplitude = msmt.params['pulse_pi_amp'],
                    length = msmt.params['MW_pi_duration'],
                    frequency = msmt.params['MW_pulse_mod_frequency'],
                    PM_risetime = msmt.params['MW_pulse_mod_risetime'])
            IQ_Hermite_pi2 = pulselib.HermitePulse_Envelope_IQ('Hermite pi/2-pulse',
                    I_channel='MW_Imod',
                    Q_channel='MW_Qmod',
                    PM_channel='MW_pulsemod',
                    amplitude = msmt.params['pulse_pi2_amp'],
                    length = msmt.params['MW_pi_duration'],
                    frequency = msmt.params['MW_pulse_mod_frequency'],
                    PM_risetime = msmt.params['MW_pulse_mod_risetime'])
            pulse_pi=IQ_Hermite_pi
            pulse_pi2=IQ_Hermite_pi2
        else :
            msmt.params['mw_frq'] = msmt.params['ms-1_cntr_frq'] 
            msmt.params['pulse_pi_amp'] = msmt.params['Hermite_pi_amp']
            msmt.params['pulse_pi2_amp'] = msmt.params['Hermite_pi2_amp']
            Hermite_pi = pulselib.HermitePulse_Envelope('Hermite pi-pulse',
                    MW_channel='MW_Imod' if Imod_channel else 'MW_Qmod',
                    PM_channel='MW_pulsemod',
                    amplitude = msmt.params['pulse_pi_amp'],
                    length = msmt.params['MW_pi_duration'],
                    PM_risetime = msmt.params['MW_pulse_mod_risetime'],
                    pi2_pulse = False)

            Hermite_pi2 = pulselib.HermitePulse_Envelope('Hermite pi/2-pulse',
                    MW_channel='MW_Imod' if Imod_channel else 'MW_Qmod',
                    PM_channel='MW_pulsemod',
                    amplitude = msmt.params['pulse_pi2_amp'],
                    length = msmt.params['MW_pi2_duration'],
                    PM_risetime = msmt.params['MW_pulse_mod_risetime'],
                    pi2_pulse = True)
            

            pulse_pi=Hermite_pi
            pulse_pi2=Hermite_pi2
        
    return pulse_pi, pulse_pi2





# currently used in the Bell project, to be removed soon 
class Test_3MW(pulsar_msmt.PulsarMeasurement):
    mprefix = 'Test'

    def autoconfig(self):
        self.params['sequence_wait_time'] = \
            int(np.ceil(np.max(self.params['MW_pulse_durations'])*1e6)+10)


        pulsar_msmt.PulsarMeasurement.autoconfig(self)

    def generate_sequence(self, upload=True):
        #print 'test'
        # define the necessary pulses

        X1 = pulselib.MW_IQmod_pulse('pi-pulse_1',
            I_channel='MW_Imod',
            Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod',
            frequency = self.params['MW_pulse_mod_frequency']-self.params['N_hyperfine_splitting'],
            PM_risetime = self.params['MW_pulse_mod_risetime'])
        X2 = pulselib.MW_IQmod_pulse('pi-pulse_2',
            I_channel='MW_Imod',
            Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod',
            frequency = self.params['MW_pulse_mod_frequency'],
            PM_risetime = self.params['MW_pulse_mod_risetime'])
        X3 = pulselib.MW_IQmod_pulse('pi-pulse_3',
            I_channel='MW_Imod',
            Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod',
            frequency = self.params['MW_pulse_mod_frequency']+self.params['N_hyperfine_splitting'],
            PM_risetime = self.params['MW_pulse_mod_risetime'])

        T = pulse.SquarePulse(channel='MW_Imod', name='delay',
            length = 200e-9, amplitude = 0.)

        on_top = False
        # make the elements - one for each ssb frequency
        elements = []
        for i in range(self.params['pts']):

            e = element.Element('ElectronRabi_pt-%d' % i, pulsar=qt.pulsar)

            ref_p=e.append(T)

            if on_top :
                e.add(pulse.cp(X1,
                        length = self.params['MW_pulse_durations'][i],
                        amplitude = self.params['MW_pulse_amplitudes'][i]),
                        refpulse = ref_p)
                e.add(pulse.cp(X2,
                        length = self.params['MW_pulse_durations'][i],
                        amplitude = self.params['MW_pulse_amplitudes'][i]),
                        refpulse = ref_p)
                e.add(pulse.cp(X3,
                        length = self.params['MW_pulse_durations'][i],
                        amplitude = self.params['MW_pulse_amplitudes'][i]),
                        refpulse = ref_p)
            else :
                e.append(pulse.cp(X1,
                        length = self.params['MW_pulse_durations'][i],
                        amplitude = self.params['MW_pulse_amplitudes'][i]))
                e.append(pulse.cp(T,
                        length = 10e-9))
                e.append(pulse.cp(X2,
                        length = self.params['MW_pulse_durations'][i],
                        amplitude = self.params['MW_pulse_amplitudes'][i]))
                e.append(pulse.cp(T,
                        length = 10e-9))
                e.append(pulse.cp(X3,
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


# currently used in the Bell project, to be removed soon 
class TestLDESequence(pulsar_msmt.PulsarMeasurement):
    """
    Class to implement dynamical decoupling sequence and look at the first revival. 
    """
    mprefix = 'Test_LDE'

    def autoconfig(self):
        self.params['sequence_wait_time'] = \
            int(36)

        pulsar_msmt.PulsarMeasurement.autoconfig(self)

    def generate_sequence(self, upload=True, **kw):

        pulse_pi=kw.get('pulse_pi', None)
        pulse_pi2=kw.get('pulse_pi2', None)

        T = pulse.SquarePulse(channel='MW_Imod', name='delay',
            length = 200e-9, amplitude = 0.)

        # make the elements - one for each ssb frequency
        elements = []
        for i in range(self.params['pts']):

            e = element.Element('LDE_test_pt-%d' % i, pulsar=qt.pulsar,
                global_time = True)
            e.append(T)

            e.add(pulse_pi2,
                start = 200e-9,
                name = 'MW_pi_over_2')
              
            e.add(pulse_pi,
                start = 600e-9,
                refpulse = 'MW_pi_over_2',
                refpoint = 'end', 
                refpoint_new = 'end', 
                name='MW_pi')
    
            
            e.add(pulse.cp(pulse_pi2,
                    amplitude = -self.params['pulse_pi2_amp']), 
                start = 4493e-9,
                refpulse = 'MW_pi_over_2',
                refpoint = 'end', 
                refpoint_new = 'start', 
                name='last_MW_pi_over_2')

            N_p = self.params['number_pulses']
            index_j = np.linspace(N_p-1, - N_p+1, N_p )
            for j in range(self.params['number_pulses']):
                e.add(pulse_pi,  
                    start = -3473e-9/(2.*self.params['number_pulses'])*(2*j+1) \
                        +self.params['free_precession_offsets'][i]*index_j[j]\
                       +self.params['echo_offsets'][i],
                    refpulse = 'last_MW_pi_over_2', 
                    refpoint = 'start', 
                    refpoint_new = 'center',
                    name='MW_echo_pi_{}'.format(j))


            elements.append(e)
        
        # create a sequence from the pulses
        seq = pulsar.Sequence('LDE test with {} pulses'.format(self.params['pulse_type']))
        for e in elements:
            seq.append(name=e.name, wfname=e.name, trigger_wait=True)
        
        if upload:
            #    qt.pulsar.upload(*elements)
            #    qt.pulsar.program_sequence(seq)
            qt.pulsar.program_awg(seq,*elements)






### called at stage 2.0
def rabi(name, IQmod=True, Imod_channel = True, pulse_type = 'Square', debug = False):

    m = pulsar_msmt.GeneralElectronRabi(name)
    funcs.prepare(m)
    pulse, pulse_pi2_not_used = pulse_defs(m,IQmod,pulse_type, Imod_channel )


    m.params['pulse_type'] = pulse_type
    m.params['IQmod'] = IQmod
    m.params['Imod_channel'] = Imod_channel
  


    m.params['pts'] = 21
    pts = m.params['pts']
    m.params['repetitions'] = 2000

    m.params['Ex_SP_amplitude']=0

    sweep_duration = True 
    if sweep_duration:
        m.params['pulse_sweep_durations'] =  np.linspace(0, 100, pts) * 1e-9
        m.params['pulse_sweep_amps'] = np.ones(pts)*0.9
        
         # for autoanalysis
        m.params['sweep_name'] = 'Pulse durations (ns)'
        m.params['sweep_pts'] = m.params['pulse_sweep_durations']*1e9
    else:

        m.params['pulse_sweep_durations'] =  np.ones(pts)*2000e-9 #np.linspace(0, 10, pts) * 1e-6
        m.params['pulse_sweep_amps'] = np.linspace(0.,0.2,pts)#0.55*np.ones(pts)

        # for autoanalysis
        m.params['sweep_name'] = 'MW_pulse_amplitudes (V)'
        m.params['sweep_pts'] = m.params['pulse_sweep_amps']
   
    print m.params['sweep_pts']

    print Imod_channel
    funcs.finish(m, upload=True, debug=debug, pulse_pi=pulse, Imod_channel = Imod_channel)


    print "\nAnalysis suggestion : execfile(r'D:\measuring\\analysis\scripts\espin\electron_rabi_analysis.py')"


### called at stage 2.5
def dark_esr(name, Imod_channel = True, pulse_type = 'Square', debug = False):
    '''
    dark ESR on the 0 <-> -1 transition. 
    This class uses IQ modulation, so set the amplitude for the IQ pi pulse and the length.
    '''

    m = pulsar_msmt.GeneralDarkESR(name)
    funcs.prepare(m)
    pulse_pi, pulse_pi2_not_used = pulse_defs(m,True,pulse_type, Imod_channel )

    m.params['pulse_type'] = pulse_type
    m.params['IQmod'] = True
    m.params['Imod_channel'] = Imod_channel
  

    m.params['repetitions']  = 1000
    m.params['Ex_SP_amplitude']=0

    m.params['range']        = 6e6
    m.params['pts'] = 131

    # Be careful, this class uses IQ modulation, so set the amplitude for the IQ pi pulse.

    m.params['ssbmod_frq_start'] = m.params['MW_pulse_mod_frequency'] - m.params['range']
    m.params['ssbmod_frq_stop']  = m.params['MW_pulse_mod_frequency'] + m.params['range']


    funcs.finish(m, upload=True, debug=False,  pulse_pi=pulse_pi)



### called at stage = 4.0
def calibrate_pi_pulse(name,IQmod=True, Imod_channel = True, pulse_type = 'Square', multiplicity=1, debug=False):

    m = pulsar_msmt.GeneralPiCalibration(name)
    funcs.prepare(m)
    pulse_pi, pulse_pi2_not_used = pulse_defs(m,IQmod,pulse_type, Imod_channel )

    m.params['pulse_type'] = pulse_type
    m.params['IQmod'] = IQmod
    m.params['Imod_channel'] = Imod_channel
    m.params['multiplicity'] = multiplicity

    pts = 11
 
    m.params['Ex_SP_amplitude']=0

    m.params['pts'] = pts
    m.params['repetitions'] = 5000

    # sweep params
    m.params['MW_pulse_amplitudes'] =  m.params['pulse_pi_amp']+np.linspace(-0.1,0.1,pts) 
    #m.params['MW_pulse_amplitudes'] = m.params['pulse_pi_amp']+  np.linspace(-0.05, 0.05, pts) #0.872982*np.ones(pts)#
    m.params['delay_reps'] = 15

    # for the autoanalysis
    m.params['sweep_name'] = 'MW amplitude (V)'
    m.params['sweep_pts'] = m.params['MW_pulse_amplitudes']
    m.params['wait_for_AWG_done'] = 1
    
    funcs.finish(m, debug=debug, pulse_pi=pulse_pi)


def calibrate_pi2_pulse(name,IQmod=True, Imod_channel = True, pulse_type = 'CORPSE', debug=False):
    

    m = pulsar_msmt.GeneralPi2Calibration(name)
    
    funcs.prepare(m)
    pulse_pi, pulse_pi2 = pulse_defs(m,IQmod,pulse_type, Imod_channel )

    m.params['pulse_type'] = pulse_type
    m.params['IQmod'] = IQmod
    m.params['Imod_channel'] = Imod_channel

    pts = 11    
    m.params['pts_awg'] = pts
    m.params['repetitions'] = 5000

    # we do actually two msmts for every sweep point, that's why the awg gets only half of the 
    # pts;
    m.params['pts'] = 2*pts 

    

    m.params['Ex_SP_amplitude']=0


    m.params['wait_for_AWG_done'] = 1

    sweep_axis =  m.params['pulse_pi2_amp']+np.linspace(-0.1,0.1,pts)
    m.params['pulse_pi2_sweep_amps'] = sweep_axis

    # for the autoanalysis
    m.params['sweep_name'] = 'MW pi/2 amp (V)'
    m.params['sweep_pts'] = np.sort(np.append(sweep_axis,sweep_axis))

    
    funcs.finish(m, debug=debug, pulse_pi=pulse_pi, pulse_pi2=pulse_pi2)

### called at stage = 5.5
def calibrate_pi4_pulse(name,IQmod=True, Imod_channel = True, pulse_type = 'Square', multiplicity=1, debug=False):

    m = pulsar_msmt.GeneralPiCalibration(name)
    funcs.prepare(m)
    pulse_pi_not_used, pulse_pi2 = pulse_defs(m,IQmod,pulse_type, Imod_channel )
    pulse_pi4 = pulse.cp(pulse_pi2,
            length = m.params['Hermite_pi4_length'])

    m.params['pulse_type'] = pulse_type
    m.params['IQmod'] = IQmod
    m.params['Imod_channel'] = Imod_channel
    m.params['multiplicity'] = multiplicity

    pts = 20
 
    m.params['Ex_SP_amplitude']=0

    m.params['pts'] = pts
    m.params['repetitions'] = 2000

    # sweep params
    m.params['MW_pulse_amplitudes'] =  np.linspace(0.25, 0.5, pts) #0.872982*np.ones(pts)#
    m.params['delay_reps'] = 1

    # for the autoanalysis
    m.params['sweep_name'] = 'MW amplitude (V)'
    m.params['sweep_pts'] = m.params['MW_pulse_amplitudes']
    m.params['wait_for_AWG_done'] = 1
    
    funcs.finish(m, debug=debug, pulse_pi=pulse_pi4)

def ramsey(name, IQmod=False, Imod_channel = True, pulse_type = 'Square', debug=False) :
    
    m = pulsar_msmt.GeneralElectronRamsey(name)
    funcs.prepare(m)
    pulse_pi_not_used, pulse_pi2= pulse_defs(m,IQmod,pulse_type, Imod_channel  )

    m.params['pulse_type'] = pulse_type
    m.params['IQmod'] = IQmod
    m.params['Imod_channel'] = Imod_channel

    pts = 300
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    m.params['Ex_SP_amplitude']=0
    
    m.params['detuning']  = 3.e6
    m.params['mw_frq'] -=  m.params['detuning'] 
    
    #m.params['evolution_times'] = np.linspace(0,(pts-1)*1/m.params['N_HF_frq'],pts)
    m.params['evolution_times'] = np.linspace(0, 8000e-9,pts)
    #m.params['evolution_times'] = 5*np.ones (pts)*1e-9

    # MW pulses
    m.params['pulse_sweep_pi2_phases1'] = np.ones(pts) * 0
    m.params['pulse_sweep_pi2_phases2'] = 0*np.ones(pts) #* (90.+15) ##np.linspace(0,360,pts) #np.ones(pts) * 0#

    # for the autoanalysis
    m.params['sweep_name'] = 'evolution time (ns)'
    m.params['sweep_pts'] = m.params['evolution_times']/1e-9
    #m.params['sweep_name'] = 'phase second pi2'
    #m.params['sweep_pts'] = m.params['CORPSE_pi2_phases2']

    funcs.finish(m,debug=debug, pulse_pi2=pulse_pi2)


def dd_sequence(name, IQmod=True, Imod_channel = True, pulse_type='CORPSE', debug=False) :
    m = pulsar_msmt.DD_GeneralSequence(name)
    funcs.prepare(m)
    pulse_pi, pulse_pi2 = pulse_defs(m,IQmod,pulse_type, Imod_channel )

    m.params['pulse_type'] = pulse_type
    m.params['IQmod'] = IQmod
    m.params['Imod_channel'] = Imod_channel

    m.params['repetitions'] = 6000
    m.params['Ex_SP_amplitude']=0
    
    #evolution times:
    T2_on_revivals_measurement= False
    if T2_on_revivals_measurement:
        revivals=7
        pts_per_revival=5
        sweep_array = np.array([300e-9])
        for r in range(1,revivals):
            sweep_array=np.append(sweep_array, \
                r*74e-6/2. \
                + np.linspace(-2e-6, 2e-6, pts_per_revival))/2.
        print sweep_array
        pts = len(sweep_array)
        m.params['evolution_times'] = sweep_array
    else:
        pts=31
        
        m.params['number_pulses'] = 1
        if mod(m.params['number_pulses'],2) ==0 :
            m.params['extra_wait_final_pi2']=np.ones(pts)*m.params['extra_wait_final_pi2']
            #m.params['extra_wait_final_pi2'] = np.linspace(-100e-9,60e-9,pts)#np.ones(pts)*0
        else :
            m.params['extra_wait_final_pi2']=np.ones(pts)*0
            #m.params['extra_wait_final_pi2'] = np.linspace(-30e-9,30e-9,pts)
        
        m.params['evolution_times'] = np.linspace(420e-9, 10e-6,pts)/(2.*m.params['number_pulses']) #np.linspace(300e-9*2.*m.params['number_pulses'], 100e-6,pts)/(2.*m.params['number_pulses'])
        
    m.params['pts'] = pts

    # MW pulses
    m.params['pulse_pi2_sweep_amps'] = np.ones(pts)*m.params['pulse_pi2_amp']#0.752#0.738
    m.params['pulse_pi2_sweep_phases1'] = np.ones(pts) * 0
    m.params['pulse_pi2_sweep_phases2'] = 0*np.ones(pts) #* (90.+15) ##np.linspace(0,360,pts) #np.ones(pts) * 0#
    m.params['pulse_pi_sweep_amps'] = np.ones(pts)*m.params['pulse_pi_amp']#0.752#0.727
    

    
    m.params['pulse_pi_sweep_phases'] = np.zeros(m.params['number_pulses'])
    if mod(m.params['number_pulses'],2) == 0 :
        # for even number of pulses, repetition of the unit : XYXYYXYX
        for i in range(m.params['number_pulses']):
            m.params['pulse_pi_sweep_phases'][i]= 90*0**mod((mod(i,2)+i/4),2)
    else :
        # for odd number of pulses, the same but the 1st one is removed
        for i in range(m.params['number_pulses']):
            m.params['pulse_pi_sweep_phases'][i]= 90*0**mod((mod(i+1,2)+(i+1)/4),2)
#
    m.params['first_pi_phase'] = 0
    if m.params['first_pi_phase'] != m.params['pulse_pi_sweep_phases'][0]:
        m.params['pulse_pi_sweep_phases'] = abs(m.params['pulse_pi_sweep_phases']- 90)

    m.params['pulse_pi_sweep_phases'] = np.ones(m.params['number_pulses'])*0

    print "Phases of the pi pulses : ",  m.params['pulse_pi_sweep_phases']


    # for the autoanalysis
    m.params['sweep_name'] = 'evolution time (us)' #'MW_1_separation (ns)'
    m.params['sweep_pts'] = m.params['evolution_times']*2*m.params['number_pulses']/1e-6
    #m.params['sweep_name'] = 'extra wait time before pi/2 (ns)'
    #m.params['sweep_pts'] = m.params['extra_wait_final_pi2']*1e9#m.params['evolution_times']*2*m.params['number_pulses']/1e-6
    #m.params['sweep_name'] = 'phase second pi2'
    #m.params['sweep_pts'] = m.params['CORPSE_pi2_phases2']
    

    funcs.finish(m, debug=debug, pulse_pi=pulse_pi, pulse_pi2=pulse_pi2)


def test_lde_sequence(name, IQmod=False, pulse_type='Hermite', debug=False) :
    m = TestLDESequence(name)
    funcs.prepare(m)
    pulse_pi, pulse_pi2 = pulse_defs(m,IQmod,pulse_type )

    m.params['pulse_type'] = pulse_type
    m.params['IQmod'] = IQmod

    m.params['repetitions'] = 12000
    m.params['Ex_SP_amplitude']=0
    
    pts=1
    
    m.params['number_pulses'] = 2 # the 1st pi pulse is added
    
    
    
    m.params['pts'] = pts

    m.params['free_precession_offsets'] = np.ones(pts)*0.0e-9
    m.params['echo_offsets'] =  np.linspace(-10,10,pts)*1e-9



    # for the autoanalysis
    m.params['sweep_name'] = 'echo offset (ns)' #'MW_1_separation (ns)'
    m.params['sweep_pts'] = m.params['echo_offsets'] 
    #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX(for hannes)
    #m.autoconfig()
    #return m.generate_sequence(upload=False, pulse_pi=pulse_pi, pulse_pi2=pulse_pi2)
    funcs.finish(m, upload=True, debug=debug, pulse_pi=pulse_pi, pulse_pi2=pulse_pi2)



### master function
def run_calibrations(stage, IQmod, Imod_channel, debug = False): 


    if stage == 0 :
        print "\nFirst measure the resonance frequency with a continuous ESR : \n \
        execfile(r'D:/measuring/scripts/espin/esr.py') \n \
        Analysis suggestion : execfile(r'D:/measuring/analysis/scripts/espin/simple_esr_fit.py')"

    if stage == 1 :
        print "\nExecute SSRO calibration : execfile(r'D:/measuring/scripts/ssro/ssro_calibration.py')"

    if stage == 2.0 :
        rabi(SAMPLE+'_'+'rabi', IQmod=IQmod, Imod_channel = Imod_channel, 
                pulse_type = 'Square', debug = debug)

    if stage == 2.5 :
        print "Starting a dark ESR spectrum" # Error in the se
        dark_esr(SAMPLE_CFG, Imod_channel = Imod_channel, pulse_type = 'Square', debug = debug)
        print "Analysis suggestion : execfile(r'D:/measuring/analysis/scripts/espin/dark_esr_analysis.py')"

    if stage == 3.0 :
        calibrate_pi_pulse(SAMPLE_CFG, IQmod = IQmod, Imod_channel = Imod_channel,
                pulse_type = 'Hermite', 
                multiplicity = 5, debug=debug)

    if stage == 4.0:
        calibrate_pi2_pulse(SAMPLE_CFG, IQmod=IQmod,Imod_channel = Imod_channel,
                pulse_type = 'Hermite', debug = debug)
  
    if stage == 4.5:
        calibrate_pi4_pulse(SAMPLE_CFG, IQmod = IQmod, Imod_channel = Imod_channel, 
                pulse_type = 'Hermite', 
                multiplicity = 1, debug=debug)
    if stage == 5.0 :
        ramsey(SAMPLE_CFG, IQmod=IQmod, Imod_channel = Imod_channel,
                pulse_type = 'Square', debug = debug)

    if stage == 6.0 :
        dd_sequence(SAMPLE_CFG, IQmod = IQmod, Imod_channel = Imod_channel, 
                pulse_type='Hermite', debug=debug)

    if stage == 7.0 :
        test_lde_sequence(SAMPLE_CFG, IQmod = IQmod, pulse_type='Hermite', debug=debug)


if __name__ == '__main__':
    run_calibrations(2.0, IQmod =False, Imod_channel=False, debug = False)

    """
    stage 0 : continuous /ESR
            --> central resonance frequency to put in 'f_msm1_cntr' in qt.exp_params 

    stage 1 : SSRO calibration

    stage 2 : : Rabi oscillations
             
    stage 2.5 : eventually perfom a dark ESR
            --> dark esr is always with IQ modulation. 
            --> central resonance frequency to put in 'f_msm1_cntr' in qt.exp_params 

    stage 3.0 : coarse calibration of the pulse 
    stage 3.5 : fine calibration of the pi pulse
    		- with multiplicity != 1
    		--> 'pulse_pi_amp' in qt.exp_params

    stage 4.0 : calibration of the pi/2 pulse

    stage 5.0 : ramsey 

    stage 6.0 : dynamical decoupling sequence
        
    """

