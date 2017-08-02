''' Measurement set to calibrate the evolution frequencies for the different carbon spins 
plus the phases they pick up during carbon gates'''

import io,sys
import numpy as np
import qt
import msvcrt
import copy
from analysis.scripts.QEC import carbon_ramsey_analysis as cr 
reload(cr)

execfile(qt.reload_current_setup)

ins_adwin = qt.instruments['adwin']
ins_counters = qt.instruments['counters']
ins_aom = qt.instruments['GreenAOM']

SETUP = qt.current_setup

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

electron_transition_string = qt.exp_params['samples'][SAMPLE]['electron_transition']

import measurement.lib.measurement2.adwin_ssro.DD_2 as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs
import measurement.scripts.carbonspin.write_to_msmt_params as write_to_msmt_params
reload(funcs)
n = 1

#######################################################
###### Set which carbons and values to calibrate ######
#######################################################

qt.exp_params['simplify_wfnames'] = True

carbons = [2,4,5,3,6,7]#[2,4,5]#,4]

"""
AFTER THE CALIBRATION IS DONE:

The measured values are directly written into msmt_params.py
"""
use_queue = False

f_ms0 = False
f_ms1 = False
update_average_freq = False

self_phase_calibration = False
self_unc_phase_offset_calibration = False
self_unc_phase_calibration = False
check_unc_phase_calibration = False
check_phase_or_offset = 'phase' # Check timing after, or phase offset.
cross_phase_calibration = True
cross_phase_steps       = 1



# Note that you wont save to msmt params if debug is on.
debug = False

### repetitions per data point.
freq_reps = 750
phase_reps = 500
crosstalk_reps = 500


### this is used to determine the detuning of the ramsey measurements.
if SETUP == 'lt2':
    detuning_basic = 5e3
    detuning_dict = {
        '1' : detuning_basic,
        '2' : detuning_basic*2,
        '3' : detuning_basic*3.,
        '4' : detuning_basic*2,
        '5' : detuning_basic,
        '6' : detuning_basic*4.,
        '7' : detuning_basic*4}

elif SETUP == 'lt3':
    detuning_basic = 2e3
    detuning_dict = {
        '1' : detuning_basic,
        '2' : 5*detuning_basic,
        '5' : detuning_basic,
        '6' : 2*detuning_basic,
        '7' : 2*detuning_basic,
        '8' : detuning_basic}

elif SETUP == 'lt4':
    detuning_basic = 5e3
    detuning_dict = {
        '1' : detuning_basic,
        '2' : detuning_basic,
        '3' : detuning_basic,
        '4' : detuning_basic,
        '5' : detuning_basic,
        '6' : detuning_basic,
        '7' : detuning_basic,
        '8' : detuning_basic
        }
######


def optimize():
    GreenAOM.set_power(10e-6)
    optimiz0r.optimize(dims=['x','y','z'], int_time=100)
    GreenAOM.set_power(0e-6)


def stop_msmt():
    print '--------------------------------'
    print 'press q to stop measurement loop'
    print '--------------------------------'
    qt.msleep(5)
    if msvcrt.kbhit() and msvcrt.getch() == 'q':
        return 0

    else: return 1

def NuclearRamseyWithInitialization_cal(name, 
        carbon_nr           = 5,               
        carbon_init_state   = 'up', 
        el_RO               = 'positive',
        detuning            = 0.5e3,
        el_state            = 0,
        debug               = False):
    
    m = DD.NuclearRamseyWithInitialization(name)
    funcs.prepare(m)

    '''Set parameters'''

    ### Sweep parameters
    m.params['reps_per_ROsequence'] = freq_reps
    m.params['C13_MBI_RO_state'] = 0
    ### overwritten from msmnt params
           
    ####################################
    ### Option 1; Sweep waiting time ###
    ####################################
    
        # 1A - Rotating frame with detuning
    m.params['add_wait_gate'] = True
    m.params['pts'] = 25
    if carbon_nr == 8:
        m.params['pts'] = 18
    m.params['free_evolution_time'] = 400e-6 + np.linspace(0e-6, 3*1./detuning,m.params['pts'])
    # m.params['free_evolution_time'] = 180e-6 + np.linspace(0e-6, 4*1./74e3,m.params['pts'])
    

    m.params['C'+str(carbon_nr)+'_freq_0']  += detuning
    m.params['C'+str(carbon_nr)+'_freq_1'+m.params['electron_transition']]  += detuning
    m.params['C_RO_phase'] =  np.ones(m.params['pts'] )*0  

    m.params['sweep_name'] = 'free_evolution_time'
    m.params['sweep_pts']  = m.params['free_evolution_time']

    '''Derived and fixed parameters'''
    # 
    m.params['electron_readout_orientation'] = el_RO
    m.params['carbon_nr']                    = carbon_nr
    m.params['init_state']                   = carbon_init_state  
    m.params['electron_after_init'] = str(el_state)
    m.params['Nr_C13_init']       = 1
    m.params['Nr_MBE']            = 0
    m.params['Nr_parity_msmts']   = 0

    funcs.finish(m, upload =True, debug=debug)

