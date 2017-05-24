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


    if msmt.params['do_calc_theta'] > 0 or msmt.params['general_sweep_name'] == 'sin2_theta':
        fit_a  = msmt.params['sin2_theta_fit_a']      
        fit_x0 = msmt.params['sin2_theta_fit_x0']     
        fit_of = msmt.params['sin2_theta_fit_of']
        p0 = msmt.params['sin2_theta']    
        msmt.params['mw_first_pulse_amp'] = fit_x0 - np.sqrt((p0-1+fit_of)/fit_a) ### calc right pulse amp from theta calibration
    Gate.mw_first_pulse = pulse.cp(ps.X_pulse(msmt),amplitude = msmt.params['mw_first_pulse_amp'],length = msmt.params['mw_first_pulse_length'],phase = msmt.params['mw_first_pulse_phase'])
    

    if msmt.params['first_mw_pulse_is_pi2'] > 0 and hasattr(Gate,'first_mw_pulse_phase'):
            Gate.mw_first_pulse = pulse.cp(Gate.mw_pi2, phase = Gate.first_mw_pulse_phase)
    elif msmt.params['first_mw_pulse_is_pi2']:
            Gate.mw_first_pulse = pulse.cp(Gate.mw_pi2, phase = msmt.params['mw_first_pulse_phase'])

    if hasattr(Gate,'no_first_pulse'):
        if Gate.no_first_pulse:
            Gate.mw_first_pulse = pulse.cp(Gate.mw_X,amplitude = 0)

    if hasattr(Gate,'no_mw_pulse') or msmt.params['do_only_opt_pi'] >0:
        if Gate.no_mw_pulse:
            Gate.mw_first_pulse = pulse.cp(Gate.mw_X,amplitude = 0)
            Gate.mw_pi2 = pulse.cp(Gate.mw_X,amplitude = 0)
            Gate.mw_mpi2 = pulse.cp(Gate.mw_X,amplitude = 0)
            Gate.mw_X = pulse.cp(Gate.mw_X,amplitude = 0)
        if msmt.params['do_only_opt_pi'] >0:
            Gate.mw_first_pulse = pulse.cp(Gate.mw_X,amplitude = 0)
            Gate.mw_pi2 = pulse.cp(Gate.mw_X,amplitude = 0)
            Gate.mw_mpi2 = pulse.cp(Gate.mw_X,amplitude = 0)
            Gate.mw_X = pulse.cp(Gate.mw_X,amplitude = 0)
        
    ### only use this if you want two proper pi pulses.
    # Gate.mw_first_pulse = pulse.cp(ps.X_pulse(msmt))

def _create_laser_pulses(msmt,Gate):
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
    if setup == 'lt3': 
        plu_amp = 1.0
    else:
        plu_amp = 0.0

    Gate.plu_gate = pulse.SquarePulse(channel = 'plu_sync', amplitude = plu_amp, 
                                    length = msmt.params['PLU_gate_duration'])

    # adwin comm
    Gate.adwin_trigger_pulse = pulse.SquarePulse(channel = 'adwin_sync',
        length = 2.2e-6, amplitude = 2) 
    Gate.adwin_count_pulse = pulse.SquarePulse(channel = 'adwin_count',
        length = 2.0e-6, amplitude = 2) 

def _create_wait_times(Gate):
    Gate.TIQ = pulse.SquarePulse(channel = 'MW_Imod',length=2e-6)
    Gate.T = pulse.SquarePulse(channel='MW_pulsemod',
        length = 50e-9, amplitude = 0)
    Gate.T_sync = pulse.SquarePulse(channel='sync',
        length = 50e-9, amplitude = 0)



