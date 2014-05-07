from measurement.lib.pulsar import pulse, pulselib, element, pulsar, eom_pulses
import qt
import numpy as np


def pulse_defs_lt3(msmt):

    # a waiting pulse on the MW pulsemod channel
    msmt.T = pulse.SquarePulse(channel='MW_pulsemod',
        length = 50e-9, amplitude = 0)

    msmt.TIQ = pulse.SquarePulse(channel='MW_Imod',
        length = 10e-9, amplitude = 0)

    msmt.T_sync = pulse.SquarePulse(channel='sync',
        length = 50e-9, amplitude = 0)

    # some not yet specified pulse on the electron
    msmt.e_pulse = pulselib.MW_IQmod_pulse('MW pulse',
        I_channel = 'MW_Imod', 
        Q_channel = 'MW_Qmod',
        PM_channel = 'MW_pulsemod',
        PM_risetime = msmt.params['MW_pulse_mod_risetime'])

    msmt.CORPSE_pi = pulselib.MW_CORPSE_pulse('CORPSE pi-pulse',
        MW_channel = 'MW_Imod', 
        PM_channel = 'MW_pulsemod',
        second_MW_channel = 'MW_Qmod',
        PM_risetime = msmt.params['MW_pulse_mod_risetime'],
        amplitude = msmt.params['CORPSE_pi_amp'],
        rabi_frequency = msmt.params['CORPSE_rabi_frequency'],
        eff_rotation_angle = 180)
    msmt.CORPSE_pi2 = pulselib.MW_CORPSE_pulse('CORPSE pi2-pulse',
        MW_channel = 'MW_Imod', 
        PM_channel = 'MW_pulsemod',
        second_MW_channel = 'MW_Qmod',
        PM_risetime = msmt.params['MW_pulse_mod_risetime'],
        amplitude = msmt.params['CORPSE_pi2_amp'],
        rabi_frequency = msmt.params['CORPSE_rabi_frequency'],
        eff_rotation_angle = 90)
    msmt.CORPSE_RND0 = pulselib.MW_CORPSE_pulse('CORPSE pi2-pulse',
        MW_channel = 'MW_Imod', 
        PM_channel = 'MW_pulsemod',
        PM_risetime = msmt.params['MW_pulse_mod_risetime'],
        amplitude = msmt.params['CORPSE_RND_amp'],
        rabi_frequency = msmt.params['CORPSE_rabi_frequency'],
        eff_rotation_angle = msmt.params['RND_angle_0'])
    msmt.CORPSE_RND1 = pulselib.MW_CORPSE_pulse('CORPSE pi2-pulse',
        MW_channel = 'MW_Qmod', 
        PM_channel = 'MW_pulsemod',
        PM_risetime = msmt.params['MW_pulse_mod_risetime'],
        amplitude = msmt.params['CORPSE_RND_amp'],
        rabi_frequency = msmt.params['CORPSE_rabi_frequency'],
        eff_rotation_angle = msmt.params['RND_angle_1'])

    msmt.eom_pulse = eom_pulses.EOMAOMPulse('Eom Aom Pulse', 
                    eom_channel = 'EOM_Matisse',
                    aom_channel = 'EOM_AOM_Matisse')


    msmt.RND_halt_off_pulse = pulse.SquarePulse(channel = 'RND_halt', amplitude = -1.0, 
                                    length = msmt.params['RND_duration'])

    ### synchronizing, etc
    msmt.adwin_trigger_pulse = pulse.SquarePulse(channel = 'adwin_sync',
        length = 5e-6, amplitude = 2) 


    msmt.sync = pulse.SquarePulse(channel = 'sync', length = 50e-9, amplitude = 1.0)
    msmt.SP_pulse = pulse.SquarePulse(channel = 'AOM_Newfocus', amplitude = 1.0)
    msmt.RO_pulse = pulse.SquarePulse(channel = 'AOM_Matisse', amplitude = 0.0)
    msmt.yellow_pulse = pulse.SquarePulse(channel = 'AOM_Yellow', amplitude = 1.0)

    msmt.plu_gate = pulse.SquarePulse(channel = 'plu_sync', amplitude = 1.0, 
                                    length = msmt.params['PLU_gate_duration'])

    return True

