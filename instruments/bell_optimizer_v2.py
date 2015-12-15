import qt
import os
import traceback
from instrument import Instrument
import numpy as np
from collections import deque
import gobject
import instrument_helper
from lib import config
from analysis.lib.fitting import common,fit
import multiple_optimizer as mo
reload(mo)
import types
import time
import dweepy
import requests.packages.urllib3

class bell_optimizer_v2(mo.multiple_optimizer):
    def __init__(self, name, setup_name='lt4'):
        mo.multiple_optimizer.__init__(self, name)
        
        ins_pars  ={'min_cr_counts'              :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':10},
                    'min_repump_counts'          :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET},
                    'max_counter_optimize'       :   {'type':types.IntType,'flags':Instrument.FLAG_GETSET, 'val':2},
                    'rejecter_step'              :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET}, 
                    'email_recipient'            :   {'type':types.StringType,'flags':Instrument.FLAG_GETSET}, 
                    'max_pulse_counts'           :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':3},
                    'max_SP_ref'                 :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':6},
                    'min_tail_counts'            :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':3.5},
                    'max_strain_splitting'       :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':2.1},
                    'max_cr_counts_avg'          :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':36},
                    }           
        instrument_helper.create_get_set(self,ins_pars)

        self._parlist = ins_pars.keys()
        
        self._parlist.append('read_interval')

        self.add_parameter('pidgate_running',
                           type=types.BooleanType,
                           flags=Instrument.FLAG_GETSET)
        self.add_parameter('pid_e_primer_running',
                           type=types.BooleanType,
                           flags=Instrument.FLAG_GETSET)
        self.add_parameter('pidyellowfrq_running',
                           type=types.BooleanType,
                           flags=Instrument.FLAG_GETSET)
        self.add_parameter('invalid_data_marker',
                          type=types.IntType,
                          flags=Instrument.FLAG_GETSET)
        
        self.add_function('optimize_nf')     
        self.add_function('optimize_gate')
        self.add_function('optimize_yellow') 
        self.add_function('rejecter_half_plus')
        self.add_function('rejecter_half_min')
        self.add_function('zoptimize_rejection')
        self.add_function('rejecter_quarter_plus')
        self.add_function('rejecter_quarter_min')
        self.add_function('check_laser_lock')

        self.setup_name = setup_name
        if 'lt3' in setup_name:
            requests.packages.urllib3.disable_warnings() #XXXXXXXXXXX FIX by updating packages in Canopy package manager?
            self._pharp=qt.instruments['PH_300']


        self._taper_index = 4 if 'lt3' in setup_name else 3

        self.max_cryo_half_rot_degrees  = 3
        self.max_laser_reject_cycles = 25
        self.nb_min_between_nf_optim = 7
        
        self.history_length = 10
        self.avg_length = 9
        self.deque_par_counts   = deque([], self.history_length)
        self.deque_par_laser    = deque([], self.history_length)
        self.deque_t            = deque([], self.history_length)
        self.deque_fpar_laser    = deque([], self.history_length)
        
        self.init_counters()  


    # override from config       
        cfg_fn = os.path.join(qt.config['ins_cfg_path'], name+'.cfg')
        if not os.path.exists(cfg_fn):
            _f = open(cfg_fn, 'w')
            _f.write('')
            _f.close()
        
        self.ins_cfg = config.Config(cfg_fn)
        self.load_cfg()
        self.save_cfg()
        
    def get_all_cfg(self):
        for n in self._parlist:
            self.get(n)
        
    def load_cfg(self):
        params_from_cfg = self.ins_cfg.get_all()
        for p in self._parlist:
                self.set(p, value=self.ins_cfg.get(p))

    def save_cfg(self):
        for param in self._parlist:
            value = self.get(param)
            self.ins_cfg[param] = value
            

    #--------------get_set   

   
    def _do_set_invalid_data_marker(self, value):
        qt.instruments['physical_adwin'].Set_Par(55,value)

    def _do_get_invalid_data_marker(self):
        return qt.instruments['physical_adwin'].Get_Par(55)


    def publish_values(self):
        try:
            dweet_name = 'bell_board-lt4' if 'lt4' in self.setup_name else 'bell_board-lt3'
            dweepy.dweet_for(dweet_name,
                {'tail'             : self.tail_counts,
                 'pulse'            : self.pulse_counts,
                 'PSB_tail'         : self.PSB_tail_counts,
                 'SP_ref'           : self.SP_ref_LT4,
                 'repump_counts'    : self.repump_counts,
                 'strain'           : self.strain,
                 'cr_counts'        : self.cr_counts_avg_excl_repump,
                 'starts'           : float(self.start_seq)/self.dt,
                 'cr_failed'        : self.failed_cr_fraction_avg,
                 'script_running'   : self.script_running,
                 'invalid_marker'   : self.get_invalid_data_marker(),
                 'status_message'   : time.strftime('%H:%M')+': '+self.status_message,
                 'ent_events'       : self.entanglement_events,
                 })
            log_file=open(self.log_fp, 'a')  
            log_file.write(time.strftime('%Y%m%d%H%M%S')+' :{}:'.format(self.get_invalid_data_marker())+self.status_message + '\n')
            log_file.close()
        except Exception as e:
            print 'Error in publishing values for freeboard:', str(e)


    def send_error_email(self, subject = 'error with Bell optimizer', text =''):

        text= text +'\n Email no. {}'\
            '\n Current status of {} setup \n \
            tail {:.2f}, PSB tail {:.0f} \n \
            pulse {:.2f}.\n \
            SP ref LT3 {:.1f} & LT4 {:.1f} \n\
            CR counts LT4: {:.1f} \n \
            repump counts LT4: {:.1f} \n \
            strain splitting : {:.2f} \n\
            starts {:.1f} :  '.format(self.flood_email_counter,self.setup_name, 
                                 self.tail_counts, self.PSB_tail_counts, self.pulse_counts, self.SP_ref_LT3,
                                 self.SP_ref_LT4,self.cr_counts_avg_excl_repump, self.repump_counts, self.strain, self.start_seq)
        

        self.flood_email_counter +=1
        if self.get_email_recipient() != '':
            if self.flood_email_counter <= 10:
                print '-'*10
                print time.strftime('%H:%M')
                print '-'*10
                print 'sending email:', subject, text
                qt.instruments['gmailer'].send_email(self.get_email_recipient(), subject, text)
            else:
                print 'Not sending email, as already 10 sent this bell_optimizser run, wihtout relax rounds. Restart to clear.'

        self.status_message = subject

    def update_values(self) :
        par_counts_new = qt.instruments['physical_adwin'].Get_Par_Block(70,10)
        fpar_laser_new = qt.instruments['physical_adwin'].Get_FPar_Block(40,5)
        if 'lt4' in self.setup_name:
            par_laser_new = qt.instruments['physical_adwin'].Get_Par_Block(50,5)
        else:
            par_laser_new = qt.instruments['physical_adwin_lt4'].Get_Par_Block(50,5)
            
        self.deque_par_counts.append(par_counts_new)
        self.deque_par_laser.append(par_laser_new)
        self.deque_fpar_laser.append(fpar_laser_new)

        t=time.time()
        self.deque_t.append(t)

        return True    

    def set_failed(self):
        if 'lt4' in self.setup_name:
            qt.instruments['lt4_measurement_helper'].set_measurement_name('bell_optimizer_failed')    
        else:
            qt.instruments['lt3_measurement_helper'].set_measurement_name('bell_optimizer_failed')


    def stop_measurement(self):
        if 'lt4' in self.setup_name:
            qt.instruments['lt4_measurement_helper'].set_is_running(False)
        else:
            qt.instruments['lt3_measurement_helper'].set_is_running(False)

    def calculate_difference(self, avg_len):

        if avg_len < len(self.deque_par_counts):
            par_counts   = self.deque_par_counts[-1]-self.deque_par_counts[-1-avg_len]
            par_laser    = self.deque_par_laser[-1]- self.deque_par_laser[-1-avg_len]
            dt           = self.deque_t[-1]- self.deque_t[-1-avg_len]
        else:
            par_counts   = self.deque_par_counts[-1]-self.deque_par_counts[0]
            par_laser    = self.deque_par_laser[-1]- self.deque_par_laser[0]
            dt           = self.deque_t[-1]- self.deque_t[0]

        return par_counts , par_laser, dt

    def check(self):

        try:
            if 'lt4' in self.setup_name:
                self.script_running = qt.instruments['lt4_measurement_helper'].get_is_running()
            else:
                self.script_running = qt.instruments['lt3_measurement_helper'].get_is_running() and \
                                            'bell_lt3.py' in qt.instruments['lt3_measurement_helper'].get_script_path()
            if not self.script_running:
                self.script_not_running_counter += 1
                self.status_message = 'Bell script not running'
                 
                            
                if self.script_not_running_counter > self.max_counter_for_waiting_time :
                    self.send_error_email(subject = 'ERROR : Bell sequence not running')
                    self.stop()
                    return False
                else:
                    print self.status_message
                
                if self.script_not_running_counter == 1:
                    self.publish_values()
            else:
                self._run_counter += 1
                
                self.update_values()
                par_counts , par_laser, dt = self.calculate_difference(1)
                par_counts_avg , par_laser_avg, _tmp1 = self.calculate_difference(self.avg_length)
                fpar_laser_array=np.array(self.deque_fpar_laser)
               
                self.dt = dt
                self.cr_checks = par_counts[2]
                self.cr_counts = 0 if self.cr_checks ==0 else np.float(par_counts[0])/self.cr_checks
                self.repumps = par_counts[1]
                self.repump_counts = self.repump_counts if self.repumps == 0 else np.float(par_counts[6])/self.repumps
                self.entanglement_events = self.deque_par_counts[-1][8]
                
                 # Currently we are using only the average value of the cr_counts & failed_cr_fraction_avg
                self.cr_checks_avg =  par_counts_avg[2]
                self.repumps_avg = par_counts_avg[1]
                cr_checks_excl_repumps_avg = self.cr_checks_avg - self.repumps_avg
                self.cr_counts_avg_excl_repump = 0 if cr_checks_excl_repumps_avg ==0 else np.float(par_counts_avg[0])/cr_checks_excl_repumps_avg
                self.failed_cr_fraction_avg = 0  if self.cr_checks_avg == 0 else np.float(par_counts_avg[9]) / self.cr_checks_avg

                self.start_seq = par_counts[3]

                self.qrng_voltage = qt.instruments['labjack'].get_analog_in1()

                if self.start_seq > 0:
                    self.PSB_tail_counts = np.float(par_laser[0])/self.start_seq/125.*10000.
                    self.tail_counts = np.float(par_laser[1])/self.start_seq/125.*10000.
                    self.pulse_counts =  np.float(par_laser[2])/self.start_seq/125.*10000.
                    self.SP_ref_LT3 = np.float(par_laser[4])/self.start_seq/125.*10000.
                    self.SP_ref_LT4 = np.float(par_laser[3])/self.start_seq/125.*10000.
                    self.tail_counts_avg = np.float(par_laser_avg[1])/par_counts_avg[3]/125.*10000.
                else:
                    self.PSB_tail_counts, self.tail_counts, self.pulse_counts, self.SP_ref_LT3, self.SP_ref_LT4 = (0,0,0,0,0)
                
                self.SP_ref = self.SP_ref_LT4 if 'lt4' in self.setup_name else self.SP_ref_LT3
                    
                self.strain = qt.instruments['e_primer'].get_strain_splitting()
                
                self.publish_values()

                if 'lt3' in self.setup_name:
                    jitterDetected, jitter_text = self.check_jitter()
                    lock_ok, lock_text = self.check_laser_lock()
                else:
                    jitterDetected, jitter_text = False, ''
                    lock_ok, lock_text = True, ''

                self.status_message = ''

                if self.qrng_voltage < 0.05 or self.qrng_voltage > 0.2 :
                    text ='The QRNG voltage is measured to be {:.3f}. The QRNG detector might be broken\n'.format(self.qrng_voltage)
                    self.status_message += text 
                    self.set_invalid_data_marker(1)
                    subject = 'ERROR : QRNG threshold voltage too low {} setup'.format(self.setup_name)
                    self.send_error_email(subject = subject, text = text)
                       
                if jitterDetected:
                    self.status_message += 'Jitter detected!\n'
                    text = jitter_text
                    subject = 'ERROR :AWG jitte detected'
                    self.send_error_email(subject = subject, text = text)

                if not(lock_ok):
                    self.status_message += 'Laser Lock issue!\n'
                    text = lock_text
                    subject = 'ERROR : Laser Lock issue!'
                    self.set_invalid_data_marker(1)  
                    self.send_error_email(subject = subject, text = text)
                    
                    #self.set_invalid_data_marker(1)

                ## WM check.
                if len(np.unique(fpar_laser_array[:,self._taper_index])) == 1:  
                    self.set_invalid_data_marker(1)
                    subject = 'ERROR : The {} frequency of the taper laser is not updated'.format(self.setup_name)
                    text= 'The taper laser frequency is not updated : {:.6f} & {:.6f}  GHz. Check the wavemeter or the laser.\n'.format(fpar_laser_array[0,self._taper_index],fpar_laser_array[-1,self._taper_index])
                    self.status_message += text 
                    self.send_error_email(subject = subject, text = text)
                if len(np.unique(fpar_laser_array[:,1])) == 1: # New focus value not updated
                    self.set_invalid_data_marker(1)
                    subject = 'ERROR : The {} frequency of the new-focus laser is not updated'.format(self.setup_name)
                    text ='The new-focus laser frequency is not updated : {:.6f} & {:.6f}  GHz. Check the wavemeter or the laser.\n'.format(fpar_laser_array[0,1],fpar_laser_array[-1,1])
                    self.status_message += text 
                    self.send_error_email(subject = subject, text = text)
                if len(np.unique(fpar_laser_array[:,2])) == 1: # Yellow value not updated
                    self.set_invalid_data_marker(1)
                    subject = 'ERROR : The {} frequency of the yellow laser is not updated'.format(self.setup_name)
                    text ='The yellow laser frequency is not updated : {:.6f} & {:.6f}  GHz. Check the wavemeter or the laser.\n'.format(fpar_laser_array[0,2],fpar_laser_array[-1,2])
                    self.status_message += text 
                    self.send_error_email(subject = subject, text = text)

                if self.cr_checks <= 50:
                    self.waiting_for_other_setup_counter += 1
                    self.status_message += 'Waiting for the other setup to come back\n'
                    if self.waiting_for_other_setup_counter > self.max_counter_for_waiting_time:
                        self.send_error_email(subject = 'ERROR : Bell sequence waiting for other setup', text = 'waiting too long')

                elif self.wait_counter > 0:
                    self.status_message+='Waiting for another {:d} rounds'.format(int(self.wait_counter))
                    self.wait_counter -=1

                elif self.cr_counts < self.get_min_cr_counts() :
                    self.status_message += 'The CR counts are too low : {:.1f} instead of {:.1f}.\n'.format(self.cr_counts,self.get_min_cr_counts())
                    self.set_invalid_data_marker(1)
                    self.gate_optimize_counter +=1
                    if self.gate_optimize_counter <= self.get_max_counter_optimize() :
                        self.optimize_gate()
                        self.wait_counter = 1
                        self.need_to_optimize_nf = True
                    else:
                        text = 'Can\'t get the CR counts higher than {} even after {} optimization cycles. I have stopped the measurement!'.format(self.get_min_cr_counts(),
                             self.get_max_counter_optimize())
                        subject = 'ERROR : CR counts failure on {} setup'.format(self.setup_name)
                        self.send_error_email(subject =  subject, text = text)
                        self.set_pidgate_running(False)
                        self.set_failed()
                        self.stop_measurement()

                elif self.repump_counts < self.get_min_repump_counts():
                    self.status_message += 'The yellow laser is not in resonance. Got {:.1f} repump counts compare to {:.1f}.\n'.format(self.repump_counts, 
                                self.get_min_repump_counts())
                    self.set_invalid_data_marker(1)
                    self.yellow_optimize_counter +=1
                    if self.yellow_optimize_counter <= self.get_max_counter_optimize() :
                        if self.yellow_optimize_counter > self.get_max_counter_optimize()-2:
                            self.optimize_nf()
                            qt.msleep(3)
                        self.optimize_yellow()
                        self.wait_counter = 1
                        self.need_to_optimize_nf = True
                    else :
                        text = 'Can\'t get the repump counts higher than {} even after {} optimization cycles. The measurements will stop after this run!'.format(self.get_min_repump_counts(),
                                 self.get_max_counter_optimize())
                        subject = 'ERROR : Yellow laser not in resonance on {} setup'.format(self.setup_name)
                        self.send_error_email(subject = subject, text = text)
                        self.set_failed()

                elif (self.need_to_optimize_nf or ((time.time()-self.nf_optimize_timer) > (self.nb_min_between_nf_optim*60)) ):
                    self.status_message += 'The NewFocus needs to be optimized.\n'
                    self.set_invalid_data_marker(1)
                    self.optimize_nf()
                    self.need_to_optimize_nf = False
                    self.nf_optimize_timer = time.time()
                    self.wait_counter = 1


                elif self.strain > self.get_max_strain_splitting():
                    text = 'The strain splitting is too high :  {:.2f} compare to {:.2f}.\n'.format(self.strain, self.get_max_strain_splitting())
                    self.status_message += text
                    subject = 'ERROR : Too high strain splitting with {} setup'.format(self.setup_name)
                    self.send_error_email(subject = subject, text = text)
                    self.set_invalid_data_marker(1)
                    self.wait_counter = 2
                    self.need_to_optimize_nf = True

                elif self.SP_ref > self.get_max_SP_ref() and not np.isnan(self.SP_ref):
                    if self.pulse_counts > self.get_max_pulse_counts():
                        self.set_invalid_data_marker(1)
                    else:
                        self.set_invalid_data_marker(0)
                    self.status_message +='Bad laser rejection detected.\n'
                    self.laser_rejection_counter +=1

                    if not(qt.instruments['rejecter'].get_is_running()):
                        print  'Starting the optimizing...'
                        self.zoptimize_rejection()
                    #self.wait_counter = 1

                    if qt.instruments['rejecter'].get_noof_reject_cycles() > self.max_laser_reject_cycles:
                        text = 'Can\'t get a good laser rejection even after {} optimization cycles.'.format(self.max_laser_reject_cycles)
                        subject = 'ERROR : Bad rejection {} setup'.format(self.setup_name)
                        self.send_error_email(subject = subject, text = text)
                        #self.set_invalid_data_marker(1)
                        #self.set_failed()
         
                elif (self.failed_cr_fraction_avg > 0.96) and (self._run_counter % self.avg_length == 0):
                    subject = 'WARNING : low CR sucess {} setup'.format(self.setup_name)
                    self.status_message += 'Im passing too little cr checks. Please adjust the Cryo waveplate\n'
                    if self.nf_optimize_counter < 2:
                        self.need_to_optimize_nf = True
                        self.nf_optimize_counter +=1

                    self.send_error_email(subject = subject, text = self.status_message)

                elif self.cr_counts_avg_excl_repump > self.get_max_cr_counts_avg() :
                    if self.cryo_half_rot_degrees < self.max_cryo_half_rot_degrees :
                        qt.instruments['rejecter'].move('cryo_half', -0.5)
                        self.cryo_half_rot_degrees += 0.5
                        text = 'The average CR counts are {:.1f}. Rotating cryo half\
                            Rotated {} degrees.\n'.format(self.cr_counts_avg_excl_repump, self.cryo_half_rot_degrees)
                        self.status_message += text 
                        subject = 'WARNING : cryo_half rotating'.format(self.setup_name)
                        self.send_error_email(subject = subject, text = text)

                    else :
                        subject = 'WARNING : too high CR success and cryo_half at limit on {} setup'.format(self.setup_name)
                        text = 'I have passed too many cr checks and the cryo_half waveplate has already been rotated of {} degrees. Please check.'.format(self.max_cryo_half_rot_degrees)
                        self.set_invalid_data_marker(1)  
                        self.send_error_email(subject = subject, text = text)

                elif 'lt4' in self.setup_name and self.tail_counts_avg < self.get_min_tail_counts():
                    text = 'WARNING: avg tail counts too low: {:.2f} < {:.2f}'.format(self.tail_counts_avg, self.get_min_tail_counts())
                    subject = 'Low tail counts'
                    self.set_invalid_data_marker(1)
                    self.send_error_email(subject = subject, text = text)

                if self.status_message == '':
                    self.status_message = 'Relax Im doing my job'
                    self.script_not_running_counter = 0 
                    self.waiting_for_other_setup_counter = 0
                    self.gate_optimize_counter = 0
                    self.flood_email_counter   = 0  
                    self.nf_optimize_counter = 0 
                    self.yellow_optimize_counter = 0
                    self.laser_rejection_counter = 0
                    self.set_invalid_data_marker(0)                    
                
                print self.status_message 

            return True

        except Exception as e:
            self.set_invalid_data_marker(1)
            text = 'Errror in bell optimizer: ' + str(e)
            print text
            traceback.print_exc()
            subject = 'ERROR : Bell optimizer crash {} setup'.format(self.setup_name)
            self.send_error_email(subject = subject, text = text)
            return False

    def optimize_nf(self):
        self.set_pid_e_primer_running(False)
        qt.instruments['nf_optimizer'].optimize()
        qt.msleep(2.5)
        self.set_pid_e_primer_running(True)

    def optimize_yellow(self):
        e_primer_was_running = self.get_pid_e_primer_running()
        self.set_pid_e_primer_running(False)
        self.set_pidyellowfrq_running(False)
        qt.instruments['yellowfrq_optimizer'].optimize()
        qt.msleep(2.5)
        self.set_pidyellowfrq_running(True)
        self.set_pid_e_primer_running(e_primer_was_running)

    def optimize_gate(self):
        self.set_pidgate_running(False)
        qt.instruments['gate_optimizer'].optimize()
        qt.msleep(0.5)
        self.set_pidgate_running(True)

    def _do_get_pid_e_primer_running(self):
        return qt.instruments['e_primer'].get_is_running()

    def _do_set_pid_e_primer_running(self, val):
        if val:
            qt.instruments['e_primer'].start()
        else:
            qt.instruments['e_primer'].stop()

    def _do_get_pidyellowfrq_running(self):
        return qt.instruments['pidyellowfrq'].get_is_running()

    def _do_set_pidyellowfrq_running(self, val):
        if val:
            qt.instruments['pidyellowfrq'].start()
        else:
            qt.instruments['pidyellowfrq'].stop()

    def _do_get_pidgate_running(self):
        return qt.instruments['pidgate'].get_is_running()

    def _do_set_pidgate_running(self, val):
        if val:
            qt.instruments['pidgate'].start()
        else:
            qt.instruments['pidgate'].stop()

    def rejecter_half_plus(self):
        qt.instruments['rejecter'].move('zpl_half',self.get_rejecter_step(),quick_scan=True)

    def rejecter_half_min(self):
        qt.instruments['rejecter'].move('zpl_half',-self.get_rejecter_step(),quick_scan=True)

    def rejecter_quarter_plus(self):
        qt.instruments['rejecter'].move('zpl_quarter',self.get_rejecter_step(),quick_scan=True)

    def rejecter_quarter_min(self):
        qt.instruments['rejecter'].move('zpl_quarter',-self.get_rejecter_step(),quick_scan=True)

    #def optimize_rejecter(self):
    #    qt.instruments['rejecter'].nd_optimize(max_range=15,stepsize=self.get_rejecter_step(),method=2,quick_scan=False)
    def optimize_half(self):
        qt.instruments['waveplates_optimizer'].optimize('Half')
    def optimize_quarter(self):
        qt.instruments['waveplates_optimizer'].optimize('Quarter')

    def zoptimize_rejection(self):
        # qt.instruments['waveplates_optimizer'].optimize_rejection()
        qt.instruments['rejecter'].set_step_size(self.get_rejecter_step())
        #qt.instruments['rejecter'].set_good_rejection(self.get_max_SP_ref()-1)
        qt.instruments['rejecter'].start()

    def start(self):
        if self.get_is_running():
            print 'ALREADY RUNNING'
            return False
        if self._is_waiting:
            print 'still waiting from previous run, will wait 20 sec extra.'
            qt.msleep(20)
            self._stop_waiting()
        self.set_is_running(True)
        self._timer=gobject.timeout_add(int(self.get_read_interval()*1e3),\
                self._check)
        self.init_counters()
        if 'lt3' in self.setup_name:
            self.start_pharp()

        d=qt.Data(name='Bell_optimizer')
        d.create_file()
        d.close_file()
        self.log_fp=d.get_filepath()
            
        
        return True

    def init_counters(self):
        self.set_invalid_data_marker(0)
        self.deque_par_counts   = deque([], self.history_length)
        self.deque_par_laser    = deque([], self.history_length)
        self.deque_t            = deque([], self.history_length)
        self.deque_fpar_laser   = deque([], self.history_length)
        self.status_message = ''
        self.update_values()
        self._run_counter               = 0
        self.script_not_running_counter = 0
        self.waiting_for_other_setup_counter = 0
        self.gate_optimize_counter      = 0
        self.yellow_optimize_counter    = 0
        self.nf_optimize_counter        = 0
        self.laser_rejection_counter    = 0
        self.need_to_optimize_nf        = False
        self.nf_optimize_timer          = time.time()
        self.wait_counter               = 0
        self.flood_email_counter        = 0  
        self.repump_counts              = 0 
        self.cryo_half_rot_degrees      = 0    
        self.max_counter_for_waiting_time = np.floor(12*60/self.get_read_interval())

    def start_pharp(self):
        self._pharp.OpenDevice()
        self._pharp.start_histogram_mode()
        self._pharp.ClearHistMem()
        self._pharp.set_Range(4) # 64 ps binsize
        self._pharp.set_CFDLevel0(50)
        self._pharp.set_CFDLevel1(50)
        qt.msleep(0.1)
        self._pharp.StartMeas(int(1*60*60 * 1e3)) #1H measurement


    def stop(self):
        if 'lt3' in self.setup_name:
            self._pharp.StopMeas()
        self.set_is_running(False)
        qt.instruments['rejecter'].stop()
        return gobject.source_remove(self._timer)

    def check_jitter(self):
        if not self._pharp.get_MeasRunning():
            ret =  'Picoharp not running!'
            self.start_pharp()
            print ret
            return False, ret
        jitterDetected= False
        hist=self._pharp.GetHistogram()
        self._pharp.ClearHistMem()
        ret=''
        ret=ret+ str(hist[hist>0])
        peaks=np.where(hist>0)[0]*self._pharp.get_Resolution()/1000.
        ret=ret+'\n'+ str(peaks)
        print ret

        peak_loc = 889.8#890.1#  889.8
        if len(peaks)>1:
            peaks_width=peaks[-1]-peaks[0]
            peak_max=np.argmax(hist)*self._pharp.get_Resolution()/1000.
            if (peaks_width)>.5:
                ret=ret+'\n'+ 'JITTERING!! Execute check_awg_triggering with a reset'
                jitterDetected=True
            elif (peak_max<peak_loc-0.25) or (peak_max>peak_loc+0.25):
                ret=ret+'\n'+ 'Warning peak max at unexpected place, PEAK WRONG'
                jitterDetected=True
            else:
                ret=ret+'\n'+'No Jitter detected'
            ret=ret+'\n peak width: {:.2f} ns'.format(peaks_width)

            ret=ret+'\npeak loc at {:.2f} ns'.format(peak_max)


        ret=ret+'\ntotal counts in hist: {}'.format(sum(hist))
        #print ret
        return jitterDetected, ret

    def check_laser_lock(self, do_plot=False):
        
        
        if qt.instruments['signalhound'].get_frequency_center() > 136e6 or qt.instruments['signalhound'].get_frequency_center() < 134e6:
            qt.instruments['signalhound'].set_frequency_center(135e6)
            qt.instruments['signalhound'].set_frequency_span(5e6) 
            qt.instruments['signalhound'].set_rbw(25e3)
            qt.instruments['signalhound'].set_vbw(25e3)
            qt.instruments['signalhound'].ConfigSweepMode()
        
        freq,mi,ma=qt.instruments['signalhound'].GetSweep(do_plot=do_plot, max_points=650)

        f = common.fit_lorentz

        #f = a + 2*A/np.pi*gamma/(4*(x-x0)**2+gamma**2)
        #args = ['g_a', 'g_A', 'g_x0', 'g_gamma']
        x = freq/1e6
        y = mi

        args=[y[0], np.max(y), x[np.argmax(y)], 0.7]
        fitres = fit.fit1d(x, y, f, *args, fixed = [],
                           do_print = False, ret = True, maxfev=100)

        if not fitres['success']:
            return False, 'laser lock fit failed'

        x0 = fitres['params_dict']['x0']
        gamma = fitres['params_dict']['gamma']
        A = fitres['params_dict']['A']


        if gamma < 0.40 and x0 > 130 and x0 < 140 and A>0.05:  #MHZ, mV #
            return True, 'laser lock ok,  gamma = {:.2f} MHz, x0 = {:.1f} MHz, A = {:.2f} mV'.format(gamma, x0, A)

        return False, 'laser lock NOT ok, gamma = {:.2f} MHz, x0 = {:.1f} MHz, A = {:.2f} mV'.format(gamma, x0, A)
