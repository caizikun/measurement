# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer/scan2d.ui'
#
# Created: Mon Feb 21 13:08:35 2011
#      by: PyQt4 UI code generator 4.7.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Panel(object):
    def setupUi(self, Panel):
        Panel.setObjectName("Panel")
        Panel.resize(518, 528)
        self.gridLayout = QtGui.QGridLayout(Panel)
        self.gridLayout.setObjectName("gridLayout")
        self.label_9 = QtGui.QLabel(Panel)
        self.label_9.setObjectName("label_9")
        self.gridLayout.addWidget(self.label_9, 0, 0, 1, 1)
        self.counter = QtGui.QComboBox(Panel)
        self.counter.setObjectName("counter")
        self.counter.addItem("")
        self.counter.addItem("")
        self.counter.addItem("")
        self.counter.addItem("")
        self.gridLayout.addWidget(self.counter, 0, 1, 1, 2)
        spacerItem = QtGui.QSpacerItem(390, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 3, 1, 8)
        self.label = QtGui.QLabel(Panel)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 2, 0, 1, 2)
        self.xstart = QtGui.QDoubleSpinBox(Panel)
        self.xstart.setMinimum(-100.0)
        self.xstart.setMaximum(100.0)
        self.xstart.setProperty("value", -10.0)
        self.xstart.setObjectName("xstart")
        self.gridLayout.addWidget(self.xstart, 2, 2, 1, 2)
        self.label_3 = QtGui.QLabel(Panel)
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 4, 1, 1)
        self.xstop = QtGui.QDoubleSpinBox(Panel)
        self.xstop.setMinimum(-100.0)
        self.xstop.setMaximum(100.0)
        self.xstop.setProperty("value", 10.0)
        self.xstop.setObjectName("xstop")
        self.gridLayout.addWidget(self.xstop, 2, 5, 1, 1)
        self.label_6 = QtGui.QLabel(Panel)
        self.label_6.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 2, 6, 1, 1)
        self.xsteps = QtGui.QSpinBox(Panel)
        self.xsteps.setMinimum(11)
        self.xsteps.setMaximum(1001)
        self.xsteps.setProperty("value", 101)
        self.xsteps.setObjectName("xsteps")
        self.gridLayout.addWidget(self.xsteps, 2, 7, 1, 1)
        self.label_7 = QtGui.QLabel(Panel)
        self.label_7.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 2, 8, 1, 2)
        self.pxtime = QtGui.QSpinBox(Panel)
        self.pxtime.setMinimum(1)
        self.pxtime.setMaximum(10000)
        self.pxtime.setObjectName("pxtime")
        self.gridLayout.addWidget(self.pxtime, 2, 10, 1, 1)
        self.label_2 = QtGui.QLabel(Panel)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 2)
        self.ystart = QtGui.QDoubleSpinBox(Panel)
        self.ystart.setMinimum(-100.0)
        self.ystart.setMaximum(100.0)
        self.ystart.setProperty("value", -10.0)
        self.ystart.setObjectName("ystart")
        self.gridLayout.addWidget(self.ystart, 3, 2, 1, 2)
        self.label_4 = QtGui.QLabel(Panel)
        self.label_4.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 3, 4, 1, 1)
        self.ystop = QtGui.QDoubleSpinBox(Panel)
        self.ystop.setMinimum(-100.0)
        self.ystop.setMaximum(100.0)
        self.ystop.setProperty("value", 10.0)
        self.ystop.setObjectName("ystop")
        self.gridLayout.addWidget(self.ystop, 3, 5, 1, 1)
        self.label_5 = QtGui.QLabel(Panel)
        self.label_5.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 3, 6, 1, 1)
        self.ysteps = QtGui.QSpinBox(Panel)
        self.ysteps.setMinimum(11)
        self.ysteps.setMaximum(1001)
        self.ysteps.setProperty("value", 101)
        self.ysteps.setObjectName("ysteps")
        self.gridLayout.addWidget(self.ysteps, 3, 7, 1, 1)
        self.do_scan = QtGui.QPushButton(Panel)
        self.do_scan.setObjectName("do_scan")
        self.gridLayout.addWidget(self.do_scan, 3, 8, 1, 2)
        self.do_stop = QtGui.QPushButton(Panel)
        self.do_stop.setObjectName("do_stop")
        self.gridLayout.addWidget(self.do_stop, 3, 10, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(120, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 4, 0, 1, 7)
        self.label_8 = QtGui.QLabel(Panel)
        self.label_8.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 4, 7, 1, 2)
        self.zoomsize = QtGui.QDoubleSpinBox(Panel)
        self.zoomsize.setMinimum(1.0)
        self.zoomsize.setProperty("value", 20.0)
        self.zoomsize.setObjectName("zoomsize")
        self.gridLayout.addWidget(self.zoomsize, 4, 9, 1, 1)
        self.do_zoom = QtGui.QPushButton(Panel)
        self.do_zoom.setObjectName("do_zoom")
        self.gridLayout.addWidget(self.do_zoom, 4, 10, 1, 1)
        self.plot = ColorPlot(Panel)
        self.plot.setMinimumSize(QtCore.QSize(500, 400))
        self.plot.setObjectName("plot")
        self.gridLayout.addWidget(self.plot, 1, 0, 1, 11)
        self.label.setBuddy(self.xstart)
        self.label_3.setBuddy(self.xstop)
        self.label_6.setBuddy(self.xsteps)
        self.label_7.setBuddy(self.pxtime)
        self.label_2.setBuddy(self.ystart)
        self.label_4.setBuddy(self.ystop)
        self.label_5.setBuddy(self.ysteps)
        self.label_8.setBuddy(self.zoomsize)

        self.retranslateUi(Panel)
        QtCore.QObject.connect(self.do_scan, QtCore.SIGNAL("clicked()"), Panel.start_scan)
        QtCore.QObject.connect(self.do_zoom, QtCore.SIGNAL("clicked()"), Panel.zoom)
        QtCore.QObject.connect(self.do_stop, QtCore.SIGNAL("clicked()"), Panel.stop_scan)
        QtCore.QMetaObject.connectSlotsByName(Panel)

    def retranslateUi(self, Panel):
        Panel.setWindowTitle(QtGui.QApplication.translate("Panel", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setText(QtGui.QApplication.translate("Panel", "Counter", None, QtGui.QApplication.UnicodeUTF8))
        self.counter.setItemText(0, QtGui.QApplication.translate("Panel", "1", None, QtGui.QApplication.UnicodeUTF8))
        self.counter.setItemText(1, QtGui.QApplication.translate("Panel", "2", None, QtGui.QApplication.UnicodeUTF8))
        self.counter.setItemText(2, QtGui.QApplication.translate("Panel", "3", None, QtGui.QApplication.UnicodeUTF8))
        self.counter.setItemText(3, QtGui.QApplication.translate("Panel", "4", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Panel", "x start [um]", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Panel", "x stop [um]", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("Panel", "px", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("Panel", "px time[ms]", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Panel", "y start [um]", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Panel", "y stop [um]", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("Panel", "px", None, QtGui.QApplication.UnicodeUTF8))
        self.do_scan.setText(QtGui.QApplication.translate("Panel", "Scan", None, QtGui.QApplication.UnicodeUTF8))
        self.do_stop.setText(QtGui.QApplication.translate("Panel", "Stop", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("Panel", "zoom size [um]", None, QtGui.QApplication.UnicodeUTF8))
        self.do_zoom.setText(QtGui.QApplication.translate("Panel", "Zoom", None, QtGui.QApplication.UnicodeUTF8))

from chaco_plot import ColorPlot
