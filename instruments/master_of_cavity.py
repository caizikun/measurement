#####################################################################################################
# CONTROLLER for JPE actuator    --- Cristian Bonato, 2014  --- cbonato80@gmail.com
# 
# 'master_of_cavity' (MOC) controls 3-axes motion of the positioning stage, taking care
#  of conversion from xyz position to splindle movement. MOC includes a _jpe_cadm instrument,
#  who physically talks to the JPE controller, and a _jpe_tracker, who keeps track of the 
#  spindles' positions. 
#  SvD: for functioning of the instrument with remote access, I am putting the JPE_pos_tracker
#  inside the master_of_cavity Instrument. I think there is no need to have it in a separate class.
#
#  To keep track of spindle length over time, avoiding end-of-range issues (in absence of
#  optical tracking mechanism), splindle lengths are saved in a file (/lib/config/jpe_tracker.cfg),
#  which is continuously updated. Maximum spindle range is stored in _jpe_tracker.max_spindle_steps
#  and a warning is given when approaching this limit.
#
#  Please run MOC.close() before quitting, to close the tracker file
#####################################################################################################

import os
from instrument import Instrument
from cyclopean_instrument import CyclopeanInstrument
import qt
import time
import types
import gobject
import numpy as np
from lib import config
from measurement.lib.config import moc_cfg

                    
class master_of_cavity(CyclopeanInstrument):

    def __init__(self, name, jpe, adwin, use_cfg = False, **kw):
        Instrument.__init__(self, name)

        print 'Initializing master_of_cavity... '

        self.add_parameter('address',
                flags = Instrument.FLAG_GETSET,
                type = types.IntType)
        self.address= 1

        self.add_parameter('temperature',
                flags = Instrument.FLAG_GETSET,
                units = 'K',
                type = types.IntType, 
                minval = 0, maxval = 300)
        self.temperature = 300

        self.add_parameter('freq',
                flags = Instrument.FLAG_GETSET,
                units = 'Hz',
                type = types.IntType, 
                minval = 0, maxval = 600)
        self.freq = 100

        self.add_parameter('rel_step_size',
                flags = Instrument.FLAG_GETSET,
                units = '%',
                type = types.IntType, 
                minval = 0, maxval = 100)
        self.rel_step_size = 30

        self.add_parameter('track_curr_x',
                type = types.FloatType,
                flags = Instrument.FLAG_GET, 
                units = 'nm')
        self.add_parameter('track_curr_y',
                type = types.FloatType,
                flags = Instrument.FLAG_GET, 
                units = 'nm')
        self.add_parameter('track_curr_z',
                type = types.FloatType,
                flags = Instrument.FLAG_GET, 
                units = 'nm')

        self.addr = 1
        self.ch_x = 1
        self.ch_y = 2
        self.ch_z = 3
        self._jpe_cadm = qt.instruments[jpe]
        # self._jpe_tracker = JPE_pos_tracker(reinit_spindles=False)
        self._step_size = None
        self.ins_adwin = qt.instruments[adwin]
        self._fine_piezo_V = None
        self.set_fine_piezo_voltages (0,0,0)

        # Init that was originally in the JPE_pos_tracker.
        # all coordinates are in mm, angles in radians
        # the number of spindle rotations for z1,z2,z3
        self.track_z1 = 0
        self.track_z2 = 0
        self.track_z3 = 0

        #design properties in mm (see JPE datasheet).
        self.cfg_pars = moc_cfg.config['moc_cav1']
        self.fiber_z_offset = self.cfg_pars['fiber_z_offset'] #fiber offset with respect to fiber interface
        self.h = self.cfg_pars['h_mm']+self.fiber_z_offset#33.85+self.fiber_z_offset
        self.R = self.cfg_pars['R_mm']#14.5
        self.max_spindle_steps = self.cfg_pars['max_spindle_steps']

        #Cartesian coordinates in the lab-frame (mm)
        self.track_curr_x = 0
        self.track_curr_y = 0
        self.track_curr_z = 0
        self.track_v_piezo_1 = None
        self.track_v_piezo_2 = None
        self.track_v_piezo_3 = None       
        self.tracker_file_name = 'D:\measuring\measurement\config\jpe_tracker.npz'

        reinit_spindles = kw.pop('reinit_spindles', False)
        if reinit_spindles:         
            self.reset_spindle_tracker()
        else:
            print 'Tracker initialized from file...'
            self.tracker_file_readout()

        #variable properties are saved in the cfg file 
        if use_cfg:
            cfg_fn = os.path.join(qt.config['ins_cfg_path'], name+'.cfg')
            if not os.path.exists(cfg_fn):
                _f = open(cfg_fn, 'w')
                _f.write('')
                _f.close()        
            self.ins_cfg = config.Config(cfg_fn)   # this uses awesome QT lab properties, 
            #that automatically saves the config file when closing qtlab. I think, at least... #test it
            self.load_cfg()
            self.save_cfg()

        # remote access functions:
        self.add_function('get_params')
        self.add_function('get_track_z')
        self.add_function('status')
        #position control function
        self.add_function('step')
        self.add_function('set_as_origin')
        self.add_function('move_to_xyz')    
        self.add_function('set_fine_piezo_voltages')
        self.add_function('move_spindle_steps')

    ### config management
    def load_cfg(self):
        params = self.ins_cfg.get_all()
        if 'temperature' in params:
            self.set_temperature(params['temperature'])
            print 'JPE temperature set to ', params['temperature']
        if 'freq' in params:
            self.set_freq(params['freq'])
        if 'rel_step_size' in params:
            self.set_rel_step_size(params['rel_step_size'])
        # if 'z1' in params:
        #     self.track_z1 = z1
        # if 'z2' in params:
        #     self.track_z2 = z2
        # if 'z3' in params:
        #     self.track_z3 = z3
        # if 'curr_x' in params:
        #     self.track_curr_x = curr_x
        # if 'curr_y' in params:
        #     self.track_curr_x = curr_y        
        # if 'curr_z' in params:
        #     self.track_curr_x = curr_z

    def save_cfg(self):
        self.ins_cfg['temperature'] = self.temperature
        self.ins_cfg['freq'] = self.freq
        self.ins_cfg['rel_step_size'] = self.rel_step_size
        self.ins_cfg['z1'] = self.track_z1
        self.ins_cfg['z2'] = self.track_z2
        self.ins_cfg['z3'] = self.track_z3
        self.ins_cfg['curr_x'] = self.track_curr_x
        self.ins_cfg['curr_y'] = self.track_curr_y
        self.ins_cfg['curr_z'] = self.track_curr_z

    def tracker_file_update(self): #originally from jpe_tracker
        '''
        Function that updates the tracker file. Originally in JPE_tracker
        '''
        # self.ins_cfg['z1'] = self.track_z1
        # self.ins_cfg['z2'] = self.track_z2
        # self.ins_cfg['z3'] = self.track_z3
        # self.ins_cfg['curr_x'] = self.track_curr_x
        # self.ins_cfg['curr_y'] = self.track_curr_y
        # self.ins_cfg['curr_z'] = self.track_curr_z
        try:
            np.savez (self.tracker_file_name, z1= self.track_z1, z2=self.track_z2, z3=self.track_z3, x=self.track_curr_x, y=self.track_curr_y, z=self.track_curr_z)
        except:
            print 'Tracker file update failed!'

    def tracker_file_readout(self):
        '''
        Function that updates the tracker file. Originally in JPE_tracker.
        Output: 
            self.track_z1 - the number of steps spindle1 made
            self.track z2 - "" spindle2
            self.track z3 - "" spindle3
        '''
        tr_file = np.load(self.tracker_file_name)
        self.track_z1 = float(tr_file['z1'])
        self.track_z2 = float(tr_file['z2'])
        self.track_z3 = float(tr_file['z3'])
        self.track_curr_x = float(tr_file['x'])
        self.track_curr_y = float(tr_file['y'])
        self.track_curr_z = float(tr_file['z'])

        return self.track_z1, self.track_z2, self.track_z3

    def check_spindle_limit (self, move):
        '''
        Function that checks if the limit of motion is reached when moving the spindles by 'move' steps.
        Originally in JPE_tracker.
        Input:
            move - array of length 3 that contains the number of steps of the spindles to be made
        Output:
            limit_reached - True if move brings one of the spindles beyond the limit, 
                            False if all are within limit
        '''
        n1 = self.track_z1+move[0]
        n2 = self.track_z2+move[1]
        n3 = self.track_z3+move[2]
        return ((n1<0)or(n2<0)or(n3<0)or(n1>self.max_spindle_steps)or(n2>self.max_spindle_steps)or(n3>self.max_spindle_steps))

    def set_as_origin (self):
        '''
        Function that sets the current x,y,z position of the fiber as the origin ([0,0,0]).
        Originally in JPE_tracker.
        '''
        self.track_curr_x = 0
        self.track_curr_y = 0
        self.track_curr_z = 0
        self.tracker_update (spindle_incr = [0,0,0], pos_values = [0.,0.,0.])

    def reset_spindle_tracker(self):
        '''
        Function that sets the current absolute number of spindle steps z1,z2,z3 to zero. 
        Thus redefines the end of the spindle range.
        Originally in JPE_tracker.
        '''
        self.track_z1 = 0
        self.track_z2 = 0
        self.track_z3 = 0
        self.tracker_file_update()
        print 'Tracker reset to zero'

    def tracker_update (self, spindle_incr, pos_values):
        '''
        Function that updates the instrument parameters and tracker file after a spindle movement.
        Input:
            spindle_incr - length 3 array with the number of spindle steps per spindle
            pos_values   - length 3 array with the new position values of the fiber (x, y, z).
        '''
        self.track_z1 = self.track_z1+spindle_incr[0]
        self.track_z2 = self.track_z2+spindle_incr[1]
        self.track_z3 = self.track_z3+spindle_incr[2]
        self.track_curr_x = pos_values[0]
        self.track_curr_y = pos_values[1]
        self.track_curr_z = pos_values[2] 
        self.tracker_file_update ()

    def position_to_spindle_steps (self, x, y, z, update_tracker=False):
        '''
        Function that calculates the number of full spindle steps to be made
        to move to a target position
        Input:
            x  - target position x
            y  - "" y
            z  - "" z
            update_tracker - whether to update the tracker with target position. default: False
        Output:
            DZ1 - number of full spindle steps for z1
            DZ2 - "" z2
            DZ3 - "" z3
        '''
        Dx = x-self.track_curr_x
        Dy = y-self.track_curr_y
        Dz = z-self.track_curr_z
            
        DZ1 = -(self.R/self.h)*Dy+Dz
        DZ2 = (3.**0.5/2.)*(self.R/self.h)*Dx+(0.5*self.R/self.h)*Dy+Dz
        DZ3 = -(3.**0.5/2.)*(self.R/self.h)*Dx+(0.5*self.R/self.h)*Dy+Dz
        
        if update_tracker:
            self.track_curr_x = x
            self.track_curr_y = y
            self.track_curr_z = z

        return DZ1, DZ2, DZ3

    def motion_to_spindle_steps (self, x, y, z, update_tracker = False):
        '''
        Function that transforms a target position to the number of spindle steps,
        taking into account the step size at LT or RT. This should also include rel. step size.
        Input:
            x  - target position x
            y  - "" y
            z  - "" z
            update_tracker - whether to update the tracker with target position. default: False
        Output:
            s1 - number of spindle steps of relative step size for z1
            s2 - "" z2
            s3 - "" z3
        '''
        dz1, dz2, dz3 = self.position_to_spindle_steps (x=x, y=y, z=z, update_tracker = update_tracker)
        s1 = dz1/self._step_size
        s2 = dz2/self._step_size
        s3 = dz3/self._step_size
        return s1, s2, s3

    def do_get_temperature (self):
        return self.temperature

    def do_set_temperature (self, value):
        self.temperature = value
        self.ins_cfg['temperature'] = self.temperature
        if (self.temperature>280):
            self._step_size = 15e-6 #in mm #SvD: what is this based on??
        
        if (self.temperature<15):
            self._step_size = 3e-6 #in mm

    def do_set_address (self, addr):
        self.addr = addr
    def do_get_address (self):
        return self.addr
    
    def do_get_freq(self):
        return self.freq
    def do_set_freq (self, value):
        self.freq = value
        self.ins_cfg['freq'] = self.freq

    def do_get_rel_step_size(self):
        return self.rel_step_size
    def do_set_rel_step_size(self, value):
        self.rel_step_size = value
        self.ins_cfg['rel_step_size'] = self.rel_step_size


    def do_get_track_curr_x(self):
        return self.track_curr_x
    def do_get_track_curr_y(self):
        return self.track_curr_y
    def do_get_track_curr_z(self):
        return self.track_curr_z
    def get_track_z(self):
        return self.track_z1, self.track_z2, self.track_z3


    def get_params (self):
        params = self.ins_cfg.get_all()
        for p in params:
            print params[p]
        print self._jpe_cadm.get_type()
        print self._jpe_cadm.info()
        
    def status (self):
        output = self._jpe_cadm.status (addr= self.addr)
        return output
            
    def step (self, ch, steps):
        self._jpe_cadm.move (addr=self.addr, ch=ch, steps = steps, 
            T=self.temperature, freq=self.freq, reL_step=self.rel_step_size)
        
    def set_as_origin (self):
        self._jpe_tracker.set_as_origin()

    def reset_spindle_tracker(self):
        self._jpe_tracker.reset_spindle_tracker()
        print 'S1, S2, S3 ', self._jpe_tracker.z1, self._jpe_tracker.z2, self._jpe_tracker.z3

    def print_current_position(self):
        print 'x = ', self._jpe_tracker.curr_x
        print 'y = ', self._jpe_tracker.curr_y
        print 'z = ', self._jpe_tracker.curr_z

    def print_tracker_params(self):
        z1, z2, z3 = self._jpe_tracker.tracker_file_readout()
        print 'Spindle positions: ', z1, z2, z3

    def get_position (self):
        return self._jpe_tracker.curr_x, self._jpe_tracker.curr_y, self._jpe_tracker.curr_z

    def set_fine_piezo_voltages (self, v1,v2,v3):
        #self.ins_adwin.set_dac('jpe_fine_tuning_1', v1)
        #self.ins_adwin.set_dac('jpe_fine_tuning_2', v2)
        #self.ins_adwin.set_dac('jpe_fine_tuning_3', v3)
        self.ins_adwin.set_fine_piezos (voltage = np.array([v1, v2, v3]))
        self._fine_piezo_V = np.array([v1,v2,v3])

    def get_fine_piezo_voltages(self):
        return self._fine_piezo_V

    def move_spindle_steps (self, s1, s2, s3, x, y, z):
        self._jpe_cadm.move(addr = self.addr, ch = self.ch_x, steps = s1)
        self._jpe_cadm.move(addr = self.addr, ch = self.ch_y, steps = s2)
        self._jpe_cadm.move(addr = self.addr, ch = self.ch_z, steps = s3)
        self._jpe_tracker.tracker_update(spindle_incr=[s1,s2,s3], pos_values = [x,y,z])
        print "Current position (MOC): ", x,y,z

    def move_to_xyz (self, x, y, z, verbose=True):
        if (self.temperature == None):
            print 'Temperature not set!'
        else:
            dz1, dz2, dz3 = self._jpe_tracker.position_to_spindle_steps (x=x, y=y, z=z, update_tracker=False)#no need to update tracker, since position values are set below
            s1 = dz1/self._step_size
            s2 = dz2/self._step_size
            s3 = dz3/self._step_size

            if verbose:
                print 'Moving the spindles the following amounts:'
                print 's-1: ', s1, ' steps'
                print 's-2: ', s2, ' steps'
                print 's-3: ', s3, ' steps'
                print 'Currently the spindle positions are the following:'
                self.print_tracker_params()
                a = raw_input ('Actuate? [y/n]')
            else:
                a='y'


            print 'a=', a
            if (a=='y'):
                print 'moving'
                self._jpe_cadm.move(addr = self.addr, ch = self.ch_x, steps = s1)
                self._jpe_cadm.move(addr = self.addr, ch = self.ch_y, steps = s2)
                self._jpe_cadm.move(addr = self.addr, ch = self.ch_z, steps = s3)
                self._jpe_tracker.tracker_update(spindle_incr=[s1,s2,s3], pos_values = [x,y,z])
        def remove(self):
            self.save_cfg()
            Instrument.remove()

    # def close(self):
    #     '''
    #     SvD: the function in the jpe tracker doesn't exist... this function has probably NEVER been called...
    #     '''
    #     self._jpe_tracker.close()

    # def line_scan (self, axis, min_val, max_val, nr_steps):
    #     '''
    #     SvD: This function
    #     (a) had a clear bug (typo), so I think never has been tested or used
    #     (b) Doesn't seem to be called upon anywhere
    #     (c) I want to remove it.
    #     Originally from JPE_tracker
    #     '''
    #     PK_val1 = np.zeros(nr_steps)
    #     PK_val2 = np.zeros(nr_steps)
    #     PK_val3 = np.zeros(nr_steps)
    #     scan_vals = np.linspace (min_val, max_val, nr_steps)
    #     ind = 0     
    #     for i in scan_vals:
    #         if (axis=='x'):
    #             dz1, dz2, dz3 = self.move_to_position (x = i, y=self.track_curr_y, z=self.track_curr_z)
    #         else:
    #             if (axis=='y'):
    #                 dz1, dz2, dz3 = self.move_to_position (x = self.track_curr_x, y=i, z=self.track_curr_z)                
    #             else:
    #                 if (axis=='z'):
    #                     dz1, dz2, dz3 = self.move_to_position (x = self.track_curr_x, y = self.track_curr_y, z=i)
    #         PK_val1 [ind] = dz1
    #         PK_val2 [ind] = dz2
    #         PK_val3 [ind] = dz3
    #         ind = ind + 1

    #     return PK_val1, PK_val2, PK_val3


