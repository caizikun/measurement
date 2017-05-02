"""
Script for e-spin Hahn echo. Uses pulsar sequencer
"""
import qt
import numpy as np
import msvcrt

#reload all parameters and modules


from measurement.scripts.espin import espin_funcs as funcs
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
from measurement.lib.measurement2.adwin_ssro import pulse_select as ps
reload(funcs)

# from darkesr, use of some of these is hidden. Not relevant
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2

from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt, pulsar_delay
from measurement.lib.measurement2.adwin_ssro import pulse_select as ps

execfile(qt.reload_current_setup)
#reload(funcs)

#name = 'HANS_sil4'
SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']
name=SAMPLE_CFG

def electronT2_NoTriggers(name, debug = False, range_start = 0e-6, range_end=1000e-6):
    m = pulsar_delay.ElectronT2NoTriggers(name)

    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    m.params['pulse_type'] = 'Hermite'

    m.params['Ex_SP_amplitude']=0
    m.params['AWG_to_adwin_ttl_trigger_duration']=2e-6  # commenting this out gives an erro
    m.params['wait_for_AWG_done']=1
    m.params['sequence_wait_time']=1

    pts = 51
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    #m.params['wait_for_AWG_done']=1
    #m.params['evolution_times'] = np.linspace(0,0.25*(pts-1)*1/m.params['N_HF_frq'],pts)
    # range from 0 to 1000 us
    m.params['evolution_times'] = np.linspace(range_start,range_end,pts) 

    # MW pulses
    m.params['detuning']  = 0 #-1e6 #0.5e6
    X_pi2 = ps.Xpi2_pulse(m)
    X_pi = ps.X_pulse(m)
    m.params['pulse_sweep_pi2_phases1'] = np.ones(pts) * m.params['X_phase']    # First pi/2 = +X
    # m.params['pulse_sweep_pi2_phases2'] = np.ones(pts) * (m.params['X_phase']+180 )   # Second pi/2 = mX
    m.params['pulse_sweep_pi2_phases2'] = np.ones(pts) * m.params['X_phase']
    m.params['pulse_sweep_pi_phases'] = np.ones(pts) * m.params['X_phase']


    # for the autoanalysis
    m.params['sweep_name'] = 'evolution time (ns)'
    m.params['sweep_pts'] = (m.params['evolution_times'] + 2*m.params['Hermite_pi2_length'] + m.params['Hermite_pi_length'])* 1e9

    # for the self-triggering through the delay line
    # m.params['self_trigger_delay'] = 500e-9 # 0.5 us
    # m.params['self_trigger_duration'] = 100e-9

    # Start measurement
    m.autoconfig()
    m.generate_sequence(upload=True, pulse_pi2 = X_pi2, pulse_pi = X_pi)

    if not debug:
        m.run(autoconfig=False)
        m.save()
        m.finish()

