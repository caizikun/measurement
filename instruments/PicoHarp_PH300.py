from ctypes import *
import os
from instrument_plugins._Spectrum_M2i2030.errors import errors as _spcm_errors
from instrument_plugins._Spectrum_M2i2030.regs import regs as _spcm_regs
from instrument import Instrument
import pickle
from time import sleep, time
import types
import logging
import numpy
#import Gnuplot
import qt
from qt import *
from numpy import *
from data import Data

LIB_VERSION =  '2.2'    # this is the version this program expects
MAXDEVNUM =      8
TTREADMAX = 131072    # 128K event records 
HISTCHAN  =  65536    # number of histogram channels
RANGES    =      8
MODE_HIST =      0
MODE_T2   =      2
MODE_T3   =      3

FLAG_OVERFLOW = 0x0040
FLAG_FIFOFULL = 0x0003

ZCMIN         =          0    # mV
ZCMAX         =         20    # mV
DISCRMIN      =          0    # mV
DISCRMAX      =        800    # mV
OFFSETMIN     =          0    # ps
OFFSETMAX     = 1000000000    # ps

ACQTMIN       =          1    # ms
ACQTMAX       =   36000000    # ms  (10*60*60*1000ms = 10h)

# Errorcodes from errorcodes.h

PH_ERROR_DEVICE_OPEN_FAIL        = -1;

