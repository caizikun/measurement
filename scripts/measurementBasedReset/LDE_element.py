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
    Gate.mw_first_pulse = pulse.cp(ps.Xpi2_pulse(msmt),amplitude = msmt.params['mw_first_pulse_amp'],length = msmt.params['mw_first_pulse_length'],phase = msmt.params['mw_first_pulse_phase'])

    


    if hasattr(Gate,'first_pulse_is_pi2') and hasattr(Gate,'first_mw_pulse_phase'):
        if Gate.first_pulse_is_pi2:
            Gate.mw_first_pulse = pulse.cp(Gate.mw_pi2, phase = Gate.first_mw_pulse_phase)
    elif hasattr(Gate,'first_pulse_is_pi2'):
        if Gate.first_pulse_is_pi2:
            Gate.mw_first_pulse = pulse.cp(Gate.mw_pi2, phase = msmt.params['mw_first_pulse_phase'])

    if hasattr(Gate,'no_first_pulse'):
        if Gate.no_first_pulse:
            Gate.mw_first_pulse = pulse.cp(Gate.mw_X,amplitude = 0)

    if hasattr(Gate,'no_mw_pulse'):
        if Gate.no_mw_pulse:
            Gate.mw_first_pulse = pulse.cp(Gate.mw_X,amplitude = 0)
            Gate.mw_pi2 = pulse.cp(Gate.mw_X,amplitude = 0)
            Gate.mw_mpi2 = pulse.cp(Gate.mw_X,amplitude = 0)
            Gate.mw_X = pulse.cp(Gate.mw_X,amplitude = 0)

    ### only use this if you want two proper pi pulses.
    # Gate.mw_first_pulse = pulse.cp(ps.X_pulse(msmt))

