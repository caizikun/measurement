# Convex optimizor
#
# author: Bas Hensen 2013

from instrument import Instrument
import types
import qt
import msvcrt
import instrument_helper
import numpy as np
from scipy import optimize

class convex_optimiz0r(Instrument):

    def __init__(self, name, mos_ins=qt.instruments['master_of_space'],
            adwin_ins=qt.instruments['adwin']):
        Instrument.__init__(self, name)

        self.add_function('optimize')
        self.mos = mos_ins
        self.adwin= adwin_ins

    def _measure_at_position(self, pos, int_time, cnt, speed, use_countrates=False):
        self.mos.move_to_xyz_pos(('x','y','z'),pos,speed,blocking=True)
        qt.msleep(0.001)
        if use_countrates:
            return self.adwin.get_countrates()[cnt-1]
        return self.adwin.measure_counts(int_time)[cnt-1]

    def optimize(self, xyz_tolerance=0.001, max_cycles=15, 
                  cnt=1, int_time=50, speed=2000, use_countrates=False,
                  do_final_countrate_check=True, method='simplex', **kw):

        pos = np.array([self.mos.get_x(), self.mos.get_y(), self.mos.get_z()])
        old_cnt = self.adwin.measure_counts(int_time)[cnt-1]

        def f(pos):
            return -1*self._measure_at_position(pos,int_time,cnt,speed,use_countrates)

        if method == 'fmin':
            new_pos = optimize.fmin(f,pos,maxfun=max_cycles, xtol=xyz_tolerance, retall=False, **kw)
        elif method == 'fmin-powell':
            new_pos = optimize.fmin_powell(f,pos,maxfun=max_cycles, xtol=xyz_tolerance, retall=False, **kw)
        else:
            print 'unknown optiisation method'
            new_pos=pos

        if do_final_countrate_check:
          print "Proposed position x change %d nm" % \
                        (1000*new_pos[0]-1000*pos[0])
          print "Proposed position y change %d nm" % \
                        (1000*new_pos[1]-1000*pos[1])
          print "Proposed position z change %d nm" % \
                        (1000*new_pos[2]-1000*pos[2])
          new_cnt = self._measure_at_position(new_pos, int_time, cnt, speed/2.)
          print 'Old countrates', old_cnt/(int_time/1000.)
          print 'New countrates', new_cnt/(int_time/1000.)
          if new_cnt>old_cnt:
            print 'New position accepted'
          else:
            print 'Old position kept'
            self.mos.move_to_xyz_pos(('x','y','z'),pos,speed,blocking=True)

        else:
          print "Position x changed %d nm" % \
                          (1000*new_pos[0]-1000*pos[0])
          print "Position y changed %d nm" % \
                          (1000*new_pos[1]-1000*pos[1])
          print "Position z changed %d nm" % \
                          (1000*new_pos[2]-1000*pos[2])
          print 'Old countrates', old_cnt/(int_time/1000.)
          print  "Countrates at new position: %d" % \
                      (float(self._measure_at_position(new_pos, int_time,cnt, speed))/(int_time/1000.))
