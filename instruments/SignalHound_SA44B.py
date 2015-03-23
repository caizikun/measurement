import ctypes as ct
import numpy as np
from instrument import Instrument
import logging
import os
import types
import instrument_helper
import qt
from lib import config

class SignalHound_SA44B(Instrument):

    _SH_errors = {100 :'ERROR_HOUND_NOT_FOUND',
                 101 :'ERROR_PACKET_HEADER_NOT_FOUND',
                 102 :'ERROR_WRITE_FAILED',
                 103 :'ERROR_WRONG_NUM_READ',
                 104 :'ERROR_READ_TIMEOUT',
                 105 :'ERROR_DEVICE_NOT_LOADED',
                 106 :'ERROR_MISSING_DATA',
                 107 :'ERROR_EXTRA_DATA',
                 200 :'ERROR_OUT_OF_RANGE',
                 201 :'ERROR_NO_EXT_REF'}

    def __init__(self, name, dev_nr = 0): #2
         # Initialize wrapper
        logging.info(__name__ + ' : Initializing instrument ADwin Pro II')
        Instrument.__init__(self, name, tags=['physical'])
        
        self._dev_nr = dev_nr
        self._Load_Dll()
        self.Initialize()  
        
        ins_pars  = {'image_handling'    :   {'type': types.IntType,'val':0,'flags':Instrument.FLAG_GETSET, 'minval':0, 'maxval':2,
                                                    'doc':'Set to 0 for default, IMAGE REJECTION ON (mask together high side \
                                                           and low side injection). Set to 1 for HIGH SIDE INJECTION. Set to \
                                                           2 for LOW SIDE INJECTION.'},
                     'fft_size_slow_scan':   {'type': types.IntType,   'val':10, 'flags':Instrument.FLAG_GETSET,  'minval':4, 'maxval':16},
                     'fft_size_fast_scan':   {'type': types.IntType,   'val':4, 'flags':Instrument.FLAG_GETSET,   'minval':4, 'maxval':8},
                     'attenuation'       :   {'type': types.FloatType, 'val':10., 'flags':Instrument.FLAG_GETSET, 'option_list': [0.,5.,10.,15.], 
                                                    'doc': 'Attenuator setting in dB. Must be 0.0, 5.0, 10.0, or 15.0 dB. '},
                     'mixerband'         :   {'type': types.IntType,   'val':1,   'flags':Instrument.FLAG_GETSET, 'minval':0, 'maxval':1, 
                                                    'doc': 'For RF input frequencies below 150 MHz this should always be set to 0. \
                                                            For RF frequencies above 150 MHz this should always be set to 1.'},
                     'sensitivity'       :   {'type': types.IntType,   'val':0,   'flags':Instrument.FLAG_GETSET, 'minval':0, 'maxval':2, 
                                                    'doc': 'For lowest sensitivity, set to 0. For highest sensitivity set to 2.'},
                     'decimation'        :   {'type': types.IntType,   'val':1,   'flags':Instrument.FLAG_GETSET, 'minval':0, 'maxval':16, 
                                                    'doc': ' Decimation Sample rate is equal to 486.1111 Ksps divided by this number.\
                                                             Must be between 1 and 16, inclusive. Part of resolution bandwidth (RBW) calculation.'}, 
                     'IF_path'           :   {'type': types.IntType,   'val':0,   'flags':Instrument.FLAG_GETSET, 'minval':0, 'maxval':1, 
                                                    'doc': 'IF Path Set to 0 for default 10.7 MHz Intermediate Frequency (IF) path.\
                                                            This path has higher selectivity but lower sensitivity. Set to 1 for 2.9 MHz IF path.'},
                     'ADC_clock'           :   {'type': types.IntType,   'val':0,   'flags':Instrument.FLAG_GETSET, 'minval':0, 'maxval':1, 
                                                    'doc': 'Set to 0 to select the default 23 1/3 MHz ADC clock.\
                                                            Set to 1 to select the for 22 1/2 MHz ADC clock,\
                                                            which is useful if your frequency is a multiple of 23 1/3 MHz.'},
                    }
                    
        instrument_helper.create_get_set(self,ins_pars)

        self.add_parameter('preamp',
                type=types.IntType,
                flags=Instrument.FLAG_GETSET,
                minval=0,maxval=1)

        self.add_parameter('synctriggermode',
                type=types.IntType,
                flags=Instrument.FLAG_GETSET,
                minval=0,maxval=3)

        self._preamp      = 1
        self._synctriggermode = 0

        self.add_function('Initialize')
        self.add_function('Slow_Scan')
        self.add_function('Configure')
        self.add_function('Fast_Scan')
        self.add_function('Calculate_RBW_Slow')
        self.add_function('Calculate_RBW_Fast')
        self.add_function('Cycle_Devices')
        self.add_function('Select_External_Reference')
        self.add_function('Get_Error_Text')
        # override from config       
        cfg_fn = os.path.join(qt.config['ins_cfg_path'], name+'.cfg')

        if not os.path.exists(cfg_fn):
            _f = open(cfg_fn, 'w')
            _f.write('')
            _f.close()

        self._ins_cfg = config.Config(cfg_fn)     
        self.load_cfg()
        self.save_cfg() 
    
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
        print self.get_name() + ': loading SH_APImw.dll'
        dll_fp=os.path.join(qt.config['hardware_path'],'SignalHound','SH_APImw.dll')
        self._dll=ct.cdll.LoadLibrary(dll_fp)

    def Initialize(self, force_cal=False):
        cal_fp = os.path.join(qt.config['hardware_path'],'SignalHound','cal.npz')
        if os.path.exists(cal_fp) and not(force_cal):
            print self.get_name() + ': loading calibration from file'
            p4KTable = np.load(cal_fp)['cal_table']
            result = self._dll.SHAPI_InitializeEx(p4KTable.ctypes.data, ct.c_int(self._dev_nr))
        else:
            result = self._dll.SHAPI_Initialize()
            p4KTable = np.zeros(4096, dtype=np.ubyte)
            self._dll.SHAPI_CopyCalTable(p4KTable.ctypes.data,ct.c_int(self._dev_nr))
            np.savez(cal_fp, cal_table=p4KTable)
        
        for i in np.arange(self._dev_nr):
            result = self._dll.SHAPI_InitializeNext()
        return result

    def Configure(self, **kw):
        attenuation  = kw.pop('attenuation',self._attenuation) 
        mixerband    = kw.pop('mixerband',self._mixerband)
        sensitivity  = kw.pop('sensitivity',self._sensitivity)
        decimation   = kw.pop('decimation',self._decimation)
        IF_path      = kw.pop('IF_path',self._IF_path)
        ADC_clock    = kw.pop('ADC_clock',self._ADC_clock)

        result = self._dll.SHAPI_Configure(ct.c_double(attenuation),
                                           ct.c_int(mixerband),
                                           ct.c_int(sensitivity),
                                           ct.c_int(decimation),
                                           ct.c_int(IF_path),
                                           ct.c_int(ADC_clock),
                                           ct.c_int(self._dev_nr))
        return result

    def Slow_Scan(self, start_freq, stop_freq, avg_count=16, do_plot=True, ret=False, force_slow_measurement =False):
        """
        This function captures an array of data. Data points are amplitude, in dBm. 
        The first data point is equal to the starting frequency. 
        Subsequent data points are spaced by 486.1111 KHz / FFT size / decimation.

        keywords:
        - avg_count: Number of FFTs that get averaged together to produce the output. 
        The amount of data captured at each frequency is a product of FFTSize and avgCount. 
        This product must be a multiple of 512 --> avg_count is rounded to match this requirement
        - do_plot: Make a plot of the captured data
        - ret: return the frequency axis and data
        - force_slow_measurement: execute measurements that take longer than 10 seconds
        """
        self.Configure()
        fft_size = 2**self.get_fft_size_slow_scan()
        if (avg_count*fft_size)%512 != 0:
            logging.warning(self.get_name()+': Product of avg_count*2**fft_size_slow_scan must be a multiple of 512')
            avg_count = max((avg_count*fft_size/512),1)*512/fft_size
        
        expected_m_time = (40. + float(fft_size * avg_count * self.get_decimation())/ 486.*(stop_freq-start_freq)/201.e3)/1000. #s
        if expected_m_time > 10 and not(force_slow_measurement):
            logging.warning(self.get_name()+': Time to execute scan to long: {:.1f} s. Use force_slow_measurement = True to go anyway.'.format(expected_m_time))

        retcount = self._dll.SHAPI_GetSlowSweepCount(ct.c_double(start_freq),
                                                ct.c_double(stop_freq),
                                                ct.c_int(fft_size))
        f_i = np.arange(retcount)
        f = start_freq + f_i * 486.1111e3/fft_size/self.get_decimation()

        dbarr = np.zeros(retcount, dtype = np.double)
        if True:
            retcount = ct.c_int(0)
            result = self._dll.SHAPI_GetSlowSweep(dbarr.ctypes.data,
                                             ct.c_double(start_freq),
                                             ct.c_double(stop_freq),
                                             ct.byref(retcount),
                                             ct.c_int(fft_size),
                                             ct.c_int(avg_count),
                                             ct.c_int(self.get_image_handling()),
                                             ct.c_int(self._dev_nr))
        if do_plot:
            self.Plot_Scan(f,dbarr)
        if ret:
            return f,dbarr

    def Fast_Scan(self, start_freq, stop_freq, do_plot=True, ret=False):
        """
        This function captures an array of data. Data points are amplitude, in dBm. 
        The first data point is equal to the starting frequency. 
        For FFT size of 1 (raw power only), data points are spaced 200 KHz. 
        Otherwise data points are spaced 400 KHz / FFT Size.
        RBW is based on FFT size only, as decimation is equal to 1.
        """
        self.Configure(decimation=1, IF_path=0, ADC_clock=0)
        fft_size = 2**self.get_fft_size_fast_scan()

        retcount = self._dll.SHAPI_GetFastSweepCount(ct.c_double(start_freq),
                                                ct.c_double(stop_freq),
                                                ct.c_int(fft_size))
        f_i = np.arange(retcount)
        f = start_freq + f_i * 400.e3/fft_size
        dbarr = np.zeros(retcount, dtype = np.double)
        retcount = ct.c_int(0)
        result = self._dll.SHAPI_GetFastSweep(dbarr.ctypes.data,
                                         ct.c_double(start_freq),
                                         ct.c_double(stop_freq),
                                         ct.byref(retcount),
                                         ct.c_int(fft_size),
                                         ct.c_int(self.get_image_handling()),
                                         ct.c_int(self._dev_nr))
        if do_plot:
            self.Plot_Scan(f,dbarr)
        if ret:    
            return f,dbarr

    def Plot_Scan(self, f, dbarr):
        """
        Creates a dataset & plot of a scan.
        """

        y = dbarr
        dat = qt.Data(name= self.get_name()+'_Scan')
        if (f[-1]-f[0])>1e6:
            dat.add_coordinate('Frequency [MHz]')
            x = f/1e6
        else:
            dat.add_coordinate('Frequency [KHz]')
            x = f/1e3
        dat.add_value('Power [dBm]')
        dat.create_file()
        plt = qt.Plot2D(dat, 'r-', name= self.get_name()+'_Scan', coorddim=0, valdim=1, clear=True)
        plt.add_data(dat, coorddim=0, valdim=2)
        dat.add_data_point(x,y)
        dat.close_file()
        plt.update()
        plt.save_png(dat.get_filepath()+'png')

    #TODO 2 RBW methods below do not conform to the API description!
    def Calculate_RBW_Slow(self):
        return self._dll.SHAPI_GetRBW(ct.c_int(2**self.get_fft_size_slow_scan()))#,ct.c_int(self.get_decimation())))
