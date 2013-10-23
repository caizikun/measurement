"""
This file contains all the measurement parameters.
"""

import numpy as np
import logging
import qt
import hdf5_data as h5

import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

params = m2.MeasurementParameters('JointParameters')
params_lt1 = m2.MeasurementParameters('LT1Parameters')
params_lt2 = m2.MeasurementParameters('LT2Parameters')

### Hardware stuff
params['HH_binsize_T3'] = 8

params_lt1['counter_channel'] = 1
params_lt1['ADwin_lt2_trigger_do_channel'] = 8 # OK
params_lt1['ADWin_lt2_di_channel'] = 17 # OK
params_lt1['AWG_lt1_trigger_do_channel'] = 10 # OK
params_lt1['AWG_lt1_di_channel'] = 16 # OK
params_lt1['PLU_arm_do_channel'] = 11
params_lt1['PLU_di_channel'] = 18
params_lt1['AWG_lt1_event_do_channel'] = 14
params_lt1['AWG_lt2_address0_do_channel'] = 0
params_lt1['AWG_lt2_address1_do_channel'] = 1
params_lt1['AWG_lt2_address2_do_channel'] = 2
params_lt1['AWG_lt2_address3_do_channel'] = 3
params_lt1['AWG_lt2_address_LDE'] = 1
params_lt1['AWG_lt2_address_U1'] = 2                    
params_lt1['AWG_lt2_address_U2'] = 3
params_lt1['AWG_lt2_address_U3'] = 4
params_lt1['AWG_lt2_address_U4'] = 5       
params_lt1['repump_off_voltage'] = 0.0         
params_lt1['E_off_voltage'] = 0.0
params_lt1['A_off_voltage'] = 0.0

params_lt2['counter_channel'] = 1
params_lt2['Adwin_lt1_do_channel'] = 2
params_lt2['Adwin_lt1_di_channel'] = 17
params_lt2['AWG_lt2_di_channel'] = 16
params_lt2['repump_off_voltage'] = 0.0
params_lt2['Ey_off_voltage'] = 0.0
params_lt2['A_off_voltage'] = -0.09
params_lt2['freq_AOM_DAC_channel'] = 4

### RO settings
params_lt1['wait_before_SSRO1'] = 3
params_lt1['wait_before_SP_after_RO'] = 3
params_lt1['A_SP_duration'] = 10 # 10 used after MBI and after the first RO of the BSM
params_lt1['wait_before_SSRO2'] = 3
params_lt1['SSRO2_duration'] = 15 #15
params_lt1['SSRO1_duration'] = 15 #15

params_lt2['SSRO_lt2_duration'] = 50

### CR and asynchronous preparation settings
params_lt1['CR_duration'] = 50
params_lt1['CR_threshold_preselect'] = 4000
params_lt1['CR_threshold_probe'] = 20
params_lt1['CR_repump'] = 1
params_lt1['CR_probe_max_time'] = 10000 #us
params_lt1['repump_duration'] = 500 #50
# params_lt1['time_before_forced_CR'] = 1 #1#20000 # FIXME
# params_lt1['N_pol_element_repetitions'] = 5 # FIXME

### MBI on LT1
params_lt1['E_SP_duration'] = 100
params_lt1['MBI_duration'] = 4 #put back to 4 with gate
params_lt1['MBI_threshold'] = 1 
params_lt1['N_randomize_duration'] = 1 # This could still be optimized, 50 is a guess
params_lt1['E_N_randomize_amplitude'] = 0e-9 # 10 nW is a guess, not optimized
params_lt1['A_N_randomize_amplitude'] = 0e-9 # 10 nW is a guess, not optimized
params_lt1['repump_N_randomize_amplitude'] = 0

params_lt2['repump_duration'] = 500 #yellow 10#green #
params_lt2['repump_freq_offset'] = 5.
params_lt2['repump_freq_amplitude'] = 4.

params_lt2['CR_duration'] = 50
params_lt2['CR_preselect'] = 25
params_lt2['CR_probe'] = 2
params_lt2['CR_repump'] = 1000
params_lt2['CR_probe_max_time'] = 500000 # us = 0.5 s 
 
