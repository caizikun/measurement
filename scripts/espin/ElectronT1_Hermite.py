"""
Script for T1 measurement using Hermite pulses, based on pulsar_msmt.ElectronT1
"""
import numpy as np
import qt
import sys
import msvcrt

#reload all parameters and modules
execfile(qt.reload_current_setup)

import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2


# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
from measurement.lib.pulsar import pulse, pulselib, element, pulsar
from measurement.lib.measurement2.adwin_ssro import pulse_select as ps
from analysis.lib.tools import toolbox
from analysis.lib.fitting import dark_esr_auto_analysis; reload(dark_esr_auto_analysis)
from analysis.lib.m2.ssro import ssro as ssro_analysis
reload(ssro_analysis)


# from measurement.scripts.lt1_scripts.quantum_memory import calibrate_quantum_memory as cqm

SAMPLE= qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']
current_f_msm1 = qt.exp_params['samples'][SAMPLE]['ms-1_cntr_frq']
magnet_Z_scanner = qt.instruments['conex_scanner_Z']
temperature_sensor = qt.instruments['kei2000']

def electronT1hermite(name, T1_initial_state = 'ms=0', T1_readout_state = 'ms=0', start_time = None, end_time = None, pts = None,debug=False, repetitions=120, wait_times=[]):
    '''Electron T1 measurement using Hermite pulses
    '''

    m = ElectronT1Hermite(name)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    # Measurement settings
    if pts != None:
        m.params['pts'] = pts
    else:
        m.params['pts'] = 6

    # m.params['pts'] = 5
    m.params['wait_time_repeat_element'] = 10000 # in us
    # m.params['wait_times'] = np.linspace(0,200000,m.params['pts'])
    # m.params['wait_times'] = np.concatenate( (np.linspace(0,int(1e5), m.params['pts'] - 3), np.linspace(int(2e5), int(4e5),3))) # in us
    # m.params['wait_times'] = np.concatenate( (np.linspace(0,int(6e5), 3), np.linspace(int(1e6), int(15e6),m.params['pts'] - 3))) # in us
   
# commented out for test
    # if start_time != None:
    #     m.params['wait_times'] = np.linspace(start_time, end_time, m.params['pts'])
    # else:
    #      m.params['wait_times'] = np.concatenate( (np.linspace(0,int(6e5), 4), np.linspace(int(1e6), int(2e6),m.params['pts'] - 4))) # in us

    m.params['wait_times'] = array(wait_times)
    print array(wait_times)
  


    m.params['repetitions'] = repetitions
    m.params['T1_initial_state'] = T1_initial_state
    m.params['T1_readout_state'] = T1_readout_state

    # Instrument settings
    # m.params['MW_power'] = 20 # Hermite pi pulses are calibrated @ 20 dBm power
    m.params['Ex_SP_amplitude'] = 0
    # m.params['Ex_SP_amplitude']= 1e-9
   # m.params['A_SP_amplitude'] = 0

    # Parameters for analysis
    m.params['sweep_name'] = 'Waiting time (ms)'
    m.params['sweep_pts'] = m.params['wait_times'] * 1e-3

    # Run measurement
    m.autoconfig()
    m.generate_sequence(upload = True)

    if not debug:
        m.run()
        m.save()
        m.finish()