def NuclearRamseyWithInitialization_phase(name, 
        carbon_nr           = 1,               
        carbon_init_state   = 'up', 
        el_RO               = 'positive',
        el_state            = 0,
        debug               = False):

    m = DD.NuclearRamseyWithInitialization(name)
    funcs.prepare(m)

    '''Set parameters'''

    ### Sweep parameters
    m.params['reps_per_ROsequence'] = phase_reps
    m.params['C13_MBI_RO_state'] =0
    m.params['pts'] = 25
    if carbon_nr == 6 and SETUP == 'lt2':
        m.params['pts'] = 21

    m.params['add_wait_gate'] = False
    # m.params['free_evolution_time'] = np.ones(m.params['pts'] )*360e-6
    m.params['C_RO_phase'] = np.linspace(-60, 400,m.params['pts'])    

    m.params['sweep_name'] = 'phase'
    m.params['sweep_pts']  = m.params['C_RO_phase']

    '''Derived and fixed parameters'''

    m.params['electron_readout_orientation'] = el_RO
    m.params['carbon_nr']                    = carbon_nr
    m.params['init_state']                   = carbon_init_state  
    m.params['electron_after_init'] = str(el_state)

    m.params['Nr_C13_init']       = 1
    m.params['Nr_MBE']            = 0
    m.params['Nr_parity_msmts']   = 0

  
    funcs.finish(m, upload =True, debug=debug)

# Added by PH to calibrate the phase for unconditional rotations on the carbons.
def NuclearRamseyWithInitialization_unc_phase(name, 
        carbon_nr           = 1,               
        carbon_init_state   = 'up', 
        el_RO               = 'positive',
        el_state            = 0,
        check_phase_or_offset     = 'phase',
        check_phase         = False,
        debug               = False):

    m = DD.NuclearRamseyWithInitializationUncondCGate(name)
    funcs.prepare(m)

    '''Set parameters'''

    if check_phase_or_offset != 'phase' and check_phase_or_offset != 'offset':
        print "Wrong parameter passed to check_phase_or_offset"
        return

    m.params['check_phase_or_offset'] = check_phase_or_offset
    m.params['check_phase'] = check_phase

    ### Sweep parameters
    m.params['reps_per_ROsequence'] = phase_reps
    m.params['C13_MBI_RO_state'] =0
    m.params['pts'] = 25
    if carbon_nr == 6 and SETUP == 'lt2':
        m.params['pts'] = 21

    m.params['add_wait_gate'] = False
    # m.params['free_evolution_time'] = np.ones(m.params['pts'] )*360e-6
    m.params['C_unc_phase'] = np.linspace(-60, 400,m.params['pts'])    

    m.params['sweep_name'] = 'phase'
    m.params['sweep_pts']  = m.params['C_unc_phase']

    '''Derived and fixed parameters'''

    m.params['electron_readout_orientation'] = el_RO
    m.params['carbon_nr']                    = carbon_nr
    m.params['init_state']                   = carbon_init_state  
    m.params['electron_after_init'] = str(el_state)


    if check_phase_or_offset == 'phase':
        m.params['C13_MBI_threshold_list'] = [1]
    else: #For offset calibration we use MBI.
        m.params['C13_MBI_threshold_list'] = [1]

    m.params['Nr_C13_init']       = 1
    m.params['Nr_MBE']            = 0
    m.params['Nr_parity_msmts']   = 0

  
    funcs.finish(m, upload =True, debug=debug)


