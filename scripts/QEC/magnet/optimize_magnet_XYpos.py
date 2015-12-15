"""
Script for fine optimization of the magnet XY-position (using the average ms=-1, ms=+1 freq).
Fine optimization measures only the center resonance
Important: choose the right domain for the range of positions in get_magnet_position in magnet tools!
"""
import time

import numpy as np
import qt
import msvcrt
from analysis.lib.fitting import fit, common; reload(common)
from matplotlib import pyplot as plt
from analysis.lib.tools import toolbox

# import the DESR measurement, DESR fit, magnet tools and master of magnet
from measurement.scripts.QEC.magnet import DESR_msmt; reload(DESR_msmt)
from analysis.lib.fitting import dark_esr_auto_analysis; reload(dark_esr_auto_analysis)
from measurement.lib.tools import magnet_tools as mt; reload(mt)
mom = qt.instruments['master_of_magnet']; reload(mt)

execfile(qt.reload_current_setup)

ins_adwin = qt.instruments['adwin']
ins_counters = qt.instruments['counters']
ins_aom = qt.instruments['GreenAOM']

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

nm_per_step = qt.exp_params['magnet']['nm_per_step']
f0p_temp = qt.exp_params['samples'][SAMPLE]['ms+1_cntr_frq']*1e-9
f0m_temp = qt.exp_params['samples'][SAMPLE]['ms-1_cntr_frq']*1e-9
N_hyperfine = qt.exp_params['samples'][SAMPLE]['N_HF_frq']
ZFS = qt.exp_params['samples'][SAMPLE]['zero_field_splitting']

qt.exp_params['protocols'][SAMPLE]['AdwinSSRO']['SP_duration'] = 50 #XXXXXXXXXXXXXXXXXX

