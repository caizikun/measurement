import qt
import os
from instrument import Instrument
import numpy as np
import gobject
import instrument_helper
from lib import config
import multiple_optimizer as mo
reload(mo)
import types
import time
import dweepy
import requests.packages.urllib3

class bell_optimizer(mo.multiple_optimizer):
    def __init__(self, name, setup_name='lt4'):
        mo.multiple_optimizer.__init__(self, name)
        
        ins_pars  ={'min_cr_counts'              :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':10},
                    'min_repump_counts'          :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET},
                    'max_counter_optimize'       :   {'type':types.IntType,'flags':Instrument.FLAG_GETSET, 'val':2},
                    'rejecter_step'              :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET}, 
                    'email_recipient'            :   {'type':types.StringType,'flags':Instrument.FLAG_GETSET}, 
                    'max_pulse_counts'           :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':3},
                    'max_SP_ref'                 :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':6},
                    'max_laser_reject_cycles'    :   {'type':types.IntType,'flags':Instrument.FLAG_GETSET, 'val':3},
                    'nb_min_between_nf_optim'    :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':2},
                    'max_strain_splitting'      :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':2.1},
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
        self.add_function('optimize_rejection')
        self.add_function('rejecter_quarter_plus')
        self.add_function('rejecter_quarter_min')
        #self.add_function('optimize_half')
        #self.add_function('optimize_quarter')

        #self._mode = 'check_starts'
        #self._mode_rep = 0

        self.setup_name = setup_name
        if 'lt3' in setup_name:
            requests.packages.urllib3.disable_warnings() #XXXXXXXXXXX FIX by updating packages in Canopy package manager?
        self.par_counts_old          = np.zeros(10,dtype= np.int32)
        self.par_laser_old           = np.zeros(5,dtype= np.int32)
        
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
        dweet_name = 'bell_board-lt4' if 'lt4' in self.setup_name else 'bell_board-lt3'
        dweepy.dweet_for(dweet_name,
            {'tail'             : self.tail_counts,
             'pulse'            : self.pulse_counts,
             'PSB_tail'         : self.PSB_tail_counts,
             'SP_ref'           : self.SP_ref_LT4,
             'repump_counts'    : self.repump_counts,
             'strain'           : self.strain,
             'cr_counts'        : self.cr_counts,
             'starts'           : float(self.start_seq)/self.dt,
             'cr_failed'        : self.failed_cr_fraction,
             'script_running'   : self.script_running,
             'invalid_marker'   : self.get_invalid_data_marker(),
             'status_message'   : time.strftime('%H:%M')+': '+self.status_message,
             'ent_events'       : self.entanglement_events,
             })

    def send_error_email(self, subject = 'error with Bell optimizer', text =''):

        text= text +'\n Current status of {} setup \n \
            tail {:.2f}, PSB tail {:.0f} \n \
            pulse {:.2f}.\n \
            SP ref LT3 {:.1f} & LT4 {:.1f} \n\
            CR counts LT4: {:.1f} \n \
            repump counts LT4: {:.1f} \n \
            strain splitting : {:.2f} \n\
            starts {:.1f} :  '.format(self.setup_name, 
                                 self.tail_counts, self.PSB_tail_counts, self.pulse_counts, self.SP_ref_LT3,
                                 self.SP_ref_LT4,self.cr_counts, self.repump_counts, self.strain, self.start_seq)
        print '-'*10
        print time.strftime('%H:%M')
        print '-'*10
        print 'sending email:', subject, text

        self.flood_email_counter +=1
        if self.get_email_recipient() != '' and self.flood_email_counter < 10 and self.status_message != subject:
            qt.instruments['gmailer'].send_email(self.get_email_recipient(), subject, text)
        self.status_message = subject



    def update_values(self) :
        par_counts_new = qt.instruments['physical_adwin'].Get_Par_Block(70,10)
        if 'lt4' in self.setup_name:
            par_laser_new = qt.instruments['physical_adwin'].Get_Par_Block(50,5)
        else:
            par_laser_new = qt.instruments['physical_adwin_lt4'].Get_Par_Block(50,5)

        par_counts = par_counts_new- self.par_counts_old
        par_laser = par_laser_new- self.par_laser_old

        self.par_counts_old = par_counts_new
        self.par_laser_old = par_laser_new

        t1=time.time()
        dt = t1-self._t0
        self._t0 = t1

        qrng_voltage = qt.instruments['labjack'].get_analog_in1()

        return par_counts, par_laser, dt, qrng_voltage

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

    def check(self):

        try:
            
            par_counts, par_laser, dt, qrng_voltage = self.update_values()
            self.dt = dt
            self.cr_checks = par_counts[2]
            self.cr_counts = 0 if self.cr_checks ==0 else np.float(par_counts[0])/self.cr_checks
            self.repumps = par_counts[1]
            self.repump_counts = self.repump_counts if self.repumps == 0 else np.float(par_counts[6])/self.repumps
            self.entanglement_events = self.par_counts_old[8]

            self.failed_cr_fraction = 0  if self.cr_checks == 0 else np.float(par_counts[9]) / self.cr_checks
            
            self.start_seq = par_counts[3]

            self.qrng_voltage = qrng_voltage

            if self.start_seq > 0:
                self.PSB_tail_counts = np.float(par_laser[0])/self.start_seq/125.*10000.
                self.tail_counts = np.float(par_laser[1])/self.start_seq/125.*10000.
                self.pulse_counts =  np.float(par_laser[2])/self.start_seq/125.*10000.
                self.SP_ref_LT3 = np.float(par_laser[4])/self.start_seq/125.*10000.
                self.SP_ref_LT4 = np.float(par_laser[3])/self.start_seq/125.*10000.
            else:
                self.PSB_tail_counts, self.tail_counts, self.pulse_counts, self.SP_ref_LT3, self.SP_ref_LT4 = (0,0,0,0,0)
            if 'lt4' in self.setup_name:
                self.SP_ref = self.SP_ref_LT4
                self.script_running = qt.instruments['lt4_measurement_helper'].get_is_running()
            else:
                self.SP_ref = self.SP_ref_LT3
                self.script_running = qt.instruments['lt3_measurement_helper'].get_is_running() and \
                        'bell_lt3.py' in qt.instruments['lt3_measurement_helper'].get_script_path()

            self.strain = qt.instruments['e_primer'].get_strain_splitting()

            max_counter_for_waiting_time = np.floor(10*60/self.get_read_interval())


            #print 'script not running counter : ', self.script_not_running_counter
            self.publish_values()

            if not self.script_running :
                self.script_not_running_counter += 1
                            
                if self.script_not_running_counter > max_counter_for_waiting_time :
                    self.send_error_email(subject = 'ERROR : Bell sequence not running')
                    self.stop()
                    return False
                else :
                    print 'Bell script not running'


            elif self.qrng_voltage < 0.05 or self.qrng_voltage > 0.2 :
                self.status_message = 'The QRNG voltage is measured to be {:.3f}. The QRNG detector might be broken'.format(self.qrng_voltage)
                print self.status_message
                self.set_invalid_data_marker(1)
                text = 'Check the QRNG, something is wrong with the theshold voltage !!!'
                subject = 'ERROR : QRNG threshold voltage too low {} setup'.format(self.setup_name)
                self.send_error_email(subject = subject, text = text)

                
            elif self.cr_checks <= 50:
                self.status_message = 'Waiting for the other setup to come back'
                print self.status_message

            elif self.wait_counter > 0:
                self.wait_counter -=1
                print 'Waiting for another {:d} rounds'.format(int(self.wait_counter))

            elif self.cr_counts < self.get_min_cr_counts() :
                self.status_message = 'The CR counts are too low : {:.1f} instead of {:.1f}.'.format(self.cr_counts,self.get_min_cr_counts())
                print self.status_message
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
                self.status_message = 'The yellow laser is not in resonance. Got {:.1f} repump counts compare to {:.1f}.'.format(self.repump_counts, 
                            self.get_min_repump_counts())
                print self.status_message
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

            elif (self.need_to_optimize_nf or ((time.time()-self.nf_optimize_timer) > (self.get_nb_min_between_nf_optim()*60)) ):
                self.status_message = 'The NewFocus needs to be optimized.'
                print self.status_message
                self.set_invalid_data_marker(1)
                self.optimize_nf()
                self.need_to_optimize_nf = False
                self.nf_optimize_timer = time.time()
                self.wait_counter = 1
                #self.set_invalid_data_marker(0)

            elif self.strain > self.get_max_strain_splitting():
                text = 'The strain splitting is too high :  {:.2f} compare to {:.2f}.'.format(self.strain, self.get_max_strain_splitting())
                subject = 'ERROR : Too high strain splitting with {} setup'.format(self.setup_name)
                self.send_error_email(subject = subject, text = text)
                print text
                self.set_invalid_data_marker(1)
                self.wait_counter = 2
                self.need_to_optimize_nf = True
                
            elif self.SP_ref > self.get_max_SP_ref() and not np.isnan(self.SP_ref):
                if self.pulse_counts > self.get_max_pulse_counts():
                    self.set_invalid_data_marker(1)
                else:
                    self.set_invalid_data_marker(0)
                self.status_message ='Bad laser rejection detected. Starting the optimizing...'
                print self.status_message
                self.laser_rejection_counter +=1
                if self.laser_rejection_counter <= self.get_max_laser_reject_cycles() :
                    self.optimize_rejection()
                    self.wait_counter = 1
                else : 
                    text = 'Can\'t get a good laser rejection even after {} optimization cycles. The measurements will stop after this run!'.format(self.get_max_laser_reject_cycles())
                    subject = 'ERROR : Bad rejection {} setup'.format(self.setup_name)
                    self.send_error_email(subject = subject, text = text)
                    self.set_invalid_data_marker(1)
                    self.set_failed()

            elif self.failed_cr_fraction < 0.5:
                subject = 'WARNING : high CR success {} setup'.format(self.setup_name)
                text = 'Im passing too many cr checks. Please adjust the Cryo waveplate'
                print text
                self.set_invalid_data_marker(1)
                #qt.instruments['rejecter'].move('cryo_half', -0.5)
                self.send_error_email(subject = subject, text = text)

            elif self.failed_cr_fraction > 0.99:
                subject = 'WARNING : low CR sucess {} setup'.format(self.setup_name)
                text = 'Im passing too little cr checks. Please adjust the Cryo waveplate'
                print text
                #qt.instruments['rejecter'].move('cryo_half', 0.5)
                self.send_error_email(subject = subject, text = text)

            else :
                self.script_not_running_counter = 0 
                self.gate_optimize_counter = 0 
                self.yellow_optimize_counter = 0
                self.laser_rejection_counter = 0
                self.set_invalid_data_marker(0)
                self.status_message = 'Relax, Im doing my job.'
                print self.status_message 

            return True

        except Exception as e:
            self.set_invalid_data_marker(1)
            text = 'Errror in bell optimizer: ' + str(e)
            print text
            subject = 'ERROR : Bell optimizer crash {} setup'.format(self.setup_name)
            self.send_error_email(subject = subject, text = text)
            return False


    def optimize_nf(self):
        self.set_pid_e_primer_running(False)
        qt.instruments['nf_optimizer'].optimize()
        qt.msleep(2.5)
        self.set_pid_e_primer_running(True)

    def optimize_yellow(self):
        self.set_pidyellowfrq_running(False)
        qt.instruments['yellowfrq_optimizer'].optimize()
        qt.msleep(2.5)
        self.set_pidyellowfrq_running(True)

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

    def optimize_rejection(self):
        qt.instruments['waveplates_optimizer'].optimize_rejection()


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
        return True

    def init_counters(self):
        self._t0 = time.time()
        self.set_invalid_data_marker(0)
        self.status_message = ''
        self.update_values()
        self.script_not_running_counter = 0
        self.gate_optimize_counter      = 0
        self.yellow_optimize_counter    = 0
        self.laser_rejection_counter    = 0
        self.need_to_optimize_nf        = False
        self.nf_optimize_timer          = self._t0
        self.wait_counter               = 0
        self.flood_email_counter        = 0  
        self.repump_counts              = 0      

        