class PicoHarp_PH300(Instrument): #1
    '''
    This is the driver for the PicoHarp PH300 Time Correlated Single Photon Counting module

    Usage:
    Initialize with
    <name> = qt.instruments.create('name', 'PicoHarp_PH300')
    
    status:
     1) create this driver!=> is never finished
    TODO:
    '''
    def __init__(self, name): #2
        # Initialize wrapper
        logging.info(__name__ + ' : Initializing instrument PH300')
        Instrument.__init__(self, name, tags=['physical'])

        # Load dll and open connection
        self._load_dll()
        sleep(0.01)

        LibraryVersion = numpy.array([8*' '])
        self._PH300_win32.PH_GetLibraryVersion(LibraryVersion.ctypes.data)
        self.LibraryVersion = LibraryVersion
        if LibraryVersion[0][0:3] != LIB_VERSION:
            logging.warning(__name__ + ' : DLL Library supposed to be ver.'+LIB_VERSION+', but found ' + LibraryVersion[0] + 'instead.')

        self.OpenDevice()

        self.add_parameter('Range', flags = Instrument.FLAG_SET, type=types.IntType)
        self.add_parameter('Offset', flags = Instrument.FLAG_SET, type=types.IntType)
        self.add_parameter('SyncDiv', flags = Instrument.FLAG_SET, type=types.IntType)
        self.add_parameter('Resolution', flags = Instrument.FLAG_GET, type=types.IntType)
        self.add_parameter('BaseResolution', flags = Instrument.FLAG_GET, type=types.IntType)
        self.add_parameter('CFDLevel0', flags = Instrument.FLAG_SET, type=types.IntType)
        self.add_parameter('CFDLevel1', flags = Instrument.FLAG_SET, type=types.IntType)
        self.add_parameter('CFDZeroCross0', flags = Instrument.FLAG_SET, type=types.IntType)
        self.add_parameter('CFDZeroCross1', flags = Instrument.FLAG_SET, type=types.IntType)
        self.add_parameter('CountRate0', flags = Instrument.FLAG_GET, type=types.IntType)
        self.add_parameter('CountRate1', flags = Instrument.FLAG_GET, type=types.IntType)
        self.add_parameter('ElapsedMeasTime', flags = Instrument.FLAG_GET, type=types.IntType)
        self.add_parameter('MeasRunning', flags = Instrument.FLAG_GET, type=types.BooleanType)
        self.add_parameter('Flags', flags = Instrument.FLAG_GET, type=types.IntType)
        self.add_parameter('Flag_Overflow', flags = Instrument.FLAG_GET, type=types.BooleanType)
        self.add_parameter('Flag_FifoFull', flags = Instrument.FLAG_GET, type=types.BooleanType)
        self.add_function('start_histogram_mode')
        self.add_function('start_T2_mode')
        self.add_function('start_T3_mode')
        self.add_function('ClearHistMem')
        self.add_function('StartMeas')
        self.add_function('StopMeas')
        self.add_function('OpenDevice')
        self.add_function('CloseDevice')
        self.add_function('GetHistogram')
        self.add_function('get_ErrorString')
        self.add_function('get_TTREADMAX')
        self.start_histogram_mode()


    def _load_dll(self): #3
        print __name__ +' : Loading phlib.dll'
        WINDIR=os.environ['WINDIR']
        self._PH300_win32 = windll.LoadLibrary(WINDIR+'\\System32\\phlib')
        sleep(0.02)

    def _init_continue(self):
        HardwareModel = numpy.array([16*' '])
        HardwareVersion = numpy.array([8*' '])
        if self._PH300_win32.PH_GetHardwareVersion(self.DevIdx, HardwareModel.ctypes.data, HardwareVersion.ctypes.data) != 0:
            logging.warning(__name__ + ' : error getting hardware version')
        if self._PH300_win32.PH_Calibrate(self.DevIdx) != 0:
            logging.warning(__name__ + ' : calibration error')

        self._do_set_CFDLevel(200)
        self._do_set_CFDZeroCross(10)
        self.set_SyncDiv(1)
        self.set_Range(0)
        self.set_Offset(0)
        self._do_set_StopOverflow(0,65535)
        self.get_BaseResolution()
        self.get_Resolution()
        self.get_CountRate0()
        self.get_CountRate1()
        self.get_ElapsedMeasTime()
        self.get_Flag_FifoFull()
        self.get_Flag_Overflow()
        self.get_MeasRunning()
        
    def start_histogram_mode(self):
        if self._PH300_win32.PH_Initialize(self.DevIdx, MODE_HIST) != 0:
            logging.warning(__name__ + ' : Histogramming mode could not be started')
        self._init_continue()

    def start_T2_mode(self):
        if self._PH300_win32.PH_Initialize(self.DevIdx, MODE_T2) != 0:
            logging.warning(__name__ + ' : T2 mode could not be started')
        self._init_continue()

    def get_DeviceType(self):
        return('PH_300')

    def start_T3_mode(self):
        if self._PH300_win32.PH_Initialize(self.DevIdx, MODE_T3) != 0:
            logging.warning(__name__ + ' : T3 mode could not be started')
        self._init_continue()

    def _do_get_BaseResolution(self):
        BaseResolution = self._PH300_win32.PH_GetBaseResolution(self.DevIdx)
        if BaseResolution < 0:
            logging.warning(__name__ + ' : error in PH_GetBaseResolution')
            self.get_ErrorString(BaseResolution)
        self.BaseResolution = BaseResolution
        return self.BaseResolution

    def _do_get_Resolution(self):
        Resolution = self._PH300_win32.PH_GetResolution(self.DevIdx)
        if Resolution < 0:
            logging.warning(__name__ + ' : error in PH_GetResolution')
            self.get_ErrorString(Resolution)
        self.Resolution = Resolution
        return self.Resolution

    def _do_get_CountRate0(self):
        CountRate = self._PH300_win32.PH_GetCountRate(self.DevIdx, 0)
        if CountRate < 0:
            logging.warning(__name__ + ' : error in PH_GetCountRate')
            self.get_ErrorString(CountRate)
        return CountRate

    def _do_get_CountRate1(self):
        CountRate = self._PH300_win32.PH_GetCountRate(self.DevIdx, 1)
        if CountRate < 0:
            logging.warning(__name__ + ' : error in PH_GetCountRate')
            self.get_ErrorString(CountRate)
        return CountRate

    def _do_get_CountRate(self):
        CountRate = self._do_get_CountRate0() + self._do_get_CountRate1()
        return CountRate

    def _do_set_CFDLevel0(self, value):
        success = self._PH300_win32.PH_SetCFDLevel(self.DevIdx, 0, value)
        if success < 0:
            logging.warning(__name__ + ' : error in PH_SetCFDLevel')
            self.get_ErrorString(success)

    def _do_set_CFDLevel1(self, value):
        success = self._PH300_win32.PH_SetCFDLevel(self.DevIdx, 1, value)
        if success < 0:
            logging.warning(__name__ + ' : error in PH_SetCFDLevel')
            self.get_ErrorString(success)

    def _do_set_CFDLevel(self, value):
        self.set_CFDLevel0(value)
        self.set_CFDLevel1(value)

    def _do_set_CFDZeroCross0(self, value):
        success = self._PH300_win32.PH_SetCFDZeroCross(self.DevIdx, 0, value)
        if success < 0:
            logging.warning(__name__ + ' : error in PH_SetCFDZeroCross')
            self.get_ErrorString(success)

    def _do_set_CFDZeroCross1(self, value):
        success = self._PH300_win32.PH_SetCFDZeroCross(self.DevIdx, 1, value)
        if success < 0:
            logging.warning(__name__ + ' : error in PH_SetCFDZeroCross')
            self.get_ErrorString(success)

    def _do_set_CFDZeroCross(self, value):
        self.set_CFDZeroCross0(value)
        self.set_CFDZeroCross1(value)

    def _do_set_SyncDiv(self, div):
        success = self._PH300_win32.PH_SetSyncDiv(self.DevIdx, div)
        if success < 0:
            logging.warning(__name__ + ' : error in PH_SetSyncDiv')
            self.get_ErrorString(success)

    def _do_set_StopOverflow(self, stop_ovfl, stopcount):
        success = self._PH300_win32.PH_SetStopOverflow(self.DevIdx, stop_ovfl, stopcount)
        if success < 0:
            logging.warning(__name__ + ' : error in PH_SetStopOverflow')
            self.get_ErrorString(success)

    def _do_set_Range(self, binsize):  # binsize in 2^n times base resolution (4ps)
        success = self._PH300_win32.PH_SetRange(self.DevIdx, binsize)
        if success < 0:
            logging.warning(__name__ + ' : error in PH_SetRange')
            self.get_ErrorString(success)

    def _do_set_Offset(self, offset):
        success = self._PH300_win32.PH_SetOffset(self.DevIdx, offset)
        if success < 0:
            logging.warning(__name__ + ' : error in PH_SetOffset')
            self.get_ErrorString(success)

    def ClearHistMem(self):
        success = self._PH300_win32.PH_ClearHistMem(self.DevIdx, 0)
        if success < 0:
            logging.warning(__name__ + ' : error in PH_ClearHistMem')
            self.get_ErrorString(success)

    def StartMeas(self,acquisition_time):
        success = self._PH300_win32.PH_StartMeas(self.DevIdx, acquisition_time)
        if success < 0:
            logging.warning(__name__ + ' : error in PH_StartMeas')
            self.get_ErrorString(success)

    def StopMeas(self):
        success = self._PH300_win32.PH_StopMeas(self.DevIdx)
        if success < 0:
            logging.warning(__name__ + ' : error in PH_StopMeas')
            self.get_ErrorString(success)

    def OpenDevice(self):
        SerialNr = numpy.array([8*' '])
        DevIdx = 0
        success = self._PH300_win32.PH_OpenDevice(DevIdx, SerialNr.ctypes.data)
        self.DevIdx = DevIdx
        self.SerialNr = SerialNr
        if success != 0:
            logging.warning(__name__ + ' : OpenDevice failed, maybe PicoHarp software is running.')
            return False
        return True

    def CloseDevice(self):
        success = self._PH300_win32.PH_CloseDevice(self.DevIdx)
        if success < 0:
            logging.warning(__name__ + ' : error in PH_CloseDevice')

    def _do_get_MeasRunning(self):
        running = self._PH300_win32.PH_CTCStatus(self.DevIdx)
        return (running == 0)

    def _do_get_Flags(self):
        return self._PH300_win32.PH_GetFlags(self.DevIdx)
        
    def _do_get_Flag_Overflow(self):
        return self._PH300_win32.PH_GetFlags(self.DevIdx) & FLAG_OVERFLOW == FLAG_OVERFLOW
        
    def _do_get_Flag_FifoFull(self):
        return self._PH300_win32.PH_GetFlags(self.DevIdx) & FLAG_FIFOFULL == FLAG_FIFOFULL
        
    def _do_get_ElapsedMeasTime(self):
        return self._PH300_win32.PH_GetElapsedMeasTime(self.DevIdx)

    def GetHistogram(self):
        data = numpy.array(numpy.zeros(65536), dtype = numpy.uint32)

        success = self._PH300_win32.PH_GetBlock(self.DevIdx,data.ctypes.data,0)
        if success < 0:
            logging.warning(__name__ + ' : error in PH_GetBlock')
        return data

    def get_TTTR_Data(self,count = TTREADMAX):
        data = numpy.array(numpy.zeros(count), dtype = numpy.uint32)
        length = self._PH300_win32.PH_TTReadData(self.DevIdx,data.ctypes.data,count)
        if length < 0:
            logging.warning(__name__ + ' : error in PH_TTReadData')
        return length, data
        
    def set_MarkerEdges(self,me):
        if me == 1:
            me0 = 1
            me1 = 0
        if me == 2:
            me0 = 0
            me1 = 1
        if me == 3:
            me0 = 1
            me1 = 1
        if me == 0:
            me0 = 0
            me1 = 0

        success = self._PH300_win32.PH_TTSetMarkerEdges(self.DevIdx, me0, me1, 0, 0)
        if success < 0:
            logging.warning(__name__ + ' : error in PH_TTSetMarkerEdges')
            
    def TTTR_decode(self, data):
        event_time = numpy.bitwise_and(data, 2**28 - 1) #the lowest 28 bits
        channel = numpy.bitwise_and(numpy.right_shift(data, 28), 2**4 - 1) #the next 4 bits
        special = (channel == 15) #channel bits all one indicates special record
        marker_channel = numpy.bitwise_and(data,2**4 - 1) #only valid for special records
        overflow = special & (marker_channel == 0)       
        return event_time, channel, special, marker_channel, overflow

    def get_ErrorString(self, errorcode):
        ErrorString = numpy.array([40*' '])
        if self._PH300_win32.PH_GetErrorString(ErrorString.ctypes.data, errorcode) != 0:
            logging.warning(__name__ + ' : error in PH_GetErrorString')
        print(ErrorString)
        return ErrorString

    def get_TTREADMAX(self):
        return TTREADMAX