def Crosstalk_vs2(name, C_measured = 5, C_gate = 1, RO_phase=0, RO_Z=False, C13_init_method = 'MBI', 
                    N_list = np.arange(4,300,24), debug = False,el_RO= 'positive',el_state = 0, nr_of_gates = 1,smart_sweep_pts=False,estimate_phase=0):
    m = DD.Nuclear_Crosstalk(name)
    funcs.prepare(m)

    '''set experimental parameters'''
    
    m.params['carbon_nr']           = C_measured    ### Carbon spin that the Ramsey is performed on
    m.params['Carbon_B']            = C_gate        ### Carbon spin that the Rabi/Gate is performed on
    
    m.params['reps_per_ROsequence'] = crosstalk_reps 
    m.params['init_state']          = 'up' 
    # m.params['nr_of_gates']          = nr_of_gates
    
    m.params['pts']                 = 16
    # if C_measured == 6:
    #     m.params['pts'] = 16

    if smart_sweep_pts:
        if np.mod(m.params['pts'],2)!=0:
            print 'to use smart data points, the number of points has to be even. Changing # pts: ', m.params['pts'], ' to # pts: ' , m.params['pts']+1
            m.params['pts']+=1
        print m.params['pts']
        #estimate_phase=m.params['C'+str(C_gate)+'_Ren_extra_phase_correction_list'+electron_transition_string][C_measured]
        print 'estimated phase for params = ', estimate_phase
        phases_a  = np.round(np.mod(np.rad2deg(np.arccos(np.linspace(-1,1,(m.params['pts']/2-2)))) - estimate_phase, 360))
        phases_b  = np.mod(phases_a[1:-1] + 180, 360)
        phases_ab = np.sort(np.append(phases_a,phases_b))
        phases = np.sort(np.append(phases_ab,(phases_ab[:6]+360)))
        m.params['C_RO_phase'] = phases
        print m.params['C_RO_phase']
    else:
        m.params['C_RO_phase']      = np.linspace(-60, 400,m.params['pts'])    

    m.params['sweep_name']          = 'phase'
    m.params['sweep_pts']           = m.params['C_RO_phase']

    '''Derived and fixed parameters'''

    m.params['electron_readout_orientation'] = el_RO

    m.params['Nr_C13_init']       = 1
    m.params['Nr_MBE']            = 0
    m.params['Nr_parity_msmts']   = 0
   
    funcs.finish(m, upload =True, debug=debug)
            
def update_msmt_params(carbons,f_ms0,f_ms1,self_phase,cross_phase,self_unc_phase,self_unc_phase_offset,debug):

    """
    This routine automatically takes the measured values and writes them to the measurement parameters.
    Takes a list of carbons as input and the booleans which decode which calibrations have been done.
    """

    if debug:
        return # bail out!

    calibrated_params = qt.exp_params['samples'][SAMPLE]

    search_strings = []
    param_string_overrides = []

    for c in carbons:
        if f_ms0:
            search_strings.append('C'+str(c)+'_freq_0')
            param_string_overrides.append(None)

        if f_ms1:
            search_strings.append('C'+str(c)+'_freq_1'+electron_transition_string)
            param_string_overrides.append(None)

        if update_average_freq and f_ms0 and f_ms1:

            Cf0_string = 'C'+str(c)+'_freq_0'
            Cf1_string = 'C'+str(c)+'_freq_1'+electron_transition_string

            search_strings.append('C'+str(c)+'_freq'+electron_transition_string)
            param_string_overrides.append("(%.2f + %.2f)/2" % (calibrated_params[Cf0_string], calibrated_params[Cf1_string]))

        if self_phase or cross_phase:
            search_strings.append('C'+str(c)+'_Ren_extra_phase_correction_list'+electron_transition_string)
            param_string_overrides.append(None)

        if self_unc_phase:
            search_strings.append('C'+str(c)+'_unc_extra_phase_correction_list'+electron_transition_string)
            param_string_overrides.append(None)

        if self_unc_phase_offset:
            search_strings.append('C'+str(c)+'_unc_phase_offset'+electron_transition_string)
            param_string_overrides.append(None)

    write_to_msmt_params.write_to_msmt_params_file(search_strings, param_string_overrides, debug)

################################################################
######              Calibrate ms=-1 frequencies           ######
################################################################


