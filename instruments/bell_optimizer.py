import qt
import os
from instrument import Instrument
import numpy as np
import instrument_helper
from lib import config
import multiple_optimizer as mo
import types

class bell_optimizer(mo.multiple_optimizer):
    def __init__(self, name):
        mo.multiple_optimizer.__init__(self, name)
       
        ins_pars  = {'min_starts'         :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET},
                    'min_cr_checks'       :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET},
                    'min_cr_counts_gate'  :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET},
                    'min_yellow_counts'   :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET},
                    'min_cr_counts_opt_nf':   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET},
                    'rejecter_step'       :   {'type':types.FloatType,'flags':Instrument.FLAG_GETSET}, 
                    }           
        instrument_helper.create_get_set(self,ins_pars)

        self.add_parameter('sec_cal_a',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='W',
                           minval=0,maxval=1.0)
        
        self.add_function('optimize_nf')     
        self.add_function('optimize_gate')
        self.add_function('optimize_yellow') 
        self.add_function('pid_e_primer_stop')
        self.add_function('pid_e_primer_start')
        self.add_function('pidgate_start')
        self.add_function('pidgate_stop')
        self.add_function('pidyellowfrq_start')
        self.add_function('pidyellowfrq_stop')
        self.add_function('rejecter_half_plus')
        self.add_function('rejecter_half_min')
        self.add_function('rejecter_quarter_plus')
        self.add_function('rejecter_quarter_min')

        self._mode = 'check_starts'
        self._mode_rep = 0

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
        for p in params_from_cfg:
                self.set(p, value=self.ins_cfg.get(p))

    def save_cfg(self):
        for param in self.get_parameter_names():
            value = self.get(param)
            self.ins_cfg[param] = value
            

    #--------------get_set        
    
    def check(self):
        if self._mode == 'check_starts':
            #print self._mode
            st1=qt.instruments['physical_adwin'].Get_Par(73)
            cr1= qt.instruments['physical_adwin'].Get_Par(72)
            qt.msleep(1)
            st2=qt.instruments['physical_adwin'].Get_Par(73)
            cr2 = qt.instruments['physical_adwin'].Get_Par(72)

            th = qt.instruments['physical_adwin'].Get_Par(75)
            if st2-st1<self.get_min_starts() and cr2-cr1 > self.min_cr_checks() and qt.instruments['gate_optimizer'].get_value() < self.min_cr_counts_gate() and th < 1000:
                print 'JUMP DETECTED! {} starts per second'.format(st2-st1)
                self._mode == 'jump_recover-0'
                self._mode_rep = 0
            else:
                print 'number of starts ok'
        elif self._mode == 'jump_recover-0':
            print self._mode, self._mode_rep
            self._mode_rep += 1
            self.optimize_gate()
            if qt.instruments['gate_optimizer'].get_last_max() > self.min_cr_counts_gate() or self._mode_rep > 2:
                self._mode == 'jump_recover-1'
                self._mode_rep = 0
            self.start_waiting(5)
        elif self._mode == 'jump_recover-1':
            print self._mode, self._mode_rep
            self._mode_rep += 1
            self.optimize_yellow()
            if qt.instruments['yellowfrq_optimizer'].get_last_max() > self.min_counts_yellow() or self._mode_rep > 2:
                self._mode == 'jump_recover-2'
                self._mode_rep = 0
            self.start_waiting(5)
        elif self._mode == 'jump_recover-2':
            print self._mode, self._mode_rep
            self._mode_rep += 1
            if qt.instruments['gate_optimizer'].get_value() > self.get_min_cr_counts_opt_nf:
                self.optimize_nf()
                mode = 'check_starts'
                self.start_waiting(5)
            else:
                mode = 'jump_recover-0'
        else:
            print 'Unknown mode:', self._mode
            return False

        return True

    def optimize_nf(self):
        self.pid_e_primer_stop()
        qt.instruments['nf_optimizer'].optimize()
        qt.msleep(2.5)
        self.pid_e_primer_start()

    def optimize_yellow(self):
        self.pidyellowfrq_stop()
        qt.instruments['yellowfrq_optimizer'].optimize()
        qt.msleep(2.5)
        self.pidyellowfrq_start()

    def optimize_gate(self):
        self.pidgate_stop()
        qt.instruments['gate_optimizer'].optimize()
        qt.msleep(0.5)
        self.pidgate_start()

    def pid_e_primer_stop(self):
        qt.instruments['e_primer'].stop()
    def pid_e_primer_start(self):
        qt.instruments['e_primer'].start()

    def pidyellowfrq_stop(self):
        qt.instruments['pidyellowfrq'].stop()
    def pidyellowfrq_start(self):
        qt.instruments['pidyellowfrq'].start()

    def pidgate_stop(self):
        qt.instruments['pidgate'].stop()
    def pidgate_start(self):
        qt.instruments['pidgate'].start()

    def rejecter_half_plus(self):
        qt.instruments['rejecter'].move('zpl_half',self.get_rejecter_step(),quick_scan=True)

    def rejecter_half_min(self):
        qt.instruments['rejecter'].move('zpl_half',-self.get_rejecter_step(),quick_scan=True)

    def rejecter_quarter_plus(self):
        qt.instruments['rejecter'].move('zpl_quarter',self.get_rejecter_step(),quick_scan=True)

    def rejecter_quarter_min(self):
        qt.instruments['rejecter'].move('zpl_quarter',-self.get_rejecter_step(),quick_scan=True)
