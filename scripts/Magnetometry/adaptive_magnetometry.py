"""
Script for adaptive magnetometry. Uses deterministic N-spin initialization by conditional MW and spin-pumping
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
from measurement.scripts.Magnetometry import pulsar_magnetometry as pulsar_mgnt
reload(pulsar_mgnt)

SAMPLE= qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']
#print SAMPLE_CFG
#print SAMPLE


def rabi (name='', fpga=False):
    '''
    initializes N-spin, then sweeps the duration of the FPGA pulse
    '''

    if fpga:
        n = 'rabi_fpga_pulse_'+name
    else:
        n = 'rabi_awg_pulse_'+name

    m = pulsar_mgnt.AdaptivePhaseEstimation(n)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE]['Magnetometry'])
    m.params.from_dict(qt.exp_params['protocols']['Magnetometry'])


    print 'MW mod frequency:', m.params['MW_modulation_frequency']/1e6, ' MHz'
    m.params['wait_for_AWG_done'] = 1
    m.params['wait_after_RO_pulse_duration']=1#10000
    m.params['Ex_SP_amplitude'] = 0
    m.params['init_repetitions'] = 100

    nr_adptv_steps = 21
    m.params['do_adaptive'] = 0
    m.params['do_phase_calibr'] = 1
    m.params['min_phase'] = 0
    m.params['delta_phase'] = 0 #just to have a label in the ssro data file
    m.params['adptv_steps'] = nr_adptv_steps
    m.params['repetitions'] = 1000
    m.params['MW_only_by_awg'] =  False#variable to do ramsey with only AWG, should be FALSE for rabi msmnts
    m.params['phase_second_pi2'] =  np.zeros(nr_adptv_steps) #variable to do ramsey with only AWG, does nothing for rabi msmnts
    
    if fpga:

        m.params['MW_pulse_mod_frqs'] = np.ones(nr_adptv_steps)*m.params['MW_modulation_frequency']
        m.params['MW_pulse_amps'] = np.zeros(nr_adptv_steps)
        m.params['MW_pulse_durations'] = np.zeros(nr_adptv_steps)#0*np.linspace(0, 300e-9, nr_adptv_steps)#
        m.params['ramsey_time'] = np.zeros(nr_adptv_steps)
        m.params['fpga_mw_duration'] = np.linspace (0e-9, 300e-9, nr_adptv_steps)
        m.params['sweep_pts'] = m.params['fpga_mw_duration']*1e9
        m.params['sweep_name'] = 'fpga pulse duration [ns]'

    else:

        m.params['MW_pulse_mod_frqs'] = np.ones(nr_adptv_steps)*m.params['MW_modulation_frequency']
        m.params['MW_pulse_amps'] = m.params['MW_pi_pulse_amp']*np.ones(nr_adptv_steps)
        m.params['MW_pulse_durations'] = np.linspace(0e-9, 200e-9, nr_adptv_steps)#
        m.params['ramsey_time'] = 0*np.ones(nr_adptv_steps)
        m.params['fpga_mw_duration'] = np.zeros(nr_adptv_steps)
        m.params['sweep_pts'] = m.params['MW_pulse_durations']*1e9
        m.params['sweep_name'] = 'awg pulse duration [ns]'


    m.autoconfig()
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()


def ramsey (name, fix_tau = None, phase = None,test_only_awg=False):
    '''
    initializes N-spin, ramsey experiment, sweeping time or phase of the fpga pulse
    '''
 
    if (fix_tau==None):
        sweep_time = 1
    else:
        sweep_time = 0

    if sweep_time:
        n = 'ramsey_sweep_time_'+name
    else:
        n = 'ramsey_sweep_phase_'+str(fix_tau*1e9)+'ns_'+name
    m = pulsar_mgnt.AdaptivePhaseEstimation(n)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE]['Magnetometry'])
    m.params.from_dict(qt.exp_params['protocols']['Magnetometry'])

    detuning = 0*500e3
    
    print 'MW mod frequency:', m.params['MW_modulation_frequency']/1e6, ' MHz'
    m.params['Ex_SP_amplitude'] = 0
    m.params['wait_for_AWG_done'] = 1
    m.params['wait_after_RO_pulse_duration']=1#10000

    m.params['init_repetitions'] = 100

    nr_adptv_steps = 13
    m.params['do_adaptive'] = 0
    m.params['do_phase_calibr'] = 1
    m.params['min_phase'] = 0
    m.params['adptv_steps'] = nr_adptv_steps
    m.params['repetitions'] = 5000
    
 
    pi2_mw_dur = m.params['AWG_pi2_duration']
    pi2_fpga_dur =m.params['fpga_pi2_duration']

    if sweep_time:

        m.params['MW_pulse_mod_frqs'] = np.ones(nr_adptv_steps)*m.params['MW_modulation_frequency']
        m.params['MW_pulse_amps'] = m.params['MW_pi_pulse_amp']*np.ones(nr_adptv_steps)
        m.params['MW_pulse_durations'] = pi2_mw_dur*np.ones(nr_adptv_steps)
        #m.params['ramsey_time'] = np.linspace(1e-9, 10000e-9, nr_adptv_steps)
        m.params['ramsey_time'] = 1e-9*(2**np.arange(nr_adptv_steps))

        #dt = m.params['ramsey_time'][1] - m.params['ramsey_time'][0]
        det=30.015e6+0e3
        #m.params['phases']=np.linspace(0,dt*(nr_adptv_steps-1)*360*det,nr_adptv_steps)+40+0
        m.params['phases']=np.mod(det*360*m.params['ramsey_time'], 360)+40+90
        m.params['fpga_mw_duration'] = pi2_fpga_dur*np.ones(nr_adptv_steps) 
        
        m.params['MW_only_by_awg'] =  test_only_awg #variable to do ramsey with only AWG
        m.params['phase_second_pi2'] =   m.params['phases']
        m.params['sweep_pts'] = m.params['ramsey_time']*1e9
        m.params['sweep_name'] = 'free evolution time [ns]'
        #m.params['sweep_pts'] = np.arange(nr_adptv_steps)*m.params['delta_phase']
        #m.params['sweep_name'] = 'phase fpga pulse [deg]'

    else:
        m.params['MW_pulse_mod_frqs'] = np.ones(nr_adptv_steps)*m.params['MW_modulation_frequency']
        m.params['MW_pulse_amps'] = m.params['MW_pi_pulse_amp']*np.ones(nr_adptv_steps)
        m.params['MW_pulse_durations'] = pi2_mw_dur*np.ones(nr_adptv_steps)
        m.params['ramsey_time'] = fix_tau*np.ones(nr_adptv_steps)
        m.params['fpga_mw_duration'] = pi2_fpga_dur*np.ones(nr_adptv_steps) 
        
        m.params['phases']=np.linspace(0,360,nr_adptv_steps)

        
        m.params['MW_only_by_awg'] =  test_only_awg #variable to do ramsey with only AWG
        m.params['phase_second_pi2'] =   m.params['phases']
        m.params['sweep_pts'] =  m.params['phases']
        m.params['sweep_name'] = 'phase fpga pulse [deg]'

    m.params['phases']=m.params['phases']*255/360    
    m.autoconfig()
    m.generate_sequence(upload=True)
    adwin.set_adaptive_magnetometry_var(phases=np.array(m.params['phases']).astype(int))
    m.run()
    m.save()
    m.finish()


def adaptive_real_time (name):
    '''
    initializes N-spin, ramsey experiment, sweeping time or phase of the fpga pulse
    '''
    nr_adptv_steps = 4
    n = 'cappellaro_protocol_'+str(nr_adptv_steps)+'steps_'+name
    m = pulsar_mgnt.AdaptivePhaseEstimation(n)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE]['Magnetometry'])
    m.params.from_dict(qt.exp_params['protocols']['Magnetometry'])

    m.params['wait_for_AWG_done'] = 1
    m.params['wait_after_RO_pulse_duration']=1#10000

    m.params['init_repetitions'] = 60

    m.params['do_adaptive'] = 1
    m.params['do_phase_calibr'] = 0
    m.params['min_phase'] = 0
    
    m.params['adptv_steps'] = nr_adptv_steps
    m.params['repetitions'] = 100
    
 
    pi2_mw_dur = m.params['AWG_pi2_duration']
    pi2_fpga_dur = m.params['fpga_pi2_duration']

    m.params['MW_pulse_mod_frqs'] = np.ones(nr_adptv_steps)*m.params['MW_modulation_frequency']
    m.params['MW_pulse_amps'] = m.params['MW_pi_pulse_amp']*np.ones(nr_adptv_steps)
    m.params['MW_pulse_durations'] = pi2_mw_dur*np.ones(nr_adptv_steps)
    m.params['fpga_mw_duration'] = pi2_fpga_dur*np.ones(nr_adptv_steps) 
    m.params['ramsey_time'] = 2**(nr_adptv_steps*np.ones(nr_adptv_steps)-np.arange(nr_adptv_steps))*2e-9
    m.params['sweep_pts'] = np.arange(nr_adptv_steps)
    m.params['sweep_name'] = 'steps'
   
    m.autoconfig()
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()

def test(name):
    m = pulsar_mgnt.AdaptivePhaseEstimation(name)
    nr_adptv_steps=11
    m.params['phases']=np.linspace(0,360,nr_adptv_steps)
    physical_adwin.Set_Data_Long(np.linspace(0,1,11),27,1,3)
    print 'PHASES!!!!! ',physical_adwin.Get_Data_Long(27,1,11)

if __name__ == '__main__':

    #for t in [50e-9, 60e-9, 70e-9, 100e-9, 200e-9, 300e-9, 500e-9, 1000e-9]:
    #    ramsey (name='det+500KHz', tau = t)

    #test('test')
    ramsey (name = 'Ramsey_second_pi2_0degr_det=0khz_optTau', fix_tau = None,test_only_awg=False)
    #rabi (name = 'init=100reps_correctedPi2pi_mod_frq', fpga=True)
    #adaptive_real_time (name='test')