def _create_laser_pulses(msmt,Gate):
    if 'msmt_based_reset' in msmt.params.parameters and msmt.params['msmt_based_reset'] == 1:
        Gate.AWG_repump = pulse.SquarePulse(channel ='AOM_Matisse',name = 'repump',
            length = msmt.params['LDE_SP_duration'],amplitude = 1.)
    else:
        Gate.AWG_repump = pulse.SquarePulse(channel ='AOM_Newfocus',name = 'repump',
            length = msmt.params['LDE_SP_duration'],amplitude = 1.)

    if (msmt.params['is_two_setup_experiment'] > 0 and msmt.current_setup == 'lt4'):
        ### The LT4 eom is not connected for this measurement. set amplitudes to 0.
        msmt.params['eom_off_amplitude'] = 0
        msmt.params['eom_pulse_amplitude'] = 0
        msmt.params['eom_overshoot1'] = 0
        msmt.params['eom_overshoot2'] = 0
        msmt.params['eom_overshoot2'] = 0

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
    
    #### hydraharp/timeharp synchronization
    if setup == 'lt4' and msmt.params['is_two_setup_experiment'] == 1:
        Gate.HHsync = pulse.SquarePulse(channel = 'sync', length = 50e-9, amplitude = 0)
    else:
        Gate.HHsync = pulse.SquarePulse(channel = 'sync', length = 50e-9, amplitude = 1.0)

    if setup == 'lt3':
        Gate.LT3HHsync = pulse.SquarePulse(channel = 'HHsync',length = 50e-9, amplitude = 1.0)


    # PLU comm
    if setup == 'lt3': #XXX get rid of LT1 later on.
        plu_amp = 1.0
    else:
        plu_amp = 0.0
    Gate.plu_gate = pulse.SquarePulse(channel = 'plu_sync', amplitude = plu_amp, 
                                    length = msmt.params['PLU_gate_duration'])

    # adwin comm
    Gate.adwin_trigger_pulse = pulse.SquarePulse(channel = 'adwin_sync',
        length = 1.5e-6, amplitude = 2) 
    Gate.adwin_count_pulse = pulse.SquarePulse(channel = 'adwin_count',
        length = 2.5e-6, amplitude = 2) 

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
                    start           = msmt.params['LDE_SP_delay'],
                    name            = 'spinpumping', 
                    refpulse        = 'initial_delay')

    ### add the option to plug in a yellow laser pulse during spin pumping. not yet considered

    ### 2 syncs

    # 2a HH sync


    if msmt.params['sync_during_LDE'] == 1 :
        e.add(Gate.HHsync,
            refpulse = 'initial_delay')

        ### one awg has to sync all yime-tagging devices.
        if setup == 'lt3' and msmt.params['is_two_setup_experiment'] > 0:
            # print 'i added the thing' 
            e.add(Gate.LT3HHsync,refpulse = 'initial_delay')

    # 2b adwin syncronization
    e.add(Gate.adwin_count_pulse,
        refpulse = 'initial_delay')


        
    if msmt.params['MW_during_LDE'] == 1: # and not ('LDE2' in Gate.name):
        
        # we choose to build the MW pulses up from the end of the element.
        # this is more convenient when trying to preserve the coherence of the electron over several elements
        # it however becomes more complicated from a programming point of view.
        
        # MW pi pulse
        if msmt.joint_params['do_final_mw_LDE'] == 1:
            # the last pulse is defined to come in 500 ns before the end of the LDE element
            e.add(pulse.cp(Gate.mw_pi2,
                phase           = msmt.joint_params['LDE_final_mw_phase'],
                amplitude       = msmt.params['LDE_final_mw_amplitude']),
                start           = msmt.joint_params['LDE_element_length']-msmt.joint_params['initial_delay']-2.5e-6,
                refpulse        = 'initial_delay',
                refpoint        = 'end',
                refpoint_new    = 'center',
                name            = 'MW_RO_rotation')


            e.add(Gate.mw_X,
                start           = -msmt.params['LDE_decouple_time'],
                refpulse        = 'MW_RO_rotation',#'MW_Theta',
                refpoint        = 'center',#'end',
                refpoint_new    = 'center',#'end',
                name            = 'MW_pi')

            #mw pi/2 pulse or 'theta'
            e.add(Gate.mw_first_pulse,
                start           = -msmt.params['LDE_decouple_time'],
                refpulse        = 'MW_pi',#'opt pi 1', 
                refpoint        = 'center', 
                refpoint_new    = 'center',
                name            = 'MW_Theta')


        else: # no final mw duration = no barret & kok
            e.add(Gate.mw_X,
                start           = msmt.joint_params['LDE_element_length']-msmt.joint_params['initial_delay']-(msmt.params['LDE_decouple_time']-msmt.params['average_repump_time']),
                refpulse        = 'initial_delay',#'MW_Theta',
                refpoint        = 'end',#'end',
                refpoint_new    = 'center',#'end',
                name            = 'MW_pi')

            #mw pi/2 pulse or 'theta'
            e.add(Gate.mw_first_pulse,
                start           = -msmt.params['LDE_decouple_time']-msmt.params['average_repump_time'],
                refpulse        = 'MW_pi',#'opt pi 1', 
                refpoint        = 'center', 
                refpoint_new    = 'center',
                name            = 'MW_Theta')




    ### we still need MW pulses (with zero amplitude) as a reference for the first optical pi pulse.
    else:
        # MW pi pulse
        e.add(pulse.cp(Gate.mw_X,amplitude=0),
            start           = msmt.joint_params['LDE_element_length']-msmt.joint_params['initial_delay']-(msmt.params['LDE_decouple_time']-msmt.params['average_repump_time']),
            refpulse        = 'initial_delay',#'MW_Theta',
            refpoint        = 'end',#'end',
            refpoint_new    = 'center',#'end',
            name            = 'MW_pi')

        #mw pi/2 pulse or 'theta'
        e.add(pulse.cp(Gate.mw_first_pulse,amplitude=0),
            start           = -msmt.params['LDE_decouple_time']-msmt.params['average_repump_time'],
            refpulse        = 'MW_pi',#'opt pi 1', 
            refpoint        = 'center', 
            refpoint_new    = 'center',
            name            = 'MW_Theta')

    #4 opt. pi pulses
    # print 'Nr of opt pi pulses', msmt.joint_params['opt_pi_pulses']

    if not ((msmt.params['LDE_1_is_init'] > 0) and 'LDE1' in Gate.name):

        if msmt.params['is_TPQI'] > 0:
            initial_reference = 'spinpumping'
            msmt.params['MW_opt_puls1_separation'] = 1e-6
        else:
            initial_reference = 'MW_Theta'
        for i in range(msmt.joint_params['opt_pi_pulses']):
            name = 'opt pi {}'.format(i+1)
            refpulse = 'opt pi {}'.format(i) if i > 0 else initial_reference
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

            e.add(pulse.cp(Gate.plu_gate, 
                    length = msmt.params['PLU_gate_3_duration']), 
                    name = 'plu gate 4', 
                    start = msmt.params['PLU_4_delay'],
                    refpulse = 'plu gate 3')
    
    #### gives a done trigger that has to be timed accordingly, is referenced to the PLU if the PLU is used by this setup.
    if Gate.is_final:
        ## one can time accurately if we use the plu during the experiment
        boolean = (setup == 'lt3' and msmt.params['PLU_during_LDE'] > 0)
        if  boolean and not ((msmt.params['LDE_1_is_init'] > 0) and 'LDE1' in Gate.name):
            e.add(Gate.adwin_trigger_pulse,
                start = 1000e-9, # should always come in later than the plu signal
                refpulse = 'plu gate 3')
        ## otherwise put the pulse at the end of the LDE sequence
        else:
            e.add(Gate.adwin_trigger_pulse,
                    start = msmt.joint_params['LDE_element_length'] - 2.6e-6,
                    refpulse = 'initial_delay')

   
    # Gate.reps = msmt.joint_params['LDE_attempts_before_CR']
    Gate.elements = [e]
    Gate.elements_duration = msmt.joint_params['LDE_element_length']

    # consistent?
    e_len = e.length()

    # uncomment for thourogh checks.
    # e.print_overview()

    # if e_len != msmt.joint_params['LDE_element_length']:
    #     raise Exception('LDE element "{}" has length {:.6e}, but specified length was {:.6e}. granularity issue?'.format(e.name, e_len, msmt.joint_params['LDE_element_length']))


