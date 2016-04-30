'''
Generates AWG elements from locally stored parameters for the purifcation project.
Specifically contains the following output possiblities:
    - Barrett & Kok Entangling element
    - Single Optical Pi pulse entangling element

This setting is changed by merely adapting the local parameters adequately.

Norbert Kalb 2016
'''

from measurement.lib.pulsar import pulse, pulselib, element, pulsar, eom_pulses
import measurement.lib.measurement2.adwin_ssro.pulse_select as ps
import qt
import numpy as np

setup = qt.current_setup

### create pulses
def _create_mw_pulses(msmt,Gate):
    Gate.mw_X = ps.X_pulse(msmt)
    Gate.mw_pi2 = ps.Xpi2_pulse(msmt)
    Gate.mw_mpi2 = ps.mXpi2_pulse(msmt)
    Gate.mw_first_pulse = pulse.cp(ps.Xpi2_pulse(msmt),amplitude = msmt.params['mw_first_pulse_amp'],length = msmt.params['mw_first_pulse_length'])


def _create_laser_pulses(msmt,Gate):
    Gate.AWG_repump = pulse.SquarePulse(channel ='AOM_Newfocus',name = 'repump',
            length = msmt.params['LDE_SP_duration'],amplitude = 1.)

    Gate.eom_pulse =     msmt.eom_pulse = eom_pulses.OriginalEOMAOMPulse('Eom_Aom_Pulse', 
                    eom_channel = 'EOM_Matisse',
                    aom_channel = 'EOM_AOM_Matisse',
                    eom_pulse_duration      = msmt.params['eom_pulse_duration'],
                    eom_off_duration        = msmt.params['eom_off_duration'],
                    eom_off_amplitude       = msmt.params['eom_off_amplitude'],
                    eom_pulse_amplitude     = msmt.params['eom_pulse_amplitude'],
                    eom_overshoot_duration1 = msmt.params['eom_overshoot_duration1'],
                    eom_overshoot1          = msmt.params['eom_overshoot1'],
                    eom_overshoot_duration2 = msmt.params['eom_overshoot_duration2'],
                    eom_overshoot2          = msmt.params['eom_overshoot2'],
                    aom_risetime            = msmt.params['aom_risetime'],
                    aom_amplitude           = msmt.params['aom_amplitude'])




def _create_syncs_and_triggers(msmt,Gate):
    
    Gate.HHsync = pulse.SquarePulse(channel = 'sync', length = 50e-9, amplitude = 1.0)

    if setup == 'lt1' or setup == 'lt4': #XXX get rid of LT1 later on.
        plu_amp = 1.0
    else:
        plu_amp = 0.0
    Gate.plu_gate = pulse.SquarePulse(channel = 'plu_sync', amplitude = plu_amp, 
                                    length = msmt.params['PLU_gate_duration'])

    Gate.adwin_trigger_pulse = pulse.SquarePulse(channel = 'adwin_sync',
        length = 5e-6, amplitude = 2) 
    Gate.adwin_count_pulse = pulse.SquarePulse(channel = 'adwin_count',
        length = 5e-6, amplitude = 2) 

def _create_wait_times(Gate):
    Gate.TIQ = pulse.SquarePulse(channel = 'MW_Imod',length=2e-6)
    Gate.T = pulse.SquarePulse(channel='MW_pulsemod',
        length = 50e-9, amplitude = 0)
    Gate.T_sync = pulse.SquarePulse(channel='sync',
        length = 50e-9, amplitude = 0)



