"""
Script for optimization of the magnet Z-position (using the ms=+1 resonance).
Coarse optimization starts with a large range scan and then zooms in
Important: choose the right domain for the range of positions in get_magnet_position in magnet tools!
"""
import numpy as np
import qt
import msvcrt
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt; reload(pulsar_msmt)

# import the DES Ranalysis and the magnet scanner instrument
from analysis.lib.fitting import dark_esr_auto_analysis; reload(dark_esr_auto_analysis)
magnet_Z_scanner = qt.instruments['conex_scanner_Z']
temperature_sensor = qt.instruments['kei2000']


execfile(qt.reload_current_setup)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']
current_f_msm1 = qt.exp_params['samples'][SAMPLE]['ms-1_cntr_frq']

def darkesr(name, range_MHz, pts, reps, power, MW_power, pulse_length):

    m = pulsar_msmt.DarkESR(name)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])

    m.params['temp'] = temperature_sensor.get_readlastval()
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



    
      
        ######################
        ### Run experiment ###
        ######################

    


for k in range (20):

    if __name__ == '__main__':

    ######################
    ## Input parameters ##
    ######################
        safemode            = False    # If True then manual confirmation is needed befor each magnet movement
        optimization_target = 5     # Target difference frequency in kHz , first (03.08) was 10 then 7 then 10 again
        field_gradient      = 0.100     
        only_fine           = True

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
              

                if u_f0_temp*1e6 < 5:
           
                    ## Limit the maximum movement range
                    if move_to_position < 0.062 or move_to_position > 0.082:
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

    temp_0 =(temperature_sensor.get_readlastval()-100)/0.385 
    temperature_compare = 51*[0]
    temperature_compare[0]= temp_0


    for i in range (25):

        print '--------------------------------'
        print 'press q to stop measurement loop'
        print '--------------------------------'
        qt.msleep(2)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            break

          # create the data lists
        

        # Measure B-field 
        darkesr('magnet_optimize_tcorr', range_MHz=coarse_range, pts=coarse_pts, reps=coarse_reps, 
                power= coarse_amplitude, MW_power = coarse_MW_power, pulse_length=coarse_pulse_length)

        # Do the fitting, returns in MHz, input in GHz
       
       
        f0_temp, u_f0_temp = dark_esr_auto_analysis.analyze_dark_esr_double(do_plot=True)
        delta_f0_temp = -f0_temp*1e6+current_f_msm1*1e-3    # in kHz

        # Magnet start position
        Start_position = magnet_Z_scanner.GetPosition()

        # List all the measured values
        f0.append(f0_temp)
        u_f0.append(u_f0_temp)
        delta_f0.append(delta_f0_temp)
        magnet_postion_list.append(Start_position)

        temp_i = (temperature_sensor.get_readlastval()-100)/0.385 
        temperature_compare[i+1] = temp_i
        

        delta_temperature = temperature_compare[i+1]-temperature_compare[j]
        delta_f_temperature = 1133*delta_temperature   #in KHz


        if abs(delta_f_temperature) > 8:

            delta_move = 1e-3*(-delta_f_temperature)/120
            j=i
            magnet_Z_scanner.MoveRelative(delta_move)



    f0 = []; u_f0 = []; delta_f0 =[]; iterations_list =[]; magnet_postion_list =[]; fit_failed_list=[]

    darkesr('magnet_optimize_init', range_MHz=coarse_range, pts=coarse_pts, reps=coarse_reps, 
                power= coarse_amplitude, MW_power = coarse_MW_power, pulse_length=coarse_pulse_length)

    # Do the fitting, returns in MHz, input in GHz
    if only_fine == False:
        f0_temp, u_f0_temp = dark_esr_auto_analysis.analyze_dark_esr(current_f_msm1*1e-9, qt.exp_params['samples'][SAMPLE]['N_HF_frq']*1e-9) 
    else: 
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
          

            if u_f0_temp*1e6 < 5:
       
                ## Limit the maximum movement range
                if move_to_position < 0.062 or move_to_position > 0.082:
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


    for s in range (25):        
                
    
        
        print '--------------------------------'
        print 'press q to stop measurement loop'
        print '--------------------------------'
        qt.msleep(2)

        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')) or abs(move_to_position-current_position) < 0.000025:
            break

        darkesr('magnet_free_running_step_' + str(iterations), range_MHz=fine_range, pts=fine_pts, reps=fine_reps, 
            power = fine_amplitude, MW_power = fine_MW_power, pulse_length=fine_pulse_length)

        f0_temp, u_f0_temp = dark_esr_auto_analysis.analyze_dark_esr_double(do_plot=True)
        delta_f0_temp = -f0_temp*1e6+current_f_msm1*1e-3

        iterations += 1

        temperature = (temperature_sensor.get_readlastval()-100)/0.385 #important to be updated here
        temperature_compare[i] = temperature
        delta_f0_check = delta_f0_temp


        print '--------------------------------'
        print 'press q to stop measurement loop'
        print '--------------------------------'
        qt.msleep(2)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')) :
            break

    print '--------------------------------'
    print 'press q to stop measurement loop'
    print '--------------------------------'
    qt.msleep(2)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')) :
        break

       

