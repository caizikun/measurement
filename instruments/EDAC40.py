from time import sleep, time
import numpy as np
from instrument import Instrument
import logging
import qt
import ctypes


class edac40_list_node(ctypes.Structure):
    _fields_ = [
        ('ip_address', ctypes.c_char*20),
        ('MAC_address', ctypes.c_char*20),
    ]
    def __init__(self):
        self.ip_address = (ctypes.c_char*20)('0')
        self.MAC_address = (ctypes.c_char*20)('0')
        
class value_array(ctypes.Structure):
    _fields_ = [
        ('value', ctypes.c_uint16*40),
    ]
    def __init__(self):
        self.value = (ctypes.c_uint16*40)('0')
        
class EDAC40(Instrument): 
    '''
    This is the driver for the EDAC40 ethernet connected 40-channel DAC module. 
    Initially used to drive an OKOtech Deformable mirror (Aug 2014 - Machiel Blok)

    Usage:
    Initialize with
    <name> = qt.instruments.create('name', 'EDAC40',MAC_address=<mac_adress>)
    MAC_address = str i.e. str(\x00\x04\xA3\x13\xDA\x94)
    
    status:
     1) create this driver!=> is never finished
    TODO:
    '''

    def __init__(self, name,MAC_address): #2
         # Initialize wrapper
        logging.info(__name__ + ' : Initializing instrument EDAC40')
        Instrument.__init__(self, name, tags=['physical'])

        # Load dll and open connection
        self._load_dll()
        sleep(0.01)
        self._edac40.edac40_init()

        #Get ip address
        self._ip = self.find_device(MAC_address)          
        self._c_ip=ctypes.create_string_buffer(self._ip)

        #Open device connection
        self._use_UDP = True
        self.open(self._c_ip,self._use_UDP)
        if self._socket<=0:
            print 'Error %d, raised while opening device. Device not opened' %self._socket
        else:    
            print 'Connected to EDAC40. Socket nr %d ; IP address: %s' % (self._socket,self._ip)

        # To add functions that are externally available
        self.add_function('close')
        self.add_function('set_single')
        self.add_function('set_all_pins')         
        self.add_function('set_all_to_constant')  
        self.add_function('restore_defaults') 
        self.add_function('find_device')
        self.add_function('set_timeout')
        
        # Configure device (TO DO: Load this from a file)
        # These settings are for EDAC40 with MAC address 00-04-A3-13-DA-94,
        # Depends on jumper settings and also might be device dependent?
        # single_pin_conversion_table[pin_nr]=set_single_chan_nr
        self.single_pin_conversion_table=np.arange(41)-1
        self.single_pin_conversion_table[2]=-42 # ground
        self.single_pin_conversion_table[1]=1   # pin 1 -> ch2 (= logical 1)
        self.single_pin_conversion_table[22]=20
        self.single_pin_conversion_table[21]=21

        # mult_pin_conversion_table[pin_nr] = set_mult_chan_nr 
        # Probably device dependent. pin 0 doesnt exist, pin 2 is ground
        # NOTE: very weird: according to manual this should contain numbers between 0 and 39. Instead I only get it working with an array twice as long, using only the even numbers between 0 and 79
        #                               #0-20
        self.mult_pin_conversion_table=[-42,14,-42,8,10,4,6,0,2,44,46,40,42,36,38,32,34,28,30,24,26,
        #                               21-40
                                        22,20,16,18,76,78,72,74,68,70,64,66,60,62,56,58,52,54,48,50]

    def _load_dll(self): 
        print __name__ +' : Loading edac40.dll'
        self._edac40 = ctypes.cdll.LoadLibrary('D:\measuring\measurement\hardware\EDAC40\edac40.dll')
        sleep(0.02)

    def find_device(self,MAC_address):
        c_MAC=ctypes.create_string_buffer(MAC_address)
        self._edac40.edac40_find_device.restype=ctypes.c_char_p

        ip = self._edac40.edac40_find_device(c_MAC)
        return ip

    def list_devices(self,max_device_num,discover_timeout,discover_attempts): 
        list_node=(edac40_list_node*max_device_num)()
        dev_num=self._edac40.edac40_list_devices(ctypes.byref(list_node),ctypes.c_int(max_device_num),ctypes.c_int(discover_timeout),ctypes.c_int(discover_attempts))
        
        print 'Found %d EDAC40 device(s)' %dev_num
        for i in np.arange(dev_num):
            print 'Device nr %d, ip_address: %s' %(dev_num,list_node[i].ip_address)
        return dev_num,list_node

    def open(self,ip_address,use_UDP):
        if use_UDP:
            #Use UDP Protocol (One-way communication to device)
            self._socket=self._edac40.edac40_open(self._c_ip,ctypes.c_int(0))
        else:
            #Use TCP Protocol (For each data packet that is sent to the device, a response from the device is recieved)
            self._socket=self._edac40.edac40_open(self._c_ip,ctypes.c_int(1))    
    
    def close(self):
        self._edac40.edac40_close(self._socket)

    def restore_defaults(self):
        self._edac40.edac40_restore_defaults(self._socket)    

    def set_timeout(self,timeout):
        self._edac40.edac40_set_timeout(self._socket,ctypes.c_long(timeout))    #in ms, default = 1000ms

    def set_single(self,command_code,channel,value):
        """
        Set property of a single channel.

        command_code:   Integer, 0-3
        channel:        Integer, 0-39
        Channel nr that is set 
        value:          Integer, 0-65535
        assigns a value to <command_code> of channel nr <channel>
        """
        ret=self._edac40.edac40_set(self._socket,ctypes.c_int(command_code),ctypes.c_int(channel),ctypes.c_uint16(value))

    def set_all_to_constant(self,command_code,value):
        """
        Set a property of all pins to single value.

        To calculate the final output (VOUT):
        DAC CODE = INPUT CODE * (GAIN + 1) + OFFSET - 2**15
        VOUT = 4 * VREF * ((DAC CODE / 2**16) - (GLOBAL OFFSET / 2**14))

        where VREF = 3.0V - voltage reference

        command_code:   Integer, 0-3
        Which property of the pin you set:
        0:  DAC value (INPUT CODE in above formula)
        1:  OFFSET
        2:  GAIN
        3:  GLOBAL OFFSET (for all pins)

        value:          Integer, 0-65535
        assigns one value to <command_code> for all pins
        """
        c_value=(ctypes.c_uint16)(value)    
        c_packet=ctypes.POINTER(ctypes.c_char)()

        self._edac40.edac40_prepare_packet_from_array.argtypes = [ctypes.c_uint16,ctypes.c_int,ctypes.POINTER(ctypes.POINTER(ctypes.c_char))]
        ret_val=self._edac40.edac40_prepare_packet_fill(c_value,ctypes.c_int(command_code),ctypes.byref(c_packet))
        if ret_val <0:
            print 'Error in preparing packet: %d', ret_val
        ret_val2=self._edac40.edac40_send_packet(self._socket,c_packet,ctypes.c_int(ret_val))
        if ret_val <0:
            print 'Error in sending packet: %d', ret_val2

    def set_all(self,command_code,values):
        """
        Set a property of all pins to a unique value.

        To calculate the final output (VOUT):
        DAC CODE = INPUT CODE * (GAIN + 1) + OFFSET - 2**15
        VOUT = 4 * VREF * ((DAC CODE / 2**16) - (GLOBAL OFFSET / 2**14))

        where VREF = 3.0V - voltage reference

        command_code:   Integer, 0-3
        Which property of the pin you set:
        0:  DAC value (INPUT CODE in above formula)
        1:  OFFSET
        2:  GAIN
        3:  GLOBAL OFFSET (for all pins)

        value:          [Integer]*80 , Integer between 0-65535
        assigns the value value[i] to <command_code> of pin nr [j] 
        Note: mapping between logical pin nr (i) and physical pin nr (j) is non-trivial and may be device dependent (?)
        """
        # TODO: find out why this length 80 array works (should be length 40 according to manual)
        c_values=(ctypes.c_uint16*80)(*values)    
        c_packet=ctypes.POINTER(ctypes.c_char)()
  

        self._edac40.edac40_prepare_packet_from_array.argtypes = [ctypes.c_uint16*80,ctypes.c_int,ctypes.POINTER(ctypes.POINTER(ctypes.c_char))]
        ret_val=self._edac40.edac40_prepare_packet_from_array(c_values,ctypes.c_int(command_code),ctypes.byref(c_packet))
        if ret_val <0:
            print 'Error in preparing packet: %d', ret_val
        ret_val2=self._edac40.edac40_send_packet(self._socket,c_packet,ctypes.c_int(ret_val))
        if ret_val <0:
            print 'Error in sending packet: %d', ret_val2    

    ##########################
    # More high level functions to convert logical channel to pin nr and accept pin nr as input.
    ##########################
    def convert_single_pin_to_chan(self,pin):
        chan=self.single_pin_conversion_table[pin]
        return chan
    def convert_mult_pin_to_chan(self,pin_vals):
        chan_vals=[-1]*80
        print len(self.mult_pin_conversion_table)
        for nr,val in enumerate(pin_vals):
            print 'nr',nr
            print 'val',val
            chan_vals[self.mult_pin_conversion_table[nr+1]]=val
            print 'log chan' , self.mult_pin_conversion_table[nr+1]
        return chan_vals
    def set_single_pin(self,command_code,pin,chan_values):
        """
        Set property of a single pin.
        To calculate the final output (VOUT):
        DAC CODE = INPUT CODE * (GAIN + 1) + OFFSET - 2**15
        VOUT = 4 * VREF * ((DAC CODE / 2**16) - (GLOBAL OFFSET / 2**14))

        where VREF = 3.0V - voltage reference

        command_code:   Integer, 0-3
        Which property of the pin you set:
        0:  DAC value (INPUT CODE in above formula)
        1:  OFFSET
        2:  GAIN
        3:  GLOBAL OFFSET (for all pins)
        
        Pin:        Integer, 1-40
        Pin nr 

        value:          Integer, 0-65535
        assigns a value to <command_code> of pin nr <channel>
        """
        channel=self.convert_single_pin_to_chan(pin)
        if channel<0:
            print 'Error: pin %d is defined as ground. ' % pin
        else:
            self.set_single(command_code,channel,value)
    def set_all_pins(self,command_code,pin_values):
        """
        Set a property of all pins to a unique value.

        To calculate the final output (VOUT):
        DAC CODE = INPUT CODE * (GAIN + 1) + OFFSET - 2**15
        VOUT = 4 * VREF * ((DAC CODE / 2**16) - (GLOBAL OFFSET / 2**14))

        where VREF = 3.0V - voltage reference

        command_code:   Integer, 0-3
        Which property of the pin you set:
        0:  DAC value (INPUT CODE in above formula)
        1:  OFFSET
        2:  GAIN
        3:  GLOBAL OFFSET (for all pins)

        pin_values:          [Integer]*40 , Integer between 0-65535
        assigns the value pin_value[i] to <command_code> of physical pin nr i+1 
        """
        chan_vals=self.convert_mult_pin_to_chan(pin_values)
        self.set_all(command_code,chan_vals)       