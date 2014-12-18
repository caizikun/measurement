# optimize on a spot in 1D
# 
# FIXME: ATM, the dimension corresponds to a single dimension of
# the position master. should be generalized to arbitrary lines in space!
#
#
# autor: wolfgang pfaff <w dot pfaff at tudelft dot nl>

from instrument import Instrument
from cyclopean_instrument import CyclopeanInstrument

import types
from time import sleep
import logging
from numpy import array
from numpy import zeros

from analysis.lib.fitting import fit,common
import qt

#class OptimizeProcess(threading.Thread):
#
#    def run(self):
#        ins = qt.instruments['opt1d_counts']
#        linescan = qt.instruments['linescan_counts']
#	print('starting linescan')
#        linescan.set_is_running(True)
#	print('linescan ended')
#        qt.msleep(0.1)
#        while linescan.get_is_running():
#             qt.msleep(0.1)
#
#        return	

        
class optimize1d_counts(CyclopeanInstrument):
    def __init__(self, name, linescan, mos, counters):
        CyclopeanInstrument.__init__(self, name, tags=[])

        self._linescan = qt.instruments[linescan]
        self._mos = qt.instruments[mos]
        self._counters = qt.instruments[counters]
        self._counter_was_running = False
        
        self.add_parameter('dimension',
                type=types.StringType,
                flags=Instrument.FLAG_GETSET)
        
        self.add_parameter('scan_length',
                           type = types.FloatType,
                           flags = Instrument.FLAG_GETSET,
                           units = 'um',)

        self.add_parameter('pixel_time',
                           type = types.FloatType,
                           flags = Instrument.FLAG_GETSET,
                           units = 'ms',) 

        self.add_parameter('nr_of_points',
                           type = types.IntType,
                           flags = Instrument.FLAG_GETSET, )

        self.add_parameter('gaussian_fit',
                           type = types.BooleanType,
                           flags = Instrument.FLAG_GETSET, )

        self.add_parameter('fit_error',
                           type = types.ListType,
                           flags = Instrument.FLAG_GET,)

        self.add_parameter('fit_result',
                           type = types.ListType,
                           flags = Instrument.FLAG_GET,)

        self.add_parameter('opt_pos',
                           type = types.FloatType,
                           flags = Instrument.FLAG_GET,)

        self.add_parameter('counter',
                           type = types.IntType,
                           flags = Instrument.FLAG_GETSET, )

        self.add_parameter('points',
                           type = types.ListType,
                           flags = Instrument.FLAG_GET, )


        ### public functions
        self.add_function('run')

        # set defaults
        self._scan_length = 1.
        self._nr_of_points = 21 
        self._pixel_time = 10
        self._gaussian_fit = True
        self._fit_error = []
        self._fit_result = []
        self._opt_pos = 0.
        self._counter = 1
        self._fitdata = []
        self._points = []
        self._busy = False
        self._dimension = 'x'
    
    def get_all(self):
        for n in self.get_parameter_names():
            self.get(n)
        
    # get and set functions
    def do_get_dimension(self):
        return self._dimension

    def do_set_dimension(self, val):
        self._dimension = val    

    def do_get_scan_length(self):
        return self._scan_length

    def do_set_scan_length(self, val):
        self._scan_length = val

    def do_get_nr_of_points(self):
        return self._nr_of_points

    def do_set_nr_of_points(self, val):
        self._nr_of_points = val

    def do_get_gaussian_fit(self):
        return self._gaussian_fit

    def do_set_gaussian_fit(self, val):
        self._gaussian_fit = val

    def do_get_counter(self):
        return self._counter

    def do_set_counter(self, val):
        self._counter = val

    def do_get_pixel_time(self):
        return self._pixel_time

    def do_set_pixel_time(self, val):
        self._pixel_time = val

    def do_get_fit_error(self):
        return self._fit_error

    def do_get_fit_result(self,):
        return self._fit_result

    def do_get_opt_pos(self):
        return self._opt_pos

    def do_get_points(self):
        return self._points


    # blocking, for usage in scripts, etc.
    def run(self, **kw):
        self._dimension = kw.pop('dimension', self._dimension)
        self._scan_length = kw.pop('scan_length', self._scan_length)
        self._nr_of_points = kw.pop('nr_of_points', self._nr_of_points)
        self._gaussian_fit = kw.pop('gaussian_fit', self._gaussian_fit)
        self._counter = kw.pop('counter', self._counter)
        self._pixel_time = kw.pop('pixel_time', self._pixel_time)
        self.get_dimension()
        self.get_scan_length()
        self.get_nr_of_points()
        self.get_gaussian_fit()
        self.get_counter()
        self.get_pixel_time()
        
        self._prepare()
       
        while self._linescan.get_is_running():
            qt.msleep(0.1)
        
        self._linescan.set_is_running(True)
        qt.msleep(0.5)
        
        while self._linescan.get_is_running():
            qt.msleep(0.1)
        
        return self._process_fit(**kw)
    
    ### internal functions
    def _start_running(self):
        CyclopeanInstrument._start_running(self)
        self._prepare()
        self._linescan.set_is_running(True)
        qt.msleep(0.1)
        while self._linescan.get_is_running():
            qt.msleep(0.1)
        return self._process_fit()
        
        #self._OptimizeProcess()
        #self._o = OptimizeProcess()
        #self._o.start()

    def _stop_running(self):
        if self._counter_was_running:
            self._counters.set_is_running(True)
            self._counter_was_running = False
	    self._process_fit()
	    self._save()

    def _sampling_event(self):
        if not self._is_running:
            return False
        
        if hasattr(self, '_o'):
            if self._o.is_alive():
                return True
            else:
                self.set_is_running(False)
                return False

        return True
    
    def _prepare(self):
        print '(%s) run optimize...' % self._dimension
	    
        dimname=self._dimension
        self._opt_pos = getattr(self._mos, 'get_'+self._dimension)()
        self._opt_pos_prev = getattr(self._mos, 'get_'+self._dimension)()
        l = self._scan_length
        self._x0, self._x1 = self._opt_pos - l/2., self._opt_pos + l/2.
        self._linescan.set_dimensions([self._dimension])
        self._linescan.set_starts([self._x0])
        self._linescan.set_stops([self._x1])
        self._linescan.set_steps(self._nr_of_points)
        self._linescan.set_px_time(self._pixel_time)
        # self._mos.set(self._dimension, value=self._x0)
        # self._mos.move_to_xyz_pos([self._dimension],[self._x0])

        # print self._dimension

    
    def _process_fit(self, **kw):
        #print('Get the data')
        return_position_change = kw.pop('return_position_change', False)
        self.set_data('points', self._linescan.get_points()[0])
        qt.msleep(0.1)
        self.set_data('countrates', self._linescan.get_data('countrates')\
                [self._counter-1])
        qt.msleep(0.1)


        self.reset_data('fit', (self._nr_of_points))

        # first get the optimal position in the first dimension and go there
        cr = self._data['countrates']
        p = self._data['points']

        # starting point for the optimization is the maximum of the signal
        i = cr.tolist().index(max(cr))
        self._opt_pos = p[i]
        ret = True
        
        if self._dimension=='z':
            sigma=0.5
        else:
            sigma=0.1

        if self._gaussian_fit:
            gaussian_fit = fit.fit1d(p, cr,common.fit_gauss, array(cr).min(), 
                    array(cr).max(), p[i], sigma, do_print=False,ret=True)
           
            if type(gaussian_fit) != dict:
                self.set_data('fit', zeros(len(p)))
                self._fit_result = False
                self._fit_error = False
                ret = False
                print '(%s) fit failed! Set to maximum.' % self.get_name()
                self._opt_pos = p[cr.tolist().index(max(cr))]

            else:
            
                if gaussian_fit['success'] != False:
                    self.set_data('fit', gaussian_fit['fitfunc'](p))
                    self._fit_result = [gaussian_fit['params'][1], 
                            gaussian_fit['params'][2], 
                            gaussian_fit['params'][3],
                            gaussian_fit['params'][0] ]
                    self._fit_error = [gaussian_fit['error'][1],
                            gaussian_fit['error'][2],
                            gaussian_fit['error'][3],
                            gaussian_fit['error'][0] ]
                    self._opt_pos = self._fit_result[0]
                    ret = True
                    print '(%s) optimize succeeded!' % self.get_name()

                
                else:
                    self.set_data('fit', zeros(len(p)))
                    self._fit_result = False
                    self._fit_error = False
                    ret = False
                    print '(%s) optimize failed!' % self.get_name()
                    if array(cr).max() == 0.:
                        print 'no counts in linescan'
                        self._opt_pos = self._opt_pos_prev
                    else:
                        self._opt_pos = p[cr.tolist().index(max(cr))]
            
            self.get_fit_result()

        if array(p).min() < self._opt_pos < array(p).max():
            self._mos.set(self._dimension, value=self._opt_pos)
        else:
            self._mos.set(self._dimension, value=p[cr.tolist().index(max(cr))])
            print'Optimum outside scan range: Position is set to local maximum'

        print "Position changed %d nm" % \
                        (self._opt_pos*1E3-self._opt_pos_prev*1E3)
        if ret and return_position_change:
            return (self._opt_pos*1E3-self._opt_pos_prev*1E3)
        return ret

