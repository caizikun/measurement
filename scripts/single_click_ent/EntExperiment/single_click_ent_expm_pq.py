import qt
import numpy as np
import time
import measurement.lib.measurement2.measurement as m2
import single_click_ent_expm, sweep_single_click_ent_expm
import measurement.lib.measurement2.pq.pq_measurement as pq
from measurement.lib.cython.PQ_T2_tools import T2_tools_v3
import copy
import msvcrt
reload(T2_tools_v3)
reload(pq)
reload(single_click_ent_expm);reload(sweep_single_click_ent_expm)

name = qt.exp_params['protocols']['current']

class PQSingleClickEntExpm(single_click_ent_expm.SingleClickEntExpm,  pq.PQMeasurement ): # pq.PQ_Threaded_Measurement ): #
    mprefix = 'PQ_single_click_ent'
    adwin_process = 'single_click_ent'
    
    def __init__(self, name,hist_only = False):
        single_click_ent_expm.SingleClickEntExpm.__init__(self, name)
        self.params['measurement_type'] = self.mprefix
        self.joint_params = m2.MeasurementParameters('JointParameters')
        self.params = m2.MeasurementParameters('LocalParameters')
        self.params['pts']=1
        self.params['repetitions']=1
        self.params['TH_hist_only'] = hist_only

    def autoconfig(self):
        single_click_ent_expm.SingleClickEntExpm.autoconfig(self)
        pq.PQMeasurement.autoconfig(self)

    def setup(self, **kw):
        if not self.params['only_meas_phase']:
            single_click_ent_expm.SingleClickEntExpm.setup(self,**kw)
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
         
    def finish(self):
        h5_joint_params_group = self.h5basegroup.create_group('joint_params')
        joint_params = self.joint_params.to_dict()
        for k in joint_params:
            h5_joint_params_group.attrs[k] = joint_params[k]
        self.h5data.flush()

        self.AWG_RO_AOM.turn_off()
        self.E_aom.turn_off()
        self.A_aom.turn_off()
        self.repump_aom.turn_off()


        pq.PQMeasurement.finish(self)
        
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
            if qt.current_setup == 'lt3':

                tail_psb_lt3 = round(float(tail_cts_ch0*1e4)/float(self.last_sync_number-self.last_sync_number_update),3)
                tail_psb_lt4 = round(float(tail_cts_ch1*1e4)/float(self.last_sync_number-self.last_sync_number_update),3)
                self.physical_adwin.Set_FPar(56, tail_psb_lt3)
                self.physical_adwin.Set_FPar(57, tail_psb_lt4)
                 
                # print 'tail_counts PSB (lt3/lt4)', tail_psb_lt3,tail_psb_lt4
            else:
                ZPL_tail = round(float( (tail_cts_ch0+ tail_cts_ch1)*1e4)/float(self.last_sync_number-self.last_sync_number_update),3)
                Pulse_counts = round(float((pulse_cts_ch1 + pulse_cts_ch0)*1e4)/float(self.last_sync_number-self.last_sync_number_update),3)
                self.physical_adwin.Set_FPar(56, ZPL_tail)
                self.physical_adwin.Set_FPar(57, Pulse_counts)


def load_TH_params(m):
    pq_measurement.PQMeasurement.PQ_ins=qt.instruments['TH_260N'] ### overwrites the use of the HH_400
    m.params['MAX_DATA_LEN'] =       int(10e6) ## used to be 100e6
    m.params['BINSIZE'] =            1 #2**BINSIZE*BASERESOLUTION 
    m.params['MIN_SYNC_BIN'] =       0
    m.params['MAX_SYNC_BIN'] =       8e3
    m.params['MIN_HIST_SYNC_BIN'] =  1
    m.params['MAX_HIST_SYNC_BIN'] =  8000
    m.params['TTTR_RepetitiveReadouts'] =  10 #
    m.params['TTTR_read_count'] =   1000 #  samples #qt.instruments['TH_260N'].get_T2_READMAX() #(=131072)
    m.params['measurement_abort_check_interval']    = 2. #sec
    m.params['wait_for_late_data'] = 1 #in units of measurement_abort_check_interval
    m.params['use_live_marker_filter']=False



