"""
Script for AWG ssro calibration.
"""

import numpy as np
import qt
#reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
from measurement.lib.measurement2.adwin_ssro import ssro
import msvcrt
from measurement.lib.measurement2.adwin_ssro import pulsar_pq
from measurement.lib.pulsar import pulse, pulselib, element, pulsar
import bell
reload(bell)
import sequence as bseq
reload(bseq)
import sweep_bell




class Bell_FastSSRO(pulsar_pq.PQPulsarMeasurement):
    # needed ? XXXXXX
    adwin_process = pulsar_pq.PQPulsarMeasurement.adwin_process


    def __init__(self, name):
        pulsar_pq.PQPulsarMeasurement.__init__(self, name)
        self.joint_params = m2.MeasurementParameters('JointParameters')
        self.params = m2.MeasurementParameters('LocalParameters')
        self.params['pts']=1
        self.params['repetitions']=1

    def autoconfig(self, **kw):
        self.params['send_AWG_start'] = 1
        self.params['wait_for_AWG_done'] = 1
        self.params['sequence_wait_time'] = self.joint_params['LDE_attempts_before_CR']*self.joint_params['LDE_element_length']*1e6\
        +self.params['free_precession_time_1st_revival']*1e6*self.joint_params['wait_for_1st_revival']+ 20
        print 'I am the sequence waiting time', self.params['sequence_wait_time']
        pulsar_pq.PQPulsarMeasurement.autoconfig(self, **kw)

        # add values from AWG calibrations
        self.params['SP_voltage_AWG'] = \
                self.A_aom.power_to_voltage(
                        self.params['AWG_SP_power'], controller='sec')
        self.params['RO_voltage_AWG'] = \
                self.AWG_RO_AOM.power_to_voltage(
                        self.params['AWG_RO_power'], controller='sec')
        self.params['yellow_voltage_AWG'] = \
                self.yellow_aom.power_to_voltage(
                        self.params['AWG_yellow_power'], controller='sec')

        self.params['A_SP_voltage_AWG'] = \
                    self.A_aom.power_to_voltage(
                            self.params['A_SP_amplitude_AWG'], controller='sec')
        qt.pulsar.set_channel_opt('AOM_Newfocus', 'high', self.params['A_SP_voltage_AWG'])


        if self.params['LDE_yellow_duration'] > 0.:
            qt.pulsar.set_channel_opt('AOM_Yellow', 'high', self.params['yellow_voltage_AWG'])
        else:
            print self.mprefix, self.name, ': Ignoring yellow'


        self.params['E_SP_voltages_AWG']=np.zeros(self.params['pts']/2)
        self.params['E_RO_voltages_AWG']=np.zeros(self.params['pts']/2)
        
        for i in range(self.params['pts']/2):
            
            self.params['E_SP_voltages_AWG'][i] = \
                    self.AWG_RO_AOM.power_to_voltage(
                            self.params['E_SP_amplitudes_AWG'][i], controller='sec')

            self.params['E_RO_voltages_AWG'][i] = \
                    self.AWG_RO_AOM.power_to_voltage(
                            self.params['E_RO_amplitudes_AWG'][i], controller='sec')

        if qt.pulsar.channels['EOM_AOM_Matisse']['type'] == 'marker' and self.params['pts']>1:
            print 'FastSSRO: WARNING, AOM Matisse is on marker channel, cannot sweep its power!'
            print 'Setting max RO power'
            qt.pulsar.set_channel_opt('EOM_AOM_Matisse', 'high', self.params['E_RO_voltages_AWG'][-1])

    def generate_sequence(self, upload=True):

        SP_A_pulse          =        pulse.SquarePulse(channel = 'AOM_Newfocus', amplitude = 1.0)
        SP_E_pulse          =        pulse.SquarePulse(channel = 'EOM_AOM_Matisse',  amplitude = 1.0)
        RO_pulse            =        pulse.SquarePulse(channel = 'EOM_AOM_Matisse',  amplitude = 1.0)
        T                   =        pulse.SquarePulse(channel = 'AOM_Newfocus', length = self.params['wait_length'], amplitude = 0)
        adwin_trigger_pulse =        pulse.SquarePulse(channel = 'adwin_sync',   length = 5e-6,   amplitude = 2)
        PQ_sync             =        pulse.SquarePulse(channel = 'sync', length = self.params['pq_sync_length'], amplitude = 1.0)
        MW_pi_pulse  =       pulselib.HermitePulse_Envelope('Hermite pi-pulse',
                                        MW_channel='MW_Imod',
                                        PM_channel='MW_pulsemod',
                                        second_MW_channel='MW_Qmod', 
                                        amplitude = self.params['Hermite_pi_amp'],
                                        length = self.params['Hermite_pi_length'],
                                        PM_risetime = self.params['MW_pulse_mod_risetime'],
                                        pi2_pulse = False)


        elements = [] 

        finished_element = element.Element('finished', pulsar = qt.pulsar)
        finished_element.append(adwin_trigger_pulse)
        elements.append(finished_element)

        seq = pulsar.Sequence('Bell_FastSSRO')


        if self.params['setup'] == 'lt4':
            bseq.pulse_defs_lt4(self)
        elif self.params['setup'] == 'lt3':
            bseq.pulse_defs_lt3(self) 



        for i in range(self.params['pts']/2):

            if self.params['do_general_sweep']:
                self.joint_params[self.params['general_sweep_name']] = self.params['general_sweep_pts'][i]

                LDE_element = bseq._LDE_element(self, 
                    name = 'Bell sweep element {}'.format(i))    
                elements.append(LDE_element)

            else :
                LDE_element = bseq._LDE_element(self, 
                    name = 'Bell element {}'.format(i))    
                elements.append(LDE_element)
            
            seq.append(name = 'Bell sweep sequence before ms0 calib {}'.format(i) if self.params['do_general_sweep'] else 'Bell sequence before ms0 calib {}'.format(i),
                    wfname = LDE_element.name,
                    trigger_wait = self.params['trigger_wait'],
                    repetitions = self.joint_params['LDE_attempts_before_CR'])


            e0 =  element.Element('SSRO-ms0-{}'.format(i), pulsar = qt.pulsar)
            e0.append(pulse.cp(T,length=3e-6))
            e0.append(PQ_sync)
            e0.append(T)  
            e0.append(pulse.cp(SP_A_pulse, length=self.params['A_SP_durations_AWG'][i]))
            e0.append(T)
            e0.append(pulse.cp(RO_pulse, length=self.params['E_RO_durations_AWG'][i],
                    amplitude=self.params['E_RO_voltages_AWG'][i]))
            e0.append(T)
            elements.append(e0)

            seq.append(name='SSRO-ms0-{}'.format(i), wfname=e0.name, trigger_wait=False)
            seq.append(name='finished-ms0-{}'.format(i), wfname=finished_element.name, trigger_wait=False)

            seq.append('Bell sweep sequence before ms1 calib {}'.format(i) if self.params['do_general_sweep'] else 'Bell sequence before ms1 calib {}'.format(i),
                wfname = LDE_element.name,
                trigger_wait = self.params['trigger_wait'],
                repetitions = self.joint_params['LDE_attempts_before_CR'])


            e1 =  element.Element('SSRO-ms1-{}'.format(i), pulsar = qt.pulsar)
            e1.append(pulse.cp(T,length=3e-6))
            e1.append(PQ_sync)
            e1.append(T)

            if self.params['init_with_MW'] : #SP on ms=0 transition, then apply a MW pi pulse to transfer population into ms=-1
                e1.append(pulse.cp(SP_A_pulse, length=self.params['A_SP_durations_AWG'][i]))
                e1.append(T)
                e1.append(MW_pi_pulse)
                self.params['E_SP_durations_AWG'][i] = self.params['A_SP_durations_AWG'][i] + self.params['wait_length'] + self.params['Hermite_pi_length']
            else:
                e1.append(pulse.cp(SP_E_pulse, length=self.params['E_SP_durations_AWG'][i], 
                    amplitude=self.params['E_SP_voltages_AWG'][i]))
            

            e1.append(T)
            e1.append(pulse.cp(RO_pulse, length=self.params['E_RO_durations_AWG'][i],
                    amplitude=self.params['E_RO_voltages_AWG'][i]))
            e1.append(T)
            elements.append(e1)

            seq.append(name='SSRO-ms1-{}'.format(i), wfname=e1.name, trigger_wait=False)
            seq.append(name='finished-ms1-{}'.format(i), wfname=finished_element.name, trigger_wait=False)
        


        if upload:
            if upload=='old_method':
                qt.pulsar.upload(*elements)
                qt.pulsar.program_sequence(seq)
            else:
                qt.pulsar.program_awg(seq,*elements)


