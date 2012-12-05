#This measurement allows one to read out the spin after turning the spin using 
#microwaves. min_mw_pulse_length is the minimum length of the microwave pulse.
#mwfrequency is the frequency of the microwaves. Note that LT1 has a amplifier,
#don't blow up the setup!!! 

import qt
import numpy as np
import ctypes
import inspect
import time as dtime
import msvcrt
import measurement.measurement as meas
from measurement.AWG_HW_sequencer_v2 import Sequence
import measurement.PQ_measurement_generator_v2 as pqm


from measurement.config import awgchannels_lt2 as awgcfg
from measurement.sequence import common as commonseq
from measurement.sequence import mwseq_calibration as cal
from analysis import lde_calibration 


nr_of_datapoints =          21      #max nr_of_datapoints should be < 10000
repetitions_per_datapoint = 1000


f_drive =                   2.8287E9#2.85877E9#2.854E9         #in Hz
pi_pulse_length =           62
pi_over_two_length =        31
time_between_pulses =       10#476/2
mwpower_lt1 =               0               #in dBm
mwpower_lt2 =               -6              #in dBm
f_mw = f_drive #- 30E6
amplitude_ssbmod = 0.48 #do not exceed 0.8, weird stuff happens: ask Wolfgang 

##########CORPSE############
pulse_420_length   =   145 # ns
pulse_300_length   =   103
pulse_60_length    =   21
time_between_CORPSE = 0 #ns

duty_cycle_time     = 5000 # ns, wait time at the end of each sequence element
max_seq_time= 10

#time=np.linspace(min_time,max_time,nr_of_datapoints)
lt1 = False

awg = qt.instruments['AWG']
temp = qt.instruments['temperature_lt1']

if lt1:
    ins_green_aom=qt.instruments['GreenAOM_lt1']
    ins_E_aom=qt.instruments['MatisseAOM_lt1']
    ins_A_aom=qt.instruments['NewfocusAOM_lt1']
    adwin=qt.instruments['adwin_lt1']
    counters=qt.instruments['counters_lt1']
    physical_adwin=qt.instruments['physical_adwin_lt1']
    microwaves = qt.instruments['SMB_100_lt1']
    ctr_channel=2
    mwpower = mwpower_lt1
    microwaves.set_status('off')
else:
    ins_green_aom=qt.instruments['GreenAOM']
    ins_E_aom=qt.instruments['MatisseAOM']
    ins_A_aom=qt.instruments['NewfocusAOM']
    adwin = adwin_lt2 #adwin=qt.instruments['adwin']
    counters=qt.instruments['counters']
    physical_adwin=qt.instruments['physical_adwin']
    microwaves = qt.instruments['SMB100']
    ctr_channel=1
    mwpower = mwpower_lt2
    microwaves.set_status('off')




par = {}
par['counter_channel'] =              ctr_channel
par['green_laser_DAC_channel'] =      adwin.get_dac_channels()['green_aom']
par['Ex_laser_DAC_channel'] =         adwin.get_dac_channels()['matisse_aom']
par['A_laser_DAC_channel'] =          adwin.get_dac_channels()['newfocus_aom']
par['AWG_start_DO_channel'] =         1
par['AWG_done_DI_channel'] =          8
par['send_AWG_start'] =               1
par['wait_for_AWG_done'] =            0
par['green_repump_duration'] =        10
par['CR_duration'] =                  100
par['SP_duration'] =                  50
par['SP_filter_duration'] =           0
par['sequence_wait_time'] =           int(ceil(max_seq_time/1e3)+1)
par['wait_after_pulse_duration'] =    1
par['CR_preselect'] =                 1000
par['RO_repetitions'] =               int(nr_of_datapoints*repetitions_per_datapoint)
par['RO_duration'] =                  26
par['sweep_length'] =                 int(nr_of_datapoints)
par['cycle_duration'] =               300
par['CR_probe'] =                     100

par['green_repump_amplitude'] =       200e-6
par['green_off_amplitude'] =          0e-6
par['Ex_CR_amplitude'] =              10e-9 #OK
par['A_CR_amplitude'] =               15e-9 #OK
par['Ex_SP_amplitude'] =              0
par['A_SP_amplitude'] =               15e-9 #OK: PREPARE IN MS = 0
par['Ex_RO_amplitude'] =              10e-9 #OK: READOUT MS = 0
par['A_RO_amplitude'] =               0e-9

