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
                    'nb_min_between_nf_optim'    :   {'type':types.IntType,'flags':Instrument.FLAG_GETSET, 'val':2},
                    }           
        instrument_helper.create_get_set(self,ins_pars)

        self._parlist = ins_pars.keys()

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
        self.add_function('rejecter_quarter_plus')
        self.add_function('rejecter_quarter_min')
        self.add_function('optimize_half')
        self.add_function('optimize_quarter')
        self.add_function('check_rejection')

        #self._mode = 'check_starts'
        #self._mode_rep = 0

        self._pulse_cts  = 0
        self._pulse_cts_lt3  = 0
        self._pulse_cts_lt4  = 0
        self._tail_cts   = 0
        self._seq_starts = 0

        self.setup_name = setup_name
        self.par_counts_old          = np.zeros(10,dtype= np.int32)
        self.par_laser_old           = np.zeros(5,dtype= np.int32)
        self.script_not_running_counter = 0
        self.need_to_optimize_nf     = False
        self.gate_optimize_counter   = 0
        self.yellow_optimize_counter = 0


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

    #XXXXX disable the functions associated with laser_rejection on LT3

    def check_rejection(self):

        tail_cts = qt.instruments['physical_adwin'].Get_Par(51)
        pulse_cts = qt.instruments['physical_adwin'].Get_Par(52)
        pulse_cts_lt4 = qt.instruments['physical_adwin'].Get_Par(53)
        pulse_cts_lt3 = qt.instruments['physical_adwin'].Get_Par(54)
        seq_starts=qt.instruments['physical_adwin'].Get_Par(73)

        try:
            tail = float(tail_cts-self._tail_cts)/(seq_starts-self._seq_starts)/125.*10000.
            pulse = float(pulse_cts-self._pulse_cts)/(seq_starts-self._seq_starts)/125.*10000.
            pulse_lt4 = float(pulse_cts_lt4-self._pulse_cts_lt4)/(seq_starts-self._seq_starts)/125.*10000.
            pulse_lt3 = float(pulse_cts_lt3-self._pulse_cts_lt3)/(seq_starts-self._seq_starts)/125.*10000.
            print 'pulse: {:.2f}, tail" {:.2f}, SP pulse lt4 {:.2f}, SP pulse lt3 {:.2f}'.format(pulse,tail, pulse_lt4, pulse_lt3)
        except ZeroDivisionError:
            print 'no sequence starts'

        self._pulse_cts  = pulse_cts
        self._tail_cts   = tail_cts
        self._seq_starts = seq_starts
        self._pulse_cts_lt3 = pulse_cts_lt3
        self._pulse_cts_lt4 = pulse_cts_lt4
        return tail, pulse, pulse_lt4, pulse_lt3


    def set_invalid_data_marker(self, value):
        qt.instruments['physical_adwin'].Set_Par(53,value)


    def send_error_email(self, subject = 'error with Bell optimizer', text =''):

        text= text +'\n Current status of {} setup \n \
            tail {:.2f}, PSB tail {:.0f} \n \
            pulse {:.2f}.\n \
            SP ref LT3 {:.1f} & LT4 {:.1f} \n\
            CR counts LT4: {:.1f} \n \
            repump counts LT4: {:.1f} \n \
            starts {:.1f} :  '.format(self.setup_name, 
                                 self.tail_counts, self.PSB_tail_counts, self.pulse_counts, self.SP_ref_LT3,
                                 self.SP_ref_LT4,self.cr_counts, self.repump_counts, self.start_seq)

        qt.instruments['gmailer'].send_email(self.get_email_recipient(), subject, text)


    def update_values(self) :
        par_counts_new = qt.instruments['physical_adwin'].Get_Par_Block(70,10)
        par_laser_new = qt.instruments['physical_adwin'].Get_Par_Block(50,5)

        par_counts = par_counts_new- self.par_counts_old
        par_laser = par_laser_new- self.par_laser_old

        self.par_counts_old = par_counts_new
        self.par_laser_old = par_laser_new
        return par_counts, par_laser

    
    def check(self):
        print 'starting Bell optimizer checks'

        script_running = qt.instruments['lt4_measurement_helper'].get_is_running()




        par_counts, par_laser = self.update_values()
        self.cr_checks = par_counts[2]
        self.cr_counts = 0 if self.cr_checks ==0 else par_counts[0]/self.cr_checks
        self.repumps = par_counts[1]
        self.repump_counts = 0 if self.repumps == 0 else par_counts[6]/self.repumps
        
        self.start_seq = par_counts[3]
        if self.start_seq > 0:
            self.PSB_tail_counts = np.float(par_laser[0])/self.start_seq/125.*10000.
            self.tail_counts = np.float(par_laser[1])/self.start_seq/125.*10000.
            self.pulse_counts =  np.float(par_laser[2])/self.start_seq/125.*10000.
            self.SP_ref_LT3 = np.float(par_laser[3])/self.start_seq/125.*10000.
            self.SP_ref_LT4 = np.float(par_laser[4])/self.start_seq/125.*10000.
        if 'lt4' in self.setup_name:
            self.SP_ref = self.SP_ref_LT4
        else:
            self.SP_ref = self.SP_ref_LT3


        max_counter_for_waiting_time = np.floor(0.1*60/self.get_read_interval())
        max_counter_for_nf_optimize = np.floor(np.float(self.get_nb_min_between_nf_optim()*60/self.get_read_interval()))

        print 'script not running counter : ', self.script_not_running_counter


        if not script_running :
            self.script_not_running_counter += 1
                        
            if self.script_not_running_counter > max_counter_for_waiting_time :
                self.send_error_email(subject = 'ERROR : Bell sequence not running')
                self.stop()
                return False
            else :
                print 'Bell script not running'
                return True
            
        elif self.cr_checks <= 0 :
            print 'Waiting for the other setup to come back'
            return True

        elif self.cr_counts < self.get_min_cr_counts() :
            self.set_invalid_data_marker(True)
            self.gate_optimize_counter +=1
            if self.gate_optimize_counter <= self.get_max_counter_optimize() :
                self.optimize_gate()
                self.need_to_optimize_nf = True
                return True
            else:
                text = 'Can\'t get the CR counts higher than {} even after {} optimization cycles'.format(self.get_min_cr_counts(),
                     self.get_max_counter_optimize())
                subject = 'ERROR : CR counts too low on {} setup'.format(self.setup_name)
                self.send_error_email(subject =  subject, text = text)
                self.stop()
                return False

        elif self.repump_counts < self.get_min_repump_counts():
            self.set_invalid_data_marker(True)
            self.yellow_optimize_counter +=1
            if self.yellow_optimize_counter <= self.get_max_counter_optimize() :
                self.optimize_yellow()
                self.need_to_optimize_nf = True
                return True
            else :
                text = 'Can\'t get the repump counts higher than {} even after {} optimization cycles'.format(self.get_min_repump_count,
                         self.get_max_counter_optimize())
                subject = 'ERROR : Yelloser not in resonance on {} setup'.format(self.setup_name)
                self.send_error_email(subject = subject, text = text)
                self.stop()
                return False

        elif (self.need_to_optimize_nf | (self.nf_optimize_counter > max_counter_for_nf_optimize)):
            self.set_invalid_data_marker(True)
            self.optimize_nf()
            self.need_to_optimize_nf = False
            self.nf_optimize_counter = 0
            
        elif self.SP_ref > self.get_max_SP_ref() :
            self.set_invalid_data_marker(True)
            print '\n Bad laser rejection detected. Starting the optimizing...'
            self.laser_rejection_counter +=1
            if self.laser_rejection_counter <= self.get_max_laser_reject_cycles() :
                self.optimize_half()
                self.optimize_quarter()
                return True
            else : 
                text = 'Can\'t get a good laser rejection even after {} optimization cycles'.format(self.get_max_laser_reject_cycles())
                subject = 'ERROR : Bad rejectin {} setup'.format(self.setup_name)
                self.send_error_email(subject = subject, text = text)
                self.stop()
                return False

        else :
            self.script_not_running_counter = 0 
            self.gate_optimize_counter = 0 
            self.yellow_optimize_counter = 0
            self.set_invalid_data_marker(False)
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
        qt.instruments['half_optimizer'].optimize()
    def optimize_quarter(self):
        qt.instruments['quarter_optimizer'].optimize()


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
        self.update_values()
        self.script_not_running_counter = 0
        self.gate_optimize_counter      = 0
        self.yellow_optimize_counter    = 0
        return True