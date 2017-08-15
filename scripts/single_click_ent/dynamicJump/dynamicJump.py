# reload all parameters and modules, import classes
import numpy as np
import qt
import random

from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
reload(pulsar_msmt)
from measurement.scripts.espin import espin_funcs
# from measurement.scripts.fast_carbon_control.delay_characterization import electron_T2_variable_delayline as hahn_sweep
from measurement.lib.pulsar import pulse, pulselib, element, pulsar, eom_pulses
execfile(qt.reload_current_setup)
from analysis.lib.sim.pulse_sim import pulse_sim
reload(pulse_sim)

SAMPLE= qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']
name = SAMPLE_CFG

def random_XY_pulsar(name, debug = False, upload = True, run_msmt = True, init_tables = True, hermite_amp = 1, min_pulses = 1, max_pulses = 61):

    m = RandomXYFidelity(name)

    m.adwin_process = 'integrated_ssro_tico_controlled'
    
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    m.params['pulse_type'] = 'Hermite'

    m.params['wait_for_AWG_done'] = 1
    m.params['sequence_wait_time'] = 1
 
    m.params['unique_no_pulses'] = 4

    pts = 16
    m.params['pts'] = pts
    m.params['repetitions'] = 2500

    num_pulses = np.round(np.linspace(min_pulses, max_pulses, pts)).astype(np.int32)
    # for the autoanalysis
    m.params['sweep_name'] = 'number of random pulses'
    m.params['sweep_pts'] = num_pulses

    # lt3 params
    m.params['AWG_start_DO_channel'] = 9
    m.params['AWG_jump_strobe_DO_channel'] = 0
    m.params['jump_bit_shift'] = 4
    m.params['do_random_gates'] = 0

    m.params['delay_time'] = 2.26e-6
    m.params['delay_clock_cycle_time'] = 20e-9

    m.params['Hermite_pi_amp'] = hermite_amp

    print 'Hermite amp ', m.params['Hermite_pi_amp']
    print 'No. pulses ', num_pulses # Show the sweep pts

    # Start measurement
    m.generate_sequence(
        upload = upload, 
        Hermite_pi = ps.X_pulse(m),
        Hermite_pi2 = ps.Y_pulse(m),
        # pulse_minX = ps.mX_pulse(m), 
        # pulse_minY = ps.mY_pulse(m),
    )
    
    if run_msmt:
        if init_tables:
            delay_cycle = np.rint(m.params['delay_time'] / m.params['delay_clock_cycle_time']).astype(np.int32)

            seq_indices = np.cumsum(np.insert(num_pulses, 0, 1))
            random_jumps = np.random.randint(low = 1, high = m.params['unique_no_pulses'] + 1, size = 1e7)

            jump_table = np.repeat(1, seq_indices[-1])
            delay_cycles = np.repeat(delay_cycle, seq_indices[-1])
            next_seq_table = np.repeat(0, m.params['pts'] * 2) # Unused atm

            m.adwin.start_dynamic_jump(
                cycle_duration = m.params['cycle_duration'],
                AWG_start_DO_channel = m.params['AWG_start_DO_channel'],
                AWG_jump_strobe_DO_channel = m.params['AWG_jump_strobe_DO_channel'],
                do_init_only = 1,
                jump_bit_shift = m.params['jump_bit_shift'],
            )

            qt.msleep(0.05)
       
            m.adwin.set_dynamic_jump_var(
                jump_table      = (2**m.params['jump_bit_shift']) *jump_table,
                delay_cycles    = delay_cycles, 
                next_seq_table  = next_seq_table,
                seq_indices     = seq_indices,
                random_ints     = (2**m.params['jump_bit_shift']) * random_jumps,
            )
        qt.msleep(0.05)
           
        m.run()
        m.save()
        m.finish()

