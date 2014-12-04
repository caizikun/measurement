# cyclopean_cavity_laser_scan.py
#
# auto-created by ui2cyclops.py v20110215, Thu Dec 04 14:07:42 2014

from instrument import Instrument
from cyclopean_instrument import CyclopeanInstrument
import types

class cyclopean_cavity_laser_scan(CyclopeanInstrument):
    def __init__(self, name, address=None):
        CyclopeanInstrument.__init__(self, name, tags=[])

        self._supported = {
            'get_running': False,
            'get_recording': False,
            'set_running': False,
            'set_recording': False,
            'save': False,
            }

        self.add_parameter('doubleSpinBox_start_F',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='',
                           minval=0.0,
                           maxval=99.0,
                           doc='')
        self._doubleSpinBox_start_F = 0.0

        self.add_parameter('doubleSpinBox_stop_f',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='',
                           minval=0.0,
                           maxval=99.0,
                           doc='')
        self._doubleSpinBox_stop_f = 0.0

        self.add_parameter('doubleSpinBox_step_f',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='',
                           minval=0.0,
                           maxval=99.0,
                           doc='')
        self._doubleSpinBox_step_f = 0.0

        self.add_parameter('doubleSpinBox_coarse_wav',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='',
                           minval=0.0,
                           maxval=99.0,
                           doc='')
        self._doubleSpinBox_coarse_wav = 0.0

        self.add_parameter('doubleSpinBox_int_time',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='',
                           minval=0.0,
                           maxval=99.0,
                           doc='')
        self._doubleSpinBox_int_time = 0.0

        self.add_function('start_scan_button')

        self.add_function('stop_scan_button')

        self.add_function('save_scan_button')

    def do_get_doubleSpinBox_start_F(self):
        return self._doubleSpinBox_start_F

    def do_set_doubleSpinBox_start_F(self, val):
        self._doubleSpinBox_start_F = val

    def do_get_doubleSpinBox_stop_f(self):
        return self._doubleSpinBox_stop_f

    def do_set_doubleSpinBox_stop_f(self, val):
        self._doubleSpinBox_stop_f = val

    def do_get_doubleSpinBox_step_f(self):
        return self._doubleSpinBox_step_f

    def do_set_doubleSpinBox_step_f(self, val):
        self._doubleSpinBox_step_f = val

    def do_get_doubleSpinBox_coarse_wav(self):
        return self._doubleSpinBox_coarse_wav

    def do_set_doubleSpinBox_coarse_wav(self, val):
        self._doubleSpinBox_coarse_wav = val

    def do_get_doubleSpinBox_int_time(self):
        return self._doubleSpinBox_int_time

    def do_set_doubleSpinBox_int_time(self, val):
        self._doubleSpinBox_int_time = val

    def start_scan_button(self, *arg, **kw):
        pass

    def stop_scan_button(self, *arg, **kw):
        pass

    def save_scan_button(self, *arg, **kw):
        pass

    def save(self, meta=""): # inherited doesn't do any saving. Implement.
        CyclopeanInstrument.save(self, meta)

        return

    def _start_running(self):
        CyclopeanInstrument._start_running(self)

        return

    def _stop_running(self):
        CyclopeanInstrument._start_running(self)

        return

    def _sampling_event(self):
        return True # sampling timer runs until return value of this is False