def pulse_defs_lt1(msmt):

    # a waiting pulse on the MW pulsemod channel
    msmt.T = pulse.SquarePulse(channel='MW_pulsemod',
        length = 50e-9, amplitude = 0)

    msmt.TIQ = pulse.SquarePulse(channel='MW_Imod',
        length = 10e-9, amplitude = 0)

    # some not yet specified pulse on the electron
    msmt.e_pulse = pulselib.MW_IQmod_pulse('MW pulse',
        I_channel = 'MW_Imod', 
        Q_channel = 'MW_Qmod',
        PM_channel = 'MW_pulsemod',
        PM_risetime = msmt.params['MW_pulse_mod_risetime'])

    msmt.CORPSE_pi = pulselib.MW_CORPSE_pulse('CORPSE pi-pulse',
        MW_channel = 'MW_Imod', 
        PM_channel = 'MW_pulsemod',
        second_MW_channel = 'MW_Qmod',
        PM_risetime = msmt.params['MW_pulse_mod_risetime'],
        amplitude = msmt.params['CORPSE_pi_amp'],
        rabi_frequency = msmt.params['CORPSE_rabi_frequency'],
        eff_rotation_angle = 180)
    msmt.CORPSE_pi2 = pulselib.MW_CORPSE_pulse('CORPSE pi2-pulse',
        MW_channel = 'MW_Imod', 
        PM_channel = 'MW_pulsemod',
        second_MW_channel = 'MW_Qmod',
        PM_risetime = msmt.params['MW_pulse_mod_risetime'],
        amplitude = msmt.params['CORPSE_pi2_amp'],
        rabi_frequency = msmt.params['CORPSE_rabi_frequency'],
        eff_rotation_angle = 90)
    msmt.CORPSE_RND0 = pulselib.MW_CORPSE_pulse('CORPSE pi2-pulse',
        MW_channel = 'MW_Imod', 
        PM_channel = 'MW_pulsemod',
        PM_risetime = msmt.params['MW_pulse_mod_risetime'],
        amplitude = msmt.params['CORPSE_RND_amp'],
        rabi_frequency = msmt.params['CORPSE_rabi_frequency'],
        eff_rotation_angle = msmt.params['RND_angle_0'])
    msmt.CORPSE_RND1 = pulselib.MW_CORPSE_pulse('CORPSE pi2-pulse',
        MW_channel = 'MW_Qmod', 
        PM_channel = 'MW_pulsemod',
        PM_risetime = msmt.params['MW_pulse_mod_risetime'],
        amplitude = msmt.params['CORPSE_RND_amp'],
        rabi_frequency = msmt.params['CORPSE_rabi_frequency'],
        eff_rotation_angle = msmt.params['RND_angle_1'])

    msmt.eom_pulse = eom_pulses.EOMAOMPulse('Eom Aom Pulse', 
                    eom_channel = 'EOM_Matisse',
                    aom_channel = 'EOM_AOM_Matisse')

    msmt.RND_halt_off_pulse = pulse.SquarePulse(channel = 'RND_halt', amplitude = -1.0, 
                                    length = msmt.params['RND_duration'])

    ### synchronizing, etc
    msmt.adwin_trigger_pulse = pulse.SquarePulse(channel = 'adwin_sync',
        length = 5e-6, amplitude = 2) 
    msmt.adwin_success_pulse = pulse.SquarePulse(channel = 'adwin_success_trigger',
        length = 5e-6, amplitude = 2) 

    msmt.SP_pulse = pulse.SquarePulse(channel = 'AOM_Newfocus', amplitude = 1.0)
    msmt.RO_pulse = pulse.SquarePulse(channel = 'AOM_Matisse', amplitude = 0.0)
    msmt.yellow_pulse = pulse.SquarePulse(channel = 'AOM_Yellow', amplitude = 1.0)



    return True

## single elements
def _lt3_sequence_start_element(msmt):
    """
    first element of a two-setup sequence. Sends a trigger to AWG LT1
    """
    e = element.Element('LT3_start', pulsar = qt.pulsar)
    e.append(msmt.T_sync)
    e.append(msmt.sync)
    e.append(pulse.cp(msmt.T_sync, length=msmt.params['AWG_wait_for_lt1_start']))
    return e

def _sequence_finished_element(msmt):
    """
    last element of a two-setup sequence. Sends a trigger to ADwin LT3.
    """
    e = element.Element('LDE_finished', pulsar = qt.pulsar)
    e.append(msmt.TIQ)
    e.append(msmt.adwin_trigger_pulse)
    return e

def _dummy_element(msmt):
    """
    A 1us empty element we can use to replace 'real' elements for certain modes.
    """
    e = element.Element('Dummy', pulsar = qt.pulsar)
    e.append(pulse.cp(msmt.T_sync, length=msmt.joint_params['LDE_element_length']))
    return e

def _lt1_entanglement_event_element(msmt):
    
    e= element.Element('Entanglement trigger', pulsar=qt.pulsar)

    e.append(msmt.TIQ)
    e.append(msmt.adwin_success_pulse)

