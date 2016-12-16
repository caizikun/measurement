"""
Script for fine optimization of the magnet XY-position (using the average ms=-1, ms=+1 freq).
Fine optimization measures only a single of th ethree 14N lines 
Important: choose the right domain for the range of positions in get_magnet_position in magnet tools!

NOTE by THT: these scripts were previously only used in LT2 with an attocube magnet scanner. Now they are also used with
othe rmagnet scanner, but the script is not yet fully cleaned up.
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
# from measurement.lib.tools import magnet_tools as mt; reload(mt)

execfile(qt.reload_current_setup)

ins_adwin = qt.instruments['adwin']
magnet_X_scanner = qt.instruments['conex_scanner_X']
magnet_Y_scanner = qt.instruments['conex_scanner_Y']
temperature_sensor = qt.instruments['kei2000']


SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

f0p_temp = qt.exp_params['samples'][SAMPLE]['ms+1_cntr_frq']*1e-9
# f0m_temp = qt.exp_params['samples'][SAMPLE]['ms-1_cntr_frq']*1e-9
f0m_temp = 1.746596
N_hyperfine = qt.exp_params['samples'][SAMPLE]['N_HF_frq']
ZFS = qt.exp_params['samples'][SAMPLE]['zero_field_splitting']

if __name__ == '__main__':
    
    ######################
    ## Input parameters ##
    ######################

    axis = 'Y_axis'               
    save_plots  = True
    
    range_coarse    = 7.5   # MHz   
    pts_coarse      = 101    
    reps_coarse     = 750   
    
    range_fine      = 0.60  # MHz
    pts_fine        = 81  
    reps_fine       = 2000  

    ###########
    ## start ##
    ###########

    #create the lists to save the data to
    f0m = []; u_f0m = []; f0p = [] ;u_f0p = []
    f_centre_list = []
    f_diff_list = []
    position_list = []
    timestamps = []
    position = 0
   
    No_steps = True

    steps = [0] #[0] + 5*[20e-3] + 10*[-20e-3] + 5*[20e-3]

    data = qt.Data(name='Magnet_optimize_' + axis)
    data.add_coordinate('position')
    data.add_value('frequency diff')
    data.create_file()

    data_plt = qt.Plot2D(data, 'ro-', name='Magnet_optimize', coorddim=0,
            valdim=1, clear=True)
    data_plt.add(data, 'bo-', coorddim=0, valdim=1)
    data_plt.set_xlabel('position')
    data_plt.set_ylabel('freq diff')


    #measure both frequencies
    for k in range(len(steps)):
        
        if No_steps == False: 
            if axis == 'Y_axis' and steps[k] != 0:
                magnet_Y_scanner.MoveRelative(steps[k])
                print 'Moving the magnet along Y with ' + str(steps[k])
            elif axis == 'X_axis'and steps[k] != 0:
                magnet_X_scanner.MoveRelative(steps[k])
                print 'Moving the magnet along X with ' + str(steps[k])

        position = position + steps[k]

        #ms=-1 coarse
        DESR_msmt.darkesr('magnet_' + 'msm1_coarse', ms = 'msm', 
                range_MHz=range_coarse, pts=pts_coarse, reps=reps_coarse, freq=f0m_temp*1e9, 
                pulse_length = 3e-6, ssbmod_amplitude = 0.08, mw_power = -1, mw_switch = False)
        
        f0m_temp, u_f0m_temp = dark_esr_auto_analysis.analyze_dark_esr(f0m_temp, 
            qt.exp_params['samples'][SAMPLE]['N_HF_frq']*1e-9,do_save=save_plots, sweep_direction ='right')
       
        #ms=+1 coarse
        DESR_msmt.darkesr('magnet_' + 'msp1_coarse', ms = 'msp', 
                range_MHz=range_coarse, pts=pts_coarse, reps=reps_coarse,freq = f0p_temp*1e9, 
                pulse_length = 3e-6, ssbmod_amplitude = 0.08, mw_power = -1, mw_switch = False)
        f0p_temp, u_f0p_temp = dark_esr_auto_analysis.analyze_dark_esr(f0p_temp, 
                qt.exp_params['samples'][SAMPLE]['N_HF_frq']*1e-9 ,do_save=save_plots, sweep_direction ='left')
           
       
        print '-----------------------------------'            
        print 'press q to stop measurement cleanly'
        print '-----------------------------------'
        qt.msleep(2)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            break
            
        #ms=-1 fine
        DESR_msmt.darkesr('magnet_' +  'msm1', ms = 'msm', 
                range_MHz=range_fine, pts=pts_fine, reps=reps_fine, freq=f0m_temp*1e9,# - N_hyperfine,
                pulse_length = 9e-6, ssbmod_amplitude = 0.08/3,  mw_power = -1, mw_switch = False)
                
        f0m_temp, u_f0m_temp = dark_esr_auto_analysis.analyze_dark_esr_double(do_plot=save_plots)
        f0m_temp = f0m_temp# + N_hyperfine*1e-9
        
        #ms=+1 fine
        DESR_msmt.darkesr('magnet_' + 'msp1', ms = 'msp', 
                range_MHz=range_fine, pts=pts_fine, reps=reps_fine, freq=f0p_temp*1e9,# + N_hyperfine, 
                pulse_length = 9e-6, ssbmod_amplitude = 0.08/3, mw_power = -1, mw_switch = False)
        
        f0p_temp, u_f0p_temp = dark_esr_auto_analysis.analyze_dark_esr_double(do_plot=save_plots)
        f0p_temp = f0p_temp# - N_hyperfine*1e-9

        # Bz_measured, Bx_measured = mt.get_B_field(msm1_freq=f0m_temp*1e9, msp1_freq=f0p_temp*1e9)
          
        print '-----------------------------------'            
        print 'press q to stop measurement cleanly'
        print '-----------------------------------'
        qt.msleep(2)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            break

        f_centre    = (f0m_temp+f0p_temp)/2
        f_diff = (f_centre-ZFS*1e-9)*1e6

    # f = open(r'D:\measuring\Tracking_Frequency.txt', 'a')
    # f.write(time.strftime("%y%m%d%H%M%S") +' '+ str(f0m_temp) +' '+ str(u_f0m_temp) + ' ' + str(f0p_temp) + ' ' + str(u_f0p_temp) + ' ' + str(f_centre) + ' ' + str(f_diff) + '\n')
    # f.close()

        f0m.append(f0m_temp)
        u_f0m.append(u_f0m_temp)
        f0p.append(f0p_temp)
        u_f0p.append(u_f0p_temp)
        f_centre_list.append(f_centre)
        f_diff_list.append(f_diff)
        position_list.append(position)

        data.add_data_point(position, f_diff)

        print 
        print '-----------------------------'
        print 'Fitted ms-1 transition frequency is '+str(round(f0m_temp,6))+' GHz' + ' +/- ' + str(round(u_f0m_temp*1e6,1)) + ' khz'
        print 'Fitted ms+1 transition frequency is '+str(round(f0p_temp,6))+' GHz' + ' +/- ' + str(round(u_f0p_temp*1e6,1)) + ' khz'
        print 'Calculated centre between ms=-1 and ms=+1 is '+ str(f_centre)+' GHz +/- '+str((u_f0m_temp**2+u_f0p_temp**2)**(1./2)/2*1e6)+' kHz'
        print 'Difference to ZFS = '+ str((f_centre-ZFS*1e-9)*1e6)+ 'kHz'
        print '-----------------------------'
   
    data_plt.save_png('Magnet_optimize.png')
    data.close_file()
    qt.mend()






    '''
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
        '''