def jitter_timings(name, debug = False, upload = True, old_school = False, run_msmt = True):

    m = SquarePulseJitter(name)

    m.adwin_process = 'dynamic_jump'

    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    m.params['pulse_type'] = 'Square'

    m.params['pts'] = 10
    m.params['repetitions'] = 1000

    # lt3 params
    m.params['AWG_start_DO_channel'] = 9
    m.params['AWG_jump_strobe_DO_channel'] = 0
    m.params['do_init_only'] = 0
    m.params['jump_bit_shift'] = 4

    m.params['table_dim'] = 256

    m.params['minimal_delay_time'] = 0
    m.params['minimal_delay_cycles'] = 0
    m.params['delay_clock_cycle_time'] = 20e-9

    # Start measurement
    seq, elements = m.generate_sequence(upload = old_school)

    print 'Programmed old sequence; creating new'

    if not(old_school):
        generate_new_sequence(m, seq, elements, upload = upload)
        calculate_delay_cycles(m)

        # Print the tables that go to the adwin
        # print m.params['jump_table']
        # print m.params['next_seq_table']
        # for delays in m.params['delays_before_jumps']:
        # print [round(var, 12) for var in delays]
    
    if run_msmt:
         
        if not(old_school):
            m.adwin.start_dynamic_jump(do_init_only = 1) # Necessary for init
            qt.msleep(0.05)
            td = m.params['table_dim']
       
            m.adwin.set_dynamic_jump_var(
            jump_table      = (2**m.params['jump_bit_shift']) * pad_and_flat(m.params['jump_table'], td, td),  
            delay_cycles    = pad_and_flat(m.params['delay_table'], td, td), 
            next_seq_table  = pad_and_flat(m.params['next_seq_table'], td, 2)
            )

            print 'Waiting until AWG done'
            qt.msleep(7)
            print 'Starting msmt'
            m.awg.start()
            qt.msleep(1)
            m.adwin.start_dynamic_jump(do_init_only = 0)

def hahn_echo_with_djump(name, debug=False, upload = False,old_school=False, range_start = -2e-6, range_end = 2e6, run_msmt = True):

    # From electron_T2_fixed_delayline
    m = ElectronT2NoTriggers(name)

    m.mprefix += "_djump"
    if old_school:
        m.adwin_process = 'integrated_ssro'
    else:
        m.adwin_process = 'integrated_ssro_tico_controlled'
    
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    m.params['pulse_type'] = 'Hermite'

    m.params['wait_for_AWG_done']=1
    m.params['sequence_wait_time']=1

    pts = 50
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    #m.params['wait_for_AWG_done']=1
    #m.params['evolution_times'] = np.linspace(0,0.25*(pts-1)*1/m.params['N_HF_frq'],pts)
    # range from 0 to 1000 us
    m.params['evolution_times'] = np.ones(pts) * 10000e-9 
    m.params['defocussing_offset'] = np.linspace(range_start,range_end,pts) 

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
    m.params['sweep_pts'] = (m.params['defocussing_offset'])* 1e9

    # for the self-triggering through the delay line
    # m.params['self_trigger_delay'] = 500e-9 # 0.5 us
    # m.params['self_trigger_duration'] = 100e-9

    # lt3 params
    m.params['AWG_start_DO_channel'] = 9
    m.params['AWG_jump_strobe_DO_channel'] = 0
    m.params['jump_bit_shift'] = 4

    m.params['table_dim'] = 256

    m.params['minimal_delay_time'] = 0
    m.params['minimal_delay_cycles'] = 0
    m.params['delay_clock_cycle_time'] = 20e-9

    # Start measurement
    seq, elements = m.generate_sequence(upload=old_school, pulse_pi2 = X_pi2, pulse_pi = X_pi)

    print 'Programmed old sequence'

    if not(old_school):
        generate_new_sequence(m, seq, elements, upload = upload)
        calculate_delay_cycles(m)

        print 'Programmed new sequence'

        # Print the tables that go to the adwin
        # print m.params['jump_table']
        # print m.params['next_seq_table']
        # for delays in m.params['delays_before_jumps']:
        # print [round(var, 12) for var in delays]

    
    if run_msmt:
         
        if not(old_school):
            m.adwin.start_dynamic_jump(do_init_only = 1) # Necessary for init
            qt.msleep(0.05)
            td = m.params['table_dim']
       
            m.adwin.set_dynamic_jump_var(
            jump_table      = (2**m.params['jump_bit_shift']) * pad_and_flat(m.params['jump_table'], td, td),  
            delay_cycles    = pad_and_flat(m.params['delay_table'], td, td), 
            next_seq_table  = pad_and_flat(m.params['next_seq_table'], td, 2)
            )
           
        m.run()
        m.save()
        m.finish()

def pad_and_flat(table, x_size, y_size, dtype = np.int32):
    np_table = np.array(table, dtype = dtype)
    ext_table = np.zeros((x_size, y_size), dtype = dtype)

    ext_table[:np_table.shape[0],:np_table.shape[1]] = np_table
    return ext_table.flatten()