### the LDE element
def generate_LDE_elt(msmt,Gate, **kw):
    '''
    returns the full LDE gate object with correctly ordered LDE element(s) 
    (multiple elements are attributed to the gate object for two-setup sequences for communication)
    
    Input: The LDE/Gate object (see DD_2.py)

    Output: None
    '''
    
    ### necessary parameters for further processing become attributes
    Gate.scheme = 'LDE'

    ### pulse definitions
    _create_mw_pulses(msmt,Gate)
    _create_laser_pulses(msmt,Gate)
    _create_syncs_and_triggers(msmt,Gate)
    _create_wait_times(Gate)


    ### create element
    e = element.Element(Gate.name, pulsar = qt.pulsar, global_time=True)

    e.add(pulse.cp(Gate.AWG_repump,
                    amplitude = 0,
                    length = msmt.joint_params['LDE_element_length']
                    )
            )

    ##

    # 1 SP
    e.add(pulse.cp(Gate.AWG_repump, 
        amplitude = 0, 
        length = msmt.joint_params['initial_delay']),
    name = 'initial_delay')

    e.add(pulse.cp( Gate.AWG_repump,
                    length          = msmt.params['LDE_SP_duration'], 
                    amplitude       = 1.0), 
                    name            = 'spinpumping', 
                    refpulse        = 'initial_delay')

    ### add the option to plug in a yellow laser pulse during spin pumping. not yet considered

    ### 2 syncs

    # 2a HH sync
    if msmt.params['sync_during_LDE'] == 1 :
        e.add(Gate.HHsync,
            refpulse = 'initial_delay')

    # 2b
    e.add(Gate.adwin_count_pulse,
        refpulse = 'initial_delay')
    #3 MW pulses
    if msmt.params['MW_during_LDE'] == 1 :
        
        # print 'this is the x pulse start'
        # x_start = msmt.joint_params['LDE_element_length']-msmt.joint_params['initial_delay']-(msmt.params['LDE_decouple_time']-msmt.params['average_repump_time']-msmt.params['SP_AOM_turn_on_delay'])
        # print x_start
        # print msmt.joint_params['LDE_element_length'] - x_start

        # MW pi pulse
        e.add(Gate.mw_X,
            start           = msmt.joint_params['LDE_element_length']-msmt.joint_params['initial_delay']-(msmt.params['LDE_decouple_time']-msmt.params['average_repump_time']),
            refpulse        = 'initial_delay',#'MW_Theta',
            refpoint        = 'end',#'end',
            refpoint_new    = 'center',#'end',
            name            = 'MW_pi')

        #mw pi/2 pulse or 'theta'
        e.add(Gate.mw_first_pulse,
            start           = -msmt.params['LDE_decouple_time'],
            refpulse        = 'MW_pi',#'opt pi 1', 
            refpoint        = 'center', 
            refpoint_new    = 'center',
            name            = 'MW_Theta')

        #final MW RO rotation
        if msmt.joint_params['do_final_mw_LDE'] == 1:
            e.add(pulse.cp(Gate.mw_pi2,
                phase           = msmt.joint_params['LDE_final_mw_phase']),
                start           = msmt.params['LDE_decouple_time'],
                refpulse        = 'MW_pi',
                refpoint        = 'start',
                refpoint_new    = 'start',
                name            = 'MW_RO_rotation')

    #4 opt. pi pulses
    for i in range(msmt.joint_params['opt_pi_pulses']):
        name = 'opt pi {}'.format(i+1)
        refpulse = 'opt pi {}'.format(i) if i > 0 else 'MW_Theta'
        start = msmt.joint_params['opt_pulse_separation'] if i > 0 else msmt.params['MW_opt_puls1_separation']
        refpoint = 'start' if i > 0 else 'end'

        e.add(Gate.eom_pulse,        
            name = name,
            start = start,
            refpulse = refpulse,
            refpoint = refpoint,)


    #5 Plu gates
    if msmt.params['PLU_during_LDE'] == 1 :
        e.add(Gate.plu_gate, name = 'plu gate 1', 
            refpulse = 'opt pi 1',
            start = msmt.params['PLU_1_delay'])

        plu_ref_name = 'plu gate 1'

        if msmt.joint_params['opt_pi_pulses'] > 1:
            e.add(Gate.plu_gate, 
                name = 'plu gate 2',
                refpulse = 'opt pi {}'.format(msmt.joint_params['opt_pi_pulses']),
                start = msmt.params['PLU_2_delay']) 
            plu_ref_name = 'plu gate 2'

        e.add(pulse.cp(Gate.plu_gate, 
                length = msmt.params['PLU_gate_3_duration']), 
            name = 'plu gate 3', 
            start = msmt.params['PLU_3_delay'], 
            refpulse = plu_ref_name)

        e.add(Gate.plu_gate, name = 'plu gate 4', start = msmt.params['PLU_4_delay'],
                refpulse = 'plu gate 3')
    

    # if msmt.joint_params['opt_pi_pulses'] > 1:
    ### then we should build up the MW pulses in a different way.


    Gate.reps = msmt.joint_params['LDE_attempts_before_CR']
    Gate.elements = [e]
    Gate.elements_duration = msmt.joint_params['LDE_element_length']

    # consistent?
    e_len = e.length()

    # uncomment for thourogh checks.
    # e.print_overview()

    if e_len != msmt.joint_params['LDE_element_length']:
        raise Exception('LDE element "{}" has length {:.6e}, but specified length was {:.6e}. granularity issue?'.format(e.name, e_len, msmt.joint_params['LDE_element_length']))