par['min_sweep_par'] =                  0
par['max_sweep_par'] =                  1
par['sweep_par_name'] =                 ''
ins_green_aom.set_power(0.)
ins_E_aom.set_power(0.)
ins_A_aom.set_power(0.)
ins_green_aom.set_cur_controller('ADWIN')
ins_E_aom.set_cur_controller('ADWIN')
ins_A_aom.set_cur_controller('ADWIN')
ins_green_aom.set_power(0.)
ins_E_aom.set_power(0.)
ins_A_aom.set_power(0.)


###########################################################
##
##  hardcoded in ADwin program (adjust there if necessary!)
##

max_SP_bins = 500
max_RO_dim = 1000000

##
###########################################################
def start_measurement(generate_sequence,sweep_param,pulse_dict,name=''):
    microwaves.set_iq('on')
    microwaves.set_frequency(f_mw)
    microwaves.set_pulm('on')
    microwaves.set_power(mwpower)
    counters.set_is_running(False)
    sequence = generate_sequence(sweep_param,pulse_dict)
    par['RO_repetitions'] =               int(nr_of_datapoints*repetitions_per_datapoint)
    par['RO_duration'] =                  26
    par['sweep_length'] =                 int(nr_of_datapoints)
    par['sequence_wait_time'] =           int(ceil(sequence["max_seq_time"]/1e3)+1)
    
    par['min_sweep_par'] =                  sweep_param.min()
    par['max_sweep_par'] =                  sweep_param.max()
    
    awg.set_runmode('SEQ')
    awg.start()  
    while awg.get_state() != 'Waiting for trigger':
        qt.msleep(1)
    data = meas.Measurement(sequence["seqname"],name)
    microwaves.set_status('on')
    spin_control(name,data,par)
    end_measurement()


