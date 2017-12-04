"""
Script for a simple Decoupling sequence
Based on Electron T1 script
Made by Adriaan Rol
"""
import numpy as np
import qt
import msvcrt
import measurement.scripts.QEC as ssro
#import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD
import measurement.scripts.mbi.mbi_funcs as funcs

#### for pulse calib

from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
reload(pulsar_msmt)
from measurement.scripts.espin import espin_funcs
reload(espin_funcs)
from measurement.lib.measurement2.adwin_ssro import pulse_select as ps
reload(ps)
from measurement.lib.pulsar import pulselib
reload(pulselib)


from analysis.lib.tools import toolbox
from analysis.lib.fitting import dark_esr_auto_analysis; reload(dark_esr_auto_analysis)
from analysis.lib.m2.ssro import ssro as ssro_analysis
reload(ssro_analysis)

magnet_X_scanner = qt.instruments['conex_scanner_X']
magnet_Y_scanner = qt.instruments['conex_scanner_Y']
magnet_Z_scanner = qt.instruments['conex_scanner_Z']




#reload all parameters and modules
execfile(qt.reload_current_setup)



######3



reload(DD)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']
current_f_msm1 = qt.exp_params['samples'][SAMPLE]['ms-1_cntr_frq']
# temperature_sensor = qt.instruments['kei2000']

def qstop(sleep=2):
    print '--------------------------------'
    print 'press q to stop measurement loop'
    print '--------------------------------'
    qt.msleep(sleep)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        return True

def SimpleDecoupling(name, sweep = 'N',N=4,end=100e-3,nr_list=[1], shutter=0, XY_scheme=8, reps=500,debug=False, MW_amplitude=0.705,delta_tau=0.2e-9):

    m = DD.SimpleDecoupling(name)
    funcs.prepare(m)

    m.params['use_shutter'] = shutter
    m.params['reps_per_ROsequence'] = reps #Repetitions of each data point
    m.params['Initial_Pulse'] ='x'
    # m.params['temp'] = temperature_sensor.get_readlastval()
    m.params['DD_in_eigenstate'] = False
    #m.params['Hermite_pi_amp']= MW_amplitude

    
    if N==1:
        m.params['Final_Pulse'] ='x'
    else:
        m.params['Final_Pulse'] ='-x'
    ### Calculate tau larmor
    #f_larmor = (m.params['ms+1_cntr_frq']-m.params['zero_field_splitting'])*m.params['g_factor_C13']/m.params['g_factor']
    f_larmor = (m.params['zero_field_splitting']-m.params['ms-1_cntr_frq'])*m.params['g_factor_C13']/m.params['g_factor']
    tau_larmor = (1/f_larmor) #rounds to ns
    #tau_larmor =2.0e-9
    # tau_larmor= 9.52e-6+2*2.314e-6
    

    # tau_larmor = 2.316e-6
    #tau_larmor = 2.524e-6
    print 'tau_larmor = %s' %tau_larmor


    if sweep == 'tau':

        
        
        ### commented out for loop functionalities
        # pts = 20
        # start   = 0e-3 + tau_larmor*(2*Number_of_pulses) 
        # end     = 60e-3 
        # nr_list = np.linspace(start/(2*Number_of_pulses)/tau_larmor, end/(2*Number_of_pulses)/tau_larmor, pts).astype(int)
        
        Number_of_pulses = N
        print nr_list*tau_larmor
        #tau_list =np.array([round(x*tau_larmor*0.25e9) / (0.25e9) for x in nr_list])
        tau_list =np.array([round(x*tau_larmor*0.5e9) / (0.5e9) for x in nr_list])
        tau_list = tau_list 

        #to check collapses
        # tau_list = tau_list-0.25*tau_larmor

        print nr_list
        print 'tau_list is  '+str(tau_list)
        print 2*tau_larmor

        m.params['pts']              = len(tau_list)
        m.params['Number_of_pulses'] = Number_of_pulses*np.ones(m.params['pts']).astype(int)
        m.params['tau_list']         = tau_list
        m.params['sweep_pts']        =  2*Number_of_pulses*tau_list*1e3
        print m.params['sweep_pts']
        m.params['sweep_name']       = 'total evolution time (ms)'
        if XY_scheme == 16:
            m.params['Decoupling_sequence_scheme']='repeating_T_elt_XY16'
        elif XY_scheme == 8:
            m.params['Decoupling_sequence_scheme']='repeating_T_elt'
        else:
            raise Exception('XY Scheme not recognized')
        #m.params['Decoupling_sequence_scheme']='single_block'


        m.autoconfig()
        funcs.finish(m, upload =True, debug=debug)

