# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\measuring\measurement\panels\designer\temp_controller.ui'
#
# Created: Fri Feb 26 12:13:27 2016
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from chaco_plot import TracePlot, TimeTracePlot
from enthought.chaco.api import PlotAxis
# from panel import HugeDisplay

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

class Ui_Panel(object):
    def setupUi(self, Panel):
        Panel.setObjectName(_fromUtf8("Panel"))
        Panel.resize(518, 528)
        self.displayActualTemp = QtGui.QLineEdit(Panel)
        self.displayActualTemp.setGeometry(QtCore.QRect(70, 30, 71, 20))
        self.displayActualTemp.setObjectName(_fromUtf8("displayActualTemp"))
        self.TargetTemp_label = QtGui.QLabel(Panel)
        self.TargetTemp_label.setGeometry(QtCore.QRect(170, 10, 101, 16))
        self.TargetTemp_label.setObjectName(_fromUtf8("TargetTemp_label"))
        self.displayTargetTemp = QtGui.QLineEdit(Panel)
        self.displayTargetTemp.setGeometry(QtCore.QRect(180, 30, 71, 20))
        self.displayTargetTemp.setObjectName(_fromUtf8("displayTargetTemp"))
        self.ActualTemp_label = QtGui.QLabel(Panel)
        self.ActualTemp_label.setGeometry(QtCore.QRect(60, 10, 101, 16))
        self.ActualTemp_label.setObjectName(_fromUtf8("ActualTemp_label"))
        


        self.displayDFG = QtGui.QLineEdit(Panel)
        self.displayDFG.setGeometry(QtCore.QRect(150, 710, 113, 20))
        self.displayDFG.setObjectName(_fromUtf8("displayDFG"))
        self.DFG_label = QtGui.QLabel(Panel)
        self.DFG_label.setGeometry(QtCore.QRect(180, 690, 61, 16))
        self.DFG_label.setObjectName(_fromUtf8("DFG_label"))
        
        # self.line = QtGui.QFrame(Panel)
        # self.line.setGeometry(QtCore.QRect(-3, 170, 811, 20))
        # self.line.setFrameShape(QtGui.QFrame.HLine)
        # self.line.setFrameShadow(QtGui.QFrame.Sunken)
        # self.line.setObjectName(_fromUtf8("line"))
        

       
        self.cleargraphButton2 = QtGui.QPushButton(Panel)
        self.cleargraphButton2.setGeometry(QtCore.QRect(270, 30, 151, 23))
        self.cleargraphButton2.setObjectName(_fromUtf8("cleargraphButton2"))
        self.cleargraphButton3 = QtGui.QPushButton(Panel)
        self.cleargraphButton3.setGeometry(QtCore.QRect(300, 705, 151, 23))
        self.cleargraphButton3.setObjectName(_fromUtf8("cleargraphButton3"))
        
        self.msgBox = QtGui.QMessageBox()
        self.msgBox.setWindowTitle('Warning')
        self.msgBox.setText('Reset temperature to zero voltage temperature before \n starting anything else for the controller!!')
        self.msgBox.show();
        
        # self.gridLayout.addWidget(self.plot1, 0, 1, 1, 1)
        self.plot2 = TimeTracePlot(Panel)
        self.plot2.setMinimumSize(QtCore.QSize(250, 200))
        self.plot2.setGeometry(QtCore.QRect(60, 60, 501, 301))
        self.plot2.setObjectName("plot2")
        # self.plot2.bottom_axis.title = 'Temp [deg]'
        self.plot2.left_axis.title = 'Power [uW]'

        self.plot3 = TimeTracePlot(Panel)
        self.plot3.setMinimumSize(QtCore.QSize(250, 200))
        self.plot3.setGeometry(QtCore.QRect(60, 355, 501, 301))
        self.plot3.setObjectName("plot3")
        # self.plot2.bottom_axis.title = 'Temp [deg]'
        self.plot3.left_axis.title = 'Temp [deg]'
        # self.plot2.marker = 'plus'
        # self.gridLayout.addWidget(self.plot2, 1, 1, 1, 1)

        self.retranslateUi(Panel)       
        # QtCore.QObject.connect(self.t_range, QtCore.SIGNAL("valueChanged(int)"), self.plot1.set_display_time)
        # QtCore.QObject.connect(self.t_range, QtCore.SIGNAL("valueChanged(int)"), self.plot2.set_display_time)
        QtCore.QMetaObject.connectSlotsByName(Panel)

    def retranslateUi(self, Panel):
        Panel.setWindowTitle(_translate("Panel", "Widget", None))
        
        self.TargetTemp_label.setText(_translate("Panel", "Target Temperature", None))
        self.ActualTemp_label.setText(_translate("Panel", "Actual Temperature", None))
        self.DFG_label.setText(_translate("Panel", "DFG power", None))
        
        self.cleargraphButton2.setText(_translate("Panel", "Clear RT Graph", None))
        self.cleargraphButton3.setText(_translate("Panel", "Clear Temp Graph", None))
        

