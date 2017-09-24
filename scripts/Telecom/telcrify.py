import qt
import numpy as np
import time
import measurement.lib.measurement2.measurement as m2
import telcrify_slave, sweep_telcrification
import measurement.lib.measurement2.pq.pq_measurement as pq
from measurement.lib.cython.PQ_T2_tools import T2_tools_v3
import copy
import msvcrt
reload(T2_tools_v3)
reload(pq)
reload(telcrify_slave);reload(sweep_telcrification)

name = qt.exp_params['protocols']['current']

class telcrify(telcrify_slave.purify_single_setup,  pq.PQMeasurement ): # pq.PQ_Threaded_Measurement ): #
    mprefix = 'Telcrification'
    adwin_process = 'telcrification'
    
    def __init__(self, name,hist_only = False):
        telcrify_slave.purify_single_setup.__init__(self, name)
        self.params['measurement_type'] = self.mprefix
        self.params = m2.MeasurementParameters('LocalParameters')
        self.params['pts']=1
        self.params['repetitions']=1
        self.params['TH_hist_only'] = hist_only
    def autoconfig(self):
        telcrify_slave.purify_single_setup.autoconfig(self)
        pq.PQMeasurement.autoconfig(self)

    def setup(self, **kw):
        telcrify_slave.purify_single_setup.setup(self,**kw)
        pq.PQMeasurement.setup(self,**kw)

    def start_measurement_process(self):
        qt.msleep(.5)
        self.start_adwin_process(load=False)
        qt.msleep(.5)

    def measurement_process_running(self):
        return self.adwin_process_running()

    def run(self, **kw):
        pq.PQMeasurement.run(self,**kw)
        
    def print_measurement_progress(self):
        reps_completed = self.adwin_var('completed_reps')    
        print('completed %s / %s readout repetitions' % \
                (reps_completed, self.params['repetitions']))

    def stop_measurement_process(self):
        self.stop_adwin_process()
        reps_completed = self.adwin_var('completed_reps')
        print('Total completed %s / %s readout repetitions' % \
                (reps_completed, self.params['repetitions']))

    def save(self, name = 'adwindata'):
        reps = self.adwin_var('completed_reps')
        # sweeps = self.params['pts'] * self.params['reps_per_ROsequence']


        self.save_adwin_data(name,
                [   ('CR_before',1, reps),
                    ('CR_after',1, reps),
                    ('statistics', 10),  
                    ('invalid_data_markers'                  ,1,reps),
                    ('counted_awg_reps'                      ,1,reps),    
                    ('attempts_first'                        ,1,reps),   
                    ('ssro_results'                          ,1,reps), 
                    'completed_reps'
                    ])
        return
    def finish(self):
        
        self.h5data.flush()

        self.AWG_RO_AOM.turn_off()
        self.E_aom.turn_off()
        self.A_aom.turn_off()
        self.repump_aom.turn_off()

        telcrify_slave.purify_single_setup.finish(self)

    def live_update_callback(self):
        ''' This is called when the measurement progress is printed in the PQMeasurement run function'''

        if self.measurement_progress_first_run:
        
            self.no_of_cycles_for_live_update_reset = 100
            self.hist_update = np.zeros((self.hist_length,2), dtype='u4')
            self.last_sync_number_update = 0
            self.measurement_progress_first_run = False
            self.live_updates = 0

        self.live_updates += 1

        if self.live_updates > self.no_of_cycles_for_live_update_reset:
            self.hist_update = copy.deepcopy(self.hist)
            self.last_sync_number_update = self.last_sync_number

        pulse_cts_ch0=np.sum((self.hist - self.hist_update)[self.params['pulse_start_bin']:self.params['pulse_stop_bin'],0])
        pulse_cts_ch1=np.sum((self.hist - self.hist_update)[self.params['pulse_start_bin']+self.params['PQ_ch1_delay'] : self.params['pulse_stop_bin']+self.params['PQ_ch1_delay'],1])
        tail_cts_ch0=np.sum((self.hist - self.hist_update)[self.params['tail_start_bin']  : self.params['tail_stop_bin'],0])
        tail_cts_ch1=np.sum((self.hist - self.hist_update)[self.params['tail_start_bin']+self.params['PQ_ch1_delay'] : self.params['tail_stop_bin']+self.params['PQ_ch1_delay'],1])
        print 'duty_cycle', self.physical_adwin.Get_FPar(58)


        #### update parameters in the adwin
        if (self.last_sync_number > 0) and (self.last_sync_number != self.last_sync_number_update): 
            
                tail_psb_lt3 = round(float(tail_cts_ch0*1e4)/float(self.last_sync_number-self.last_sync_number_update),3)
                tail_psb_lt4 = round(float(tail_cts_ch1*1e4)/float(self.last_sync_number-self.last_sync_number_update),3)
                self.physical_adwin.Set_FPar(56, tail_psb_lt3)
                self.physical_adwin.Set_FPar(57, tail_psb_lt4)
            
    