def _LDE_rephasing_elt(msmt,Gate,forced_wait_duration = 0):
    """waits the right amount of time after and LDE element for the 
    electron to rephase.

    NOTE: after developing the purification code for several one realizes that we should distinguish between LDE 1 and LDE 2.
    The two elements are very different from each other.
    """
    _create_wait_times(Gate)
    _create_syncs_and_triggers(msmt,Gate)
    e = element.Element(Gate.name, pulsar = qt.pulsar)

    if forced_wait_duration == 0:

        ### we need to add some time for the following carbon gate to this rephasing element
        ### this time is tau_cut and is calculated below.
        c = str(msmt.params['carbon'])
        e_trans = msmt.params['electron_transition']

        #### for concatenating LDE with a longer entangling sequence, see also purify_slave, function carbon_swap_gate:
        if 'ElectronDD_tau' in msmt.params.to_dict().keys():
            tau = msmt.params['ElectronDD_tau']
        else:
            tau = msmt.params['C'+c+'_Ren_tau'+e_trans][0]
        ps.X_pulse(msmt) # update pi pulse parameters
        fast_pi_duration        = msmt.params['fast_pi_duration'] 
        pulse_tau               = tau - fast_pi_duration/2.0
        n_wait_reps, tau_remaind = divmod(round(2*pulse_tau*1e9),1e3) 
        if n_wait_reps %2 == 0:
            tau_cut = 1e-6
        else:
            tau_cut = 1.5e-6


        # LDE 2 does not need tau_cut because we do dynamic phase correction with a fixed tau_cut.
        if 'LDE_rephasing_2' in Gate.name:
            tau_cut =1e-6 #0e-6
            # print e.samples()


        ### avg. repump time + tau_cut gives the right amount of time.
        wait_duration = msmt.params['average_repump_time'] + tau_cut

        
        test = pulse.cp(Gate.T, length=wait_duration,name='rephasing')
        test.name = 'rephase'
        e.add(test)

    else:
        e = element.Element(Gate.name, pulsar = qt.pulsar)
        test = pulse.cp(Gate.T,length=forced_wait_duration,name = 'rephase_with_known_wait')
        e.add(test)
    return e
