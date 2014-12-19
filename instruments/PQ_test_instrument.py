import ctypes
import os
from instrument import Instrument
import time
import types
import logging
import numpy as np
import qt
import gobject
import h5py

LIB_VERSION = "1.1"
DRIVER = 'th260lib'

LIB_VERSION = "1.1"
DRIVER = 'th260lib'
MAXDEVNUM     = 4             # max num of USB devices
THMAXCHAN   = 2           # max num of logical channels
MAXBINSTEPS = 22          # get actual number via TH_GetBaseResolution) !
MAXHISTLEN  = 5         # max number of histogram bins= 1024*2**MAXHISTLEN
MAXLENCODE  = 5           # max length code histo mode
MAXHISTLEN_CONT = 8192  # max number of histogram bins in continuous mode
MAXLENCODE_CONT = 3     # max length code in continuous mode
TTREADMAX   = 131072    # 128K event records can be read in one chunk
MODE_HIST                   = 0
MODE_T2                     = 2
MODE_T3                     = 3
MODE_CONT                   = 8
MEASCTRL_SINGLESHOT_CTC     = 0 # default
MEASCTRL_C1_GATE                = 1
MEASCTRL_C1_START_CTC_STOP  = 2
MEASCTRL_C1_START_C2_STOP   = 3
T2_WRAPAROUND               = 33554432 #=2**25
T2_TIMEFACTOR               = 1

#continuous mode only
MEASCTRL_CONT_EXTTRIG       = 5
MESACTRL_CONT_CTCTRIG       = 6

EDGE_RISING                 = 1
EDGE_FALLING                = 0

FLAG_OVERFLOW               = 0x0001  #histo mode only
FLAG_FIFOFULL               = 0x0002  
FLAG_SYNC_LOST              = 0x0004  
FLAG_REF_LOST               = 0x0008  
FLAG_SYSERROR               = 0x0010  #hardware error, must contact support

SYNCDIVMIN                  = 1
SYNCDIVMAX                  = 8

DISCRMIN                    = -1200           # mV
DISCRMAX                    = 1200          # mV 

CHANOFFSMIN                 = -99999        # ps
CHANOFFSMAX                 = 99999         # ps

OFFSETMIN                   =   0                 # ps
OFFSETMAX                   =   100000000      # ps 
ACQTMIN                     = 1               # ms
ACQTMAX                     =   360000000     # ms  (100*60*60*1000ms = 100h)

STOPCNTMIN                  = 1
STOPCNTMAX                  = 4294967295  # 32 bit is mem max

#The following are bitmasks for return values from GetWarnings()

WARNING_SYNC_RATE_ZERO      = 0x0001
WARNING_SYNC_RATE_TOO_LOW   = 0x0002
WARNING_SYNC_RATE_TOO_HIGH  = 0x0004

WARNING_INPT_RATE_ZERO      = 0x0010
WARNING_INPT_RATE_TOO_HIGH  = 0x0040

WARNING_INPT_RATE_RATIO     = 0x0100
WARNING_DIVIDER_GREATER_ONE = 0x0200
WARNING_TIME_SPAN_TOO_SMALL = 0x0400
WARNING_OFFSET_UNNECESSARY  = 0x0800
WARNING_DIVIDER_TOO_SMALL   = 0x1000
WARNING_COUNTS_DROPPED      = 0x2000

FIFO_BUFFER = 32e6