### SSRO, CR, SP Laser powers
params_lt1['E_CR_amplitude'] = 5e-9
params_lt1['A_CR_amplitude'] = 15e-9               
params_lt1['E_SP_amplitude'] = 10e-9 #was 10e-9              
params_lt1['E_RO_amplitude'] = 7e-9  
params_lt1['A_RO_amplitude'] = 0
params_lt1['repump_amplitude'] = 50e-9 #300e-6#

params_lt2['Ey_CR_amplitude'] = 6e-9             
params_lt2['A_CR_amplitude'] = 16e-9              
params_lt2['Ey_SP_amplitude'] = 0e-9              
params_lt2['A_SP_amplitude'] = 20e-9             
params_lt2['Ey_RO_amplitude'] = 10e-9
params_lt2['A_RO_amplitude'] = 0
params_lt2['repump_amplitude'] = 200e-6 #yellow 200e-6#green #

####################
### pulses and MW stuff LT1
#####################
## general
f_msm1_cntr_lt1 = 2.828040e9
N_frq_lt1 = 7.13456e6
N_HF_frq_lt1 = 2.19290e6
mw0_lt1= 2.8e9
f0_lt1 = f_msm1_cntr_lt1 - mw0_lt1
finit_lt1 = f0_lt1 - N_HF_frq_lt1

params_lt1['ms-1_cntr_frq'] = f_msm1_cntr_lt1
params_lt1['N_0-1_splitting_ms-1'] = N_frq_lt1
params_lt1['N_HF_frq'] = N_HF_frq_lt1
params_lt1['mw_frq'] = mw0_lt1
params_lt1['mw_power'] = 20
params_lt1['mI-1_mod_frq'] = finit_lt1
params_lt1['MW_pulse_mod_risetime'] = 10e-9
params_lt1['AWG_MBI_MW_pulse_mod_frq'] = finit_lt1

# for the BSM:
params_lt1['N_ref_frq'] = N_frq_lt1
params_lt1['e_ref_frq'] = finit_lt1
params_lt1['pi2_evolution_time'] = 50.615e-6
params_lt1['H_evolution_time'] = 35.0834e-6
params_lt1['H_phase'] = -82.1 # was 28
params_lt1['echo_time_after_LDE'] = -713e-9

params_lt1['buffer_time_for_CNOT'] = 240e-9
# this time is removed at the previous element before the pi2pi CNOT element, 
# and added to the CNOT element: it serves to put the center of the CNOT on the C echo
# change only when the pi2pi length would be changed.

## pulses
params_lt1['fast_pi_mod_frq'] = finit_lt1
params_lt1['fast_pi_amp'] = 0.816
params_lt1['fast_pi_duration'] = 80e-9

# fast pi/2 pulse
params_lt1['fast_pi2_mod_frq'] = finit_lt1
params_lt1['fast_pi2_amp'] = 0.849
params_lt1['fast_pi2_duration'] = 40e-9

# slow pi  pulse
params_lt1['selective_pi_mod_frq'] = finit_lt1
params_lt1['selective_pi_amp'] =  0.0181
params_lt1['selective_pi_duration'] = 2500e-9

CORPSE_frq_lt1 = 5e6
params_lt1['CORPSE_pi_mod_frq'] = finit_lt1 + N_HF_frq_lt1/2.
params_lt1['CORPSE_pi_60_duration'] = 1./CORPSE_frq_lt1/6.
params_lt1['CORPSE_pi_m300_duration'] = 5./CORPSE_frq_lt1/6.
params_lt1['CORPSE_pi_420_duration'] = 7./CORPSE_frq_lt1/6.
params_lt1['CORPSE_pi_amp'] = 0.526
params_lt1['CORPSE_pi_phase_shift'] = 89.7
params_lt1['CORPSE_pi_center_shift'] = 0.e-9

params_lt1['pi2pi_mIm1_mod_frq'] = finit_lt1
params_lt1['pi2pi_mIm1_amp'] = 0.110
params_lt1['pi2pi_mIm1_duration'] = 396e-9

params_lt1['N_pi_duration'] = 57.98e-6
params_lt1['N_pi_amp'] = 1.

params_lt1['N_pi2_duration'] = params_lt1['N_pi_duration']/2.
params_lt1['N_pi2_amp'] =1.