def tail_sweep(name,debug = True,upload_only=True, minval = 0.1, maxval = 0.8, local = True, TH = True):
    """
    Performs a tail_sweep in the LDE_1 element
    """
    m = telcrify(name)
    sweep_telcrification.prepare(m)

    if TH:
        old_pq_ins = pq_measurement.PQMeasurement.PQ_ins
        pq_measurement.PQMeasurement.PQ_ins=qt.instruments['TH_260N']
        load_TH_params(m)
        
    ### general params
    pts = 8
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000

    #m.params['maximum_meas_time_in_min'] = 2


    sweep_telcrification.turn_all_sequence_elements_off(m)
    ### which parts of the sequence do you want to incorporate.
    ### --> for this measurement: none.
    m.params['LDE1_attempts'] = 250

    m.params['opt_pi_pulses'] = 1
    m.params['opt_pulse_separation'] = 197e-9
    m.params['MW_during_LDE'] = 0
    m.params['PLU_during_LDE'] = 0
    if local:
        m.params['is_two_setup_experiment'] = 0 ## set to 1 in case you want to do optical pi pulses on lt4!
    else:
        m.params['is_two_setup_experiment'] = 1 ## set to 1 in case you want to do optical pi pulses on lt4!
    
    # put sweep together:
    sweep_off_voltage = False
    sweep_on_voltage = False

    m.params['do_general_sweep']    = True

    if sweep_off_voltage:
        m.params['general_sweep_name'] = 'eom_off_amplitude'
        print 'sweeping the', m.params['general_sweep_name']
        m.params['general_sweep_pts'] = np.linspace(0.5,0.8,pts)#(-0.04,-0.02,pts)
    elif sweep_on_voltage:
        m.params['general_sweep_name'] = 'eom_pulse_amplitude'
        print 'sweeping the', m.params['general_sweep_name']
        m.params['general_sweep_pts'] = np.linspace(-2.0,2.0,pts)#(-0.04,-0.02,pts)
    
    else:
        m.params['general_sweep_name'] = 'aom_amplitude'
        print 'sweeping the', m.params['general_sweep_name']
        m.params['general_sweep_pts'] = np.linspace(minval,maxval,pts)


    m.params['sweep_name'] = m.params['general_sweep_name'] 
    m.params['sweep_pts'] = m.params['general_sweep_pts']
    ### upload

    sweep_telcrification.run_sweep(m,debug = debug,upload_only = upload_only)

    if TH:
        pq_measurement.PQMeasurement.PQ_ins= old_pq_ins



def load_BK_params(m):
    m.params['opt_pi_pulses'] = 2
    m.params['LDE_decouple_time'] = 0.50e-6
    m.params['opt_pulse_separation'] = 0.50e-6 
    m.params['LDE_element_length'] = 6e-6
    m.params['do_final_mw_LDE'] = 1
    m.params['PLU_during_LDE'] = 1
    m.params['LDE_SP_duration'] = 1.5e-6


def load_TH_params(m):

    m.params['MAX_DATA_LEN'] =       int(10e6) ## used to be 100e6
    m.params['BINSIZE'] =            1 #2**BINSIZE*BASERESOLUTION 
    m.params['MIN_SYNC_BIN'] =       0#2500
    m.params['MAX_SYNC_BIN'] =       8500
    m.params['MIN_HIST_SYNC_BIN'] =  0#2500
    m.params['MAX_HIST_SYNC_BIN'] =  8500
    m.params['TTTR_RepetitiveReadouts'] =  10 #
    m.params['TTTR_read_count'] =     1000 #  samples #qt.instruments['TH_260N'].get_T2_READMAX() #(=131072)
    m.params['count_marker_channel'] = 4 ##### put plu marker on HH here! needs to be kept!



