# Created by Bas Hensen, 2014
from instrument import Instrument
from lib import config
import logging
import types
import qt
import d2xx
import os

class RF_Multiplexer(Instrument):

    def __init__(self, name, serial='UM245R', reset=False):
        """
        Creates an interface to Raymond's RF Multiplexer, allowing each RF relais to be switched
        on or off. The manual overide switch should be in the down position, thereby turining the 
        LED off. The LED then indicates if any of the relais are switched on. 
        Note that 8 bits can be set, but currently only relays 1-5 are connected.

        Requires pyusb package (http://bleyer.org/pyusb/)

        Arguments:
        - address corresponds to the Device description.
        """
        Instrument.__init__(self, name)


        self._serial = serial

        self.add_parameter('state', 
                           type=types.IntType,
                           flags = Instrument.FLAG_GETSET,
                           minval=0,maxval=255)

        self.add_function('set_state_bitstring')
        self.add_function('get_state_bitstring')
        self.add_function('turn_on_relay')
        self.add_function('turn_off_relay')
        self.add_function('toggle_relay')
        self.add_function('get_dev')

        dev_list_len = d2xx.createDeviceInfoList()
        dev_id=-1
        for i in range(dev_list_len):
            dev_info = d2xx.getDeviceInfoDetail(i)
            if dev_info['serial']==self._serial:
                dev_id = i
                break
        if dev_id == -1:
            error_str = 'Device address serial {} not found in device list'.format(self._serial)
            logging.error(error_str)
            raise Exception(error_str)

        self._dev = d2xx.open(dev_id)
        self._dev.setBitMode(0xFF,1) #BitBangMode!

        self._state = 0

 # override from config       
        cfg_fn = os.path.abspath(
                os.path.join(qt.config['ins_cfg_path'], name+'.cfg'))
        if not os.path.exists(cfg_fn):
            _f = open(cfg_fn, 'w')
            _f.write('')
            _f.close()

        self.ins_cfg = config.Config(cfg_fn)
        self.load_cfg()
        self.save_cfg()
        
    def load_cfg(self):
        params_from_cfg = self.ins_cfg.get_all()
        for p in params_from_cfg:
                self.set(p, value=self.ins_cfg.get(p))

    def save_cfg(self):
        for param in self.get_parameter_names():
            value = self.get(param)
            self.ins_cfg[param] = value


    def get_dev(self):
        return self._dev

    def do_get_state(self):
        return self._state

    def do_set_state(self,val):
        self._state = val
        return self._dev.write(chr(val))

    def get_state_bitstring(self):
        """
        Gets the current state of the relays, and prints the result
        """
        st='{:b}'.format(self._state)
        while len(st)<=7:
            st='0'+st
        print 'Relay status: [87654321] = ['+st+']'

    def set_state_bitstring(self,state):
        """
        Sets the state of the relays. Input relay state in string format of 8 bits containing the states,
        in the order [87654321].

        returns 1 on success.

        eg. to set the status of relay 1 and 3 to on and the others to off, 
        call Set_Relay_State('00000101').

        """
        st = int(state,2)
        if st>255:
            logging.warning(self.get_name()+': invalid relay state, must be 8 bits')
        return self.set_state(st)

    def turn_off_relay(self,relay_no):
        """
        Turns off a single relay identified by relay_no, where relay_no is 1-8
        """
        if not(self._check_relay_no(relay_no)): return False
        stnew = self.get_state() & (255-2**(relay_no-1))
        return self.set_state(stnew)

    def turn_on_relay(self,relay_no):
        """
        Turns on a single relay identified by relay_no, where relay_no is 1-8
        """
        if not(self._check_relay_no(relay_no)): return False
        stnew = self.get_state() | (2**(relay_no-1))
        return self.set_state(stnew)

    def toggle_relay(self,relay_no):
        """
        Toggles a single relay identified by relay_no, where relay_no is 1-8
        """
        if not(self._check_relay_no(relay_no)): return False
        stnew = self.get_state() ^ (2**(relay_no-1))
        return self.set_state(stnew)

    def _check_relay_no(self, relay_no):
        if relay_no<1 or relay_no>8 or type(relay_no)!=int:
            logging.warning(self.get_name()+': invalid relay number, must be integer 1<relay_no<8')
            return False
        return True

    def remove(self):
        self._dev.close()
        print 'removing'
        Instrument.remove(self)

    def reload(self):
        self._dev.close()
        print 'reloading'
        Instrument.reload(self)