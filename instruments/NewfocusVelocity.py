from instrument import Instrument
import visa
import types
import logging
import numpy
import time

class NewfocusVelocity(Instrument):
    '''
    This is the python driver for the Newfocus Velocity 6300

    Usage:
    Initialize with
    <name> = instruments.create('name', 'NewfocusVelocity', address='<GPIB address>')
    '''

    def __init__(self, name, address, reset=False):
        '''
        Initializes the Newfocus Laser.

        Input:
            name (string)    : name of the instrument
            address (string) : GPIB address

        Output:
            None
        '''
        logging.info(__name__ + ' : Initializing instrument')
        Instrument.__init__(self, name, tags=['physical'])

        self._address = address
        rm = visa.ResourceManager()
        self._visainstrument = rm.open_resource(self._address)

        self.add_parameter('wavelength',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='nm',
                           minval=632.5,maxval=639)

        self.add_parameter('diode_temperature',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='C',
                           minval=15,maxval=30)
        self.add_parameter('diode_current',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='mA',
                           minval=0,maxval=70)
        self.add_parameter('piezo_voltage',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='V',
                           minval=0,maxval=100)
        self.add_parameter('power_level',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='mW',
                           minval=0,maxval=10)

        self.add_function('set_ready_mode')

        self.add_function('get_output')

        self.add_function('set_output')

        self.add_function('set_wavelength_input')

        self.add_function('set_constant_power_mode')


    def do_get_diode_temperature(self):
        logging.debug(__name__ + ' : reading diode temperature from instrument')
        return float(self._visainstrument.ask(':TEMP?'))

    def do_set_diode_temperature(self, temperature):
        logging.debug(__name__ + ' : setting diode temperature to %s C' % temperature)
        self._visainstrument.write(':TEMP %e' % temperature)

    def do_get_diode_current(self):
        logging.debug(__name__ + ' : reading diode current from instrument')
        return float(self._visainstrument.ask(':CURR?'))

    def do_set_diode_current(self, current):
        logging.debug(__name__ + ' : setting diode current to %s mA' % current)
        self._visainstrument.write(':CURR %e' % current)

    def do_get_piezo_voltage(self):
        logging.debug(__name__ + ' : reading piezo voltage from instrument')
        return float(self._visainstrument.ask(':VOLT?'))

    def do_set_piezo_voltage(self,voltage):
        logging.debug(__name__ + ' : setting piezo voltage to %s V' % voltage)
        self._visainstrument.write(':VOLT %e' % voltage)

    def do_get_wavelength(self):
        logging.debug(__name__ + ' : reading wavelength from instrument')
        return float(self._visainstrument.ask(':WAVE?'))

    def do_set_wavelength(self, wavelength):
        logging.debug(__name__ + ' : setting wavelength to %s nm' % wavelength)
        self._visainstrument.write(':WAVE %e' % wavelength)
        while self._visainstrument.ask('*OPC?') != '1':
            time.sleep(0.1)
        self._visainstrument.write(':OUTP:TRAC OFF')

    def do_set_power_level(self,power):
        logging.debug(__name__ + ' : setting power to %s mW' % power)
        self._visainstrument.write(':POW %e' % power)

    def do_get_power_level(self):
        logging.debug(__name__ + ' : reading power level from instrument')
        return float(self._visainstrument.ask(':SENS:POW:FRON ?'))

    def set_ready_mode(self):
        logging.debug(__name__ + ' : setting device to ready mode')
        self._visainstrument.write(':OUTP:TRAC OFF')

    def get_output(self):
        logging.debug(__name__ + ' : reading status from instrument')
        stat = self._visainstrument.ask(':OUTP ?')

        if stat == '1':
            return 'on'
        elif stat == '0':
            return 'off'
        else:
            raise ValueError('Output status not specified : %s' % stat)

    def set_output(self,status):
        logging.debug(__name__ + ' : setting output to "%s"' % status)
        if status.upper() in ('ON', 'OFF'):
            status = status.upper()
        else:
            raise ValueError('set_output(): can only set on or off')
        self._visainstrument.write(':OUTP %s' % status)

    def set_wavelength_input(self,status):
        logging.debug(__name__ + ' : setting wavelength input mode to "%s"' % status)
        if status.upper() in ('ON', 'OFF'):
            status = status.upper()
        else:
            raise ValueError('set_wavelength_input(): can only set on or off')
        self._visainstrument.write(':SYST:WINP %s' % status)

    def set_constant_power_mode(self,status):
        logging.debug(__name__ + ' : setting constant power mode to "%s"' % status)
        if status.upper() in ('ON', 'OFF'):
            status = status.upper()
        else:
            raise ValueError('set_constant_power_mode(): can only set on or off')
        self._visainstrument.write(':CPOW %s' % status)