def MW_Position(name,debug = False,upload_only=False):
    """
    Initializes the electron in ms = -1 
    Put a very long repumper. Leave one MW pi pulse to find the microwave position.
    THIS MEASUREMENT RUNS EXCLUSIVELY ON THE TIMEHARP!
    NK 2016
    """

    m = PQSingleClickEntExpm(name)
    sweep_single_click_ent_expm.prepare(m)

    # load_TH_params(m)
    #load_BK_params(m)
    ### general params
    pts = 1
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 2000

    sweep_single_click_ent_expm.turn_all_sequence_elements_off(m)

    ### sequence specific parameters
    
    m.params['MW_before_LDE'] = 1 # allows for init in -1 before LDE
    m.params['input_el_state'] = 'mZ'
    m.params['MW_during_LDE'] = 1

    m.params['PLU_during_LDE'] = 0
    m.joint_params['opt_pi_pulses'] = 1
    m.params['is_two_setup_experiment'] = 2

    m.joint_params['LDE_attempts'] = 250

    m.params['LDE_SP_delay'] = 0e-6

    ### prepare sweep / necessary for the measurement that we under go.
    m.params['do_general_sweep']    = True
    m.params['general_sweep_name'] = 'LDE_SP_duration'
    print 'sweeping the', m.params['general_sweep_name']
    m.params['general_sweep_pts'] = np.array([m.joint_params['LDE_element_length']-200e-9-m.params['LDE_SP_delay']])
    m.params['general_sweep_pts'] = np.array([2e-6])
    m.params['sweep_name'] = m.params['general_sweep_name']
    m.params['sweep_pts'] = m.params['general_sweep_pts']*1e9

    ### upload and run

    sweep_single_click_ent_expm.run_sweep(m,debug = debug,upload_only = upload_only)

def phase_stability(name,debug = False,upload_only=False):

    """
    Just runs a phase stability meausrement
    """
    m = PQSingleClickEntExpm(name)
    sweep_single_click_ent_expm.prepare(m)

    pts = 1
    m.params['reps_per_ROsequence'] = 200
    
    sweep_single_click_ent_expm.turn_all_sequence_elements_off(m)
    ### which parts of the sequence do you want to incorporate.
    m.params['is_two_setup_experiment'] = 0 ## set to 1 in case you want to do optical pi pulses on lt4!
    m.params['do_phase_stabilisation']  = 1
    m.params['only_meas_phase']         = 1 

    sweep_single_click_ent_expm.run_sweep(m,debug = debug,upload_only = upload_only)



def tail_sweep(name,debug = True,upload_only=True, minval = 0.1, maxval = 0.8, local = False):
    """
    Performs a tail_sweep in the LDE_1 element
    """
    m = PQSingleClickEntExpm(name)
    sweep_single_click_ent_expm.prepare(m)

    ### general params
    pts = 15
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 100


    sweep_single_click_ent_expm.turn_all_sequence_elements_off(m)
    ### which parts of the sequence do you want to incorporate.
    ### --> for this measurement: none.
    m.joint_params['LDE_attempts'] = 250

    m.joint_params['opt_pi_pulses'] = 1
    m.params['MW_during_LDE'] = 0
    m.params['PLU_during_LDE'] = 0
    if local:
        m.params['is_two_setup_experiment'] = 0 ## set to 1 in case you want to do optical pi pulses on lt4!
    else:
        m.params['is_two_setup_experiment'] = 1 ## set to 1 in case you want to do optical pi pulses on lt4!



    # put sweep together:
    sweep_off_voltage = False
    m.params['do_yellow_with_AWG'] = 0
    m.params['do_general_sweep']    = True

    if sweep_off_voltage:
        m.params['general_sweep_name'] = 'eom_off_amplitude'
        print 'sweeping the', m.params['general_sweep_name']
        m.params['general_sweep_pts'] = np.linspace(-0.1,0.06,pts)#(-0.04,-0.02,pts)
    else:
        m.params['general_sweep_name'] = 'aom_amplitude'
        print 'sweeping the', m.params['general_sweep_name']
        m.params['general_sweep_pts'] = np.linspace(minval,maxval,pts)


    m.params['sweep_name'] = m.params['general_sweep_name'] 
    m.params['sweep_pts'] = m.params['general_sweep_pts']
    ### upload

    sweep_single_click_ent_expm.run_sweep(m,debug = debug,upload_only = upload_only)

