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

class xy_scan_jpe(CyclopeanInstrument):
    def __init__(self, name, point_manager, *arg, **kw):
        """
        Parameters:
            adwin : string
                qtlab-name of the adwin instrument to be used
            mos : string
                qtlab-name of the master of space to be used
        """
        CyclopeanInstrument.__init__(self, name, tags=['measure'])

        # related instruments: do I need to know about adwin and moc, here???
        #self._adwin = qt.instruments[adwin] #used only for counts
        #self._moc = qt.instruments[moc] #master_of_cavity, controls jpe motion (both actual jpe and jpe_tracker)
        self._point_mngr = qt.instruments[point_manager]
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

        self.set_xsteps(1)
        self.set_ysteps(1)
        self.set_xstart(0)
        self.set_ystart(0)
        self.set_xstop(0)
        self.set_ystop(0)
        self.set_z_pos_spin_box(0)
        self.set_px_time(1)

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

    def do_get_scan_value(self):
        return self._scan_value

    def do_set_scan_value(self, val):
        self._scan_value = val

    # public functions
    def get_points(self):
        return self._points

    def stop_scan(self):
        print 'Stop scan!'

    def start_scan(self):
        print 'Start scan!'

    def set_xstart(self, val):
        self._x_start = val

    def set_xsteps(self, val):
        self._x_steps = val 

    def set_xstop(self, val):
        self._x_stop = val

    def set_ystart(self, val):
        self._y_start = val

    def set_ysteps(self, val):
        self._y_steps = val

    def set_ystop(self, val):
        self._y_stop = val

    def set_z_pos_spin_box(self, val):
        self._z_pos = val

    def set_px_time (self, val):
        self._px_time = val

    def get_xstart(self):
        return self._x_start

    def get_xsteps(self):
        return self._x_steps

    def get_xstop(self):
        return self._x_stop

    def get_ystart(self):
        return self._y_start

    def get_ysteps(self):
        return self._y_steps

    def get_ystop(self):
        return self._y_stop

    def get_z_pos_spin_box(self):
        return self._z_pos 

    def get_pxtime (self):
        return self._px_time

    # internal functions
    def _start_running(self):

        CyclopeanInstrument._start_running(self)

        ## initalize data field and set current status (i.e, empty)
        #pts = zeros((self._x_steps, self._y_steps))
        self._max_points = self._x_steps*self._y_steps
        self._current_point = 0 
        self._curr_x_point = 0
        self._curr_y_line = 0
        #2D scan is performed along a meander path to minimize movement
        self.y_vals = linspace (self._y_start, self._y_stop,self._y_steps)
        self.curr_z = self._z_pos

        # hook up linescanner changes
        self._point_mngr.connect('changed', self._point_update)

        # now start the actual scanning
        self._next_point()   

    def _sampling_event(self):
        if not self._is_running:
            return False
        
        if self._point_mngr.get_is_running():
            return True
        else:
            # if point_mngr is not running move to next point or stop (if 2D scan is done)
            #self._point_finished()
            self._check_new_data()

            if not self._point_mngr.get_is_running():
                if (self._current_point < self._max_points):
                    self._next_point()
                else:
                    return False
            #    self.set_is_running = False
        ## THIS GUY SHOULD MANAGE THE 2D SCAN!!!!!



    def _check_new_data(self):
        self._new_data = self._point_mnge._new_data()

    '''
    def _mos_changed(self, unused, changes, *arg, **kw):
        for c in changes:
            if c == 'linescan_px_clock':
                self._px_clock_set(changes[c])

            if c == 'linescan_running':
                self._linescan_running_changed(changes[c])
    '''

    def _px_clock_set(self, px_clock):
        if self._px_clock >= px_clock:
            return
        else:
            self._px_clock = px_clock
            self._px_clock_changed(px_clock)

    def _point_running_changed(self, running):
        if not running:
            self._point_finished()
            self.set_is_running(False)

    # inherit in child classes for real functionality
    def _px_clock_changed(self, px_clock):
        pass

    def _scan_finished(self):
        pass

    def _point_finished(self):
        pass

    def _point_update(self, unused, changes, *arg, **kw):
        pass

    def _next_point(self):

        self._current_point += 1
        self._curr_x_point += 1

        if (self._curr_x_point > self._x_steps):
            self._curr_x_point = 0
        #for the first point of the line, check whether you want to scan forward or backward (meander path)
        if (self._curr_x_point == 0):
            self._curr_y_line += 1
            if mod(self._curr_y_line,2)==0:
                self.x_vals = linspace (self._x_start, self._x_stop, self._x_steps)
            else:
                self.x_vals = linspace (self._x_stop, self._x_start, self._x_steps)
        if (self._curr_y_line < self._y_steps): ##IS THIS OK?
            x = self.x_vals[self._curr_x_point]
            y = self.y_vals[self._curr_y_line]
            self._point_mngr.set_coordinates (x=x,y=y,z=self._z_pos)
            self._point_mngr.set_px_time()
            self._point_mngr.set_is_running(True)
            return True
        else:
            self._point_mngr.set_is_running(False)
            return False


