# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer/lt2_coordinator.ui'
#
# Created: Tue Jan 31 01:31:02 2012
#      by: PyQt4 UI code generator 4.8.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Panel(object):
    def setupUi(self, Panel):
        Panel.setObjectName(_fromUtf8("Panel"))
        Panel.resize(683, 817)
        Panel.setWindowTitle(QtGui.QApplication.translate("Panel", "Form", None, QtGui.QApplication.UnicodeUTF8))
        Panel.setToolTip(_fromUtf8(""))
        Panel.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.gridLayout_2 = QtGui.QGridLayout(Panel)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label_3 = QtGui.QLabel(Panel)
        self.label_3.setText(QtGui.QApplication.translate("Panel", "Keyword", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_2.addWidget(self.label_3, 0, 0, 1, 1)
        self.keyword = QtGui.QLineEdit(Panel)
        self.keyword.setObjectName(_fromUtf8("keyword"))
        self.gridLayout_2.addWidget(self.keyword, 0, 1, 1, 2)
        self.groupBox = QtGui.QGroupBox(Panel)
        self.groupBox.setTitle(QtGui.QApplication.translate("Panel", "Scanner position", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setText(QtGui.QApplication.translate("Panel", "x [um]", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.x = QtGui.QDoubleSpinBox(self.groupBox)
        self.x.setEnabled(True)
        self.x.setMinimum(-100.0)
        self.x.setMaximum(100.0)
        self.x.setSingleStep(0.2)
        self.x.setObjectName(_fromUtf8("x"))
        self.gridLayout.addWidget(self.x, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setText(QtGui.QApplication.translate("Panel", "y [um]", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.y = QtGui.QDoubleSpinBox(self.groupBox)
        self.y.setEnabled(True)
        self.y.setDecimals(2)
        self.y.setMinimum(-100.0)
        self.y.setMaximum(100.0)
        self.y.setSingleStep(0.2)
        self.y.setObjectName(_fromUtf8("y"))
        self.gridLayout.addWidget(self.y, 1, 1, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox, 1, 0, 1, 2)
        self.groupBox_3 = QtGui.QGroupBox(Panel)
        self.groupBox_3.setTitle(QtGui.QApplication.translate("Panel", "z [um]", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_3)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.z = QtGui.QDoubleSpinBox(self.groupBox_3)
        self.z.setMaximum(100.0)
        self.z.setMinimum(-100.0)
        self.z.setSingleStep(0.2)
        self.z.setObjectName(_fromUtf8("z"))
        self.gridLayout_3.addWidget(self.z, 0, 0, 1, 1)
        self.z_slider = QtGui.QSlider(self.groupBox_3)
        self.z_slider.setMaximum(125)
        self.z_slider.setMinimum(-125)
        self.z_slider.setSingleStep(1)
        self.z_slider.setPageStep(100)
        self.z_slider.setProperty("value", 0)
        self.z_slider.setSliderPosition(0)
        self.z_slider.setOrientation(QtCore.Qt.Vertical)
        self.z_slider.setInvertedAppearance(False)
        self.z_slider.setTickPosition(QtGui.QSlider.TicksAbove)
        self.z_slider.setTickInterval(20)
        self.z_slider.setObjectName(_fromUtf8("z_slider"))
        self.gridLayout_3.addWidget(self.z_slider, 1, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox_3, 1, 2, 2, 1)
        self.groupBox_5 = QtGui.QGroupBox(Panel)
        self.groupBox_5.setTitle(QtGui.QApplication.translate("Panel", "Scanner step [um]", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_5.setObjectName(_fromUtf8("groupBox_5"))
        self.gridLayout_5 = QtGui.QGridLayout(self.groupBox_5)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        spacerItem = QtGui.QSpacerItem(72, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_5.addItem(spacerItem, 0, 0, 1, 1)
        self.step_up = QtGui.QPushButton(self.groupBox_5)
        self.step_up.setText(QtGui.QApplication.translate("Panel", "up", None, QtGui.QApplication.UnicodeUTF8))
        self.step_up.setObjectName(_fromUtf8("step_up"))
        self.gridLayout_5.addWidget(self.step_up, 0, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(72, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_5.addItem(spacerItem1, 0, 2, 1, 1)
        self.step_left = QtGui.QPushButton(self.groupBox_5)
        self.step_left.setText(QtGui.QApplication.translate("Panel", "left", None, QtGui.QApplication.UnicodeUTF8))
        self.step_left.setObjectName(_fromUtf8("step_left"))
        self.gridLayout_5.addWidget(self.step_left, 1, 0, 1, 1)
        self.step = QtGui.QDoubleSpinBox(self.groupBox_5)
        self.step.setDecimals(1)
        self.step.setSingleStep(0.1)
        self.step.setProperty("value", 1.0)
        self.step.setObjectName(_fromUtf8("step"))
        self.gridLayout_5.addWidget(self.step, 1, 1, 1, 1)
        self.step_right = QtGui.QPushButton(self.groupBox_5)
        self.step_right.setText(QtGui.QApplication.translate("Panel", "right", None, QtGui.QApplication.UnicodeUTF8))
        self.step_right.setObjectName(_fromUtf8("step_right"))
        self.gridLayout_5.addWidget(self.step_right, 1, 2, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(72, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_5.addItem(spacerItem2, 2, 0, 1, 1)
        self.step_down = QtGui.QPushButton(self.groupBox_5)
        self.step_down.setText(QtGui.QApplication.translate("Panel", "down", None, QtGui.QApplication.UnicodeUTF8))
        self.step_down.setObjectName(_fromUtf8("step_down"))
        self.gridLayout_5.addWidget(self.step_down, 2, 1, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(72, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_5.addItem(spacerItem3, 2, 2, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox_5, 2, 0, 1, 2)

        self.retranslateUi(Panel)
        QtCore.QObject.connect(self.x, QtCore.SIGNAL(_fromUtf8("editingFinished()")), Panel.new_x)
        QtCore.QObject.connect(self.y, QtCore.SIGNAL(_fromUtf8("editingFinished()")), Panel.new_y)
        QtCore.QObject.connect(self.z_slider, QtCore.SIGNAL(_fromUtf8("sliderMoved(int)")), Panel.slide_z)
        QtCore.QObject.connect(self.z, QtCore.SIGNAL(_fromUtf8("editingFinished()")), Panel.new_z)
        QtCore.QObject.connect(Panel, QtCore.SIGNAL(_fromUtf8("z_slide_changed(int)")), self.z_slider.setValue)
        QtCore.QObject.connect(Panel, QtCore.SIGNAL(_fromUtf8("z_changed(double)")), self.z.setValue)
        QtCore.QObject.connect(Panel, QtCore.SIGNAL(_fromUtf8("x_changed(double)")), self.x.setValue)
        QtCore.QObject.connect(Panel, QtCore.SIGNAL(_fromUtf8("y_changed(double)")), self.y.setValue)
        QtCore.QObject.connect(self.keyword, QtCore.SIGNAL(_fromUtf8("textEdited(QString)")), Panel.set_keyword)
        QtCore.QObject.connect(self.step_left, QtCore.SIGNAL(_fromUtf8("clicked()")), Panel.left)
        QtCore.QObject.connect(self.step_up, QtCore.SIGNAL(_fromUtf8("clicked()")), Panel.up)
        QtCore.QObject.connect(self.step_right, QtCore.SIGNAL(_fromUtf8("clicked()")), Panel.right)
        QtCore.QObject.connect(self.step_down, QtCore.SIGNAL(_fromUtf8("clicked()")), Panel.down)
        QtCore.QObject.connect(Panel, QtCore.SIGNAL(_fromUtf8("keyword_changed(QString)")), self.keyword.setText)
        QtCore.QMetaObject.connectSlotsByName(Panel)

    def retranslateUi(self, Panel):
        pass