if __name__ == '__main__':
    
    ######################
    ## Input parameters ##
    ######################

    axis = 'Y_axis'               # X usually moves 2x slower than Y (current settings)  
    #scan_range       = 200        # From -scan range/2 to +scan range/2, Y  
    #no_of_steps      = 5               # with a total of no_of_steps measurment points.
    min_counts_before_optimize = 5e4    #optimize position if counts are below this
    # mom.set_mode(axis, 'stp')     # turn on or off the stepper
    laser_power = 10e-6
    save_plots = True
    fine_only = False
    coarse_only = True

    do_m1_fine = False ### circumvents fitting problems on the coarse measurement of the transition to -1
    range_coarse  = 5.0 #7.0
    pts_coarse    = 51   #81
    reps_coarse   = 750 #750
    numer_of_reps = 1
    range_fine  = 0.40
    pts_fine    = 51  
    reps_fine   = 1000 # 3000 #1500
    
    #reps_fine = 4000
    #pts_fine = 81
    #range_fine = 0.5
    #reps_coarse = 1250
    #pts_coarse = 121
    ###########
    ## start ##
    ###########

    #calculate steps to do
    #stepsize = scan_range/(no_of_steps-1) 
    #steps = [0] + (no_of_steps-1)/2*[stepsize] + (no_of_steps-1)*[-stepsize] + (no_of_steps-1)/2*[stepsize] 
    No_steps = True
    if No_steps == True: 
        steps = [0]*numer_of_reps # !!!! if we use this to measure for a long time, do not forget to save data: remove if-loop!
    else: 
        if axis == 'Y_axis':
            steps = [200,200,200] #[-scan_range/2] + (no_of_steps-1)*[stepsize]
            magnet_step_size = 100         # the sample position is checked after each magnet_step_siz 
        elif axis == 'X_axis':
            steps = [150, 150, 150] 
            magnet_step_size = 150         # the sample position is checked after each magnet_step_siz


    print 'Moving along %s' %axis 
    print 'Steps: %s' %steps

    #create the lists to save the data to
    f0m = []; u_f0m = []; f0p = [] ;u_f0p = []
    Bx_field_measured = []
    Bz_field_measured = []
    f_centre_list = []
    f_diff_list = []
    positions = []
    timestamps = []
    pos = 0

    
    for k in range(len(steps)):
        
        print '-----------------------------------'            
        print 'press q to stop measurement cleanly'
        print '-----------------------------------'
        qt.msleep(5)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            break

        GreenAOM.set_power(laser_power)
        optimiz0r.optimize(dims=['x','y','z','x','y'], int_time=100)
        

        step = steps[k]
        pos += step
        positions.append(pos) 
        print 'stepping by ' + str(step) + 'to_pos = ' + str(pos)  
        if step == 0:
            print 'step = 0, made no steps'
        else:
            if abs(step)/magnet_step_size == 0: 
                print 'check your magnet stepsize!'
                break

            for i in range(abs(step)/magnet_step_size):
                print 'step by ' + str(np.sign(step)*magnet_step_size)
                mom.step(axis,np.sign(step)*magnet_step_size)
                print 'magnet stepped by ' + str((i+1)*np.sign(step)*magnet_step_size) + ' out of ' + str(step)
                qt.msleep(1)
                GreenAOM.set_power(laser_power)
                ins_counters.set_is_running(0)
                int_time = 1000 
                cnts = ins_adwin.measure_counts(int_time)[0]
                print 'counts = '+str(cnts)
                if ((cnts < min_counts_before_optimize) & (i != abs(step)/magnet_step_size-1)):
                    optimiz0r.optimize(dims=['x','y','z'])
                print 'press q to stop magnet movement loop'
                qt.msleep(0.5)
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                    break

                    
                optimiz0r.optimize(dims=['x','y','z'])

        #measure both frequencies
            #ms=-1 coarse
        if fine_only == False:
            DESR_msmt.darkesr('magnet_' + axis + 'msm1_coarse', ms = 'msm', ssbmod_amplitude = 0.01,
                    range_MHz=range_coarse, pts=pts_coarse, reps=reps_coarse, freq=f0m_temp*1e9, mw_switch = True)
            f0m_temp, u_f0m_temp = dark_esr_auto_analysis.analyze_dark_esr(f0m_temp, 
                qt.exp_params['samples'][SAMPLE]['N_HF_frq']*1e-9,do_save=save_plots, sweep_direction ='right')
            #ms=-1 fine
        
        if do_m1_fine == True or coarse_only == False or u_f0m_temp > 1e-4: ## uncertainty larger than 100 kHz triggers the fine measurement.
            DESR_msmt.darkesr('magnet_' + axis + 'msm1', ms = 'msm', 
                    range_MHz=range_fine, pts=pts_fine, reps=reps_fine, freq=f0m_temp*1e9,# - N_hyperfine,
                    pulse_length = 8e-6, ssbmod_amplitude = 0.003, mw_switch = True)
            f0m_temp, u_f0m_temp = dark_esr_auto_analysis.analyze_dark_esr_double(do_plot=save_plots)
            f0m_temp = f0m_temp# + N_hyperfine*1e-9
                   
        print '-----------------------------------'            
        print 'press q to stop measurement cleanly'
        print '-----------------------------------'
        qt.msleep(5)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            break
        
            #ms=+1 coarse
        if fine_only == False:
            DESR_msmt.darkesr('magnet_' + axis + 'msp1_coarse', ms = 'msp', 
                    range_MHz=range_coarse, pts=pts_coarse,ssbmod_amplitude = 0.02, reps=reps_coarse,freq = f0p_temp*1e9, mw_switch = True)
            f0p_temp, u_f0p_temp = dark_esr_auto_analysis.analyze_dark_esr(f0p_temp, 
                    qt.exp_params['samples'][SAMPLE]['N_HF_frq']*1e-9,do_save=save_plots, sweep_direction ='left')
                #ms=+1 fine

        if coarse_only == False:
            DESR_msmt.darkesr('magnet_' + axis + 'msp1', ms = 'msp', 
                    range_MHz=range_fine, pts=pts_fine, reps=reps_fine, freq=f0p_temp*1e9,# + N_hyperfine, 
                    pulse_length = 8e-6, ssbmod_amplitude = 0.005, mw_switch = True)
            f0p_temp, u_f0p_temp = dark_esr_auto_analysis.analyze_dark_esr_double(do_plot=save_plots)
            f0p_temp = f0p_temp# - N_hyperfine*1e-9

        Bz_measured, Bx_measured = mt.get_B_field(msm1_freq=f0m_temp*1e9, msp1_freq=f0p_temp*1e9)
        
        print '-----------------------------------'            
        print 'press q to stop measurement cleanly'
        print '-----------------------------------'
        qt.msleep(5)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            break

        f_centre    = (f0m_temp+f0p_temp)/2
        f_diff = (f_centre-ZFS*1e-9)*1e6

        f = open(r'D:\measuring\Tracking_Frequency.txt', 'a')
        f.write(time.strftime("%y%m%d%H%M%S") +' '+ str(f0m_temp) +' '+ str(u_f0m_temp) + ' ' + str(f0p_temp) + ' ' + str(u_f0p_temp) + ' ' + str(f_centre) + ' ' + str(f_diff) + ' ' + str(Bx_measured) + ' ' + str(Bz_measured) + '\n')
        f.close()

        f0m.append(f0m_temp)
        u_f0m.append(u_f0m_temp)
        f0p.append(f0p_temp)
        u_f0p.append(u_f0p_temp)
        f_centre_list.append(f_centre)
        f_diff_list.append(f_diff)
        Bx_field_measured.append(Bx_measured)
        Bz_field_measured.append(Bz_measured)
    


        print 
        print '-----------------------------'
        print 'Fitted ms-1 transition frequency is '+str(round(f0m_temp,6))+' GHz' + ' +/- ' + str(round(u_f0m_temp*1e6,1)) + ' khz'
        print 'Fitted ms+1 transition frequency is '+str(round(f0p_temp,6))+' GHz' + ' +/- ' + str(round(u_f0p_temp*1e6,1)) + ' khz'
        print 'Calculated centre between ms=-1 and ms=+1 is '+ str(f_centre)+' GHz +/- '+str((u_f0m_temp**2+u_f0p_temp**2)**(1./2)/2*1e6)+' kHz'
        print 'Difference to ZFS = '+ str((f_centre-ZFS*1e-9)*1e6)+ 'kHz'
        print 'Measured B_field is: Bz = '+str(Bz_measured)+ ' G ,Bx = '+str(Bx_measured)+ ' G'
        print '-----------------------------'
        
        folder = toolbox.latest_data('DarkESR')
        plt.figure(figsize=(15, 3)) 
        plt.plot([0],[1],label = 
         'Fitted ms-1 transition frequency is '+str(f0m_temp)+' GHz' + ' +/- ' + str(u_f0m_temp*1e6) + ' khz \n'+
         'Fitted ms+1 transition frequency is '+str(f0p_temp)+' GHz' + ' +/- ' + str(u_f0p_temp*1e6) + ' khz \n'+
         'Calculated centre between ms=-1 and ms=+1 is '+ str(f_centre)+' GHz +/- '+str((u_f0m_temp**2+u_f0p_temp**2)**(1./2)/2*1e6)+' kHz \n'+
         'Difference to ZFS = '+ str((f_centre-ZFS*1e-9)*1e6)+ 'kHz \n'+
         'Measured B_field is: Bz = '+str(Bz_measured)+ ' G ,Bx = '+str(Bx_measured)+ ' G')
        plt.legend()
        plt.savefig(os.path.join(folder, 'fitting_results.png'),
        format='png')
        plt.close('all')

    if No_steps == False: 
   
        qt.mstart()

        d = qt.Data(name=SAMPLE_CFG+'_magnet_optimization_' + axis)
        


        d.add_coordinate('position')
        d.add_value('ms-1 transition frequency (GHz)')
        d.add_value('ms+1 transition frequency error (GHz)')
        d.add_value('ms-1 transition frequency (GHz)')
        d.add_value('ms+1 transition frequency error (GHz)')
        d.add_value('center frequency (GHz)')
        d.add_value('Difference to set ZFS (kHz)')
        d.add_value('measured Bx field (G)')
        d.add_value('measured Bz field (G)')

        
        # #fitting

        # if len(f_diff_list) != 1:  #Should add some kind of if statement if only one point is measured to prevent the program from crashing here.  
        p0, fitfunc, fitfunc_str = common.fit_parabole(g_o=5,g_A=1,g_c=0)
        fit_result = fit.fit1d(positions, f_diff_list, None, p0=p0, fitfunc = fitfunc, ret=True, fixed=[])
        # print 'minimum at steps = '+str(fit_result['params_dict']['c'])
        # # print 'So step magnet '+str(fit_result['params_dict']['c']-scan_range/2)+' to go to optimum'

        # print positions  
        d.create_file()
        filename=d.get_filepath()[:-4]
        d.add_data_point(positions, f0m,u_f0m,f0p,u_f0p,f_centre_list,f_diff_list,Bx_field_measured,Bz_field_measured)


        # to do show error bars
        positions[0] = positions[0] + 0.00001 #for some reason the plot below cannot handle twice the same x-coordinate
        
        fd = zeros(1000)
        x_fd = linspace(min(positions),max(positions),1000)
        if type(fit_result) != type(False):
            fd = fit_result['fitfunc'](x_fd)
            fd = fd.tolist()


        min_fd = (min(fd))
        pos_min_fd = x_fd[fd.index(min_fd)]
        print 'Minumum (%s kHz) located at %s' %(min_fd,pos_min_fd)
        print 'Current position: (%s) move the magnet: (%s) along the %s' %(sum(steps),pos_min_fd-sum(steps),axis)
        
        p_c = qt.Plot2D(x_fd,fd, 'b-', name='f_centre relative to ZFS', clear=True)
        p_c.add_data(d, coorddim=0, valdim=6,style='rO')
        p_c.save_png(filename+'.png')
        d.close_file()
        qt.mend()