# measure
if f_ms1 and n == 1:
    print 'Calibrate ms=-1 frequencies'


    for c in carbons:
        detuning = detuning_dict[str(c)]
        if n == 1:

            NuclearRamseyWithInitialization_cal(SAMPLE_CFG+'_msm1_freq_C'+str(c), carbon_nr= c, detuning = detuning,debug=debug, el_state = 1)
            # fit
            if not debug:
                f0, uf0 = cr.Carbon_Ramsey(timestamp=None, 
                              offset = 0.5, amplitude = 0.3, x0=0, decay_constant = 1e5, exponent = 2, 
                              frequency = detuning, phase =0, 
                              plot_fit = True, show_guess = False,fixed = [2,3,4],            
                              return_freq = True,
                              return_results = False,
                              title = 'msm1_freq_C'+str(c))
                #update
                qt.exp_params['samples'][SAMPLE]['C'+str(c)+'_freq_1'+electron_transition_string] += -f0 + detuning

                n = stop_msmt()

                #optimize()

    



###############################################################
######              Calibrate ms=0 frequencies           ######
###############################################################
if n == 1 and f_ms0:
    print 'Calibrate ms=0 frequencies'
    # measure
    for c in carbons:
        detuning = detuning_dict[str(c)]
        if n == 1:
            NuclearRamseyWithInitialization_cal(SAMPLE+'_msm0_freq_C'+str(c), carbon_nr= c, 
                                detuning = detuning,debug=debug, el_state = 0)
            # fit
            if not debug:
                f0, uf0 = cr.Carbon_Ramsey(timestamp=None, 
                              offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
                              frequency = detuning, phase =0, 
                              plot_fit = True, show_guess = False,fixed = [2,3,4],            
                              return_freq = True,
                              return_results = False,
                              title = '_msm0_freq_C'+str(c))
                #update
                qt.exp_params['samples'][SAMPLE]['C'+str(c)+'_freq_0'] += -f0 + detuning
                print 'C'+str(c)+'_freq_0'
                print qt.exp_params['samples'][SAMPLE]['C'+str(c)+'_freq_0']

                n = stop_msmt()

                
##################################################################
##### Calibrate extra phase for gate for all 3 carbon spins ######
#################################################################



if n == 1 and self_phase_calibration:
    print 'Calibrate self phases for gates'

    #set all to zero to start with
    for c in carbons:
        if n == 1:
            qt.exp_params['samples'][SAMPLE]['C'+str(c)+'_Ren_extra_phase_correction_list'+electron_transition_string][c] = 0
            # measure
            NuclearRamseyWithInitialization_phase(SAMPLE+'_phase_C'+str(c),debug=debug, carbon_nr= c)
            # fit
            if not debug:
                phi0,u_phi_0,Amp,Amp_u =    cr.Carbon_Ramsey(timestamp=None, 
                                       offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
                                       frequency = 1/360., phase =0, 
                                       plot_fit = True, show_guess = False,fixed = [2,3,4,5],
                                    return_phase = True, return_amp = True,
                                    return_results = False, 
                                    title = 'phase_C'+str(c))
                if Amp < 0:
                    qt.exp_params['samples'][SAMPLE]['C'+str(c)+'_Ren_extra_phase_correction_list'+electron_transition_string][c] = phi0+180
                else:
                    qt.exp_params['samples'][SAMPLE]['C'+str(c)+'_Ren_extra_phase_correction_list'+electron_transition_string][c] = phi0

                print 'C'+str(c)+'_Ren_extra_phase_correction_list['+str(c)+']'
                print qt.exp_params['samples'][SAMPLE]['C'+str(c)+'_Ren_extra_phase_correction_list'+electron_transition_string][c]
                

                n = stop_msmt()


##################################################################
##### Calibrate extra phase for unconditional rotations     ######
#################################################################

if n == 1 and self_unc_phase_offset_calibration:
    print 'Calibrate phase offset for unconditional rotations for carbon spins'

    for c in carbons:
        if n == 1:
            # measure
            qt.exp_params['samples'][SAMPLE]['C'+str(c)+'_unc_phase_offset'+electron_transition_string] = 0
            
            NuclearRamseyWithInitialization_unc_phase(SAMPLE+'_unc_phase_offset_C'+str(c), carbon_nr= c,debug=debug, check_phase_or_offset = 'offset')
            # fit
            if not debug:
                phi0,u_phi_0,Amp,Amp_u =    cr.Carbon_Ramsey(timestamp=None, 
                                       offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
                                       frequency = 1/360., phase =0, 
                                       plot_fit = True, show_guess = False,fixed = [2,3,4,5],
                                    return_phase = True, return_amp = True,
                                    return_results = False, 
                                    title = 'unc_phase_offset_C'+str(c))
                if Amp < 0:
                    qt.exp_params['samples'][SAMPLE]['C'+str(c)+'_unc_phase_offset'+electron_transition_string] = phi0-90 # phi 0 gives -y rotation
                else:
                    qt.exp_params['samples'][SAMPLE]['C'+str(c)+'_unc_phase_offset'+electron_transition_string] = phi0+90

                print 'C'+str(c)+'_unc_phase_offset'+electron_transition_string
                print qt.exp_params['samples'][SAMPLE]['C'+str(c)+'_unc_phase_offset'+electron_transition_string]
                

                n = stop_msmt()

