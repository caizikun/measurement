from measurement.lib.pulsar import pulse, pulselib, element, pulsar, eom_pulses
import qt
import numpy as np


def pulse_defs_lt4(msmt):

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

    if msmt.params['square_MW_pulses']:
        msmt.MW_pi = pulselib.MW_pulse('Square pi-pulse',
                        MW_channel='MW_Imod',
                        PM_channel='MW_pulsemod',
                        second_MW_channel='MW_Qmod', 
                        amplitude = msmt.params['MW_pi_amp'],
                        length = msmt.params['MW_pi_duration'],
                        PM_risetime = msmt.params['MW_pulse_mod_risetime'])
       
        msmt.MW_pi2 = pulselib.MW_pulse('Square pi/2-pulse',
                        MW_channel='MW_Imod',
                        PM_channel='MW_pulsemod',
                        second_MW_channel='MW_Qmod', 
                        amplitude = msmt.params['MW_pi2_amp'],
                        length = msmt.params['MW_pi2_duration'],
                        PM_risetime = msmt.params['MW_pulse_mod_risetime'])

        msmt.MW_first_pi2 = pulselib.MW_pulse('Square pi/2-pulse',
                        MW_channel='MW_Imod',
                        PM_channel='MW_pulsemod',
                        second_MW_channel='MW_Qmod', 
                        amplitude = msmt.params['MW_pi2_amp'] + msmt.params['MW_BellStateOffset'],
                        length = msmt.params['MW_pi2_duration'],
                        PM_risetime = msmt.params['MW_pulse_mod_risetime'])

        msmt.MW_RND_I = pulselib.MW_pulse('Square RND-pulse-I',
                        MW_channel='MW_Imod',
                        PM_channel='MW_pulsemod',
                        amplitude = msmt.params['MW_RND_amp_I'],
                        length = msmt.params['MW_RND_duration_I'],
                        PM_risetime = msmt.params['MW_pulse_mod_risetime'])
        msmt.MW_RND_Q = pulselib.MW_pulse('Square RND-pulse-Q',
                        MW_channel='MW_Qmod',
                        PM_channel='MW_pulsemod',
                        amplitude = msmt.params['MW_RND_amp_Q'],
                        length = msmt.params['MW_RND_duration_Q'],
                        PM_risetime = msmt.params['MW_pulse_mod_risetime'])
    else:

        
        msmt.MW_pi = pulselib.HermitePulse_Envelope('Hermite pi-pulse',
                         MW_channel='MW_Imod', 
                         PM_channel='MW_pulsemod',
                         second_MW_channel= 'MW_Qmod',
                         amplitude = msmt.params['MW_pi_amp'],
                         length = msmt.params['MW_pi_duration'],
                         PM_risetime = msmt.params['MW_pulse_mod_risetime'],
                         pi2_pulse = False)
        msmt.MW_pi2 = pulselib.HermitePulse_Envelope('Hermite pi/2-pulse',
                         MW_channel='MW_Imod',
                         PM_channel='MW_pulsemod',
                         second_MW_channel='MW_Qmod',
                         amplitude = msmt.params['MW_pi2_amp'],
                         length = msmt.params['MW_pi2_duration'],
                         PM_risetime = msmt.params['MW_pulse_mod_risetime'],
                         pi2_pulse = True)
        msmt.MW_first_pi2 = pulselib.HermitePulse_Envelope('Hermite pi/2-pulse',
                        MW_channel='MW_Imod',
                        PM_channel='MW_pulsemod',
                        second_MW_channel='MW_Qmod',
                        amplitude = msmt.params['MW_pi2_amp'] + msmt.params['MW_BellStateOffset'],
                        length = msmt.params['MW_pi2_duration'],
                        PM_risetime = msmt.params['MW_pulse_mod_risetime'],
                        pi2_pulse = True)
        msmt.MW_RND_I = pulselib.HermitePulse_Envelope('Hermite RND-pulse-I',
                        MW_channel='MW_Imod',
                        PM_channel='MW_pulsemod',
                        amplitude = msmt.params['MW_RND_amp_I'],
                        length = msmt.params['MW_RND_duration_I'],
                        PM_risetime = msmt.params['MW_pulse_mod_risetime'],
                        pi2_pulse = msmt.params['MW_RND_I_ispi2'])
        msmt.MW_RND_Q = pulselib.HermitePulse_Envelope('Hermite RND-pulse-Q',
                        MW_channel='MW_Qmod',
                        PM_channel='MW_pulsemod',
                        amplitude = msmt.params['MW_RND_amp_Q'],
                        length = msmt.params['MW_RND_duration_Q'],
                        PM_risetime = msmt.params['MW_pulse_mod_risetime'],
                        pi2_pulse = msmt.params['MW_RND_Q_ispi2'])

    msmt.eom_pulse = eom_pulses.OriginalEOMAOMPulse('Eom Aom Pulse', 
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


    msmt.RND_sample_hold_pulse = pulse.SquarePulse(channel = 'RND_halt', amplitude = 2.0, 
                                    length = msmt.params['RND_duration'])

    ### synchronizing, etc
    msmt.adwin_trigger_pulse = pulse.SquarePulse(channel = 'adwin_sync',
        length = 5e-6, amplitude = 2) 
    msmt.adwin_success_pulse = pulse.SquarePulse(channel = 'adwin_success_trigger',
        length = 5e-6, amplitude = 2) 

    msmt.sync = pulse.SquarePulse(channel = 'sync', length = 50e-9, amplitude = 1.0)
    msmt.SP_pulse = pulse.SquarePulse(channel = 'AOM_Newfocus', amplitude = 1.0)
    msmt.RO_pulse = pulse.SquarePulse(channel = 'EOM_AOM_Matisse', amplitude = 0.0)
    msmt.yellow_pulse = pulse.SquarePulse(channel = 'AOM_Yellow', amplitude = 1.0)

    msmt.plu_gate = pulse.SquarePulse(channel = 'plu_sync', amplitude = 0.0, 
                                    length = msmt.params['PLU_gate_duration'])

    return True

def pulse_defs_lt3(msmt):

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
    if msmt.params['square_MW_pulses']:
        msmt.MW_pi = pulselib.MW_pulse('Square pi-pulse',
                        MW_channel='MW_Imod',
                        PM_channel='MW_pulsemod',
                        second_MW_channel='MW_Qmod', 
                        amplitude = msmt.params['MW_pi_amp'],
                        length = msmt.params['MW_pi_duration'],
                        PM_risetime = msmt.params['MW_pulse_mod_risetime'],)
        msmt.MW_pi2 = pulselib.MW_pulse('Square pi2-pulse',
                        MW_channel='MW_Imod',
                        second_MW_channel='MW_Qmod', 
                        PM_channel='MW_pulsemod',
                        amplitude = msmt.params['MW_pi2_amp'], 
                        length = msmt.params['MW_pi2_duration'],
                        PM_risetime = msmt.params['MW_pulse_mod_risetime'])
        msmt.MW_first_pi2 = pulselib.MW_pulse('Square pi/2-pulse',
                        MW_channel='MW_Imod',
                        PM_channel='MW_pulsemod',
                        second_MW_channel='MW_Qmod', 
                        amplitude = msmt.params['MW_pi2_amp']+msmt.params['MW_BellStateOffset'],
                        length = msmt.params['MW_pi2_duration'],
                        PM_risetime = msmt.params['MW_pulse_mod_risetime'])
        msmt.MW_RND_I = pulselib.MW_pulse('Square RND0-pulse',
                        MW_channel='MW_Imod',
                        PM_channel='MW_pulsemod',
                        amplitude = msmt.params['MW_RND_amp_I'],
                        length = msmt.params['MW_RND_duration_I'],
                        PM_risetime = msmt.params['MW_pulse_mod_risetime'])
        msmt.MW_RND_Q = pulselib.MW_pulse('Square RND1-pulse',
                        MW_channel='MW_Qmod',
                        PM_channel='MW_pulsemod',
                        amplitude = msmt.params['MW_RND_amp_Q'],
                        length = msmt.params['MW_RND_duration_Q'],
                        PM_risetime = msmt.params['MW_pulse_mod_risetime'])
    else:

        msmt.MW_pi = pulselib.HermitePulse_Envelope('Hermite pi-pulse',
                        MW_channel='MW_Imod',
                        PM_channel='MW_pulsemod',
                        second_MW_channel='MW_Qmod', 
                        amplitude = msmt.params['MW_pi_amp'],
                        length = msmt.params['MW_pi_duration'],
                        PM_risetime = msmt.params['MW_pulse_mod_risetime'],
                        pi2_pulse = False)
        msmt.MW_pi2 = pulselib.HermitePulse_Envelope('Hermite pi2-pulse',
                        MW_channel='MW_Imod',
                        second_MW_channel='MW_Qmod', 
                        PM_channel='MW_pulsemod',
                        amplitude = msmt.params['MW_pi2_amp'], 
                        length = msmt.params['MW_pi2_duration'],
                        PM_risetime = msmt.params['MW_pulse_mod_risetime'],
                        pi2_pulse = True)
        msmt.MW_first_pi2 = pulselib.HermitePulse_Envelope('Hermite pi/2-pulse',
                        MW_channel='MW_Imod',
                        PM_channel='MW_pulsemod',
                        second_MW_channel='MW_Qmod', 
                        amplitude = msmt.params['MW_pi2_amp']+msmt.params['MW_BellStateOffset'],
                        length = msmt.params['MW_pi2_duration'],
                        PM_risetime = msmt.params['MW_pulse_mod_risetime'],
                        pi2_pulse = True)
        msmt.MW_RND_I = pulselib.HermitePulse_Envelope('Hermite RND0-pulse',
                        MW_channel='MW_Imod',
                        PM_channel='MW_pulsemod',
                        amplitude = msmt.params['MW_RND_amp_I'],
                        length = msmt.params['MW_RND_duration_I'],
                        PM_risetime = msmt.params['MW_pulse_mod_risetime'],
                        pi2_pulse = msmt.params['MW_RND_I_ispi2'])
        msmt.MW_RND_Q = pulselib.HermitePulse_Envelope('Hermite RND1-pulse',
                        MW_channel='MW_Qmod',
                        PM_channel='MW_pulsemod',
                        amplitude = msmt.params['MW_RND_amp_Q'],
                        length = msmt.params['MW_RND_duration_Q'],
                        PM_risetime = msmt.params['MW_pulse_mod_risetime'],
                        pi2_pulse = msmt.params['MW_RND_Q_ispi2'])

    msmt.eom_pulse = eom_pulses.OriginalEOMAOMPulse('Eom Aom Pulse', 
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

    msmt.RND_sample_hold_pulse = pulse.SquarePulse(channel = 'RND_halt', amplitude = 2.0, 
                                    length = msmt.params['RND_duration'])

    ### synchronizing, etc
    msmt.adwin_trigger_pulse = pulse.SquarePulse(channel = 'adwin_sync',
        length = 5e-6, amplitude = 2) 
    msmt.adwin_success_pulse = pulse.SquarePulse(channel = 'adwin_success_trigger',
        length = 5e-6, amplitude = 2) 
    msmt.sync = pulse.SquarePulse(channel = 'sync', length = 50e-9, amplitude = 1.0)

    #msmt.SP_pulse = pulse.SquarePulse(channel = 'EOM_AOM_Matisse', amplitude = 1.)
    msmt.SP_pulse = pulse.SquarePulse(channel = 'AOM_Newfocus', amplitude = 1.0)
    #msmt.RO_pulse = pulse.SquarePulse(channel = 'AOM_Newfocus', amplitude = 1.0)
    msmt.RO_pulse = pulse.SquarePulse(channel = 'EOM_AOM_Matisse', amplitude = 1.)
    msmt.yellow_pulse = pulse.SquarePulse(channel = 'AOM_Yellow', amplitude = 1.0)

    msmt.plu_gate = pulse.SquarePulse(channel = 'plu_sync', amplitude = 1.0, 
                                    length = msmt.params['PLU_gate_duration'])

    return True

## single elements
def _lt4_sequence_start_element(msmt):
    """
    first element of a two-setup sequence. Sends a trigger to AWG lt3
    """
    e = element.Element('LDE_start', pulsar = qt.pulsar)
    e.append(msmt.T_sync)
    ref_p=e.append(msmt.sync)
    e.add(pulse.cp(msmt.T_sync, length=msmt.params['AWG_wait_for_lt3_start']),
        refpulse=ref_p,
        refpoint='start'
        )
    ref_p=e.add(pulse.cp(msmt.plu_gate, length=50e-9), refpulse=ref_p, start=100e-9)
    ref_p=e.add(pulse.cp(msmt.plu_gate, length=50e-9), refpulse=ref_p, start=50e-9)
    ref_p=e.add(pulse.cp(msmt.plu_gate, length=50e-9), refpulse=ref_p, start=50e-9)
    ref_p=e.add(pulse.cp(msmt.plu_gate, length=50e-9), refpulse=ref_p, start=50e-9)
    return e

def _lt3_sequence_start_element(msmt):
    """
    first element of a two-setup sequence. Sends waits an additional time after receiving the trigger from lt4, before starting lde
    """
    e = element.Element('lt3_start', pulsar = qt.pulsar)
    e.append(pulse.cp(msmt.SP_pulse, length=1e-6, amplitude = 0))
    return e

def _lt3_sequence_finished_element(msmt):
    """
    last element of a two-setup sequence. Sends a trigger to ADwin lt3.
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

def _lt3_entanglement_event_element(msmt):
    
    e= element.Element('Entanglement trigger', pulsar=qt.pulsar)

    e.append(pulse.cp(msmt.TIQ, length=1e-6))
    e.append(msmt.adwin_success_pulse)
    return e

def _lt4_entanglement_event_element(msmt):
    
    e= element.Element('Entanglement event element', pulsar=qt.pulsar)

    e.append(pulse.cp(msmt.TIQ, length=1e-6))
    e.append(msmt.adwin_success_pulse)
    return e

def _lt4_sequence_finished_element(msmt):
    """
    last element of a two-setup sequence. Sends a trigger to ADwin lt4.
    """
    e = element.Element('LDE_finished', pulsar = qt.pulsar)
    e.append(msmt.TIQ)
    e.append(msmt.adwin_trigger_pulse)
    return e

def _lt4_wait_1us_element(msmt):
    """
    A 1us empty element we can use to replace 'real' elements for certain modes.
    """
    e = element.Element('wait_1_us', 
        pulsar = qt.pulsar)
    e.append(pulse.cp(msmt.T, length=1e-6))
    return e

def _LDE_element(msmt, **kw):
    """
    This element contains the LDE part, i.e., spin pumping and MW pulses
    for the lt4 NV and the optical pi pulses as well as all the markers for HH and PLU.
    """

    # variable parameters
    name = kw.pop('name', 'LDE_element')
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
            amplitude = 0., 
            length = msmt.joint_params['initial_delay']),
        name = 'initial_delay')
    
    if True:
        e.add(pulse.cp(msmt.SP_pulse, 
            length = msmt.params['LDE_SP_duration'], 
            amplitude = 1), name = 'spinpumping', refpulse = 'initial_delay', start= 250e-9)
    else:
        number_of_pulses=50
        for i in range(number_of_pulses):
            name = 'spinpumping {}'.format(i+1) if i<(number_of_pulses-1) else ('spinpumping')
            refpulse = 'spinpumping {}'.format(i) if i > 0 else ('initial_delay')
            start = msmt.joint_params['opt_pulse_separation'] if i > 0 else msmt.params['opt_pulse_start']
            refpoint = 'start' if i > 0 else 'end'
            e.add(pulse.cp(msmt.SP_pulse, 
            length = 50.0e-9,#msmt.params['LDE_SP_duration'], 
             amplitude = 1.), start= (5+i)*1e-9 if i>0 else 500.0e-9, refpoint='end', name = name, refpulse = refpulse)

    if msmt.params['LDE_yellow_duration'] > 0.:
        e.add(pulse.cp(msmt.yellow_pulse, 
                length = msmt.params['LDE_yellow_duration'], 
                amplitude = 1.0), 
            name = 'yellow_pumping', 
            refpulse = 'initial_delay')

    # if msmt.params['Spin_Init_MW'] == True:
    #     e.add(msmt.MW_pi, 
    #         start = msmt.params['MW_PiInit_Delay'],
    #         refpulse = 'spinpumping',
    #         refpoint = 'end', 
    #         refpoint_new = 'end', 
    #         name='spin_init_MW')

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
        refpulse = 'opt pi {}'.format(i) if i > 0 else ('spin_init_MW' if msmt.params['Spin_Init_MW'] == True else 'spinpumping')
        start = msmt.joint_params['opt_pulse_separation'] if i > 0 else msmt.params['opt_pulse_start']
        refpoint = 'start' if i > 0 else 'end'

        e.add(eom_pulse,        
            name = name, 
            start = start,
            refpulse = refpulse,
            refpoint = refpoint)

    if msmt.params['Spin_Init_MW'] == True:
        e.add(msmt.MW_pi, 
            start = msmt.params['MW_PiInit_Delay'],
            refpulse = 'opt pi {}'.format(msmt.joint_params['opt_pi_pulses']),
            refpoint = 'end', 
            refpoint_new = 'end', 
            name='spin_init_MW')
    #4 MW pi/2
    # if msmt.params['MW_during_LDE'] == 1:
    #     e.add(msmt.MW_first_pi2,
    #         start = -msmt.params['MW_opt_puls1_separation'],
    #         refpulse = 'opt pi 1', 
    #         refpoint = 'start', 
    #         refpoint_new = 'end',
    #         name = 'MW_BellAngle')
    #5 HHsync
    
    # #6 plugate 1
    # if msmt.params['plu_during_LDE'] == 1 :
    #     e.add(msmt.plu_gate, name = 'plu gate 1', 
    #         refpulse = 'opt pi 1',
    #         start = msmt.params['PLU_1_delay'])

    #8 MW pi 
    if msmt.joint_params['do_final_MW_rotation'] == 1:
        e.add(msmt.MW_pi, 
            start = msmt.params['MW_1_separation'],
            refpulse = 'opt pi 1',
            refpoint = 'end', 
            refpoint_new = 'end', 
            name='MW_pi')


    # #10 plugate 2
    # if msmt.params['plu_during_LDE'] == 1 :
    #     e.add(msmt.plu_gate, 
    #         name = 'plu gate 2',
    #         refpulse = 'opt pi {}'.format(msmt.joint_params['opt_pi_pulses']),
    #         start = msmt.params['PLU_2_delay']) 

    # #11 plugate 3
    # if msmt.params['plu_during_LDE'] == 1 :
    #     e.add(pulse.cp(msmt.plu_gate, 
    #             length = msmt.params['PLU_gate_3_duration']), 
    #         name = 'plu gate 3', 
    #         start = msmt.params['PLU_3_delay'], 
    #         refpulse = 'plu gate 2')
    
    # #12 plugate 4
    # if msmt.params['plu_during_LDE'] == 1 :
    #     e.add(msmt.plu_gate, name = 'plu gate 4', start = msmt.params['PLU_4_delay'],
    #             refpulse = 'plu gate 3')


    # # 14 RND generator HOLD OFF
    # if  msmt.joint_params['RND_during_LDE'] ==1  or ( msmt.joint_params['do_final_MW_rotation'] == 1 and msmt.joint_params['wait_for_1st_revival'] == 0 ):
    #     e.add(pulse.cp(msmt.RND_sample_hold_pulse,
    #                    amplitude = msmt.joint_params['RND_during_LDE']),
    #             start = msmt.joint_params['RND_start'],
    #             refpulse = 'initial_delay',
    #             name = 'RND')

    # 14 RND MW pulse
    # if msmt.params['MW_during_LDE'] == 1 and msmt.joint_params['wait_for_1st_revival'] == 0 and msmt.joint_params['do_final_MW_rotation'] == 1 :
    #     if msmt.joint_params['do_echo'] == 1:
    #         e.add(msmt.MW_RND_I, 
    #             start = msmt.params['MW_RND_wait'],
    #             refpulse = 'RND', 
    #             refpoint = 'end', 
    #             refpoint_new = 'start',
    #             name='MW_RND_0')
    #         e.add(msmt.MW_RND_Q, 
    #             start = msmt.params['MW_RND_wait'],
    #             refpulse = 'RND', 
    #             refpoint = 'end', 
    #             refpoint_new = 'start',
    #             name='MW_RND_1')
    #     else:
    #         e.add(msmt.MW_RND_I, 
    #             start = msmt.params['MW_1_separation'],
    #             refpulse = 'MW_pi', 
    #             refpoint = 'start', 
    #             refpoint_new = 'start',
    #             name='MW_RND_0')
    #         e.add(msmt.MW_RND_Q, 
    #             start = msmt.params['MW_1_separation'],
    #             refpulse = 'MW_pi', 
    #             refpoint = 'start', 
    #             refpoint_new = 'start',
    #             name='MW_RND_1')

    #15 RO
    if msmt.joint_params['RO_during_LDE'] == 1 and msmt.joint_params['wait_for_1st_revival'] == 0:
        refpulse = 'MW_pi' if (msmt.params['MW_during_LDE'] == 1 and msmt.joint_params['do_final_MW_rotation'] == 1) else 'opt pi {}'.format(msmt.joint_params['opt_pi_pulses'])
        #print 'RO voltage ', msmt.params['RO_voltage_AWG']
        e.add(pulse.cp(msmt.RO_pulse,
            amplitude = 0.3,
            length = msmt.joint_params['LDE_RO_duration']),
            start = msmt.params['RO_wait'],
            refpulse = 'initial_delay', 
            refpoint = 'end', 
            refpoint_new = 'start',
            name='RO')

    #13 Echo pulse
    # if msmt.params['MW_during_LDE'] == 1 and msmt.joint_params['wait_for_1st_revival'] == 0 and msmt.joint_params['do_echo'] == 1:
    #     ref_p_1 = e.pulses['MW_pi']
    #     ref_p_2 = e.pulses['MW_RND_0']
    #     #print 'RND MW start:', ref_p_2.effective_start()
    #     #calculate middle between the final pi/n pulse and the echo from the LDE pi/2+pi
    #     LDE_echo_point = ref_p_1.effective_start()+ msmt.params['MW_1_separation']
    #     expected_echo_time = (ref_p_2.effective_start()- LDE_echo_point)
    #     #print 'LDE_echo_point, expected_echo_time: ', LDE_echo_point, expected_echo_time
    #     noof_p = msmt.joint_params['DD_number_pi_pulses']
    #     index_j = np.linspace(noof_p-1, - noof_p+1, noof_p )
    #     for j in range(noof_p):
    #         e.add(pulse.cp(msmt.MW_pi,
    #                 amplitude=(1.)**(noof_p-j)*msmt.params['MW_pi_amp'],
    #                 ), 
    #             start = -expected_echo_time/(2.*noof_p)*(2*j+1) \
    #                 +msmt.params['free_precession_offset']*index_j[j]\
    #                 +msmt.params['echo_offset'],
    #             refpulse = 'MW_RND_0', 
    #             refpoint = 'start', 
    #             refpoint_new = 'center',
    #             name='MW_echo_pi_{}'.format(j))



    ############
    #print e.print_overview()
    e_len = e.length()
    #print 'SAMPLES', e.samples
    if e_len != msmt.joint_params['LDE_element_length']:
        raise Exception('LDE element "{}" has length {:.6e}, but specified length was {:.6e}. granularity issue?'.format(e.name, e_len, msmt.joint_params['LDE_element_length']))
    return e


def _1st_revival_RO(msmt, LDE_echo_point, **kw):

    name = kw.pop('name', '1st_revival_RO')

    ###
    e = element.Element(name, 
        pulsar = qt.pulsar, 
        global_time = True)  

    e.add(pulse.cp(msmt.SP_pulse, 
            amplitude = 0, 
            length = msmt.joint_params['initial_delay']),
        name = 'initial_delay')
 
    # 14 RND MW pulse
    if msmt.params['MW_during_LDE'] == 1 and msmt.joint_params['do_final_MW_rotation'] == 1:
        e.add(msmt.MW_RND_I, 
            #start = msmt.params['MW_RND_wait'],
            start = msmt.params['free_precession_time_1st_revival']-LDE_echo_point,
            refpulse = 'initial_delay',
            refpoint = 'start', 
            refpoint_new = 'start',
            name='MW_RND_0')
        e.add(msmt.MW_RND_Q, 
            start = msmt.params['free_precession_time_1st_revival']-LDE_echo_point,
            refpulse = 'initial_delay',
            refpoint = 'start', 
            refpoint_new = 'start',
            name='MW_RND_1')
    
    # 14 RND generator HOLD OFF
    if msmt.joint_params['RND_during_LDE'] == 1:
        #print 'RND_start', msmt.joint_params['RND_start']
        e.add(msmt.RND_sample_hold_pulse,
                start = -msmt.params['MW_RND_wait'],
                refpulse = 'MW_RND_0', 
                refpoint = 'start', 
                refpoint_new = 'end',
                name = 'RND')


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
    if msmt.params['MW_during_LDE'] == 1 and msmt.joint_params['do_echo'] == 1:
        for j in range(msmt.joint_params['DD_number_pi_pulses']):
            e.add(msmt.MW_pi, 
                start = -msmt.params['free_precession_time_1st_revival']/(2.*msmt.joint_params['DD_number_pi_pulses'])*(2*j+1)+msmt.params['echo_offset'],
                refpulse = 'MW_RND_0', 
                refpoint = 'start', 
                refpoint_new = 'center',
                name='MW_echo_pi_{}'.format(j))

    return e