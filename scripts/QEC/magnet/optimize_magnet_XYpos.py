"""
Script for fine optimization of the magnet XY-position (using the average ms=-1, ms=+1 freq).
Fine optimization measures only the center resonance
Important: choose the right domain for the range of positions in get_magnet_position in magnet tools!
"""
import numpy as np
import qt
import msvcrt
from analysis.lib.fitting import fit, common; reload(common)


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
current_f_msp1 = qt.exp_params['samples'][SAMPLE]['ms+1_cntr_frq']
current_f_msm1 = qt.exp_params['samples'][SAMPLE]['ms-1_cntr_frq']
ZFS = qt.exp_params['samples'][SAMPLE]['zero_field_splitting']

if __name__ == '__main__':
    
    ######################
    ## Input parameters ##
    ######################

    axis = 'X_axis'
    scan_range       = 200        # From -scan range/2 to +scan range/2  
    no_of_steps      = 5          # with a total of no_of_steps measurment points.
    magnet_step_size = 10         # the sample position is checked after each magnet_step_size
    mom.set_mode(axis, 'stp')     # turn on or off the stepper

    range_coarse = 5.00
    pts_coarse  = 81   
    reps_coarse   = 500

    range_fine = 0.25
    pts_fine  = 51   
    reps_fine   = 2000

    ###########
    ## start ##
    ###########

    #calculate steps to do
    stepsize = scan_range/(no_of_steps-1) 
    #steps = [0] + (no_of_steps-1)/2*[stepsize] + (no_of_steps-1)*[-stepsize] + (no_of_steps-1)/2*[stepsize] 
    steps = [0]# -scan_range/2] + (no_of_steps-1)*[stepsize] 


    print steps

    #create the lists to save the data to
    f0m = []; u_f0m = []; f0p = [] ;u_f0p = []
    Bx_field_measured = []
    Bz_field_measured = []
    f_centre_list = []
    f_diff_list = []
    positions = []
    pos = 0
    
    for k in range(len(steps)):
        
        print '-----------------------------------'            
        print 'press q to stop measurement cleanly'
        print '-----------------------------------'
        qt.msleep(2)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            break

        step = steps[k]
        pos += step
        positions.append(pos) 
        print 'stepping by ' + str(step) + 'to_pos = ' + str(pos)  
        if step == 0:
            print 'step = 0, made no steps'
        else:
            for i in range(abs(step)/magnet_step_size):
                print 'step by ' + str(np.sign(step)*magnet_step_size)
                mom.step(axis,np.sign(step)*magnet_step_size)
                print 'magnet stepped by ' + str((i+1)*np.sign(step)*magnet_step_size) + ' out of ' + str(step)
                qt.msleep(1)
                GreenAOM.set_power(5e-6)
                ins_counters.set_is_running(0)
                int_time = 1000 
                cnts = ins_adwin.measure_counts(int_time)[0]
                print 'counts = '+str(cnts)
                if cnts < 1e4:
                    optimiz0r.optimize(dims=['x','y','z'])
                print 'press q to stop magnet movement loop'
                qt.msleep(0.5)
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                    break
            #use a higher threshold at the very end
            GreenAOM.set_power(5e-6)
            ins_counters.set_is_running(0)
            int_time = 1000 
            cnts = ins_adwin.measure_counts(int_time)[0]
            print 'counts = '+str(cnts)
            if cnts < 30e4:
                optimiz0r.optimize(dims=['x','y','z'])

        #measure both frequencies
            #ms=-1 coarse
        DESR_msmt.darkesr('magnet_' + axis + 'msm1_coarse', ms = 'msm', range_MHz=range_coarse, pts=pts_coarse, reps=reps_coarse)
        f0m_temp, u_f0m_temp = dark_esr_auto_analysis.analyze_dark_esr(current_f_msm1*1e-9, qt.exp_params['samples'][SAMPLE]['N_HF_frq']*1e-9)
            #ms=-1 fine
        DESR_msmt.darkesr('magnet_' + axis + 'msm1', ms = 'msm', range_MHz=range_fine, pts=pts_fine, reps=reps_fine, freq=f0m_temp*1e9)
        f0m_temp, u_f0m_temp = dark_esr_auto_analysis.analyze_dark_esr_single(current_f_msp1*1e-9)
                   
        qt.msleep(1)
        
            #ms=+1 coarse
        DESR_msmt.darkesr('magnet_' + axis + 'msp1_coarse', ms = 'msp', range_MHz=range_coarse, pts=pts_coarse, reps=reps_coarse)
        f0p_temp, u_f0p_temp = dark_esr_auto_analysis.analyze_dark_esr(current_f_msp1*1e-9, qt.exp_params['samples'][SAMPLE]['N_HF_frq']*1e-9)
            #ms=+1 fine
        DESR_msmt.darkesr('magnet_' + axis + 'msp1', ms = 'msp', range_MHz=range_fine, pts=pts_fine, reps=reps_fine, freq=f0p_temp*1e9)
        f0p_temp, u_f0p_temp = dark_esr_auto_analysis.analyze_dark_esr_single(current_f_msp1*1e-9)

        Bz_measured, Bx_measured = mt.get_B_field(msm1_freq=f0m_temp*1e9, msp1_freq=f0p_temp*1e9)
        
        f_centre    = (f0m_temp+f0p_temp)/2
        f_diff = (f_centre-ZFS*1e-9)*1e6

        f0m.append(f0m_temp)
        u_f0m.append(u_f0m_temp)
        f0p.append(f0p_temp)
        u_f0p.append(u_f0p_temp)
        f_centre_list.append(f_centre)
        f_diff_list.append(f_diff)
        Bx_field_measured.append(Bx_measured)
        Bz_field_measured.append(Bz_measured)

        print '-----------------------------'
        print 'Fitted ms-1 transition frequency is '+str(f0m_temp)+' GHz' + ' +/- ' + str(u_f0m_temp*1e6) + ' khz'
        print 'Fitted ms+1 transition frequency is '+str(f0p_temp)+' GHz' + ' +/- ' + str(u_f0p_temp*1e6) + ' khz'
        print 'Calculated centre between ms=-1 and ms=+1 is '+ str(f_centre)+' GHz +/- '+str((u_f0m_temp**2+u_f0p_temp**2)**(1./2)/2*1e6)+' kHz'
        print 'Difference to ZFS = '+ str((f_centre-ZFS*1e-9)*1e6)+ 'kHz'
        print 'Measured B_field is: Bz = '+str(Bz_measured)+ ' G ,Bx = '+str(Bx_measured)+ ' G'
        print '-----------------------------'
   
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
    
    p_c = qt.Plot2D(x_fd,fd, 'b-', name='f_centre relative to ZFS', clear=True)
    p_c.add_data(d, coorddim=0, valdim=6,style='rO')
    p_c.save_png(filename+'.png')
    d.close_file()
    qt.mend()