def SPCorrsPuri_PSB_singleSetup(name, debug = False, upload_only = False):
    """
    Performs a regular Spin-photon correlation measurement.
    """

    m = telcrify(name)
    sweep_telcrification.prepare(m)

    old_pq_ins = pq_measurement.PQMeasurement.PQ_ins
    pq_measurement.PQMeasurement.PQ_ins=qt.instruments['TH_260N']
    load_TH_params(m)

    ### general params
    m.params['pts'] = 1
    m.params['reps_per_ROsequence'] = 50000

    sweep_telcrification.turn_all_sequence_elements_off(m)
    ### which parts of the sequence do you want to incorporate.
    m.params['do_general_sweep']    = False
    m.params['PLU_during_LDE'] = 0

    m.params['opt_pi_pulses'] = 2

    m.params['LDE1_attempts'] = 1

    m.params['mw_first_pulse_amp'] = m.params['Hermite_pi2_amp']
    m.params['mw_first_pulse_length'] = m.params['Hermite_pi2_length']

    m.params['is_two_setup_experiment'] = 0 

    m.params['do_final_mw_LDE'] = 1
    m.params['LDE_final_mw_amplitude'] = 0
    ### upload

    sweep_telcrification.run_sweep(m, debug = debug, upload_only = upload_only)

    pq_measurement.PQMeasurement.PQ_ins= old_pq_ins

def SPCorrsPuri_ZPL_singleSetup(name, debug = False, upload_only = False):
    """
    Performs a regular Spin-photon correlation measurement.
    """

    m = telcrify(name)
    sweep_telcrification.prepare(m)


    ### general params
    m.params['pts'] = 1
    m.params['reps_per_ROsequence'] = 1000

    sweep_telcrification.turn_all_sequence_elements_off(m)
    ### which parts of the sequence do you want to incorporate.
    m.params['do_general_sweep']    = False
    m.params['PLU_during_LDE'] = 1

    m.params['opt_pi_pulses'] = 2

    m.params['LDE1_attempts'] = 350

    m.params['mw_first_pulse_amp'] = m.params['Hermite_pi2_amp']
    m.params['mw_first_pulse_length'] = m.params['Hermite_pi2_length']

    m.params['is_two_setup_experiment'] = 0 

    m.params['do_final_mw_LDE'] = 1
    m.params['LDE_final_mw_amplitude'] = 0
    ### upload

    sweep_telcrification.run_sweep(m, debug = debug, upload_only = upload_only)


# pq_measurement.PQMeasurement.PQ_ins=qt.instruments['HH_400']

