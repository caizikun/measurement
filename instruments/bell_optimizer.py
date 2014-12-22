import qt
import os
from instrument import Instrument
import numpy as np
import instrument_helper
from lib import config
import multiple_optimizer as mo
reload(mo)
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
        for p in self._parlist:
                self.set(p, value=self.ins_cfg.get(p))

    def save_cfg(self):
        for param in self._parlist:
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
                print '-'*20
                print '-'*20
                #self._mode == 'jump_recover-0'
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