class RandomXYFidelity(pulsar_msmt.PulsarMeasurement):

    mprefix = 'RandomXYFidelity'

    def generate_sequence(self, upload = True, **kw):

        qt.pulsar.AWG_sequence_cfg['JUMP_TIMING'] = 0 # ASYNC
        seq = pulsar.Sequence('Random XY pulses')
        seq.set_djump(True)

        elements = []

        adwin_sync = pulse.SquarePulse(channel='adwin_sync', length = 10e-6, amplitude = 2)
        empty = pulse.SquarePulse(channel = 'adwin_sync', length = 1e-6, amplitude = 0)

        jump_index = 0

        e_loop = element.Element('loop', pulsar = qt.pulsar, global_time = True, min_samples = 1e3)
        e_wait = element.Element('trigger_wait', pulsar = qt.pulsar, global_time = True, min_samples = 1e3) # currently not used
    
        e_wait.add(pulse.cp(empty), name = e_wait.name)
        elements.append(e_wait)
        seq.append(name = e_wait.name, wfname = e_wait.name, goto_target = e_loop.name, trigger_wait = True)
        # seq.add_djump_address(jump_index, e_wait.name)

        e_loop.add(pulse.cp(empty, length = 1e-3), name = e_loop.name)
        elements.append(e_loop)
        seq.append(name = e_loop.name, wfname = e_loop.name, goto_target = e_wait.name, repetitions = 65536)

        for name, ps in kw.iteritems():
            jump_index += 1

            e = element.Element(name + '-%d' % jump_index, pulsar = qt.pulsar, global_time = True, min_samples = 1e3)
            e.add(pulse.cp(ps), name = e.name)

            elements.append(e)

            seq.append(name = e.name, wfname = e.name, goto_target = e_loop.name)
            seq.add_djump_address(jump_index, e.name)

        # For some strange reason the last pulse doenst treat goto_target correctly
        e_sync = element.Element('sync', pulsar = qt.pulsar, global_time = True, min_samples = 1e3)
        e_sync.add(pulse.cp(adwin_sync), name = e_sync.name)
        elements.append(e_sync)
        seq.append(name = e_sync.name, wfname = e_sync.name, goto_target = e_loop.name)
        seq.add_djump_address(0, e_sync.name)

        # upload the waveforms to the AWG
        if upload:
            if upload=='old_method':
                qt.pulsar.upload(*elements)
                qt.pulsar.program_sequence(seq)
            else:
                qt.pulsar.program_awg(seq,*elements)

class SquarePulseJitter(pulsar_msmt.PulsarMeasurement):

    mprefix = 'SquarePulseJitter'

    def generate_sequence(self, upload = True):

        T = pulse.SquarePulse(channel='MW_Imod', name='delay',
            length = 3000e-9, amplitude = 0.)

        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = 10e-6,
            amplitude = 2)

        X_pi = ps.X_pulse(self)

        elements = []

        e = element.Element('Square_pulses', pulsar = qt.pulsar, global_time = True)

        e.append(pulse.cp(T))

        e.append(pulse.cp(X_pi, phase = 0))

        e.append(pulse.cp(T))

        pid = e.append(pulse.cp(X_pi, phase = 90))

        e.add(pulse.cp(adwin_sync), start = 5e-6, refpulse = pid)

        elements.append(e)

        seq = pulsar.Sequence('Square pulses for jitter timing')
        for e in elements:
            seq.append(name=e.name, wfname=e.name, trigger_wait=True)

        # upload the waveforms to the AWG
        if upload:
            if upload=='old_method':
                qt.pulsar.upload(*elements)
                qt.pulsar.program_sequence(seq)
            else:
                qt.pulsar.program_awg(seq,*elements)

        return seq, elements

