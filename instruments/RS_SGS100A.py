# RS_SGS100A.py class, to perform the communication between the Wrapper and the device
# AR and NK 2015

from instrument import Instrument
import visa
import types
import logging
import socket
import select
from time import sleep, time

def has_newline(ans):
    if len(ans) > 0 and ans.find('\n') != -1:
        return True
    return False

class SocketVisa:
    def __init__(self, host, port):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((host, port))
        self._socket.settimeout(20)

    def clear(self):
        rlist, wlist, xlist = select.select([self._socket], [], [], 0)
        if len(rlist) == 0:
            return
        ret = self.read()
        print 'Unexpected data before ask(): %r' % (ret, )

    def write(self, data):
        self.clear()
        if len(data) > 0 and data[-1] != '\r\n':
            data += '\n'
        # if len(data)<100:
        # print 'Writing %s' % (data,)
        self._socket.send(data)

    def read(self,timeouttime=20):
        start = time()
        try:
            ans = ''
            while len(ans) == 0 and (time() - start) < timeouttime or not has_newline(ans):
                ans2 = self._socket.recv(8192)
                ans += ans2
                if len(ans2) == 0:
                    sleep(0.01)
            #print 'Read: %r (len=%s)' % (ans, len(ans))
            AWGlastdataread = ans
        except socket.timeout, e:
            print 'Timed out'
            return ''

        if len(ans) > 0:
            ans = ans.rstrip('\r\n')
        return ans

    def ask(self, data):
        self.clear()
        self.write(data)
        return self.read()


