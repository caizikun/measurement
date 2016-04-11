
from instrument import Instrument
import types
import logging
import numpy as np
import socket
import time



class Toptica_DLpro(Instrument):
    '''SK 2016

    Driver for the toptica diode laser.
    Alternatively 'TOPAS DLC' GUI provided by Toptica can be used.

    Usage:
    Initialize with
    <name> = instruments.create('<name>', 'Toptica_DLpro',
        address='<TCP/IP address>')
    '''
    def __init__(self,name,address):

        '''
        Initializes the Toptica_DLpro, and communicates with the wrapper.

        Input:
            name (string)           : name of the instrument
            address (DEstring)        : TCP/IP address
     
        Output:
            Laser started! Welcome to:
            *smiley *heart* DLCpro firmware, version 1.3.1
            SN: DLC PRO_020295
            uptime: ###:##:##

            Decof Command Line
        '''

        logging.info('Initializing instrument DLpro')
        Instrument.__init__(self, name, tags=['physical'])
        self._address = address
        self.name=name

        try: 
            self._sock.close()
        except:
            pass

        # Essential functions
        self.add_function('Initialize')
        self.add_function('Turn_Laser_On')
        self.add_function('Turn_Laser_Off')
        self.add_function('Remove')
        self.add_function('Reload')
        self.add_function('Save')
        self.add_function('Load')
        
        # Informational functions, for additional functions refer to manual or use
        # _send_recv('(param-disp)') to receive all parameters
        self.add_function('Get_SN')
        self.add_function('Get_Sock')
        self.add_function('Laser_Info')
        self.add_function('Play_Melody')
        self.add_function('Reset_IP')
     
        # parameters
        self.add_parameter('current',
            flags=Instrument.FLAG_GETSET | Instrument.FLAG_GET_AFTER_SET,
            units='mA', minval=0.5, maxval=245, type=types.FloatType)

        self.add_parameter('piezo_voltage',
            flags=Instrument.FLAG_GETSET | Instrument.FLAG_GET_AFTER_SET,
            units='V', minval=-1, maxval=140, type=types.FloatType)
        
        self._current = 0
        self._piezo_voltage = 70

        self.Initialize()

