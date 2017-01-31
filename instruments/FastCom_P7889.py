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

class P7889_Status(Structure):
    _fields_ = [
        ('started', c_int),
        ('runtime', c_double),
        ('totalsum', c_double),
        ('roisum', c_double),
        ('roirate', c_double),
        ('ofls', c_double),
        ('sweeps', c_double),
        ('stevents', c_double),
        ('maxval', c_ulong),
    ]

class P7889_Settings(Structure):
    _fields_ = [
        ('range', c_ulong),
        ('prena', c_long),
        ('cftfak', c_long), #don't know what this is
        ('roimin', c_ulong),
        ('roimax', c_ulong),
        ('eventpreset', c_double),
        ('timepreset', c_double),
        ('savedata', c_long),
        ('fmt', c_long), #format type
        ('autoinc', c_long), #auto increent filename
        ('cycles', c_long), 
        ('sweepmode', c_long),
        ('syncout', c_long), #bit 0..5 NIM syncout, bit 6..12 TTL syncout
        ('bitshift', c_long), #binwidth = 2**bitshift
        ('digval', c_long), #value for saml\ple changer (digval=0..255)
        ('digio', c_long), #use of digI/O line (see manual)
        ('dac0', c_long),
        ('dac1', c_long),
        ('swpreset', c_double), #sweep preset value
        ('nregions', c_long), #number of regions or whatever that may be        
        ('caluse', c_long),
        ('fstchan', c_double),
        ('active', c_long),
        ('calpoints', c_long),
    ]

class P7889_Data(Structure):
    '''
    Still has to be implemented, would be good to have since it unloads the p7889 program
    '''
    _fields_ = [
        ('to_be_implemented', c_int),
    ]



class FastCom_P7889(Instrument): #1
    '''
    This is the driver for the FastComTec P7889 multiple-event time digitizer card

    Usage:
    Initialize with
    <name> = qt.instruments.create('name', 'FastCom_P7889')
    
    status:
    -1) Solve Sweepmode bug=> solved!
     1) create this driver!=> is never finished
     2) There is a bug when starting up qtlab=> FIXED!
     3) Need to add sweepreset functionality => fixed
     4) debugged seepmode section

    TODO:
     - add Eventpreset, acq. delay, and holdaftersweep control
     - add control over inputs thresholds
    '''
    def __init__(self, name): #2
         # Initialize wrapper
        logging.info(__name__ + ' : Initializing instrument DP7889')
        Instrument.__init__(self, name, tags=['physical'])

        # Load dll and open connection
        self._load_dll()
        sleep(0.01)
        #self._Start_Server(False) #
        self._get_settings_overview()

        self.add_parameter('range', flags=Instrument.FLAG_GETSET, type=types.IntType)
        self.add_parameter('ROI_max', flags=Instrument.FLAG_GETSET, type=types.IntType)
        self.add_parameter('ROI_min', flags=Instrument.FLAG_GETSET, type=types.IntType)
        self.add_parameter('timebase', flags=Instrument.FLAG_GET, type=types.IntType)
        self.add_parameter('number_of_cycles', flags=Instrument.FLAG_GETSET, type=types.IntType)
        self.add_parameter('number_of_sequences', flags=Instrument.FLAG_GETSET, type=types.IntType)
        self.add_parameter('time_preset_length', flags=Instrument.FLAG_GETSET, type=types.IntType)
        self.add_parameter('binwidth',flags=Instrument.FLAG_GETSET, type=types.FloatType)
        self.add_parameter('sweep_preset_number',flags=Instrument.FLAG_GETSET,type=types.IntType)
        self.add_parameter('ROI_rate',flags=Instrument.FLAG_GET,type=types.IntType)
        self.add_parameter('state',flags=Instrument.FLAG_GET, type=types.BooleanType)

#########################
#       SWITCHES        #
#########################

    ######################    
    # sweepmode settings #
    ######################        
        self.add_parameter('sweepmode_sequential',flags=Instrument.FLAG_GETSET, type=types.BooleanType)
        self.add_parameter('sweepmode_time_differences',flags=Instrument.FLAG_GETSET, type=types.BooleanType)    
        self.add_parameter('sweepmode_software_start',flags=Instrument.FLAG_GETSET, type=types.BooleanType)
        self.add_parameter('sweepmode_wrap_around',flags=Instrument.FLAG_GETSET, type=types.BooleanType)
        self.add_parameter('sweepmode_start_event_generation',flags=Instrument.FLAG_GETSET, type=types.BooleanType)
        self.add_parameter('sweepmode_DMA',flags=Instrument.FLAG_GETSET, type=types.BooleanType)

    ######################
    # Preset settings    #
    ######################
        self.add_parameter('starts_preset',flags=Instrument.FLAG_GETSET, type=types.BooleanType)
        self.add_parameter('sweep_preset',flags=Instrument.FLAG_GETSET, type=types.BooleanType)
        self.add_parameter('time_preset',flags=Instrument.FLAG_GETSET, type=types.BooleanType)
        self.add_parameter('event_preset',flags=Instrument.FLAG_GETSET, type=types.BooleanType)

