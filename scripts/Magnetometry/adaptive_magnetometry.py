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
print SAMPLE_CFG
print SAMPLE


def erabi_fpga_pulse (name):
    '''
    initializes N-spin, then sweeps the duration of the FPGA pulse
    '''
    n = 'rabiFPGApulse_'+name
    m = pulsar_mgnt.AdaptivePhaseEstimation(n)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE]['Magnetometry'])
    m.params.from_dict(qt.exp_params['protocols']['Magnetometry'])

    m.params['MW_modulation_frequency'] = 30e6
    m.params['mw_frq'] = m.params['ms+1_cntr_frq']-m.params['MW_modulation_frequency']
    print 'MW mod frequency:', m.params['MW_modulation_frequency']/1e6, ' MHz'
    m.params['Ex_SP_amplitude'] = 0
    m.params['wait_for_AWG_done'] = 1
    m.params['wait_after_RO_pulse_duration']=1#10000

    m.params['init_repetitions'] = 70

    nr_adptv_steps = 12
    m.params['do_adaptive'] = 0
    m.params['do_phase_calibr'] = 1
    m.params['min_phase'] = 0
    m.params['delta_phase'] = 1 #just to have a label in the ssro data file
    m.params['adptv_steps'] = nr_adptv_steps
    m.params['repetitions'] = 1000
    
    rabi_fpga = 1

    if rabi_fpga:

        m.params['MW_pulse_mod_frqs'] = np.ones(nr_adptv_steps)*m.params['MW_modulation_frequency']
        m.params['MW_pulse_amps'] = np.zeros(nr_adptv_steps)
        m.params['MW_pulse_durations'] = np.zeros(nr_adptv_steps)*55e-9#0*np.linspace(0, 300e-9, nr_adptv_steps)#
        m.params['ramsey_time'] = np.zeros(nr_adptv_steps)
        m.params['fpga_mw_duration'] = np.linspace (0e-9, 200e-9, nr_adptv_steps)
        m.params['sweep_pts'] = m.params['fpga_mw_duration']*1e9
        m.params['sweep_name'] = 'fpga pulse duration [ns]'

    else:

        m.params['MW_pulse_mod_frqs'] = np.ones(nr_adptv_steps)*m.params['MW_modulation_frequency']
        m.params['MW_pulse_amps'] = m.params['MW_pi_pulse_amp']*np.ones(nr_adptv_steps)
        m.params['MW_pulse_durations'] = np.linspace(0, 200e-9, nr_adptv_steps)#
        m.params['ramsey_time'] = 0*np.ones(nr_adptv_steps)
        m.params['fpga_mw_duration'] = np.zeros(nr_adptv_steps)
        m.params['sweep_pts'] = m.params['MW_pulse_durations']*1e9
        m.params['sweep_name'] = 'awg pulse duration [ns]'


    m.autoconfig()
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()


