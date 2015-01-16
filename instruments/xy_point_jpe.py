# line scanner that controls position and obtains counts via the adwin
#
# Author: Wolfgang Pfaff <w dot pfaff at tudelft dot nl>

from instrument import Instrument
from cyclopean_instrument import CyclopeanInstrument
import qt
from qt import msleep
import types
import time
from numpy import *

class xy_point_jpe(CyclopeanInstrument):
    def __init__(self, name, adwin, moc, *arg, **kw):
        """
        Parameters:
            adwin : string
                qtlab-name of the adwin instrument to be used
            mos : string
                qtlab-name of the master of space to be used
        """
        CyclopeanInstrument.__init__(self, name, tags=['measure'])

        # related instruments
        self._adwin = qt.instruments[adwin] #used only for counts
        self._moc = qt.instruments[moc] #master_of_cavity, controls jpe motion (both actual jpe and jpe_tracker)
        self._scan_value = 'counts'

        # connect the mos to monitor methods
        #self._mos.connect('changed', self._mos_changed) #THIS NEEDS TO BE DONE FOR moc????

        '''
        # params that define the linescan
        self.add_parameter('dimensions', 
                type=types.TupleType,
                flags=Instrument.FLAG_GETSET,
                doc="""Sets the names of the dimensions involved, as specified
                in the master of space""")

        self.add_parameter('starts',
                type=types.TupleType,
                flags=Instrument.FLAG_GETSET)

        self.add_parameter('stops',
                type=types.TupleType,
                flags=Instrument.FLAG_GETSET)
 
        self.add_parameter('steps',
                type=types.IntType,
                flags=Instrument.FLAG_GETSET)

        self.add_parameter('px_time',
                type=types.IntType,
                flags=Instrument.FLAG_GETSET,
                units='ms')

        self.add_parameter('scan_value',
                type=types.StringType,
                flags=Instrument.FLAG_GETSET)
        '''
        self.add_function('get_points')

        self._points = ()

        self.set_x(0)
        self.set_y(0)
        self.set_z(0)
        self.do_set_px_time(1)

        # other vars
        self._px_clock = 0

        self._supported = {
            'get_running': True,
            'get_recording': False,
            'set_running': False,
            'set_recording': False,
            'save': False,
            }


    def do_set_px_time(self, val):
        self._px_time = val

    # public functions
    def get_points(self):
        return self._points

    # internal functions
    def _start_running(self):
        CyclopeanInstrument._start_running(self)
        if not self._move_to_position_and_count():
            self.set_is_running = False

    def _move_to_position_and_count():
        #moc.####MOVE####
        #adwin.###COUNT####
        print 'Moving to position!!'
        return False

    def set_coordinates(x,y,z):
        pass


    def _new_data(self):
        pass

    def _sampling_event(self):
        if self.get_is_running():
            return True
        else:
            return False
    
    def _px_clock_set(self, px_clock):
        if self._px_clock >= px_clock:
            return
        else:
            self._px_clock = px_clock
            self._px_clock_changed(px_clock)

    def _linescan_running_changed(self, running):
        if not running:
            self._linescan_finished()
            self.set_is_running(False)

    # inherit in child classes for real functionality
    def _px_clock_changed(self, px_clock):
        pass

    def _linescan_finished(self):
        pass

    def stop_scan(self):
        print 'Stop scan!'

    def start_scan(self):
        print 'Start scan!'

    def set_x(self, val):
        self._x = val

    def set_y(self, val):
        self._y = val

    def set_z(self, val):
        self._z = val

    def set_pxtime (self, val):
        self._px_time = val

    def get_x(self):
        return self._x 

    def get_y(self):
        return self._y

    def get_z(self):
        return self._z 

    def get_pxtime (self):
        return self._px_time
