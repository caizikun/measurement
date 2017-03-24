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



def V_c_from_dl_fit(dl_in_s, dl0, V_c0, A, B, C, D):
    dl = dl_in_s * 1e9
    return V_c0 + A / (dl0-dl) + B / (dl0-dl)**2 + C / (dl0-dl)**3 + D / (dl0-dl)**4

def upload_dummy_selftrigger_sequence(name, period=200e-6, on_time=2e-6, debug=True):
    m = pulsar_delay.DummySelftriggerSequence(name, save=False)

    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+delay'])

    pts = 11

    m.params['pts'] = pts
    m.params['repetitions'] = 1000

    m.params['delay_to_voltage_fitparams'] = np.loadtxt('../lt4_V_c_from_dl_fit_20170323_1914.txt')
    m.params['delay_to_voltage_fitfunc'] = V_c_from_dl_fit

    #m.params['delay_voltages'] = np.linspace(2.5,2.7,pts)
    m.params['self_trigger_delay'] = np.linspace(200e-9, 1200e-9, pts)
    # m.params['delay_voltage_DAC_channel'] = 16
    m.params['do_delay_voltage_control'] = 1

    # Start measurement
    m.autoconfig()
    m.generate_sequence(upload=True, period=period, on_time=on_time)

    if not debug:
        m.run(autoconfig=False)
        m.finish()

def hahn_echo_variable_delayline(name, debug=False, 
    vary_refocussing_time=True, range_start=-2e-6, range_end=2e6,
    evolution_1_self_trigger=False, evolution_2_self_trigger=False,
    refocussing_time=1e-6):
    m = pulsar_delay.ElectronRefocussingTriggered(name)

    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+delay'])

    m.params['delay_to_voltage_fitparams'] = np.loadtxt('../lt4_V_c_from_dl_fit_20170323_1914.txt')
    m.params['delay_to_voltage_fitfunc'] = V_c_from_dl_fit

    m.params['pulse_type'] = 'Hermite'

    m.params['Ex_SP_amplitude']=0
    m.params['AWG_to_adwin_ttl_trigger_duration']=2e-6
    m.params['wait_for_AWG_done']=1
    m.params['sequence_wait_time']=1

    m.params['self_trigger_duration'] = 100e-9

    # m.params['delay_voltage_DAC_channel'] = 16 # should be moved to msmt_params?
    m.params['do_delay_voltage_control'] = 1

    pts = 11

    m.params['pts'] = pts
    m.params['repetitions'] = 1000

    if vary_refocussing_time:
        m.params['refocussing_time'] = np.linspace(range_start, range_end, pts)
        m.params['defocussing_offset'] = 0.0 * np.ones(pts)
        m.params['self_trigger_delay'] = m.params['refocussing_time'] 

        m.params['sweep_name'] = 'single-sided free evolution time (us)'
        m.params['sweep_pts'] = (m.params['refocussing_time']) * 1e6

    else:
        m.params['refocussing_time'] = np.ones(pts) * refocussing_time
        m.params['defocussing_offset'] = np.linspace(range_start,range_end,pts)
        m.params['self_trigger_delay'] = m.params['refocussing_time']

        m.params['sweep_name'] = 'defocussing offset (us)'
        m.params['sweep_pts'] = (m.params['defocussing_offset']) * 1e6

    # MW pulses
    X_pi2 = ps.Xpi2_pulse(m)
    X_pi = ps.X_pulse(m)

    # Start measurement
    m.autoconfig()
    print(m.params['delay_voltages'])
    m.generate_sequence(upload=True, pulse_pi2 = X_pi2, pulse_pi = X_pi, evolution_1_self_trigger=evolution_1_self_trigger, evolution_2_self_trigger=evolution_2_self_trigger)

    if not debug:
        m.run(autoconfig=False)
        m.save()
        m.finish()

if __name__ == '__main__':
    upload_dummy_selftrigger_sequence("Dummy_Selftrigger", period=200e-6, on_time=2e-6, debug=False)
    # hahn_echo_variable_delayline("VariableDelay_Defocussing_1T_" + name, 
    #     debug=True,
    #     range_start = -100e-9,
    #     range_end = 100e-9,
    #     vary_refocussing_time = False,
    #     evolution_1_self_trigger = True,
    #     evolution_2_self_trigger = False)