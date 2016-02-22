########################################
# Cristian Bonato, 2015
# cbonato80@gmail.com
########################################

from __future__ import unicode_literals
import os, sys, time
from datetime import datetime
from PySide.QtCore import *
from PySide.QtGui import *
import random

from matplotlib.backends import qt4_compat
use_pyside = qt4_compat.QT_API == qt4_compat.QT_API_PYSIDE
if use_pyside:
    from PySide import QtGui, QtCore, uic
else:
    from PyQt4 import QtGui, QtCore, uic

# import pylab as plt
# import h5py
# from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.figure import Figure
# from matplotlib import cm
# from analysis.lib.fitting import fit

from panel import Panel, MsgBox


# import measurement.lib.cavity.cavity_scan_v2
# import measurement.lib.cavity.panels.scan_gui_panels 
# import measurement.lib.cavity.panels.control_panel_2
# import measurement.lib.cavity.panels.ui_scan_panel_v9
# import measurement.lib.cavity.panels.slow_piezo_scan_panel
# import measurement.lib.cavity.panels.XYscan_panel 

# from measurement.lib.cavity.cavity_scan_v2 import CavityExpManager, CavityScan
# from measurement.lib.cavity.panels.scan_gui_panels import MsgBox, ScanPlotCanvas
from measurement.lib.cavity.panels.ui_control_panel_2 import Ui_Dialog as Ui_Form

