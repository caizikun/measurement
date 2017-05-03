from instrument import Instrument
import visa
#
# These functions provide access to many of the Maestro's capabilities using the
# Pololu serial protocol. Adapted code taken from 
# Steven Jacobs -- Aug 2013
# https://github.com/FRC4564/Maestro/

# When connected via USB, the Maestro creates two virtual serial ports.
# For example COM8 for commands and COM9 for communications.
# Be sure the Maestro is configured for "USB Dual Port" serial mode.
# "USB Chained Mode" may work as well, but hasn't been tested.
#
# The target position is entered in units of quarter-microsecond, so 
# center position is 4*1500 = 6000

class MaestroServoController(Instrument):


    def __init__(self, name, address=0, reset=False):
        Instrument.__init__(self, name)

        self._address = address
        rm = visa.ResourceManager()
        self._visainstrument = rm.open_resource(self._address,
                       baud_rate=19200, data_bits=8, stop_bits=visa.constants.StopBits.one,
                       parity=visa.constants.Parity.none, write_termination='',read_termination = '')

        #self._ser = serial.Serial(address,19200, timeout = 3)
        self.add_function('Set_Range')
        self.add_function('Get_Min')
        self.add_function('Get_Max')
        self.add_function('Set_Position')
#        self.add_function('Get_Position')
        self.add_function('Set_Speed')
        self.add_function('Set_Acceleration')
        self.add_function('Close')

        # Command lead-in and device 12 are sent for each Pololu serial commands.
        self.PololuCmd = chr(0xaa) + chr(0xc)
        # Servo minimum and maximum targets can be restricted to protect components.
        self.Mins = [0] * 24
        self.Maxs = [0] * 24

    def Set_Range(self, chan, min, max):
        self.Mins[chan] = min
        self.Maxs[chan] = max

    # Return Minimum channel range value
    def Get_Min(self, chan):
        return self.Mins[chan]

    # Return Minimum channel range value
    def Get_Max(self, chan):
        return self.Maxs[chan]

    def Set_Position(self,chan,speed,position):
         # if Min is defined and Target is below, force to Min
        if self.Mins[chan] > 0 and position < self.Mins[chan]:
            position = self.Mins[chan]
        # if Max is defined and Target is above, force to Max
        if self.Maxs[chan] > 0 and position > self.Maxs[chan]:
            position = self.Maxs[chan]
        #    
        lsb = position & 0x7f #7 bits for least significant byte
        msb = (position >> 7) & 0x7f #shift 7 and take next 7 bits for msb
        # Send Pololu intro, device number, command, channel, and position lsb/msb
        cmd = self.PololuCmd + chr(0x04) + chr(chan) + chr(lsb) + chr(msb)
        self._visainstrument.write_raw(cmd)

#    #does not work with either pyserial or pyvisa...
#    def Get_Position(self,channel):
#        cmd = self.PololuCmd + chr(0x10) + chr(channel)
#        self._visainstrument.write_raw(cmd)
#        answer = self._visainstrument.read_raw()
#        lsb = ord(answer[0])
#        msb = ord(answer[1])
#        return (msb << 8) + lsb

    def Set_Speed(self, chan, speed):
        lsb = speed & 0x7f #7 bits for least significant byte
        msb = (speed >> 7) & 0x7f #shift 7 and take next 7 bits for msb
        # Send Pololu intro, device number, command, channel, speed lsb, speed msb
        cmd = self.PololuCmd + chr(0x07) + chr(chan) + chr(lsb) + chr(msb)
        self._visainstrument.write_raw(cmd)


    def Set_Acceleration(self, chan, accel):
        lsb = accel & 0x7f #7 bits for least significant byte
        msb = (accel >> 7) & 0x7f #shift 7 and take next 7 bits for msb
        # Send Pololu intro, device number, command, channel, accel lsb, accel msb
        cmd = self.PololuCmd + chr(0x09) + chr(chan) + chr(lsb) + chr(msb)
        self._visainstrument.write_raw(cmd)

    def Close(self):
        self._visainstrument.close()

    def reload(self):
        self.Close()
        Intrument.reload(self)
        
    def remove(self):
        self.Close()
        Intrument.remove(self)
