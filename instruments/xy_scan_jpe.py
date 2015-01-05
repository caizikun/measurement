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

        self.set_xsteps(1)
        self.set_ysteps(1)
        self.set_xstart(0)
        self.set_ystart(0)
        self.set_xstop(0)
        self.set_ystop(0)
        self.set_z_pos_spin_box(0)
        self.set_px_time(1)
        #self.set_dimensions(())
        #self.set_starts(())
        #self.set_stops(())
        #self.set_scan_value('counts')

        # other vars
        self._px_clock = 0

        self._supported = {
            'get_running': True,
            'get_recording': False,
            'set_running': False,
            'set_recording': False,
            'save': False,
            }

    #def do_get_dimensions(self):
    #    return self._dimensions

    #def do_set_dimensions(self, val):
    #    self._dimensions = val

    #def do_get_starts(self):
    #    return self._starts

    #def do_set_starts(self, val):
    #    self._starts = val

    #def do_get_stops(self):
    #    return self._stops

    #def do_set_stops(self, val):
    #    self._stops = val

    #def do_get_steps(self):
    #    return self._steps

    #def do_set_steps(self, val):
    #    self._steps = val

    #def do_get_px_time(self):
    #    return self._px_time

    def do_set_px_time(self, val):
        self._px_time = val

    def do_get_scan_value(self):
        return self._scan_value

    def do_set_scan_value(self, val):
        self._scan_value = val

    # public functions
    def get_points(self):
        return self._points

    # internal functions
    def _start_running(self):
        CyclopeanInstrument._start_running(self)

        # determine points of the line
        #self._points = zeros((self_, self._steps)) #points for xy scan

        #for i,d in enumerate(['x', 'y']):
    	#    self._points[i,:] = linspace(self._starts[i], self._stops[i],self._steps)

        if not self._manage_2D_scan():
            self.set_is_running (False)

        # start the linescan
        #if not self._mos.linescan_start(self._dimensions, self._starts, 
        #        self._stops, self._steps, self._px_time, 
        #        value=self._scan_value):
        #    self.set_is_running(False)
   

    def _manage_2D_scan(self):
        #2D scan is performed following a meander to minimize 
        self.y_vals = linspace (self._y_start, self._y_stop,self._y_steps)
        self.curr_z = self._z_pos
        stop_scan = False
        i = -1
        for y in self.vals:
            i = i+1
            self.curr_y = y
            if mod(i,2)==0:
                self.x_vals = linspace (self._x_start, self._x_stop, self._x_steps)
            else:
                self.x_vals = linspace (self._x_stop, self._x_start, self._x_steps)
            linescan_vals = zeros(self._x_steps)
            for ind, x in enumerate(self.x_vals):
                self.curr_x = x
                #self._moc.move_to_xyz (x=curr_x, y=curr_y, z=curr_z, verbose=False)
                print "Moving to: ", self.curr_x, self.curr_y, self.curr_z
                counts = 0#self._adwin.###GET_COUNTS??####
                linescan_vals[ind] = counts

                if not self._sampling_event():
                    stop_scan = True

                if stop_scan:
                    break
            if stop_scan:
                break
        return True

    def _sampling_event(self):
        if self.get_is_running():
            return True
        else:
            return False
    
    def _mos_changed(self, unused, changes, *arg, **kw):
        for c in changes:
            if c == 'linescan_px_clock':
                self._px_clock_set(changes[c])

            if c == 'linescan_running':
                self._linescan_running_changed(changes[c])

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