class ElectronT1Hermite(pulsar_msmt.ElectronT1):

    def generate_sequence(self, upload = True, debug = False):

        ### define basic pulses/times ###
        # pi-pulse, needs different pulses for ms=-1 and ms=+1 transitions in the future.
        X = ps.X_pulse(self)
        # Wait-times
        T = pulse.SquarePulse(channel='MW_Imod', name='delay',
            length = self.params['wait_time_repeat_element']*1e-6, amplitude = 0.)
        T_before_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
            length = 100e-9, amplitude = 0.) #the unit waittime is 10e-6 s
        T_after_p = pulse.SquarePulse(channel='MW_Imod', name='delay',
            length = (1000. - self.params['Hermite_pi_length'] * 1e9)*1e-9, amplitude = 0.) # waiting time chosen s.t. T_before_p + X + T_after_p = 1 us
        # Trigger pulse
        Trig = pulse.SquarePulse(channel = 'adwin_sync',
        length = 5e-6, amplitude = 2)

        ### create the elements/waveforms from the basic pulses ###
        list_of_elements = []

        #Pi-pulse element/waveform
        e = element.Element('Pi_pulse',  pulsar=qt.pulsar,
                global_time = True)
        e.append(T_before_p)
        e.append(pulse.cp(X))
        e.append(T_after_p)
        list_of_elements.append(e)

        #Wait time element/waveform
        e = element.Element('T1_wait_time',  pulsar=qt.pulsar,
                global_time = True)
        e.append(T)
        list_of_elements.append(e)

        #Trigger element/waveform
        e = element.Element('ADwin_trigger',  pulsar=qt.pulsar,
                global_time = True)
        e.append(Trig)
        list_of_elements.append(e)

        ### create sequences from the elements/waveforms ###
        seq = pulsar.Sequence('ElectronT1_sequence')

        for i in range(len(self.params['wait_times'])):

            if self.params['wait_times'][i]/self.params['wait_time_repeat_element'] !=0:
                if self.params['T1_initial_state'] == 'ms=-1':
                    seq.append(name='Init_Pi_pulse_%d'%i,wfname='Pi_pulse',trigger_wait=True)
                    seq.append(name='ElectronT1_wait_time_%d'%i, wfname='T1_wait_time', trigger_wait=False,repetitions=self.params['wait_times'][i]/self.params['wait_time_repeat_element'])
                    if self.params['T1_readout_state'] == 'ms=-1':
                        if i !=0:
                            seq.append(name='Readout_Pi_pulse_%d'%i,wfname='Pi_pulse',trigger_wait=False)
                    seq.append(name='ElectronT1_ADwin_trigger_%d'%i, wfname='ADwin_trigger', trigger_wait=False)
                #elif self.params['T1_initial_state'] == 'ms=+1':

                else:
                    seq.append(name='ElectronT1_wait_time_%d'%i, wfname='T1_wait_time', trigger_wait=True,repetitions=self.params['wait_times'][i]/self.params['wait_time_repeat_element'])
                    if self.params['T1_readout_state'] == 'ms=-1':
                        seq.append(name='Readout_Pi_pulse_%d'%i,wfname='Pi_pulse',trigger_wait=False)
                    seq.append(name='ElectronT1_ADwin_trigger_%d'%i, wfname='ADwin_trigger', trigger_wait=False)
            else:
                if self.params['T1_initial_state'] == 'ms=-1' and self.params['T1_readout_state'] == 'ms=0':
                    seq.append(name='Init_Pi_pulse_%d'%i,wfname='Pi_pulse',trigger_wait=True)
                    seq.append(name='ElectronT1_ADwin_trigger_%d'%i, wfname='ADwin_trigger', trigger_wait=False)
                elif self.params['T1_initial_state'] == 'ms=0' and self.params['T1_readout_state'] == 'ms=-1':
                    seq.append(name='Readout_Pi_pulse_%d'%i,wfname='Pi_pulse',trigger_wait=True)
                    seq.append(name='ElectronT1_ADwin_trigger_%d'%i, wfname='ADwin_trigger', trigger_wait=False)
                #elif self.params['T1_initial_state'] == 'ms=+1' and self.params['T1_readout_state'] == 'ms=0':
                #elif self.params['T1_readout_state'] == 'ms=+1' and self.params['T1_initial_state'] == 'ms=0':
                else:
                    seq.append(name='ElectronT1_ADwin_trigger_%d'%i, wfname='ADwin_trigger', trigger_wait=True)

                    ### added for test




         # upload the waveforms to the AWG
        if upload:
            qt.pulsar.program_awg(seq,*list_of_elements, debug = debug)