SAMPLE_CFG = qt.exp_params['protocols']['current']
SAMPLE_NAME =  qt.exp_params['samples']['current']


def _setup_params(msmt, setup):
    msmt.params['setup']=setup
    msmt.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    msmt.params.from_dict(qt.exp_params['protocols']['cr_mod'])

    
    if not(hasattr(msmt,'joint_params')):
        msmt.joint_params = {}
    import joint_params
    reload(joint_params)
    for k in joint_params.joint_params:
        msmt.joint_params[k] = joint_params.joint_params[k]

    if setup == 'lt4' :
        import params_lt4
        reload(params_lt4)
        msmt.AWG_RO_AOM = qt.instruments['PulseAOM']
        for k in params_lt4.params_lt4:
            msmt.params[k] = params_lt4.params_lt4[k]
        msmt.params['MW_BellStateOffset'] = 0.0
        bseq.pulse_defs_lt4(msmt)
    elif setup == 'lt3' :
        import params_lt3
        reload(params_lt3)
        msmt.AWG_RO_AOM = qt.instruments['PulseAOM']
        for k in params_lt3.params_lt3:
            msmt.params[k] = params_lt3.params_lt3[k]
        msmt.params['MW_BellStateOffset'] = 0.0
        bseq.pulse_defs_lt3(msmt)
    else:
        print 'Sweep_bell: invalid setup:', setup

    msmt.params['send_AWG_start'] = 1
    msmt.params['sync_during_LDE'] = 1
    msmt.params['wait_for_AWG_done'] = 0
    msmt.params['trigger_wait'] = 1