def ramsey (name, tau = None, phase = None):
    '''
    initializes N-spin, ramsey experiment, sweeping time or phase of the fpga pulse
    '''
 
    if (tau==None):
        sweep_time = 1
    else:
        sweep_time = 0

    if sweep_time:
        n = 'ramsey_sweep_time_'+name
    else:
        n = 'ramsey_sweep_phase_'+str(tau*1e9)+'ns_'+name
    m = pulsar_mgnt.AdaptivePhaseEstimation(n)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE]['Magnetometry'])
    m.params.from_dict(qt.exp_params['protocols']['Magnetometry'])

    m.params['MW_modulation_frequency'] = 30e6
    m.params['mw_frq'] = m.params['ms+1_cntr_frq']-m.params['MW_modulation_frequency']
    print 'MW mod frequency:', m.params['MW_modulation_frequency']/1e6, ' MHz'
    m.params['Ex_SP_amplitude'] = 0
    m.params['wait_for_AWG_done'] = 1
    m.params['wait_after_RO_pulse_duration']=1#10000

    m.params['init_repetitions'] = 1

    nr_adptv_steps = 30
    m.params['do_adaptive'] = 0
    m.params['do_phase_calibr'] = 1
    m.params['min_phase'] = 0
    m.params['delta_phase'] = int(360/nr_adptv_steps) #just to have a label in the ssro data file
    m.params['adptv_steps'] = nr_adptv_steps
    m.params['repetitions'] = 1000
    
 
    pi2_mw_dur = 35e-9
    pi2_fpga_dur = 33e-9

    if sweep_time:

        m.params['MW_pulse_mod_frqs'] = np.ones(nr_adptv_steps)*m.params['MW_modulation_frequency']
        m.params['MW_pulse_amps'] = m.params['MW_pi_pulse_amp']*np.ones(nr_adptv_steps)
        m.params['MW_pulse_durations'] = pi2_mw_dur*np.ones(nr_adptv_steps)
        m.params['ramsey_time'] = np.linspace(0e-9, 120e-9, nr_adptv_steps)
        m.params['fpga_mw_duration'] = pi2_fpga_dur*np.ones(nr_adptv_steps) 
        m.params['sweep_pts'] = m.params['ramsey_time']*1e9
        m.params['sweep_name'] = 'free evolution time [ns]'

    else:

        m.params['MW_pulse_mod_frqs'] = np.ones(nr_adptv_steps)*m.params['MW_modulation_frequency']
        m.params['MW_pulse_amps'] = m.params['MW_pi_pulse_amp']*np.ones(nr_adptv_steps)
        m.params['MW_pulse_durations'] = pi2_mw_dur*np.ones(nr_adptv_steps)
        m.params['ramsey_time'] = tau*np.ones(nr_adptv_steps)
        m.params['fpga_mw_duration'] = pi2_fpga_dur*np.ones(nr_adptv_steps) 
        #m.params['sweep_pts'] = np.arange(nr_adptv_steps)
        #m.params['sweep_name'] = 'step'
        m.params['sweep_pts'] = np.arange(nr_adptv_steps)*m.params['delta_phase']
        m.params['sweep_name'] = 'phase fpga pulse [deg]'


    m.autoconfig()
    m.generate_sequence(upload=True)
    #m.run()
    #m.save()
    #m.finish()


def adaptive_real_time (name):
    '''
    initializes N-spin, ramsey experiment, sweeping time or phase of the fpga pulse
    '''
    nr_adptv_steps = 8 
    n = 'cappellaro_protocol_'+str(nr_adptv_steps)+'steps_'+name
    m = pulsar_mgnt.AdaptivePhaseEstimation(n)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE]['Magnetometry'])
    m.params.from_dict(qt.exp_params['protocols']['Magnetometry'])

    m.params['MW_modulation_frequency'] = 30e6
    m.params['mw_frq'] = m.params['ms+1_cntr_frq']-m.params['MW_modulation_frequency']
    print 'MW mod frequency:', m.params['MW_modulation_frequency']/1e6, ' MHz'
    m.params['Ex_SP_amplitude'] = 0
    m.params['wait_for_AWG_done'] = 1
    m.params['wait_after_RO_pulse_duration']=1#10000

    m.params['init_repetitions'] = 10

    nr_adptv_steps = 8
    m.params['do_adaptive'] = 1
    m.params['do_phase_calibr'] = 0
    m.params['min_phase'] = 0
    m.params['delta_phase'] = int(360/nr_adptv_steps) #just to have a label in the ssro data file
    m.params['adptv_steps'] = nr_adptv_steps
    m.params['repetitions'] = 1000
    
 
    pi2_mw_dur = 35e-9
    pi2_fpga_dur = 33e-9

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



if __name__ == '__main__':

    ramsey (name='', tau = 500e-9)


    #erabi_fpga_pulse (name = 'fpga_pulse')
    #adaptive_real_time (name='test')