##########################        
# add functions          # 
##########################
        self.add_function('Start')
        self.add_function('Stop')
        self.add_function('Continue')

        self.add_function('get_range_ns')
        self.add_function('set_range_ns')
        self.add_function('get_binsize_ns')
        self.add_function('set_ROI_ns')

        self.add_function('get_timebase_ns')

        self.get_all()
        self.get_range()
        self.get_binwidth()
        self.get_number_of_cycles()

    def get_all(self):
        self._do_get_range()
        self._do_get_number_of_cycles()
        self.get_number_of_sequences()
        self.get_time_preset_length()
        self.get_sweep_preset_number()
        self._do_get_binwidth(True)

        self.get_sweepmode_sequential()
        self.get_sweepmode_time_differences()
        self.get_sweepmode_software_start()
        self.get_sweepmode_wrap_around()
        self.get_sweepmode_start_event_generation()
        #self.set_sweepmode_DMA(False) #Disables this buggy option
        self.get_state()
        self.get_starts_preset()
        self.get_sweep_preset()
        self.get_time_preset()
        self.get_event_preset()
        self.operation_mode = 'counter'
        self.integration_time = 50e-3
        


    def _load_dll(self,Load_Functions=False): #3
        '''
        Loads the functions from DP7889.dll

        Input:
            None

        Output:
            None
        '''
        print __name__ +' : Loading DP7889.dll'
        WINDIR=os.environ['WINDIR']
        self._DP7889_win32 = windll.LoadLibrary(WINDIR+'\\System32\\DP7889')
        sleep(0.02)


        if Load_Functions: #These are actually executed!!!! do not use. will crash MCDWIN
            self._DP7889_win32.Cont         =   self._DP7889_win32.RunCmd(0,"cont")
            self._DP7889_win32.Close        =   self._DP7889_win32.RunCmd(0,"exit")
            self._DP7889_win32.SaveSetting  =   self._DP7889_win32.SaveSetting

    def Start(self):    #4
        return self._DP7889_win32.Start(0)

    def Stop(self): #5
        return self._DP7889_win32.Halt(0)


    def Continue(self): #6
        self._DP7889_win32.Continue(0)

    # Base communication tools
    def _Start_Server(self,Start_MCDWIN=False): #7
        '''
        Starts the Server
        Only execute once.

        Input:
            None

        Output:
            None
        '''
        if not self.check_if_server_is_running():
            j=0
            not_loaded=True
            logging.warning(__name__ + ' : Server Program not yet started, starting it now')
            os.startfile("c:\\p7889\\p7889.EXE")
            #os.startfile('c:\\P7889\\','explore')
            #   sleep(2)
             #   j=j+1
              #  not_loaded = not self.check_if_server_is_running()
               # if j==4:
             #       logging.warning(__name__ + ' : Server Start time-out')
            #sleep(2)
        else:
            logging.warning(__name__ + ' : Server is already running!')
        sleep(0.05)
        #if self.check_if_server_is_running():
         #   print __name__ + self.check_if_serveSetNumberOfCyclesr_is_running()
        #else:            
         #   logging.error(__name__ + ' : Unable to open Server Program')
         #   self._card_is_open = False
        if Start_MCDWIN:
            sleep(0.05)
            logging.warning(__name__ + ' : Starting MCDWIN')
            os.startfile("c:\\p7889\\MyMCDWIN.EXE")
        #print __name__ + ' Server running? : %s '%self.check_if_server_is_running()

    def exit_server(self): #8
        self._DP7889_win32.Exit

    def check_if_server_is_running(self): #9
        return self._DP7889_win32.GetStatus(0)==1

    def RunCmd(self, Command=''): #10
        #print __name__ + ': %s' %Command
        return self._DP7889_win32.RunCmd(0,Command)

