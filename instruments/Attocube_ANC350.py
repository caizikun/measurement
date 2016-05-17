from ctypes import *
import os
from instrument import Instrument
import pickle
from time import sleep, time
import types
import logging
import numpy
import qt
from qt import *
from numpy import *
from data import Data

class PositionerInfo(Structure):
    _fields_ = [("id", c_int),
                ("locked", c_bool)]

class Attocube_ANC350(Instrument): #1
    '''
    This is the driver for the Attocube ANC_350 controller

    Usage:
    Initialize with
    <name> = qt.instruments.create('name', 'Attocube_ANC350')
    
    status:
     1) works, but problem in combination with eg qutau
    TODO:
     2) expand and test functions below "not tested yet:"
    '''

    _error_codes = ['OK','timeout','not connected over USB', 'driver error', 'boot ignored', 
                   'file not found', 'invalid parameter', 'device locked', 
                   'not specified parameter', 'unknown error']

    def __init__(self, name, dev_no=0): #2
         # Initialize wrapper
        logging.info(__name__ + ' : Initializing instrument ANC_350')
        Instrument.__init__(self, name, tags=['physical'])

        # Load dll and open connection
        self._load_dll()
        sleep(0.01)
        self.Connect(dev_no)

        self.add_function('Connect')
        self.add_function('Close')
        self.add_function('GetPosition')
        self.add_function('MoveNSteps')
       

        # not tested yet:
        # self.add_function('GetReference')
        # self.add_function('ResetPosition')
        # self.add_function('GetStatus')
        # self.add_function('SetOutput')
        # self.add_function('DcInEnable')
        # self.add_function('AcInEnable')
        # self.add_function('IntEnable')
        # self.add_function('BandwidthLimitEnable')
        # self.add_function('GetDcInEnable')
        # self.add_function('')
        # self.add_function('')
        # self.add_function('')
        # self.add_function('')
        # self.add_function('')
        


