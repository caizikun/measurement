# reload all parameters and modules, import classes
import numpy as np
import qt

from measurement.lib.measurement2.adwin_ssro import pulsar_msmt, pulsar_delay
reload(pulsar_msmt)
from measurement.scripts.espin import espin_funcs
from measurement.scripts.fast_carbon_control.delay_characterization import electron_T2_variable_delayline as hahn_sweep
from measurement.lib.pulsar import pulse, pulselib, element, pulsar, eom_pulses
execfile(qt.reload_current_setup)
from analysis.lib.sim.pulse_sim import pulse_sim
reload(pulse_sim)

SAMPLE= qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']
name = SAMPLE_CFG

def hahn_echo_with_djump(name, debug=False, upload = False,
    vary_refocussing_time=True, range_start=-2e-6, range_end=2e6,
    evolution_1_self_trigger=False, evolution_2_self_trigger=False,
    refocussing_time=10e-6):

    m = pulsar_delay.ElectronRefocussingTriggered(name)

    m.mprefix += "_djump"
    m.adwin_process = 'dynamic_jump'

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

    m.params['self_trigger_duration'] = 100e-9

    pts = 51

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

    m.params['delay_times'] = m.params['self_trigger_delay']
    m.params['do_tico_delay_control'] = 0

    m.params['minimal_delay_cycles'] = 0
    m.params['minimal_delay_time'] = 0

    # MW pulses
    X_pi2 = ps.Xpi2_pulse(m)
    X_pi = ps.X_pulse(m)

    # We have to upload the old sequence if we want to retrieve it from the pulsar
    m.generate_sequence(upload = True, pulse_pi2 = X_pi2, pulse_pi = X_pi, 
        evolution_1_self_trigger=evolution_1_self_trigger, 
        volution_2_self_trigger=evolution_2_self_trigger,
        post_selftrigger_delay = 2e-6)

    print 'Programmed old sequence; creating new'

    old_seq = qt.pulsar.last_programmed_sequence
    old_elems = qt.pulsar.last_programmed_elements

    generate_new_sequence(m, old_seq, old_elems, upload = upload)
    calculate_delay_cycles(m)

    m.adwin.set_dynamic_jump_var(
        jump_table      = flat(m.params['jump_table']),  
        delay_cycles    = flat(m.params['delay_table'], np.float32), 
        next_seq_table  = flat(m.params['next_seq_table'])
        )

    m.setup(wait_for_awg = False, mw = False, ssro_setup = False, awg_ready_state='Running')
    m.run(autoconfig = False, setup = False)

