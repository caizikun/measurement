# Created by Bas Hensen, 2014
from instrument import Instrument
import instrument_helper
import serial
import logging
import types
import qt

class Conrad_Relaycard(Instrument):

    _commands = {
    'NOP' :         0,
    'SETUP':        1,
    'GET_PORT':     2,
    'SET_PORT':     3,
    'GET_OPTION':   4,
    'SET_OPTION':   5,
    'SET_SINGLE':   6,
    'DEL_SINGLE':   7,
    'TOGGLE':       8,
    }

    def __init__(self, name, address, reset=False):
        Instrument.__init__(self, name)


        self._address = address
        self._ser = serial.Serial(address,19200,timeout = 2)
        ins_pars  = {'current_card_address'    :   {'type':types.IntType,'val':0,'flags':Instrument.FLAG_GETSET},
                    }
        instrument_helper.create_get_set(self,ins_pars)

        self.add_function('Initialize')
        self.add_function('Get_Relay_State')
        self.add_function('Get_Status')
        self.add_function('Set_Relay_State')
        self.add_function('Turn_On_Relay')
        self.add_function('Turn_Off_Relay')
        self.add_function('Toggle_Relay')

        self.Initialize()


    #def get_ser(self):
    #    return self._ser

    def Initialize(self):
        """
        Currently only clears the serial input buffer and sets the number of connected cards to 1.

        TO be implemented: discovery of connected cards, and automatic address assignment
        """
        self._card_count = 1
        self._clear_ser_in_buffer()

    def Get_Relay_State(self):
        """
        Gets the current state of the relays, and prints the result
        """
        cmd=self._commands['GET_PORT']
        self._send_command(cmd,0)
        self._ser_wait()
        r_cmd, r_data=self._get_answer()
        st='{:b}'.format(r_data)
        while len(st)<=7:
            st='0'+st
        return 'Relay status: [87654321] = ['+st+']'

    def Set_Relay_State(self,state):
        """
        Sets the state of the relays. Input relay state in string format of 8 bits containing the states,
        in the order [87654321].

        returns True on success.

        eg. to set the status of relay 1 and 3 to on and the others to off, 
        call Set_Relay_State('00000101').

        """
        cmd=self._commands['SET_PORT']
        st = int(state,2)
        if st>255:
            logging.warning(self.get_name()+': invalid relay state, must be 8 bits')
        self._send_command(cmd,st)
        self._ser_wait()
        r_cmd, r_data=self._get_answer()
        return (r_cmd==255-cmd)

    def Turn_On_Relay(self,relay_no):
        """
        Turns on a single relay identified by relay_no, where relay_no is 1-8
        """
        if not(self._check_relay_no(relay_no)): return False
        st = 2**(relay_no-1)
        cmd = self._commands['SET_SINGLE']
        self._send_command(cmd,st)
        self._ser_wait()
        r_cmd, r_data=self._get_answer()
        return (r_cmd==255-cmd)

    def Turn_Off_Relay(self,relay_no):
        """
        Turns off a single relay identified by relay_no, where relay_no is 1-8
        """
        if not(self._check_relay_no(relay_no)): return False
        st = 2**(relay_no-1)
        cmd = self._commands['DEL_SINGLE']
        self._send_command(cmd,st)
        self._ser_wait()
        r_cmd, r_data=self._get_answer()
        return (r_cmd==255-cmd)

    def Toggle_Relay(self,relay_no):
        """
        Toggles a single relay identified by relay_no, where relay_no is 1-8
        """
        if not(self._check_relay_no(relay_no)): return False
        st = 2**(relay_no-1)
        cmd = self._commands['TOGGLE']
        self._send_command(cmd,st)
        self._ser_wait()
        r_cmd, r_data=self._get_answer()
        return (r_cmd==255-cmd)

    def _check_relay_no(self, relay_no):
        if relay_no<1 or relay_no>8 or type(relay_no)!=int:
            logging.warning(self.get_name()+': invalid relay number, must be integer 1<relay_no<8')
            return False
        return True

    def Get_Status(self):
        """
        Prints connection status of Relay board
        """
        cmd=self._commands['NOP']
        self._send_command(cmd,0)
        self._ser_wait()
        r_cmd, r_data=self._get_answer(check_error=False)
        if r_cmd == 255:
            return 'Status OK'
        else:
            print 'device returned:', r_cmd, r_data
            return 'Status not OK'

    def _send_command(self,cmd,data):
        adr= self._current_card_address
        checksum=cmd^adr^data
        self._ser.write(chr(cmd)+chr(adr)+chr(data)+chr(checksum))

    def _get_answer(self, check_error=True):
        answer = self._ser.read(4)
        self._clear_ser_in_buffer()
        r_cmd, r_adr, r_data, r_checksum = ord(answer[0]), ord(answer[1]), ord(answer[2]), ord(answer[3])
        
        if r_cmd ^ r_adr^r_data != r_checksum:
            logging.error(self.get_name()+': Return data failed checksum, '+str(checksum))
            return -1, -1
        if check_error:
            if r_cmd == 255:
                logging.warning(self.get_name()+': Device returned error state')
            if self._current_card_address!= 0 and r_adr != self._current_card_address:
                logging.warning(self.get_name()+': Returned card adress, ' + str(r_adr) + \
                                                ' is not current card adress, '+ str(self._current_card_address))
        return r_cmd, r_data

    def _ser_wait(self):
        qt.msleep((self._card_count*8.*10.)/1000.)

    def _clear_ser_in_buffer(self):
        self._ser.read(self._ser.inWaiting())

    def remove(self):
        self._ser.close()
        print 'removing'
        Instrument.remove(self)

    def reload(self):
        self._ser.close()
        print 'reloading'
        Instrument.reload(self)