def optical_rabi(name,debug = True,upload_only=True, local = False):
    """
    Very similar to tail sweep.



    ...

    Also, best doc string ever.
    """
    m = PQSingleClickEntExpm(name)
    sweep_single_click_ent_expm.prepare(m)

    ### general params
    pts = 1
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 10000


    sweep_single_click_ent_expm.turn_all_sequence_elements_off(m)
    ### which parts of the sequence do you want to incorporate.
    ### --> for this measurement: none.

    m.joint_params['opt_pi_pulses'] = 1
    m.params['MW_during_LDE'] = 0
    m.params['PLU_during_LDE'] = 0
    if local:
        m.params['is_two_setup_experiment'] = 0 ## set to 1 in case you want to do optical pi pulses on lt4!
    else:
        m.params['is_two_setup_experiment'] = 1 ## set to 1 in case you want to do optical pi pulses on lt4!


    # put sweep together:

    m.params['do_general_sweep']    = True
    m.params['general_sweep_name'] = 'eom_pulse_duration'
    print 'sweeping the', m.params['general_sweep_name']
    m.params['general_sweep_pts'] = np.linspace(39e-9,40e-9,pts)



    m.params['sweep_name'] = m.params['general_sweep_name'] 
    m.params['sweep_pts'] = m.params['general_sweep_pts']
    ### upload

    sweep_single_click_ent_expm.run_sweep(m,debug = debug,upload_only = upload_only)

def SPCorrs_PSB_singleSetup(name, debug = False, upload_only = False):
    """
    Performs a Spin-photon correlation measurement in the PSB (therefore post selected).
    """
    ### general params
    m = PQSingleClickEntExpm(name)
    sweep_single_click_ent_expm.prepare(m)
    load_TH_params(m) # has to be after prepare(m)

    ### general params
    m.params['reps_per_ROsequence'] = 50000

    sweep_single_click_ent_expm.turn_all_sequence_elements_off(m)
    ### which parts of the sequence do you want to incorporate.

    m.params['do_general_sweep']    = True
    m.params['general_sweep_name'] = 'MW_pi_during_LDE' 
    m.params['general_sweep_pts'] = np.array([0,1]) ## turn pi pulse on or off for spcorrs
    m.params['sweep_name'] = m.params['general_sweep_name'] 
    m.params['sweep_pts'] = m.params['general_sweep_pts']
    m.params['pts'] = len(m.params['sweep_pts'])

    m.joint_params['do_final_mw_LDE'] = 0

    m.joint_params['opt_pi_pulses'] = 1
    m.joint_params['LDE_attempts'] = 250
    if True:
        m.params['mw_first_pulse_amp'] = m.params['Hermite_pi2_amp']
        m.params['mw_first_pulse_length'] = m.params['Hermite_pi2_length']

    m.params['is_two_setup_experiment'] = 0

    ### upload

    sweep_single_click_ent_expm.run_sweep(m, debug = debug, upload_only = upload_only)


def SPCorrs_ZPL_twoSetup(name, debug = False, upload_only = False):
    """
    Performs a Spin-photon correlation measurement including the PLU.
    """
    m = PQSingleClickEntExpm(name)
    sweep_single_click_ent_expm.prepare(m)

    ### general params
    m.params['reps_per_ROsequence'] = 2000

    sweep_single_click_ent_expm.turn_all_sequence_elements_off(m)
    ### which parts of the sequence do you want to incorporate.

    m.params['do_general_sweep']    = True
    m.params['general_sweep_name'] = 'MW_pi_during_LDE' 
    m.params['general_sweep_pts'] = np.array([0,1]) ## turn pi pulse on or off for spcorrs
    m.params['sweep_name'] = m.params['general_sweep_name'] 
    m.params['sweep_pts'] = m.params['general_sweep_pts']
    m.params['pts'] = len(m.params['sweep_pts'])
    m.params['do_phase_stabilisation'] = 1

    m.params['is_two_setup_experiment'] = 1
    m.params['PLU_during_LDE'] = 1
    m.joint_params['do_final_mw_LDE'] = 0

    m.joint_params['opt_pi_pulses'] = 1
    m.joint_params['LDE_attempts'] = 250

    ### upload

    sweep_single_click_ent_expm.run_sweep(m, debug = debug, upload_only = upload_only)

