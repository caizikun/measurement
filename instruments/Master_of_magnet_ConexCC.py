### Instrument class to control a set of Newport Conex CC X-Y-Z stages.
#
### Work in progress, Martin Eschen

from instrument import Instrument

class Master_of_magnet_ConexCC(Instrument):

    def __init__(self, name,  x_stage, y_stage, z_stage):

        Instrument.__init__(self, name)
        self._anc_ins = qt.instruments[anc_ins]
        # first check if all axes are qt instruments, existing and responding



#        ### Axis modules <-> magnet scan axes
#        self.Axis_config = {
#        'X_axis': 5,
#        'Y_axis': 6,
#        'Z_axis': 4}

#        self._anc_ins.Turn_off_AC_IN(self.Axis_config['Y_axis'])
#        self._anc_ins.Turn_off_AC_IN(self.Axis_config['Z_axis'])
#        self._anc_ins.Turn_off_AC_IN(self.Axis_config['X_axis'])

#        self._anc_ins.Turn_off_DC_IN(self.Axis_config['X_axis'])
#        self._anc_ins.Turn_off_DC_IN(self.Axis_config['Y_axis'])
#        self._anc_ins.Turn_off_DC_IN(self.Axis_config['Z_axis'])

    def set_mode(self, axis, mode):
        ''' Sets the mode (string) of axis 'X_axis', 'Y_axis', 'Z_axis' or 'all'
            to the following:
        gnd     Disables all outputs and connects them to ground(chassis mass).

        stp     Stepping mode. AC-IN and DC-IN functionalities are not modified.
                Offset is turned off.

        inp     External scanning mode. AC-IN and DC-IN can be enabled for external scanning
                using the Turn_on_AC_IN and Turn_on_DC_IN methods. Disables stepping and
                offset modes.

        off     Offset mode / scanning mode. AC-IN and DC-IN functionalities are
                not modified. Any stepping is turned off.

        stp+    Additive offset + stepping mode. Stepping waveforms are added to
                the offset. AC-IN and DC-IN functionalities are not modified.

        stp-    Subtractive offset + stepping mode. Stepping
                waveforms are subtracted from an offset. AC-IN and DC-IN
                functionalities are not modified.

        cap     Starts a capacitance measurement. The axis
                returns to gnd mode afterwards. It is not needed to switch to gnd
                mode before.
        '''
        if axis == 'all':
            for ax in ['X_axis', 'Y_axis', 'Z_axis']:
                axis_number = self.Axis_config[ax]
                self._anc_ins.SetMode(axis_number, mode)
        else:
            axis_number = self.Axis_config[axis]
            self._anc_ins.SetMode(axis_number, mode)

    def get_mode(self,axis):
        if axis == 'all':
            for ax in ['X_axis', 'Y_axis', 'Z_axis']:
                axis_number = self.Axis_config[ax]
                print ax+ ' '+ self._anc_ins.GetMode(axis_number)
        else:
            axis_number = self.Axis_config[axis]
            return self._anc_ins.GetMode(axis_number)

    def get_axis_config(self):
        print 'X_axis = ' + str(self.Axis_config['X_axis'])
        print 'Y_axis = ' + str(self.Axis_config['Y_axis'])
        print 'Z_axis = ' + str(self.Axis_config['Z_axis'])

    # get/set scan/step paramaters
    def get_frequency(self, axis):
        ''' Get the stepper frequency'''
        if axis == 'all':
            for ax in ['X_axis', 'Y_axis', 'Z_axis']:
                axis_number = self.Axis_config[axis]
                return self._anc_ins.GetFrequency(axis_number)

        else:
            axis_number = self.Axis_config[axis]
            print(axis_number)
            return self._anc_ins.GetFrequency(axis_number)

    def set_frequency(self, axis, frequency):
        ''' Set the stepper frequency'''
        self._anc_ins.SetFrequency(self.Axis_config[axis], frequency)
        print 'frequency of %s set to %d Hz' %(axis, frequency)

    def get_amplitude(self, axis):
        ''' Get the stepper amplitude'''
        axis_number = self.Axis_config[axis]
        return self._anc_ins.GetAmplitude(axis_number)

    def set_amplitude(self, axis, amplitude):
        ''' Set the stepper amplitude'''
        self._anc_ins.SetAmplitude(self.Axis_config[axis], amplitude)
        print 'amplitude of %s set to %d V' %(axis, amplitude)

    def get_offset(self, axis):
        ''' Get the scanner offset'''
        axis_number = self.Axis_config[axis]
        return self._anc_ins.GetOffset(axis_number)

    def set_offset(self, axis, offset):
        ''' Get the stepper offset'''
        self._anc_ins.SetOffset(self.Axis_config[axis], offset)
        print 'offset of %s set to %d V' %(axis, offset)

    # Stepping and stopping.
    def step(self, axis, steps):  #TODO add a timer to stop the continious movement
        ''' Performs #steps along the given axis.
        axis    the axis to step.levelmon
        steps   integer, positive values for positive steps, negative values for
                negative steps. Valid inputs: +/- 1,2,3,4,5... and 'c','-c' for continious
        '''
        axis_number = self.Axis_config[axis]
        print (self.get_frequency(axis)[12:15])
        freq = int(self.get_frequency(axis)[12:15])
        if steps == 'c':
            self._anc_ins.StepUp(axis_number, steps)
        elif steps == '-c':
            self._anc_ins.StepDown(axis_number, 'c')
        elif int(steps) > 0:
            self._anc_ins.StepUp(axis_number, steps)
            qt.msleep(int(steps)/freq + 2)
        elif int(steps) < 0:
            self._anc_ins.StepDown(axis_number, abs(int(steps)))
            qt.msleep(abs(int(steps))/freq + 2)
        elif int(steps) == 0:
            print 'Number of steps is 0, not moved'
        else:
            print "Error: invalid input. 'c' or '-c' for continious, '+/- 1,2,3,4...' for number of int steps" 

    def stop(self, axis):
        axis_number = self.Axis_config[axis]
        self._anc_ins.Stop(axis_number)

    def Read(self):
        return self._anc_ins.Read()