def SimpleDecoupling_Single_Block(name, sweep = 'N',N=4,end=100e-3,nr_list=[1], shutter=0, XY_scheme=8, reps=500,debug=False):

    m = DD.SimpleDecoupling_Single_Block(name)
    funcs.prepare(m)

    # Details for multiple C13 Adwin script 
    m.params['use_shutter'] = shutter

    m.params['reps_per_ROsequence'] = reps #Repetitions of each data point
    m.params['Initial_Pulse'] ='x'
    m.params['Final_Pulse'] ='-x'
    print 'XY_scheme', XY_scheme
    m.params['Number of pulses in XY scheme'] = XY_scheme
    m.params['DD_in_eigenstate'] = False
    # m.params['temp'] = temperature_sensor.get_readlastval()
    ### Calculate tau larmor
    #f_larmor = (m.params['ms+1_cntr_frq']-m.params['zero_field_splitting'])*m.params['g_factor_C13']/m.params['g_factor']
    f_larmor = (m.params['zero_field_splitting']-m.params['ms-1_cntr_frq'])*m.params['g_factor_C13']/m.params['g_factor']
    tau_larmor = (1/f_larmor)#rounds to ns
    # tau_larmor=1e-9
    #tau_larmor =9.668e-6
    # tau_larmor= 9.52e-6+2*2.314e-6

    print 'tau_larmor = %s' %tau_larmor
    #tau_larmor = 2.3147e-6  
    #tau_larmor = 2.524e-6



    if sweep == 'tau':


        Number_of_pulses = N
        tau_list =np.array([round(x*tau_larmor*1.e9) / (1.e9) for x in nr_list])
        tau_list = tau_list
        #tau_list = nr_list*tau_larmor 

        print 'nr_list is '+str(nr_list)
        print 'tau_list is'+ str(tau_list)
        print 2*tau_larmor
        m.params['pts']              = len(tau_list)
        m.params['Number_of_pulses'] = Number_of_pulses*np.ones(m.params['pts']).astype(int)
        m.params['tau_list']         = tau_list
        m.params['sweep_pts']        =  2*Number_of_pulses*tau_list*1e3
        print m.params['sweep_pts'] 
        m.params['sweep_name']       = 'total evolution time (ms)'

        m.autoconfig()
        funcs.finish(m, upload =True, debug=debug)


def take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=2,Single_Block=False,shutter=False,XY_scheme=8, reps=500, optimize=True,debug=False,MW_amplitude=0.705,delta_tau=0.1e-9):
    ## loop function for data acquisition.
    # GreenAOM.set_power(20e-6)
    # counters.set_is_running(1)
    # optimiz0r.optimize(dims = ['x','y','z','x','y'], int_time = 120)
    # stools.turn_off_all_lasers()

    Continue_bool = True 


    larmor_steps = pts*larmor_step ### how many steps in in tau_larmor are taken, the total experiment time is divided into smaller periods
    nr_of_runs = int(np.floor((larmor_max-larmor_min)/larmor_steps))
    print 'nrofruns', nr_of_runs
    if qstop(sleep=3):
            Continue_bool = False
    else:
        for n in range(nr_of_runs):
            if qstop(sleep=3):
                Continue_bool = False
                break
            if optimize and not debug:
                GreenAOM.set_power(7e-6)
                counters.set_is_running(1)
                optimiz0r.optimize(dims = ['x','y','z'], int_time = 120)
                stools.turn_off_all_lasers()

            print 'n', n
            nr_list = np.arange(larmor_min+n*larmor_steps,larmor_min+(n+1)*larmor_steps,larmor_step)
            print 'nr_list', nr_list
            if Single_Block:
                if shutter:
                    adwin.start_set_dio(dio_no=4,dio_val=0)
                    SimpleDecoupling_Single_Block(SAMPLE+'_SB_ShutterYES_XY'+str(XY_scheme)+'_sweep_tau_N_'+str(N)+'_LarmorNR'+'&'.join([str(s) for s in nr_list]) +'_part'+str(n+1),sweep='tau',N=N,nr_list = nr_list, shutter=1, XY_scheme=XY_scheme, reps=reps,debug=debug)
                    adwin.start_set_dio(dio_no=4,dio_val=0)
                else:
                    SimpleDecoupling_Single_Block(SAMPLE+'_SB_XY'+str(XY_scheme)+'_sweep_tau_N_'+str(N),sweep='tau',N=N,nr_list = nr_list, XY_scheme=XY_scheme, reps=reps,debug=debug)
            else:
                if shutter:
                    adwin.start_set_dio(dio_no=4,dio_val=0)
                    SimpleDecoupling(SAMPLE+'_RepT_ShutterYES_XY'+str(XY_scheme)+'sweep_tau_N_'+str(N)+'_part'+str(n+1),sweep='tau',N=N,nr_list = nr_list,reps=reps, XY_scheme=XY_scheme, shutter=1, debug=debug)
                    adwin.start_set_dio(dio_no=4,dio_val=0)
                else:
                    SimpleDecoupling(SAMPLE+'_RepT_ShutterNO_XY'+str(XY_scheme)+'sweep_tau_N_'+str(N)+'_part'+str(n+1),sweep='tau',N=N,nr_list = nr_list,reps=reps, XY_scheme=XY_scheme, shutter=0, debug=debug, MW_amplitude=MW_amplitude)

    ### get the remaining larmor revivals in.
    if Continue_bool:
        nr_list = np.arange(larmor_min+larmor_steps*nr_of_runs,larmor_max+1,larmor_step)

        if optimize and not debug:
            GreenAOM.set_power(5e-6)
            counters.set_is_running(1)
            optimiz0r.optimize(dims = ['x','y','z','x','y'], int_time = 200)
            stools.turn_off_all_lasers()

        print 'nr_list', nr_list
        if Single_Block:
            if shutter:
                adwin.start_set_dio(dio_no=4,dio_val=0)
                SimpleDecoupling_Single_Block(SAMPLE+'_SB_XY'+str(XY_scheme)+'_sweep_tau_N_'+str(N),sweep='tau',N=N,nr_list = nr_list, XY_scheme=XY_scheme, reps=reps,debug=debug)
                adwin.start_set_dio(dio_no=4,dio_val=0)
            else:
                SimpleDecoupling_Single_Block(SAMPLE+'_SB_XY'+str(XY_scheme)+'_sweep_tau_N_'+str(N),sweep='tau',N=N,nr_list = nr_list, XY_scheme=XY_scheme, reps=reps,debug=debug)

        else:
            if shutter:
                adwin.start_set_dio(dio_no=4,dio_val=0)
                SimpleDecoupling(SAMPLE+'_RepT_ShutterYES_XY'+str(XY_scheme)+'sweep_tau_N_'+str(N)+'_part'+str(1+nr_of_runs),sweep='tau',N=N,nr_list = nr_list,reps=reps, XY_scheme=XY_scheme, shutter=1, debug=debug)
                adwin.start_set_dio(dio_no=4,dio_val=0)
            else:
                SimpleDecoupling(SAMPLE+'_RepT_ShutterNO_XY'+str(XY_scheme)+'sweep_tau_N_'+str(N)+'_part'+str(1+nr_of_runs),sweep='tau',N=N,nr_list = nr_list,reps=reps, XY_scheme=XY_scheme, shutter=0, debug=debug, MW_amplitude=MW_amplitude,delta_tau=delta_tau)

    return Continue_bool
    ### optimize position for the following run.



