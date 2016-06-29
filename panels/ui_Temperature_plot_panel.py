# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\measuring\measurement\panels\designer\temp_controller.ui'
#
# Created: Fri Feb 26 12:13:27 2016
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from chaco_plot import TracePlot
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
        Panel.resize(792, 650)
        # self.gridLayout = QtGui.QGridLayout(Panel)
        # self.gridLayout.setObjectName("gridLayout")
        # self.displayActualTemp = QtGui.QLineEdit(Panel)
        # self.displayActualTemp.setGeometry(QtCore.QRect(20, 70, 71, 20))
        # self.displayActualTemp.setObjectName(_fromUtf8("displayActualTemp"))
        self.scanButton = QtGui.QPushButton(Panel)
        self.scanButton.setGeometry(QtCore.QRect(40, 380, 151, 23))
        self.scanButton.setObjectName(_fromUtf8("scanButton"))
        # self.setTempButton = QtGui.QPushButton(Panel)
        # self.setTempButton.setGeometry(QtCore.QRect(90, 10, 111, 23))
        # self.setTempButton.setObjectName(_fromUtf8("setTempButton"))
        # self.fontComboBox = QtGui.QFontComboBox(Panel)
        # self.fontComboBox.setGeometry(QtCore.QRect(-220, 280, 188, 22))
        # self.fontComboBox.setObjectName(_fromUtf8("fontComboBox"))
        # self.TargetTemp_label = QtGui.QLabel(Panel)
        # self.TargetTemp_label.setGeometry(QtCore.QRect(120, 50, 101, 16))
        # self.TargetTemp_label.setObjectName(_fromUtf8("TargetTemp_label"))
        # self.displayTargetTemp = QtGui.QLineEdit(Panel)
        # self.displayTargetTemp.setGeometry(QtCore.QRect(130, 70, 71, 20))
        # self.displayTargetTemp.setObjectName(_fromUtf8("displayTargetTemp"))
        # self.ActualTemp_label = QtGui.QLabel(Panel)
        # self.ActualTemp_label.setGeometry(QtCore.QRect(10, 50, 101, 16))
        # self.ActualTemp_label.setObjectName(_fromUtf8("ActualTemp_label"))
        # self.resetButton = QtGui.QPushButton(Panel)
        # self.resetButton.setGeometry(QtCore.QRect(30, 95, 151, 23))
        # self.resetButton.setObjectName(_fromUtf8("resetButton"))
        # self.setTemp = QtGui.QDoubleSpinBox(Panel)
        # self.setTemp.setGeometry(QtCore.QRect(20, 10, 62, 22))
        # self.setTemp.setObjectName(_fromUtf8("setTemp"))
        # self.displayDFG = QtGui.QLineEdit(Panel)
        # self.displayDFG.setGeometry(QtCore.QRect(50, 145, 113, 20))
        # self.displayDFG.setObjectName(_fromUtf8("displayDFG"))
        # self.DFG_label = QtGui.QLabel(Panel)
        # self.DFG_label.setGeometry(QtCore.QRect(80, 125, 61, 16))
        # self.DFG_label.setObjectName(_fromUtf8("DFG_label"))
        # self.line = QtGui.QFrame(Panel)
        # self.line.setGeometry(QtCore.QRect(-3, 170, 811, 20))
        # self.line.setFrameShape(QtGui.QFrame.HLine)
        # self.line.setFrameShadow(QtGui.QFrame.Sunken)
        # self.line.setObjectName(_fromUtf8("line"))
        self.scan_label = QtGui.QLabel(Panel)
        self.scan_label.setGeometry(QtCore.QRect(90, 190, 47, 13))
        self.scan_label.setObjectName(_fromUtf8("scan_label"))
        self.dsb_Tmin = QtGui.QDoubleSpinBox(Panel)
        self.dsb_Tmin.setGeometry(QtCore.QRect(110, 230, 62, 22))
        self.dsb_Tmin.setObjectName(_fromUtf8("dsb_Tmin"))
        self.dsb_Tmax = QtGui.QDoubleSpinBox(Panel)
        self.dsb_Tmax.setGeometry(QtCore.QRect(110, 260, 62, 22))
        self.dsb_Tmax.setObjectName(_fromUtf8("dsb_Tmax"))
        self.sb_steps = QtGui.QSpinBox(Panel)
        self.sb_steps.setGeometry(QtCore.QRect(110, 290, 61, 22))
        self.sb_steps.setObjectName(_fromUtf8("sb_steps"))
        self.sb_dwell_time = QtGui.QSpinBox(Panel)
        self.sb_dwell_time.setGeometry(QtCore.QRect(110, 320, 62, 22))
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
        self.dwell_time_label.setGeometry(QtCore.QRect(40, 320, 51, 21))
        self.dwell_time_label.setObjectName(_fromUtf8("dwell_time_label"))
        self.stopButton = QtGui.QPushButton(Panel)
        self.stopButton.setGeometry(QtCore.QRect(40, 420, 151, 23))
        self.stopButton.setObjectName(_fromUtf8("stopButton"))
        self.saveButton = QtGui.QPushButton(Panel)
        self.saveButton.setGeometry(QtCore.QRect(40, 460, 151, 23))
        self.saveButton.setObjectName(_fromUtf8("saveButton"))
        # self.graphicsView = QtGui.QGraphicsView(Panel)
        # self.graphicsView.setGeometry(QtCore.QRect(290, 400, 431, 331))
        # self.graphicsView.setObjectName(_fromUtf8("graphicsView"))
        # self.formLayout = QtGui.QFormLayout()
        # self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        # self.formLayout.setObjectName("formLayout")
        # self.label = QtGui.QLabel(Panel)
        # self.label.setObjectName("label")
        # self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        # self.t_range = QtGui.QSpinBox(Panel)
        # self.t_range.setObjectName("t_range")
        # self.t_range.setGeometry(QtCore.QRect(40, 500, 151, 23))
        # self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.t_range)
        self.plot1 = TracePlot(Panel)
        self.plot1.setMinimumSize(QtCore.QSize(350, 200))
        self.plot1.setGeometry(QtCore.QRect(290, 50, 431, 331))
        self.plot1.setObjectName("plot1")
        # self.gridLayout.addWidget(self.plot1, 0, 1, 1, 1)
        # self.plot2 = TracePlot(Panel)
        # self.plot2.setMinimumSize(QtCore.QSize(350, 200))
        # self.plot2.setGeometry(QtCore.QRect(790, 50, 431, 331))
        # self.plot2.setObjectName("plot2")
        # self.gridLayout.addWidget(self.plot2, 1, 1, 1, 1)

        self.retranslateUi(Panel)       
        # QtCore.QObject.connect(self.t_range, QtCore.SIGNAL("valueChanged(int)"), self.plot1.set_display_time)
        # QtCore.QObject.connect(self.t_range, QtCore.SIGNAL("valueChanged(int)"), self.plot2.set_display_time)
        QtCore.QMetaObject.connectSlotsByName(Panel)

    def retranslateUi(self, Panel):
        Panel.setWindowTitle(_translate("Panel", "Widget", None))
        self.scanButton.setText(_translate("Panel", "Scan", None))
        # self.setTempButton.setText(_translate("Panel", "Set Temperature", None))
        # self.TargetTemp_label.setText(_translate("Panel", "Target Temperature", None))
        # self.ActualTemp_label.setText(_translate("Panel", "Actual Temperature", None))
        # self.DFG_label.setText(_translate("Panel", "DFG power", None))
        self.scan_label.setText(_translate("Panel", "Scan", None))
        self.tmin_label.setText(_translate("Panel", "Tmin", None))
        self.Tmax_label.setText(_translate("Panel", "Tmax", None))
        self.steps_label.setText(_translate("Panel", "#steps", None))
        self.dwell_time_label.setText(_translate("Panel", "dwell time", None))
        self.stopButton.setText(_translate("Panel", "Stop", None))
        self.saveButton.setText(_translate("Panel", "Save", None))
        # self.resetButton.setText(_translate("Panel", "Reset Voltage to 0", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Panel = QtGui.QWidget()
    ui = Ui_Panel()
    ui.setupUi(Panel)
    Panel.show()
    sys.exit(app.exec_())