def _LDE_rephasing_elt(msmt,Gate):
    """waits the right amount of time after and LDE element for the 
    electron to rephase.
    """
    _create_wait_times(Gate)
    _create_syncs_and_triggers(msmt,Gate)
    e = element.Element(Gate.name, pulsar = qt.pulsar)

    wait_duration = msmt.params['average_repump_time']
    e.add(pulse.cp(Gate.T_sync, length=wait_duration))

    return e

### communication for start, finish & success elements / used in two setup sequences with mutual AWG triggering
def _master_sequence_start_element(msmt,Gate):
    """
    first element of a two-setup sequence. Sends a trigger to AWG lt3
    """
    _create_wait_times(Gate)
    _create_syncs_and_triggers(msmt,Gate)
    e = element.Element('LDE_start', pulsar = qt.pulsar)
    e.append(Gate.T_sync)
    ref_p=e.append(Gate.HHsync)
    e.add(pulse.cp(Gate.T_sync, length=msmt.params['AWG_wait_for_lt3_start']),
        refpulse=ref_p,
        refpoint='start'
        )
    ref_p=e.add(pulse.cp(Gate.plu_gate, length=50e-9), refpulse=ref_p, start=100e-9)
    ref_p=e.add(pulse.cp(Gate.plu_gate, length=50e-9), refpulse=ref_p, start=50e-9)
    ref_p=e.add(pulse.cp(Gate.plu_gate, length=50e-9), refpulse=ref_p, start=50e-9)
    ref_p=e.add(pulse.cp(Gate.plu_gate, length=50e-9), refpulse=ref_p, start=50e-9)
    return e

def _slave_sequence_start_element(Gate):
    """
    first element of a two-setup entangling sequence. Sends waits an additional time after receiving the trigger from lt4, before starting lde
    """
    e = element.Element('lt3_start', pulsar = qt.pulsar)
    e.append(pulse.cp(Gate.SP_pulse, length=1e-6, amplitude = 0))
    return e

def _lt3_entanglement_event_element(Gate):
    
    e= element.Element('Entanglement trigger', pulsar=qt.pulsar)

    e.append(pulse.cp(Gate.TIQ, length=1e-6))
    # e.append(Gate.adwin_success_pulse)
    return e

def _lt3_sequence_finished_element(Gate):
    """
    last element of a two-setup entangling sequence. Sends a trigger to ADwin lt3.
    """
    e = element.Element('LDE_finished', pulsar = qt.pulsar)
    e.append(Gate.TIQ)
    e.append(Gate.adwin_trigger_pulse)
    return e

def _lt4_entanglement_event_element(Gate):
    
    e= element.Element('Entanglement event element', pulsar=qt.pulsar)

    e.append(pulse.cp(Gate.TIQ, length=1e-6))
    # e.append(Gate.adwin_success_pulse)
    return e

def _lt4_sequence_finished_element(Gate):
    """
    last element of a two-setup entangling sequence. Sends a trigger to ADwin lt4.
    """
    e = element.Element('LDE_finished', pulsar = qt.pulsar)
    e.append(Gate.TIQ)
    e.append(Gate.adwin_trigger_pulse)
    return e

def _lt4_wait_1us_element(Gate):
    """
    A 1us empty element we can use to replace 'real' elements for certain modes.
    """
    e = element.Element('wait_1_us', 
        pulsar = qt.pulsar)
    e.append(pulse.cp(Gate.T, length=1e-6))
    return e