from measurement.lib.measurement2.adwin_ssro import ssro
# Magnetic field optimization during experiment
def darkesr(name, range_MHz, pts, reps, power, MW_power, pulse_length):

    m = pulsar_msmt.DarkESR_Switch(name)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['111_1_sil18']['pulses']) #Added to include the MW switch MA

    m.params['temp'] = temperature_sensor.get_readlastval()
    m.params['magnet_position'] = magnet_Z_scanner.GetPosition()

    m.params['mw_frq']      = m.params['ms-1_cntr_frq']-43e6 #MW source frequency

    m.params['mw_power']    = MW_power
    m.params['repetitions'] = reps

    m.params['ssbmod_frq_start'] = 43e6 - range_MHz*1e6 ## first time we choose a quite large domain to find the three dips (15)
    m.params['ssbmod_frq_stop']  = 43e6 + range_MHz*1e6
    m.params['pts'] = pts
    m.params['pulse_length'] = pulse_length
    m.params['ssbmod_amplitude'] = power #0.01

    m.params['sweep_pts'] = (np.linspace(m.params['ssbmod_frq_start'],
                    m.params['ssbmod_frq_stop'], m.params['pts']) 
                    + m.params['mw_frq'])*1e-9

    m.autoconfig()
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()

# ###################################################
def optimize_magnetic_field():

    safemode            = False    # If True then manual confirmation is needed befor each magnet movement
    optimization_target = 15     # Target difference frequency in kHz , first (03.08) was 10 then 7 then 10 again
    field_gradient      = 0.100     
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


## Run optimizor ##############
    GreenAOM.set_power(10e-6)
    counters.set_is_running(True)
    optimiz0r.optimize(dims=['x','y','z'], int_time=300)

    GreenAOM.set_power(10e-6)
    counters.set_is_running(True)
    optimiz0r.optimize(dims=['x','y','z'], int_time=300)

    name = 'SSRO_calib'
    ssrocalibration(name)

   ### SSRO Analysis
    ssro_analysis.ssrocalib()

#########################################

    f0 = []; u_f0 = []; delta_f0 =[]; iterations_list =[]; magnet_postion_list =[]; fit_failed_list=[]

    darkesr('magnet_optimize_init', range_MHz=coarse_range, pts=coarse_pts, reps=coarse_reps, 
                power= coarse_amplitude, MW_power = coarse_MW_power, pulse_length=coarse_pulse_length)

    # Do the fitting, returns in MHz, input in GHz
     
    f0_temp, u_f0_temp = dark_esr_auto_analysis.analyze_dark_esr_double(do_plot=True)
    delta_f0_temp = -f0_temp*1e6+current_f_msm1*1e-3    # in kHz

    # Magnet start position
    Start_position = magnet_Z_scanner.GetPosition()

    # List all the measured values
    iterations = 0
    f0.append(f0_temp)
    u_f0.append(u_f0_temp)
    delta_f0.append(delta_f0_temp)
    magnet_postion_list.append(Start_position)


    while abs(delta_f0_temp) > optimization_target:

            ## Determine new postition
            current_position = magnet_Z_scanner.GetPosition()
            delta_position = delta_f0_temp/field_gradient*1e-6
            move_to_position = current_position + delta_position

            print 'Target frequency =' + str(current_f_msm1)
            print 'Measured frequency = ' + str(f0_temp) + ' GHz +/- ' + str(u_f0_temp*1e6) + ' kHz'
            print 'Difference = ' + str(delta_f0_temp) + ' kHz'
            print 'Current magnet position = ' + str(current_position) + ' mm'
            print 'Move to position          ' + str(move_to_position) + ' mm'
            print 'By                        ' + str(delta_position*1e6) + 'nm'
            

            # if u_f0_temp*1e6 > 15:
            #     print 'Uncertainty larger than 15 kHz, fit failed'
            #     fit_failed = 1
            # else: 
            #     fit_failed = 0

            # fit_failed_list.append(fit_failed)
            
            ## Actually move the magnet
          

            if u_f0_temp*1e6 < 15:
       
                ## Limit the maximum movement range
                if move_to_position < 0.042 or move_to_position > 0.072:
                    print 'movement is going out of range, abort!!!'
                    break

                print 'Target frequency =' + str(current_f_msm1)
                print 'Measured frequency = ' + str(f0_temp) + ' GHz +/- ' + str(u_f0_temp*1e6) + ' kHz'
                print 'Difference = ' + str(delta_f0_temp) + ' kHz'
                print 'Current magnet position = ' + str(current_position) + ' mm'
                print 'Move to position          ' + str(move_to_position) + ' mm'
                print 'By                        ' + str((move_to_position-current_position)*1e6) + 'nm'

                if safemode == True: 
                    print '\a\a\a' 
                    ri = raw_input ('move magnet? (y/n)')
                    if str(ri) != 'y': 
                        break
                
                ## Actually move the magnet
                magnet_Z_scanner.MoveRelative(delta_position)
                print 'moving magnet...'

            else:
                print 'Uncertainty larger than 15 kHz, fit failed'
                break

            print '--------------------------------'
            print 'press q to stop measurement loop'
            print '--------------------------------'
            qt.msleep(2)

            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')) or abs(move_to_position-current_position) < 0.000025:
                break

            darkesr('magnet_optimize_step_' + str(iterations), range_MHz=fine_range, pts=fine_pts, reps=fine_reps, 
                power = fine_amplitude, MW_power = fine_MW_power, pulse_length=fine_pulse_length)

            f0_temp, u_f0_temp = dark_esr_auto_analysis.analyze_dark_esr_double(do_plot=True)
            delta_f0_temp = -f0_temp*1e6+current_f_msm1*1e-3

            iterations += 1


