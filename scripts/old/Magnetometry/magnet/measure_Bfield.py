"""
Script that measures the current B_field
"""
import numpy as np
import qt
import msvcrt
# import the msmt class
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
# import the dESR fit
from analysis.lib.fitting import dark_esr_auto_analysis; reload(dark_esr_auto_analysis)
# import magnet tools and master of magnet
from measurement.lib.tools import magnet_tools as mt; reload(mt)

execfile(qt.reload_current_setup)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

nm_per_step = qt.exp_params['magnet']['nm_per_step']
current_f_msp1 = qt.exp_params['samples'][SAMPLE]['ms+1_cntr_frq']
current_f_msm1 = qt.exp_params['samples'][SAMPLE]['ms-1_cntr_frq']
ZFS = qt.exp_params['samples'][SAMPLE]['zero_field_splitting']

def darkesr(name, ms = 'msp'):

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
  
    m.params['repetitions'] = 1000
    m.params['ssbmod_frq_start'] = 43e6 - 5.5e6
    m.params['ssbmod_frq_stop'] = 43e6 + 5.5e6
    m.params['pts'] = 81
    m.params['pulse_length'] = 2e-6
    
    m.autoconfig()
    m.generate_sequence()
    m.run()
    m.save()
    m.finish()

if __name__ == '__main__':
    
    repetitions = 5
    ## Create the lists to save the data to
    f0m = []; u_f0m = []; f0p = [] ;u_f0p = []
    Bx_field_measured = []
    Bz_field_measured = []
    f_centre_list = []; f_diff_list=[]
    
    for kk in range(repetitions):

        print '-----------------------------------'            
        print 'press q to stop measurement cleanly'
        print '-----------------------------------'
        qt.msleep(3)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            break

        print 'measurement_' + str(kk) + '/' + str(repetitions)

        ## measure both ESR's
        darkesr(SAMPLE_CFG+'_magnet_stability_msmt_msm_' + str(kk), ms = 'msm')
        f0m_temp,u_f0m_temp = dark_esr_auto_analysis.analyze_dark_esr(current_f_msm1*1e-9,qt.exp_params['samples'][SAMPLE]['N_HF_frq']*1e-9 )
            
        qt.msleep(1)
            
        darkesr(SAMPLE_CFG+'_magnet_stability_msmt_msp_' + str(kk), ms = 'msp')
        f0p_temp,u_f0p_temp = dark_esr_auto_analysis.analyze_dark_esr(current_f_msp1*1e-9,qt.exp_params['samples'][SAMPLE]['N_HF_frq']*1e-9 )

        Bz_measured, Bx_measured = mt.get_B_field(msm1_freq=f0m_temp*1e9, msp1_freq=f0p_temp*1e9)
        f_centre = (f0m_temp+f0p_temp)/2
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

        GreenAOM.set_power(5e-6)
        optimiz0r.optimize(dims=['x','y','z'])

    ## SAVE THE DATA
    qt.mstart()

    d = qt.Data(name=SAMPLE_CFG+'_magnet_stability_msmt')
    d.add_value('ms-1 transition frequency (GHz)')
    d.add_value('ms+1 transition frequency error (GHz)')
    d.add_value('ms-1 transition frequency (GHz)')
    d.add_value('ms+1 transition frequency error (GHz)')
    d.add_value('center frequency (GHz)')
    d.add_value('measured Bx field (G)')
    d.add_value('measured Bz field (G)')

    d.create_file()
    filename=d.get_filepath()[:-4]
    d.add_data_point(f0m,u_f0m,f0p,u_f0p,f_centre_list,Bx_field_measured,Bz_field_measured)
    d.close_file()

    #d.create_file()
    #filename=d.get_filepath()[:-4] + 'average_only'
    #d.add_data_point(f_centre_list)
    #d.close_file()

    p_c = qt.Plot2D(range(len(f_diff_list)), f_diff_list, 'bO-', name='f_centre', clear=True)
    p_c.save_png(filename+'.png')

    qt.mend()
    