######### Start SETTINGS SECTION ###################################################################################

    ########## Some general settings functionality #######################################################################

    def _get_settings(self): #this is to keep it compatible with other functions
        settings = P7889_Settings()
        st = self._DP7889_win32.GetSettingData(byref(settings), 0)
        self.settings = settings
        return self.settings

    def get_settings_structure(self): #this is to keep it compatible with other functions
        settings = P7889_Settings()
        st = self._DP7889_win32.GetSettingData(byref(settings), 0)
        self.settings = settings
        return self.settings

    def _do_get_ROI_rate(self):
        self.get_status()
        return self.RoiRate



    def _get_setting(self,Setting='', NextSetting=''): #12
        '''
        Some settings can not be extracted directly from the dll, 
        so here the config file is saved and read instead
        '''
        check = True #= self.check_if_server_is_running():
        if check:
            settings=''
            settings    =     self._get_settings_overview()
            while settings=='':
                sleep(0.05)
            start       =       settings.rfind('%s' %Setting)+len(Setting)
            stop        =       settings.rfind('%s' %NextSetting)-1
            return settings[start:stop]
        else:
            logging.warning(__name__ + ' : Server not running!')

    def _get_settings_overview(self): #11
        '''
        This opens the configfile of the card and returns its contents as a string
        07:48'''
        x=0
        while x == 0:
            x=self._DP7889_win32.SaveSetting()
            sleep(0.05)
        #GetSet          =       open('C:\P7889\pythonA.cfg','r')
        GetSet          =       open('C:\P7889\p7889A.cfg','r')
        self.Settings   =       GetSet.read()
        return self.Settings

    ############### get specific settings ##########################

    def _do_get_range(self, get_from_dll=True): #14
        '''
        Gets the current range. It sets the size of one dimension of the data array
        '''        
        if get_from_dll:
            settings = self._get_settings()
            # I, NK, reverted tis from self.a_range = settings.range to the previous setting.
            try:
                self.a_range=settings.range/settings.cycles
            except ZeroDivisionError:
                self.a_range = 0.
                print 'self.arange set to 0'
        else:
            pass
        return self.a_range

    def _do_get_number_of_cycles(self, get_from_dll=True):#28
        '''
        Gets the current number of cycles. 
        '''
        if get_from_dll:
            settings = self._get_settings()
            self.a_number_of_cycles = settings.cycles
        return self.a_number_of_cycles

    def _do_get_time_preset_length(self, get_from_dll = True):
        if get_from_dll:
            settings = self._get_settings()
            self.a_time_preset_length= settings.timepreset
        return self.a_time_preset_length

    def _do_get_binwidth(self, get_from_dll=False): #36
        if get_from_dll:
            settings = self._get_settings()
            self.a_binwidth=2**settings.bitshift #multiples of 100 ps
        return self.a_binwidth

    def _do_get_sweep_preset_number(self, get_from_dll = True): #38
        if get_from_dll:
            settings = self._get_settings()
            self.a_sweep_preset_number = settings.swpreset
        return self.a_sweep_preset_number

    def _do_get_number_of_sequences(self): #32
        '''
        Gets the number of sequences.
        '''
        self.a_number_of_sequences = int(self._get_setting('sequences=','dac0'), 10)
        return self.a_number_of_sequences

    def _do_get_ROI_min(self, get_from_dll = True): #41
        if get_from_dll:
            settings = self._get_settings()
            self.a_roimin = settings.roimin
        return self.a_roimin

    def _do_get_ROI_max(self, get_from_dll = True): #41
        if get_from_dll:
            settings = self._get_settings()
            self.a_roimax = settings.roimax
        return self.a_roimax

    ############### set specific settings ##########################

    def _do_set_number_of_cycles(self,numberofcycles): #26
        '''
        Sets the number of sequence cycles.
        '''
        self.RunCmd('cycles=%s' %numberofcycles)
        self.a_number_of_cycles=self._do_get_number_of_cycles()

    def _do_set_time_preset_length(self, time_length):
        '''
        Sets the number of sequence cycles.
        '''
        self.RunCmd('rtpreset=%s' %time_length)
        self.a_time_preset_length=self._do_get_time_preset_length()

    def _do_set_number_of_sequences(self,numberofsequences): #30
        '''
        Sets the number of sequences.
        '''
        self.RunCmd('sequences=%s' %numberofsequences)
        self.a_number_of_sequences=self._do_get_number_of_sequences()

    def _do_set_binwidth(self,binwidth): #33
        '''
        Sets the time bin width, be carefull
        SETS POWERS OF TWO (Binwidth: 0=>1, 1=>2, 2=>4, 3=>8, etc.
        '''
        bitshift = numpy.log2(binwidth)
        self.RunCmd('bitshift=%s' %bitshift)
        binwidth=2**bitshift
        #print __name__ + 'Binwidth set to: 0.1x%s ns' %binwidth
        self.a_binwidth=binwidth
        return binwidth

    def _do_set_sweep_preset_number(self, SweepPreset): #37
        self.RunCmd('swpreset=%s' %SweepPreset)
        self.a_sweep_preset_number=self._do_get_sweep_preset_number()

    def _do_set_acq_delay(self,Delay): #39
        '''
        function does not work yet
        '''
        logging.error(__name__ + ': This function does not yet work')
        #self.RunCmd('

    def _do_get_acq_delay(self): #40
        '''
        function does not work yet
        '''
        logging.error(__name__ + ': This function does not yet work')
        #self.RunCmd('

    def _do_set_ROI_min(self,ROImin): #42
        self.RunCmd('roimin=%s' %ROImin)

    def _do_set_ROI_max(self,ROImax): #44
        self.RunCmd('roimax=%s' %ROImax)


    def _do_set_range(self, Range): #15
        '''
        Sets the time range over which is measured
        '''
        self.RunCmd('range=%s' %Range)
        set_range=self._do_get_range(True)
        self._do_set_ROI_max(set_range-64)
        #print __name__ + ': Range set to %s' %set_range
        self.a_range=set_range
        return self.a_range

