# from instrument import Instrument
import types
import logging
import numpy as np
import socket

'''SK 2016

TDL 
1. When sending commands too fast after each other timeouts occur?
'''

class toptica_DLpro:


    def __init__(self,name,address):
        self._address = address
        self.name=name
        #self._visainstrument = visa.instrument(self._address, timeout=300)
        try: 
            self._sock.close()
        except:
            pass


        # should be moved to separate method
        # print socket.getdefaulttimeout()
        socket.setdefaulttimeout(2.5)
        # print socket.getdefaulttimeout()

        self._port = 1998
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print 'connecting to socket!'
        print self._sock.connect((self._address, self._port))


    def get_sock(self):
        return self._sock


    def Get_Alarm_State(self):
        """
        returns True if Cryostation is in Alarm state
        """        
        cmd = '03GAS'
        response = self._send_receive(cmd)
        return response == 'T'

    def _send_recv(self,cmd):
        self._sock.sendall(cmd)
        
        out = ''
        o = ''
        while "\n> " not in out:
            o = self._sock.recv(1000)
            # print 'o: ' + o
            out += o
        print 'Data receive loop ended, returning to base'
        return out



    # def _send_receive(self,cmd):
    #     self._sock.sendall(cmd)
    #     return self._sock.recv(int(self._sock.recv(2)))

    def remove(self):
        self._sock.close()
        print 'removing'
        # Instrument.remove(self)

    def reload(self):
        self._sock.close()
        print 'reloading'
        self._port = 1998
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print self._sock.connect((self._address, self._port))

    def get_SN(self):
        cmd         = "(param-ref 'serial-number)\n"
        response    = self._send_recv(cmd)
        #could also return, but print is more beautiful for elegance
        print response


    def laser_on(self):
        if '#t' in self._send_recv('(param-ref \'laser1:dl:cc:enabled)\n'):
            return 'laser already on'
        else:
            self._send_recv('(param-set! \'laser1:dl:cc:enabled #t)\n')
            self._send_recv('(param-ref \'laser1:dl:cc:enabled)\n')

        if '#t' in self._send_recv('(param-ref \'laser1:dl:cc:emission)\n'):
            return 'All conditions met! Succesfully emitting'
        else: 
            'Emission unsuccesful, check the following or refer to toptica DLpro manual:'
            '1. Interlock closed'
            '2. Front panel switch'
            '3. Laser emission push button on the front panel not pressed'
            '4. Laser emission is disabled by software'

    def laser_off(self):
        if '#f' in self._send_recv('(param-ref \'laser1:dl:cc:enabled)\n'):
            return 'laser already off'
        else:
            self._send_recv('(param-set! \'laser1:dl:cc:enabled #f)\n')
            self._send_recv('(param-ref \'laser1:dl:cc:enabled)\n')



    def get_current(self):
        #text display?
        self._send_recv('(param-disp \'laser1:dl:cc:current-act)\n')
        #only value return? 
        self._send_recv('(param-ref \'laser1:dl:cc:current-act)\n')
        # Just the difference between ref and disp is extra text. Disp has return value 0 if correct

    def set_current(self,current):
        '''(REAL parameter, read-write)
        Parameter to set the desired laser diode current in mA.
        If laser1:dl:cc:feedforward-enabled is #t, laser1:dl:cc:current-set is determined as follows:
        laser1:dl:cc:current-set = laser1:dl:cc:current-offset + (laser1:dl:cc:feedforward-
        factor * (laser1:dl:pc:voltage-set - 70.3 V)
        This parameter setting affects the laser1:dl:cc:current-offset value.'''

        self._send_recv('(param-set! \'laser1:dl:cc:current-set ' + str(current) +')\n')
        print 'current actual: ' + str(self.get_current)

    #piezo under construction
    # def get_piezo_voltage(self):
    #     self._send_receive('(param')

    # def set_piezo_voltage(self,voltage):
    #     self._send_receive('(param-set! \'laser1:scope:channel1:signal 50)\\n')

    def play_melody(self):
        cmd = '(exec \'buzzer:play "A A A A A E E H E H E AAAA")\n'
        self._send_recv(cmd)

    def laser_info(self):
        self._send_recv('(param-disp \'laser1)\n')
  
    def normal_sum(self):
        self._send_recv('(+ 3 3 5)\n')

    def reset_IP(self):
        cmd = '(exec \'net-conf:set-ip "192.168.1.1" "255.255.255.0")\n'
        self._send_recv(cmd)



if __name__ == '__main__':
    red = toptica_DLpro(name = 'red',
    address = '192.168.0.56')
    print 'Laser startup statement:\n' + red._send_recv('')

#TCPIP0::192.168.0.56::inst0::INSTR


# class toptica_DLpro(Instrument):
#     '''
#     SK ~ 2016
#     Python class to control toptica_DLCpro
#     Alternatively a GUI provided by Toptica can be used

#     Usage:
#     Initialize with

#     <name> = instruments.create('name', 'toptica_DL_laser', address='<GPIB address>',
#         reset=<bool>, numpoints=<int>)

#     TODO:
#     1) Get/Set I
#     2) Get/Set V
#      '''

 
#     def __init__(self, name, address, reset=False):
#         '''
#         Initializes the toptica_DL_laser.

#         Input:
#             name (string)    : name of the instrument
#             address (string) : GPIB address
#             reset (bool)     : resets to default values, default=false

#         Output:
#             None
#         '''
#         Instrument.__init__(self, name)

#         self._address = address
#         self._visainstrument = visa.instrument(self._address, timeout=300)

#         # Add functions
#         self.add_function('clear_visa')
#         self.add_function('get_I')
#         self.add_function('reset')
#         self.add_function('reset_sweep')
#         self.add_function('get_all')
#         self.add_function('get_errors')
#         self.add_function('get_error_queue_length')
#         print '####################################'
#         print 'Hello!! The toptica_DLpro is created'
#         print '####################################'



#     # Functions

#     # Clears visa object
#     def clear_visa(self):
#         self._visainstrument.clear()
#         for i in range(5):
#             try:
#                 self._visainstrument.read()
#             except(visa.VisaIOError):
#                 #print 'reset complete'
#                 break

#     # Gets laser current
#     def get_I(self):
#         self._visainstrument.ask('laser1:amp:cc:current-act')
        

#      # Functions
#     def reset(self):
#         '''
#         Resets the instrument to default values

#         Input:
#             None

#         Output:
#             None
#         '''
#         logging.info(__name__ + ' : Resetting instrument')
#         self._visainstrument.write('*RST')
#         self.get_all()

#     def get_all(self):m
#         '''
#         Reads all implemented parameters from the instrument,
#         and updates the wrapper.

#         Input:
#             None

#         Output:
#             None
#         '''
#         logging.info(__name__ + ' : reading all settings from instrument')
#         self.get_frequency()
#         self.get_power()
#         self.get_status()

#     def get_error(self):
#         pass

#     def get_error_queue_length(self):
#         pass

#     def reset_sweep(self):
#         pass