#
    def Calculate_RBW_Fast(self):
        return self._dll.SHAPI_GetRBW(ct.c_int(self.get_fft_size_fast_scan()))#,ct.c_int(self.get_decimation())))

    def Cycle_Devices(self):
        return self._dll.SHAPI_CyclePort()

    def Select_External_Reference(self):
        return self._dll.SHAPI_SelectExt10MHz(ct.c_int(self._dev_nr))

    #TODO GetIQDataPacket
    #TODO SHAPI_GetTemperature
    #TODO SHAPI_LoadTemperatureCorrections

    #TODO sync_triggermode selection does not seem to work, and/ore does not conform to the API description.
    def do_get_synctriggermode(self):
        return self._synctriggermode

    def do_set_synctriggermode(self, val):
        """
        When using an external trigger (3.3V or 5V OK), some functions (slow sweep, measurement receiver) 
        will wait for a logic high before beginning data collection. 
        There is no timeout, so use the external trigger with caution as it will halt operations until a TTL high is received.
        """
        self._synctriggermode = val
        return self._dll.SHAPI_SyncTriggerMode(ct.c_int(self._synctriggermode), ct.c_int(self._dev_nr))

    def Get_Error_Text(self, err_nr):
        return self._SH_errors[err_nr]

    def do_get_preamp(self):
        return self._preamp

    def do_set_preamp(self, val):
        """
        Turns on or turns off the RF preamplifier. 
        The preamplifier can be used to improve the sensitivity and decrease LO feed-through 
        for sensitive readings. Set the attenuator to ensure the preamplifier input sees less 
        than -25 dBm of input power to avoid overdriving your mixer and distorting your signal. 
        Turn off the preamplifier below 500 KHz.
        """
        self._preamp = val
        self._dll.SHAPI_SetPreamp(ct.c_int(val))
        self.save_cfg()

    def remove(self):
        self._dll.SHAPI_CyclePowerOnExit()
        print 'removing'
        Instrument.remove(self)