def _lt3_wait_1us_element(msmt):
    """
    A 1us empty element we can use to replace 'real' elements for certain modes.
    """
    e = element.Element('wait_1_us', 
        pulsar = qt.pulsar)
    e.append(pulse.cp(msmt.T, length=1e-6))
    return e

def _LDE_element(msmt, **kw):
    """
    This element contains the LDE part for LT3, i.e., spin pumping and MW pulses
    for the LT3 NV and the optical pi pulses as well as all the markers for HH and PLU.
    """

    # variable parameters
    name = kw.pop('name', 'LDE_LT3')
    eom_pulse = kw.pop('eom_pulse', msmt.eom_pulse)#pulse.cp(msmt.eom_aom_pulse, aom_on=msmt.params['eom_aom_on']))

    ###
    e = element.Element(name, 
        pulsar = qt.pulsar, 
        global_time = True)  
    
    e.add(pulse.cp(msmt.SP_pulse,
            amplitude = 0,
            length = msmt.joint_params['LDE_element_length']))
    
    #1 SP
    e.add(pulse.cp(msmt.SP_pulse, 
            amplitude = 0, 
            length = msmt.joint_params['initial_delay']), 
        name = 'initial_delay')
    
    e.add(pulse.cp(msmt.SP_pulse, 
            length = msmt.params['LDE_SP_duration'], 
            amplitude = 1.0), 
        name = 'spinpumping', 
        refpulse = 'initial_delay')
    if msmt.params['LDE_yellow_duration'] > 0.:
        e.add(pulse.cp(msmt.yellow_pulse, 
                length = msmt.params['LDE_yellow_duration'], 
                amplitude = 1.0), 
            name = 'yellow_pumping', 
            refpulse = 'initial_delay')

    if msmt.params['sync_during_LDE'] == 1 :
        e.add(msmt.sync,
            refpulse = 'initial_delay')
    # e.add(pulse.cp(msmt.yellow_pulse, 
    #         length = msmt.joint_params['LDE_SP_duration_yellow'], 
    #         amplitude = 1.0), 
    #     name = 'spinpumpingyellow', 
    #     refpulse = 'initial delay')

    for i in range(msmt.joint_params['opt_pi_pulses']):
        name = 'opt pi {}'.format(i+1)
        refpulse = 'opt pi {}'.format(i) if i > 0 else 'initial_delay'
        start = msmt.joint_params['opt_pulse_separation'] if i > 0 else msmt.params['opt_pulse_start']
        refpoint = 'start' if i > 0 else 'end'

        e.add(eom_pulse,        
            name = name, 
            start = start,
            refpulse = refpulse,
            refpoint = refpoint,)

    #4 MW pi/2
    if msmt.params['MW_during_LDE'] == 1 :
        e.add(msmt.CORPSE_pi2,
            start = -msmt.params['MW_opt_puls1_separation'],
            refpulse = 'opt pi 1', 
            refpoint = 'start', 
            refpoint_new = 'end',
            name = 'MW_pi_over_2')
    #5 HHsync
    
    #6 plugate 1
    if msmt.params['sync_during_LDE'] == 1 :
        e.add(msmt.plu_gate, name = 'plu gate 1', 
            refpulse = 'opt pi 1',
            start = msmt.params['PLU_1_delay'])

    #8 MW pi
    if msmt.params['MW_during_LDE'] == 1:
        e.add(msmt.CORPSE_pi, 
            start = msmt.params['MW_1_separation'],
            refpulse = 'MW_pi_over_2',
            refpoint = 'end', 
            refpoint_new = 'end', 
            name='MW_pi')
    
    #10 plugate 2
    if msmt.params['sync_during_LDE'] == 1 :
        e.add(msmt.plu_gate, 
            name = 'plu gate 2',
            refpulse = 'opt pi {}'.format(msmt.joint_params['opt_pi_pulses']),
            start = msmt.params['PLU_2_delay']) 

    #11 plugate 3
    if msmt.params['sync_during_LDE'] == 1 :
        e.add(pulse.cp(msmt.plu_gate, 
                length = msmt.params['PLU_gate_3_duration']), 
            name = 'plu gate 3', 
            start = msmt.params['PLU_3_delay'], 
            refpulse = 'plu gate 2')
    
    #12 plugate 4
    if msmt.params['sync_during_LDE'] == 1 :
        e.add(msmt.plu_gate, name = 'plu gate 4', start = msmt.params['PLU_4_delay'],
                refpulse = 'plu gate 3')

    # 14 RND generator HOLD OFF
    e.add(msmt.RND_halt_off_pulse,
            start = msmt.joint_params['RND_start'],
            refpulse = 'initial_delay',
            name = 'RND')

    # 14 RND MW pulse
    if msmt.params['MW_during_LDE'] == 1:
        e.add(msmt.CORPSE_RND0, 
            start = msmt.params['MW_RND_wait'],
            refpulse = 'RND', 
            refpoint = 'end', 
            refpoint_new = 'start',
            name='MW_RND_0')
        e.add(msmt.CORPSE_RND1, 
            start = msmt.params['MW_RND_wait'],
            refpulse = 'RND', 
            refpoint = 'end', 
            refpoint_new = 'start',
            name='MW_RND_1')
    #15 RO
    if msmt.joint_params['RO_during_LDE'] == 1:
        refpulse = 'MW_RND_0' if  msmt.params['MW_during_LDE'] == 1 else 'RND'
        e.add(pulse.cp(msmt.RO_pulse,
                amplitude = msmt.params['RO_voltage_AWG'],
                length = msmt.joint_params['LDE_RO_duration']),
            start = msmt.params['RO_wait'],
            refpulse = refpulse, 
            refpoint = 'end', 
            refpoint_new = 'start',
            name='RO')

    #13 Echo pulse
    if msmt.params['MW_during_LDE'] == 1:
        ref_p_1 = e.pulses['MW_pi']
        ref_p_2 = e.pulses['MW_RND_0']
        #calculate middle between the final pi/n pulse and the echo from the LDE pi/2+pi
        echo_start = -(ref_p_2.effective_start()-ref_p_1.effective_stop()-msmt.params['MW_1_separation'])/2.+msmt.params['MW_12_offset']
        #print 'echo start: ', echo_start
        e.add(msmt.CORPSE_pi, 
            start = echo_start,
            refpulse = 'MW_RND_0', 
            refpoint = 'start', 
            refpoint_new = 'end',
            name='MW_pi_2')

    ############
    #print e.print_overview()
    e_len = e.length()
    if e_len != msmt.joint_params['LDE_element_length']:
        raise Exception('LDE element "{}" has length {:.2e}, but specified length was {:.2e}. granularity issue?'.format(e.name, e_len, msmt.joint_params['LDE_element_length']))
    return e