####################
### pulses and MW stuff LT2
#####################
## general
f_msm1_cntr_lt2 = 2.828825e9
mw0_lt2 = 2.8e9
f0_lt2 = f_msm1_cntr_lt2 - mw0_lt2
params_lt2['ms-1_cntr_frq'] = f_msm1_cntr_lt2
params_lt2['mw_frq'] = mw0_lt2
params_lt2['mw_power'] = 20
params_lt2['MW_pulse_mod_risetime'] = 10e-9

CORPSE_frq_lt2 = 8.15e6
params_lt2['CORPSE_pi_mod_frq'] = f0_lt2
params_lt2['CORPSE_pi_amp'] = 0.438
params_lt2['CORPSE_pi_60_duration'] =1./CORPSE_frq_lt2/6.
params_lt2['CORPSE_pi_m300_duration'] = 5./CORPSE_frq_lt2/6.
params_lt2['CORPSE_pi_420_duration'] = 7./CORPSE_frq_lt2/6.

params_lt2['CORPSE_pi2_mod_frq'] = f0_lt2
params_lt2['CORPSE_pi2_amp'] = 0.506
params_lt2['CORPSE_pi2_24p3_duration'] = 24.3/CORPSE_frq_lt2/360.
params_lt2['CORPSE_pi2_m318p6_duration'] = 318.6/CORPSE_frq_lt2/360.
params_lt2['CORPSE_pi2_384p3_duration'] = 384.3/CORPSE_frq_lt2/360.

params_lt2['DD_pi_phases'] = [-90,0,-90] ## THIS DEFINES THE YXY SEQUENCE
params_lt2['first_C_revival'] = 53.6e-6
params_lt2['dd_extra_t_between_pi_pulses'] = 22e-9
params_lt2['dd_spin_echo_time'] = 520e-9 

### LDE sequence settings
params['HH_sync_period'] = 400e-9 # in seconds -- important for checking (see measurement_loop())
									#Question from hannes: is this the separation of the optical pi pulses?

# LDE Sequence in the AWGs
params_lt2['eom_pulse_duration']        = 2e-9
params_lt2['eom_off_duration']          = 100e-9
params_lt2['eom_off_amplitude']         = -.26  # calibration from 23-08-2013
params_lt2['eom_pulse_amplitude']       = 1.2
params_lt2['eom_overshoot_duration1']   = 10e-9
params_lt2['eom_overshoot1']            = -0.03
params_lt2['eom_overshoot_duration2']   = 4e-9
params_lt2['eom_overshoot2']            = -0.03
params_lt2['aom_risetime']              = 42e-9

params_lt2['AWG_SP_power']            = 40e-9
params_lt2['AWG_yellow_power']        = 0e-9 #yellow power during SP in LDE on LT1
params_lt2['opt_pulse_separation']    = 600e-9
params_lt2['MW_opt_puls1_separation'] = 50e-9 #distance between the end of the MW and the start of opt puls1
params_lt2['MW_opt_puls2_separation'] = 50e-9

params_lt2['PLU_gate_duration']       = 70e-9
params_lt2['PLU_gate_3_duration']     = 40e-9
params_lt2['PLU_3_delay']             = 50e-9
params_lt2['PLU_4_delay']             = 150e-9

params_lt1['AWG_SP_power']            = 20e-9 # the 
params_lt1['AWG_yellow_power']        = 0e-9  # yellow power during SP in LDE on LT1
params_lt1['MW_wait_after_SP']        = 200e-9 # wait time between end of SP_lt1 and start of first MW
params_lt1['MW_separation']           = 600e-9 # separation between the two MW pulses on LT1

params_lt1['initial_delay']           = 10e-9 + 240e-9
params_lt2['initial_delay']           = 10e-9

params['single_sync']                 = 1 #if ==1 then there will only be 1 sync otherwise 1 for each puls
params_lt1['MW_during_LDE']           = 0 #NOTE:MW stuff not implemented, yet
params_lt2['MW_during_LDE']           = 0 #NOTE:MW stuff not implemented, yet

params['LDE_SP_duration']             = 5e-6
params['LDE_SP_duration_yellow']      = 3e-6
params['wait_after_sp']               = 500e-9 #this should be large enough, so that the MW puls fits
params['LDE_element_length']          = 8e-6 # 9k for TPQI with 5 pulses

params['source_state_basis'] = 'X'

### default process settings
params['LDE_attempts_before_CR'] = 100 # 1000 for tpqi seems ok