# for ssro measurement
def ssrocalibration(name,RO_power=None,SSRO_duration=None):
    m = ssro.AdwinSSRO('SSROCalibration_'+name)
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])

    if RO_power != None:
        m.params['Ex_RO_amplitude'] = RO_power
    if SSRO_duration != None:
        m.params['SSRO_duration'] = SSRO_duration

    # ms = 0 calibration
    m.params['Ex_SP_amplitude'] = 0
    m.run()
    m.save('ms0')

    # ms = 1 calibration
    m.params['SP_duration']     = 500
    m.params['A_SP_amplitude']  = 0.
    m.params['Ex_SP_amplitude'] = 3e-9
    m.run()
    m.save('ms1')
    m.finish()

def darkesr(name, range_MHz, pts, reps, power, MW_power, pulse_length):

    m = pulsar_msmt.DarkESR_Switch(name)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['111_1_sil18']['pulses']) #Added to include the MW switch MA

    # m.params['temp'] = temperature_sensor.get_readlastval()
    m.params['magnet_position'] = magnet_Z_scanner.GetPosition()

    m.params['mw_frq']      = m.params['ms-1_cntr_frq']-43e6 #MW source frequency

    m.params['mw_power']    = MW_power
    m.params['repetitions'] = reps

    m.params['ssbmod_frq_start'] = 43e6 - range_MHz*1e6 ## first time we choose a quite large domain to find the three dips (15)
    m.params['ssbmod_frq_stop']  = 43e6 + range_MHz*1e6
    m.params['pts'] = pts
    m.params['pulse_length'] = pulse_length
    m.params['ssbmod_amplitude'] = power #0.01

    m.params['sweep_pts'] = (np.linspace(m.params['ssbmod_frq_start'],
                    m.params['ssbmod_frq_stop'], m.params['pts']) 
                    + m.params['mw_frq'])*1e-9

    m.autoconfig()
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()


def optimize_magnetic_field():

    safemode            = False    # If True then manual confirmation is needed befor each magnet movement
    optimization_target = 15     # Target difference frequency in kHz , first (03.08) was 10 then 7 then 10 again
    field_gradient      = 0.100     
    only_fine           = False

    ### Settings for the first coarse steps
    coarse_range          = 7.5     #Common: 10 MHz
    coarse_pts            = 101     #Common: 121
    coarse_reps           = 750     #Common: 500
    coarse_amplitude      = 0.08
    coarse_pulse_length   = 3e-6
    coarse_MW_power       = -1

    ### Settings for the fine steps
    fine_range          = 0.600
    fine_pts            = 81
    fine_reps           = 2000
    fine_amplitude      = 0.08/3 
    fine_pulse_length   = 9e-6
    fine_MW_power       = -1

    
    
    
    coarse_range   = fine_range     
    coarse_pts     = fine_pts    
    coarse_reps    = fine_reps   
    coarse_pulse_length = fine_pulse_length
    coarse_amplitude    = fine_amplitude 
    coarse_MW_power = fine_MW_power




## Run optimizor ##############
    GreenAOM.set_power(10e-6)
    counters.set_is_running(True)
    optimiz0r.optimize(dims=['x','y','z'], int_time=300)

    GreenAOM.set_power(10e-6)
    counters.set_is_running(True)
    optimiz0r.optimize(dims=['x','y','z'], int_time=300)

    name = 'SSRO_calib'
    ssrocalibration(name)

   ### SSRO Analysis
    ssro_analysis.ssrocalib()