######### End SETTINGS SECTION ###################################################################################

######### Start STATUS SECTION ###################################################################################

    def get_status(self):
        status = P7889_Status()

        x = self._DP7889_win32.GetStatusData(byref(status), 0)
        
        self.running      = status.started
        self.runtime      = status.runtime
        self.totalsum     = status.totalsum
        self.RoiSum       = status.roisum
        self.RoiRate      = status.roirate
        self.Fifo_full    = status.ofls
        self.Sweeps       = status.sweeps
        self.Start_events = status.stevents
        return status
    
        
    def do_get_state(self):
        self._state = self.get_server_running()==1
        return self._state
        
    def get_server_running(self):
        self.get_status()
        return self.running
    def get_runtime(self):
        self.get_status()
        return self.runtime
    def get_total_sum(self):
        self.get_status()
        return self.totalsum
    def get_RoiSum(self):
        self.get_status()
        return self.RoiSum
    def get_RoiRate(self):
        self.get_status()
        return self.RoiRate
    def get_Fifo_full(self):
        self.get_status()
        return self.Fifo_full
    def get_Sweeps(self):
        self.get_status()
        return self.Sweeps
    def get_Start_events(self):
        status = self.get_status()
        return self.Start_events    

######### End STATUS SECTION ###################################################################################

######### Start DATA SECTION ###################################################################################

    def _do_get_timebase(self): #17
        length          =       int(self._do_get_range())
        # delta_t         =       self._do_get_binwidth()*0.1 #binwidth in ns
        timerange       =       numpy.arange(length)#,dtype='int')#numpy.linspace(0, length, length, False)
        self.a_timebase =       timerange
        return self.a_timebase

    def get_timebase_ns(self): #17
        delta_t         =       self._do_get_binwidth()*0.1 #binwidth in ns
        timerange       =       self.get_timebase()*delta_t
        return timerange

    def get_1Ddata(self,plot_data=False,time=0.2): #18
        '''
        Gets 1D start-stop data
        '''
        timerange, length   =       self._do_get_timebase()
        data                =       numpy.array(numpy.zeros(length), dtype = numpy.uint32)

        self._DP7889_win32.LVGetDat(data.ctypes.data,0) #writes data into memory @ pointer data.ctypes.data
        
        if plot_data:
            Figure=Gnuplot.Gnuplot()
            Figure.plot(data)
            sleep(time)
        return timerange, data

    def _do_get_number_of_stops(self): #19
        if self._do_get_sweepmode_sequential():
            dat=self.get_2Ddata()
            print 'Card is in sequential mode'
        else:
            dat=self.get_1Ddata()
        x=dat[1]
        return x.sum()

    def _do_get_runtime(self): #21
        time=numpy.array([0],dtype=numpy.double)
        self._DP7889_win32.LVGetCnt(time.ctypes.data,0)
        return types.FloatType(time)
    
    def switch_to_counter_mode(self, int_time=50):
        # if integration_time == None:
        #     integration_time = self.integration_time
        # else:
        #     pass   
        # self._disable_all_sweepmodes()
        # self._disable_all_presets()
        # self.set_binwidth(24) #sets it to 1677721.6 ns or 1.6 us
        # range = self._do_set_range(integration_time/1.6777216e-6)
        # self._do_set_ROI_max(range)
        # self.integration_time = 1.6777216e-6*range
        # self.set_sweepmode_software_start(True)
        # self.set_sweep_preset(True)
        # self.set_sweep_preset_number(1)
        # self.operation_mode = 'counter' 
        #self._disable_all_sweepmodes()
        #self._disable_all_presets()
        #self.set_binwidth(1)
        #self.set_range(100)
        self._last_t=0
        self._last_sweep_count=0
        self.Start()
        sleep(int_time/1000.)
        self.Stop()
        sleep(0.3)
        return float(self.get_Sweeps())/self.get_runtime()



    def _do_get_counts(self):
        if self.operation_mode is 'counter':
            pass
        else:
            self.switch_to_counter_mode(self.integration_time)
            DP7889.Start()
            sleep(0.1)
            while self.get_server_running:
                sleep(0.1)

                
        return self.get_RoiSum()

    def _do_get_count_rate(self):
        return self._do_get_counts()/self.integration_time  

    def get_count_rate(self):
        return self._do_get_counts()/self.integration_time  



    def switch_to_TOF_mode(self):
        pass