class ElectronT2NoTriggers(pulsar_msmt.PulsarMeasurement):
    """
    Class to generate an electron Hahn echo sequence with a single refocussing pulse.
    generate_sequence needs to be supplied with a pi2_pulse as kw.
    """
    mprefix = 'ElectronT2NoTriggers'

    def autoconfig(self):
        self.params['sequence_wait_time'] = \
            int(np.ceil(np.max(self.params['evolution_times'])*1e6)+10)


        pulsar_msmt.PulsarMeasurement.autoconfig(self)

    def  generate_sequence(self, upload=True, **kw):

        # define the necessary pulses
        
        # rotations
        pulse_pi2 = kw.get('pulse_pi2', None)
        pulse_pi = kw.get('pulse_pi', None)

        # waiting element        
        T = pulse.SquarePulse(channel='MW_Imod', name='delay',
            length = 200e-9, amplitude = 0.)

        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = 10e-6,
            amplitude = 2)

        # make the elements, one for each evolution time
        elements = []
        for i in range(self.params['pts']):

            e1 = element.Element('ElectronT2_notrigger_pt-%d_A' % i, pulsar=qt.pulsar,
                global_time = True)
            e1.append(pulse.cp(T,
                length = 3000e-9))

            e1.append(pulse.cp(pulse_pi2,
                phase = self.params['pulse_sweep_pi2_phases1'][i]))

            e1.append(pulse.cp(T,
                length = self.params['evolution_times'][i] / 2.))

            e1.append(pulse.cp(pulse_pi,
                phase = self.params['pulse_sweep_pi_phases'][i]))

            e1.append(pulse.cp(T,
                length = (self.params['evolution_times'][i]/2) +  self.params['defocussing_offset'][i] / 2.))

            pid = e1.append(pulse.cp(pulse_pi2,
                phase = self.params['pulse_sweep_pi2_phases2'][i]))

            e1.add(adwin_sync, start = 3e-6, refpulse = pid)

            elements.append(e1)
        # return_e=e
        # create a sequence from the pulses
        seq = pulsar.Sequence('Electron T2 with AWG timing with {} pulses'.format(self.params['pulse_type']))
        for e in elements:
            seq.append(name=e.name, wfname=e.name, trigger_wait=True)

        # upload the waveforms to the AWG
        if upload:
            if upload=='old_method':
                qt.pulsar.upload(*elements)
                qt.pulsar.program_sequence(seq)
            else:
                qt.pulsar.program_awg(seq,*elements)

        return seq, elements

def generate_new_sequence(m, seq, elements, upload = False):
    qt.pulsar.AWG_sequence_cfg['JUMP_TIMING'] = 0 # ASYNC
    [overview, pulse_array] = group_seq_elems(seq, elements)
   
    seq_uniq = pulsar.Sequence(seq.name + '-unique')
    seq_uniq.set_djump(True)
    elements_uniq = []

    unique_pulses = {}
    jump_index = 0

    # empty = pulse.SquarePulse(channel = 'tico_sync', length = 1e-6, amplitude = 0)
    empty = pulse.SquarePulse(channel = 'adwin_sync', length = 1e-6, amplitude = 0)

    e_loop = element.Element('loop', pulsar = qt.pulsar, global_time = True, min_samples = 1e3)
    e_wait = element.Element('trigger_wait', pulsar = qt.pulsar, global_time = True, min_samples = 1e3) # currently not used
    # e_start_tico = element.Element('start_tico', pulsar = qt.pulsar, global_time = True, min_samples = 1e3)

    # e_loop.add(pulse.cp(empty, amplitude = 2, length = 100e-9), name = e_loop.name + '_sync')
    
    e_wait.add(pulse.cp(empty), name = e_wait.name)
    elements_uniq.append(e_wait)
    seq_uniq.append(name = e_wait.name, wfname = e_wait.name, goto_target = e_loop.name, trigger_wait = True)
    seq_uniq.add_djump_address(jump_index, e_wait.name)

    # e_start_tico.add(pulse.cp(empty, amplitude = 2, length = 100e-9), name = e_start_tico.name)
    # elements_uniq.append(e_start_tico)
    # seq_uniq.append(name = e_start_tico.name, wfname = e_start_tico.name, goto_target = e_loop.name)
    # seq_uniq.add_djump_address(jump_index, e_start_tico.name)

    e_loop.add(pulse.cp(empty, length = 1e-3), name = e_loop.name) # + '_empty', refpulse = e_loop.name + '_sync')
    elements_uniq.append(e_loop)
    seq_uniq.append(name = e_loop.name, wfname = e_loop.name, goto_target = e_wait.name, repetitions = 65536)
    
    m.params['jump_table'] = []
    m.params['delays_before_jumps'] = []
    m.params['next_seq_table'] = []

    start_prev = 0

    for seq_idx, (pulse_overview, pulse_seq) in enumerate(zip(overview, pulse_array)):

        pulse_overview['jump_table'] = []
        pulse_overview['delays'] = []

        if pulse_overview['trigger_wait'] > 0:
            start_prev = 0

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
                pulse_overview['jump_table'].append(0)
                pulse_overview['delays'].append(pulse_overview['final_time'] - start - length) # Not used atm
            
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

def calculate_delay_cycles(m):
        # convert delay times into number of cycles
        delay_cycles = (
            (
                np.array(m.params['delays_before_jumps'], dtype = np.float32) 
                - m.params['minimal_delay_time']
            ) 
            / m.params['delay_clock_cycle_time'] 
            + m.params['minimal_delay_cycles']
        )
        
        if np.min(delay_cycles) < m.params['minimal_delay_cycles']:
            raise Exception("Desired delay times are too short")

        # round delay times (not keeping in mind cumulative errors)
        m.params['delay_table'] = np.rint(delay_cycles).astype(np.int32)