class RS_SGS100A(Instrument):
    '''
    This is the python driver for the Rohde & Schwarz SMR40
    signal generator

    Usage:
    Initialize with
    <name> = instruments.create('name', 'RS_SGS100A', address='<GPIB address>',
        reset=<bool>)
    '''

    def __init__(self, name, address, reset=False,max_cw_pwr=-5):
        '''
        Initializes the RS_SGS100A, and communicates with the wrapper.

        Input:
            name (string)    : name of the instrument
            address (string) : GPIB address
            reset (bool)     : resets to default values, default=false

        Output:
            None
        '''
        logging.info(__name__ + ' : Initializing instrument')
        Instrument.__init__(self, name, tags=['physical', 'source'])

        self._address = address
        # if address[:5] == 'TCPIP':
        #     self._visainstrument = SocketVisa(self._address[8:], 5025)
        # else:
        rm = visa.ResourceManager()
        
        self._visainstrument = rm.open_resource(address, timeout=60000)
        self.add_parameter(
            'frequency', type=types.FloatType, flags=Instrument.FLAG_GETSET,
            minval=1e9, maxval=20e9, units='Hz',  # format='%.12e',
            tags=['sweep'])
        self.add_parameter(
            'phase', type=types.FloatType,
            flags=Instrument.FLAG_GETSET | Instrument.FLAG_GET_AFTER_SET,
            minval=0, maxval=360, units='DEG', format='%.01e', tags=['sweep'])
        self.add_parameter(
            'power',
            type=types.FloatType,
            flags=Instrument.FLAG_GETSET | Instrument.FLAG_GET_AFTER_SET,
            minval=-120, maxval=25, units='dBm',
            tags=['sweep'])
        self.add_parameter(
            'status', type=types.StringType,
            flags=Instrument.FLAG_GETSET | Instrument.FLAG_GET_AFTER_SET)
        self.add_parameter(
            'pulm', type=types.StringType,
            flags=Instrument.FLAG_GETSET | Instrument.FLAG_GET_AFTER_SET)
        self.add_parameter(
            'iq', type=types.StringType,
            flags=Instrument.FLAG_GETSET | Instrument.FLAG_GET_AFTER_SET)
        # self.add_parameter(
        #     'pulsemod_source', type=types.StringType,
        #     flags=Instrument.FLAG_GETSET | Instrument.FLAG_GET_AFTER_SET)


        self.add_parameter('sweep_frequency_start', type=types.FloatType,
            flags=Instrument.FLAG_SET,
            minval=9e3, maxval=40e9,
            units='Hz', format='%.04e',
            tags=['sweep'])
        
        self.add_parameter('sweep_frequency_stop', type=types.FloatType,
            flags=Instrument.FLAG_SET,
            minval=9e3, maxval=40e9,
            units='Hz', format='%.04e',
            tags=['sweep'])
        
        self.add_parameter('sweep_frequency_step', type=types.FloatType,
            flags=Instrument.FLAG_SET,
            minval=1, maxval=1e9,
            units='Hz', format='%.04e',
            tags=['sweep'])
        
        self.add_parameter('max_cw_pwr',
                type=types.FloatType,
                flags=Instrument.FLAG_GETSET,
                minval=-30, maxval=30, units='dBm')


        # can be different from device to device, set by argument
        self.set_max_cw_pwr(max_cw_pwr)
        self.add_function('reset')
        self.add_function('get_all')
        self.add_function('get_errors')
        self.add_function('get_error_queue_length')

        if reset:
            self.reset()
        else:
            self.get_all()

    # Functions

    def perform_internal_adjustments(self,all_f = False,cal_IQ_mod=True):
        status=self.get_status()
        self.off()
        if all_f:
            s=self._visainstrument.ask('CAL:ALL:MEAS?')
        else:
            s=self._visainstrument.ask('CAL:FREQ:MEAS?')
            print 'Frequency calibrated'
            s=self._visainstrument.ask('CAL:LEV:MEAS?')
            print 'Level calibrated'
            if cal_IQ_mod:
                self.set_iq('on')
                s=self._visainstrument.ask('CAL:IQM:LOC?')
                print 'IQ modulator calibrated'
        
        self.set_status('off')
        self.set_pulm('off')
        self.set_iq('off')
        sleep(0.1)    
        
    def reset(self):
        '''
        Resets the instrument to default values

        Input:
            None

        Output:
            None
        '''
        logging.info(__name__ + ' : Resetting instrument')
        self._visainstrument.write('*RST')
        self.get_all()

    def get_all(self):
        '''
        Reads all implemented parameters from the instrument,
        and updates the wrapper.

        Input:
            None

        Output:
            None
        '''
        logging.info(__name__ + ' : reading all settings from instrument')
        self.get_frequency()
        self.get_power()
        self.get_status()

    # communication with machine

    def do_get_frequency(self):
        '''
        Get frequency from device

        Input:
            None

        Output:
            frequency (float) : frequency in Hz
        '''
        logging.debug(__name__ + ' : reading frequency from instrument')
        return float(self._visainstrument.ask('SOUR:FREQ?'))

    def do_set_frequency(self, frequency):
        '''
        Set frequency of device

        Input:
            frequency (float) : frequency in Hz

        Output:
            None
        '''
        logging.debug(__name__ + ' : setting frequency to %s GHz' % frequency)
        self._visainstrument.write('SOUR:FREQ %s' % frequency)

    def _do_set_sweep_frequency_start(self, frequency):
        '''
        Set start frequency of sweep

        Input:
            frequency (float) : frequency in Hz

        Output:
            None
        '''
        logging.debug(__name__ + ' : setting sweep frequency start to %s GHz' % frequency)
        self._visainstrument.write('SOUR:FREQ:STAR %e' % frequency)

    def _do_set_sweep_frequency_stop(self, frequency):
        '''
        Set stop frequency of sweep

        Input:
            frequency (float) : frequency in Hz

        Output:
            None
        '''
        logging.debug(__name__ + ' : setting sweep frequency stop to %s GHz' % frequency)
        self._visainstrument.write('SOUR:FREQ:STOP %e' % frequency)

    def _do_set_sweep_frequency_step(self, frequency):
        '''
        Set step frequency of sweep

        Input:
            frequency (float) : frequency in Hz

        Output:
            None
        '''
        logging.debug(__name__ + ' : setting sweep frequency step to %s GHz' % frequency)
        self._visainstrument.write('SOUR:SWE:FREQ:STEP:LIN %e' % frequency)


    def _do_get_power(self):
        '''
        Get output power from device

        Input:
            None

        Output:
            power (float) : output power in dBm
        '''
        logging.debug(__name__ + ' : reading power from instrument')
        return float(self._visainstrument.ask('SOUR:POW?'))

    def _do_set_power(self,power):
        '''
        Set output power of device

        Input:
            power (float) : output power in dBm

        Output:
            None
        '''
        logging.debug(__name__ + ' : setting power to %s dBm' % power)

        if self.get_pulm() == False and power > self.get_max_cw_pwr():
            logging.warning(__name__ + ' : power exceeds max cw power; power not set. ')
            raise ValueError('power exceeds max cw power. The pulse modulation is off')
            
        else:
            self._visainstrument.write('SOUR:POW %e' % power)

    def _do_set_max_cw_pwr(self, pwr):
        self._max_cw_pwr = pwr
        if self.get_power() > pwr and self.get_pulm() == 'off' and self.get_status() == 'on':  
            self.set_status('off')
            logging.warning(__name__ + ' : power exceeds max cw power; RF off')
            raise ValueError('power exceeds max cw power')

        return

    def _do_get_max_cw_pwr(self):
        return self._max_cw_pwr

    def do_get_status(self):
        '''
        Get status from instrument

        Input:
            None

        Output:
            status (string) : 'on or 'off'
        '''
        logging.debug(__name__ + ' : reading status from instrument')
        stat = self._visainstrument.ask(':OUTP:STAT?')

        if int(stat) == 1:
            return 'on'
        elif int(stat) == 0:
            return 'off'
        else:
            raise ValueError('Output status not specified : %s' % stat)

    def do_set_status(self, status):
        '''
        Set status of instrument

        Input:
            status (string) : 'on or 'off'

        Output:
            None
        '''
        logging.debug(__name__ + ' : setting status to "%s"' % status)
        if status.upper() in ('ON', 'OFF'):
            status = status.upper()
        else:
            raise ValueError('set_status(): can only set on or off')
        self._visainstrument.write(':OUTP:STAT %s' % status)

    # shortcuts
    def off(self):
        '''
        Set status to 'off'

        Input:
            None

        Output:
            None
        '''
        self.set_status('off')

    def on(self):
        '''
        Set status to 'on'

        Input:
            None

        Output:
            None
        '''
        self.set_status('on')

    def _do_set_phase(self, poffset):
        self._phase_offset = poffset
        self._visainstrument.write('SOUR:PHAS %sDEG' % poffset)

    def _do_get_phase(self):
        self._phase_offset = self._visainstrument.ask('SOUR:PHAS?')
        return self._phase_offset

    def do_set_pulm(self, state):
        if (state.upper() == 'ON'):
            state_s = 'ON'
        elif (state.upper() == 'OFF'):
            state_s = 'OFF'
        else:
            logging.error(__name__ + ' : Unable to set pulsed mode to %s,\
                                         expected "ON" or "OFF"' % state)

        self._visainstrument.write(':PULM:SOUR EXT')
        self._visainstrument.write(':SOUR:PULM:STAT %s' % state_s)

    def do_get_pulm(self):
        return self._visainstrument.ask(':SOUR:PULM:STAT?') == '1'

    def _do_get_iq(self):
        '''
        Get IQ modulation status from instrument
        Input:
            None
        Output:
            iq (string) : 'on' or 'off'
        '''
        logging.debug(__name__ + ' : reading IQ modulation status from instrument')
        stat = self._visainstrument.ask('IQ:STAT?')

        if stat == '1':
            return 'on'
        elif stat == '0':
            return 'off'
        else:
            raise ValueError('IQ modulation status not specified : %s' % stat)

    def _do_set_iq(self,iq):
        '''
        Switch external IQ modulation
        Input:
            iq (string) : 'on' or 'off'
        Output:
            None
        '''
        logging.debug(__name__ + ' : setting external IQ modulation to "%s"' % iq)
        if iq.upper() in ('ON', 'OFF'):
            iq = iq.upper()
        else:
            raise ValueError('set_iq(): can only set on or off')
        self._visainstrument.write('IQ:SOUR ANAL')
        self._visainstrument.write('IQ:STAT %s'%iq)
    # def do_set_pulsemod_source(self, source):
    #     self._visainstrument.write('SOUR:PULM:SOUR %s' % source)

    # def do_get_pulsemod_source(self):
    #     return self._visainstrument.ask('SOUR:PULM:SOUR?')


    def get_errors(self):
        '''
        This function is directly copied from the SMB100 driver.
        Get all entries in the error queue and then delete them.

        Input:
            None

        Output:
            errors (string) : 0 No error, i.e the error queue is empty.
                              Positive error numbers denote device-specific errors.
                              Negative error numbers denote error messages defined by SCPI
        '''
        logging.debug(__name__ + ' : reading errors from instrument')
        stat = self._visainstrument.ask('SYSTem:ERRor:ALL?')
        return stat

    def get_error_queue_length(self):
        '''
        This function is directly copied from the SMB100 driver.
        Get all entries in the error queue and then delete them.

        Input:
            None

        Output:
            errors (string) : 0 No error, i.e the error queue is empty.
                              Positive error numbers denote device-specific errors.
                              Negative error numbers denote error messages defined by SCPI
        '''
        logging.debug(__name__ + ' : reading errors from instrument')
        count = self._visainstrument.ask('SYSTem:ERRor:COUNt?')
        return int(count)