def _lt3_first_pi2(msmt, **kw):
    init_ms1 = kw.pop('init_ms1', False)
    # around each pulse I make an element with length 1600e-9; 
    # the centre of the pulse is in the centre of the element.
    # this helps me to introduce the right waiting times, counting from centre of the pulses
    CORPSE_pi2_wait_length = msmt.params['CORPSE_pi2_wait_length'] #- (msmt.CORPSE_pi2.length - 2*msmt.params['MW_pulse_mod_risetime'])/2 

    first_pi2_elt = element.Element('first_pi2_elt', pulsar= qt.pulsar, 
        global_time = True, time_offset = 0.)

    first_pi2_elt.append(pulse.cp(msmt.T, length = 100e-9))
    
    if init_ms1:
        first_pi2_elt.append(pulse.cp(msmt.CORPSE_pi))
        first_pi2_elt.append(pulse.cp(msmt.T, length = 100e-9))
    
    first_pi2_elt.append(pulse.cp(msmt.CORPSE_pi2))
    first_pi2_elt.append(pulse.cp(msmt.T, 
        length =  CORPSE_pi2_wait_length))

    return first_pi2_elt

def _lt3_final_pi2(msmt, name, time_offset, **kw):
    extra_t_before_pi2 = kw.pop('extra_t_before_pi2', 0)
    CORPSE_pi2_phase = kw.pop('CORPSE_pi2_phase', 0)

    # around each pulse I make an element with length 1600e-9; 
    # the centre of the pulse is in the centre of the element.
    # this helps me to introduce the right waiting times, counting from centre of the pulses
    CORPSE_pi2_wait_length = msmt.params['CORPSE_pi2_wait_length'] #- (msmt.CORPSE_pi2.length - 2*msmt.params['MW_pulse_mod_risetime'])/2 

    second_pi2_elt = element.Element('second_pi2_elt-{}'.format(name), pulsar= qt.pulsar, 
        global_time = True, time_offset = time_offset)
    second_pi2_elt.append(pulse.cp(msmt.T, 
        length = CORPSE_pi2_wait_length + extra_t_before_pi2))
    second_pi2_elt.append(pulse.cp(msmt.CORPSE_pi2, 
        phase = CORPSE_pi2_phase))
    second_pi2_elt.append(pulse.cp(msmt.T, length =  100e-9 ))           

    return second_pi2_elt