class ControlPanelGUI (Panel):
    def __init__(self, parent, *arg, **kw):
        Panel.__init__(self, parent, *arg, **kw)

        self._moc = exp_mngr._moc
        self._wm = exp_mngr._wm_adwin
        self._laser = exp_mngr._laser

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        #self.setWindowTitle("Laser-Piezo Scan Interface")
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.p1_V = 0
        self.p2_V = 0
        self.p3_V = 0
        self.piezo_locked = False
        self.pzk_X = self._ins.get_track_curr_x()*1000
        self.pzk_Y = self._ins.get_track_curr_y()*1000
        self.pzk_Z = self._ins.get_track_curr_z()*1000
        self.use_wm = False
   
        self.ui.label_curr_pos_readout.setText('[ '+str(self.pzk_X)+' ,'+str(self.pzk_Y)+' ,'+str(self.pzk_Z)+'] um')
        # self._exp_mngr.update_coarse_piezos (x=self.pzk_X, y=self.pzk_Y, z=self.pzk_Z)
        #Set all parameters and connect all events to actions
        # LASER
        self.ui.dSBox_coarse_lambda.setRange (635.00, 640.00)
        self.ui.dSBox_coarse_lambda.setSingleStep (0.01)
        self.ui.dSBox_coarse_lambda.setValue(637.0)
        self.ui.dSBox_coarse_lambda.valueChanged.connect(self.set_laser_wavelength)
        self.ui.dsB_power.setRange (0.0, 15.0)
        self.ui.dsB_power.setSingleStep(0.1)     
        self.ui.dsB_power.setValue(0)   
        self.ui.dsB_power.valueChanged.connect(self.set_laser_power)
        #########This is a box that refers to a function that does nothing. remove the box. 
        self.ui.dsBox_fine_laser_tuning.setRange (0, 100)
        self.ui.dsBox_fine_laser_tuning.setDecimals(2)
        self.ui.dsBox_fine_laser_tuning.setSingleStep(0.01)
        self.ui.dsBox_fine_laser_tuning.setValue(50)
        self.ui.dsBox_fine_laser_tuning.valueChanged.connect(self.set_fine_laser_tuning)
        #self.set_laser_wavelength(637)# moved this to cavity_exp_manager, but like to remove it alltogether. 
        #self.set_laser_power(0)
        # self.set_fine_laser_tuning(50)

        # FINE PIEZOS
        self.ui.doubleSpinBox_p1.setRange (-2, 10)
        self.ui.doubleSpinBox_p1.setDecimals (3)        
        self.ui.doubleSpinBox_p1.setSingleStep (0.001)
        self.ui.doubleSpinBox_p1.setValue(self.p1_V)
        self.ui.doubleSpinBox_p1.valueChanged.connect(self.set_dsb_p1)
        #SvD: can the range -2000 to 10000 work?
        self.ui.horizontalSlider_p1.setRange (-2000, 10000)#(0,10000)
        self.ui.horizontalSlider_p1.setSingleStep (1)        
        self.ui.horizontalSlider_p1.valueChanged.connect(self.set_hsl_p1)
        self.set_dsb_p1 (self.p1_V)
        
        # PiezoKnobs
        self.ui.spinBox_X.setRange (-999, 999)
        self.ui.spinBox_X.setValue(self.pzk_X)
        self.ui.spinBox_X.valueChanged.connect(self.set_pzk_X)
        self.ui.spinBox_Y.setRange (-999, 999)
        self.ui.spinBox_Y.setValue(self.pzk_Y)
        self.ui.spinBox_Y.valueChanged.connect(self.set_pzk_Y)
        self.ui.spinBox_Z.setRange (-999, 999)
        self.ui.spinBox_Z.setValue(self.pzk_Z)
        self.ui.spinBox_Z.valueChanged.connect(self.set_pzk_Z)
        self.ui.pushButton_activate.clicked.connect (self.move_pzk)
        self.ui.pushButton_set_as_origin.clicked.connect (self.pzk_set_as_origin)

        #Temperature
        self.ui.radioButton_roomT.toggled.connect (self.room_T_button)
        self.ui.radioButton_lowT.toggled.connect (self.low_T_button)

        #Wavemeter
        self.ui.checkBox_wavemeter.stateChanged.connect (self.use_wavemeter)
        # self._exp_mngr._system_updated = True
        self.refresh_time = 100

        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update)
        timer.start(self.refresh_time)

        a = self._ins.status()
        if (a[:5]=='ERROR'):
            msg_text = 'JPE controller is OFF or in manual mode!'
            ex = panel.MsgBox(msg_text=msg_text)
            ex.show()


    def _instrument_changed(self, changes):
        text = self.ui.label_curr_pos_readout.getText('[ '+str(int(curr_x*1000))+' ,'+str(int(curr_y*1000))+' ,'+str(int(curr_z*1000))+'] um')
        #SvD: probably have to change this, want to change for x,y,z separate in textboxes
        if changes.has_key('track_curr_x'):
            text[2:6] = changes['track_curr_x']
        if changes.has_key('track_curr_y'):
            text[9:13] = changes['track_curr_y']
        if changes.has_key('track_curr_z'):
            text[16:20] = changes['track_curr_z']
        if changes.has_key('laser_wavelength'):
            self.ui.dSBox_coarse_lambda.setValue(changes['laser_wavelength'])
        if changes.has_key('laser_power'):
            self.ui.dSBox_coarse_lambda.setValue(changes['laser_power'])
        if changes.has_key('laser_wm_frequency'):
            self.ui.label_wavemeter_readout.setText (str(changes['laser_wm_frequency'])+ ' GHz')


        self.ui.label_curr_pos_readout.setText(text)

    def set_laser_coarse (self, value):
        self._ins.set_laser_wavelength(value)

    def set_laser_power (self, value):
        self._ins.set_power_level(value)

    # SvD: this function is doing nothing?? -> remove the whole button from the GUI then....
    def set_fine_laser_tuning (self, value):
        voltage = 3*(value-50)/50.
        print "SvD: Setting fine laser tuning is not connected to anything. remove from the gui, or connect."
        #     ### self._ HERE WE SET THE ADWIN VOLTAGE #####

    def set_p1 (self, value):
        self._ins.set_fine_piezo_voltages(v1 = value, v2 = value, v3 = value)
        self.ui.horizontalSlider_p1.setValue (int(value*1000))# (int(10000*(value+2.)/12.))

    def set_slide_p1 (self, value):
        value_V = value/1000. #convert slider position to voltage #12*value/10000.-2.
        self._ins.set_fine_piezo_voltages(v1 = value_V, v2 = value_V, v3 = value_V)
        self.ui.doubleSpinBox_p1.setValue(value_V)
 
    #remove this function; it is now incorporated in the two above.
    # def set_fine_piezos (self, value):
    #     self._moc.set_fine_piezo_voltages (v1 = self.p1_V, v2 = self.p1_V, v3 = self.p1_V)

    def set_pzk_X (self, value):
        self.pzk_X = value

    def set_pzk_Y (self, value):
        self.pzk_Y = value

    def set_pzk_Z (self, value):
        self.pzk_Z = value

    def move_pzk(self):
        """function to move the piezoknobs.
        """
        a = self._ins.status()
        if (self.room_T == None and self.low_T == None):
            msg_text = 'Set temperature before moving PiezoKnobs!'
            ex = panel.MsgBox(msg_text=msg_text)
            ex.show()
        elif (a[:5]=='ERROR'): #SvD: this error handling should perhaps be done in the JPE_CADM instrument itself
            msg_text = 'JPE controller is OFF or in manual mode!'
            ex = panel.MsgBox(msg_text=msg_text)
            ex.show()
        else:
            print 'Current JPE position: ', self._ins.print_current_position(), self._ins.print_tracker_params()
            s1, s2, s3 = self._ins.motion_to_spindle_steps (x=self.pzk_X/1000., y=self.pzk_Y/1000., z=self.pzk_Z/1000., 
                update_tracker=False)

            msg_text = 'Moving the spindles by ['+str(s1)+' , '+str(s2)+' , '+str(s3)+' ] steps. Continue?'
            ex = panel.MsgBox(msg_text=msg_text)
            ex.show()
            print ex.ret
            if (ex.ret==0):
                self._ins.move_spindle_steps (s1=s1, s2=s2, s3=s3, x=self.pzk_X/1000., y=self.pzk_Y/1000., z=self.pzk_Z/1000.)
                self.ui.label_curr_pos_readout.setText('[ '+str(self.pzk_X)+' ,'+str(self.pzk_Y)+' ,'+str(self.pzk_Z)+'] um')
                # self._exp_mngr.update_coarse_piezos (x = self.pzk_X, y = self.pzk_Y, z = self.pzk_Z)

    def pzk_set_as_origin(self):
        self._ins.set_as_origin()
        self.ui.label_curr_pos_readout.setText('[ '+str(0)+' ,'+str(0)+' ,'+str(0)+'] um')

    def use_wavemeter (self):
        if self.ui.checkBox_wavemeter.isChecked():
            self.use_wm = True           
        else:
            self.use_wm = False

    # def update (self):
    #     if self.use_wm:
    #         wm_read = self._wm.Get_FPar (45)
    #         self.ui.label_wavemeter_readout.setText (str(wm_read)+ ' GHz')

    def room_T_button (self):
        if self.ui.radioButton_roomT.isChecked():
            self.ui.radioButton_lowT.setChecked(False)
            self._ins.set_temperature(300)
        else:
            self.ui.radioButton_lowT.setChecked(True)
            self._ins.set_temperature(4)

    def low_T_button (self):
        if self.ui.radioButton_lowT.isChecked():
            self.ui.radioButton_roomT.setChecked(False)
            self._ins.set_temperature(4)
        else:
            self.ui.radioButton_roomT.setChecked(True)
            self._ins.set_temperature(300)

    #I think I don't need these.
    # def fileQuit(self):
    #     print 'Closing!'
    #     self.set_dsb_p1 (0)
    #     self.close()

    # def closeEvent(self, ce):
    #     self.fileQuit()



