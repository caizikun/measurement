"""
Script for e-spin Hahn echo. Uses pulsar sequencer
"""
import qt
import numpy as np
import msvcrt

#reload all parameters and modules


from measurement.scripts.espin import espin_funcs as funcs
reload(funcs)

# from darkesr, use of some of these is hidden. Not relevant
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2

from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import pulsar_delay; reload(pulsar_delay)#, pulsar_msmt, pulsar_msmt_delay
# reload(pulsar_msmt)
# reload(pulsar_msmt_delay)
from measurement.lib.measurement2.adwin_ssro import pulse_select as ps

#import delay_pulsar_msmt
#reload(delay_pulsar_msmt)

execfile(qt.reload_current_setup)
#reload(funcs)

#name = 'HANS_sil4'
SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']
name=SAMPLE_CFG

def hahn_echo_variable_delayline(name, debug=False, 
    vary_refocussing_time=True, range_start=-2e-6, range_end=2e6,
    evolution_1_self_trigger=False, evolution_2_self_trigger=False,
    refocussing_time=10e-6, is_calibration_msmt=False, do_HH_trigger=False):
    m = pulsar_delay.ElectronRefocussingTriggered(name)

    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+delay'])

    m.params['pulse_type'] = 'Hermite'

    m.params['Ex_SP_amplitude']=0
    m.params['AWG_to_adwin_ttl_trigger_duration']=2e-6
    m.params['wait_for_AWG_done']=1
    m.params['sequence_wait_time']=1

    if do_HH_trigger:
        m.params['do_delay_HH_trigger'] = 1

    pts = 1

    m.params['pts'] = pts
    m.params['repetitions'] = 1000000

    if vary_refocussing_time:
        m.params['refocussing_time'] = np.linspace(range_start, range_end, pts)
        m.params['defocussing_offset'] = 0.0 * np.ones(pts)
        m.params['self_trigger_delay'] = m.params['refocussing_time'] 

        m.params['sweep_name'] = 'single-sided free evolution time (us)'
        m.params['sweep_pts'] = (m.params['refocussing_time']) * 1e6

    else:
        
        m.params['defocussing_offset'] = np.linspace(range_start,range_end,pts)

        if is_calibration_msmt:
            m.params['sweep_name'] = 'effective delay (ns)'
            m.params['sweep_pts'] = (
                m.params['physical_delay_time_offset'] # - m.params['delayed_element_run_up_time']
                # - (m.params['minimal_delay_cycles'] * m.params['delay_clock_cycle_time'])
                - m.params['defocussing_offset']) * 1e9

            # compatibilize the refocussing time and the delay time 
            # (i.e. make the number of delay cycles integer)
            delay_clock_cycle_time = m.params['delay_clock_cycle_time']
            minimal_delay_time = m.params['delay_time_offset']
            delay_time_remainder = minimal_delay_time - int(minimal_delay_time / delay_clock_cycle_time) * delay_clock_cycle_time

            refocussing_time = int(refocussing_time / delay_clock_cycle_time) * delay_clock_cycle_time
            refocussing_time += delay_time_remainder
        else:
            m.params['sweep_name'] = 'defocussing offset (us)'
            m.params['sweep_pts'] = (m.params['defocussing_offset']) * 1e6

        m.params['refocussing_time'] = np.ones(pts) * refocussing_time
        m.params['self_trigger_delay'] = m.params['refocussing_time']

    m.params['delay_times'] = m.params['self_trigger_delay']
    m.params['do_tico_delay_control'] = 1

    # MW pulses
    X_pi2 = ps.Xpi2_pulse(m)
    X_pi = ps.X_pulse(m)

    # Start measurement
    m.autoconfig()
    print(m.params['delay_cycles'])
    m.generate_sequence(upload=True, pulse_pi2 = X_pi2, pulse_pi = X_pi, 
        evolution_1_self_trigger=evolution_1_self_trigger, 
        evolution_2_self_trigger=evolution_2_self_trigger,
        post_selftrigger_delay = 2e-6)

    if not debug:
        m.run(autoconfig=False)
        m.save()
        m.finish()

if __name__ == '__main__':
    # upload_dummy_selftrigger_sequence("Dummy_Selftrigger", period=10e-6, on_time=100e-9, debug=False, do_delay_control=True)
    # hahn_echo_variable_delayline("VariableDelay_Defocussing_0T_" + name, 
    #     debug=False,
    #     range_start = -200e-9,
    #     range_end = 200e-9,
    #     vary_refocussing_time = False,
    #     evolution_1_self_trigger = False,
    #     evolution_2_self_trigger = False)
    # hahn_echo_variable_delayline("VariableDelay_Defocussing_1T_" + name, 
    #     debug=False,
    #     range_start = -500e-9,
    #     range_end = 500e-9,
    #     vary_refocussing_time = False,
    #     evolution_1_self_trigger = True,
    #     evolution_2_self_trigger = False)

    # hahn_echo_variable_delayline("VariableDelay_HahnEcho_0T_" + name, 
    #     debug=False,
    #     range_start = 10e-6,
    #     range_end = 100e-6,
    #     vary_refocussing_time = True,
    #     evolution_1_self_trigger = False,
    #     evolution_2_self_trigger = False)

    msmt = "calibration"

    if msmt == "calibration":
        hahn_echo_variable_delayline("VariableDelay_Calibration_HahnEcho_1T_" + name, 
            debug=False,
            range_start = -200e-9,
            range_end = 200e-9,
            vary_refocussing_time = False,
            refocussing_time = 3e-6,
            evolution_1_self_trigger = True,
            evolution_2_self_trigger = False,
            is_calibration_msmt = True,
            do_HH_trigger=True)
    elif msmt == "check_calibration":
        hahn_echo_variable_delayline("VariableDelay_CheckCalib_HahnEcho_1T_" + name, 
            debug=False,
            range_start = 10e-6 + 1294e-9,
            range_end = 100e-6 + 1294e-9,
            vary_refocussing_time = True,
            evolution_1_self_trigger = True,
            evolution_2_self_trigger = False,
            is_calibration_msmt = False)