def bell_fast_ssro_calibration(name):

    m = Bell_FastSSRO('FastSSROCalib_'+name)
    _setup_params(m, setup = qt.current_setup)



    #m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+PQ'])
    #m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    #m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    #m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    #m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])
    #m.params.from_dict(qt.exp_params['samples'][SAMPLE_NAME])

    pts = 10
    m.params['pts'] = 2*pts
    m.params['repetitions'] = 3000

    m.params['sync_during_LDE'] = 0
    m.params['wait_length']    = 1000e-9
    m.params['pq_sync_length']    = 150e-9
    m.params['init_with_MW']  = False
    m.params['mw_frq'] = m.params['ms-1_cntr_frq']

    m.params['do_general_sweep']= 1
    if m.params['do_general_sweep'] :
        m.params['general_sweep_name'] = 'LDE_attempts_before_CR'
        m.params['general_sweep_pts'] = np.array(np.linspace(1,250,pts),dtype=np.int32)
        m.params['sweep_name'] = m.params['general_sweep_name'] 
        m.params['sweep_pts'] = m.params['general_sweep_pts']
        print m.params['sweep_pts']
        m.params['E_RO_amplitudes_AWG']    =   np.ones(pts)*m.params['AWG_RO_power'] 
    else :
        m.params['E_RO_amplitudes_AWG']    =   np.linspace(0,3,pts)*m.params['Ex_RO_amplitude']
        m.params['sweep_name'] = 'Readout power [nW]'
        m.params['sweep_pts'] = m.params['E_RO_amplitudes_AWG']*1e9


    m.params['E_RO_durations_AWG']    =    np.ones(pts)*10e-6
    m.params['E_SP_amplitudes_AWG']    =    np.ones(pts)*m.params['Ex_SP_amplitude']
    m.params['A_SP_durations_AWG']    =    np.ones(pts)*5e-6  # after, check with 5 us
    m.params['E_SP_durations_AWG']    =    np.ones(pts)*50*1e-6
    m.params['A_SP_amplitude_AWG']    =    m.params['A_SP_amplitude']

    
    m.params['SP_duration'] = 1
    m.params['A_SP_amplitude'] = 0
    m.params['E_SP_amplitude'] = 0
    m.params['SSRO_duration'] = 1

    debug=False
    measure_bs=False
    upload=True#'old_method'

    
    print 'sequence_wait_time', m.params['sequence_wait_time']

    m.autoconfig()
    m.generate_sequence(upload=upload)
   
    m.setup(mw=m.params['init_with_MW'], debug=debug)
    m.params['MAX_SYNC_BIN'] = (np.max(m.params['E_SP_durations_AWG']) + np.max(m.params['E_RO_durations_AWG']))/(2**m.params['BINSIZE']*m.PQ_ins.get_BaseResolutionPS()*1e-12)
    print m.params['MAX_SYNC_BIN']

    if measure_bs:
        bs_helper = qt.instruments['bs_helper']
        bs_helper.set_script_path(r'D:/measuring/measurement/scripts/bs_scripts/remote_ssro_fast.py')
        bs_helper.set_is_running(True)
        bs_helper.execute_script()
    
    m.run(autoconfig=False, setup=False, debug=debug)    
    m.save()
    
    if measure_bs:
        bs_helper.set_is_running(False)
        m.params['bs_data_path'] = bs_helper.get_data_path()
    
    m.finish()


if __name__ == '__main__':
    bell_fast_ssro_calibration(SAMPLE_CFG)