def spin_control(name, data, par):
    par['green_repump_voltage'] = ins_green_aom.power_to_voltage(par['green_repump_amplitude'])
    par['green_off_voltage'] = 0.01#ins_green_aom.power_to_voltage(par['green_off_amplitude'])
    par['Ex_CR_voltage'] = ins_E_aom.power_to_voltage(par['Ex_CR_amplitude'])
    par['A_CR_voltage'] = ins_A_aom.power_to_voltage(par['A_CR_amplitude'])
    par['Ex_SP_voltage'] = ins_E_aom.power_to_voltage(par['Ex_SP_amplitude'])
    par['A_SP_voltage'] = ins_A_aom.power_to_voltage(par['A_SP_amplitude'])
    par['Ex_RO_voltage'] = ins_E_aom.power_to_voltage(par['Ex_RO_amplitude'])
    par['A_RO_voltage'] = ins_A_aom.power_to_voltage(par['A_RO_amplitude'])

    if  (par['SP_duration'] > max_SP_bins) or \
        (par['sweep_length']*par['RO_duration'] > max_RO_dim):
            print ('Error: maximum dimensions exceeded')
            return(-1)

    #print 'SP E amplitude: %s'%par['Ex_SP_voltage']
    #print 'SP A amplitude: %s'%par['A_SP_voltage']

    adwin.start_spincontrol(
        counter_channel = par['counter_channel'],
        green_laser_DAC_channel = par['green_laser_DAC_channel'],
        Ex_laser_DAC_channel = par['Ex_laser_DAC_channel'],
        A_laser_DAC_channel = par['A_laser_DAC_channel'],
        AWG_start_DO_channel = par['AWG_start_DO_channel'],
        AWG_done_DI_channel = par['AWG_done_DI_channel'],
        send_AWG_start = par['send_AWG_start'],
        wait_for_AWG_done = par['wait_for_AWG_done'],
        green_repump_duration = par['green_repump_duration'],
        CR_duration = par['CR_duration'],
        SP_duration = par['SP_duration'],
        SP_filter_duration = par['SP_filter_duration'],
        sequence_wait_time = par['sequence_wait_time'],
        wait_after_pulse_duration = par['wait_after_pulse_duration'],
        CR_preselect = par['CR_preselect'],
        RO_repetitions = par['RO_repetitions'],
        RO_duration = par['RO_duration'],
        sweep_length = par['sweep_length'],
        cycle_duration = par['cycle_duration'],
        green_repump_voltage = par['green_repump_voltage'],
        green_off_voltage = par['green_off_voltage'],
        Ex_CR_voltage = par['Ex_CR_voltage'],
        A_CR_voltage = par['A_CR_voltage'],
        Ex_SP_voltage = par['Ex_SP_voltage'],
        A_SP_voltage = par['A_SP_voltage'],
        Ex_RO_voltage = par['Ex_RO_voltage'],
        A_RO_voltage = par['A_RO_voltage'])
        
    if lt1:
        adwin_lt2.start_check_trigger_from_lt1()

    CR_counts = 0
    while (physical_adwin.Process_Status(9) == 1):
        reps_completed = physical_adwin.Get_Par(73)
        CR_counts = physical_adwin.Get_Par(70) - CR_counts
        cts = physical_adwin.Get_Par(26)
        trh = physical_adwin.Get_Par(25)
        print('completed %s / %s readout repetitions, %s CR counts/s'%(reps_completed,par['RO_repetitions'], CR_counts))
        print('threshold: %s cts, last CR check: %s cts'%(trh,cts))
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
            break

        qt.msleep(2.5)
    physical_adwin.Stop_Process(9)
    
    if lt1:
        adwin_lt2.stop_check_trigger_from_lt1()

    reps_completed  = physical_adwin.Get_Par(73)
    print('completed %s / %s readout repetitions'%(reps_completed,par['RO_repetitions']))

    sweep_length = par['sweep_length']
    par_long   = physical_adwin.Get_Data_Long(20,1,25)
    par_float  = physical_adwin.Get_Data_Float(20,1,10)
    CR_before = physical_adwin.Get_Data_Long(22,1,1)
    CR_after  = physical_adwin.Get_Data_Long(23,1,1)
    SP_hist   = physical_adwin.Get_Data_Long(24,1,par['SP_duration'])
    RO_data   = physical_adwin.Get_Data_Long(25,1,
                    sweep_length * par['RO_duration'])
    RO_data = reshape(RO_data,(sweep_length,par['RO_duration']))
    SSRO_data   = physical_adwin.Get_Data_Long(27,1,
                    sweep_length * par['RO_duration'])
    SSRO_data = reshape(SSRO_data,(sweep_length,par['RO_duration']))
    statistics = physical_adwin.Get_Data_Long(26,1,10)

    sweep_index = arange(sweep_length)
    sp_time = arange(par['SP_duration'])*par['cycle_duration']*3.333
    ro_time = arange(par['RO_duration'])*par['cycle_duration']*3.333


    data.save()
    savdat={}
    savdat['counts']=CR_after
    data.save_dataset(name='ChargeRO_after', do_plot=False, 
        data = savdat, idx_increment = False)
    savdat={}
    savdat['time']=sp_time
    savdat['counts']=SP_hist
    data.save_dataset(name='SP_histogram', do_plot=False, 
        data = savdat, idx_increment = False)
    savdat={}
    savdat['time']=ro_time
    savdat['sweep_axis']=sweep_index
    savdat['counts']=RO_data
    savdat['SSRO_counts']=SSRO_data
    data.save_dataset(name='Spin_RO', do_plot=False, 
        data = savdat, idx_increment = False)
    savdat={}
    savdat['par_long']=par_long
    savdat['par_float']=par_float
    data.save_dataset(name='parameters', do_plot=False, 
        data = savdat, idx_increment = False)
    
    ######################
    ###statistics file####
    ######################
    savdat={}
    savdat['completed_repetitions']=(reps_completed/sweep_length)
    savdat['total_repumps']=statistics[0]
    savdat['total_repump_counts']=statistics[1]
    savdat['noof_failed_CR_checks']=statistics[2]
    savdat['mw_center_freq']=f_mw
    savdat['mw_drive_freq']=f_drive
    savdat['mw_power']=mwpower
    savdat['min_pulse_nr']=par['min_sweep_par']
    savdat['max_pulse_nr']=par['max_sweep_par']
    savdat['min_pulse_amp']=par['min_sweep_par']
    savdat['max_pulse_amp']=par['max_sweep_par']
    savdat['min_time'] = par['min_sweep_par']
    savdat['max_time'] = par['max_sweep_par']
    savdat['min_sweep_par']=par['min_sweep_par']
    savdat['max_sweep_par']=par['max_sweep_par']
    savdat['sweep_par_name'] = par['sweep_par_name']
    savdat['noof_datapoints']=nr_of_datapoints
    
    data.save_dataset(name='statics_and_parameters', do_plot=False, 
        data = savdat, idx_increment = True)
   
    return 

