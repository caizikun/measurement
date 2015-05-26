########################################
# Cristian Bonato, 2015
# cbonato80@gmail.com
########################################

from __future__ import unicode_literals
import os, sys, time
from PySide.QtCore import *
from PySide.QtGui import *
import random
from matplotlib.backends import qt4_compat
use_pyside = qt4_compat.QT_API == qt4_compat.QT_API_PYSIDE
if use_pyside:
    from PySide import QtGui, QtCore, uic
else:
    from PyQt4 import QtGui, QtCore, uic

import pylab as plt
import h5py
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from measurement.lib.cavity.cavity_scan import CavityScan 
from control_panel_2 import Ui_Dialog as Ui_Form


class MsgBox(QtGui.QDialog):
    def __init__(self, msg_text = 'What to do?', parent=None):
        super(MsgBox, self).__init__(parent)

        msgBox = QtGui.QMessageBox()
        msgBox.setText(msg_text)
        msgBox.addButton(QtGui.QPushButton('Accept'), QtGui.QMessageBox.YesRole)
        msgBox.addButton(QtGui.QPushButton('Reject'), QtGui.QMessageBox.NoRole)
        self.ret = msgBox.exec_();

class MyCanvas(FigureCanvas):

    def __init__(self,  scan_manager, status_label, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        # Clear axes every time plot() is called
        self.axes.hold(False)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self._scan_manager = scan_manager
        self._status_label = status_label
        self.refresh_time = 100
        self.name = self._scan_manager.name
        self._task = None

    def save(self):
        if self.name:
            name = '_'+self.name
        else:
            name = ''
        time_stamp = time.strftime ('%Y%m%d_%H%M%S')
        fName = time_stamp + '_scan_'+self._task
        f0 = os.path.join('D:/measuring/data/', time.strftime('%Y%m%d'))
        directory = os.path.join(f0, fName)

        if not os.path.exists(directory):
            os.makedirs(directory)

        f = plt.figure()
        ax = f.add_subplot(1,1,1)
        ax.plot (self._scan_manager.v_for_saving, self._scan_manager.PD_for_saving, '.b', linewidth = 2)
        ax.set_xlabel ('voltage [V]')
        ax.set_ylabel ('photodiode signal [a.u.]')
        ax.set_title (time_stamp)
        f.savefig(os.path.join(directory, fName+'.png'))
        
        f = h5py.File(os.path.join(directory, fName+'.hdf5'))
        #f.attrs ['laser_power'] = self._laserscan.laser_power
        #f.attrs ['laser_wavelength'] = self._laserscan.laser_wavelength
        scan_grp = f.create_group('laserscan')
        scan_grp.create_dataset('V', data = self._scan_manager.v_for_saving)
        scan_grp.create_dataset('PD_signal', data = self._scan_manager.PD_for_saving)
        #scan_grp.create_dataset('wm_frequency', data = self._scan_manager.frequencies)
        f.close()



class ScanCanvas(MyCanvas):

    def __init__(self, *args, **kwargs):
        MyCanvas.__init__(self, *args, **kwargs)
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_plot)
        timer.start(self.refresh_time)

    def update_laserscan(self):
        self._status_label.setText("<font style='color: red;'>SCANNING LASER</font>")
        self._task = 'laser'
        self._scan_manager.laser_scan(use_wavemeter = self.use_wm, fine_scan=True, avg_nr_samples = self.averaging_samples)
        #self.random_noise = 0*0.1*np.random.rand(len(self._laserscan.v_vals))
        if self.use_wm:
            print 'Use_wm!!'
            self.axes.plot(self._scan_manager.frequencies, self._scan_manager.PD_signal, '.b', linewidth =2)
            self.axes.set_xlabel ('frequency [GHz]')
        else:
            self.axes.plot(self._scan_manager.v_vals, self._scan_manager.PD_signal, '.b', linewidth =2)
            self.axes.set_xlabel ('voltage [V]')            
        self.axes.set_ylabel('photodiode signal [a.u.]')
        self.axes.set_ylim ([min(self._scan_manager.PD_signal), max(self._scan_manager.PD_signal)])
        self._scan_manager.v_for_saving = self._scan_manager.v_vals
        self._scan_manager.PD_for_saving = self._scan_manager.PD_signal        
        self.draw()
        if self.autosave:
            print "Saving..."
            self.save()
        if self.autostop:
            self.scan_laser_running = False

    def calibrate_laser_frequency(self):
        self._status_label.setText("<font style='color: red;'>CALIBRATION... please wait!</font>")
        self._scan_manager.laser_scan(use_wavemeter = True, fine_scan = True)
        self.calibrate = False
        self._status_label.setText("<font style='color: red;'>IDLE</font>")

        if self.name:
            name = '_'+self.name
        else:
            name = ''
        fName = time.strftime ('%Y%m%d_%H%M%S')+ '_laser_calib'+name
        f0 = os.path.join('D:/measuring/data/', time.strftime('%Y%m%d'))
        directory = os.path.join(f0, fName)

        if not os.path.exists(directory):
            os.makedirs(directory)

        f = plt.figure()
        ax = f.add_subplot(1,1,1)
        ax.plot (self._scan_manager.v_vals, self._scan_manager.frequencies, '.b', linewidth =2)
        ax.set_xlabel ('voltage [V]')
        ax.set_ylabel ('laser frequency [GHz]')
        f.savefig(os.path.join(directory, fName+'.png'))
        
        f5 = h5py.File(os.path.join(directory, fName+'.hdf5'))
        #f.attrs ['laser_power'] = self._laserscan.laser_power
        #f.attrs ['laser_wavelength'] = self._laserscan.laser_wavelength
        scan_grp = f5.create_group('calibration')
        scan_grp.create_dataset('V', data = self._scan_manager.v_vals)
        scan_grp.create_dataset('freq_GHz', data = self._scan_manager.frequencies)
        f5.close()
        plt.show()


    def update_piezoscan(self):
        # Build a list of 4 random integers between 0 and 10 (both inclusive)
        self._task = 'piezos'
        continuous_saving = True
        self._status_label.setText("<font style='color: red;'>SCANNING PIEZOs</font>")
        self._scan_manager.initialize_piezos(wait_time=1)
        self._scan_manager.piezo_scan(avg_nr_samples=self.averaging_samples)
        self.axes.plot(self._scan_manager.v_vals, self._scan_manager.PD_signal, '.b', linewidth =2)
        self.axes.set_xlabel ('piezo voltage')
        self.axes.set_ylabel('photodiode signal [a.u.]')
        self.axes.set_ylim ([min(self._scan_manager.PD_signal), max(self._scan_manager.PD_signal)])
        self._scan_manager.v_for_saving = self._scan_manager.v_vals
        self._scan_manager.PD_for_saving = self._scan_manager.PD_signal        
        #plt.tight_layout()
        self.draw()
        if self.autosave:
            self.save()
        if self.autostop:
            self.scan_piezo_running = False

    def update_plot(self):
        if self.scan_piezo_running:
            self.update_piezoscan()
        elif self.scan_laser_running:
            self.update_laserscan()
        elif self.calibrate:
            self.calibrate_laser_frequency()
        else:
            self._status_label.setText("<font style='color: red;'>IDLE</font>")