#########################################

    f0 = []; u_f0 = []; delta_f0 =[]; iterations_list =[]; magnet_postion_list =[]; fit_failed_list=[]

    darkesr('magnet_optimize_init', range_MHz=coarse_range, pts=coarse_pts, reps=coarse_reps, 
                power= coarse_amplitude, MW_power = coarse_MW_power, pulse_length=coarse_pulse_length)

    # Do the fitting, returns in MHz, input in GHz
     
    f0_temp, u_f0_temp = dark_esr_auto_analysis.analyze_dark_esr_double(do_plot=True)
    delta_f0_temp = -f0_temp*1e6+current_f_msm1*1e-3    # in kHz

    # Magnet start position
    Start_position = magnet_Z_scanner.GetPosition()

    # List all the measured values
    iterations = 0
    f0.append(f0_temp)
    u_f0.append(u_f0_temp)
    delta_f0.append(delta_f0_temp)
    magnet_postion_list.append(Start_position)


    while abs(delta_f0_temp) > optimization_target:

            ## Determine new postition
            current_position = magnet_Z_scanner.GetPosition()
            delta_position = delta_f0_temp/field_gradient*1e-6
            move_to_position = current_position + delta_position

            print 'Target frequency =' + str(current_f_msm1)
            print 'Measured frequency = ' + str(f0_temp) + ' GHz +/- ' + str(u_f0_temp*1e6) + ' kHz'
            print 'Difference = ' + str(delta_f0_temp) + ' kHz'
            print 'Current magnet position = ' + str(current_position) + ' mm'
            print 'Move to position          ' + str(move_to_position) + ' mm'
            print 'By                        ' + str(delta_position*1e6) + 'nm'
            

            # if u_f0_temp*1e6 > 15:
            #     print 'Uncertainty larger than 15 kHz, fit failed'
            #     fit_failed = 1
            # else: 
            #     fit_failed = 0

            # fit_failed_list.append(fit_failed)
            
            ## Actually move the magnet
          

            if u_f0_temp*1e6 < 15:
       
                ## Limit the maximum movement range
                if move_to_position < 0.042 or move_to_position > 0.072:
                    print 'movement is going out of range, abort!!!'
                    break

                print 'Target frequency =' + str(current_f_msm1)
                print 'Measured frequency = ' + str(f0_temp) + ' GHz +/- ' + str(u_f0_temp*1e6) + ' kHz'
                print 'Difference = ' + str(delta_f0_temp) + ' kHz'
                print 'Current magnet position = ' + str(current_position) + ' mm'
                print 'Move to position          ' + str(move_to_position) + ' mm'
                print 'By                        ' + str((move_to_position-current_position)*1e6) + 'nm'

                if safemode == True: 
                    print '\a\a\a' 
                    ri = raw_input ('move magnet? (y/n)')
                    if str(ri) != 'y': 
                        break
                
                ## Actually move the magnet
                magnet_Z_scanner.MoveRelative(delta_position)
                print 'moving magnet...'

            else:
                print 'Uncertainty larger than 15 kHz, fit failed'
                break

            print '--------------------------------'
            print 'press q to stop measurement loop'
            print '--------------------------------'
            qt.msleep(2)

            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')) or abs(move_to_position-current_position) < 0.000025:
                break

            darkesr('magnet_optimize_step_' + str(iterations), range_MHz=fine_range, pts=fine_pts, reps=fine_reps, 
                power = fine_amplitude, MW_power = fine_MW_power, pulse_length=fine_pulse_length)

            f0_temp, u_f0_temp = dark_esr_auto_analysis.analyze_dark_esr_double(do_plot=True)
            delta_f0_temp = -f0_temp*1e6+current_f_msm1*1e-3

            iterations += 1


def calibrate_pi_pulse(name, multiplicity=1,RO_basis = 'Z', debug=False, mw2=False, wait_time_pulses=15000e-9, **kw):

    
    m = pulsar_msmt.GeneralPiCalibrationSingleElement(name+str(multiplicity))
    
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    pulse_shape = m.params['pulse_shape']
    pts = 20

    m.params['pts'] = pts
    
    ps.X_pulse(m) #### update the pulse params depending on the chosen pulse shape.

    m.params['repetitions'] = 1600 if multiplicity == 1 else 2000
    rng = 0.15 if multiplicity == 1 else 0.04


    ### comment NK: the previous parameters for MW_duration etc. were not used anywhere in the underlying measurement class.
    ###             therefore, I removed them
    if mw2:
        m.params['MW_pulse_amplitudes'] = m.params['mw2_fast_pi_amp'] + np.linspace(-rng, rng, pts)
    else: 
        m.params['MW_pulse_amplitudes'] = m.params['fast_pi_amp'] + np.linspace(-rng, rng, pts)  
            
    print m.params['MW_pulse_amplitudes'] 
    
    m.params['multiplicity'] = np.ones(pts)*multiplicity
    m.params['wait_time_pulses']=wait_time_pulses
    m.params['RO_basis'] = RO_basis
    m.params['delay_reps'] = 0
    # for the autoanalysis
    m.params['sweep_name'] = 'MW amplitude (V)'
   
    m.params['sweep_pts'] = m.params['MW_pulse_amplitudes']
    m.params['wait_for_AWG_done'] = 1

    m.MW_pi=ps.X_pulse(m)
    m.MW_pi2=ps.Xpi2_pulse(m)

    # m.MW_pi = pulse.cp(ps.mw2_X_pulse(m), phase = 0) if mw2 else pulse.cp(ps.X_pulse(m), phase = 0)
    # m.MW_pi = pulse.cp(ps.mw2_X_pulse(m), phase = 0) if mw2 else pulse.cp(ps.X_pulse(m), phase = 0)
    espin_funcs.finish(m, debug=debug, pulse_pi=m.MW_pi,pulse_pi2=m.MW_pi2)