def Determine_eta(name, debug = False, upload_only = False):
    """
    Performs a Spin-photon correlation measurement including the PLU.
    This msmt is effectively the same as a SPCorr msmt in the ZPL. 
    Actual work is done by the analysis script.
    """

    m = PQSingleClickEntExpm(name)
    sweep_single_click_ent_expm.prepare(m)

    ### general params
    m.params['reps_per_ROsequence'] = 2000

    sweep_single_click_ent_expm.turn_all_sequence_elements_off(m)
    ### which parts of the sequence do you want to incorporate.

    m.params['do_general_sweep']    = True
    m.params['general_sweep_name'] = 'MW_pi_during_LDE' 
    m.params['general_sweep_pts'] = np.array([0,1]) ## turn pi pulse on or off for spcorrs
    m.params['sweep_name'] = m.params['general_sweep_name'] 
    m.params['sweep_pts'] = m.params['general_sweep_pts']
    m.params['pts'] = len(m.params['sweep_pts'])
    m.params['do_phase_stabilisation'] = 1

    m.params['is_two_setup_experiment'] = 1
    m.params['PLU_during_LDE'] = 1
    m.joint_params['do_final_mw_LDE'] = 0

    m.joint_params['opt_pi_pulses'] = 1
    m.joint_params['LDE_attempts'] = 250

    ### upload & run

    sweep_single_click_ent_expm.run_sweep(m, debug = debug, upload_only = upload_only)
def TPQI(name,debug = False,upload_only=False):
    
    m = PQSingleClickEntExpm(name)
    sweep_single_click_ent_expm.prepare(m)

    pts = 1
    m.params['reps_per_ROsequence'] = 50000
    sweep_single_click_ent_expm.turn_all_sequence_elements_off(m)


    m.params['MIN_SYNC_BIN'] =       1.5e6
    m.params['MAX_SYNC_BIN'] =       9e6
    m.params['is_TPQI'] = 1
    m.params['is_two_setup_experiment'] = 1
    m.params['do_general_sweep'] = 0
    m.params['MW_during_LDE'] = 0


    m.joint_params['LDE_element_length'] = 10e-6
    m.joint_params['opt_pi_pulses'] = 5
    m.joint_params['opt_pulse_separation'] = 1400e-9
    m.joint_params['LDE_attempts'] = 100


    #####################################################
    #   These parameters have not beeen reviewed!!      #
    #####################################################

    m.params['pulse_start_bin'] = 2625e3- m.params['MIN_SYNC_BIN']  
    m.params['pulse_stop_bin'] = 2635e3 - m.params['MIN_SYNC_BIN'] 
    m.params['tail_start_bin'] = 2635e3 - m.params['MIN_SYNC_BIN']  
    m.params['tail_stop_bin'] = 2700e3  - m.params['MIN_SYNC_BIN'] 

    if qt.current_setup == 'lt3':
        m.params['pulse_start_bin'] = 2625e3- m.params['MIN_SYNC_BIN']  
        m.params['pulse_stop_bin'] = 2635e3 - m.params['MIN_SYNC_BIN'] 
        m.params['tail_start_bin'] = 2100e3 - m.params['MIN_SYNC_BIN']  
        m.params['tail_stop_bin'] = 2800e3  - m.params['MIN_SYNC_BIN'] 
        m.params['MIN_SYNC_BIN'] =       1.5e3
        m.params['MAX_SYNC_BIN'] =       9e3
        m.params['pulse_start_bin'] = m.params['pulse_start_bin']/1e3
        m.params['pulse_stop_bin'] = m.params['pulse_stop_bin']/1e3
        m.params['tail_start_bin'] = m.params['tail_start_bin']/1e3
        m.params['tail_stop_bin'] = m.params['tail_stop_bin']/1e3

    ### upload and run
    sweep_single_click_ent_expm.run_sweep(m,debug = debug,upload_only = upload_only)





