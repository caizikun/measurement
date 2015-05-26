# Bas Hensen, 2015
# TODO:
#-  Currently only supports Swept Analysis mode 
#   (Real-Time Analysis, I/Q Streaming, Audio Demodulation, 
#   Scalar Network Analysis) modes not yet supported
#-  Currently only SA44 is supported

import ctypes as ct
import numpy as np
import gobject
from instrument import Instrument
import logging
import os
import types
import instrument_helper
import qt
from lib import config

class SignalHound_SA44B(Instrument):

    SA_MAX_DEVICES = 8

    saDeviceType = {
        0: 'saDeviceTypeNone',
        1: 'saDeviceTypeSA44',
        2: 'saDeviceTypeSA44B',
        3: 'saDeviceTypeSA124A',
        4: 'saDeviceTypeSA124B',
    }

    # Limits
    SA44_MIN_FREQ = 1.0 
    SA124_MIN_FREQ = 100.0e3 
    SA44_MAX_FREQ = 4.4e9 
    SA124_MAX_FREQ = 13.0e9 
    SA_MIN_SPAN = 1.0 
    SA_MAX_REF = 20  # dBm
    SA_MAX_ATTEN = 3 
    SA_MAX_GAIN = 2 
    SA_MIN_RBW = 0.1 
    SA_MAX_RBW = 250e3
    SA_MIN_RT_RBW = 100.0 
    SA_MAX_RT_RBW = 10000.0 
    SA_MIN_IQ_BANDWIDTH = 100.0 
    SA_MAX_IQ_DECIMATION = 128 

    SA_IQ_SAMPLE_RATE = 486111.111 

    # Modes
    SA_IDLE      = -1 
    SA_SWEEPING  = 0x0 
    SA_REAL_TIME = 0x1 
    SA_IQ        = 0x2 
    SA_AUDIO     = 0x3 
    SA_TG_SWEEP  = 0x4 

    # Detectors
    SA_MIN_MAX = 0x0 
    SA_AVERAGE = 0x1 

    # Scales
    SA_LOG_SCALE      = 0x0 
    SA_LIN_SCALE      = 0x1 
    SA_LOG_FULL_SCALE = 0x2  # N/A
    SA_LIN_FULL_SCALE = 0x3  # N/A

    # Levels
    SA_AUTO_ATTEN = -1 
    SA_0DB_ATTEN   = 0
    SA_5DB_ATTEN   = 1
    SA_10DB_ATTEN  = 2
    SA_15DB_ATTEN  = 3
    SA_AUTO_GAIN  = -1 
    SA_16DB_GAIN  = 0
    SA_MID_GAIN  = 1
    SA_12DB_DIG_GAIN  = 2

    # Video Processing Units
    SA_LOG_UNITS   = 0x0 
    SA_VOLT_UNITS  = 0x1 
    SA_POWER_UNITS = 0x2  
    SA_BYPASS      = 0x3 

    SA_AUDIO_AM  = 0x0 
    SA_AUDIO_FM  = 0x1 
    SA_AUDIO_USB = 0x2 
    SA_AUDIO_LSB = 0x3 
    SA_AUDIO_CW  = 0x4 

    # TG Notify Flags
    TG_THRU_0DB  = 0x1 
    TG_THRU_20DB  = 0x2 

    # Return values
    saStatus =  {
         -666 : 'saUnknownErr',

        # Setting specific error codes
        -99: 'saFrequencyRangeErr : The calculated start or stop frequencies fall outside of the operational frequency range of the specified device.',
        -95: 'saInvalidDetectorErr',
        -94: 'saInvalidScaleErr',
        -91: 'saBandwidthErr: rbw or vbw falls outside possible input range / vbw is greater than resolution bandwidth.',
        -89: 'aaExternalReferenceNotFound',
        
        # Device-specific errors
        -20: 'saOvenColdErr',

        # Data errors
        -12: 'saInternetErr',
        -11: 'saUSBCommErr: Device connection issues were present in the acquisition of this sweep.',

        # General configuration errors
        -10:'saTrackingGeneratorNotFound ',
        -9: 'saDeviceNotIdleErr',
        -8: 'saDeviceNotFoundErr: A valid Signal Hound device was not found.',
        -7: 'saInvalidModeErr',
        -6: 'saNotConfiguredErr',
        -5: 'saTooManyDevicesErr',
        -4: 'saInvalidParameterErr',
        -3: 'saDeviceNotOpenErr: The device specified is not currently open.',
        -2: 'saInvalidDeviceErr',
        -1: 'saNullPtrErr: Indicates one or more pointer parameters were equal to NULL.',

        # No Error
        0: 'saNoError',
        
        # Warnings
        1: 'saNoCorrections',
        2: 'saCompressionWarning : This warning is returned when the ADC detects clipping of the input signal. \
                                   This occurs when the maximum input voltage has been reached. \
                                   Signal analysis and reconstruction become issues on clipped signals. \
                                   To prevent this, a combination of increasing attenuation, decreasing gain, \
                                   or increasing reference level(when gain/atten is automatic) will allow for more headroom.',
        3: 'saParameterClamped: The provided gain or attenuation values were clamped to normal operating ranges.',
        4: 'saBandwidthClamped',
    }

    def __init__(self, name, serial_number = None): #2
         # Initialize wrapper
        logging.info(__name__ + ' : Initializing instrumentSignalHound SA44B')
        Instrument.__init__(self, name, tags=['physical'])
        
        self._Load_Dll()
        self.OpenDevice(serial_number)

        ins_pars  = {'scale'    :       {'type': types.IntType,'val':self.SA_LOG_SCALE,'flags':Instrument.FLAG_GETSET, 
                                         'option_list': [self.SA_LOG_SCALE,self.SA_LIN_SCALE, self.SA_LOG_FULL_SCALE,self.SA_LIN_FULL_SCALE],
                                         'doc':'The scale parameter will change the units of returned sweeps. \
                                                If self.SA_LOG_SCALE is chosen, sweeps will be returned in amplitude unit dBm. \
                                                If self.SA_LIN_SCALE is chosen, the returned units will be in millivolts. \
                                                If the full scale units are specified, no corrections are applied to the \
                                                data and amplitudes are taken directly from the full scale input.'},
                    'detection':        {'type': types.IntType,'val': self.SA_AVERAGE,'flags':Instrument.FLAG_GETSET, 
                                         'option_list': [self.SA_AVERAGE, self.SA_MIN_MAX],
                                         'doc':'detector setting specifies how to produce the results of the signal processing \
                                                for the final sweep. Depending on settings, potentially many overlapping \
                                                FFTs will be performed on the input time domain data to retrieve a more \
                                                consistent and accurate final result. When the results overlap detector \
                                                chooses whether to average the results together, or maintain the minimum \
                                                and maximum values. If self.SA_AVERAGE is chosen, the min and max sweep arrays \
                                                will contain the same averaged data.'},
                    'frequency_center': {'type': types.FloatType, 'val':1e6, 'flags':Instrument.FLAG_GETSET, 
                                         'minval':self.SA44_MIN_FREQ, 'maxval':self.SA44_MAX_FREQ, 'units': 'Hz',
                                         'doc':'This function configures the operating frequency band of the device. \
                                                Start and stop frequencies can be determined from the center and span. \
                                                start = center - span/2\
                                                stop = center + span/2'},
                    'frequency_span':   {'type': types.FloatType, 'val':1e3, 'flags':Instrument.FLAG_GETSET, 
                                         'minval':self.SA_MIN_SPAN, 'maxval':self.SA44_MAX_FREQ, 'units': 'Hz',
                                         'doc':'This function configures the operating frequency band of the device. \
                                                Start and stop frequencies can be determined from the center and span. \
                                                start = center - span/2\
                                                stop = center + span/2'},
                    'ref_level':        {'type': types.FloatType, 'val':0, 'flags':Instrument.FLAG_GETSET, 
                                         'maxval':self.SA_MAX_REF,
                                         'doc':'Set reference level in dBm. This function is best utilized when the \
                                                device attenuation and gain is set to automatic(default). When both attenuation \
                                                and gain are set to AUTO, the API uses the reference level to best choose \
                                                the gain and attenuation for maximum dynamic range.'},
                    'attenuation':      {'type': types.IntType, 'val':-1, 'flags':Instrument.FLAG_GETSET, 
                                         'option_list': [self.SA_AUTO_ATTEN, self.SA_0DB_ATTEN, self.SA_10DB_ATTEN, self.SA_15DB_ATTEN], 
                                         'doc':'Attenuator setting in dB. It is suggested to leave these values as automatic \
                                                as it will greatly increase the consistency of your results.'},
                    'gain':             {'type': types.IntType, 'val':-1, 'flags':Instrument.FLAG_GETSET, 
                                         'option_list': [self.SA_AUTO_GAIN, self.SA_16DB_GAIN, self.SA_MID_GAIN, self.SA_12DB_DIG_GAIN], 
                                         'doc':'Gain setting in dB. It is suggested to leave these values as automatic \
                                                as it will greatly increase the consistency of your results.'},
                    'preamp':           {'type': types.BooleanType, 'val':True, 'flags':Instrument.FLAG_GETSET, 
                                         'doc':'Specify whether to enable the internal device pre-amplifier. \
                                                The preamp parameter is ignored when gain and attenuation are \
                                                automatic and is chosen automatically'},
                    'rbw':              {'type': types.FloatType, 'val':1e3, 'flags':Instrument.FLAG_GETSET, 
                                         'minval': self.SA_MIN_RBW, 'maxval':self.SA_MAX_RBW, 'units': 'Hz', 
                                         'doc':'The resolution bandwidth, or RBW, represents the bandwidth of \
                                                spectral energy represented in each frequency bin. For example, \
                                                with an RBW of 10 kHz, the amplitude value for each bin would \
                                                represent the total energy from 5 kHz below to 5 kHz above the \
                                                bins center. For standard bandwidths, the API uses the  3 dB\
                                                points to define the RBW.'},
                    'vbw':              {'type': types.FloatType, 'val':1e3, 'flags':Instrument.FLAG_GETSET, 
                                         'minval': self.SA_MIN_RBW, 'maxval':self.SA_MAX_RBW, 'units': 'Hz', 
                                         'doc':'VBW must be less than or equal to RBW. VBW can be arbitrary. \
                                                For best performance use RBW as the VBW. The video bandwidth, or VBW, \
                                                is applied after the signal has been \
                                                converted to frequency domain as power, voltage, or log units. It is \
                                                implemented as a simple rectangular window, averaging the amplitude \
                                                readings for each frequency bin over several overlapping FFTs. A signal \
                                                whose amplitude is modulated at a much higher frequency than the VBW \
                                                will be shown as an average, whereas amplitude modulation at a lower \
                                                frequency will be shown as a minimum and maximum value.'},
                    'reject':           {'type': types.BooleanType, 'val':True, 'flags':Instrument.FLAG_GETSET, 
                                         'doc':'The parameter reject determines whether software image reject will be \
                                                performed. The SA-series spectrum analyzers do not have hardware-based \
                                                image rejection, instead relying on a software algorithm to reject \
                                                image responses. See the USB-SA44B or USB-SA124B manuals for additional\
                                                details. Generally, set reject to True for continuous signals, \
                                                and False to catch short duration signals at a known frequency. \
                                                To capture short duration signals with an unknown frequency, consider \
                                                the Signal Hound BB60C.'},
                    }
                    
        instrument_helper.create_get(self,ins_pars)
        self._is_running = False

        self.add_function('OpenDevice')
        self.add_function('CloseDevice')
        self.add_function('GetAllSerialNumbers')
        self.add_function('GetCurrentSerialNumber')
        self.add_function('ConfigSweepMode')
        self.add_function('GetSweep')
        self.add_function('PlotSweep')
        self.add_function('StartLivePlot')
        self.add_function('StopLivePlot')

        ## override from config       
        cfg_fn = os.path.join(qt.config['ins_cfg_path'], name+'.cfg')

        if not os.path.exists(cfg_fn):
            _f = open(cfg_fn, 'w')
            _f.write('')
            _f.close()

        self._ins_cfg = config.Config(cfg_fn)     
        self.load_cfg()
        self.save_cfg() 

        self.ConfigSweepMode()
        
    
    def load_cfg(self):
        params_from_cfg = self._ins_cfg.get_all()

        for p in params_from_cfg:
            val = self._ins_cfg.get(p)
            if type(val) == unicode:
                val = str(val)
            
            self.set(p, value=val)


    def save_cfg(self):
        parlist = self.get_parameters()
        for param in parlist:
            value = self.get(param)
            self._ins_cfg[param] = value

    def _Load_Dll(self):
        dll_fp = r'C:\Program Files\Signal Hound\Spike\api\sa_series\x86\sa_api.dll'
        self._dll=ct.cdll.LoadLibrary(dll_fp)

    def OpenDevice(self, serial_number=None):
        """
        This function attempts to open the first SA44/SA124 it detects. If 
        serial_number is not None, the device with given serial number will 
        be openend.
        """
        print self.get_name() + ': opening SignalHound... 5 secs...'
        dev_id = ct.c_int()
        if serial_number == None:
            result = self._dll.saOpenDevice(ct.byref(dev_id))
        else:
            sn = ct.c_int(serial_number)
            result = self._dll.saOpenDeviceBySerialNumber(ct.byref(dev_id),sn)
        self._dev_id = dev_id
        return self._handle_result(result)

    def ConfigSweepMode(self):
        """
        Initiate the  Swept analysis mode (BH 2015: currently only mode supported)
        This function must be called once after changing any of the settings, 
        for the new settings to take effect.
        Swept analysis represents the most traditional form of spectrum analysis. 
        This mode offers the largest amount of configuration options, 
        and returns traditional frequency domain sweeps. 
        A frequency domain sweep displays amplitude on the vertical 
        axis and frequency on the horizontal axis.
        """
        mode = ct.c_int(0)
        result = self._dll.saInitiate(self._dev_id, mode, ct.c_uint(0))
        return self._handle_result(result)

    def GetSweep(self, do_plot=False, max_points = 500):
        """
        Upon returning successfully, this function returns the frequency axis, and 
        minimum and maximum arrays of one full sweep. 
        If the detection parameter is set to SA_AVERAGE, 
        the arrays will be populated with the same values.
        """      
        sweep_length, start_freq, binsize = self.GetSweepInfo()
        if sweep_length == None:
            return False
        if sweep_length > max_points:
            print 'Sweep length ({}) longer than speciied max_points kw ({})'.format(sweep_length, max_points)
            print 'For long sweeps consider using the live updated GetSweepIncremental'
            return False
        freq_axis = start_freq + np.arange(0,sweep_length)*binsize
        min_arr = np.zeros(sweep_length, dtype=np.double)
        max_arr = np.zeros(sweep_length, dtype=np.double)
        result = self._dll.saGetSweep_64f(self._dev_id, min_arr.ctypes.data, max_arr.ctypes.data)
        if self._handle_result(result):
            if do_plot:
                self.PlotSweep(freq_axis, min_arr)
            return freq_axis, min_arr, max_arr
        return False

    def GetSweepInfo(self):
        sweep_length = ct.c_int()
        start_freq = ct.c_double()
        binsize = ct.c_double()
        result = self._dll.saQuerySweepInfo(self._dev_id, ct.byref(sweep_length), 
                        ct.byref(start_freq), ct.byref(binsize))
        if not self._handle_result(result):
            return None, None, None
        return sweep_length.value, start_freq.value, binsize.value


    def PlotSweep(self, f, y):
        """
        Creates a dataset & plot of a scan.
        """

        self._create_data_plot()
        x = f/self._xfactor
        self._dat.add_data_point(x,y)
        self._close_data_plot()
        

    def _create_data_plot(self):
        self._dat = qt.Data(name= self.get_name()+'_Scan')
        if self.get_frequency_center()>1e6:
            self._dat.add_coordinate('Frequency [MHz]')
            self._xfactor = 1e6
        else:
            self._dat.add_coordinate('Frequency [KHz]')
            self._xfactor = 1e3
        if self.get_scale() == self.SA_LIN_SCALE or self.get_scale() == self.SA_LIN_FULL_SCALE:
            self._dat.add_value('Power [mV]')
        else:
            self._dat.add_value('Power [dBm]')
        self._dat.create_file()
        self._plt = qt.Plot2D(self._dat, 'r-', name= self.get_name()+'_Scan', coorddim=0, valdim=1, clear=True)

    def _close_data_plot(self):
        self._dat.close_file()
        self._plt.update()
        self._plt.save_png(self._dat.get_filepath()+'png')

    def StartLivePlot(self, update_interval = 0.5):
        if self._is_running:
            print 'Already running'
            return False
        sweep_length, start_freq, binsize = self.GetSweepInfo()
        if sweep_length == None:
            return False
        self._freq_axis = start_freq + np.arange(0,sweep_length)*binsize
        self._min_arr = np.zeros(sweep_length, dtype=np.double)
        self._max_arr = np.zeros(sweep_length, dtype=np.double)

        self._create_data_plot()
        self._is_running = True
        self._timer=gobject.timeout_add(int(update_interval*1e3),\
                self._update_live_plot)

    def _update_live_plot(self):
        if not(self._is_running):
            return False
        start = ct.c_int()
        stop = ct.c_int()

        result = self._dll.saGetPartialSweep_64f(self._dev_id, self._min_arr.ctypes.data, self._max_arr.ctypes.data, ct.byref(start), ct.byref(stop))
        if self._handle_result(result):
            x = self._freq_axis[start.value:stop.value-1]/self._xfactor
            y = self._min_arr[start.value:stop.value-1]
            self._dat.add_data_point(x,y)
            self._plt.update()
            if stop.value == len(self._freq_axis):
                self._dat.new_block()
            return True
        return False

    def StopLivePlot(self):
        self._is_running = False
        self._close_data_plot()
        return gobject.source_remove(self._timer)
        
    def CloseDevice(self):
        result = self._dll.saCloseDevice(self._dev_id)
        return self._handle_result(result)

    def Reset(self):
        """
        This function exists to invoke a hard reset of the device.
        """
        result = self._dll.saPreset(self._dev_id)
        return self._handle_result(result)

    def GetAllSerialNumbers(self):
        """
        Get a list of serial numbers of available devices connected to the PC.
        """
        serial_numbers = np.zeros(self.SA_MAX_DEVICES, dtype=np.int)
        device_count = ct.c_int()
        result = self._dll.saGetSerialNumberList(serial_numbers.ctypes.data, ct.byref(device_count))
        if self._handle_result(result):
            return serial_numbers[:device_count]
        return False

    def GetCurrentSerialNumber(self):
        """
        Retrieve the serial number of the currently connected device.
        """
        sn = ct.c_int()
        result = self._dll.saGetSerialNumber(self._dev_id, ct.byref(sn))
        if self._handle_result(result):
            return sn.value
        return False

    def _do_set_scale(self, val):
        self._scale = val
        return self._config_aquisition()

    def _do_set_detection(self, val):
        self._scale = val
        return self._config_aquisition()

    def _config_aquisition(self):
        scale = ct.c_int(self._scale)
        detector = ct.c_int(self._detection)
        result = self._dll.saConfigAcquisition(self._dev_id, detector, scale)
        return self._handle_result(result)

    def _do_set_frequency_center(self, val):
        self._frequency_center = val
        return self._config_center_span()

    def _do_set_frequency_span(self, val):
        self._frequency_span = val
        return self._config_center_span()

    def _config_center_span(self):
        center = ct.c_double(self._frequency_center)
        span = ct.c_double(self._frequency_span)
        result = self._dll.saConfigCenterSpan(self._dev_id, center, span)
        return self._handle_result(result)

    def _do_set_ref_level(self, val):
        self._ref_level = val
        ref = ct.c_double(self._ref_level)
        result = self._dll.saConfigLevel(self._dev_id, ref)
        return self._handle_result(result)

    def do_set_attenuation(self,val):
        self._attenuation = val
        return self._config_gain_att_preamp()

    def do_set_gain(self,val):
        self._gain = val
        return self._config_gain_att_preamp()

    def do_set_preamp(self,val):
        self._preamp = val
        return self._config_gain_att_preamp()

    def _config_gain_att_preamp(self):
        atten  = ct.c_int(self._attenuation)
        gain   = ct.c_int(self._gain)
        preamp = ct.c_bool(self._preamp)
        result = self._dll.saConfigGainAtten(self._dev_id, atten, gain, preamp)
        return self._handle_result(result)

    def do_set_rbw(self,val):
        self._rbw = val
        return self._config_sweep_coupling()

    def do_set_vbw(self,val):
        self._vbw = val
        return self._config_sweep_coupling()

    def do_set_reject(self,val):
        self._reject = val
        return self._config_sweep_coupling()

    def _config_sweep_coupling(self):
        rbw    = ct.c_double(self._rbw)
        vbw    = ct.c_double(min(self._rbw,self._vbw))
        reject = ct.c_bool(self._reject)
        result = self._dll.saConfigSweepCoupling(self._dev_id, rbw, vbw, reject)
        return self._handle_result(result)

    def _handle_result(self, result):
        if result > 0:
            if result in self.saStatus:
                logging.warning(self.get_name() + ': ' + self.saStatus[result])
            else:
                logging.warning(self.get_name() + ': ' + 'Unknown status warning')
        elif result < 0:
            if result in self.saStatus:
                logging.error(self.get_name() + ': ' + self.saStatus[result])
            else:
                logging.warning(self.get_name() + ': ' + 'Unknown status error')
        return result >= 0

    def remove(self):
        self.save_cfg()
        self.CloseDevice()
        print 'removing'
        Instrument.remove(self)

    def reload(self):
        self.save_cfg()
        self.CloseDevice()
        print 'reloading'
        Instrument.reload(self)