class Ui_Panel2(object):
    def setupUi(self, Panel):
        Panel.setObjectName(_fromUtf8("Panel"))
        Panel.resize(518, 528)

        self.setTempButton = QtGui.QPushButton(Panel)
        self.setTempButton.setGeometry(QtCore.QRect(90, 55, 111, 23))
        self.setTempButton.setObjectName(_fromUtf8("setTempButton"))

        self.resetButton = QtGui.QPushButton(Panel)
        self.resetButton.setGeometry(QtCore.QRect(30, 10, 151, 23))
        self.resetButton.setObjectName(_fromUtf8("resetButton"))
        self.setTemp = QtGui.QDoubleSpinBox(Panel)
        self.setTemp.setGeometry(QtCore.QRect(20, 55, 62, 22))
        self.setTemp.setObjectName(_fromUtf8("setTemp"))

        self.scan_label = QtGui.QLabel(Panel)
        self.scan_label.setGeometry(QtCore.QRect(90, 190, 47, 13))
        self.scan_label.setObjectName(_fromUtf8("scan_label"))
        self.dsb_Tmin = QtGui.QDoubleSpinBox(Panel)
        self.dsb_Tmin.setGeometry(QtCore.QRect(130, 230, 62, 22))
        self.dsb_Tmin.setObjectName(_fromUtf8("dsb_Tmin"))
        self.dsb_Tmax = QtGui.QDoubleSpinBox(Panel)
        self.dsb_Tmax.setGeometry(QtCore.QRect(130, 260, 62, 22))
        self.dsb_Tmax.setObjectName(_fromUtf8("dsb_Tmax"))
        self.sb_steps = QtGui.QSpinBox(Panel)
        self.sb_steps.setGeometry(QtCore.QRect(130, 290, 61, 22))
        self.sb_steps.setObjectName(_fromUtf8("sb_steps"))
        self.sb_dwell_time = QtGui.QSpinBox(Panel)
        self.sb_dwell_time.setGeometry(QtCore.QRect(130, 320, 62, 22))
        self.sb_dwell_time.setObjectName(_fromUtf8("sb_dwell_time"))
        self.tmin_label = QtGui.QLabel(Panel)
        self.tmin_label.setGeometry(QtCore.QRect(40, 230, 47, 21))
        self.tmin_label.setObjectName(_fromUtf8("tmin_label"))
        self.Tmax_label = QtGui.QLabel(Panel)
        self.Tmax_label.setGeometry(QtCore.QRect(40, 260, 47, 21))
        self.Tmax_label.setObjectName(_fromUtf8("Tmax_label"))
        self.steps_label = QtGui.QLabel(Panel)
        self.steps_label.setGeometry(QtCore.QRect(40, 292, 47, 21))
        self.steps_label.setObjectName(_fromUtf8("steps_label"))
        self.dwell_time_label = QtGui.QLabel(Panel)
        self.dwell_time_label.setGeometry(QtCore.QRect(40, 320, 71, 21))
        self.dwell_time_label.setObjectName(_fromUtf8("dwell_time_label"))
        self.stopButton = QtGui.QPushButton(Panel)
        self.stopButton.setGeometry(QtCore.QRect(40, 420, 151, 23))
        self.stopButton.setObjectName(_fromUtf8("stopButton"))
        self.saveButton = QtGui.QPushButton(Panel)
        self.saveButton.setGeometry(QtCore.QRect(40, 460, 151, 23))
        self.saveButton.setObjectName(_fromUtf8("saveButton"))
        self.scanButton = QtGui.QPushButton(Panel)
        self.scanButton.setGeometry(QtCore.QRect(40, 380, 151, 23))
        self.scanButton.setObjectName(_fromUtf8("scanButton"))

        self.plot1 = TracePlot(Panel)
        self.plot1.setMinimumSize(QtCore.QSize(350, 200))
        self.plot1.setGeometry(QtCore.QRect(290, 50, 531, 431))
        self.plot1.setObjectName("plot1")
        self.plot1.bottom_axis.title = 'Temp [deg]'
        self.plot1.left_axis.title = 'Power [uW]'

        self.textEdit = QtGui.QTextEdit(Panel)
        self.textEdit.setGeometry(QtCore.QRect(300, 520, 221, 171))
        self.textEdit.setObjectName(_fromUtf8("GraphAnnotations"))
        self.label_annotations = QtGui.QLabel(Panel)
        self.label_annotations.setGeometry(QtCore.QRect(270, 500, 281, 16))
        self.label_annotations.setObjectName(_fromUtf8("label_annotations"))

        self.lineEdit = QtGui.QLineEdit(Panel)
        self.lineEdit.setGeometry(QtCore.QRect(460, 30, 113, 20))
        self.lineEdit.setObjectName(_fromUtf8("GraphTitle"))
        self.label_graph_title = QtGui.QLabel(Panel)
        self.label_graph_title.setGeometry(QtCore.QRect(460, 10, 201, 16))
        self.label_graph_title.setObjectName(_fromUtf8("label_graph_title"))

        self.cleargraphButton = QtGui.QPushButton(Panel)
        self.cleargraphButton.setGeometry(QtCore.QRect(600, 500, 151, 23))
        self.cleargraphButton.setObjectName(_fromUtf8("cleargraphButton"))

        self.label_warning = QtGui.QLabel(Panel)
        self.label_warning.setGeometry(QtCore.QRect(10, 35, 351, 16))
        self.label_warning.setObjectName(_fromUtf8("label_warning"))

        
        self.retranslateUi(Panel)       
        QtCore.QMetaObject.connectSlotsByName(Panel)

    def retranslateUi(self, Panel):
        Panel.setWindowTitle(_translate("Panel", "Widget", None))
        self.scanButton.setText(_translate("Panel", "Scan", None))
        self.setTempButton.setText(_translate("Panel", "Set Temperature", None))
        self.scan_label.setText(_translate("Panel", "Scan", None))
        self.tmin_label.setText(_translate("Panel", "Tmin", None))
        self.Tmax_label.setText(_translate("Panel", "Tmax", None))
        self.steps_label.setText(_translate("Panel", "#steps", None))
        self.dwell_time_label.setText(_translate("Panel", "dwell time(ms)", None))
        self.stopButton.setText(_translate("Panel", "Stop", None))
        self.saveButton.setText(_translate("Panel", "Save", None))
        self.resetButton.setText(_translate("Panel", "Reset Voltage to 0", None))
        self.cleargraphButton.setText(_translate("Panel", "Clear Graph", None))
        self.label_graph_title.setText(_translate("Panel", "Subtitle of graph when saving", None))
        self.label_annotations.setText(_translate("Panel", "Annotations/comments to add to data file when saving", None))
        self.label_warning.setText(_translate("Panel", "Reset to zero voltage everytime you touch the temperature knob!", None))