# for ssro measurement
def ssrocalibration(name,RO_power=None,SSRO_duration=None):
    m = ssro.AdwinSSRO('SSROCalibration_'+name)
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])

    if RO_power != None:
        m.params['Ex_RO_amplitude'] = RO_power
    if SSRO_duration != None:
        m.params['SSRO_duration'] = SSRO_duration

    # ms = 0 calibration
    m.params['Ex_SP_amplitude'] = 0
    m.run()
    m.save('ms0')

    # ms = 1 calibration
    m.params['SP_duration']     = 500
    m.params['A_SP_amplitude']  = 0.
    m.params['Ex_SP_amplitude'] = 5e-9
    m.run()
    m.save('ms1')
    m.finish()







if __name__ == '__main__':
    # electronT1hermite(SAMPLE_CFG, T1_initial_state = 'ms=0', T1_readout_state = 'ms=0', start_time = 0, end_time = 1.5e6, pts = 4)
    # qt.instruments['optimiz0r'].optimize(dims=['x','y','z','y','x'], cnt=1, int_time=50, cycles=3)
    #electronT1hermite(SAMPLE_CFG, T1_initial_state = 'ms=0', T1_readout_state = 'ms=0', start_time = 0.0e6, end_time = 5e6, pts = 7)
    #electronT1hermite(SAMPLE_CFG+'0to0', T1_initial_state = 'ms=0', T1_readout_state = 'ms=0', start_time = 0e6, end_time = 200e3, pts =9)
    #electronT1hermite(SAMPLE_CFG+'0top1', T1_initial_state = 'ms=0', T1_readout_state = 'ms=1', start_time = 1e3, end_time = 800e3, pts = 8)
    #electronT1hermite(SAMPLE_CFG+'m0to0'+'time_10_to_200', T1_initial_state = 'ms=0', T1_readout_state = 'ms=0', start_time = 10e3, end_time = 200e3, pts = 5,debug=False,repetitions=360)
    #electronT1hermite(SAMPLE_CFG+'m1top1', T1_initial_state = 'ms=-1', T1_readout_state = 'ms=1', start_time = 1e3, end_time = 20e3, pts = 8)

   

   #  name = 'SSRO_calib'
   #  ssrocalibration(name)
   #  ssro_analysis.ssrocalib()
   #  optimize_magnetic_field()  

   #  # #############################################################
   #  # electronT1hermite(SAMPLE_CFG+'m-1to-1'+'fake', T1_initial_state = 'ms=-1', T1_readout_state = 'ms=-1', start_time = 10e3, end_time = 200e3, pts = 2,wait_times=[10e3,20e3],debug=False,repetitions=10)
   #  # electronT1hermite(SAMPLE_CFG+'m+1to+1'+'_time_600_to_1000ms', T1_initial_state = 'ms=-1', T1_readout_state = 'ms=-1', start_time = 10e3, end_time = 200e3, pts = 5,wait_times=[600e3,700e3,800e3,900e3,1000e3],debug=False,repetitions=300)
    
   #  # ##############################

   #  # name = 'SSRO_calib'
   #  # ssrocalibration(name)
   #  # ssro_analysis.ssrocalib()
   #  # optimize_magnetic_field()

   #  # electronT1hermite(SAMPLE_CFG+'m+1to+1'+'fake', T1_initial_state = 'ms=-1', T1_readout_state = 'ms=-1', start_time = 10e3, end_time = 200e3, pts = 2,wait_times=[15e3,30e3],debug=False,repetitions=50)
   #  electronT1hermite(SAMPLE_CFG+'m+1to+1'+'_time_20s_part', T1_initial_state = 'ms=-1', T1_readout_state = 'ms=-1', start_time = 10e3, end_time = 200e3, pts = 3,wait_times=[10e3,20e3,20e6],debug=False,repetitions=180)
    
   #  name = 'SSRO_calib'
   #  ssrocalibration(name)
   #  ssro_analysis.ssrocalib()
   #  optimize_magnetic_field()

   #  # electronT1hermite(SAMPLE_CFG+'m-1to-1'+'fake', T1_initial_state = 'ms=-1', T1_readout_state = 'ms=-1', start_time = 10e3, end_time = 200e3, pts = 2,wait_times=[10e3,20e3],debug=False,repetitions=10)
   #  electronT1hermite(SAMPLE_CFG+'m+1to+1'+'_time_40s_part1', T1_initial_state = 'ms=-1', T1_readout_state = 'ms=-1', start_time = 10e3, end_time = 200e3, pts = 3,wait_times=[10e3,20e3,40000e3],debug=False,repetitions=90)
    

   #  name = 'SSRO_calib'
   #  ssrocalibration(name)
   #  ssro_analysis.ssrocalib()
   #  optimize_magnetic_field()

   #  # electronT1hermite(SAMPLE_CFG+'m-1to-1'+'fake', T1_initial_state = 'ms=-1', T1_readout_state = 'ms=-1', start_time = 10e3, end_time = 200e3, pts = 2,wait_times=[10e3,20e3],debug=False,repetitions=10)
   #  electronT1hermite(SAMPLE_CFG+'m+1to+1'+'_time_40s_part2', T1_initial_state = 'ms=-1', T1_readout_state = 'ms=-1', start_time = 10e3, end_time = 200e3, pts = 3,wait_times=[10e3,20e3,40000e3],debug=False,repetitions=90)
    

   #  name = 'SSRO_calib'
   #  ssrocalibration(name)
   #  ssro_analysis.ssrocalib()
   #  optimize_magnetic_field()

   #  # electronT1hermite(SAMPLE_CFG+'m-1to-1'+'fake', T1_initial_state = 'ms=-1', T1_readout_state = 'ms=-1', start_time = 10e3, end_time = 200e3, pts = 2,wait_times=[10e3,20e3],debug=False,repetitions=10)
   #  electronT1hermite(SAMPLE_CFG+'m+1to+1'+'_time_60s_part1', T1_initial_state = 'ms=-1', T1_readout_state = 'ms=-1', start_time = 10e3, end_time = 200e3, pts = 3,wait_times=[10e3,20e3,60000e3],debug=False,repetitions=60)
    

   #  name = 'SSRO_calib'
   #  ssrocalibration(name)
   #  ssro_analysis.ssrocalib()
   #  optimize_magnetic_field()

   #  # electronT1hermite(SAMPLE_CFG+'m-1to-1'+'fake', T1_initial_state = 'ms=-1', T1_readout_state = 'ms=-1', start_time = 10e3, end_time = 200e3, pts = 2,wait_times=[10e3,20e3],debug=False,repetitions=10)
   #  electronT1hermite(SAMPLE_CFG+'m+1to+1'+'_time_60s_part2', T1_initial_state = 'ms=-1', T1_readout_state = 'ms=-1', start_time = 10e3, end_time = 200e3, pts = 3,wait_times=[10e3,20e3,60000e3],debug=False,repetitions=60)
    
   #  name = 'SSRO_calib'
   #  ssrocalibration(name)
   #  ssro_analysis.ssrocalib()
   #  optimize_magnetic_field()

   #electronT1hermite(SAMPLE_CFG+'m-1to-1'+'fake', T1_initial_state = 'ms=-1', T1_readout_state = 'ms=-1', start_time = 10e3, end_time = 200e3, pts = 2,wait_times=[10e3,20e3],debug=False,repetitions=10)
   #  electronT1hermite(SAMPLE_CFG+'m+1to+1'+'_time_60s_part3', T1_initial_state = 'ms=-1', T1_readout_state = 'ms=-1', start_time = 10e3, end_time = 200e3, pts = 3,wait_times=[10e3,20e3,60000e3],debug=False,repetitions=60)


   #  #####################################
   # #  electronT1hermite(SAMPLE_CFG+'m-1to-1'+'time_250_to_500', T1_initial_state = 'ms=-1', T1_readout_state = 'ms=-1', start_time = 250e3, end_time = 500e3, pts = 6,debug=False,repetitions=600)
   # # #########################################

   #  name = 'SSRO_calib'
   #  ssrocalibration(name)
   #  ssro_analysis.ssrocalib()
   #  optimize_magnetic_field()

   #  #####################################
   #  electronT1hermite(SAMPLE_CFG+'m-1to-1'+'time_600_to_1000', T1_initial_state = 'ms=-1', T1_readout_state = 'ms=-1', start_time = 600e3, end_time = 1000e3, pts = 5,debug=False,repetitions=600)
    
    # name = 'SSRO_calib'
    # ssrocalibration(name)
   #  optimize_magnetic_field()

    







    # electronT1hermite(SAMPLE_CFG+'m+1to+1'+'time_10_to_200', T1_initial_state = 'ms=-1', T1_readout_state = 'ms=-1', start_time = 10e3, end_time = 200e3, pts = 20,debug=False,repetitions=650)
    #     #### Some examples for stuff to put in long measurements
   

    for i in range(0,2):
        

        ### To be able to stop measurement loops (very handy, otherwise you will be pressing q for a long time) 
        import qt
        import msvcrt

        print '-----------------------------------'
        print 'press q to stop measurement cleanly'
        print '-----------------------------------'
        
        qt.msleep(2)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            break

        

        optimize_magnetic_field()



        electronT1hermite(SAMPLE_CFG+'m0to-1'+'time_10_min'+'part_'+str(i+1), T1_initial_state = 'ms=0', T1_readout_state = 'ms=-1', start_time = 10e3, end_time = 600e6, pts = 3,wait_times=[10e3,20e3,600e6],debug=False,repetitions=5)
        #execfile('D:\measuring\measurement\scripts\QEC\magnet\optimize_magnet_during_experiments.py')


        ### SSRO calibration

        name = 'SSRO_calib'
        ssrocalibration(name)

        ### SSRO Analysis
        ssro_analysis.ssrocalib()




    # for i in range(0,20):
    #     #electronT1hermite(SAMPLE_CFG+'m0to0'+'time_10_to_200', T1_initial_state = 'ms=0', T1_readout_state = 'ms=0', start_time = 10e3, end_time = 200e3, pts = 20,debug=False,repetitions=600)
    #     #### Some examples for stuff to put in long measurements

    #     ### To be able to stop measurement loops (very handy, otherwise you will be pressing q for a long time) 

    #     print '-----------------------------------'
    #     print 'press q to stop measurement cleanly'
    #     print '-----------------------------------'
        
    #     qt.msleep(2)
    #     if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
    #         break



    #     optimize_magnetic_field()
    #     electronT1hermite(SAMPLE_CFG+'fake', T1_initial_state = 'ms=-1', T1_readout_state = 'ms=-1', start_time = 10e3, end_time = 200e3, pts = 2,wait_times=[10e3,20e3],debug=False,repetitions=5)
    #     electronT1hermite(SAMPLE_CFG+'m+1to+1'+'time_10_min'+'part_'+str(i+1), T1_initial_state = 'ms=-1', T1_readout_state = 'ms=-1', start_time = 10e3, end_time = 600e6, pts = 3,wait_times=[10e3,20e3,600e6],debug=False,repetitions=5)




    #     ### SSRO calibration

    #     name = 'SSRO_calib'
    #     ssrocalibration(name)

    #     ssro_analysis.ssrocalib()

    


    