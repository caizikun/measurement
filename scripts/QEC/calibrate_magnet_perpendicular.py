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


#SET AXIS TO SCAN, range and number of steps to scan over
axis = 'x_axis'
scan_range = 2000
no_of_steps = 20
no_of_rounds = 4

execfile(qt.reload_current_setup)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

nm_per_step = qt.exp_params['magnet']['nm_per_step']

current_f_msp1 = qt.exp_params['samples'][SAMPLE]['ms+1_cntr_frq']
current_f_msm1 = qt.exp_params['samples'][SAMPLE]['ms-1_cntr_frq']
ZFS = qt.exp_params['samples'][SAMPLE]['zero_field_splitting']

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


    #create the lists to save the data to

    f0m = []
    u_f0m = []
    f0p = []
    u_f0p = []
    Bx_field_measured = []
    Bz_field_measured = []
    f_centre_list = []
    steps_list = []

    step_size= 2*scan_range/no_of_steps #because we go one way and the other

    #we want to do several round, one way and back
    for x_iterations in range(no_of_rounds*no_of_steps):
        if x_iterations%no_of_steps < (no_of_steps/4) or x_iterations%no_of_steps>(no_of_steps*3/4-1):
            sign = +1
        else:
            sign = -1

        steps_list.append(x_iterations%no_of_steps*sign*step_size)

        #divide the step_size to steps of 10
        for i in range((scan_range/no_of_steps)/10):
            mom.step('x_axis',sign*10)
            qt.msleep(1)
            GreenAOM.set_power(5e-6)
            counters.set_is_running(True)
            int_time = 100   #(ms)
            counts = ins_adwin.measure_counts(int_time)[counter-1]
            if counts < 2e3:
                optimiz0r.optimize(dims=['x','y','z','x','y'])

        optimiz0r.optimize(dims=['x','y','z','x','y'])

        #measure both ESR's

        darkesrm1_auto(SAMPLE_CFG+'_magnet_calibration')
        f0m_temp,u_f0m_temp = dark_esr_auto_analysis.analyze_dark_esr(current_f_msm1*1e-9,qt.exp_params['samples'][SAMPLE]['N_HF_frq']*1e-9 )

        qt.msleep(1)
        
        darkesrp1_auto(SAMPLE_CFG+'_magnet_calibration')
        f0p_temp,u_f0p_temp = dark_esr_auto_analysis.analyze_dark_esr(current_f_msp1*1e-9,qt.exp_params['samples'][SAMPLE]['N_HF_frq']*1e-9 )

        Bz_measured, Bx_measured = mt.get_B_field(msm1_freq=f0m_temp, msp1_freq=f0p_temp)
        f_centre = (f0m[x_iterations]+f0p[x_iterations])/2

        f0m.append(f0m_temp)
        u_f0m.append(u_f0m_temp)
        f0p.append(f0p_temp)
        u_f0p.append(u_f0_temp)
        f_centre_list.append(f_centre)
        Bx_field_measured.append(Bx_measured)
        Bz_field_measured.append(Bz_measured)

        print 'Fitted ms-1 transition frequency is '+str(f0m_temp)+' GHz'
        print 'Fitted ms+1 transition frequency is '+str(f0p_temp)+' GHz'
        print 'Calculated centre between ms=-1 and ms=+1 is '+ str(f_centre)+' GHz +/- '+str((uf0m[x_iterations]+uf0p[x_iterations])/2*1e6)+' kHz'
        print 'Current ZFS is '+str(ZFS*1e-9)+ ' GHz, centre is '+ str((f_centre-ZFS*1e-9)*1e6)+ 'kHz away from ZFS'
        print 'Measured B_field is: Bz = '+str(Bz_measured)+ ' G ,Bx = '+str(Bx_measured)+ ' G'


    d = qt.Data(name=SAMPLE_CFG+'_magnet_calibration')
    d.add_coordinate('steps_list')
    d.add_value('ms-1 transition frequency (GHz)')
    d.add_value('ms+1 transition frequency error (GHz)')
    d.add_value('ms-1 transition frequency (GHz)')
    d.add_value('ms+1 transition frequency error (GHz)')
    d.add_value('center frequency (GHz)')
    d.add_value('measured Bx field (G)')
    d.add_value('measured Bz field (G)')

    d.create_file()
    filename=d.get_filepath()[:-4]
    d.add_data_point(steps_list, f0m,u_f0m,f0p,u_f0p,f_centre_list,Bx_field_measured,Bz_field_measured)
    d.close_file()

