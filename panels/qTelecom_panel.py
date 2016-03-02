########################################
# Cristian Bonato, 2015
# cbonato80@gmail.com
# Adapted by Anais Dreau
########################################

from __future__ import unicode_literals
import os, sys, time
from datetime import datetime

import random
# from pyqtgraph.Qt import QtGui, QtCore
# import pyqtgraph as pg
# from pyqtgraph.ptime import time
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends import qt4_compat
use_pyside = qt4_compat.QT_API == qt4_compat.QT_API_PYSIDE
if use_pyside:
    from PySide import QtGui, QtCore, uic
else:
    from PyQt4 import QtGui, QtCore, uic


from ui_Temperature_panel import Ui_Panel as Ui_Init 

from panel import Panel


class TempCtrlPanel (Panel):
    def __init__(self, parent, *arg, **kw):
        Panel.__init__(self,parent,*arg,**kw)

        self.ui = Ui_Init()
        self.ui.setupUi(self)

        self.ui.setTemp.setRange(-20.0, 120.0)
        self.ui.setTemp.setDecimals(2)
        self.ui.setTemp.setSingleStep(0.01)
        self.ui.setTemp.valueChanged.connect(self.set_target_temperature)

        # self.ui.dsb_Tmin.setRange(-20.0, 120.0)
        # self.ui.dsb_Tmin.setDecimals(2)
        # self.ui.dsb_Tmin.setSingleStep(0.01)
        # self.ui.dsb_Tmin.valueChanged.connect(self.set_Tmin)


        # self.ui.dsb_Tmax.setRange(-20.0, 120.0)
        # self.ui.dsb_Tmax.setDecimals(2)
        # self.ui.dsb_Tmax.setSingleStep(0.01)
        # self.ui.dsb_Tmax.valueChanged.connect(self.set_Tmax)


        # self.ui.sb_steps.setRange(0, 1000)
        # # self.ui.setTemp.setDecimals(2)
        # self.ui.sb_steps.setSingleStep(1)
        # self.ui.sb_steps.valueChanged.connect(self.set_nsteps)


        # self.ui.sb_dwell_time.setRange(0, 1000)
        # # self.ui.dsb_dwell_time.setDecimals(2)
        # self.ui.sb_dwell_time.setSingleStep(1)
        # self.ui.sb_dwell_time.valueChanged.connect(self.set_dwell_time)


        self.ui.stopButton.clicked.connect(self.stop_running)
        self.ui.setTempButton.clicked.connect(self.readNset_target)

        self.check_knob_temperature()
        self.read_temperature()
        self.read_DFG_power()
        self.start_running()

        # for p in [self.ui.plot1, self.ui.plot2]:
        #     p.left_axis.title = 'counts [Hz]'
        #     p.plot.padding = 5
        #     p.plot.padding_bottom = 30
        #     p.plot.padding_left = 100
        #     # plot = p.plot.plots['trace'][0]
        #     plot.padding = 0
        #     plot.color = 'green'
        #     plot.marker = 'circle'
        #     plot.marker_size = 3
            

        # self.ui.plot1.display_time = 20
        # self.ui.plot2.display_time = 20
        # self.ui.t_range.setValue(20)




    def _instrument_changed(self,changes):
        Panel._instrument_changed(self, changes)
        # print changes
        if changes.has_key('curr_temperature'):
            self.ui.displayActualTemp.setText(str(changes['curr_temperature']))

        if changes.has_key('DFG_power'):
             self.ui.displayDFG.setText(str(changes['DFG_power']))

        if changes.has_key('set_temperature'):
            self.ui.displayTargetTemp.setText(str(changes['set_temperature']))

        if changes.has_key('temperature_channel_plot_DFG_values'):
            self.ui.plot1.add_point(changes['temperature_channel_plot_DFG_values'], changes['dfg_channel_plot_DFG_values'])


    def read_temperature (self):
        self._ins.read_temperature()

    def plot_values (self):
        self._ins.plot_values()

    # def change_temperature (self):
    #     self._ins.change_temperature

    def read_DFG_power (self):
        self._ins.read_DFG_power()

    def set_target_temperature (self, value):
        self._ins.set_target_temperature(value)

    def check_knob_temperature (self):
        self._ins.check_knob_temperature()

    def set_Tmin (self, value):
        self._ins.set_Tmin(value)

    def set_Tmax (self, value):
        self._ins.set_Tmax(value)

    def set_nsteps (self, value):
        self._ins.set_nsteps(value)

    def set_dwell_time (self, value):
        self._ins.set_dwell_time(value)

    def readNset_target (self):
        self._ins.readNset_target()

    def display_values (self):
        self._ins.display_values()

    def start_running (self):
        self._ins.start_running()

    def stop_running (self):
        self._ins.stop_running()