#        self.add_parameter('Wavelength', flags = Instrument.FLAG_GET, type=types.FloatType)
#        self.add_parameter('Frequency', flags = Instrument.FLAG_GET, type=types.FloatType)

    def _load_dll(self): #3
        logging.info(self._log_text('Loading hvpositionerv2.dll'))
        self._attodll = windll.LoadLibrary(qt.config['anc350_dll']) 
        # this folder should also be added to the windows path variable, 
        # see eg Search Path Used by Windows to Locate a DLL 
        # https://msdn.microsoft.com/en-us/library/7d83bc18.aspx

    def Connect(self, dev_no):
        p_info = PositionerInfo()
        dev_count = self._attodll.PositionerCheck(byref(p_info))
        print dev_count, p_info.id, p_info.locked#
        logging.info(self._log_text('found {:d} devices'.format(dev_count)))
        if dev_count > 0:
            logging.info(self._log_text('attempting to connect to device {:d}'.format(dev_no)))
            self._device = c_int(0)
            status = self._attodll.PositionerConnect(dev_no,byref(self._device))
            sleep(0.02)
            self._handle_error(status)
            logging.info(self._log_text('connected'))

    def _log_text(self,text):
        return self.get_name() + ': ' + str(text)

    def _handle_error(self,status):
        if status == 0:
            return True #No errors!
        elif status > 0  and status <= 8:
            logging.warning(self._log_text('error {:d}; {}'.format(status,self._error_codes[status])))
        else:
            logging.warning(self._log_text('error {:d}; Unknown error'.format(status)))
        return False

    def Close(self):
        status = self._attodll.PositionerClose(self._device)
        self._handle_error(status)

    def remove(self):
        self.Close()
        Instrument.remove(self)

    def reload(self):
        self.Close()
        Instrument.reload(self)

    def GetPosition(self,axis):
        '''
        Returns the position of the given axis in um
        '''
        Position = c_int(0)
        self._attodll.PositionerGetPosition(self._device,c_int(axis),byref(Position))
        return float(Position.value)/1000.

    def MoveNSteps(self,axis, direction, steps):
        '''
        Move given axis given number of steps in given direction (0:forward/1:backward)
        '''
        status = self._attodll.PositionerStepCount(self._device,c_int(axis),c_int(steps))
        if self._handle_error(status):
            status = self._attodll.PositionerMoveSingleStep(self._device,c_int(axis),c_int(direction))
            self._handle_error(status)

    

    # not tested yet:   

    def MoveContinuous(self,axis,direction):
        self._attodll.PositionerMoveContinuous(self._device,c_int(axis),c_int(direction))

    def StopMoving(self,axis):
        self._attodll.PositionerStopMoving(self._device,c_int(axis))

    def StepCount(self,axis,stepCount):
        self._attodll.PositionerMoveContinuous(self._device,c_int(axis),c_int(stepCount)) 

    def GetReference(self,axis):
        Position = c_int(0)
        Valid = c_int(0)
        self._attodll.PositionerGetReference(self._device,c_int(axis),byref(Position),byref(Valid))
        return Position.value, Valid.value

    def ResetPosition(self,axis):
        self._attodll.PositionerResetPosition(self._device,c_int(axis))

    def GetStatus(self,axis):
        Status = c_int(0)
        self._attodll.PositionerGetStatus(self._device,c_int(axis),byref(Status))
        return Status.value

    def SetOutput(self,status):
        self._attodll.PositionerSetOutput(self._device,c_int(status))

    def DcInEnable(self,axis,status):
        self._attodll.PositionerDcInEnable(self._device,c_int(axis),c_int(status))

    def AcInEnable(self,axis,status):
        self._attodll.PositionerAcInEnable(self._device,c_int(axis),c_int(status))

    def IntEnable(self,axis,status):
        self._attodll.PositionerIntEnable(self._device,c_int(axis),c_int(status))

    def BandwidthLimitEnable(self,axis,status):
        self._attodll.PositionerBandwidthLimitEnable(self._device,c_int(axis),c_int(status))

    def GetDcInEnable(self,axis):
        Enable = c_int(0)
        self._attodll.PositionerGetDcInEnable(self._device,c_int(axis),byref(Enable))
        return Enable.value

    def GetAcInEnable(self,axis):
        Enable = c_int(0)
        self._attodll.PositionerGetAcInEnable(self._device,c_int(axis),byref(Enable))
        return Enable.value

    def GetIntEnable(self,axis):
        Enable = c_int(0)
        self._attodll.PositionerGetIntEnable(self._device,c_int(axis),byref(Enable))
        return Enable.value

    def GetBandwidthLimitEnable(self,axis):
        Enable = c_int(0)
        self._attodll.PositionerGetBandwidthLimitEnable(self._device,c_int(axis),byref(Enable))
        return Enable.value

    def CapMeasurement(self,axis):
        Capacity = c_int(0)
        self._attodll.PositionerCapMeasure(self._device,c_int(axis),byref(Capacity))
        return Capacity.value

    def MoveAbsolute(self,axis,position,rotCount):
        self._attodll.PositionerMoveAbsolute(self._device,c_int(axis),c_int(position),c_int(rotCount))

    def MoveRelative(self,axis,distance,rotCount):
        self._attodll.PositionerMoveRelative(self._device,c_int(axis),c_int(distance),c_int(rotCount))

    def MoveReference(self,axis):
        self._attodll.PositionerMoveReference(self._device,c_int(axis))

    def StopDetection(self,axis,status):
        self._attodll.PositionerStopDetection(self._device,c_int(axis),c_int(status))

    def SetStopDetectionSticky(self,axis,status):
        self._attodll.PositionerMoveReference(self._device,c_int(axis),c_int(status))

    def ClearStopDetection(self,axis):
        self._attodll.PositionerClearStopDetection(self._device,c_int(axis))

    def SetTargetGround(self,axis,status):
        self._attodll.PositionerSetTargetGround(self._device,c_int(axis),c_int(status))

    def AmplitudeControl(self,axis,mode):
        self._attodll.PositionerAmplitudeControl(self._device,c_int(axis),c_int(mode))

    def Amplitude(self,axis,amplitude):
        self._attodll.PositionerAmplitude(self._device,c_int(axis),c_int(amplitude))

    def GetAmplitude(self,axis):
        Amplitude = c_int(0)
        self._attodll.PositionerGetAmplitude(self._device,c_int(axis),byref(Amplitude))
        return Amplitude.value

    def GetSpeed(self,axis):
        Speed = c_int(0)
        self._attodll.PositionerGetSpeed(self._device,c_int(axis),byref(Speed))
        return Speed.value

    def GetStepwidth(self,axis):
        Stepwidth = c_int(0)
        self._attodll.PositionerGetStepwidth(self._device,c_int(axis),byref(Stepwidth))
        return Stepwidth.value

    def Frequency(self,axis,frequency):
        self._attodll.PositionerFrequency(self._device,c_int(axis),c_int(frequency))

    def GetFrequency(self,axis):
        Frequency = c_int(0)
        self._attodll.PositionerGetFrequency(self._device,c_int(axis),byref(Frequency))
        return Frequency.value

    def DCLevel(self,axis,level):
        self._attodll.PositionerDCLevel(self._device,c_int(axis),c_int(level))