# def darkesr(name, range_MHz, pts, reps, power, MW_power, pulse_length):

#     m = pulsar_msmt.DarkESR_Switch(name)
#     m.params.from_dict(qt.exp_params['samples'][SAMPLE])
#     m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
#     m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
#     m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
#     m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
#     m.params.from_dict(qt.exp_params['protocols']['111_1_sil18']['pulses']) #Added to include the MW switch MA

#     m.params['temp'] = temperature_sensor.get_readlastval()
#     m.params['magnet_position'] = magnet_Z_scanner.GetPosition()

#     m.params['mw_frq']      = m.params['ms-1_cntr_frq']-43e6 #MW source frequency

#     m.params['mw_power']    = MW_power
#     m.params['repetitions'] = reps

#     m.params['ssbmod_frq_start'] = 43e6 - range_MHz*1e6 ## first time we choose a quite large domain to find the three dips (15)
#     m.params['ssbmod_frq_stop']  = 43e6 + range_MHz*1e6
#     m.params['pts'] = pts
#     m.params['pulse_length'] = pulse_length
#     m.params['ssbmod_amplitude'] = power #0.01

#     m.params['sweep_pts'] = (np.linspace(m.params['ssbmod_frq_start'],
#                     m.params['ssbmod_frq_stop'], m.params['pts']) 
#                     + m.params['mw_frq'])*1e-9

#     m.autoconfig()
#     m.generate_sequence(upload=True)
#     m.run()
#     m.save()
#     m.finish()




############################################################################################################