# Maybe need to remove #20 and #21 since it are not really count rates
#20
        

    def _do_get_average_stops_per_second(self): #22
        totalcounts=self._do_get_number_of_stops()
        sleep(0.05)
        totaltime=self._do_get_runtime()
        return types.FloatType(totalcounts/totaltime)



    def get_2Ddata(self): #24
        '''
        Gets 2D start-stop data
        '''
        timerange =       self.get_timebase_ns()
        sleep(0.1)
        length    =        int(self._do_get_range())
        print 'timebase extracted'
        traces              =       int(self._do_get_number_of_cycles())
        print 'traces extracted'
        sleep(0.1)
        # tracearray          =       numpy.array(numpy.linspace(0, traces-1, traces))
        # data                =       numpy.array(numpy.zeros((traces, length)), dtype = numpy.uint32)
        tracearray          =       numpy.linspace(0, traces-1, traces, dtype='int')
        data                =       numpy.zeros((traces, length), dtype = numpy.uint32) # could try uint64...?
        print 'exctracting actual data'
        self._DP7889_win32.LVGetDat(data.ctypes.data,0)
        # data = self.fake_data(traces, length)
        print 'data transferred'
        sleep(1.)
        # if traces>200:
        sleep(2*traces/1000.)

        return timerange/(self._do_get_binwidth()*0.1), tracearray, data
    
    def fake_data(self, xl, yl):
        data = numpy.zeros((xl, yl))
        for x in arange(xl):
            data[x,int(yl/2)] = 10 + numpy.random.randn()
        return data



        