def electronRefocussingTriggered(name, debug = False, range_start = -2e-6, range_end = 2e-6, 
    evolution_1_self_trigger=True, evolution_2_self_trigger=False, vary_refocussing_time=False,
    refocussing_time = 200e-6):
    m = pulsar_delay.ElectronRefocussingTriggered(name)

    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    m.params['pulse_type'] = 'Hermite'

    m.params['Ex_SP_amplitude']=0
    m.params['AWG_to_adwin_ttl_trigger_duration']=2e-6  # commenting this out gives an erro
    m.params['wait_for_AWG_done']=1
    m.params['sequence_wait_time']=1

    m.params['do_delay_voltage_control']=0
    m.params['delay_voltage_DAC_channel'] = 14

    pts = 51
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    #m.params['wait_for_AWG_done']=1
    #m.params['evolution_times'] = np.linspace(0,0.25*(pts-1)*1/m.params['N_HF_frq'],pts)
    # range from 0 to 1000 us

    # calibrated using Hahn echo
    m.params['self_trigger_delay'] = 2.950e-6 * np.ones(pts)
    m.params['self_trigger_duration'] = 100e-9

    if vary_refocussing_time:
        m.params['refocussing_time'] = np.linspace(range_start, range_end, pts)
        m.params['defocussing_offset'] = 0.0 * np.ones(pts)

        m.params['sweep_name'] = 'single-sided free evolution time (us)'
        m.params['sweep_pts'] = (m.params['refocussing_time']) * 1e6

    else:
        m.params['refocussing_time'] = np.ones(pts) * refocussing_time
        m.params['defocussing_offset'] = np.linspace(range_start,range_end,pts)

        m.params['sweep_name'] = 'defocussing offset (us)'
        m.params['sweep_pts'] = (m.params['defocussing_offset']) * 1e6

    # MW pulses
    X_pi2 = ps.Xpi2_pulse(m)
    X_pi = ps.X_pulse(m)

    # for the self-triggering through the delay line
    # m.params['self_trigger_delay'] = 500e-9 # 0.5 us
    # m.params['self_trigger_duration'] = 100e-9

    # Start measurement
    m.autoconfig()
    m.generate_sequence(upload=True, pulse_pi2 = X_pi2, pulse_pi = X_pi, evolution_1_self_trigger=evolution_1_self_trigger, evolution_2_self_trigger=evolution_2_self_trigger)

    if not debug:
        m.run(autoconfig=False)
        m.save()
        m.finish()

def reoptimize():
    GreenAOM.set_power(5e-6)
    optimiz0r.optimize(dims=['x','y','z'], cycles=2)
    GreenAOM.turn_off()

if __name__ == '__main__':

    # reoptimize()

    # electronT2_NoTriggers(name, debug=False)
    # bins = np.linspace(-5e-6, 5e-6, 11)[2:]

    # for i in range(len(bins) - 1):
    #     if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
    #         print 'aborting'
    #         break
    #     reoptimize()
    #     print('Starting delay line refocussing run with self-trigger offsets from {} ns to {} ns'.format(bins[i] * 1e9, bins[i+1] * 1e9))
    #     electronRefocussingTriggered("OneTrigger_" + name, debug=False, range_start = bins[i], range_end = bins[i+1], evolution_1_self_trigger = True)

    # for i in range(len(bins) - 1):
    #     if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
    #         print 'aborting'
    #         break
    #     reoptimize()
    #     print('Starting delay line refocussing run with no trigger offsets from {} ns to {} ns'.format(bins[i] * 1e9, bins[i+1] * 1e9))
    #     electronRefocussingTriggered("NoTrigger_" + name, debug=False, range_start = bins[i], range_end = bins[i+1], evolution_1_self_trigger = False)

    hahn_echo_range = [3.5e-6, 53.5e-6]
    defocussing_range = [-0.5e-6, 0.5e-6]

    # electronT2_NoTriggers(name, debug=True, range_start = hahn_echo_range[0], range_end = hahn_echo_range[1])

    # reoptimize()
    electronRefocussingTriggered("HahnEchoNoTrigger_" + name, debug=True, 
        range_start = hahn_echo_range[0], range_end = hahn_echo_range[1], 
        evolution_1_self_trigger = False, evolution_2_self_trigger=False,
        vary_refocussing_time = True)
    
    # reoptimize()    
    # electronRefocussingTriggered("DefocussingNoTrigger_" + name, debug=False, 
    #     range_start = defocussing_range[0], range_end = defocussing_range[1], 
    #     evolution_1_self_trigger = False, evolution_2_self_trigger=False,
    #     vary_refocussing_time = False)

    # reoptimize()    
    # electronRefocussingTriggered("DefocussingOneTrigger_" + name, debug=False, 
    #     range_start = defocussing_range[0], range_end = defocussing_range[1], 
    #     evolution_1_self_trigger = True, evolution_2_self_trigger=False,
    #     vary_refocussing_time = False)

    # reoptimize()
    # electronRefocussingTriggered("HahnEchoTwoTrigger_" + name, debug=False, 
    #     range_start = hahn_echo_range[0], range_end = hahn_echo_range[1], 
    #     evolution_1_self_trigger = True, evolution_2_self_trigger=True,
    #     vary_refocussing_time = True)