### the LDE element
def generate_LDE_elt(msmt,Gate, **kw):
    '''
    returns the full LDE gate object with correctly ordered LDE element

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
    sp_amp = 1.0
    if msmt.params['do_only_opt_pi'] >0:
        sp_amp = 0.0

    # 1 SP
    e.add(pulse.cp(Gate.AWG_repump, 
        amplitude = 0, 
        length = msmt.joint_params['initial_delay']),
    name = 'initial_delay')
    
    e.add(pulse.cp( Gate.AWG_repump,
                    length          = msmt.params['LDE_SP_duration'], 
                    amplitude       = sp_amp), 
                    start           = msmt.params['LDE_SP_delay'],
                    name            = 'spinpumping', 
                    refpulse        = 'initial_delay')

    ### add the option to plug in a yellow laser pulse during spin pumping. not yet considered

    ### 2 syncs

    # 2a HH sync


    if msmt.params['sync_during_LDE'] == 1 :
        e.add(Gate.HHsync,
            refpulse = 'initial_delay')

        ### one awg has to sync all time-tagging devices.
        if setup == 'lt3' and msmt.params['is_two_setup_experiment'] > 0:
            # print 'i added the thing' 
            e.add(Gate.LT3HHsync,refpulse = 'initial_delay')

    # 2b adwin syncronization
    e.add(Gate.adwin_count_pulse,
        refpulse = 'initial_delay',
        name = 'count_pulse')#,start = 1e-6)


        
    if msmt.params['MW_during_LDE'] == 1: # and not ('LDE2' in Gate.name):
        
        # we choose to build the MW pulses up from the end of the element.
        # this is more convenient when trying to preserve the coherence of the electron over several elements
        # it however becomes more complicated from a programming point of view.
        
        # MW pi pulse
        if msmt.params['check_EOM_projective_noise'] > 0:
            e.add(Gate.mw_X,
                start           = msmt.params['MW_repump_distance'],
                refpulse        = 'spinpumping',
                refpoint        = 'end',
                refpoint_new    = 'center',
                name            = 'invert_before_excitation')
            mw_theta_ref_pulse  = 'invert_before_excitation'
            mw_theta_delay =  500e-9 ### hardcoded botching. because why not.
            mw_theta_refpoint = 'center'
        else:
            mw_theta_ref_pulse = 'spinpumping'
            mw_theta_delay = msmt.params['MW_repump_distance']
            mw_theta_refpoint = 'end'
            #mw pi/2 pulse or 'theta'
        e.add(Gate.mw_first_pulse,
            start           = mw_theta_delay,
            refpulse        = mw_theta_ref_pulse,
            refpoint        = mw_theta_refpoint,
            refpoint_new    = 'center',
            name            = 'MW_Theta')

        if msmt.params['MW_pi_during_LDE'] == 1:
            e.add(Gate.mw_X,
                start           = msmt.params['LDE_decouple_time'],
                refpulse        = 'MW_Theta',
                refpoint        = 'center',
                refpoint_new    = 'center',
                name            = 'MW_pi')


            if msmt.params['MW_RO_pulse_in_LDE'] == 1:
                e.add(pulse.cp(Gate.mw_pi2,phase = msmt.params['LDE_final_mw_phase']),
                    start           = msmt.params['LDE_decouple_time'],
                    refpulse        = 'MW_pi',
                    refpoint        = 'center',
                    refpoint_new    = 'center',
                    name            = 'RO_pulse')

    else:

        #mw pi/2 pulse or 'theta'
        e.add(pulse.cp(Gate.mw_first_pulse,amplitude=0),
            start           = msmt.params['MW_repump_distance'],
            refpulse        = 'spinpumping', #for this measurement: nobody gives a damn about carbons: therefore easier to build up the sequence.
            refpoint        = 'end', 
            refpoint_new    = 'center',
            name            = 'MW_Theta')

    #4 opt. pi pulses
    # print 'Nr of opt pi pulses', msmt.joint_params['opt_pi_pulses']

    if not (msmt.params['LDE_is_init'] > 0):

        if msmt.params['is_TPQI'] > 0:
            initial_reference = 'spinpumping'
            msmt.params['MW_opt_puls1_separation'] = 1e-6
        else:
            initial_reference = 'MW_Theta'

        if qt.current_setup == 'lt3': ### only LT3 gives out the pi pulses
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

                opt_ref_name = 'opt pi {}'.format(i+1)

                if msmt.params['PLU_during_LDE'] == 1 :
                    e.add(Gate.plu_gate, name = 'plu gate 1', 
                        refpulse = opt_ref_name,
                        start = msmt.params['PLU_1_delay'])

                    plu_to_plu_ref_name = 'plu gate {}'.format(i+1)


            plu_to_plu_ref_name = 'plu gate {}'.format(i+1)
            #5 Plu gates
            if msmt.params['PLU_during_LDE'] == 1:
                ## the name plu 3 is historic... see bell.
                e.add(pulse.cp(Gate.plu_gate, 
                        length = msmt.params['PLU_gate_3_duration']), 
                    name = 'plu gate 3', 
                    start = msmt.params['PLU_3_delay'], 
                    refpulse = plu_to_plu_ref_name)


                e.add(pulse.cp(Gate.plu_gate, 
                        length = msmt.params['PLU_gate_3_duration']), 
                        name = 'plu gate 4', 
                        start = msmt.params['PLU_4_delay'],
                        refpulse = 'plu gate 3')
    #### gives a done trigger that has to be timed accordingly, is referenced to the PLU if the PLU is used by this setup.
    if Gate.is_final:
        ## one can time accurately if we use the plu during the experiment

        boolean = (msmt.params['PLU_during_LDE'] > 0) and (msmt.params['LDE_is_init'] == 0)
        if not boolean: ### if this is not the case then the measurement is PLU insensitive
            e.add(Gate.adwin_trigger_pulse, ### insert the trigger right at the start
                    start = 0,
                    refpulse = 'count_pulse',
                    refpoint = 'start',
                    refpoint_new = 'start')

        else:
            ## if we are dependent on the plu then the plu trigger has to come in before the done trigger.
            ## otherwise the ADwins will get confused!
            ## we therefore make the sequence jump to the end of the awg sequence to obtain the jump trigger.
            pass

   
    # Gate.reps = msmt.joint_params['LDE_attempts_before_CR']
    Gate.elements = [e]
    Gate.elements_duration = msmt.joint_params['LDE_element_length']

    # consistent?
    e_len = e.length()

    # uncomment for thourogh checks.
    # e.print_overview()

    if e_len != msmt.joint_params['LDE_element_length']:
        raise Exception('LDE element "{}" has length {:.6e}, but specified length was {:.6e}. granularity issue?'.format(e.name, e_len, msmt.joint_params['LDE_element_length']))

def generate_LDE_rephasing_elt(msmt,Gate,**kw):
    """
    Attaches the LDE rephasing element to the a DD_2 gate object.
    The element encompasses one pi pulse or a pi/2 pulse.
    Input: Gate object
    Output: None
    """
    _create_wait_times(Gate)
    _create_syncs_and_triggers(msmt,Gate)
    _create_mw_pulses(msmt,Gate)
    _create_laser_pulses(msmt,Gate)

    #### calculate the time after the first pi/2 pulse:

    ### first: how far is the pi pulse in the sequence away from the end of the LDe element
    echo_time = msmt.joint_params['LDE_element_length']-msmt.params['MW_repump_distance']-msmt.params['LDE_SP_duration']
    echo_time -=  msmt.params['LDE_SP_delay'] + msmt.params['LDE_decouple_time']
    if msmt.params['check_EOM_projective_noise'] > 0:
        echo_time -= 500e-9 # bodged as above

    ### calculate the time for the pi/2 pulse to come in
    echo_time = msmt.params['LDE_decouple_time'] - echo_time
    echo_time += msmt.params['MW_final_delay_offset'] # dirty hack. has to be calibrated once. See sweep_single_click_ent_expm.py
    end_delay_refpulse = 'initial_delay'

    ### length of the element is calculated according to the required echo condition
    e = element.Element(Gate.name, pulsar = qt.pulsar)
    e.add(pulse.cp(Gate.AWG_repump,
                amplitude = 0,
                length = echo_time + 2*msmt.params['dynamic_decoupling_tau'] 
                )
        )

    e.add(pulse.cp(Gate.AWG_repump, 
        amplitude = 0, 
        length = msmt.joint_params['initial_delay']),
        name = 'initial_delay')



    if msmt.joint_params['do_final_mw_LDE'] == 1 and (not msmt.params['MW_RO_pulse_in_LDE'] == 1):

        if msmt.params['do_dynamical_decoupling'] > 0:
            e.add(pulse.cp(Gate.mw_X,phase = msmt.params['Y_phase']),
                start           = echo_time+msmt.params['dynamic_decoupling_tau'],
                refpulse        = 'initial_delay',
                refpoint        = 'start',
                refpoint_new    = 'center',
                name            = 'MW_RO_rotation')
        else:

            e.add(pulse.cp(Gate.mw_pi2,
                phase           = msmt.params['LDE_final_mw_phase'],
                amplitude       = msmt.params['LDE_final_mw_amplitude']),
                start           = echo_time,
                refpulse        = 'initial_delay',
                refpoint        = 'start',
                refpoint_new    = 'center',
                name            = 'MW_RO_rotation')




    if msmt.params['PLU_during_LDE'] == 1 and qt.current_setup == 'lt3':
        ### this pulse is supposed to turn off the plu signal to both adwins
        e.add(pulse.cp(Gate.plu_gate, 
            length = msmt.params['PLU_gate_3_duration']), 
            name = 'plu for adwin', 
            start = 1.2e-6, ## arbitrarily chosen number
            refpulse = 'initial_delay')


    Gate.elements = [e]



def generate_tomography_mw_pulse(msmt,Gate,**kw):
    """
    Attaches a last pi/2 pulse or no pulse to a DD_2 gate object.
    The element encompasses one pi/2 pulse after the dynamical decoupling sequence.
    Input: Gate object
    Output: None
    """
    _create_wait_times(Gate)
    _create_mw_pulses(msmt,Gate)
    _create_laser_pulses(msmt,Gate)
    
    e = element.Element(Gate.name, pulsar = qt.pulsar)
    e.add(pulse.cp(Gate.AWG_repump,
                amplitude = 0,
                length = 2*1e-6
                )
        )

    e.add(pulse.cp(Gate.AWG_repump, 
        amplitude = 0, 
        length = msmt.joint_params['initial_delay']),
        name = 'initial_delay')

    ### this contains our RO definitions
    tomo_dict = {
        'X': pulse.cp(Gate.mw_pi2,phase = msmt.params['LDE_final_mw_phase']), #### check this!!!
        'Y': pulse.cp(Gate.mw_pi2,phase = msmt.params['LDE_final_mw_phase']+90),
        'Z': pulse.cp(Gate.mw_pi2, amplitude = 0)
    }

    if msmt.joint_params['do_final_mw_LDE'] > 0:
        e.add(tomo_dict[msmt.params['tomography_basis']],
            start           = 1e-6,
            refpulse        = 'initial_delay',
            refpoint        = 'start',
            refpoint_new    = 'center',
            name            = 'MW_RO_rotation')


        end_delay_refpulse = 'MW_RO_rotation'
    else:
        end_delay_refpulse = 'initial_delay'
    e.add(pulse.cp(Gate.AWG_repump, 
        amplitude = 0, 
        length = msmt.joint_params['initial_delay']),
        name = 'output_delay',
        refpulse        = end_delay_refpulse,
        refpoint        = 'end',
        refpoint_new    = 'start')
    Gate.elements = [e]
