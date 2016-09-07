"""
Script to calibrate the movement of the magnet scanner by scanning it back and forth. By THT
"""
import msvcrt
from analysis.lib.fitting import fit, common; reload(common)

# import the DESR measurement, DESR fit, magnet tools and master of magnet
from measurement.scripts.QEC.magnet import DESR_msmt; reload(DESR_msmt)
from analysis.lib.fitting import dark_esr_auto_analysis; reload(dark_esr_auto_analysis)
execfile(qt.reload_current_setup)

magnet_Z_scanner = qt.instruments['conex_scanner_Z']
ins_counters = qt.instruments['counters']


SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

f0p_temp = qt.exp_params['samples'][SAMPLE]['ms+1_cntr_frq']*1e-9
f0m_temp = qt.exp_params['samples'][SAMPLE]['ms-1_cntr_frq']*1e-9
N_hyperfine = qt.exp_params['samples'][SAMPLE]['N_HF_frq']

if __name__ == '__main__':
    
    ######################
    ## Input parameters ##
    ######################
    
    # magnet_positions_list = [0] + 4*([8e-3] + 2*[1e-3]+ 2*[-1e-3]+[-8e-3] + [-8e-3] +2*[-1e-3]+ 2*[1e-3]+ [8e-3])   # Note: in units of millimeters
    # magnet_positions_list = [0] + 4*([8e-3] + 2*[0.1e-3]+ 2*[-0.1e-3]+[-8e-3]+[-8e-3] + 2*[-0.1e-3]+ 2*[0.1e-3]+ [8e-3])   # Note: in units of millimeters
    # magnet_positions_list = [0] + 5*([8e-3] + 5*[0.2e-3]+ 5*[-0.2e-3]+[-8e-3]+[-8e-3] + 5*[-0.2e-3]+ 5*[0.2e-3]+ [8e-3])   # Note: in units of millimeters
    magnet_positions_list = [0] +[8e-3] + 5*( 5*[0.2e-3]+ 5*[-0.2e-3])
    # backlash_compensation_list = [0.0048, 0.0049, 0.0050, 0.0051]
    backlash_compensation_list = [0.0050]
    step = 0.2
    print '.......................................'
    print 'step is    ' + str(step)
    print '......................................'
    save_plots  = True
    
    range_coarse    = 7.5     
    pts_coarse      = 101    
    reps_coarse     = 750   
    
    range_fine      = 0.60
    pts_fine        = 81  
    reps_fine       = 2000  

    ###########
    ## start ##
    ###########
    
    for ll in range(len(backlash_compensation_list)):
        print 'setting backlash to: ' + str(backlash_compensation_list[ll])
        magnet_Z_scanner.SetBacklashCompensation(backlash_compensation_list[ll])
        for k in range(len(magnet_positions_list)):
            
            if mod(k,10)==0:
                GreenAOM.set_power(10e-6)
                qt.msleep(10)
                ins_counters.set_is_running(0)  
                optimiz0r.optimize(dims=['x','y','z'], int_time=300, gaussian_fit = False)

            print 'Starting step ' + str(k+1) + '/' + str(len(magnet_positions_list))
            print 'Moving magnet Z with ' +str(magnet_positions_list[k])

            print '-----------------------------------'            
            print 'press q to stop measurement cleanly'
            print '-----------------------------------'
            qt.msleep(5)
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                break

            magnet_Z_scanner.MoveRelative(magnet_positions_list[k])

            print 'Current magnet position is ' + str(magnet_Z_scanner.GetPosition())
            # magnet_scanner_position = magnet_Z_scanner.GetPosition()

            DESR_msmt.darkesr('magnet_scanner_calib_coarse' + str(ll) + '_'+ str(k), ms = 'msm', 
                    range_MHz=range_coarse, pts=pts_coarse, reps=reps_coarse, freq=f0m_temp*1e9, 
                    pulse_length = 3e-6, ssbmod_amplitude = 0.08, mw_power = -1, mw_switch = False)
            
            f0m_temp, u_f0m_temp = dark_esr_auto_analysis.analyze_dark_esr(f0m_temp, 
                qt.exp_params['samples'][SAMPLE]['N_HF_frq']*1e-9,do_save=save_plots, sweep_direction ='right')
                
                #ms=-1 fine
            DESR_msmt.darkesr('magnet_scanner_calib_fine' + str(ll) + '_' + str(k),  ms = 'msm', 
                    range_MHz=range_fine, pts=pts_fine, reps=reps_fine, freq=f0m_temp*1e9,# - N_hyperfine,
                    pulse_length = 9e-6, ssbmod_amplitude = 0.08/3,  mw_power = -1, mw_switch = False)
        
        # f0m_temp, u_f0m_temp = dark_esr_auto_analysis.analyze_dark_esr_double(do_plot=save_plots)
        # f0m_temp = f0m_temp
               
        # print 
        # print '-----------------------------'
        # print 'Fitted ms-1 transition frequency is '+str(round(f0m_temp,6))+' GHz' + ' +/- ' + str(round(u_f0m_temp*1e6,1)) + ' khz'
