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

class purification_optimizer(mo.multiple_optimizer):
    def __init__(self, name, setup_name='lt4'):
        mo.multiple_optimizer.__init__(self, name)
        
        ins_pars  ={'min_cr_counts'              :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':10},
                    'min_repump_counts'          :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET},
                    'max_counter_optimize'       :   {'type':types.IntType,'flags':Instrument.FLAG_GETSET, 'val':2},
                    'rejecter_step'              :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET}, 
                    'email_recipient'            :   {'type':types.StringType,'flags':Instrument.FLAG_GETSET, 'val':''}, 
                    'max_pulse_counts'           :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':3},
                    'max_SP_ref'                 :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':6},
                    'min_tail_counts'            :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':3.5},
                    'max_strain_splitting'       :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':2.1},
                    'max_cr_counts_avg'          :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':36},
                    'babysitting'                :   {'type':types.BooleanType,'flags':Instrument.FLAG_GETSET, 'val':False},
                    'stop_optimize'              :   {'type':types.BooleanType,'flags':Instrument.FLAG_GETSET, 'val':False},
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
        # self.add_function('rejecter_half_plus')
        # self.add_function('rejecter_half_min')
        # self.add_function('rejecter_quarter_plus')
        # self.add_function('rejecter_quarter_min')
        self.add_function('toggle_pid_gate')
        self.add_function('toggle_pid_nf')
        self.add_function('toggle_pid_yellowfrq')
        self.add_function('auto_optimize')
        self.add_function('start_babysit')
        self.add_function('stop_babysit')  
        self.add_function('stop_optimize_now')         

        self.setup_name = setup_name

        self._busy = False;

        self._taper_index = 4 if 'lt3' in setup_name else 3

        self.max_cryo_half_rot_degrees  = 3
        self.nb_min_between_nf_optim = 4
        
        self.history_length = 10
        self.avg_length = 9
        self.deque_par_counts   = deque([], self.history_length)
        self.deque_par_laser    = deque([], self.history_length)
        self.deque_t            = deque([], self.history_length)
        self.deque_fpar_laser    = deque([], self.history_length)
        self.deque_repump_counts = deque(self.history_length*[-1], self.history_length)
        
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

    #### no fiddling around wit adwin values yet. would not be a good idea!
    def _do_set_invalid_data_marker(self, value):
        pass
        # qt.instruments['physical_adwin'].Set_Par(55,value)

    def _do_get_invalid_data_marker(self):
        pass
        # return qt.instruments['physical_adwin'].Get_Par(55)


    def publish_values(self):
        try:
            # dweet_name = 'bell_board-lt4' if 'lt4' in self.setup_name else 'bell_board-lt3'
            # dweepy.dweet_for(dweet_name,
            #     {'tail'             : self.tail_counts,
            #      'pulse'            : self.pulse_counts,
            #      'PSB_tail'         : self.PSB_tail_counts,
            #      'SP_ref'           : self.SP_ref_LT4,
            #      'repump_counts'    : self.repump_counts,
            #      'strain'           : self.strain,
            #      'cr_counts'        : self.cr_counts_avg_excl_repump,
            #      'starts'           : float(self.start_seq)/self.dt,
            #      'cr_failed'        : self.failed_cr_fraction_avg,
            #      'script_running'   : self.script_running,
            #      'invalid_marker'   : self.get_invalid_data_marker(),
            #      'status_message'   : time.strftime('%H:%M')+': '+self.status_message,
            #      'ent_events'       : self.entanglement_events,
            #      })
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
                print 'Not sending email, as already 10 sent this purification_optimizer_failed run, wihtout relax rounds. Restart to clear.'

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
        print 'would set everything to failed now'
        # if 'lt4' in self.setup_name:
        #     qt.instruments['lt4_measurement_helper'].set_measurement_name('purification_optimizer_failed')    
        # else:
        #     qt.instruments['lt3_measurement_helper'].set_measurement_name('purification_optimizer_failed')


    def stop_measurement(self):
        print 'would stop the measurement now!' 
        # if 'lt4' in self.setup_name:
        #     qt.instruments['lt4_measurement_helper'].set_is_running(False)
        # else:
        #     qt.instruments['lt3_measurement_helper'].set_is_running(False)

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
        print "Check started"
        try:
            ### msmt helpers not currently implemented
            if 'lt4' in self.setup_name:
                self.script_running = qt.instruments['lt4_measurement_helper'].get_is_running()
            else:
                self.script_running = qt.instruments['lt3_measurement_helper'].get_is_running() and \
                                            'purify.py' in qt.instruments['lt3_measurement_helper'].get_script_path()

            if not self.script_running:
                self.script_not_running_counter += 1
                self.status_message = 'Purification script not running'
                 
                            
                if self.script_not_running_counter > self.max_counter_for_waiting_time :
                    # self.send_error_email(subject = 'ERROR : Purification sequence not running')
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

                self.status_message = ''


                print 'Cr counts / Yellow counts ', self.cr_counts, self.repump_counts
                
                if self.cr_checks <= 50:
                    self.waiting_for_other_setup_counter += 1
                    self.status_message += 'Waiting for the other setup to come back\n'
                    # if self.waiting_for_other_setup_counter > self.max_counter_for_waiting_time:
                    #     self.send_error_email(subject = 'ERROR : Purification sequence sequence waiting for other setup', text = 'waiting too long')

                elif self.wait_counter > 0:
                    self.status_message+='Waiting for another {:d} rounds'.format(int(self.wait_counter))
                    self.wait_counter -=1

                # PH Changed structure so that can try to optimise both gate AND yellow
                elif (self.cr_counts < self.get_min_cr_counts() ) or (self.repump_counts < self.get_min_repump_counts()):

                    if self.cr_counts < self.get_min_cr_counts() :
                        self.status_message += 'The CR counts are too low : {:.1f} instead of {:.1f}.\n'.format(self.cr_counts,self.get_min_cr_counts())
                        self.set_invalid_data_marker(1)
                        self.gate_optimize_counter +=1
                        if self.gate_optimize_counter <= self.get_max_counter_optimize() :

                            self.optimize_gate()
                            self.wait_counter = 1
                            self.need_to_optimize_nf = True
                            if self.gate_optimize_counter > self.get_max_counter_optimize()/2:
                                self.set_pid_e_primer_running(False)
                                #qt.instruments['physical_adwin'].Set_FPar(51,66.65)

                        else:
                            text = 'Can\'t get the CR counts higher than {} even after {} optimization cycles. I have stopped the measurement!'.format(self.get_min_cr_counts(),
                                 self.get_max_counter_optimize())
                            subject = 'ERROR : CR counts failure on {} setup'.format(self.setup_name)
                            self.send_error_email(subject =  subject, text = text)
                            self.set_pidgate_running(False)
                            self.set_failed()
                            self.stop_measurement()

                    if self.repump_counts < self.get_min_repump_counts():
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
                    # self.set_invalid_data_marker(1)
                    self.wait_counter = 2
                    self.need_to_optimize_nf = True

         
                # elif (self.failed_cr_fraction_avg > 0.96) and (self._run_counter % self.avg_length == 0):
                #     subject = 'WARNING : low CR sucess {} setup'.format(self.setup_name)
                #     self.status_message += 'Im passing too little cr checks. Please adjust the Cryo waveplate\n'
                #     if self.nf_optimize_counter < 2:
                #         self.need_to_optimize_nf = True
                #         self.nf_optimize_counter +=1

                #     self.send_error_email(subject = subject, text = self.status_message)

                # elif self.cr_counts_avg_excl_repump > self.get_max_cr_counts_avg() :
                #     if self.cryo_half_rot_degrees < self.max_cryo_half_rot_degrees :
                #         qt.instruments['rejecter'].move('cryo_half', -0.5)
                #         self.cryo_half_rot_degrees += 0.5
                #         text = 'The average CR counts are {:.1f}. Rotating cryo half\
                #             Rotated {} degrees.\n'.format(self.cr_counts_avg_excl_repump, self.cryo_half_rot_degrees)
                #         self.status_message += text 
                #         subject = 'WARNING : cryo_half rotating'.format(self.setup_name)
                #         self.send_error_email(subject = subject, text = text)

                #     else :
                #         subject = 'WARNING : too high CR success and cryo_half at limit on {} setup'.format(self.setup_name)
                #         text = 'I have passed too many cr checks and the cryo_half waveplate has already been rotated of {} degrees. Please check.'.format(self.max_cryo_half_rot_degrees)
                #         self.set_invalid_data_marker(1)  
                #         self.send_error_email(subject = subject, text = text)

                # elif 'lt4' in self.setup_name and self.tail_counts_avg >0 and self.tail_counts_avg < self.get_min_tail_counts():
                #     text = 'WARNING: avg tail counts too low: {:.2f} < {:.2f}'.format(self.tail_counts_avg, self.get_min_tail_counts())
                #     subject = 'Low tail counts'
                #     self.set_invalid_data_marker(1)
                #     self.send_error_email(subject = subject, text = text)

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
            text = 'Errror in purification optimizer: ' + str(e)
            print text
            traceback.print_exc()
            subject = 'ERROR : Bell optimizer crash {} setup'.format(self.setup_name)
            self.send_error_email(subject = subject, text = text)
            return False

    def optimize_nf(self):
        e_primer_was_running = self.get_pid_e_primer_running()        
        self.set_pid_e_primer_running(False)
        # qt.instruments['nf_optimizer'].optimize()
        qt.instruments['auto_optimizer'].optimize_newfocus()
        qt.msleep(0.5)
        self.set_pid_e_primer_running(e_primer_was_running)

    def optimize_yellow(self):
        e_primer_was_running = self.get_pid_e_primer_running()
        self.set_pid_e_primer_running(False)
        self.set_pidyellowfrq_running(False)
        self.set_pidgate_running(False)        
        #qt.instruments['yellowfrq_optimizer'].optimize()
        qt.instruments['auto_optimizer'].optimize_yellow();
        qt.msleep(4.0)
        self.set_pidyellowfrq_running(True)
        self.set_pidgate_running(True)        
        self.set_pid_e_primer_running(e_primer_was_running)

    def optimize_gate(self):
        # self.set_pidgate_running(False)
        # qt.instruments['gate_optimizer'].optimize()
        # qt.msleep(0.5)
        # self.set_pidgate_running(True)
        e_primer_was_running = self.get_pid_e_primer_running()
        self.set_pid_e_primer_running(False)
        self.set_pidyellowfrq_running(False)
        self.set_pidgate_running(False)        
        #qt.instruments['yellowfrq_optimizer'].optimize()
        qt.instruments['auto_optimizer'].optimize_gate();
        qt.msleep(0.5)
        self.set_pidyellowfrq_running(True)
        self.set_pidgate_running(True)        
        self.set_pid_e_primer_running(e_primer_was_running)        

    def auto_optimize(self):
        e_primer_was_running = self.get_pid_e_primer_running()        
        self.set_pid_e_primer_running(False)
        self.set_pidyellowfrq_running(False)
        self.set_pidgate_running(False)           
        if qt.instruments['auto_optimizer'].flow():
            print 'Success!'
        else:
            print 'Finished before end'
        qt.msleep(3.0)
        self.set_pidyellowfrq_running(True)
        self.set_pidgate_running(True)        
        self.set_pid_e_primer_running(e_primer_was_running)            

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

    def toggle_pid_gate(self):

        self.set_pidgate_running(not self._do_get_pidgate_running())

    def toggle_pid_nf(self):
       self.set_pid_e_primer_running(not self._do_get_pid_e_primer_running())


    def toggle_pid_yellowfrq(self):
        self.set_pidyellowfrq_running(not self._do_get_pidyellowfrq_running())

    def rejecter_half_plus(self):
        qt.instruments['rejecter'].move('zpl_half',self.get_rejecter_step(),quick_scan=True)

    def rejecter_half_min(self):
        qt.instruments['rejecter'].move('zpl_half',-self.get_rejecter_step(),quick_scan=True)

    def rejecter_quarter_plus(self):
        qt.instruments['rejecter'].move('zpl_quarter',self.get_rejecter_step(),quick_scan=True)

    def rejecter_quarter_min(self):
        qt.instruments['rejecter'].move('zpl_quarter',-self.get_rejecter_step(),quick_scan=True)

    def start_babysit(self):
        print 'Start'
        if self._babysitting:
            print 'Already running'
            return
        self._babysitting = True            
        self.set_stop_optimize(False)

        # Start running babysitter
        self._timer=gobject.timeout_add(int(self.get_read_interval()*1e3),self._babysit)

    def stop_babysit(self):
        # print 'Stop'
        # if not self._babysitting:
        #     print 'Not running'
        self._babysitting = False
        return gobject.source_remove(self._timer)        

    def _babysit(self):
        # print 'Check if all is OK'
        if not self._babysitting:
            return False   
        
        # Read values
        self.update_values()
        par_counts , par_laser, dt = self.calculate_difference(1)
        par_counts_avg , par_laser_avg, _tmp1 = self.calculate_difference(self.avg_length)
        fpar_laser_array=np.array(self.deque_fpar_laser)
       
        self.dt = dt
        self.cr_checks = par_counts[2]
        self.cr_counts = 0 if self.cr_checks ==0 else np.float(par_counts[0])/self.cr_checks
        self.repumps = par_counts[1]
        self.repump_counts = self.repump_counts if self.repumps == 0 else np.float(par_counts[6])/self.repumps

        # If all lasers are on resonance: write to logger
        if (self.cr_counts > self.get_min_cr_counts() ) and (self.repump_counts > self.get_min_repump_counts()):
            # print self.cr_counts, '>', self.get_min_cr_counts(), 'and', self.repump_counts, '>', self.get_min_repump_counts(), 'so logging frequencies'
            qt.instruments['frequency_logger'].log()            
            
        # If one of the lasers is off and the optimizer is not already running: run optimizer
        if self._busy:
            print 'Optimizer is running, so do not do anything'
        else:
            if (self.cr_counts < self.get_min_cr_counts() or self.repump_counts < self.get_min_repump_counts()):
                if (self.cr_counts == 0):
                    print 'No measurement running atm!'
                else:
                    print self.cr_counts, '<', self.get_min_cr_counts(), 'or', self.repump_counts, '<', self.get_min_repump_counts(), 'so start optimizer'
                    self.busy = True
                    e_primer_was_running = self.get_pid_e_primer_running()        
                    self.set_pid_e_primer_running(False)
                    self.set_pidyellowfrq_running(False)
                    self.set_pidgate_running(False)   
                    if qt.instruments['auto_optimizer'].flow():
                        print 'Success!'
                    else:
                        print 'Exited before end'
                    qt.msleep(2)
                    self.set_pidyellowfrq_running(True)
                    self.set_pidgate_running(True)        
                    self.set_pid_e_primer_running(e_primer_was_running) 
                    self._busy = False
            else:
                # Even if all counts are fine, the newfocus might still be off
                if qt.instruments['auto_optimizer'].check_detuned_repump():
                    self.busy = True                    
                    self.optimize_nf()
                    self._busy = False                    
                else:
                    print 'Everything OK'
        return True;

    def stop_optimize_now(self):
        self._stop_optimize = True;


    def start(self):
        print 'Starting'
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


        d=qt.Data(name='Purification_optimizer')
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




    def stop(self):
        self.set_is_running(False)
        return gobject.source_remove(self._timer)