class ScanGUI(QtGui.QMainWindow):
    def __init__(self, scan_manager):
        QtGui.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("Laser-Piezo Scan Interface")

        self.file_menu = QtGui.QMenu('&File', self)
        self.file_menu.addAction('&Save', self.fileSave,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_S)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)
        self.main_widget = QtGui.QWidget(self)

        l = QtGui.QGridLayout(self.main_widget)

        self.status_label = QtGui.QLabel ('IDLE')
        font = QtGui.QFont()
        font.setBold(True)
        #font.setHeight(105)
        self.status_label.setFont(font)
        self.status_label.setText("<font style='color: red;'>IDLE</font>")
        l.addWidget (self.status_label, 10, 2)
        #self.setLayout (l)
        self.dc = ScanCanvas(parent=self.main_widget, width=5, height=4, dpi=100, scan_manager = scan_manager, status_label = self.status_label)
        l.addWidget(self.dc, 0, 0, 4, 4)
        self.btn_scan_laser = QtGui.QPushButton('Scan laser', self)
        self.btn_scan_laser.clicked.connect(self.scan_laser)
        l.addWidget(self.btn_scan_laser, 4,0)
        self.btn_scan_piezos = QtGui.QPushButton('Scan piezos', self)
        self.btn_scan_piezos.clicked.connect(self.scan_piezos)
        l.addWidget(self.btn_scan_piezos,4,1)
        self.btn_stop = QtGui.QPushButton('Stop scan', self)
        self.btn_stop.clicked.connect(self.stop_scan)
        l.addWidget(self.btn_stop,4,2)
        self.btn_calibr = QtGui.QPushButton('Calibration', self)
        self.btn_calibr.clicked.connect(self.calibration)
        l.addWidget(self.btn_calibr,4,3)
        self.cb_autosave = QtGui.QCheckBox('Auto-save', self)
        self.cb_autosave.stateChanged.connect(self.autosave)
        l.addWidget(self.cb_autosave,6,0)
        self.cb_autostop = QtGui.QCheckBox('Auto-stop', self)
        self.cb_autostop.stateChanged.connect(self.autostop)
        l.addWidget(self.cb_autostop,6,1)
        self.cb_normalize = QtGui.QCheckBox('Normalize', self)
        self.cb_normalize.stateChanged.connect(self.normalize)
        l.addWidget(self.cb_normalize,6,2)
        self.cb_coarse = QtGui.QCheckBox('coarse (freq laser scan)', self)
        self.cb_coarse.stateChanged.connect(self.laser_scan_type)
        l.addWidget(self.cb_coarse,6,3)
        self.v_min_box = QtGui.QDoubleSpinBox()
        self.v_min_box.setRange (-10, 10)
        self.v_min_box.setDecimals (3)        
        self.v_min_box.setSingleStep (0.001)
        self.v_min_box.setSuffix(' V')
        self.v_min_box.setValue(0)
        self.v_min_box.valueChanged.connect(self.set_V_min)
        l.addWidget (self.v_min_box, 8, 0)
        self.v_max_box = QtGui.QDoubleSpinBox()
        self.v_max_box.setRange (-10, 10)
        self.v_max_box.setDecimals (3)        
        self.v_max_box.setSingleStep (0.001)
        self.v_max_box.setSuffix(' V')
        self.v_max_box.setValue(4)
        self.v_max_box.valueChanged.connect(self.set_V_max)
        l.addWidget (self.v_max_box, 8, 1)
        self.nr_steps_box = QtGui.QSpinBox()
        self.nr_steps_box.setRange (1, 999)
        self.nr_steps_box.setSingleStep (1)
        self.nr_steps_box.setValue(10)
        self.nr_steps_box.valueChanged.connect(self.set_nr_steps)
        l.addWidget (self.nr_steps_box, 8, 2)
        self.avg_box = QtGui.QSpinBox()
        self.avg_box.setRange (1, 999)
        self.avg_box.setSingleStep (1)
        self.avg_box.setValue(1)
        self.avg_box.valueChanged.connect(self.set_avg)
        l.addWidget (self.avg_box, 8, 3)

        self.qlb1 = QtGui.QLabel ('min voltage')
        l.addWidget (self.qlb1, 9, 0) 
        self.qlb2 = QtGui.QLabel ('max voltage')
        l.addWidget (self.qlb2, 9, 1)
        self.qlb3 = QtGui.QLabel ('nr steps')
        l.addWidget (self.qlb3, 9, 2)
        self.qlb3 = QtGui.QLabel ('averaging (nr samples)')
        l.addWidget (self.qlb3, 9, 3)


        self.qlb4 = QtGui.QLabel ('status:')
        self.qlb4.setAlignment(QtCore.Qt.AlignRight)
        l.addWidget (self.qlb4, 10, 1)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.dc.scan_piezo_running = False
        self.dc.scan_laser_running = False
        self.dc.calibrate = False
        self.dc.coarse = False
        self.dc.use_wm = False
        self.dc.averaging_samples = 1
        self.dc.autosave = False
        self.dc.autostop = False


    def fileQuit(self):
        self.close()

    def fileSave(self):
        self.dc.save()

    def closeEvent(self, ce):
        self.fileQuit()

    def set_avg (self, value):
        self.dc.averaging_samples = value
        print 'Averaging changed...', self.dc.averaging_samples

    def scan_laser(self):
        if self.dc.coarse:
            if (self.dc._scan_manager.V_min < 0.1):
                msg_text = 'Min_V should be larger than 0.1V!'
                ex = MsgBox(msg_text=msg_text)
                ex.show()
                self.dc.scan_laser_running = False
            elif (self.dc._scan_manager.V_max >10):
                msg_text = 'Max_V should not exceed 10V!'
                ex = MsgBox(msg_text=msg_text)
                ex.show()
                self.dc.scan_laser_running = False
            else:
                self.dc.scan_laser_running = True

        else:
            if (self.dc._scan_manager.V_min <-3):
                msg_text = 'Min_V should be larger than -3V!'
                ex = MsgBox(msg_text=msg_text)
                ex.show()
                self.dc.scan_laser_running = False
            elif (self.dc._scan_manager.V_max > 3):
                msg_text = 'Max_V should not exceed 3V!'
                ex = MsgBox(msg_text=msg_text)
                ex.show()
                self.dc.scan_laser_running = False
            else:
                self.dc.scan_laser_running = True


    def scan_piezos(self):
        if (self.dc._scan_manager.V_min <-2):
            msg_text = 'Min_V should be larger than -2V!'
            ex = MsgBox(msg_text=msg_text)
            ex.show()
        elif (self.dc._scan_manager.V_max >10):
            msg_text = 'Min_V should be larger than 0.1V!'
            ex = MsgBox(msg_text=msg_text)
            ex.show()
        else:
            self.dc.scan_piezo_running = True




    def stop_scan(self):
        self.dc.scan_laser_running = False
        self.dc.scan_piezo_running = False


    def calibration(self):
        self.dc.scan_laser_running = False
        self.dc.scan_piezo_running = False
        self.dc.calibrate = True

    def autosave (self, state):
        if state == QtCore.Qt.Checked:
                self.dc.autosave = True
        else:
            self.dc.autosave = False

    def autostop (self, state):
        if state == QtCore.Qt.Checked:
            self.dc.autostop = True
        else:
            self.dc.autostop = False

    def normalize (self, state):
        if state == QtCore.Qt.Checked:
            self.dc.normalize = True
        else:
            self.dc.normalize = False

    def laser_scan_type (self, state):
        if state == QtCore.Qt.Checked:
            self.dc.coarse = True
        else:
            self.dc.coarse = False

    def set_V_min (self, value):
        self.dc._scan_manager.V_min = value

    def set_V_max (self, value):
        self.dc._scan_manager.V_max = value

    def set_nr_steps (self, value):
        self.dc._scan_manager.nr_V_steps = value