if n == 1 and self_unc_phase_calibration:
    print 'Calibrate extra phase for unconditional rotations for carbon spins'

    for c in carbons:
        if n == 1:

            # measure
            NuclearRamseyWithInitialization_unc_phase(SAMPLE+'_unc_phase_C'+str(c),debug=debug, carbon_nr= c)
            # fit
            if not debug:
                phi0,u_phi_0,Amp,Amp_u =    cr.Carbon_Ramsey(timestamp=None, 
                                       offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
                                       frequency = 1/360., phase =0, 
                                       plot_fit = True, show_guess = False,fixed = [2,3,4,5],
                                    return_phase = True, return_amp = True,
                                    return_results = False, 
                                    title = 'unc_phase_C'+str(c))
                if Amp < 0:
                    qt.exp_params['samples'][SAMPLE]['C'+str(c)+'_unc_extra_phase_correction_list'+electron_transition_string][c] = -phi0+180 
                else:
                    qt.exp_params['samples'][SAMPLE]['C'+str(c)+'_unc_extra_phase_correction_list'+electron_transition_string][c] = -phi0 # Zero phase gives a -Y rotation!

                print 'C'+str(c)+'_unc_extra_phase_correction_list['+str(c)+']'
                print qt.exp_params['samples'][SAMPLE]['C'+str(c)+'_unc_extra_phase_correction_list'+electron_transition_string][c]
                

                n = stop_msmt()



if n == 1 and check_unc_phase_calibration:
    print 'Check calibration of unconditional rotations for carbon spins'

    #set all to zero to start with

    for c in carbons:
        if n == 1:

            # measure
            NuclearRamseyWithInitialization_unc_phase(SAMPLE+'_unc_phase_C'+str(c),debug=debug, carbon_nr= c, check_phase_or_offset = check_phase_or_offset, check_phase = True)
            # fit
            if not debug:
                phi0,u_phi_0,Amp,Amp_u =    cr.Carbon_Ramsey(timestamp=None, 
                                       offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
                                       frequency = 1/360., phase =0, 
                                       plot_fit = True, show_guess = False,fixed = [2,3,4,5],
                                    return_phase = True, return_amp = True,
                                    return_results = True, 
                                    title = 'phase_C'+str(c))
                           

                n = stop_msmt()

########################
######################## Cross-phase calibraiton.
########################


if cross_phase_calibration and n ==1 and len(carbons)>1:
    #set all cross-phases to zero to start with
    estimate_phase=np.zeros([8,8])
    for c in carbons:
        # remove that specific carbon from the list
        carbons_cross = copy.deepcopy(carbons)
        carbons_cross.remove(c)
        # reset phases to 0
        for c_cross in carbons_cross:
            estimate_phase[c,c_cross]=qt.exp_params['samples'][SAMPLE]['C'+str(c)+'_Ren_extra_phase_correction_list'+electron_transition_string][c_cross]
            qt.exp_params['samples'][SAMPLE]['C'+str(c)+'_Ren_extra_phase_correction_list'+electron_transition_string][c_cross] = 0.