def MW_Position(name,debug = False,upload_only=False):
    """
    Initializes the electron in ms = -1 
    Put a very long repumper. Leave one MW pi pulse to find the microwave position.
    THIS MEASUREMENT RUNS EXCLUSIVELY ON THE TIMEHARP!
    NK 2016
    """

    m = telcrify(name)
    sweep_telcrification.prepare(m)

    old_ins = pq_measurement.PQMeasurement.PQ_ins
    pq_measurement.PQMeasurement.PQ_ins=qt.instruments['TH_260N']

    # load_TH_params(m)
    #load_BK_params(m)
    ### general params
    pts = 1
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 5000

    sweep_telcrification.turn_all_sequence_elements_off(m)

    ### sequence specific parameters
    
    m.params['MW_before_LDE1'] = 1 # allows for init in -1 before LDE
    m.params['input_el_state'] = 'mZ'
    m.params['MW_during_LDE'] = 1

    m.params['PLU_during_LDE'] = 0
    m.params['opt_pi_pulses'] = 1
    m.params['is_two_setup_experiment'] = 0
    m.params['do_final_mw_LDE'] = 0
    m.params['LDE1_attempts'] = 250

    m.params['LDE_SP_delay'] = 0e-6

    m.params['MAX_DATA_LEN'] =       int(10e6) ## used to be 100e6
    m.params['BINSIZE'] =            1 #2**BINSIZE*BASERESOLUTION 
    m.params['MIN_SYNC_BIN'] =       0#2500
    m.params['MAX_SYNC_BIN'] =       8500
    m.params['MIN_HIST_SYNC_BIN'] =  0#2500
    m.params['MAX_HIST_SYNC_BIN'] =  8500
    m.params['TTTR_RepetitiveReadouts'] =  10 #
    m.params['TTTR_read_count'] =     1000 #  samples #qt.instruments['TH_260N'].get_T2_READMAX() #(=131072)
    m.params['measurement_abort_check_interval']    = 2. #sec
    m.params['wait_for_late_data'] = 1 #in units of measurement_abort_check_interval
    m.params['use_live_marker_filter']=True
    m.params['count_marker_channel'] = 4 ##### put plu marker on HH here! needs to be kept!
    m.params['pulse_start_bin'] = 2050-m.params['MIN_SYNC_BIN']       #### Puri: 2550 BK: 2950
    m.params['pulse_stop_bin'] = 2050+2000-m.params['MIN_SYNC_BIN']    #### BK: 2950
    m.params['tail_start_bin'] = 2050 -m.params['MIN_SYNC_BIN']       #### BK: 2950
    m.params['tail_stop_bin'] = 2050+2000 -m.params['MIN_SYNC_BIN']    #### BK: 2950

    ### prepare sweep / necessary for the measurement that we under go.
    m.params['do_general_sweep']    = True
    m.params['general_sweep_name'] = 'LDE_SP_duration'
    print 'sweeping the', m.params['general_sweep_name']
    # m.params['general_sweep_pts'] = np.array([m.params['LDE_element_length']-200e-9-m.params['LDE_SP_delay']])
    m.params['general_sweep_pts'] = np.array([2e-6])
    m.params['sweep_name'] = m.params['general_sweep_name']
    m.params['sweep_pts'] = m.params['general_sweep_pts']*1e9

    ### upload and run

    sweep_telcrification.run_sweep(m,debug = debug,upload_only = upload_only)

    pq_measurement.PQMeasurement.PQ_ins = old_ins

def TPQI(name,debug = False,upload_only=False):
    
    m = telcrify(name)
    sweep_telcrification.prepare(m)

    print 'Starting TPQI seq.'

    pts = 1
    m.params['reps_per_ROsequence'] = 100000#20000
    sweep_telcrification.turn_all_sequence_elements_off(m)

    #m.params['maximum_meas_time_in_min'] = 1

    # m.params['MIN_SYNC_BIN'] =      0.0e6 +5e6 # +5 us because of longer spin pumping interval!
    # m.params['MAX_SYNC_BIN'] =       5.5e6 +5e6
    m.params['is_TPQI'] = 1
    m.params['is_two_setup_experiment'] = 0
    m.params['do_general_sweep'] = 0
    m.params['MW_during_LDE'] = 0
    m.params['mw_first_pulse_length'] = 1e-9 
    m.params['mw_second_pulse_length'] = 1e-9

    m.params['LDE_element_length'] = 6e-6
    m.params['opt_pi_pulses'] = 1
    m.params['opt_pulse_separation'] = 500e-9#197e-9 #+ 50e-9 #199e-9 for the red , 190e-9 for telecom
    m.params['LDE1_attempts'] = 200

    m.params['pulse_start_bin'] = 2625e3- m.params['MIN_SYNC_BIN']  
    m.params['pulse_stop_bin'] = 2635e3 - m.params['MIN_SYNC_BIN'] 
    m.params['tail_start_bin'] = 2635e3 - m.params['MIN_SYNC_BIN']  
    m.params['tail_stop_bin'] = 2700e3  - m.params['MIN_SYNC_BIN'] 

    if qt.current_setup == 'lt3':

        m.params['pulse_start_bin'] = 2625e3- m.params['MIN_SYNC_BIN']  
        m.params['pulse_stop_bin'] = 2635e3 - m.params['MIN_SYNC_BIN'] 
        m.params['tail_start_bin'] = 2380e3 - m.params['MIN_SYNC_BIN']  
        m.params['tail_stop_bin'] = 2480e3  - m.params['MIN_SYNC_BIN'] 
        m.params['MIN_SYNC_BIN'] =       5.88e3 #+5e3
        m.params['MAX_SYNC_BIN'] =       5.95e3
        m.params['pulse_start_bin'] = m.params['pulse_start_bin']/1e3
        m.params['pulse_stop_bin'] = m.params['pulse_stop_bin']/1e3
        m.params['tail_start_bin'] = m.params['tail_start_bin']/1e3
        m.params['tail_stop_bin'] = m.params['tail_stop_bin']/1e3

    elif qt.current_setup == 'lt4':

        m.params['pulse_start_bin'] = 2900- m.params['MIN_SYNC_BIN']  
        m.params['pulse_stop_bin'] =  2900+100 - m.params['MIN_SYNC_BIN'] 
        m.params['tail_start_bin'] = 2900 - m.params['MIN_SYNC_BIN']  
        m.params['tail_stop_bin'] = 2900+100  - m.params['MIN_SYNC_BIN'] 
        m.params['MIN_SYNC_BIN'] =       2000 #+5e3
        m.params['MAX_SYNC_BIN'] =       8500
        
    ### upload and run
    sweep_telcrification.run_sweep(m,debug = debug,upload_only = upload_only,hist_only = False)