class PQ_test_instrument(Instrument): #1
    '''
    This is a virtual PQ instrument like the Hydraharpo for testing purposes.

    Usage:
    Initialize with
    PQ_test_ins = qt.instruments.create('PQ_test_ins', 'PQ_test_instrument')
    
    status:
     1) Histogramming mode tested
    TODO:
     2) Test T2/T3 modes
    '''
    def __init__(self, name, DeviceIndex = 0): #2
        # Initialize wrapper
        logging.info(__name__ + ' : Initializing PQ test instrument')
        Instrument.__init__(self, name, tags=['virtual'])

        # Load dll and open connection

        self.add_parameter('data_fp', flags = Instrument.FLAG_GETSET, type=types.StringType)

        self.add_parameter('Range', flags = Instrument.FLAG_SET, type=types.IntType)
        self.add_parameter('Offset', flags = Instrument.FLAG_SET, type=types.IntType,
                           minval=OFFSETMIN, maxval=OFFSETMAX)
        self.add_parameter('SyncDiv', flags = Instrument.FLAG_SET, type=types.IntType,
                           minval=SYNCDIVMIN, maxval=SYNCDIVMAX)
        self.add_parameter('ResolutionPS', flags = Instrument.FLAG_GET, type=types.FloatType)
        self.add_parameter('BaseResolutionPS', flags = Instrument.FLAG_GET, type=types.FloatType)
        self.add_parameter('MaxBinSteps', flags = Instrument.FLAG_GET, type=types.IntType)
        self.add_parameter('SyncEdgeTrg', flags = Instrument.FLAG_SET, type=types.IntType,
                           minval=DISCRMIN, maxval=DISCRMAX)

        self.add_parameter('SyncChannelOffset', flags = Instrument.FLAG_SET, type=types.IntType,
                           minval=CHANOFFSMIN, maxval=CHANOFFSMAX)
        self.add_parameter('InputEdgeTrg', flags = Instrument.FLAG_SET, type=types.IntType,
                           minval=DISCRMIN, maxval=DISCRMAX)

        self.add_parameter('InputChannelOffset', flags = Instrument.FLAG_SET, type=types.IntType,
                           minval=CHANOFFSMIN, maxval=CHANOFFSMAX)
        self.add_parameter('HistoLen', flags = Instrument.FLAG_SET, type=types.IntType,
                           minval=0, maxval=MAXLENCODE)
        self.add_parameter('InputEdgeTrg0', flags = Instrument.FLAG_SET, type=types.IntType)
        self.add_parameter('InputEdgeTrg1', flags = Instrument.FLAG_SET, type=types.IntType)
        self.add_parameter('CountRate0', flags = Instrument.FLAG_GET, type=types.IntType)
        self.add_parameter('CountRate1', flags = Instrument.FLAG_GET, type=types.IntType)
        self.add_parameter('ElapsedMeasTimePS', flags = Instrument.FLAG_GET, type=types.FloatType)
        self.add_parameter('DeviceIndex', flags = Instrument.FLAG_SET, type=types.IntType)

        self.add_parameter('MeasRunning', flags = Instrument.FLAG_GET, type=types.BooleanType)
        self.add_parameter('Flags', flags = Instrument.FLAG_GET, type=types.IntType)
        self.add_parameter('Flag_Overflow', flags = Instrument.FLAG_GET, type=types.BooleanType)
        self.add_parameter('Flag_FifoFull', flags = Instrument.FLAG_GET, type=types.BooleanType)
        self.add_parameter('Flag_RefLost', flags = Instrument.FLAG_GET, type=types.BooleanType)
        self.add_parameter('Flag_SyncLost', flags = Instrument.FLAG_GET, type=types.BooleanType)
        self.add_parameter('Flag_SystemError', flags = Instrument.FLAG_GET, type=types.BooleanType)
        self.add_parameter('NumOfInputChannels', flags = Instrument.FLAG_GET, type=types.IntType)
        self.add_parameter('Channel', flags = Instrument.FLAG_SET, type=types.IntType)
        self.add_parameter('Binning', flags = Instrument.FLAG_SET, type=types.IntType,
                           minval=0, maxval=MAXBINSTEPS-1)
        self.add_parameter('T2_WRAPAROUND', flags = Instrument.FLAG_GET, type=types.IntType)
        self.add_parameter('T2_TIMEFACTOR', flags = Instrument.FLAG_GET, type=types.IntType)
        self.add_parameter('T2_READMAX', flags = Instrument.FLAG_GET, type=types.IntType)
        
        self.add_function('start_histogram_mode')
        self.add_function('start_T2_mode')
        self.add_function('start_T3_mode')
        self.add_function('ClearHistMem')
        self.add_function('StartMeas')
        self.add_function('StopMeas')
        self.add_function('OpenDevice')
        self.add_function('CloseDevice')
        # self.add_function('get_T3_pulsed_events')
        
        self.meas_running = False
        if self.start_histogram_mode():
            self.BaseResolutionPS = 1
            self.Binning = 1
            self.rates=1e3 # = 250 * 180 syncs per second == bell data rate.
            self._do_set_HistoLen(45000) 
            self.hist=np.zeros(self.HistogramLength, dtype=np.uint32)

            self._t0 = time.time()
            self._t1= self._t0

            self._fifo_full = False

        else:
            logging.error('TH260 device could not be initialized.')
            self.CloseDevice()


    def _do_set_DeviceIndex(self,val):
        self.DevIdx = val

    def _do_get_T2_WRAPAROUND(self):
        return T2_WRAPAROUND

    def _do_get_T2_TIMEFACTOR(self):
        return T2_TIMEFACTOR

    def _do_get_T2_READMAX(self):
        return TTREADMAX

    def _do_set_Channel(self,val):
	if val < self.NumOfInputChannels:
            self.Channel = val
        else:
            logging.warning('Error: Channel Index out of range')

    def start_histogram_mode(self):
        self.t2_mode=False
        return True

    def start_T2_mode(self):
        self.t2_mode=True

    def start_T3_mode(self):
        pass

    def _do_get_NumOfInputChannels(self):
        return 2
       
    def _do_get_MaxBinSteps(self):
        return -1

    def _do_get_BaseResolutionPS(self):
        return self.BaseResolutionPS

    def _do_get_ResolutionPS(self):
        return 2**self.Binning*self.BaseResolutionPS

    def get_CountRate(self):
        return self.rates

    def get_SyncRate(self):
        return self.rates

    def _do_get_CountRate0(self):
        return self.rates

    def _do_get_CountRate1(self):
        return self.rates

    def _do_set_InputEdgeTrg0(self, value,**kw):
        pass

    def _do_set_InputEdgeTrg1(self, value,**kw):
        pass

    def set_EdgeTrg(self, value, **kw):
        pass

    def _do_set_InputEdgeTrg(self, value, edge=EDGE_RISING):
        pass

    def _do_set_SyncEdgeTrg(self, value, edge=EDGE_RISING):
        pass

    def _do_set_InputChannelOffset(self, value):
        pass

    def _do_set_SyncChannelOffset(self, value):
        pass

    def _do_set_SyncDiv(self, div):
        pass

    def set_StopOverflow(self, stop_ovfl, stopcount):
        pass

    def _do_set_Binning(self, value):
        self.Binning = value

    def _do_set_Offset(self, offset):
        pass

    def _do_set_Range(self, binsize):  # binsize in 2^n times base resolution (4ps)
        pass

    def _do_set_HistoLen(self, lencode):
        self.HistogramLength = lencode

    def ClearHistMem(self):
        self.hist=np.zeros(self.HistogramLength, dtype=np.uint32)

    def StartMeas(self,aquisition_time_ms):
        self.meas_running = True
        self._t0 = time.time()
        gobject.timeout_add(aquisition_time_ms,self.StopMeas)
        if self.t2_mode:
            self.prepare_data()

    def StopMeas(self):
        self.meas_running = False
        return False

    def OpenDevice(self):
        return True

    def CloseDevice(self):
        return True

    def _do_get_MeasRunning(self):
        return self.meas_running

    def _do_get_Flags(self):
        return 0
        
    def _do_get_Flag_Overflow(self):
        return 0
        
    def _do_get_Flag_FifoFull(self):
        return self._fifo_full
        
    def _do_get_Flag_SyncLost(self):
        return 0
        
    def _do_get_Flag_RefLost(self):
        return 0
        
    def _do_get_Flag_SystemError(self):
        return 0
        
    def _do_get_ElapsedMeasTimePS(self):
        return (time.time() - self._t0)*1e12

    def get_Histogram(self, channel, clear=0):
        dt = time.time() - max(self._t0,self._t1)
        self._t1 = time.time()
        T = self.get_ResolutionPS()*self.HistogramLength
        avg_cts = self.rates/dt/self.HistogramLength


        data = self.hist + np.array(np.random.randint(0,max(2,2*avg_cts),self.HistogramLength), dtype = np.uint32)
        if clear:
            self.ClearHistMem()
        else:
            self.hist = data
        return data
 
    def get_Block(self):
        return self.get_Histogram(0,0)

    def get_Warnings(self):
        return 0
        
    def get_WarningsText(self, warnings):
            return 0
            
    def get_TTTR_Data(self,count = TTREADMAX):
        if self.get_MeasRunning():
            data = self.generate_data()
            return len(data), data # used to be data AR2014-11-14
        else:
            return 0, np.zeros(0,dtype=np.uint32)
        
        
    def set_MarkerEdgesRising(self,me0,me1,me2,me3):
        pass
            
    def set_MarkerEnable(self,me0,me1,me2,me3):
        pass
            
    def get_ErrorString(self, errorcode):
        return ''


    def prepare_data(self):
        f=h5py.File(self.get_data_fp(),'r')
        print 'preparing data'

        self.pq_sn = f['/PQ_sync_number-1'].value 
        self.pq_sp = f['/PQ_special-1'].value      
        self.pq_st = f['/PQ_sync_time-1'].value
        self.pq_tt = f['/PQ_time-1'].value   
        self.pq_ch = f['/PQ_channel-1'].value

        f.close()

        self.cur_pq_sn = 0
        self.cur_pq_tt = 0

    def generate_data(self):
        dt = time.time() - max(self._t0,self._t1)
        
        noof_syncs = self.rates*dt
        sn_fltr = (self.pq_sn > self.cur_pq_sn) & (self.pq_sn <= self.cur_pq_sn+noof_syncs)

        noof_events = np.sum(sn_fltr)
        if noof_events==0:
            return np.zeros(0, dtype = np.uint32)
        sn = self.pq_sn[sn_fltr]  
        sp = self.pq_sp[sn_fltr]     
        st = self.pq_st[sn_fltr] 
        tt = self.pq_tt[sn_fltr]
        tt_rem = np.remainder(tt,T2_WRAPAROUND)   
        ch = self.pq_ch[sn_fltr] 
        total_time = tt[-1] - self.cur_pq_tt
        noof_overflows = np.floor(total_time/T2_WRAPAROUND)
        true_noof_syncs = sn[-1] - self.cur_pq_sn

        new_data_len = true_noof_syncs + noof_events + noof_overflows
        ttime = np.zeros(new_data_len, dtype = np.uint32)
        channel = np.zeros(new_data_len, dtype = np.uint32)
        special= np.zeros(new_data_len, dtype = np.uint32)
        d_idx = 0
        for i in range(len(sn)):
            #first insert some overflows and syncs to correct for boring time without events
            ovfls = np.floor((tt[i]-self.cur_pq_tt)/T2_WRAPAROUND)
            special[d_idx:d_idx+ovfls] = 1
            channel[d_idx:d_idx+ovfls] = 63
            d_idx+=ovfls
            syncs = max(sn[i] - self.cur_pq_sn - 1,0)
            special[d_idx:d_idx+syncs] = 1
            channel[d_idx:d_idx+syncs] = 0
            d_idx+=syncs

            #now comes the sync corresponding to the event
            if sn[i] > self.cur_pq_sn:
                channel[d_idx] = 0
                special[d_idx] = 1
                sync_time = int(tt_rem[i]) - int(st[i])
                if sync_time > 0:
                    ttime[d_idx] = sync_time  #this will produce some errors 
                                                #when the event comes directly 
                                                #after a t2_wraparound, 
                                                #ie the wraparound is 
                                                #in between the sync and the event
                else:
                    #raise Exception('Wrong sync generated')
                    logging.error('Wrong sync generated')
                    ttime[d_idx] = 1
                d_idx += 1
                    

            
            #now comes the event                                                   
            channel[d_idx] = ch[i]
            special[d_idx] = sp[i]
            ttime[d_idx] = tt_rem[i]
            d_idx += 1

            self.cur_pq_tt = tt[i]
            self.cur_pq_sn = sn[i]


        self._t1 = time.time()

        return PQ_encode(ttime,channel,special)

    def do_get_data_fp(self):
        return self._data_fp

    def do_set_data_fp(self,val):
        self._data_fp = val

def PQ_encode(ttime, channel, special):
    """
    Decode the binary data into event time (absolute, highest precision),
    channel number and special bit. See PicoQuant (HydraHarp, TimeHarp, PicoHarp) 
    documentation about the details.
    """
    data = ttime + np.left_shift(channel,25) + np.left_shift(special,31)
    return data