"""
Driver for remote controlable powerplugs by energie.
http://energenie.com/item.aspx?id=7415 /// One example part number is EG-PMS2

NK 2017
"""

from instrument import Instrument
import numpy as np
import qt
import types
from lib import config
import logging

class remote_powersocket(Instrument):
    """
    The socket has to got to be recognized by the energenie software (name: energenie power manager) with a specific name.
    """

    __init__(name,socket_name,**kws):
        logging.info(__name__ + ' : Initializing remotely controllable powerplug')
        Instrument.__init__(self, name)

        self.add_parameter('status', type=types.BooleanType,
            flags=Instrument.FLAG_GETSET,
            channels=(1, 2, 3 ,4), channel_prefix='socket%d_',val=False)


        self.add_function('turn_socket_on')
        self.add_function('turn_socket_off')
        self.add_function('get_all')

        # override from config       
        cfg_fn = os.path.join(qt.config['ins_cfg_path'], name+'.cfg')

        if not os.path.exists(cfg_fn):
            _f = open(cfg_fn, 'w')
            _f.write('')
            _f.close()

        self.set_socket_name(socket_name)
        self._ins_cfg = config.Config(cfg_fn)     
        self.load_cfg()
        self.save_cfg()


    def load_cfg(self):
        params_from_cfg = self._ins_cfg.get_all()

        for p in params_from_cfg:
            val = self._ins_cfg.get(p)
            if type(val) == unicode:
                val = str(val)
            
            try:
                self.set(p, value=val)
            except:
                pass

    def save_cfg(self):
        parlist = self.get_parameters()
        for param in parlist:
            value = self.get(param)
            self._ins_cfg[param] = value

    def get_socket_status(self,channel_name):
        return elf.get("socket%d_status",(self.get_outlet_number(channel_name)))

    def turn_socket_on(self,channel_name):
        Call([r"C:/program files/power manager/pm.exe","-on","-"+self.get_socket_name(),"-Socket"+str(self.get_outlet_number(channel_name))])
        self.set("socket%d_status",(self.get_outlet_number(channel_name)),True)
    def turn_socket_off(self,channel_name):
        Call([r"C:/program files/power manager/pm.exe","-off","-"+self.get_socket_name(),"-Socket"+str(self.get_outlet_number(channel_name))])
        self.set("socket%d_status",(self.get_outlet_number(channel_name)),False)