def EntangleXY(name,debug = False,upload_only=False):
    """
    Sweeps the phase of the last pi/2 pulse on one of the two setups to measure the 
    stabilized phase of the entangled state.
    """
    m = PQSingleClickEntExpm(name)
    sweep_single_click_ent_expm.prepare(m)
   
    sweep_single_click_ent_expm.turn_all_sequence_elements_off(m)

    m.params['do_phase_stabilisation'] = 1

    m.params['reps_per_ROsequence'] = 300
    m.params['MW_during_LDE'] = 1
    m.joint_params['do_final_mw_LDE'] = 1
    m.params['is_two_setup_experiment'] = 1
    m.params['PLU_during_LDE'] = 1
    m.joint_params['LDE_attempts'] = 250

    if qt.current_setup == 'lt4':
        m.params['do_general_sweep'] = 0
    else:
        m.params['do_general_sweep']    = 1
        m.params['general_sweep_name'] = 'LDE_final_mw_phase' 
        m.params['general_sweep_pts'] = np.linspace(0,180,10) ## turn pi pulse on or off for spcorrs
        m.params['sweep_name'] = m.params['general_sweep_name'] 
        m.params['sweep_pts'] = m.params['general_sweep_pts']
        m.params['pts'] = len(m.params['sweep_pts'])
    ### upload and run


    sweep_single_click_ent_expm.run_sweep(m,debug = debug,upload_only = upload_only)


if __name__ == '__main__':


    ########### local measurements
    # phase_stability(name+'_phase_stab',upload_only=False)

    # MW_Position(name+'_MW_position',upload_only=False)

    tail_sweep(name+'_tail',debug = False,upload_only=False, minval = 0.0, maxval=1.0, local=False)
    # optical_rabi(name+'_optical_rabi_22_deg',debug = False,upload_only=False, local=False)
    # SPCorrsPuri_PSB_singleSetup(name+'_SPCorrs_PSB',debug = False,upload_only=False)
    


    ###### non-local measurements
  
    # qt.instruments['ZPLServo'].move_in()
    # SPCorrs_ZPL_twoSetup(name+'_SPCorrs_ZPL_LT3',debug = False,upload_only=True)
    # qt.instruments['ZPLServo'].move_out()
    # SPCorrs_ZPL_twoSetup(name+'_SPCorrs_ZPL_LT4',debug = False,upload_only=False)
  
    
    # Determine_eta(name+'_eta_XX_35percent',debug = False,upload_only=False) ### this just a spcorr msmt on both setups

    # TPQI(name+'_TPQI',debug = False,upload_only=True)

    # EntangleXY(name+'_Entangle_XX',debug = False,upload_only=True)

    if hasattr(qt,'master_script_is_running'):
        if qt.master_script_is_running:
            # Experimental addition for remote running
            if (qt.current_setup == 'lt4'): ## i moved this here (from the run function of the class purify), otherwise the loop would crash. NK
                qt.instruments['lt3_helper'].set_is_running(False)
                qt.msleep(1.5)
                qt.instruments['lt3_helper'].set_measurement_name(str(qt.purification_name_index))
                qt.instruments['lt3_helper'].set_script_path(r'D:/measuring/measurement/scripts/Purification/purify.py')
                qt.msleep(1.5)
                qt.instruments['lt3_helper'].execute_script()
                qt.msleep(1.5)
                qt.instruments['lt4_helper'].set_is_running(True)
                qt.instruments['lt3_helper'].set_is_running(True)
                
            else:
                ### synchronize the measurement name index.
                qt.purification_name_index = int(qt.instruments['remote_measurement_helper'].get_measurement_name())

            AWG.clear_visa
            qt.msleep(2)
            qt.instruments['purification_optimizer'].start_babysit()
            
            for i in range(1):

                print '-----------------------------------'            
                print 'press q to stop measurement cleanly'
                print '-----------------------------------'
                qt.msleep(1)
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                    qt.purification_succes = False
                    break

                PurifyYY(name+'_SingleClickEnt_XX'+str(qt.purification_name_index+i),debug = False, upload_only = False)
                AWG.clear_visa()
            
            qt.instruments['purification_optimizer'].set_stop_optimize(True)
            qt.instruments['purification_optimizer'].stop_babysit()
            qt.master_script_is_running = False
            qt.purification_succes = True
            