# --------------------------------------
#           functions
# --------------------------------------

    def Initialize(self):
        """
        Connect to the Toptical DL Pro controler via TCP/IP
        Connecton port 1998
        Default IP: 192.168.0.56
        Default Gateway: 255.255.255.0
        """
        socket.setdefaulttimeout(1)

        self._port = 1998
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        logging.debug(__name__ + 'connecting to dlpro socket!')
        self._sock.connect((self._address, self._port))
        print 'Laser started! Welcome to:\n' + self._send_recv('')

    def Get_Sock(self):
        logging.debug(__name__ + 'returning socket')
        return self._sock

    def _send_recv(self,cmd):
        logging.debug(__name__ + 'retreiving output from DLCpro')
        
        self._sock.sendall(cmd)
        
        out = ''
        while "\n> " not in out:
            o = self._sock.recv(1000)
            out += o

        
        print 'readreturntest: ' + repr(out[:-3])
        return out[:-3]

    def Remove(self):

        logging.debug(__name__ + 'removing socket & instrument')
        self._sock.close()
        print 'removing'
        Instrument.remove(self)

    def Reload(self):

        logging.debug(__name__ + 'reloading socket & instrument')
        self._sock.close()
        print 'reloading'
        Instrument.reload(self)


    def Get_SN(self):

        logging.debug(__name__ + 'retreiving SN')
        return self._send_recv('(param-ref \'serial-number)\n')


    def Turn_Laser_On(self):

        logging.debug(__name__ + 'turning laser on')
        if '#t' in self._send_recv('(param-ref \'laser1:dl:cc:enabled)\n'):
            return 'laser already on'
        else:
            self._send_recv('(param-set! \'laser1:dl:cc:enabled #t)\n')
            print 'Laser on? ' + self._send_recv('(param-ref \'laser1:dl:cc:enabled)\n')

        if '#t' in self._send_recv('(param-ref \'laser1:dl:cc:emission)\n'):
            return 'All conditions met! Succesfully emitting'
        else: 
            print 'Emission unsuccesful, check the following or refer to toptica DLpro manual:'
            print '1. Interlock closed'
            print '2. Front panel switch'
            print '3. Laser emission push button on the front panel not pressed'
            print '4. Laser emission is disabled by software'

    def Turn_Laser_Off(self):

        logging.debug(__name__ + 'turning laser off')
        if '#f' in self._send_recv('(param-ref \'laser1:dl:cc:enabled)\n'):
            return 'laser already off'
        else:
            self._send_recv('(param-set! \'laser1:dl:cc:enabled #f)\n')
            print 'Laser on? ' + self._send_recv('(param-ref \'laser1:dl:cc:enabled)\n')



    def _do_get_current(self):

        logging.debug(__name__ + ' : reading current from DLpro laser1')
        self._current = float(self._send_recv('(param-ref \'laser1:dl:cc:current-act)\n'))
        return self._current
        # Just the difference between ref and disp is extra text. Disp has return value 0 if correct

    def _do_set_current(self,current):
        '''(REAL parameter, read-write)
        Parameter to set the desired laser diode current in mA.
        If laser1:dl:cc:feedforward-enabled is #t (by default it is), 
        laser1:dl:cc:current-set is determined as follows:
        laser1:dl:cc:current-set = laser1:dl:cc:current-offset + (laser1:dl:cc:feedforward-
        factor * (laser1:dl:pc:voltage-set - 70.3 V)
        This parameter setting affects the laser1:dl:cc:current-offset value.'''
        
        logging.debug(__name__ + ' : setting current in DLpro laser1')
        self._send_recv('(param-set! \'laser1:dl:cc:current-set ' + str(current) +')\n')
        
        #print 'current set to: ' + self._send_recv('(param-ref \'laser1:dl:cc:current-set)\n')
        #print 'current actual: ' 
        #self.get_current()


    def _do_get_piezo_voltage(self):

        logging.debug(__name__ + ' : reading piezo_voltage from DLpro laser1')
        cmd = "(param-ref 'laser1:dl:pc:voltage-act)\n"
        self._piezo_voltage = float(self._send_recv(cmd))
        return self._piezo_voltage
     


    def _do_set_piezo_voltage(self,voltage):
        
        logging.debug(__name__ + ' : setting piezo_voltage in DLpro laser1')
        self._send_recv("(param-set! 'laser1:dl:pc:voltage-set " + str(voltage) +")\n")

        # time.sleep(.5)
        # print 'piezo voltage set to: ' + self._send_recv("(param-ref 'laser1:dl:pc:voltage-set)\n")
        # print 'actual piezo voltage: ' 
        # self.get_piezo_voltage()


    def Play_Melody(self):
        cmd = '(exec \'buzzer:play "A A A A A E E H E H E AAAA")\n'
        print self._send_recv(cmd)


    def Laser_Info(self):
        cmd = "(param-disp 'laser1)\n"
        print self._send_recv(cmd)
  

    def Reset_IP(self):
        cmd = '(exec \'net-conf:set-ip "192.168.1.1" "255.255.255.0")\n'
        print self._send_recv(cmd)

    def Save(self):
        'Command to save laser parameters to the DLC pro flash memory.'
        cmd = "(exec 'laser1:save)\n"
        self._send_recv(cmd)

    def Load(self):
        'Command to load laser parameters from the DLC pro flash memory.'
        cmd = "(exec 'laser1:load)\n"
        self._send_recv(cmd)

#if __name__ == '__main__':
#    red = toptica_DLpro(name = 'red',
#    address = '192.168.0.56')
#    print 'Engaging laser, welcome!\n' + red._send_recv('')
# de __init...
#         # override from config       
#         cfg_fn = os.path.join(qt.config['ins_cfg_path'], name+'.cfg')

#         if not os.path.exists(cfg_fn):
#             _f = open(cfg_fn, 'w')
#             _f.write('')
#             _f.close()

#         self._ins_cfg = config.Config(cfg_fn)     
#         self.load_cfg()
#         self.save_cfg()

#     def get_all(self):
#         for n in self.get_parameter_names():
#             self.get(n)
        
    
#     def load_cfg(self):
#         params_from_cfg = self._ins_cfg.get_all()

#         for p in params_from_cfg:
#             val = self._ins_cfg.get(p)
#             if type(val) == unicode:
#                 val = str(val)
            
#             self.set(p, value=val)


#     def save_cfg(self):
#         parlist = self.get_parameters()
#         for param in parlist:
#             value = self.get(param)
#             self._ins_cfg[param] = value