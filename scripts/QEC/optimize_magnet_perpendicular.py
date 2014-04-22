"""
Script for calibrating the x and y axis B-field vs steps
Important: choose the right domain for the range of positions in get_magnet_position in magnet tools!

"""
import numpy as np
import qt
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
import msvcrt

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt

# import the dESR fit
from analysis.lib.fitting import dark_esr_auto_analysis

# import magnet tools and master of magnet
from measurement.lib.tools import magnet_tools as mt
mom = qt.instruments['master_of_magnet']
reload(mt)


#SET AXIS TO SCAN, range and no of steps to scan over
axis_list = ['x_axis','y_axis']
first_step_size = 100 (to find out which way to move)

execfile(qt.reload_current_setup)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

nm_per_step = qt.exp_params['magnet']['nm_per_step']

current_f_msp1 = qt.exp_params['samples'][SAMPLE]['ms+1_cntr_frq']
current_f_msm1 = qt.exp_params['samples'][SAMPLE]['ms-1_cntr_frq']
ZFS = qt.exp_params['samples'][SAMPLE]['zero_field_splitting']

# Define the wanted magnet position
B_field_ideal = mt.convert_f_to_Bz(freq=current_f_msp1)
position_ideal = mt.get_magnet_position(msp1_freq=current_f_msp1,ms = 'plus',solve_by = 'list')
B_error_range = 2e-3 # allowed error in B_field (it was 7mG in RT experiment, can be changed)

ZFS_error = 30e3


def darkesr_auto(name,upload=False):

    m = pulsar_msmt.DarkESR(name)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])

    m.params['mw_frq'] = m.params['ms+1_cntr_frq']-43e6 #MW source frequency
    #m.params['mw_frq'] = 2*m.params['zero_field_splitting'] - m.params['ms-1_cntr_frq'] -43e6

    m.params['mw_power'] = 20
    m.params['repetitions'] = 1000

    m.params['ssbmod_frq_start'] = 43e6 - 6e6
    m.params['ssbmod_frq_stop'] = 43e6 + 6e6
    m.params['pts'] = 61
    m.params['pulse_length'] = 2e-6
    m.params['ssbmod_amplitude'] = 0.05

    m.autoconfig()
    m.generate_sequence(upload=upload)
    m.run()
    m.save()
    m.finish()


def darkesrm1_auto(name,upload=True):

    m = pulsar_msmt.DarkESR(name)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])

    m.params['mw_frq'] = 2*m.params['zero_field_splitting'] - m.params['ms+1_cntr_frq'] - m.params['mw_mod_freq']
    #m.params['mw_frq'] = 2*m.params['zero_field_splitting'] - m.params['ms-1_cntr_frq'] -43e6

    m.params['mw_power'] = 20
    m.params['repetitions'] = 1000

    m.params['ssbmod_frq_start'] = 43e6 - 6e6
    m.params['ssbmod_frq_stop'] = 43e6 + 6e6
    m.params['pts'] = 61
    m.params['pulse_length'] = 2e-6
    m.params['ssbmod_amplitude'] = 0.05

    m.autoconfig()
    m.generate_sequence(upload=upload)
    m.run()
    m.save()
    m.finish()

if __name__ == '__main__':

    iterations = 0

    darkesrm1_auto(SAMPLE_CFG+'_magnet_calibration')
    f0m_temp,u_f0m_temp = dark_esr_auto_analysis.analyze_dark_esr(current_f_msm1*1e-9,qt.exp_params['samples'][SAMPLE]['N_HF_frq']*1e-9 )

    darkesrp1_auto(SAMPLE_CFG+'_magnet_calibration')
    f0p_temp,u_f0p_temp = dark_esr_auto_analysis.analyze_dark_esr(current_f_msp1*1e-9,qt.exp_params['samples'][SAMPLE]['N_HF_frq']*1e-9 )

    Bz_measured, Bx_measured[iterations] = mt.get_B_field(msm1_freq=f0m_temp, msp1_freq=f0p_temp)
    f_centre = (f0m[x_iterations]+f0p[x_iterations])/2


    print 'Fitted ms-1 transition frequency is '+str(f0m_temp)+' GHz'
    print 'Fitted ms+1 transition frequency is '+str(f0p_temp)+' GHz'
    print 'Calculated centre between ms=-1 and ms=+1 is '+ str(f_centre)+' GHz +/- '+str((uf0m[x_iterations]+uf0p[x_iterations])/2*1e6)+' kHz'
    print 'Current ZFS is '+str(ZFS*1e-9)+ ' GHz, centre is '+ str((f_centre-ZFS*1e-9)*1e6)+ 'kHz away from ZFS'
    print 'Measured B_field is: Bz = '+str(Bz_measured)+ ' G ,Bx = '+str(Bx_measured)+ ' G'

    print 'press q to stop measurement loop. Do you want to continue to optimize the field?'
    qt.msleep(5)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        break

    for axis in axis_list:
        sign = +1

        iterations = iterations+1

        for i in range(first_step_size/10):
            mom.step('x_axis',sign*10)
            qt.msleep(1)
            GreenAOM.set_power(5e-6)
            counters.set_is_running(True)
            ## put something in that reads counts!!!!
            if counts < XXX:
                optimiz0r.optimize(dims=['x','y','z','x','y'])

        darkesrm1_auto(SAMPLE_CFG+'_magnet_calibration')
        f0m_temp,u_f0m_temp = dark_esr_auto_analysis.analyze_dark_esr(current_f_msm1*1e-9,qt.exp_params['samples'][SAMPLE]['N_HF_frq']*1e-9 )

        darkesrp1_auto(SAMPLE_CFG+'_magnet_calibration')
        f0p_temp,u_f0p_temp = dark_esr_auto_analysis.analyze_dark_esr(current_f_msp1*1e-9,qt.exp_params['samples'][SAMPLE]['N_HF_frq']*1e-9 )

        Bz_measured, Bx_measured[iterations] = mt.get_B_field(msm1_freq=f0m_temp, msp1_freq=f0p_temp)
        f_centre = (f0m[x_iterations]+f0p[x_iterations])/2

        print 'Fitted ms-1 transition frequency is '+str(f0m_temp)+' GHz'
        print 'Fitted ms+1 transition frequency is '+str(f0p_temp)+' GHz'
        print 'Calculated centre between ms=-1 and ms=+1 is '+ str(f_centre)+' GHz +/- '+str((uf0m[x_iterations]+uf0p[x_iterations])/2*1e6)+' kHz'
        print 'Current ZFS is '+str(ZFSe9)+ ' GHZ, centre is '+ str((f_centre-ZFS)*1e6)+ 'kHz away from ZFS'
        print 'Measured B_field is: Bz = '+str(Bz_measured)+ ' G ,Bx = '+str(Bx_measured)+ ' G'

        print 'press q to stop measurement loop. Do you want to continue to optimize the field?'
        qt.msleep(5)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            break

        
        if Bx_measured[iterations] > Bx_measured[iterations-1]:
            sign = sign*1 #move magnet in other direction
        else:
            sign = sign
