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
from ui_Temperature_panel import Ui_Panel2 as Ui_Init2 
# from ui_Temperature_panel import Ui_Panel3 as Ui_Init3 


from panel import Panel
# from panel import Panel2

class TempCtrlPanel (Panel):
    def __init__(self, parent, *arg, **kw):
        Panel.__init__(self,parent,*arg,**kw)
        # Panel2.__init__(self,parent,*arg,**kw)

        self.ui = Ui_Init()
        self.ui.setupUi(self)

       
        self.ui.cleargraphButton2.clicked.connect(self.ui.plot2.reset)
        self.ui.cleargraphButton3.clicked.connect(self.ui.plot3.reset)
        self.ui.cleargraphButton4.clicked.connect(self.ui.plot4.reset)
        

        # self.check_knob_temperature()
        # self.read_temperature()
        # self.read_DFG_power()
        # self.start_running()





    def _instrument_changed(self,changes):
        Panel._instrument_changed(self, changes)
        # print changes
        if changes.has_key('curr_temperature'):
            self.ui.displayActualTemp.setText(str(changes['curr_temperature']))

        if changes.has_key('DFG_power'):
             self.ui.displayDFG.setText(str(changes['DFG_power']))

        if changes.has_key('set_temperature'):
            self.ui.displayTargetTemp.setText(str(changes['set_temperature']))

       


        if changes.has_key('temperature_channel2_plot_DFG_values2'):
            # print "plotting"
            self.ui.plot2.add_point(changes['dfg_channel2_plot_DFG_values2'])
            # self.ui.plot2.add_point(changes['temperature_channel2_plot_DFG_values2'], changes['dfg_channel2_plot_DFG_values2'])
            # print "Something is happening"


        if changes.has_key('temperature_channel2_plot_DFG_values2'):
            # print "plotting"
            # self.ui.plot2.add_point(changes['dfg_channel2_plot_DFG_values2'])
            self.ui.plot3.add_point(changes['temperature_channel2_plot_DFG_values2'])
            # print "Something is happening"

        if changes.has_key('temperature_channel2_plot_DFG_values2'):
            # print "plotting"
            # self.ui.plot2.add_point(changes['dfg_channel2_plot_DFG_values2'])
            self.ui.plot3.add_point(changes['red_channel2_plot_DFG_values2'])
            # print "Something is happening"


    

    # def read_temperature (self):
    #     self._ins.read_temperature()

   

    # def clear_graph( self):
    #     self._ins.clear_graph()

    # def change_temperature (self):
    #     self._ins.change_temperature

    def read_DFG_power (self):
        self._ins.read_DFG_power()

    



    def start_running (self):
        self._ins.start_running()

    def stop_running (self):
        self._ins.stop_running()



class TempCtrlMonitor (Panel):
    def __init__(self, parent, *arg, **kw):
        Panel.__init__(self,parent,*arg,**kw)
        self.ui = Ui_Init2()
        self.ui.setupUi(self)

        self.ui.setTemp.setRange(-20.0, 120.0)
        self.ui.setTemp.setDecimals(2)
        self.ui.setTemp.setSingleStep(0.01)
        self.ui.setTemp.valueChanged.connect(self.set_target_temperature)

        self.ui.lineEdit.textChanged.connect(self.set_input_fig_title)
        self.ui.textEdit.textChanged.connect(self.apply_changes)

        self.ui.dsb_Tmin.setRange(-20.0, 120.0)
        self.ui.dsb_Tmin.setDecimals(2)
        self.ui.dsb_Tmin.setSingleStep(0.01)
        self.ui.dsb_Tmin.valueChanged.connect(self.set_Tmin)


        self.ui.dsb_Tmax.setRange(-20.0, 120.0)
        self.ui.dsb_Tmax.setDecimals(2)
        self.ui.dsb_Tmax.setSingleStep(0.01)
        self.ui.dsb_Tmax.valueChanged.connect(self.set_Tmax)

        # self.ui.plot1.set_marker('plus')
        # self.ui.plot2.set_marker('plus')


        self.ui.sb_steps.setRange(0, 1000)
        # self.ui.setTemp.setDecimals(2)
        self.ui.sb_steps.setSingleStep(1)
        self.ui.sb_steps.valueChanged.connect(self.set_nsteps)


        self.ui.sb_dwell_time.setRange(0, 1000)
        # self.ui.dsb_dwell_time.setDecimals(2)
        self.ui.sb_dwell_time.setSingleStep(1)
        self.ui.sb_dwell_time.valueChanged.connect(self.set_dwell_time)

        self.start_running()

        self.ui.scanButton.clicked.connect(self.start_plotting)
        self.ui.stopButton.clicked.connect(self.stop_plotting)
        self.ui.saveButton.clicked.connect(self.save_scan)
        self.ui.resetButton.clicked.connect(self.check_knob_temperature)
        self.ui.setTempButton.clicked.connect(self.readNset_target)
        self.ui.cleargraphButton.clicked.connect(self.ui.plot1.reset)

    def _instrument_changed(self,changes):
        Panel._instrument_changed(self, changes)

        if changes.has_key('temperature_channel_plot_DFG_values'):
            # print "plotting"
            self.ui.plot1.add_point(changes['temperature_channel_plot_DFG_values'], changes['dfg_channel_plot_DFG_values'])


    def start_plotting (self):
        self._ins.start_plotting()

    def stop_plotting (self):
        self._ins.stop_plotting()

    def apply_changes(self):
        text = self.ui.textEdit.toPlainText()
        self.set_comments(text)

    def set_target_temperature (self, value):
        self._ins.set_target_temperature(value)

    def set_input_fig_title (self, value):
        self._ins.set_input_fig_title(value)

    def set_comments (self, value):
        self._ins.set_comments(value)

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

    def save_scan (self):
        self._ins.save_scan()

    def readNset_target (self):
        self._ins.readNset_target()

    def display_values (self):
        self._ins.display_values()

    def plot_values (self):
        self._ins.plot_values()

    
    def start_running (self):
        self._ins.start_running()

    def stop_running (self):
        self._ins.stop_running()


# class DM_sweep_optimization (Panel):
#     def __init__(self, parent, *arg, **kw):
#         Panel.__init__(self,parent,*arg,**kw)
#         self.ui = Ui_Init3()
#         self.ui.setupUi(self)

#         self.ui.sb_pin_nr.setRange(1, 40)
#         # self.ui.setTemp.setDecimals(2)
#         self.ui.sb_pin_nr.setSingleStep(1)
#         self.ui.sb_pin_nr.valueChanged.connect(self.set_pin_nr)

#         self.ui.sweepButton.clicked.connect(self.start_sweep_pin)
#         self.ui.stopButton.clicked.connect(self.stop_sweep_pin)
#         self.ui.saveButton.clicked.connect(self.save_sweep_pin)

#         if changes.has_key('temperature_channel_plot_DFG_values'):  
#                 # print "plotting"
#                 self.ui.plot4.add_point(changes['temperature_channel_plot_DFG_values'], changes['dfg_channel_plot_DFG_values'])

#     def set_pin_nr (self, value):
#         self._ins.set_pin_nr(value)

#     def save_sweep_pin (self):
#         self._ins.save_sweep_pin()

#     def start_sweep_pin (self):
#         self._ins.start_plotting()

#     def stop_sweep_pin (self):
#         self._ins.stop_plotting()