class ControlPanelGUI (QtGui.QMainWindow):
    def __init__(self, master_of_cavity, wavemeter, laser, parent=None):

        self._moc = master_of_cavity
        self._wm = wavemeter
        self._laser = laser
        QtGui.QWidget.__init__(self, parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        #self.setWindowTitle("Laser-Piezo Scan Interface")
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.p1_V = 0
        self.p2_V = 0
        self.p3_V = 0
        self.piezo_locked = False
        self.pzk_X = self._moc._jpe_tracker.curr_x*1000
        self.pzk_Y = self._moc._jpe_tracker.curr_y*1000
        self.pzk_Z = self._moc._jpe_tracker.curr_z*1000
        self.use_wm = False
        self.room_T = None
        self.ui.label_curr_pos_readout.setText('[ '+str(self.pzk_X)+' ,'+str(self.pzk_Y)+' ,'+str(self.pzk_Z)+'] um')

        #Set all parameters and connect all events to actions
        # LASER
        self.ui.dSBox_coarse_lambda.setRange (635.00, 640.00)
        self.ui.dSBox_coarse_lambda.setSingleStep (0.01)
        self.ui.dSBox_coarse_lambda.setValue(637.0)
        self.ui.dSBox_coarse_lambda.valueChanged.connect(self.set_laser_coarse)
        self.ui.dsBox_fine_laser_tuning.setDecimals(1)
        self.ui.dsB_power.setRange (0.0, 15.0)
        self.ui.dsB_power.setSingleStep(0.1)     
        self.ui.dsB_power.setValue(0)   
        self.ui.dsB_power.valueChanged.connect(self.set_laser_power)
        self.ui.dsBox_fine_laser_tuning.setRange (0, 100)
        self.ui.dsBox_fine_laser_tuning.setDecimals(2)
        self.ui.dsBox_fine_laser_tuning.setSingleStep(0.01)
        self.ui.dsBox_fine_laser_tuning.setValue(50)
        self.ui.dsBox_fine_laser_tuning.valueChanged.connect(self.set_fine_laser_tuning)
        self.set_laser_coarse(637.0)
        self.set_laser_power(0)
        self.set_fine_laser_tuning(50)

        # FINE PIEZOS
        self.ui.doubleSpinBox_p1.setRange (-2, 10)
        self.ui.doubleSpinBox_p1.setDecimals (3)        
        self.ui.doubleSpinBox_p1.setSingleStep (0.001)
        self.ui.doubleSpinBox_p1.setValue(self.p1_V)
        self.ui.doubleSpinBox_p1.valueChanged.connect(self.set_dsb_p1)
        self.ui.horizontalSlider_p1.setRange (0, 10000)
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

        self.refresh_time = 100

        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_wm)
        timer.start(self.refresh_time)

        a = self._moc.status()
        if (a[:5]=='ERROR'):
            msg_text = 'JPE controller is OFF!'
            ex = MsgBox(msg_text=msg_text)
            ex.show()


    def set_laser_coarse (self, value):
        self._laser.set_wavelength (wavelength=value)

    def set_laser_power (self, value):
        self._laser.set_power_level (power=value)

    def set_fine_laser_tuning (self, value):
        voltage = 3*(value-50)/50.
        ### self._ HERE WE SET THE ADWIN VOLTAGE #####

    def set_dsb_p1 (self, value):
        self.set_fine_piezos (value)
        self.ui.horizontalSlider_p1.setValue (int(10000*(value+2.)/12.))

    def set_fine_piezos (self, value):
        self.p1_V = value
        self._moc.set_fine_piezo_voltages (v1 = self.p1_V, v2 = self.p1_V, v3 = self.p1_V)

    def set_hsl_p1 (self, value):
        value_V = 12*value/10000.-2.
        self.ui.doubleSpinBox_p1.setValue(value_V)
        self.set_fine_piezos (value_V)

    def set_pzk_X (self, value):
        self.pzk_X = value

    def set_pzk_Y (self, value):
        self.pzk_Y = value

    def set_pzk_Z (self, value):
        self.pzk_Z = value

    def move_pzk(self):
        if (self.room_T == None):
            msg_text = 'Set temperature before moving PiezoKnobs!'
            ex = MsgBox(msg_text=msg_text)
            ex.show()
        else:
            s1, s2, s3 = self._moc.motion_to_spindle_steps (x=self.pzk_X/1000., y=self.pzk_Y/1000., z=self.pzk_Z/1000.)
            msg_text = 'Moving the spindles by ['+str(s1)+' , '+str(s2)+' , '+str(s3)+' ] steps. Continue?'
            ex = MsgBox(msg_text=msg_text)
            ex.show()
            if (ex.ret==0):
                self._moc.move_spindle_steps (s1=s1, s2=s2, s3=s3, x=self.pzk_X/1000., y=self.pzk_Y/1000., z=self.pzk_Z/1000.)
                self.ui.label_curr_pos_readout.setText('[ '+str(self.pzk_X)+' ,'+str(self.pzk_Y)+' ,'+str(self.pzk_Z)+'] um')

    def pzk_set_as_origin(self):
        self._moc_set_as_origin()
        self.ui.label_curr_pos_readout.setText('[ '+str(0)+' ,'+str(0)+' ,'+str(0)+'] um')

    def use_wavemeter (self):
        if self.ui.checkBox_wavemeter.isChecked():
            self.use_wm = True           
        else:
            self.use_wm = False

    def update_wm (self):
        if self.use_wm:
            wm_read = self._wm.Get_FPar (45)
            self.ui.label_wavemeter_readout.setText (str(wm_read)+ ' GHz')

    def room_T_button (self):
        if self.ui.radioButton_roomT.isChecked():
            self.room_T =  True
            self.ui.radioButton_lowT.setChecked(False)
            self._moc.set_temperature(300)
        else:
            self.room_T =  False
            self.ui.radioButton_lowT.setChecked(True)
            self._moc.set_temperature(4)

    def low_T_button (self):
        if self.ui.radioButton_lowT.isChecked():
            self.room_T =  False
            self.ui.radioButton_roomT.setChecked(False)
            self._moc.set_temperature(4)
        else:
            self.room_T =  True
            self.ui.radioButton_roomT.setChecked(True)
            self._moc.set_temperature(300)

    def fileQuit(self):
        print 'Closing!'
        self.set_dsb_p1 (0)
        self.set_laser_power(0)
        self.set_fine_laser_tuning(0)
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

#adwin = qt.instruments.get_instruments()['adwin']
wm_adwin = qt.instruments.get_instruments()['physical_adwin_cav1']
moc = qt.instruments.get_instruments()['master_of_cavity']
newfocus = qt.instruments.get_instruments()['newfocus1']

qApp = QtGui.QApplication(sys.argv)
lc = CavityScan (name='test')
lc.set_laser_params (wavelength = 637.1, power = 5)
lc.set_scan_params (v_min=0.02, v_max=4, nr_points=100)

aw_scan = ScanGUI(scan_manager = lc)
aw_scan.setWindowTitle('Laser & Piezo Scan Interface')
aw_scan.show()

aw_ctrl = ControlPanelGUI(master_of_cavity = moc, wavemeter = wm_adwin, laser=newfocus)
aw_ctrl.setWindowTitle ('Control Panel')
aw_ctrl.show()
sys.exit(qApp.exec_())