# class Ui_Panel3(object):
#     def setupUi(self, Panel):
#         Panel.setObjectName(_fromUtf8("Panel"))
#         Panel.resize(518, 528)

#         # self.scan_label = QtGui.QLabel(Panel)
#         # self.scan_label.setGeometry(QtCore.QRect(90, 190, 47, 13))
#         # self.scan_label.setObjectName(_fromUtf8("scan_label"))
#         # self.dsb_Tmin = QtGui.QDoubleSpinBox(Panel)
#         # self.dsb_Tmin.setGeometry(QtCore.QRect(130, 230, 62, 22))
#         # self.dsb_Tmin.setObjectName(_fromUtf8("dsb_Tmin"))
#         # self.dsb_Tmax = QtGui.QDoubleSpinBox(Panel)
#         # self.dsb_Tmax.setGeometry(QtCore.QRect(130, 260, 62, 22))
#         # self.dsb_Tmax.setObjectName(_fromUtf8("dsb_Tmax"))
#         self.sb_pin_nr = QtGui.QSpinBox(Panel)
#         self.sb_pin_nr.setGeometry(QtCore.QRect(130, 10, 61, 22))
#         self.sb_pin_nr.setObjectName(_fromUtf8("pin_nr"))
#         # self.sb_dwell_time = QtGui.QSpinBox(Panel)
#         # self.sb_dwell_time.setGeometry(QtCore.QRect(130, 320, 62, 22))
#         # self.sb_dwell_time.setObjectName(_fromUtf8("sb_dwell_time"))
#         # self.tmin_label = QtGui.QLabel(Panel)
#         # self.tmin_label.setGeometry(QtCore.QRect(40, 230, 47, 21))
#         # self.tmin_label.setObjectName(_fromUtf8("tmin_label"))
#         # self.Tmax_label = QtGui.QLabel(Panel)
#         # self.Tmax_label.setGeometry(QtCore.QRect(40, 260, 47, 21))
#         # self.Tmax_label.setObjectName(_fromUtf8("Tmax_label"))
#         self.pin_nr_label = QtGui.QLabel(Panel)
#         self.pin_nr_label.setGeometry(QtCore.QRect(40, 12, 47, 21))
#         self.pin_nr_label.setObjectName(_fromUtf8("pin_nr_label"))
#         # self.dwell_time_label = QtGui.QLabel(Panel)
#         # self.dwell_time_label.setGeometry(QtCore.QRect(40, 320, 71, 21))
#         # self.dwell_time_label.setObjectName(_fromUtf8("dwell_time_label"))
#         self.stopButton = QtGui.QPushButton(Panel)
#         self.stopButton.setGeometry(QtCore.QRect(40, 120, 151, 23))
#         self.stopButton.setObjectName(_fromUtf8("stopButton"))
#         self.saveButton = QtGui.QPushButton(Panel)
#         self.saveButton.setGeometry(QtCore.QRect(40, 160, 151, 23))
#         self.saveButton.setObjectName(_fromUtf8("saveButton"))
#         self.sweepButton = QtGui.QPushButton(Panel)
#         self.sweepButton.setGeometry(QtCore.QRect(40, 80, 151, 23))
#         self.sweepButton.setObjectName(_fromUtf8("sweepButton"))

