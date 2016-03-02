########################################
# Cristian Bonato, 2015
# cbonato80@gmail.com
# Adapted by Anais Dreau
########################################

import os
from instrument import Instrument
from cyclopean_instrument import CyclopeanInstrument

# from matplotlib.backends import qt4_compat
import qt
import time
import types
# import pyqtgraph as pg
import numpy as np
# import pylab as pltexit
from lib import config



class qTelecom_manager (CyclopeanInstrument):
    def __init__(self, name, adwin, powermeter, parent=None):
        CyclopeanInstrument.__init__(self,name, tags=[])


        self._adwin = qt.instruments[adwin]
        self._pmeter = qt.instruments[powermeter]

        self.dac_no = 8
        self.adc_no = 2

        self.sampling_interval = 250

        self.add_parameter('plot_DFG_values',
                           flags=Instrument.FLAG_GET,
                           units='uW',
                           tags=['measure'],
                           channels=('temperature_channel', 'dfg_channel'),
                           channel_prefix='%s_',
                           doc="""
                           Returns the measured temperature and dfg power
                           """)
        self._plot_DFG_values = {'temperature_channel': 0.0, 'dfg_channel': 0.0, }

        self.add_parameter('curr_temperature',
                type= types.FloatType, 
                flags=Instrument.FLAG_GETSET, 
                units = 'deg',
                minval = -20, maxval = 120)
        self.curr_temperature=0

        self.add_parameter('knob_temperature',
                type= types.FloatType, 
                flags=Instrument.FLAG_GETSET, 
                units = 'deg',
                minval = -20, maxval = 120)
        self.knob_temperature=0

        self.add_parameter('DFG_power',
                type= types.FloatType, 
                flags=Instrument.FLAG_GETSET, 
                units = 'muW',
                minval = 0, maxval = 2000)
        self.DFG_power=0

        self.add_parameter('target_temperature',
                type= types.FloatType, 
                flags=Instrument.FLAG_GETSET, 
                units = 'deg',
                minval = -50, maxval = 120)
        self.target_temperature=0.00

        self.add_parameter('set_temperature',
                type= types.FloatType, 
                flags=Instrument.FLAG_SET, 
                units = 'deg',
                minval = -50, maxval = 120)
        self.set_temperature=0.00

        self.add_parameter('plot_temperature',
                type= types.FloatType, 
                flags=Instrument.FLAG_GETSET, 
                units = 'deg',
                minval = -50, maxval = 120)
        self.plot_temperature=0.00

        self.add_parameter('plot_dfg',
                type= types.FloatType, 
                flags=Instrument.FLAG_GETSET, 
                units = 'uW',
                minval = -50, maxval = 120)
        self.plot_dfg=0.00

        self.add_parameter('Tmin',
                type= types.FloatType, 
                flags=Instrument.FLAG_GETSET, 
                units = 'deg',
                minval = -50, maxval = 120)
        self.Tmin=0.00

        self.add_parameter('Tmax',
                type= types.FloatType, 
                flags=Instrument.FLAG_GETSET, 
                units = 'deg',
                minval = -50, maxval = 120)
        self.Tmax=0.00

        self.add_parameter('nsteps',
                type= types.IntType, 
                flags=Instrument.FLAG_GETSET, 
                units = '',
                minval = 0, maxval = 1000)
        self.nsteps=0

        self.add_parameter('dwell_time',
                type= types.IntType, 
                flags=Instrument.FLAG_GETSET, 
                units = 'us',
                minval = 0, maxval = 1000)
        self.dwell_time=0




        self.add_function('read_temperature')

        self.add_function('read_DFG_power')

        self.add_function('readNset_target')

        self.add_function('start_running')
        self.add_function('stop_running')

        self.add_function('display_values')

        self.add_function('check_knob_temperature')

        self.add_function('plot_values')

        # self.add_function('change_temperature')


    def _sampling_event(self):
        while self.get_is_running():
            # time.sleep(0.05)
            self.read_temperature() 
            self.read_DFG_power()
            self._plot_DFG_values = {'temperature_channel': self.get_curr_temperature(), 'dfg_channel': self.get_DFG_power(), }
            self.get_temperature_channel_plot_DFG_values()
            self.get_dfg_channel_plot_DFG_values()
            return True
        else:
            return False

    # def _sampling_event(self):
    #     self.read_temperature() 
    #     return True

    def start_running (self):
        self.set_is_running(True)

    def stop_running (self):
        # print "Trying to stop"
        self.set_is_running(False)

    def read_temperature (self):
        test = 0
    	self._adwin.start_read_adc (adc_no = self.adc_no)
        voltage = self._adwin.get_read_adc_var ('fpar')[0][1]
    	T = 0.01*int(voltage*20.*100)
        self.set_curr_temperature(T)
        self.get_curr_temperature()

    def read_DFG_power(self):
        DFG = self._pmeter.get_power()*1e6
        self.set_DFG_power(DFG)
        self.get_DFG_power()

    def check_knob_temperature (self):
        zero_voltage = 0.0
        self._adwin.start_set_dac(dac_no=self.dac_no, dac_voltage=zero_voltage)
        self._adwin.start_read_adc (adc_no = self.adc_no)
        voltage = self._adwin.get_read_adc_var ('fpar')[0][1]
        oldT = 0.01*int(voltage*20.*100)
        newT = 300
        while abs(newT - oldT) > 0.05:
            time.sleep(1)
            oldT = newT
            self._adwin.start_read_adc (adc_no = self.adc_no)
            voltage = self._adwin.get_read_adc_var ('fpar')[0][1]
            newT = 0.01*int(voltage*20.*100)
            # newT = 300
        else:
            self.set_knob_temperature(newT)
            self.get_knob_temperature()
        print "Knob temperature at 0 voltage: ", self.get_knob_temperature()



    # def change_temperature (self):
    #     self.delta_T = self.get_target_temperature()
    #     voltage = value/20.
    #     self._adwin.start_set_dac(dac_no=self.dac_no, dac_voltage=voltage)
    #     print "voltage: ", voltage

    # def read_target_temperature (self, value):
    #     self.set_target_temperature(value)

    def readNset_target (self):
        setT = self.get_target_temperature() - self.get_knob_temperature()
        print "set temperature is ", setT, self.get_target_temperature()
        self.set_set_temperature(self.get_target_temperature())
        voltage = setT/20.
        self._adwin.start_set_dac(dac_no=self.dac_no, dac_voltage=voltage)
        print "voltage: ", voltage
        self.set_is_running(True)

    def display_values (self):
        step = 0
        setT = self.get_Tmin() - self.get_knob_temperature()
        self.set_set_temperature(setT)
        voltage = setT/20.
        self._adwin.start_set_dac(dac_no=self.dac_no, dac_voltage=voltage)
        self._adwin.start_read_adc (adc_no = self.adc_no)
        voltage = self._adwin.get_read_adc_var ('fpar')[0][1]
        oldT = 0.01*int(voltage*20.*100)
        newT = 300

        print "#steps", self.get_nsteps(), "step ", step
        print (self.get_nsteps() > step)
        for i in range(0,self.get_nsteps()):
            # print "step", i
            meas_T = self.get_Tmin() + i*(self.get_Tmax() - self.get_Tmin())/self.get_nsteps() - self.get_knob_temperature()
            self.set_set_temperature(meas_T)
            voltage = meas_T/20.
            self._adwin.start_set_dac(dac_no=self.dac_no, dac_voltage=voltage)
            time.sleep(0.001*self.get_dwell_time())
            self.read_temperature()
            self.read_DFG_power()
            print "Tmin: " + str(self.get_Tmin()) + " Tmax: " + str(self.get_Tmax()) + " #steps: " + str(self.get_nsteps()) + " dwell time: " + str(self.get_dwell_time())
            print "Temperature: ", self.get_curr_temperature(), " DFG power: ", self.get_DFG_power(), " i ", i , " Target ", meas_T + self.get_knob_temperature() 
            # step = step + 1


    def plot_values (self):
        step = 0
        setT = self.get_Tmin() - self.get_knob_temperature()
        self.set_set_temperature(setT)
        voltage = setT/20.
        self._adwin.start_set_dac(dac_no=self.dac_no, dac_voltage=voltage)
        self._adwin.start_read_adc (adc_no = self.adc_no)
        voltage = self._adwin.get_read_adc_var ('fpar')[0][1]
        oldT = 0.01*int(voltage*20.*100)
        newT = 300

        self.set_plot_temperature(self.get_curr_temperature())
        self.get_plot_temperature()
        self.set_plot_dfg(self.get_DFG_power())
        self.get_plot_dfg()

        self._plot_DFG_values = {'temperature_channel': self.get_plot_temperature(), 'dfg_channel': self.get_plot_dfg(), }

        for i in range(0,self.get_nsteps()):
            meas_T = self.get_Tmin() + i*(self.get_Tmax() - self.get_Tmin())/self.get_nsteps() - self.get_knob_temperature()
            self.set_set_temperature(meas_T)
            voltage = meas_T/20.
            self._adwin.start_set_dac(dac_no=self.dac_no, dac_voltage=voltage)
            time.sleep(0.001*self.get_dwell_time())
            self.read_temperature()
            self.read_DFG_power()
            # self.plot1.add_point(self.get_curr_temperature(), self.get_DFG_power())

            self.set_plot_temperature(self.get_curr_temperature())
            self.get_plot_temperature()
            self.set_plot_dfg(self.get_DFG_power())
            self.get_plot_dfg()
            # cr = [0., int(normal(mean1, sqrt(mean1))), int(normal(mean2, sqrt(mean2))) ]
            self._plot_DFG_values['temperature_channel'] = self.get_plot_temperature()
            self._plot_DFG_values['dfg_channel'] = self.get_plot_dfg()
            self.get_temperature_channel_plot_DFG_values()
            self.get_dfg_channel_plot_DFG_values()
            print "done", self.get_plot_temperature()
            # self._sampling_event()

            # print "Tmin: " + str(self.get_Tmin()) + " Tmax: " + str(self.get_Tmax()) + " #steps: " + str(self.get_nsteps()) + " dwell time: " + str(self.get_dwell_time())
            # print "Temperature: ", self.get_curr_temperature(), " DFG power: ", self.get_DFG_power(), " i ", i , " Target ", meas_T + self.get_knob_temperature() 
            # step = step + 1


    def do_get_plot_DFG_values(self, channel):
        return self._plot_DFG_values[channel]



    def do_get_DFG_power(self):
        return self.DFG_power

    def do_set_DFG_power(self,value):
        self.DFG_power = value

    def do_get_knob_temperature(self):
        return self.knob_temperature

    def do_set_knob_temperature(self,value):
        self.knob_temperature = value

    def do_get_curr_temperature(self):
        return self.curr_temperature

    def do_set_curr_temperature(self,value):
        self.curr_temperature = value

    def do_set_set_temperature(self,value):
        self.set_temperature = value

    def do_set_plot_temperature(self,value):
        self.plot_temperature = value

    def do_get_plot_temperature(self):
        return self.plot_temperature

    def do_set_plot_dfg(self,value):
        self.plot_dfg = value

    def do_get_plot_dfg(self):
        return self.plot_dfg

    def do_get_target_temperature(self):
        return self.target_temperature

    def do_set_target_temperature(self,value):
        self.target_temperature = value

    def do_get_Tmin(self):
        return self.Tmin

    def do_set_Tmin(self,value):
        self.Tmin = value

    def do_get_Tmax(self):
        return self.Tmax

    def do_set_Tmax(self,value):
        self.Tmax = value

    def do_get_nsteps(self):
        return self.nsteps

    def do_set_nsteps(self,value):
        self.nsteps = value

    def do_get_dwell_time(self):
        return self.dwell_time

    def do_set_dwell_time(self,value):
        self.dwell_time = value

    def do_set_is_running(self, val):
        self._is_running = val
        if val: self._start_running()
        else: self._stop_running()
    
    def do_get_is_running(self):
        return self._is_running