def measureInterferometerDelay(name,debug = False,upload_only=False):
    
    m = telcrify(name)
    sweep_telcrification.prepare(m)

    print 'Starting TPQI seq.'

    pts = 1
    m.params['reps_per_ROsequence'] = 100000
    sweep_telcrification.turn_all_sequence_elements_off(m)

    #m.params['maximum_meas_time_in_min'] = 1

    # m.params['MIN_SYNC_BIN'] =      0.0e6 +5e6 # +5 us because of longer spin pumping interval!
    # m.params['MAX_SYNC_BIN'] =       5.5e6 +5e6
    m.params['is_TPQI'] = 1
    m.params['is_two_setup_experiment'] = 0
    m.params['do_general_sweep'] = 0
    m.params['MW_during_LDE'] = 0
    m.params['mw_first_pulse_length'] = 1e-9 
    m.params['mw_second_pulse_length'] = 1e-9

    m.params['LDE_element_length'] = 6e-6
    m.params['opt_pi_pulses'] = 1
    m.params['opt_pulse_separation'] = 197e-9 #+ 50e-9 #199e-9 for the red , 190e-9 for telecom
    m.params['LDE1_attempts'] = 1000

    m.params['pulse_start_bin'] = 2625e3- m.params['MIN_SYNC_BIN']  
    m.params['pulse_stop_bin'] = 2635e3 - m.params['MIN_SYNC_BIN'] 
    m.params['tail_start_bin'] = 2635e3 - m.params['MIN_SYNC_BIN']  
    m.params['tail_stop_bin'] = 2700e3  - m.params['MIN_SYNC_BIN'] 

    if qt.current_setup == 'lt3':

        m.params['pulse_start_bin'] = 2625e3- m.params['MIN_SYNC_BIN']  
        m.params['pulse_stop_bin'] = 2635e3 - m.params['MIN_SYNC_BIN'] 
        m.params['tail_start_bin'] = 2380e3 - m.params['MIN_SYNC_BIN']  
        m.params['tail_stop_bin'] = 2480e3  - m.params['MIN_SYNC_BIN'] 
        m.params['MIN_SYNC_BIN'] =       5.88e3 #+5e3
        m.params['MAX_SYNC_BIN'] =       5.95e3
        m.params['pulse_start_bin'] = m.params['pulse_start_bin']/1e3
        m.params['pulse_stop_bin'] = m.params['pulse_stop_bin']/1e3
        m.params['tail_start_bin'] = m.params['tail_start_bin']/1e3
        m.params['tail_stop_bin'] = m.params['tail_stop_bin']/1e3

    elif qt.current_setup == 'lt4':

        m.params['pulse_start_bin'] = 2900- m.params['MIN_SYNC_BIN']  
        m.params['pulse_stop_bin'] =  2900+100 - m.params['MIN_SYNC_BIN'] 
        m.params['tail_start_bin'] = 2900 - m.params['MIN_SYNC_BIN']  
        m.params['tail_stop_bin'] = 2900+100  - m.params['MIN_SYNC_BIN'] 
        m.params['MIN_SYNC_BIN'] =       2000 #+5e3
        m.params['MAX_SYNC_BIN'] =       8500
        
    ### upload and run
    sweep_telcrification.run_sweep(m,debug = debug,upload_only = upload_only,hist_only = False)