#############################################################
# Below the sweepmoderoutines are defined. The sweepmodeparameters (the checkedboxes and more in the server program)
# are set by a 14 bit hex number. Below shows a function that sets the attributes of the instrument. It shows a list of 
# the parameters it sets and the corresponding bit number (#'bitno'). So all routines in this part of the driver are to
# convert hex to a list of 14 1's and 0's, change individual bits, and convert it back to a hex number. The principle 
# is easy but it took me long enough to get it working. The settings it controls and the bit they belong to are shown below
#
#sweepmode=280 ; (hex) sweepmode & 0xF: 0 = normal, 4=sequential
#                                bit 4: Softw. Start
#                                bit 5: DMA mode
#                                bit 6: Wrap around
#                                bit 7: Start event generation
#                                bit 8: Enable Tag bits
#                           bit (9,10): 0=rising, 1=falling, 2=both, 3=both+CFT
#                               bit 11: pulse width
#                               bit 12: 6 bits of Sweepcounter in Data
#                               bit 13: card ID in data
###############################################################


    def _get_sweepmode(self): #45
        settings    =   self._get_settings()
        sweepmode   =   settings.sweepmode
        Sweepmodebits_str =   self.hex2bin(sweepmode)
        if Sweepmodebits_str =='0':
            Sweepmodebits_lstCheck=Sweepmodebits_lst=14*[0]
        else:
            length=Sweepmodebits_str.__len__()
            iter=Sweepmodebits_lst=length*[0]
            l=0
            for i in iter:
                Sweepmodebits_lst[l]=int(Sweepmodebits_str[l],2)
                l=l+1
            Sweepmodebits_lstCheck = Sweepmodebits_lst
            if length < 14: #it is a 14 bit number that defines the Sweepmode
                Sweepmodebits_lst=(14-length)*[0]+Sweepmodebits_lst
        #print __name__ + 'Settings as read from file: %s'%sweepmode
        #print __name__ + '_get_sweepmode() result: %s' %Sweepmodebits_str
        #print __name__ + 'Calculated bitlist before zeros: %s' %Sweepmodebits_lstCheck 
        #print __name__ + 'and after zeros:                 %s' %Sweepmodebits_lst
        return Sweepmodebits_lst    
    
   
    def _get_sweepmode_settings_from_server(self,OnScreen=True): #46
        Sweepmodebitlist = self._get_sweepmode()
        self._set_sweepmode_attributes(Sweepmodebitlist,OnScreen)
        return Sweepmodebitlist

    def _set_sweepmode_attributes(self,Sweepmodesettingsbinlist, OnScreen = False): #47
        OnScreen=False #Overide
        #print __name__ + 'Setting attributes using %s' %Sweepmodesettingsbinlist
        self.sweepmode_mode_set_to_timediff                   =       Sweepmodesettingsbinlist[13]  #00

        if Sweepmodesettingsbinlist[11]==1:                                                         #02&01
            self.sweepmode_mode_set_to_normal                 =       False                         
            self.sweepmode_mode_set_to_sequential_cycles      =       True                          
        else:                                                                                       #02&01
            self.sweepmode_mode_set_to_normal                 =       True                          
            self.sweepmode_mode_set_to_sequential_cycles      =       False                         

        self.sweepmode_softw_start_enabled                    =       Sweepmodesettingsbinlist[10]  #03
        self.sweepmode_DMA_mode_enabled                       =       Sweepmodesettingsbinlist[ 8]  #05
        self.sweepmode_wrap_around_enabled                    =       Sweepmodesettingsbinlist[ 7]  #06
        self.sweepmode_start_event_generation_enabled         =       Sweepmodesettingsbinlist[ 6]  #07
        self.sweepmode_tagged_bits_enabled                    =       Sweepmodesettingsbinlist[ 5]  #08

        if Sweepmodesettingsbinlist[ 4]==0 and Sweepmodesettingsbinlist[ 3]==0:                     #0910
            self.sweepmode_inputedges_set_to_rising           =       True
            self.sweepmode_inputedges_set_to_falling          =       False
            self.sweepmode_inputedges_set_to_both             =       False
            self.sweepmode_inputedges_set_to_both_CFT         =       False
        elif Sweepmodesettingsbinlist[ 4]==1 and Sweepmodesettingsbinlist[ 3]==0:                #0910
            self.sweepmode_inputedges_set_to_rising           =       False
            self.sweepmode_inputedges_set_to_falling          =       True
            self.sweepmode_inputedges_set_to_both             =       False
            self.sweepmode_inputedges_set_to_both_CFT         =       False
        elif Sweepmodesettingsbinlist[ 4]==0 and Sweepmodesettingsbinlist[ 3]==1:                #0910
            self.sweepmode_inputedges_set_to_rising           =       False
            self.sweepmode_inputedges_set_to_falling          =       False
            self.sweepmode_inputedges_set_to_both             =       True
            self.sweepmode_inputedges_set_to_both_CFT         =       False
        elif Sweepmodesettingsbinlist[ 4]==3 and Sweepmodesettingsbinlist[ 3]==1:                #0910
            self.sweepmode_inputedges_set_to_rising           =       False
            self.sweepmode_inputedges_set_to_falling          =       False
            self.sweepmode_inputedges_set_to_both             =       False
            self.sweepmode_inputedges_set_to_both_CFT         =       True

        self.sweepmode_inputedges_set_fall_bothedge           =       Sweepmodesettingsbinlist[ 3]  #10
        self.sweepmode_record_pulse_width                     =       Sweepmodesettingsbinlist[ 2]  #11
        self.sweepmode_sweepcounterbit_enabled                =       Sweepmodesettingsbinlist[ 1]  #12
        self.sweepmode_Card_ID_enabled                        =       Sweepmodesettingsbinlist[ 0]  #13
        
        if OnScreen:
            print __name__ + ': mode set to timediff:                              %s' %(self.sweepmode_mode_set_to_timediff==1)
            print __name__ + ': mode set to normal:                                %s' %(self.sweepmode_mode_set_to_normal==1)
            print __name__ + ': mode set to Sequential cycles:                     %s' %(self.sweepmode_set_mode_to_sequential_cycles==1)
            print __name__ + ': Software start Enabled:                            %s' %(self.sweepmode_softw_start_enabled==1)
            print __name__ + ': DMA_mode_enabled!!!:                               %s' %(self.sweepmode_DMA_mode_enabled==1)
            print __name__ + ': wrap around enabled:                               %s' %(self.sweepmode_wrap_around_enabled==1)
            print __name__ + ': Start event generation enabled:                    %s' %(self.sweepmode_start_event_generation_enabled==1)
            print __name__ + ':   Tagged bits enabled                                  %s' %(self.sweepmode_tagged_bits_enabled==1)
            print __name__ + ':   inputedges set both to rising :                      %s' %(self.sweepmode_inputedges_set_to_rising==1)
            print __name__ + ':   inputedges set to falling:                           %s' %(self.sweepmode_inputedges_set_to_falling==1)
            print __name__ + ':   inputedges set to both:                              %s' %(self.sweepmode_inputedges_set_to_both==1)
            print __name__ + ':   inputedges set to both+CFT:                          %s' %(self.sweepmode_inputedges_set_to_both==1)
            print __name__ + ':   record pulsewidth??:                                 %s' %(self.sweepmode_record_pulse_width==1)
            print __name__ + ':   6bits Sweep counter bit enabled:                     %s' %(self.sweepmode_inputedges_set_to_both_CFT==1)
            print __name__ + ':   CardID enabled??:                                    %s' %(self.sweepmode_Card_ID_enabled==1)
            print __name__ + 'Note: The indentation is to indicate the ones that do not yet have their own GETSET functions.'
    

    def _set_sweepmode_parameter_at_index(self,Parnr,state,IsLastChange=True):#48
        Sweepmodesettingbitlist=self._get_sweepmode_settings_from_server() 
        Sweepmodesettingbitlist[Parnr]=int(state)
        if IsLastChange:
            self._send_sweepmode_settings_to_server(Sweepmodesettingbitlist)
            Sweepmodesettingbitlist=self._get_sweepmode_settings_from_server()
            while not Sweepmodesettingbitlist[Parnr]==int(state):
                print __name__ + ' Sweepmode not set!'
                sleep(0.05)
                self._send_sweepmode_settings_to_server(Sweepmodesettingbitlist)
            #print __name__ + ': Sweepmode Settings Updated'
    
    def _get_sweepmode_parameter_at_index(self,Parnr): #49
        '''
        This is used to set individual sweepmode parameters Parnr refers to the bit number belonging to the setting
        '''
        Sweepmodesettingbitlist=self._get_sweepmode_settings_from_server()
        return Sweepmodesettingbitlist[Parnr]==1

    '''
    Below all the relevant sweepmode getset functions are definined. To add one more just use self._get_sweepmode_parameter_at_index(self,Parnr): 
    in the way as is used below
    '''
    def _do_set_sweepmode_normal(self,state=True,IsLastChange=True): #50
        self._set_sweepmode_parameter_at_index(11, not state, IsLastChange)
    def _do_get_sweepmode_normal(self):
        return self._get_sweepmode_parameter_at_index(11)==False


    def _do_set_sweepmode_time_differences(self,state=True,IsLastChange=True): #51
        self._set_sweepmode_parameter_at_index(13, state, IsLastChange)
    def _do_get_sweepmode_time_differences(self):
        return self._get_sweepmode_parameter_at_index(13)


    def _do_set_sweepmode_sequential(self,state=True,IsLastChange=True): #52
        self._set_sweepmode_parameter_at_index(11, state, IsLastChange)
    def _do_get_sweepmode_sequential(self):
        return self._get_sweepmode_parameter_at_index(11)



    def _do_set_sweepmode_software_start(self,state=False, IsLastChange=True): #53
       self._set_sweepmode_parameter_at_index(9, state, IsLastChange)
    def _do_get_sweepmode_software_start(self):
       return self._get_sweepmode_parameter_at_index(9)


    def _do_set_sweepmode_wrap_around(self,state=False, IsLastChange=True): #54
       self._set_sweepmode_parameter_at_index(7, state, IsLastChange)
    def _do_get_sweepmode_wrap_around(self):
       return self._get_sweepmode_parameter_at_index(7)



    def _do_set_sweepmode_start_event_generation(self,state=False,IsLastChange=True): #55
        self._set_sweepmode_parameter_at_index(6, state, IsLastChange)
    def _do_get_sweepmode_start_event_generation(self):
        return self._get_sweepmode_parameter_at_index(6)


    def _do_set_sweepmode_DMA(self,state=False,IsLastChange=True): #56
        if state:
            print __name__ + ' Warning, this setting will crash the computer if used at low event rates!'
            self._set_sweepmode_parameter_at_index(8, True, IsLastChange)

        else:
            self._set_sweepmode_parameter_at_index(8, False, IsLastChange)
    def _do_get_sweepmode_DMA(self):
        return self._get_sweepmode_parameter_at_index(8)



    def _disable_all_sweepmodes(self): #57
        self.RunCmd('sweepmode=0x0')
        Sweepmodesettingbitlist=self._get_sweepmode_settings_from_server()


    def _send_sweepmode_settings_to_server(self,SweepmodeSettingsbinlist): #58
        setting=self._create_hex_from_settings(SweepmodeSettingsbinlist)
        setstring = 'sweepmode=%s' %setting
        self.RunCmd(setstring)
        self._DP7889_win32.SaveSetting()
        #sleep(0.01)
        #print __name__ + 'Sent to server %s' %setstring
        #print __name__ + setting

    def hex2bin(self,number): #59
        if number == 0:
            bitlist='0'
        else:
            hex2bin = {"0":"0000", "1":"0001", "2":"0010", "3":"0011",
                       "4":"0100", "5":"0101", "6":"0110", "7":"0111",
                       "8":"1000", "9":"1001", "A":"1010", "B":"1011",
                       "C":"1100", "D":"1101", "E":"1110", "F":"1111"}
            bitlist="".join([hex2bin[h] for h in '%X'%number]).lstrip('0')
        #print __name__ + 'bitlist= %s' %bitlist
        return bitlist
    
    def _create_hex_from_settings(self,settings): #60
        k=0
        total=0
        #print __name__ + 'create settingshex from: %s'%settings
        for x in settings:
            d=2**k
            element=(settings[-k-1]*(2**k))
            k=k+1
            total=total+element
            #print __name__ + ' total: %s' %total
        self.SweepmodeSettingsHEX=hex(total)
        return hex(total)