def end_measurement():
    awg.stop()
    awg.set_runmode('CONT')
    adwin.set_simple_counting()
    counters.set_is_running(True)
    ins_green_aom.set_power(200e-6)   
    microwaves.set_status('off')
    microwaves.set_iq('off')
    microwaves.set_pulm('off')
    ins_E_aom.set_power(0)
    ins_A_aom.set_power(0)



def power_and_mw_ok():
    ret = True
    max_E_power = ins_E_aom.get_cal_a()
    max_A_power = ins_A_aom.get_cal_a()
    if (max_E_power < par['Ex_CR_amplitude']) or \
            (max_E_power < par['Ex_SP_amplitude']) or \
            (max_E_power < par['Ex_RO_amplitude']):
        print 'Trying to set too large value for E laser, quiting!'
        ret = False    
    if (max_A_power < par['A_CR_amplitude']) or \
            (max_A_power < par['A_SP_amplitude']) or \
            (max_A_power < par['A_RO_amplitude']):
        print 'Trying to set too large value for A laser, quiting'
        ret = False
    if mwpower > 0:
        print 'MW power > 0 dBm, are you sure you want to continue? Press q to quit, c to continue.'
        idx = 0
        max_idx = 5
        kb_hit = None
        while (idx<max_idx) and kb_hit == None:
            kb_hit = msvcrt.getch()
            if kb_hit == 'q':
                ret = False
            if kb_hit == 'c':
                ret = True
            qt.msleep(1)
            idx += 1
       
    return ret

def main():
    datafolder= 'D:/measuring/data/'
    date = dtime.strftime('%Y') + dtime.strftime('%m') + dtime.strftime('%d')
    datapath = datafolder+date + '/'
    nr_of_datapoints = 21
    
    min_pulse_amp =             0.0
    max_pulse_amp =             0.85
    amplitude = np.linspace(min_pulse_amp,max_pulse_amp,nr_of_datapoints)
    
    pulse_dict = {
            "Pi":{"duration": 58., "amplitude":0.5},
                "Pi_2":   {"duration": 29., "amplitude": 0.7},
                "init_state_pulse": {"duration":29. , "amplitude":0.7,  
                                "Do_Pulse": False},
                "time_between_pulses": 10.,
                "nr_of_pulses": 1.,
                "duty_cycle_time": 20000.,                             
                }
    execfile('ssro_ADwinv2.py')
    path = lde_calibration.find_newest_data(datapath,string='ADwin_SSRO_')
    ssro_dict=lde_calibration.ssro_calibration(path)
    #return ssro_dict
    par['RO_duration'] = int(round(ssro_dict["t_max"]))
    
    ins_green_aom.set_power(30e-6)
    execfile('esr.py')
    
    path = lde_calibration.find_newest_data(datapath,string='ESR')
    f_fit=lde_calibration.esr_calibration(path)
    
    f_drive=f_fit
    print f_drive
    microwaves.set_frequency(f_drive)

    start_measurement(cal.Pi_Pulse_amp,amplitude,pulse_dict,name='Cal_Pi_amp')

    #par[''] = 
    par['sweep_par_name'] = 'Pi Pulse amp'
    path = lde_calibration.find_newest_data(datapath,string='Cal_Pi')
    fit_amp = lde_calibration.rabi_calibration(path,close_fig=False)
    print fit_amp
    pulse_dict["nr_of_pulses"] = 5
    pulse_dict["duty_cycle_time"] = 500
    min_pulse_amp=fit_amp-0.1
    max_pulse_amp=fit_amp+0.1
    amplitude = np.linspace(min_pulse_amp,max_pulse_amp,nr_of_datapoints)
    print amplitude
    start_measurement(cal.Pi_Pulse_amp,amplitude,pulse_dict,name='Cal_5_Pi_amp')
    path = lde_calibration.find_newest_data(datapath,string='Cal_5_Pi')
    fit_amp = lde_calibration.rabi_calibration(path,new_fig=False,close_fig=True)
    print fit_amp


    # evt Rabi oscilatie
    #path = lde_calibration.find_newest_data(datapath,string='rabi')
    #rabi_calibration(path,ssro_dict=ssro_dict)



if __name__ == '__main__':
    main()