def generate_new_sequence(m, seq, elements, upload = False):
    qt.pulsar.AWG_sequence_cfg['JUMP_TIMING'] = 0 # ASYNC
    [overview, pulse_array] = pulse_sim.group_seq_elems(seq, elements)
   
    seq_uniq = pulsar.Sequence(seq.name + '-unique')
    seq_uniq.set_djump(True)
    elements_uniq = []

    unique_pulses = {}
    jump_index = 0

    empty = pulse.SquarePulse(channel = 'adwin_sync', length = 1e-6, amplitude = 0)

    e_loop = element.Element('loop', pulsar = qt.pulsar, global_time = True)
    e_wait = element.Element('trigger_wait', pulsar = qt.pulsar, global_time = True)

    e_loop.add(pulse.cp(empty, length = 1e-3), name = e_loop.name)
    elements_uniq.append(e_loop)
    seq_uniq.append(name = e_loop.name, wfname = e_loop.name, goto_target = e_wait.name, repetitions = 65536)

    e_wait.add(pulse.cp(empty), name = e_wait.name)
    elements_uniq.append(e_wait)
    seq_uniq.append(name = e_wait.name, wfname = e_wait.name, goto_target = e_loop.name, trigger_wait = True)
    seq_uniq.add_djump_address(0, e_wait.name)

    m.params['jump_table'] = []
    m.params['delays_before_jumps'] = []
    m.params['next_seq_table'] = []

    start_prev = 0

    for seq_idx, (pulse_overview, pulse_seq) in enumerate(zip(overview, pulse_array)):

        pulse_overview['jump_table'] = []
        pulse_overview['delays'] = []

        for pul_idx, pul in enumerate(pulse_seq):
            pul_physical = None

            mid_point, length, phase, rotation, special = pul

            phase = 180 * phase / np.pi

            key = tuple([round(var, 5) for var in (length, phase, rotation, special)]) # rounding errors in pars

            if key in unique_pulses:
                pul_physical = unique_pulses[key][0]
            else:
                jump_index += 1 # We are adding a new pulse to the jump table

                if special == 0:
                    if rotation == np.pi:
                        pul_physical = pulse.cp(ps.X_pulse(m), phase = phase)
                    else:
                        pul_physical = pulse.cp(ps.Xpi2_pulse(m), phase = phase)
                elif special == 1:
                    pul_phsyical = pulse.SquarePulse(channel='AOM_Newfocus', length = length, amplitude = 0.2)
                elif special == 2:
                    pul_physical = pulse.SquarePulse(channel='adwin_sync', length = length, amplitude = 2)
                    # ADWIN DOESN'T NEED TO SYNC WITH ITSELF?
                else:
                    pul_phsyical = pulse.SquarePulse(channel='AOM_Matisse', length = length, amplitude = 0.2)

                pul_name = pul_physical.name + ('-%i' % jump_index) # Give pulses unique names
                e = element.Element(pul_name, pulsar = qt.pulsar, global_time = True, min_samples = 1e3)
                e.add(pul_physical, name = pul_name)

                elements_uniq.append(e)

                seq_uniq.append(name = e.name, wfname = e.name, goto_target = e_loop.name)
                seq_uniq.add_djump_address(jump_index, e.name)

                unique_pulses[key] = [pul_physical, jump_index]

            channel_offset = 0
            for ch in pul_physical.channels:
                if qt.pulsar.channels[ch]['delay'] > channel_offset:
                    channel_offset = qt.pulsar.channels[ch]['delay']

            length += pul_physical.start_offset + pul_physical.stop_offset
            start = mid_point - length / 2 - channel_offset
            delay = start - start_prev

            pulse_overview['jump_table'].append(unique_pulses[key][1])
            pulse_overview['delays'].append(delay)

            if pul_idx == len(pulse_seq) - 1:
                pulse_overview['jump_table'].append(-1)
                pulse_overview['delays'].append(pulse_overview['final_time'] - start - length)
            
            start_prev = start

        m.params['jump_table'].append(pulse_overview['jump_table'])
        m.params['delays_before_jumps'].append(pulse_overview['delays'])

        if pulse_overview['goto_target'] != 'None':
            start_prev = 0
            next_goto = next(i for (i, o) in enumerate(overview) if o['goto_target'] == pulse_overview['goto_target'])
        else:
            start_prev = pulse_overview['final_time']
            if seq_idx + 1 == len(overview):
                next_goto = 1
            else:
                next_goto = seq_idx + 2

        if pulse_overview['jump_target'] != 'None':
            start_prev = 0
            next_jump = next(i for (i, o) in enumerate(overview) if o['jump_target'] == pulse_overview['jump_target'])
        else:
            start_prev = pulse_overview['final_time']
            next_jump = 0

        m.params['next_seq_table'].append([next_goto, next_jump])

    # upload new seq
    if upload:
        qt.pulsar.program_awg(seq_uniq, *elements_uniq)

def flat(table, dtype = np.int32):
    return np.array(table, dtype = dtype).flatten()

def calculate_delay_cycles(m):
        # convert delay times into number of cycles
        delay_cycles = (
            (
                np.array(m.params['delays_before_jumps']) 
                - m.params['minimal_delay_time']
            ) 
            / m.params['delay_clock_cycle_time'] 
            + m.params['minimal_delay_cycles']
        )
        m.params['delay_table'] = delay_cycles
        if np.min(delay_cycles) < m.params['minimal_delay_cycles']:
            raise Exception("Desired delay times are too short")

if __name__ == '__main__':

    hahn_echo_with_djump("VariableDelay_HahnEcho_2T_" + name + "_DJUMP", 
    debug = True,
    upload = True,
    range_start = 2e-6,
    range_end = 100e-6,
    vary_refocussing_time = True,
    evolution_1_self_trigger = False,
    evolution_2_self_trigger = False)