if __name__ == '__main__':

    ########### local measurements

    # MW_Position(name+'_MW_position',upload_only=False)

    # tail_sweep(name[:-1]+'tail',debug = False,upload_only=False, minval = 0.1, maxval=0.8, local=True, TH = False)
    # TPQI(name+'_HOM_test_red',debug = True,upload_only=True)
    # optical_rabi(name+'_optical_rabi_22_deg',debug = False,upload_only=False, local=False)
    # SPCorrsPuri_PSB_singleSetup(name+'_SPCorrs_PSB',debug = False,upload_only=False)
    
    SPCorrsPuri_ZPL_singleSetup(name+'_SPCorrs_ZPL',debug = False,upload_only=False)
    # measureInterferometerDelay(name,debug = False,upload_only=False)
    
    # qt.mstart()
    if hasattr(qt,'master_script_is_running'):
        print 'STATUS :',  qt.master_script_is_running
        if qt.master_script_is_running:
            # Experimental addition for remote running
            if (qt.current_setup == 'lt4' or qt.current_setup == 'lt3'): ## i moved this here (from the run function of the class purify), otherwise the loop would crash. NK
                qt.instruments['tel1_helper'].set_is_running(False)
                # qt.msleep(1.5)
                qt.instruments['tel1_helper'].set_measurement_name(str(qt.telcrify_name_index))
                qt.instruments['tel1_helper'].set_script_path(r'D:/measuring/measurement/scripts/tel1_scripts/pq_telecom.py')
                qt.msleep(1.5)
                print qt.instruments['tel1_helper']
                qt.instruments['tel1_helper'].execute_script()
                qt.msleep(1.5)
            #     qt.instruments['lt4_helper'].set_is_running(True)
                qt.instruments['tel1_helper'].set_is_running(True)
                
            else:
                ### synchronize the measurement name index.
                qt.telcrify_name_index = int(qt.instruments['remote_measurement_helper'].get_measurement_name())

            AWG.clear_visa
            qt.msleep(2)
            # qt.instruments['purification_optimizer'].start_babysit()
            # #qt.telcrification_success = True
            
            for i in range(1):

                # print '-----------------------------------'            
                # print 'press q to stop measurement cleanly'
                # print '-----------------------------------'
                # qt.msleep(1)
                # if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                #    break

                # 
                # qt.instruments['ZPLServo'].move_in()
                # SPCorrsPuri_ZPL_twoSetup(name+'_SPCorrs_ZPL_LT3',debug = False,upload_only=False)
                # qt.instruments['ZPLServo'].move_out()
                # SPCorrsPuri_ZPL_twoSetup(name+'_SPCorrs_ZPL_LT4',debug = False,upload_only=False)
                # qt.instruments['ZPLServo'].move_out()


                ## XY measurement
                print '-----------------------------------'            
                print 'press q to stop measurement cleanly'
                print '-----------------------------------'
                qt.msleep(1)
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                    qt.telcrification_success = False
                    break



                TPQI(name+'_TPQI_LT4_PulseOnly_1APDDisc_15optpi_100reps'+str(qt.telcrify_name_index+i),debug = False,upload_only=False)
                AWG.clear_visa()
                ## XZ measurement
                print '-----------------------------------'            
                print 'press q to stop measurement cleanly'
                print '-----------------------------------'
                qt.msleep(1)
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                    qt.telcrification_success = False
                    break

                

            # qt.instruments['purification_optimizer'].set_stop_optimize(True)
            # qt.instruments['purification_optimizer'].stop_babysit()
            qt.master_script_is_running = False
            qt.telcrification_success = True
    # qt.mend()
            