if n == 1 and cross_phase_calibration and len(carbons)>1:

    #optimize()

    for c in carbons:
        # remove that specific carbon from the list
        carbons_cross = copy.deepcopy(carbons)
        carbons_cross.remove(c)
        for cross_c in carbons_cross:
            #measure

            Crosstalk_vs2(SAMPLE+ '_phase_cal_gateC'+str(cross_c)+'_measC'+str(c), C_measured = c, C_gate =cross_c ,
                debug = debug, nr_of_gates=1,smart_sweep_pts=True,estimate_phase=estimate_phase[cross_c,c])
            if not debug:
                phi0,u_phi_0,Amp,Amp_u =    cr.Carbon_Ramsey(timestamp=None, 
                                       offset = 0.5, amplitude = 0.5, x0=0, decay_constant = 1e5, exponent = 2, 
                                       frequency = 1/360., phase =0, 
                                       plot_fit = True, show_guess = False,fixed = [2,3,4,5],
                                    return_phase = True,return_amp = True,
                                    return_results = False,
                                    title = 'phase_cal_gateC'+str(cross_c)+'_measC'+str(c))

                # if Amp <0:
                #   phase_list[kk] = (phi0+180)/(kk+1)
        
                #   phase_list[kk] = (phi0)/(kk+1)

                # phase_u_list[kk] = u_phi_0/(kk+1)

                # print phase_list
                # print phase_u_list
                # phase_overview.append(phase_list)

                if Amp <0:
                    qt.exp_params['samples'][SAMPLE]['C'+str(cross_c)+'_Ren_extra_phase_correction_list'+electron_transition_string][c] = phi0+180
                else:
                    qt.exp_params['samples'][SAMPLE]['C'+str(cross_c)+'_Ren_extra_phase_correction_list'+electron_transition_string][c] = phi0
                #update
                print 'C'+str(cross_c)+'_Ren_extra_phase_correction_list['+str(c)+']'
                print qt.exp_params['samples'][SAMPLE]['C'+str(cross_c)+'_Ren_extra_phase_correction_list'+electron_transition_string][c]
                
                if n == 1:
                    n = stop_msmt()
                if n == 0:
                    break

        if n == 1:
            n = stop_msmt()
        if n == 0:
            break

#################################
###### Print final results ######
#################################
print 
print 'Finished C13 calibration measurements'
print 'Values found:'
print

if f_ms1:
    print '#########################'
    print 'ms = 1 frequencies'
    for c in carbons:
        print 'Carbon '+str(c)
        print qt.exp_params['samples'][SAMPLE]['C'+str(c)+'_freq_1'+electron_transition_string]
    print
    print '#########################'

print

if f_ms0:
    print '#########################'
    print 'ms = 0 frequencies'
    print
    for c in carbons:
        print 'Carbon '+str(c)
        print qt.exp_params['samples'][SAMPLE]['C'+str(c)+'_freq_0']
    print
    print '#########################'
print

if self_phase_calibration:
    print '#########################'
    print 'self phases'
    print
    for c in carbons:
        print 'C'+str(c)+'_Ren_extra_phase_correction_list'+electron_transition_string+'['+str(c)+']'
        print qt.exp_params['samples'][SAMPLE]['C'+str(c)+'_Ren_extra_phase_correction_list'+electron_transition_string][c]
    print
    print '#########################'
print

if self_unc_phase_offset_calibration:
    print '#########################'
    print 'self unconditional phases'
    print
    for c in carbons:
        print ['C'+str(c)+'_unc_phase_offset'+electron_transition_string]
        print qt.exp_params['samples'][SAMPLE]['C'+str(c)+'_unc_phase_offset'+electron_transition_string]
    print
    print '#########################'
print

if self_unc_phase_calibration:
    print '#########################'
    print 'self unconditional phases'
    print
    for c in carbons:
        print 'C'+str(c)+'_unc_extra_phase_correction_list'+electron_transition_string+'['+str(c)+']'
        print qt.exp_params['samples'][SAMPLE]['C'+str(c)+'_unc_extra_phase_correction_list'+electron_transition_string][c]
    print
    print '#########################'
print

if cross_phase_calibration and len(carbons)>1:
    print '#########################'
    print 'cross phases'
    print
    for c in carbons:
        carbons_cross = copy.deepcopy(carbons)
        carbons_cross.remove(c)
        for cross_c in carbons_cross:
            print 'C'+str(c)+'_Ren_extra_phase_correction_list'+electron_transition_string+'['+str(cross_c)+']'
            print qt.exp_params['samples'][SAMPLE]['C'+str(c)+'_Ren_extra_phase_correction_list'+electron_transition_string][cross_c]

# print phase_overview

# write to msmt_params.py if the calibration was finished succesfully.
if n== 1 and not debug:
    update_msmt_params(carbons,f_ms0,f_ms1,True,cross_phase_calibration,self_unc_phase_calibration,self_unc_phase_offset_calibration,debug)
else:
    print 'Sequence was aborted: I did not save the calibration results'


if use_queue:
    execfile(r'D:\measuring\measurement\scripts\Decoupling_Memory\queue.py')