def group_seq_elems(combined_seq,combined_list_of_elements):
    jumps_or_go_tos = []
    sequence_overview = []
    pulse_array = []
    current_group_pulses = np.array([]).reshape(0,5)
    time = 0
    first_group_elem_name = None 
    trigger_wait = False
    
    for seq_elem in combined_seq.elements:
        
        if seq_elem['goto_target'] != None: # End of group!
                jumps_or_go_tos.append(seq_elem['goto_target'])
            
        if seq_elem['jump_target'] != None: # End of group!
                jumps_or_go_tos.append(seq_elem['jump_target'])
    
    for seq_elem in combined_seq.elements:
        
        elem = pulse_sim.get_pulse_elem_for_seq_element(seq_elem,combined_list_of_elements)

        current_elem_pulses = pulse_sim.get_seq_element_pulses(elem,verbose = False)
        reps = int(seq_elem['repetitions'])
        
        if seq_elem['goto_target'] != None or seq_elem['jump_target'] != None:
            reps = 1 # Dont repeat an element if you can jump out of it.
        
        if seq_elem['trigger_wait'] != False:
            time = 0

        pulses = np.array([]).reshape(0,5)
            
        for x in range(reps):
            if np.size(current_elem_pulses):
                temp_pulses = np.copy(current_elem_pulses)
                temp_pulses[:,0] += time
                pulses = np.vstack([pulses,temp_pulses])
            time += elem.length()
            
        if first_group_elem_name == None:
            first_group_elem_name = seq_elem['name']
        
        start_of_group = False
        end_of_group = False
        
        if seq_elem['trigger_wait'] != False or seq_elem['name'] in jumps_or_go_tos: # Start of new group!
            if np.size(current_group_pulses):
                sequence_overview.append({'name' : first_group_elem_name,\
                               'trigger_wait' : int(trigger_wait),\
                               'goto_target' : str(seq_elem['goto_target']),\
                               'jump_target' : str(seq_elem['jump_target']), 'final_time' : float(time)}) 
                pulse_array.append(current_group_pulses)
            first_group_elem_name = seq_elem['name']
            trigger_wait = seq_elem['trigger_wait']
            current_group_pulses = pulses
            
            start_of_group = True
         
        if seq_elem['goto_target'] != None or seq_elem['jump_target'] != None:
            end_of_group = True
            
            if not(start_of_group): current_group_pulses = np.vstack([current_group_pulses,pulses])
            sequence_overview.append({'name' : first_group_elem_name,\
                               'trigger_wait' : int(trigger_wait),\
                               'goto_target' : str(seq_elem['goto_target']),\
                               'jump_target' : str(seq_elem['jump_target']), 'final_time' : float(time)}) 
            pulse_array.append(current_group_pulses) 
            time = 0
            first_group_elem_name = None
            trigger_wait = False
            current_group_pulses = np.array([]).reshape(0,5)
        elif end_of_group == False and start_of_group == False:
            current_group_pulses = np.vstack([current_group_pulses,pulses])
            
    
    if np.size(current_group_pulses):
                sequence_overview.append({'name' : first_group_elem_name,\
                               'trigger_wait' : int(trigger_wait),\
                               'goto_target' : str(seq_elem['goto_target']),\
                               'jump_target' : str(seq_elem['jump_target']), 'final_time' : float(time)}) 
                pulse_array.append(current_group_pulses)

    return [sequence_overview,pulse_array]

if __name__ == '__main__':

    # hahn_echo_with_djump("VariableDelay_HahnEcho_2T_" + name + "_DJUMP", 
    # debug = True,
    # upload = True,
    # old_school = False,
    # range_start = 0e-6,
    # range_end = 10e-6,
    # run_msmt = True)

    # jitter_timings("SquarePulse_Jitter_Timings", debug = True, upload = True, old_school = False, run_msmt = True)
    
    # amp_rng = 0.15
    # amp_pts = 16
    # pi_amps = 0.650 + np.linspace(-amp_rng, amp_rng, amp_pts)

    # for amp in pi_amps:
    #     init = False if amp != pi_amps[0] else True
    #     random_XY_pulsar("Random XY pulsar", debug = False, upload = True, run_msmt = True, hermite_amp = amp, init_tables = init)

    random_XY_pulsar("Random XY pulsar", debug = False, upload = True, run_msmt = False, hermite_amp = 0.67, init_tables = False)