#         self.plot4 = TracePlot(Panel)
#         self.plot4.setMinimumSize(QtCore.QSize(350, 200))
#         self.plot4.setGeometry(QtCore.QRect(290, 20, 531, 431))
#         self.plot4.setObjectName("plot4")
#         self.plot4.bottom_axis.title = 'Voltage [V]'
#         self.plot4.left_axis.title = 'Power [uW]'

#         # self.textEdit = QtGui.QTextEdit(Panel)
#         # self.textEdit.setGeometry(QtCore.QRect(300, 520, 221, 171))
#         # self.textEdit.setObjectName(_fromUtf8("GraphAnnotations"))
#         # self.label_annotations = QtGui.QLabel(Panel)
#         # self.label_annotations.setGeometry(QtCore.QRect(270, 500, 281, 16))
#         # self.label_annotations.setObjectName(_fromUtf8("label_annotations"))

#         # self.lineEdit = QtGui.QLineEdit(Panel)
#         # self.lineEdit.setGeometry(QtCore.QRect(460, 30, 113, 20))
#         # self.lineEdit.setObjectName(_fromUtf8("GraphTitle"))
#         # self.label_graph_title = QtGui.QLabel(Panel)
#         # self.label_graph_title.setGeometry(QtCore.QRect(460, 10, 201, 16))
#         # self.label_graph_title.setObjectName(_fromUtf8("label_graph_title"))

#         self.cleargraphButton4 = QtGui.QPushButton(Panel)
#         self.cleargraphButton4.setGeometry(QtCore.QRect(600, 470, 151, 23))
#         self.cleargraphButton4.setObjectName(_fromUtf8("cleargraphButton4"))

#         # self.label_warning = QtGui.QLabel(Panel)
#         # self.label_warning.setGeometry(QtCore.QRect(10, 35, 351, 16))
#         # self.label_warning.setObjectName(_fromUtf8("label_warning"))

        
#         self.retranslateUi(Panel)       
#         QtCore.QMetaObject.connectSlotsByName(Panel)

#     def retranslateUi(self, Panel):
#         Panel.setWindowTitle(_translate("Panel", "Widget", None))
#         self.sweepButton.setText(_translate("Panel", "Sweep", None))
#         # self.setTempButton.setText(_translate("Panel", "Set Temperature", None))
#         # self.scan_label.setText(_translate("Panel", "Scan", None))
#         # self.tmin_label.setText(_translate("Panel", "Tmin", None))
#         # self.Tmax_label.setText(_translate("Panel", "Tmax", None))
#         self.pin_nr_label.setText(_translate("Panel", "pin_nr", None))
#         # self.dwell_time_label.setText(_translate("Panel", "dwell time(ms)", None))
#         self.stopButton.setText(_translate("Panel", "Stop", None))
#         self.saveButton.setText(_translate("Panel", "Save", None))
#         # self.resetButton.setText(_translate("Panel", "Reset Voltage to 0", None))
#         self.cleargraphButton4.setText(_translate("Panel", "Clear Graph", None))
#         # self.label_graph_title.setText(_translate("Panel", "Subtitle of graph when saving", None))
#         # self.label_annotations.setText(_translate("Panel", "Annotations/comments to add to data file when saving", None))
#         # self.label_warning.setText(_translate("Panel", "Reset to zero voltage everytime you touch the temperature knob!", None))


# if __name__ == "__main__":
#     import sys
#     app = QtGui.QApplication(sys.argv)
#     # Panel = QtGui.QWidget()
#     Panel2 = QtGui.QWidget()
#     # ui = Ui_Panel()
#     ui2 = Ui_Panel2()
#     # ui.setupUi(Panel)
#     ui2.setupUi2(Panel2)
#     # Panel.show()
#     Panel2.show()
#     sys.exit(app.exec_())