############################
#Next section implements control over wether starts_preset or sweep_preset is enabled or if they are both disabled. 
#Details of what it controls are shown in the list below
#
# prena=0         Presets enabled (hex)
#                 bit 0: real time preset enabled
#                 bit 2: sweep preset enabled
#                 bit 3: ROI preset enabled
#                 bit 4: Starts preset enabled
#There are two strategies for setting the options. One is for when there are multiple changes
#, and one for when there is only one parameter that needs to be varied. For multiple changes first set the attributes (64)
#and then send them all to the server at once using (63)
#
#
############################

    def _do_get_preset_settings(self, Onscreen=False): #61
        prena=int(self._get_setting('prena=', 'syncout'), 16)
        bitlist=self.hex2bin(prena)
        if size(bitlist)<5:
            bitlist = (5-len(bitlist))*'0' + bitlist
        bitlist=bitlist[::-1]
        prena_table=5*[False]
        for k in arange(0,5):
            prena_table[k]= bitlist[k] == '1' 
        self._set_preset_attributes(bitlist, Onscreen)
        return prena_table ##not needed i think

    def _do_set_preset_settings_at_index(self, Parnr, state): #62
        prena_table=self._do_get_preset_settings()
        #if Parnr == 2 or Parnr == 4:
        #    prena_table[8/Parnr]= (not state)
        prena_table[Parnr] = state
        self._send_prena_table_to_server(prena_table)
        
    def _send_prena_table_to_server(self, prena_table): #63
        prena=self._create_hex_from_settings(prena_table[::-1])
        setstring = 'prena=%s' %prena
        self.RunCmd(setstring)
        self._DP7889_win32.SaveSetting()
        prena_table=self._do_get_preset_settings()
        self._set_preset_attributes(prena_table)
        
    
    def _set_preset_attributes(self, prena_table, Onscreen=False):  #64     
                                                                        #   dec.   hex
        self.preset_setting_time_preset_enabled   = prena_table[0]      #   1        1
        self.preset_setting_sweep_preset_enabled  = prena_table[2]      #   4        4
        self.preset_setting_event_preset_enabled  = prena_table[3]      #   8        8
        self.preset_setting_starts_preset_enabled = prena_table[4]      #   16      10
        if Onscreen:
            print 'Setting:               |'
            print 'time   preset enabled  | %s' %prena_table[0]
            print 'sweep  preset enabled  | %s' %prena_table[2]
            print 'event  preset enabled  | %s' %prena_table[3]
            print 'starts preset enabled  | %s' %prena_table[4]

    def _get_prena_table_from_attributes(self): #65
        prena_table=5*[False]
        prena_table[0] = self.preset_setting_time_preset_enabled      #   1        1
        prena_table[2] = self.preset_setting_sweep_preset_enabled     #   4        4
        prena_table[3] = self.preset_setting_event_preset_enabled     #   8        8
        prena_table[4] = self.preset_setting_starts_preset_enabled    #   16      10
        return prena_table

    def _update_prena_settings(self): #66
        prena_table = self._get_prena_table_from_attributes()
        self._send_prena_table_to_server(self, prena_table)
        print 'updated'

