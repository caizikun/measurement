import visa
from instrument import Instrument
from monitor_instrument import MonitorInstrument
import types
import qt
import time
import numpy as np
import os
import urllib
import qt

class monitor_montana(MonitorInstrument):
    '''This is a child class of the monitor instrument. 
	It monitors the temperature and alarm state of the Montana Cryostation'''
	
    def __init__(self, name, montana_ins_name='montana_cryostation', mailer='gmailer'):
		
        MonitorInstrument.__init__(self, name)
		
        self._montana = qt.instruments[montana_ins_name]
        self._mailer = qt.instruments[mailer]
                
        self.add_parameter('temperature',
                type=types.FloatType,
                flags=Instrument.FLAG_GET,
                units='K')

        self.add_parameter('alarm_state',
                type = types.BooleanType,
                flags=Instrument.FLAG_GET,)

        self.add_parameter('ignore_alarm_state',
                type = types.BooleanType,
                flags=Instrument.FLAG_GETSET,)

        self.add_parameter('max_temperature',
                type=types.FloatType,
                flags=Instrument.FLAG_GETSET,
                units='K')

        self.add_parameter('recording',
                flags=Instrument.FLAG_GETSET,
                type=types.BooleanType)

        self.add_function('restart_recording')

        self._max_temperature = 300.
        self._ignore_alarm_state = False

        self._recording = False
        self.set_recording(True)

		#override from config:
        self._parlist.extend(['max_temperature', 'ignore_alarm_state'])
        self.load_cfg()
        self.save_cfg()

    def restart_recording(self):
        self.set_recording(False)
        self.set_recording(True)
        return

    def do_set_recording(self, val):
        if not self._recording and val:
            self._recording = val
            self._T0 = time.time()
            self._data = qt.Data(name=self.get_name())
            self._data.add_coordinate('time')
            self._data.add_value('Platform_Temperature')

            self._data.create_file()
            
            self._plt = qt.Plot2D(self._data, 'ro', name=self.get_name(), 
                    coorddim=0, valdim=1, clear=True)
            self._plt.set_xlabel('time (hours)')
            self._plt.set_ylabel('Platform Temperature (K)')
        
        elif self._recording and not val:
            self._recording = val
            self._data.close_file()

    def do_get_recording(self):
        return self._recording

    def do_get_max_temperature(self):
        return self._max_temperature

    def do_set_max_temperature(self, val):
        self._max_temperature = val
    
    def do_get_temperature(self):
        return self._montana.Get_Platform_Temperature()

    def do_get_alarm_state(self):
        return self._montana.Get_Alarm_State()

    def do_get_ignore_alarm_state(self):
        return self._ignore_alarm_state

    def do_set_ignore_alarm_state(self, val):
        self._ignore_alarm_state = val
        		
    def _update(self):
        if not MonitorInstrument._update(self):
            return False

        temp = self.get_temperature()
        alarm = self.get_alarm_state() 
        t_num = time.time() 
        t_str = time.asctime()
        print('current time: %s'%t_str)
        print 'current alarm state: ', alarm
        print('current platform temperature:')
        print'{:.2f} K'.format(temp)

        if self.get_recording():
            self._data.add_data_point((t_num-self._T0)/3600., temp)


        if (temp > self.get_max_temperature()) or (alarm and not(self.get_ignore_alarm_state())):
            subject= 'Warning from ' + self.get_name()
            message = 'Warning from ' + self.get_name() +': \n'+\
                      'current Platform Temperature Reading:\n' + \
                      ' {:.2f} \n'.format(temp) + \
                      'current alarm state: ' + str(alarm) + '.\n' + \
                      'Please help me!!!\n xxx'
            #recipients  = ['h.bernien@tudelft.nl', 'M.S.Blok@tudelft.nl', 'julia.cramer@gmail.com','t.h.taminiau@tudelft.nl', 'N.Kalb@tudelft.nl']
            recipients  = ['B.J.Hensen@tudelft.nl', 'h.bernien@tudelft.nl', 'a.a.reiserer@tudelft.nl','A.E.Dreau@tudelft.nl']
            print message
            if self.get_send_email():
                    if self._mailer.send_email(recipients,subject,message):
						print 'Warning email message sent'					

        return True

