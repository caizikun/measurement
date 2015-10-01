# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'scan_panel.ui'
#
# Created: Mon Jun 01 11:07:27 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)
from measurement.lib.cavity.scan_gui_panels import MsgBox, ScanPlotCanvas


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(958, 708)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        Form.setFont(font)
        self.plot_canvas = ScanPlotCanvas(parent=Form, width=900, height=370)
        self.plot_canvas.setGeometry(QtCore.QRect(20, 0, 921, 371))
        self.plot_canvas.setObjectName(_fromUtf8("graphicsView"))
        self.cb_autosave = QtGui.QCheckBox(Form)
        self.cb_autosave.setGeometry(QtCore.QRect(60, 430, 101, 17))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.cb_autosave.setFont(font)
        self.cb_autosave.setObjectName(_fromUtf8("cb_autosave"))
        self.cb_autostop = QtGui.QCheckBox(Form)
        self.cb_autostop.setGeometry(QtCore.QRect(60, 390, 101, 17))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.cb_autostop.setFont(font)
        self.cb_autostop.setObjectName(_fromUtf8("cb_autostop"))
        self.label_piezoscan = QtGui.QLabel(Form)
        self.label_piezoscan.setGeometry(QtCore.QRect(30, 500, 111, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(12)
        font.setBold(True)
        font.setItalic(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.label_piezoscan.setFont(font)
        self.label_piezoscan.setObjectName(_fromUtf8("label_piezoscan"))
        self.label_minV_ps = QtGui.QLabel(Form)
        self.label_minV_ps.setGeometry(QtCore.QRect(30, 530, 46, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.label_minV_ps.setFont(font)
        self.label_minV_ps.setObjectName(_fromUtf8("label_minV_ps"))
        self.dsb_minV_pzscan = QtGui.QDoubleSpinBox(Form)
        self.dsb_minV_pzscan.setGeometry(QtCore.QRect(110, 530, 62, 22))
        self.dsb_minV_pzscan.setObjectName(_fromUtf8("dsb_minV_pzscan"))
        self.dsb_maxV_pzscan = QtGui.QDoubleSpinBox(Form)
        self.dsb_maxV_pzscan.setGeometry(QtCore.QRect(110, 570, 62, 22))
        self.dsb_maxV_pzscan.setObjectName(_fromUtf8("dsb_maxV_pzscan"))
        self.labelmaxV_pzscan = QtGui.QLabel(Form)
        self.labelmaxV_pzscan.setGeometry(QtCore.QRect(30, 570, 46, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.labelmaxV_pzscan.setFont(font)
        self.labelmaxV_pzscan.setObjectName(_fromUtf8("labelmaxV_pzscan"))
        self.label_avg = QtGui.QLabel(Form)
        self.label_avg.setGeometry(QtCore.QRect(200, 390, 71, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.label_avg.setFont(font)
        self.label_avg.setObjectName(_fromUtf8("label_avg"))
        self.sb_avg = QtGui.QSpinBox(Form)
        self.sb_avg.setGeometry(QtCore.QRect(290, 390, 42, 22))
        self.sb_avg.setObjectName(_fromUtf8("sb_avg"))
        self.label_steps_pzscan = QtGui.QLabel(Form)
        self.label_steps_pzscan.setGeometry(QtCore.QRect(30, 610, 51, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.label_steps_pzscan.setFont(font)
        self.label_steps_pzscan.setObjectName(_fromUtf8("label_steps_pzscan"))
        self.sb_nr_steps_pzscan = QtGui.QSpinBox(Form)
        self.sb_nr_steps_pzscan.setGeometry(QtCore.QRect(110, 610, 61, 22))
        self.sb_nr_steps_pzscan.setObjectName(_fromUtf8("sb_nr_steps_pzscan"))
        self.dsb_minV_finelaser = QtGui.QDoubleSpinBox(Form)
        self.dsb_minV_finelaser.setGeometry(QtCore.QRect(340, 530, 62, 22))
        self.dsb_minV_finelaser.setObjectName(_fromUtf8("dsb_minV_finelaser"))
        self.sb_nr_steps_finelaser = QtGui.QSpinBox(Form)
        self.sb_nr_steps_finelaser.setGeometry(QtCore.QRect(340, 610, 61, 22))
        self.sb_nr_steps_finelaser.setObjectName(_fromUtf8("sb_nr_steps_finelaser"))
        self.label_finescan = QtGui.QLabel(Form)
        self.label_finescan.setGeometry(QtCore.QRect(270, 500, 111, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(12)
        font.setBold(True)
        font.setItalic(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.label_finescan.setFont(font)
        self.label_finescan.setObjectName(_fromUtf8("label_finescan"))
        self.dsb_maxV_finelaser = QtGui.QDoubleSpinBox(Form)
        self.dsb_maxV_finelaser.setGeometry(QtCore.QRect(340, 570, 62, 22))
        self.dsb_maxV_finelaser.setObjectName(_fromUtf8("dsb_maxV_finelaser"))
        self.label_nr_steps_finelaser = QtGui.QLabel(Form)
        self.label_nr_steps_finelaser.setGeometry(QtCore.QRect(270, 610, 51, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.label_nr_steps_finelaser.setFont(font)
        self.label_nr_steps_finelaser.setObjectName(_fromUtf8("label_nr_steps_finelaser"))
        self.label_minV_finelaser = QtGui.QLabel(Form)
        self.label_minV_finelaser.setGeometry(QtCore.QRect(270, 530, 46, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.label_minV_finelaser.setFont(font)
        self.label_minV_finelaser.setObjectName(_fromUtf8("label_minV_finelaser"))
        self.label_maxV__finelaser = QtGui.QLabel(Form)
        self.label_maxV__finelaser.setGeometry(QtCore.QRect(270, 570, 46, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.label_maxV__finelaser.setFont(font)
        self.label_maxV__finelaser.setObjectName(_fromUtf8("label_maxV__finelaser"))
        self.dsb_max_lambda = QtGui.QDoubleSpinBox(Form)
        self.dsb_max_lambda.setGeometry(QtCore.QRect(610, 560, 62, 22))
        self.dsb_max_lambda.setObjectName(_fromUtf8("dsb_max_lambda"))
        self.dsb_min_lambda = QtGui.QDoubleSpinBox(Form)
        self.dsb_min_lambda.setGeometry(QtCore.QRect(610, 530, 62, 22))
        self.dsb_min_lambda.setObjectName(_fromUtf8("dsb_min_lambda"))
        self.label_min_lambda = QtGui.QLabel(Form)
        self.label_min_lambda.setGeometry(QtCore.QRect(490, 530, 111, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.label_min_lambda.setFont(font)
        self.label_min_lambda.setObjectName(_fromUtf8("label_min_lambda"))
        self.label_max_lambda = QtGui.QLabel(Form)
        self.label_max_lambda.setGeometry(QtCore.QRect(490, 560, 111, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.label_max_lambda.setFont(font)
        self.label_max_lambda.setObjectName(_fromUtf8("label_max_lambda"))
        self.label_longrangescan = QtGui.QLabel(Form)
        self.label_longrangescan.setGeometry(QtCore.QRect(490, 500, 181, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(12)
        font.setBold(True)
        font.setItalic(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.label_longrangescan.setFont(font)
        self.label_longrangescan.setObjectName(_fromUtf8("label_longrangescan"))
        self.button_start_pzscan = QtGui.QPushButton(Form)
        self.button_start_pzscan.setGeometry(QtCore.QRect(50, 680, 75, 23))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.button_start_pzscan.setFont(font)
        self.button_start_pzscan.setObjectName(_fromUtf8("button_start_pzscan"))
        self.button_stop_pzscan = QtGui.QPushButton(Form)
        self.button_stop_pzscan.setGeometry(QtCore.QRect(50, 710, 75, 23))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.button_stop_pzscan.setFont(font)
        self.button_stop_pzscan.setObjectName(_fromUtf8("button_stop_pzscan"))
        self.button_stop_finelaser = QtGui.QPushButton(Form)
        self.button_stop_finelaser.setGeometry(QtCore.QRect(290, 680, 75, 23))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.button_stop_finelaser.setFont(font)
        self.button_stop_finelaser.setObjectName(_fromUtf8("button_stop_finelaser"))
        self.button_start_finelaser = QtGui.QPushButton(Form)
        self.button_start_finelaser.setGeometry(QtCore.QRect(290, 650, 75, 23))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.button_start_finelaser.setFont(font)
        self.button_start_finelaser.setObjectName(_fromUtf8("button_start_finelaser"))
        self.button_stop_long_scan = QtGui.QPushButton(Form)
        self.button_stop_long_scan.setGeometry(QtCore.QRect(540, 690, 75, 23))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.button_stop_long_scan.setFont(font)
        self.button_stop_long_scan.setObjectName(_fromUtf8("button_stop_long_scan"))
        self.button_start_long_scan = QtGui.QPushButton(Form)
        self.button_start_long_scan.setGeometry(QtCore.QRect(490, 660, 75, 23))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.button_start_long_scan.setFont(font)
        self.button_start_long_scan.setObjectName(_fromUtf8("button_start_long_scan"))
        self.button_save = QtGui.QPushButton(Form)
        self.button_save.setGeometry(QtCore.QRect(210, 430, 75, 23))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.button_save.setFont(font)
        self.button_save.setObjectName(_fromUtf8("button_save"))
        self.button_calibrate_finelaser = QtGui.QPushButton(Form)
        self.button_calibrate_finelaser.setGeometry(QtCore.QRect(280, 710, 101, 23))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.button_calibrate_finelaser.setFont(font)
        self.button_calibrate_finelaser.setObjectName(_fromUtf8("button_calibrate_finelaser"))
        self.sb_nr_calib_pts = QtGui.QSpinBox(Form)
        self.sb_nr_calib_pts.setGeometry(QtCore.QRect(610, 590, 61, 22))
        self.sb_nr_calib_pts.setObjectName(_fromUtf8("sb_nr_calib_pts"))
        self.label_nr_calib_pts = QtGui.QLabel(Form)
        self.label_nr_calib_pts.setGeometry(QtCore.QRect(490, 590, 111, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.label_nr_calib_pts.setFont(font)
        self.label_nr_calib_pts.setObjectName(_fromUtf8("label_nr_calib_pts"))
        self.button_resume_long_scan = QtGui.QPushButton(Form)
        self.button_resume_long_scan.setGeometry(QtCore.QRect(590, 660, 75, 23))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.button_resume_long_scan.setFont(font)
        self.button_resume_long_scan.setObjectName(_fromUtf8("button_resume_long_scan"))
        self.label_fine_tuning_steps = QtGui.QLabel(Form)
        self.label_fine_tuning_steps.setGeometry(QtCore.QRect(490, 620, 111, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.label_fine_tuning_steps.setFont(font)
        self.label_fine_tuning_steps.setObjectName(_fromUtf8("label_fine_tuning_steps"))
        self.sb_fine_tuning_steps_LRscan = QtGui.QSpinBox(Form)
        self.sb_fine_tuning_steps_LRscan.setGeometry(QtCore.QRect(610, 620, 61, 22))
        self.sb_fine_tuning_steps_LRscan.setObjectName(_fromUtf8("sb_fine_tuning_steps_LRscan"))
        self.label_status = QtGui.QLabel(Form)
        self.label_status.setGeometry(QtCore.QRect(430, 390, 51, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.label_status.setFont(font)
        self.label_status.setObjectName(_fromUtf8("label_status"))
        self.label_status_display = QtGui.QLabel(Form)
        self.label_status_display.setGeometry(QtCore.QRect(480, 390, 461, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_status_display.setFont(font)
        self.label_status_display.setObjectName(_fromUtf8("label_status_display"))
        self.button_timeseries = QtGui.QPushButton(Form)
        self.button_timeseries.setGeometry(QtCore.QRect(760, 530, 141, 23))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.button_timeseries.setFont(font)
        self.button_timeseries.setObjectName(_fromUtf8("button_timeseries"))
        self.button_2D_scan = QtGui.QPushButton(Form)
        self.button_2D_scan.setGeometry(QtCore.QRect(760, 570, 141, 23))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.button_2D_scan.setFont(font)
        self.button_2D_scan.setObjectName(_fromUtf8("button_2D_scan"))
        self.button_track = QtGui.QPushButton(Form)
        self.button_track.setGeometry(QtCore.QRect(760, 610, 141, 23))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.button_track.setFont(font)
        self.button_track.setObjectName(_fromUtf8("button_track"))
        self.label_other_tools = QtGui.QLabel(Form)
        self.label_other_tools.setGeometry(QtCore.QRect(790, 500, 91, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(12)
        font.setBold(True)
        font.setItalic(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.label_other_tools.setFont(font)
        self.label_other_tools.setObjectName(_fromUtf8("label_other_tools"))
        self.label_fileTag = QtGui.QLabel(Form)
        self.label_fileTag.setGeometry(QtCore.QRect(370, 430, 51, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.label_fileTag.setFont(font)
        self.label_fileTag.setObjectName(_fromUtf8("label_fileTag"))
        self.lineEdit_fileName = QtGui.QLineEdit(Form)
        self.lineEdit_fileName.setGeometry(QtCore.QRect(430, 430, 181, 20))
        self.lineEdit_fileName.setObjectName(_fromUtf8("lineEdit_fileName"))
        self.line = QtGui.QFrame(Form)
        self.line.setGeometry(QtCore.QRect(0, 460, 951, 20))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.label_wait_cycles = QtGui.QLabel(Form)
        self.label_wait_cycles.setGeometry(QtCore.QRect(30, 640, 71, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.label_wait_cycles.setFont(font)
        self.label_wait_cycles.setObjectName(_fromUtf8("label_wait_cycles"))
        self.sb_wait_cycles = QtGui.QSpinBox(Form)
        self.sb_wait_cycles.setGeometry(QtCore.QRect(110, 640, 61, 22))
        self.sb_wait_cycles.setObjectName(_fromUtf8("sb_wait_cycles"))
        self.button_slowscan = QtGui.QPushButton(Form)
        self.button_slowscan.setGeometry(QtCore.QRect(760, 650, 141, 23))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Calibri"))
        font.setPointSize(11)
        self.button_slowscan.setFont(font)
        self.button_slowscan.setObjectName(_fromUtf8("button_slowscan"))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.cb_autosave.setText(_translate("Form", "Auto-save", None))
        self.cb_autostop.setText(_translate("Form", "Auto-stop", None))
        self.label_piezoscan.setText(_translate("Form", "Piezo-Scan", None))
        self.label_minV_ps.setText(_translate("Form", "min V", None))
        self.labelmaxV_pzscan.setText(_translate("Form", "max V", None))
        self.label_avg.setText(_translate("Form", "averaging:", None))
        self.label_steps_pzscan.setText(_translate("Form", "nr steps", None))
        self.label_finescan.setText(_translate("Form", "Fine Laser-Scan", None))
        self.label_nr_steps_finelaser.setText(_translate("Form", "nr steps", None))
        self.label_minV_finelaser.setText(_translate("Form", "min V", None))
        self.label_maxV__finelaser.setText(_translate("Form", "max V", None))
        self.label_min_lambda.setText(_translate("Form", "min lambda [nm]", None))
        self.label_max_lambda.setText(_translate("Form", "max lambda [nm]", None))
        self.label_longrangescan.setText(_translate("Form", "Long-Range Laser Scan", None))
        self.button_start_pzscan.setText(_translate("Form", "START", None))
        self.button_stop_pzscan.setText(_translate("Form", "STOP", None))
        self.button_stop_finelaser.setText(_translate("Form", "STOP", None))
        self.button_start_finelaser.setText(_translate("Form", "START", None))
        self.button_stop_long_scan.setText(_translate("Form", "STOP", None))
        self.button_start_long_scan.setText(_translate("Form", "START", None))
        self.button_save.setText(_translate("Form", "SAVE", None))
        self.button_calibrate_finelaser.setText(_translate("Form", "CALIBRATE", None))
        self.label_nr_calib_pts.setText(_translate("Form", "nr calibration pts", None))
        self.button_resume_long_scan.setText(_translate("Form", "RESUME", None))
        self.label_fine_tuning_steps.setText(_translate("Form", "fine-tuning steps", None))
        self.label_status.setText(_translate("Form", "status:", None))
        self.label_status_display.setText(_translate("Form", "idle", None))
        self.button_timeseries.setText(_translate("Form", "Time Series", None))
        self.button_2D_scan.setText(_translate("Form", "2D Scan", None))
        self.button_track.setText(_translate("Form", "TRACK", None))
        self.label_other_tools.setText(_translate("Form", "Other tools", None))
        self.label_fileTag.setText(_translate("Form", "file tag:", None))
        self.label_wait_cycles.setText(_translate("Form", "wait cycles", None))
        self.button_slowscan.setText(_translate("Form", "Slow Piezo Scan", None))