# Here are the methods to set them individually
################################################

    def _do_set_starts_preset(self,state): #67
        self._do_set_preset_settings_at_index(4, state)
    def _do_get_starts_preset(self):
        prena_table=self._do_get_preset_settings()
        self._set_preset_attributes(prena_table)
        return prena_table[4]

    def _do_set_sweep_preset(self,state): #68
        self._do_set_preset_settings_at_index(2, state)
    def _do_get_sweep_preset(self):
        prena_table=self._do_get_preset_settings()
        self._set_preset_attributes(prena_table)
        return prena_table[2]

    def _do_set_event_preset(self,state): #69
        self._do_set_preset_settings_at_index(3, state)
    def _do_get_event_preset(self):
        prena_table=self._do_get_preset_settings()
        self._set_preset_attributes(prena_table)
        return prena_table[3]

    def _do_set_time_preset(self,state): #70
        self._do_set_preset_settings_at_index(0, state)
    def _do_get_time_preset(self):
        prena_table=self._do_get_preset_settings()
        self._set_preset_attributes(prena_table)
        return prena_table[0]

    def _disable_all_presets(self): #71
        self.RunCmd('prena=0x0')
        self._do_get_preset_settings()

    def _disable_all(self):
        self._disable_all_presets()
        self._disable_all_sweepmodes()

    def get_binsize_ns(self):
        return 0.1 * 2**(self.get_binwidth()-1)

    def set_range_ns(self, val):
        self.set_range(val/self.get_binsize_ns())

    def get_range_ns(self):
        return self.get_binsize_ns() * self.get_range()

    def set_ROI_ns(self,min_ns,max_ns):
        self.set_ROI_min(min_ns/self.get_binsize_ns())
        self.set_ROI_max(max_ns/self.get_binsize_ns())