if __name__ == '__main__':
    n=0
    Total_time = 0.
    debug = True
    Cont = True
    Run_Msmt = True
    optimize = True
    magnet_postion_list =[]


    n=1

    # N_list=[1024,2048]#[16,32,64,128,256,512]
    # larmor_max_list=[2400,1200,600,300,200,150,120,100,90,75]
    # larmor_step_list=[120/2,60/2,30/2,7,5,4,3,2,2,2]
    #pts_list=6*[4]+9*[2]+13*[1]

    #larmor_min_list=[3,43,61,75,87,96,3,30,42,52,60,67,73,79,84,3,21,30,37,43,48,52,57,61,64,68,72,75]#,3600,3800,4000,4200,4600]
    #larmor_max_list=[43,61,75,87,96,106,30,42,52,60,67,73,79,84,90,21,30,37,43,48,52,57,61,64,68,72,75,78]#,4200,4600,4800]

    # larmor_min_list=[1,17,25,30,35,39,43,46,49,52,55]
    # larmor_max_list=[16,24,29,34,38,42,45,48,51,54,57]

    # larmor_min_list=[1,11,17,21,25,29,33,37,41]
    # larmor_max_list=[10,16,20,24,28,32,36,40,44]

    larmor_min_list=[1,11,17,21,25,28,32,36,40]
    larmor_max_list=[10,16,20,24,27,31,35,39,43]


    #larmor_min_list=[7,17,17,21,21,21,21,21,21]
    #larmor_max_list=[7,17,17,21,21,21,21,21,21]

    # larmor_min_list=[3,22,31,38,44,49,53,58,62,65,69,73,76]#,3600,3800,4000,4200,4600]
    # larmor_max_list=[21,30,37,43,48,52,57,61,64,68,72,75,78]#,4200,4600,4800]

    #N_list=13*[2048]
    #pts_list=13*[1]
    #N_list=6*[512]+9*[1024]+13*[2048]
    #N_list = [32,64,128,512,1024,2048,3072,4096,6144]
    #N_list= [8192,8192,10240,10240,12288,12288]
    #larmor_min_list=[21,22,21,22,21,22]
    #larmor_max_list=[21,22,21,22,21,22]

    # #larmor_max_list=[75,75,75,75]
    # larmor_step_list=[2,2,2,2]
    # pts_list=[4,4,4,4]
    #steps = 6*[40e-3]

    N_list=[1024]

    for jj in range(0,1):
        for ii in range(0,len(N_list)):
            # magnet_X_scanner.MoveRelative(steps[ii])
            # Start_position = magnet_X_scanner.GetPosition()
            # magnet_postion_list.append(Start_position)
            # optimize_magnetic_field()
            MW_amplitude = 0.92+jj*.000
            delta_tau= ii*0.2e-9*0.0

            if n==1 and Cont:
                N = N_list[ii] ### number of pulses
                pts = 1#pts_list[ii] ### number of points per loading of the AWG (100)
                larmor_max = 10# 29500+100*(ii+1)
                larmor_min = 4#29500+100*ii#larmor_min_list[ii]
                larmor_step = 4 #20
                reps =400

                Number_of_pulses = N
                nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
                Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.3158e-6*larmor_min,2*Number_of_pulses*2.3158e-6*larmor_max,nr_of_runs)) /3600.
                print Total_time

                # if ii%5 == 0:
                #     optim=True

                # else:
                #     optim=False


                if Run_Msmt:
                   
                    Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=False,Single_Block=False,shutter=False,XY_scheme=8,reps=reps,debug=False,MW_amplitude=MW_amplitude,delta_tau=delta_tau)
        
                    #if ii % 3 == 2 :
                    # name = 'SSRO_calib'
                    # ssrocalibration(name)
                    # ssro_analysis.ssrocalib()
                    # optimize_magnetic_field()
                   # calibrate_pi_pulse(SAMPLE_CFG + 'Pi', multiplicity =11, debug = False, mw2=False,wait_time_pulses=15000e-9)


    # for jj in range(0,1):
    #     for ii in range(0,7):
    #         MW_amplitude = 0.92+jj*.000
    #         if n==1 and Cont:
    #             N = 256### number of pulses
    #             pts = pts_list[ii] ### number of points per loading of the AWG
    #             larmor_max = larmor_max_list[ii]
    #             larmor_min = larmor_min_list[ii]
    #             larmor_step = larmor_step_list[ii]
    #             reps = 2000

    #             Number_of_pulses = N
    #             nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
    #             Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.
    #             print Total_time

    #             # if ii%5 == 0:
    #             #     optim=True

    #             # else:
    #             #     optim=False


    #             if Run_Msmt:
                   
    #                 Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=False,Single_Block=False,shutter=False,XY_scheme=8,reps=reps,debug=False,MW_amplitude=MW_amplitude)
    #                 name = 'SSRO_calib'
    #                 ssrocalibration(name)
    #                 ssro_analysis.ssrocalib()
    #                 optimize_magnetic_field()




    n=0
    if n==1 and Cont:
        N = 1024 ### number of pulses
        pts = 2 ### number of points per loading of the AWG
        larmor_max = 20 ### the order of the last revival
        larmor_min = 2
        larmor_step = 4
        reps = 800

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.
        
        print Total_time

        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=False,Single_Block=False,shutter=False,XY_scheme=8,reps=reps,debug=False)

    n=0
    if n==1 and Cont:
        N = 128
        pts = 30
        larmor_max = 100
        larmor_min = 4
        larmor_step = 10
        reps = 800

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.

        print Total_time

        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=False,Single_Block=False,shutter=False,XY_scheme=8,reps=reps,debug=False)
    n=0

    if n==1 and Cont:
        N = 32
        pts = 40
        larmor_max = 222
        larmor_min = 2
        larmor_step = 5
        reps = 800

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.

        print Total_time

        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=optimize,Single_Block=False,shutter=True,XY_scheme=8,reps=reps,debug=debug)


    n=0
    if n==1 and Cont:
        N = 16
        pts = 60
        larmor_max = 270
        larmor_min = 2
        larmor_step = 6
        reps = 800

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.

        print Total_time

        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=optimize,Single_Block=False,shutter=False,XY_scheme=8,reps=reps,debug=debug)


    n=0
    n=0  
    if n==1 and Cont:
        N = 16
        pts = 70
        larmor_max = 2 #380
        larmor_min = 2
        larmor_step = 6
        reps = 800

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.

        print Total_time

        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=optimize,Single_Block=True,shutter=False,XY_scheme=4,reps=reps,debug=debug)


    n=0      
    if n==1 and Cont:
        N = 4
        pts = 70
        larmor_max = 352
        larmor_min = 2
        larmor_step = 6
        reps = 800

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.

        print Total_time

        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=optimize,Single_Block=False,shutter=False,XY_scheme=8,reps=reps,debug=debug)
    

    n=0           
    if n==1 and Cont:
        N = 2
        pts = 70
        larmor_max = 450
        larmor_min = 2
        larmor_step = 8
        reps = 800

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.

        print Total_time

        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=optimize,Single_Block=False,shutter=True,XY_scheme=8,reps=reps,debug=debug)
         

    n=0


    if n==1 and Cont:
        N = 1
        pts = 70
        larmor_max = 602
        larmor_min = 2
        larmor_step = 1
        reps = 800
        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.

        print 'total time is '+ str(Total_time)

        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=optimize,Single_Block=False,shutter=False,XY_scheme=8,reps=reps,debug=debug)
      
    n=0      
    ######
    # Test msmt
    #######

    # N = 1024
    # pts = 2
    # larmor_max = 3
    # larmor_min = 3

    # take_DD_Data(larmor_min,larmor_max,N,pts,Single_Block=True)
    # take_DD_Data(larmor_min,larmor_max,N,pts,Single_Block=True,shutter=True)
    # take_DD_Data(larmor_min,larmor_max,N,pts,Single_Block=False)

    # n=0
    # '''
    # Difference is 4515 between two pulses
    # Between start and first 2256
    # 2258
    # '''
    ###
    # 128 pi - pulses
    # estimated T_coh = 25.4 ms @ T_Hahn approximately 1 ms
    #######




    n=0
    ### need to exclude the first larmor revival, timing is too short when using the MW switch.
    ### measurement loop for several larmor revivals
    if n==1 and Cont:
        N = 128
        pts = 20
        larmor_max = 151
        larmor_min = 2
        larmor_step = 2
        reps = 800

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.

        print Total_time

        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=optimize,Single_Block=False,shutter=False,XY_scheme=8,reps=reps,debug=debug)

    n=0
    ##############################
    ##############################

    #######
    # 256 pi - pulses
    # estimated T_coh = 40 ms @ T_Hahn approximately 1 ms
    # sweep until 100 ms overall evolution time --> 100/(2.315*e-3*2*256) = 84....
    # --> sweep until tau = 85*tau_larmor.
    #######

    if n==1 and Cont:
        N = 256 ### number of pulses
        pts = 10 ### number of points per loading of the AWG
        larmor_max = 131 ### the order of the last revival
        larmor_min = 2
        larmor_step = 1
        reps = 800

        '''Start at larmor_min = 1'''
        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.

        print Total_time

        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=optimize,Single_Block=False,shutter=True,XY_scheme=8,reps=reps,debug=debug)

    
    ##############################
    ##############################

    #######
    # 512 pi - pulses
    # estimated T_coh = 64 ms @ T_Hahn approximately 1 ms
    # sweep until 130 ms overall evolution time --> 140/(2.315*e-3*2*512) = 59....
    # --> sweep until tau = 59*tau_larmor.
    #######
 
    # ### measurement loop for several larmor revivals

    n=0
    if n == 1 and Cont:
        N = 512 ### number of pulses
        pts = 5 ### number of points per loading of the AWG
        larmor_max = 115 ### the order of the last revival
        larmor_min = 2
        larmor_step = 1
        reps = 800

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.
        
        print Total_time

        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=False,Single_Block=False,shutter=False,XY_scheme=8,reps=reps,debug=debug)


    n=0
    ##############################
    ##############################
  
    #######
    # 1024 pi - pulses
    # estimated T_coh = 101 ms @ T_Hahn approximately 1 ms
    # sweep until 200 ms overall evolution time --> 200/(2.315*e-3*2*1024) = 42...
    # --> sweep until tau = 61*tau_larmor.
    #######

    # ### measurement loop for several larmor revivals
    
    #execfile(r'D:\measuring\measurement\scripts\Decoupling_Memory\queue.py')


    ##############################
    ##############################
    
    #######
    # 2048 pi - pulses
    # estimated T_coh = 161 ms @ T_Hahn approximately 1 ms
    # sweep until 300 ms overall evolution time --> 300/(2.315*e-3*2*2048) = 31.6
    # --> sweep until tau = 61*tau_larmor.
    #######

   
    
    
    n = 0
    ### measurement loop for several larmor revivals
    if n==1 and Cont:
        N = 2048 ### snumber of pulses
        pts = 1 ### number of points per loading of the AWG
        larmor_max = 66 ### the order of the last revival
        larmor_min = 2
        larmor_step = 1
        reps = 800

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += 2.*reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.
        print Total_time

        # Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=optimize,Single_Block=True,shutter=False,XY_scheme=8,reps=reps)
        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=optimize,Single_Block=False,shutter=True,XY_scheme=8,reps=reps,debug=debug)
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=optimize,Single_Block=True,shutter=True,XY_scheme=8,reps=reps,debug=debug)
        # Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=optimize,Single_Block=False,shutter=False,XY_scheme=8,reps=reps)
    n = 0
    #execfile(r'D:\measuring\measurement\scripts\Decoupling_Memory\queue.py')
    #######
    # 4096 pi - pulses
    # estimated T_coh = 256 ms @ T_Hahn approximately 1 ms
    # sweep until 500 ms overall evolution time --> 500/(2.315*e-3*2*4096) = 27
    # --> sweep until tau = 61*tau_larmor.
    #######
    if n==1 and Cont:
        N = 4096 ### number of pulses
        pts = 1 ### number of points per loading of the AWG
        larmor_max = 51
        larmor_min = 31

        Cont = take_DD_Data(larmor_min,larmor_max,N,pts,Single_Block=True,shutter=True,XY_scheme=16)

    '''
    Stel je hebt 10 punten
    stopts punt 3
    start punt 7
    delta = 4
    stopt punt 7
    9-7 = 2
    start punt 2


    '''


    '''
    Rep Tr
    between pi2 and end 1472
    number of tau = 4
    between end and first pi 1390

    between pi and end 2390
    number of tau = 9
    between start and second pi (Y)  2390
    total = 13780

    Single Block
    between pi2 and end 6864

    between pi and pi 13781

    between pi and end 6890
    between start and pi 6890
    = 13780


    '''
    # if n==1:
    # ### measurement loop for several larmor revivals
    #     N = 32768 ### number of pulses
    #     pts = 1 ### number of points per loading of the AWG
    #     # larmor_max = 49 ### the order of the last revival
    #     larmor_max = 1
    #     larmor_min = 1

    #     Cont = take_DD_Data(larmor_min,larmor_max,N,pts,Single_Block=True,shutter=True,XY_scheme=16)

    #     if Cont:
    #         Cont = take_DD_Data(larmor_min,larmor_max,N,pts,Single_Block=True,shutter=True,XY_scheme=8)

    #     N = 65536
    #     if Cont:
    #         Cont = take_DD_Data(larmor_min,larmor_max,N,pts,Single_Block=True,shutter=True,XY_scheme=16)
    #     if Cont:
    #         Cont = take_DD_Data(larmor_min,larmor_max,N,pts,Single_Block=True,shutter=True,XY_scheme=8)

    #     # N = 16384
    #     # if Cont:
    #     #     Cont = take_DD_Data(larmor_min,larmor_max,N,pts,Single_Block=True,shutter=True,XY_scheme=16)
    #     # if Cont:
    #     #     Cont = take_DD_Data(larmor_min,larmor_max,N,pts,Single_Block=True,shutter=True,XY_scheme=8)

    #######
    # 65536 pi - pulses
    # estimated T_coh = 1626 ms @ T_Hahn approximately 1 ms
    # sweep until 3300 ms overall evolution time --> 3300/(2.315*e-3*2*65536) = 10.9
    # --> sweep until tau = 17*tau_larmor.
    #######
    n=0
    if n==1 and Cont:
        N = 65536 ### number of pulses
        pts = 1 ### number of points per loading of the AWG
        larmor_max = 3
        larmor_min = 3
        larmor_step = 1
        reps = 900

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.
        print Total_time

        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=optimize,Single_Block=False,shutter=False,XY_scheme=16,reps=reps)

   
    n=0

    #######
    # 32768 pi - pulses
    # estimated T_coh = 1024 ms @ T_Hahn approximately 1 ms
    # sweep until 2100 ms overall evolution time --> 2100/(2.315*e-3*2*32768) = 13.8
    # --> sweep until tau = 21*tau_larmor.
    #######


    n=0

    # N_list=[16,32,64,96,128,160]
    # larmor_max_list=[1200,600,300,200,150,120]
    # larmor_step_list=[60,30,15,10,7,6]
    # pts_list=[128,64,32,20,16,12]
    # for ii in range(0,len(N_list)):
    #     MW_amplitude = 0.511+jj*.000
    #     if n==1 and Cont:
    #         N = 64 ### number of pulses
    #         pts = pts_list[ii] ### number of points per loading of the AWG
    #         larmor_max = larmor_max_list[ii]
    #         larmor_min = 6
    #         larmor_step = larmor_step_list[ii]
    #         reps = 1000

    #         Number_of_pulses = N
    #         nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
    #         Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.
    #         print Total_time

    #         if ii%5 == 0:
    #             optim=True

    #         else:
    #             optim=False


    #         if Run_Msmt:
               
    #             Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=False,Single_Block=False,shutter=False,XY_scheme=8,reps=reps,debug=False,MW_amplitude=MW_amplitude)
                #execfile('D:\measuring\measurement\scripts\QEC\QEC_ssro_calibration.py')
                





    n=0
    
    if n==1 and Cont:
        N = 1600 ### number of pulses
        pts = 1 ### number of points per loading of the AWG
        larmor_max = 15
        larmor_min = 1
        larmor_step = 5
        reps = 700

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.
        print Total_time

        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=True,Single_Block=False,shutter=False,XY_scheme=8,reps=reps,debug=False)
    

    if n==1 and Cont:
        N = 3200 ### number of pulses
        pts = 1 ### number of points per loading of the AWG
        larmor_max = 15
        larmor_min = 1
        larmor_step = 5
        reps = 700

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.
        print Total_time

        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=False,Single_Block=False,shutter=False,XY_scheme=8,reps=reps,debug=False)
    

    n=0
    #######
    # 16384 pi - pulses
    # estimated T_coh = 645 ms @ T_Hahn approximately 1 ms
    # sweep until 1200 ms overall evolution time --> 1200/(2.315*e-3*2*16384) = 15.8
    # --> sweep until tau = 25*tau_larmor.
    #######
    if n==1 and Cont:
        N = 16384 ### number of pulses
        pts = 1 ### number of points per loading of the AWG
        larmor_max = 17
        larmor_min = 1
        larmor_step = 1
        reps = 600

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.
        print Total_time

        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=optimize,Single_Block=True,shutter=True,XY_scheme=16,reps=reps)

    #######
    # 8192 pi - pulses
    # estimated T_coh = 406 ms @ T_Hahn approximately 1 ms
    # sweep until 800 ms overall evolution time --> 800/(2.315*e-3*2*8192) = 21.1
    # --> sweep until tau = 41*tau_larmor.
    #######
    if n==1 and Cont:
        N = 8192 ### number of pulses
        pts = 1 ### number of points per loading of the AWG
        larmor_max = 23
        larmor_min = 1
        larmor_step = 1
        reps = 450

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.
        print Total_time

        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=False,Single_Block=True,shutter=False,XY_scheme=16,reps=reps)


    #######
    # 4096 pi - pulses
    # estimated T_coh = 256 ms @ T_Hahn approximately 1 ms
    # sweep until 500 ms overall evolution time --> 500/(2.315*e-3*2*4096) = 27
    # --> sweep until tau = 61*tau_larmor.
    #######
    if n==1 and Cont:
        N = 4096 ### number of pulses
        pts = 1 ### number of points per loading of the AWG
        larmor_max = 29
        larmor_min = 1
        larmor_step = 1
        reps = 400

        Number_of_pulses = N
        nr_of_runs = int(np.floor((larmor_max-larmor_min)/float(larmor_step)))
        Total_time += reps*sum(np.linspace(2*Number_of_pulses*2.315e-6*larmor_min,2*Number_of_pulses*2.315e-6*larmor_max,nr_of_runs)) /3600.
        print Total_time

        if Run_Msmt:
            Cont = take_DD_Data(larmor_min,larmor_max,N,pts,larmor_step=larmor_step,optimize=optimize,Single_Block=True,shutter=True,XY_scheme=16,reps=reps)

    # if Run_Msmt and Cont and n==1:
    #     execfile(r'D:\measuring\measurement\scripts\QEC\carbon_calibration_routine_v2.py')