params_lt1['max_CR_starts'] = -1
params_lt1['teleportation_repetitions'] = -1
params_lt1['do_remote'] = 1
params_lt1['do_N_polarization'] = 1

params_lt2['teleportation_repetitions'] = -1

########
## parameters (for now) only used in calibration scripts
########
CALIBRATION = True
if CALIBRATION:

    ############### lt1
    ####################
    params_lt1['AWG_wait_duration_before_MBI_MW_pulse'] = 1e-6
    params_lt1['AWG_wait_for_adwin_MBI_duration'] = 15e-6
    params_lt1['AWG_wait_duration_before_shelving_pulse'] = 100e-9

    params['nr_of_ROsequences'] = 1 # this is the standard
    params_lt1['max_MBI_attempts'] = 1
    params_lt1['Ex_MBI_amplitude'] = 5e-9
    #params_lt1['AWG_to_adwin_ttl_trigger_duration'] = 2e-6


    params_lt1['A_SP_amplitude'] = 15e-9 #was 10
    params_lt1['repump_after_MBI_amplitude'] = params_lt1['A_SP_amplitude']
    params_lt1['repump_after_MBI_duration'] = params_lt1['A_SP_duration']
    params_lt1['repump_after_E_RO_duration'] = 10
    params_lt1['repump_after_E_RO_amplitude']  = params_lt1['A_SP_amplitude']

    #MBI
    params_lt1['AWG_MBI_MW_pulse_ssbmod_frq'] = params_lt1['AWG_MBI_MW_pulse_mod_frq']
    params_lt1['AWG_MBI_MW_pulse_amp'] = params_lt1['selective_pi_amp']
    params_lt1['AWG_MBI_MW_pulse_duration'] = params_lt1['selective_pi_duration']

    params_lt1['Ex_CR_amplitude'] = params_lt1['E_CR_amplitude']
    params_lt1['A_CR_amplitude'] = params_lt1['A_CR_amplitude']
    params_lt1['Ex_SP_amplitude'] = params_lt1['E_SP_amplitude'] # to pump to ms+- 1 before MBI slow pulse
    params_lt1['A_off_voltage'] = params_lt1['A_off_voltage']
    params_lt1['Ex_off_voltage'] = params_lt1['E_off_voltage']
    params_lt1['SP_E_duration'] = params_lt1['E_SP_duration']

    params_lt1['cycle_duration'] = 300
    params_lt1['repump_after_repetitions'] = 1 #could remove this altogether from adwin...
    params_lt1['send_AWG_start'] = 1
    params_lt1['AWG_done_DI_channel'] = params_lt1['AWG_lt1_di_channel']
    params_lt1['AWG_event_jump_DO_channel'] = params_lt1['AWG_lt1_event_do_channel']
    params_lt1['AWG_start_DO_channel'] = params_lt1['AWG_lt1_trigger_do_channel'] 

    params_lt1['CR_preselect'] = params_lt1['CR_threshold_preselect']
    params_lt1['CR_probe'] = params_lt1['CR_threshold_probe']

    params_lt1['wait_after_RO_pulse_duration'] = 3
    params_lt1['wait_after_pulse_duration'] = 3


    ############### lt2
    ####################
    params_lt2['SP_duration'] = 250
    params_lt2['SSRO_duration'] = params_lt2['SSRO_lt2_duration'] 
    params_lt2['SSRO_stop_after_first_photon'] = 0
    params_lt2['SP_filter_duration'] = 0

    params_lt2['cycle_duration'] = 300
    params_lt2['sequence_wait_time'] = 1
    params_lt2['wait_after_RO_pulse_duration'] = 3
    params_lt2['wait_after_pulse_duration'] = 3
    params_lt2['send_AWG_start'] = 1
    params_lt2['repump_after_repetitions'] = 1

    params_lt2['AWG_done_DI_channel'] = params_lt2['AWG_lt2_di_channel']
    params_lt2['AWG_event_jump_DO_channel'] = 6
    params_lt2['AWG_start_DO_channel'] = 1

    params_lt2['Ex_CR_amplitude'] = params_lt2['Ey_CR_amplitude']
    params_lt2['Ex_SP_amplitude'] = params_lt2['Ey_SP_amplitude']
    params_lt2['Ex_RO_amplitude'] = params_lt2['Ey_RO_amplitude']
    params_lt2['Ex_off_voltage'] = params_lt2['Ey_off_voltage']