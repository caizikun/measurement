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

class bell_optimizer(mo.multiple_optimizer):
    def __init__(self, name, setup_name='lt4'):
        mo.multiple_optimizer.__init__(self, name)
       
        ins_pars  = {'min_starts'                :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET},
                    'min_cr_counts'              :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':10},
                    'min_repump_counts'          :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET},
                    'max_counter_optimize'       :   {'type':types.IntType,'flags':Instrument.FLAG_GETSET, 'val':2},
                    'rejecter_step'              :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET}, 
                    'email_recipient'            :   {'type':types.StringType,'flags':Instrument.FLAG_GETSET}, 
                    'min_tail_counts'            :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':3},
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

   
    def set_invalid_data_marker(self, value):
        qt.instruments['physical_adwin'].Set_Par(55,value)


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
        print 'sending email:', subject, text
        if self.get_email_recipient() != '':
            qt.instruments['gmailer'].send_email(self.get_email_recipient(), subject, text)



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
        return par_counts, par_laser

    
    def check(self):

        par_counts, par_laser = self.update_values()
        self.cr_checks = par_counts[2]
        self.cr_counts = 0 if self.cr_checks ==0 else np.float(par_counts[0])/self.cr_checks
        self.repumps = par_counts[1]
        self.repump_counts = 0 if self.repumps == 0 else np.float(par_counts[6])/self.repumps
        
        self.start_seq = par_counts[3]
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
            script_running = qt.instruments['lt4_measurement_helper'].get_is_running()
        else:
            self.SP_ref = self.SP_ref_LT3
            script_running = qt.instruments['lt3_measurement_helper'].get_is_running()

        self.strain = qt.instruments['e_primer'].get_strain_splitting()

        max_counter_for_waiting_time = np.floor(1*60/self.get_read_interval())
        max_counter_for_nf_optimize = np.floor(np.float(self.get_nb_min_between_nf_optim()*60/self.get_read_interval()))

        #print 'script not running counter : ', self.script_not_running_counter


        if not script_running :
            self.script_not_running_counter += 1
                        
            if self.script_not_running_counter > max_counter_for_waiting_time :
                self.send_error_email(subject = 'ERROR : Bell sequence not running')
                self.stop()
                return False
            else :
                print 'Bell script not running'
            
        elif self.cr_checks <= 0 :
            print 'Waiting for the other setup to come back'

        elif self.wait_counter > 0:
            self.wait_counter -=1
            print 'Waiting for another {:d} rounds'.format(int(self.wait_counter))

        elif self.cr_counts < self.get_min_cr_counts() :
            print '\nThe CR counts are too low : {:.1f} instead of {:.1f}.\n'.format(self.cr_counts,self.get_min_cr_counts())
            self.set_invalid_data_marker(1)
            self.gate_optimize_counter +=1
            if self.gate_optimize_counter <= self.get_max_counter_optimize() :
                self.optimize_gate()
                self.need_to_optimize_nf = True
            else:
                text = 'Can\'t get the CR counts higher than {} even after {} optimization cycles'.format(self.get_min_cr_counts(),
                     self.get_max_counter_optimize())
                subject = 'ERROR : CR counts too low on {} setup'.format(self.setup_name)
                self.send_error_email(subject =  subject, text = text)
                self.stop()
                return False

        elif self.repump_counts < self.get_min_repump_counts():
            print '\nThe yellow laser is not in resonance. Got {:.1f} repump counts compare to {:.1f}.\n'.format(self.repump_counts, 
                        self.get_min_repump_counts())
            self.set_invalid_data_marker(1)
            self.yellow_optimize_counter +=1
            if self.yellow_optimize_counter <= self.get_max_counter_optimize() :
                self.optimize_yellow()
                self.need_to_optimize_nf = True
            else :
                text = 'Can\'t get the repump counts higher than {} even after {} optimization cycles'.format(self.get_min_repump_counts(),
                         self.get_max_counter_optimize())
                subject = 'ERROR : Yellow laser not in resonance on {} setup'.format(self.setup_name)
                self.send_error_email(subject = subject, text = text)
                self.stop()
                return False

        elif (self.need_to_optimize_nf or (self.nf_optimize_counter > max_counter_for_nf_optimize)):
            print '\nThe NewFocus needs to be optimized.\n'
            self.set_invalid_data_marker(1)
            self.optimize_nf()
            self.need_to_optimize_nf = False
            self.nf_optimize_counter = 0
            self.wait_counter = 1

        elif self.strain > self.get_max_strain_splitting():
            print '\n The strain splitting is too high :  {:.2f} compare to {:.2f}.'.format(self.strain, self.get_max_strain_splitting())
            self.set_invalid_data_marker(1)
            text = 'The strain splitting is too high :  {:.2f} compare to {:.2f}.'.format(self.strain, self.get_max_strain_splitting())
            subject = 'ERROR : Too high strain splitting with {} setup'.format(self.setup_name)
            if  self.strain_email_counter == 0 :
                self.send_error_email(subject = subject, text = text)
            self.strain_email_counter +=1
            
        elif self.SP_ref > self.get_max_SP_ref() :
            if self.pulse_counts > self.get_max_pulse_counts():
                self.set_invalid_data_marker(1)
            print '\n Bad laser rejection detected. Starting the optimizing...'
            self.laser_rejection_counter +=1
            if self.laser_rejection_counter <= self.get_max_laser_reject_cycles() :
                self.optimize_rejection()
                #self.optimize_half()
                #self.optimize_quarter()
                self.wait_counter = 1
            else : 
                text = 'Can\'t get a good laser rejection even after {} optimization cycles'.format(self.get_max_laser_reject_cycles())
                subject = 'ERROR : Bad rejection {} setup'.format(self.setup_name)
                self.send_error_email(subject = subject, text = text)
                self.stop()
                return False


        else :
            self.script_not_running_counter = 0 
            self.gate_optimize_counter = 0 
            self.yellow_optimize_counter = 0
            self.laser_rejection_counter = 0
            self.nf_optimize_counter += 1
            self.set_invalid_data_marker(0)
            print 'Relax, Im doing my job.'

        return True


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
        self.set_invalid_data_marker(0)
        self.update_values()
        self.script_not_running_counter = 0
        self.gate_optimize_counter      = 0
        self.yellow_optimize_counter    = 0
        self.laser_rejection_counter    = 0
        self.need_to_optimize_nf     = False
        self.nf_optimize_counter     = 0
        self.wait_counter = 0
        self.strain_email_counter           = 0

        