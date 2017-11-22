"""
Script for optimization of the magnet Z-position (using the ms=+1 resonance).
Coarse optimization starts with a large range scan and then zooms in
Important: choose the right domain for the range of positions in get_magnet_position in magnet tools!
"""
import numpy as np
import qt
import msvcrt
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt; reload(pulsar_msmt)
from measurement.scripts.QEC.magnet import DESR_msmt; reload(DESR_msmt)
from measurement.lib.tools import magnet_tools as mt; reload(mt)
from analysis.lib.fitting import fit, common; reload(common)
from matplotlib import pyplot as plt
from analysis.lib.tools import toolbox
from analysis.lib.fitting import dark_esr_auto_analysis; reload(dark_esr_auto_analysis)

mom = qt.instruments['master_of_magnet']; reload(mt)

# import the DES Ranalysis and the magnet scanner instrument

magnet_Z_scanner = qt.instruments['conex_scanner_Z']
magnet_X_scanner = qt.instruments['conex_scanner_X']
magnet_Y_scanner = qt.instruments['conex_scanner_Y']
temperature_sensor = qt.instruments['kei2000']


execfile(qt.reload_current_setup)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']
current_f_msm1 = qt.exp_params['samples'][SAMPLE]['ms-1_cntr_frq']

f0p_temp = qt.exp_params['samples'][SAMPLE]['ms+1_cntr_frq']*1e-9
f0m_temp = qt.exp_params['samples'][SAMPLE]['ms-1_cntr_frq']*1e-9
N_hyperfine = qt.exp_params['samples'][SAMPLE]['N_HF_frq']
ZFS = qt.exp_params['samples'][SAMPLE]['zero_field_splitting']


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



    
      
        ######################
        ### Run experiment ###
        ######################

    




if __name__ == '__main__':

######################
## Input parameters ##
######################


    safemode            = False    # If True then manual confirmation is needed befor each magnet movement
    optimization_target = 8     # Target difference frequency in kHz , first (03.08) was 10 then 7 then 10 again
    field_gradient      = 0.110#0.100     
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
    axis = 'X_axis'

    f0_avg = 0;
    D_ZFS = 0;



    for j in range (0,3):

       
        Start_position = magnet_X_scanner.GetPosition()

        # msm1
        f0 = []; u_f0 = []; iterations_list =[]; magnet_postion_list =[]; fit_failed_list=[]; f0_p = []; u_f0_p = []; f0_avg; D_ZFS_list=[]

        DESR_msmt.darkesr('magnet_' + axis + 'msm1_coarse', ms = 'msm', ssbmod_amplitude = 0.004,
        range_MHz=coarse_range, pts=coarse_pts, reps=coarse_reps, freq=f0m_temp*1e9, mw_switch = False)
        # Do the fitting, returns in MHz, input in GHz
         
        f0_temp, u_f0_temp = dark_esr_auto_analysis.analyze_dark_esr_double(do_plot=True)

        #msp1

        

        DESR_msmt.darkesr('magnet_' + axis + 'msp1_coarse', ms = 'msp', 
                range_MHz=coarse_range, pts=coarse_pts,ssbmod_amplitude = 0.009, reps=coarse_reps,freq = f0p_temp*1e9, mw_switch = False)

        # Do the fitting, returns in MHz, input in GHz
         
        f0_temp_p, u_f0_temp_p = dark_esr_auto_analysis.analyze_dark_esr_double(do_plot=True)

        f0_avg = (f0_temp + f0_temp_p)/2
        D_ZFS = f0_avg - ZFS


        

        # List all the measured values
        iterations = 0
        f0.append(f0_temp)
        f0_p.append(f0_temp_p)
        u_f0.append(u_f0_temp)
        u_f0_p.append(u_f0_temp_p)
        D_ZFS_list.append(D_ZFS)

        magnet_postion_list.append(Start_position)

        magnet_X_scanner.MoveRelative(0.01)


        print '--------------------------------'
        print 'press q to stop measurement loop'
        print '--------------------------------'
        qt.msleep(2)

        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')) or abs(move_to_position-current_position) < 0.000025:
            break


        




   


        # while abs(delta_f0_temp) > optimization_target:

        #         ## Determine new postition
        #         current_position = magnet_Z_scanner.GetPosition()
        #         delta_position = delta_f0_temp/field_gradient*1e-6
        #         move_to_position = current_position + delta_position

        #         print 'Target frequency =' + str(current_f_msm1)
        #         print 'Measured frequency = ' + str(f0_temp) + ' GHz +/- ' + str(u_f0_temp*1e6) + ' kHz'
        #         print 'Difference = ' + str(delta_f0_temp) + ' kHz'
        #         print 'Current magnet position = ' + str(current_position) + ' mm'
        #         print 'Move to position          ' + str(move_to_position) + ' mm'
        #         print 'By                        ' + str(delta_position*1e6) + 'nm'
                

        #         # if u_f0_temp*1e6 > 15:
        #         #     print 'Uncertainty larger than 15 kHz, fit failed'
        #         #     fit_failed = 1
        #         # else: 
        #         #     fit_failed = 0

        #         # fit_failed_list.append(fit_failed)
                
        #         ## Actually move the magnet
              

        #         if u_f0_temp*1e6 < 15:
           
        #             ## Limit the maximum movement range
        #             if move_to_position < 0.042 or move_to_position > 0.072:
        #                 print 'movement is going out of range, abort!!!'
        #                 break

        #             print 'Target frequency =' + str(current_f_msm1)
        #             print 'Measured frequency = ' + str(f0_temp) + ' GHz +/- ' + str(u_f0_temp*1e6) + ' kHz'
        #             print 'Difference = ' + str(delta_f0_temp) + ' kHz'
        #             print 'Current magnet position = ' + str(current_position) + ' mm'
        #             print 'Move to position          ' + str(move_to_position) + ' mm'
        #             print 'By                        ' + str((move_to_position-current_position)*1e6) + 'nm'

        #             if safemode == True: 
        #                 print '\a\a\a' 
        #                 ri = raw_input ('move magnet? (y/n)')
        #                 if str(ri) != 'y': 
        #                     break
                    
        #             ## Actually move the magnet
        #             magnet_Z_scanner.MoveRelative(delta_position)
        #             print 'moving magnet...'

        #         else:
        #             print 'Uncertainty larger than 15 kHz, fit failed'
        #             break

        #         print '--------------------------------'
        #         print 'press q to stop measurement loop'
        #         print '--------------------------------'
        #         qt.msleep(2)

        #         if (msvcrt.kbhit() and (msvcrt.getch() == 'q')) or abs(move_to_position-current_position) < 0.000025:
        #             break

        #         darkesr('magnet_optimize_step_' + str(iterations), range_MHz=fine_range, pts=fine_pts, reps=fine_reps, 
        #             power = fine_amplitude, MW_power = fine_MW_power, pulse_length=fine_pulse_length)

        #         f0_temp, u_f0_temp = dark_esr_auto_analysis.analyze_dark_esr_double(do_plot=True)
        #         delta_f0_temp = -f0_temp*1e6+current_f_msm1*1e-3

        #         iterations += 1

        


