"""
Script for calibrating the x and y axis B-field vs steps
Important: choose the right domain for the range of positions in get_magnet_position in magnet tools!

"""
import numpy as np
import qt
import msvcrt
# import the msmt class
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt
# import the dESR fit
from analysis.lib.fitting import dark_esr_auto_analysis; reload(dark_esr_auto_analysis)
# import magnet tools and master of magnet
from measurement.lib.tools import magnet_tools as mt; reload(mt)
mom = qt.instruments['master_of_magnet']

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

def darkesr_auto(name, ms = 'msp'):

    m = pulsar_msmt.DarkESR(name)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    
    if ms == 'msp':
        m.params['mw_frq'] = m.params['ms+1_cntr_frq']-43e6 #MW source frequency
        m.params['ssbmod_amplitude'] = 0.03
    elif ms == 'msm':
        m.params['mw_frq'] = 2*m.params['zero_field_splitting'] - m.params['ms+1_cntr_frq'] - 43e6
        m.params['ssbmod_amplitude'] = 0.015
  
    m.params['repetitions'] = 500
    m.params['ssbmod_frq_start'] = 43e6 - 5.5e6
    m.params['ssbmod_frq_stop'] = 43e6 + 5.5e6
    m.params['pts'] = 121
    m.params['pulse_length'] = 2e-6
    
    m.autoconfig()
    m.generate_sequence()
    m.run()
    m.save()
    m.finish()

if __name__ == '__main__':
    
    ### Set input parameters ###
    axis = 'Y_axis'
    scan_range       = 400      # From -scan range/2 to +scan range/2  
    no_of_steps      = 5          # with a total of no_of_steps measurment points.
    magnet_step_size = 50         # the sample position is checked after each magnet_step_size
    mom.set_mode(axis, 'stp')     # turn on or off the stepper

    #calculate steps to do
    stepsize = scan_range/(no_of_steps-1) 
    steps = [0] + (no_of_steps-1)/2*[stepsize] + (no_of_steps-1)*[-stepsize] + (no_of_steps-1)/2*[stepsize] 
    steps = [0, -scan_range/2] + (no_of_steps-1)*[stepsize]
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
        qt.msleep(3)
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

        #measure both ESR's
        darkesr_auto(SAMPLE_CFG+'_magnet_calibration', ms = 'msm')
        f0m_temp,u_f0m_temp = dark_esr_auto_analysis.analyze_dark_esr(current_f_msm1*1e-9,qt.exp_params['samples'][SAMPLE]['N_HF_frq']*1e-9 )
        
        qt.msleep(1)
        
        darkesr_auto(SAMPLE_CFG+'_magnet_calibration', ms = 'msp')
        f0p_temp,u_f0p_temp = dark_esr_auto_analysis.analyze_dark_esr(current_f_msp1*1e-9,qt.exp_params['samples'][SAMPLE]['N_HF_frq']*1e-9 )

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

        print 'Fitted ms-1 transition frequency is '+str(f0m_temp)+' GHz'
        print 'Fitted ms+1 transition frequency is '+str(f0p_temp)+' GHz'
        print 'Calculated centre between ms=-1 and ms=+1 is '+ str(f_centre)+' GHz +/- '+str((u_f0m_temp**2+u_f0p_temp**2)**(1./2)/2*1e6)+' kHz'
        print 'Current ZFS is '+str(ZFS*1e-9)+ ' GHz, centre is '+ str((f_centre-ZFS*1e-9)*1e6)+ 'kHz away from ZFS'
        print 'Measured B_field is: Bz = '+str(Bz_measured)+ ' G ,Bx = '+str(Bx_measured)+ ' G'
        
   
    qt.mstart()

    d = qt.Data(name=SAMPLE_CFG+'_magnet_calibration')
    
    d.add_coordinate('position')
    d.add_value('ms-1 transition frequency (GHz)')
    d.add_value('ms+1 transition frequency error (GHz)')
    d.add_value('ms-1 transition frequency (GHz)')
    d.add_value('ms+1 transition frequency error (GHz)')
    d.add_value('center frequency (GHz)')
    d.add_value('measured Bx field (G)')
    d.add_value('measured Bz field (G)')
    print positions  
    d.create_file()
    filename=d.get_filepath()[:-4]
    d.add_data_point(positions, f0m,u_f0m,f0p,u_f0p,f_centre_list,Bx_field_measured,Bz_field_measured)
    d.close_file()
    
    
    positions[0] = positions[0] + 0.001 #for some reason the plot below cannot handle twice the same x-coordinate
    print positions
    p_c = qt.Plot2D(positions, f_diff_list, 'bO-', name='f_centre relative to ZFS', clear=True)
    p_c.save_png(filename+'.png')

    qt.mend()
