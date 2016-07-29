from instrument import Instrument
import visa
import types
import logging
import re
import math

class Millennia_Pro(Instrument):

    def __init__(self, name, address, reset=False):
        Instrument.__init__(self, name)

        self._address = address
        rm = visa.ResourceManager()
        self._visa = rm.open_resource(self._address,
                        baud_rate=9600, data_bits=8, stop_bits=visa.constants.StopBits.one,
                        parity=visa.constants.Parity.none, write_termination='\r\n',read_termination = '\r\n')

    def On(self):
        self._visa.write('ON')

    def Get_Warmup_State(self):
        return self._visa.ask('?WARMUP%')

    def Set_Shutter_Open(self):
        self._visa.write('SHUTTER:1')

    def Set_Shutter_Closed(self):
        self._visa.write('SHUTTER:0')

    def Get_Power(self):
        return self._visa.ask('?P')

    def Get_Shutter_State(self):
        return self._visa.ask('?SHUTTER')

