# Created by Bas Hensen, 2014
from instrument import Instrument
import logging
import socket

class Montana_Cryostation(Instrument):


    def __init__(self, name, ip_address, port, reset=False):
        Instrument.__init__(self, name)


        self._ip_address = ip_address
        self._port = port

        self.add_function('Initialize')
        self.add_function('Get_Alarm_State')
        self.add_function('Get_Platform_Temperature')
        self.add_function('Get_Platform_Stability')
        self.add_function('Get_Platform_Temperature_Setpoint')
        self.add_function('Get_Platform_Heater_Power')
        self.add_function('Get_Sample_Temperature')
        self.add_function('Get_Sample_Stability')
        self.add_function('Get_User_Temperature')
        self.add_function('Get_User_Stability')
        self.add_function('Get_PID_Values')
        self.add_function('Get_Magnet_State')
        self.add_function('Get_Magnet_Target_Field')
        self.add_function('Start_Cooldown')
        self.add_function('Start_Warmup')
        self.add_function('Start_Standby')
        self.add_function('Stop')
        self.add_function('Set_Temperature_Setpoint')
        self.add_function('Set_PID_Values')
        self.add_function('Reset_PID_default')
        self.add_function('Enable_Magnet')
        self.add_function('Set_Magnet_Target_Field')

        self.Initialize()


    def get_sock(self):
        return self._sock

    def Initialize(self):
        """
        Connect to the Cryostation 
        """
        try: 
            self._sock.close()
        except:
            pass
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((self._ip_address, self._port))

    def Get_Alarm_State(self):
        """
        returns True if Cryostation is in Alarm state
        """        
        cmd = '03GAS'
        response = self._send_receive(cmd)
        return response == 'T'

    def Get_Platform_Temperature(self):
        """
        in Kelvin
        """        
        cmd = '03GPT'
        response = self._send_receive(cmd)
        return float(response)

    def Get_Platform_Stability(self):
        """
        in Kelvin
        """        
        cmd = '03GPS'
        response = self._send_receive(cmd)
        return float(response)

    def Get_Platform_Temperature_Setpoint(self):
        """
        in Kelvin
        """        
        cmd = '04GTSP'
        response = self._send_receive(cmd)
        return float(response)

    def Get_Platform_Heater_Power(self):
        """
        in Watt
        """
        cmd = '04GPHP'
        response = self._send_receive(cmd)
        return float(response)

    def Get_Sample_Temperature(self):
        """
        in Kelvin
        """
        cmd = '03GST'
        response = self._send_receive(cmd)
        return float(response)

    def Get_Sample_Stability(self):
        """
        in Kelvin
        """
        cmd = '03GSS'
        response = self._send_receive(cmd)
        return float(response)

    def Get_User_Temperature(self):
        cmd = '03GUT'
        response = self._send_receive(cmd)
        return float(response)

    def Get_User_Stability(self):
        cmd = '03GUS'
        response = self._send_receive(cmd)
        return float(response)

    def Get_PID_Values(self):
        """
        Returns the (K,F,T) PID setting in units of (W/K, Hz, s)
        """
        cmd1 = '05GPIDK'
        response1 = self._send_receive(cmd1)
        cmd2 = '05GPIDF'
        response2 = self._send_receive(cmd2)
        cmd3 = '05GPIDT'
        response3 = self._send_receive(cmd3)
        return (float(response1),float(response2),float(response3))

    def Get_Magnet_State(self):
        cmd = '03GMS'
        response = self._send_receive(cmd)
        return response

    def Get_Magnet_Target_Field(self):
        """
        in Tesla
        """
        cmd = '04GMTF'
        response = self._send_receive(cmd)
        return float(response)

    def Start_Cooldown(self):
        cmd = '03SCD'
        response = self._send_receive(cmd)
        return response

    def Start_Warmup(self):
        cmd = '03SWU'
        response = self._send_receive(cmd)
        return response

    def Start_Standby(self):
        cmd = '03SSB'
        response = self._send_receive(cmd)
        return response

    def Stop(self):
        cmd = '03STP'
        response = self._send_receive(cmd)
        return response


    def Set_Temperature_Setpoint(self,val):
        """
        in Kelvin
        """
        cmd = '10STSP{:06.2f}'.format(val)
        response = self._send_receive(cmd)
        return response

    def Set_PID_Values(self,K,F,T):
        """
        Set the (K,F,T) PID setting in units of (W/K, Hz, s)
        """
        cmd1 = '12SPIDK{:07.3f}'.format(K)
        response1 = self._send_receive(cmd1)
        cmd2 = '12SPIDF{:07.3f}'.format(F)
        response2 = self._send_receive(cmd2)
        cmd3 = '12SPIDT{:07.3f}'.format(T)
        response3 = self._send_receive(cmd3)
        return (response1,response2,response3)

    def Reset_PID_default(self):
        cmd = '04RPID'
        response = self._send_receive(cmd)
        return response

    def Enable_Magnet(self):
        cmd = '03SME'
        response = self._send_receive(cmd)
        return response

    def Disable_Magnet(self):
        cmd = '03SMD'
        response = self._send_receive(cmd)
        return response

    def Set_Magnet_Target_Field(self,val):
        """
        in Tesla
        """
        cmd = '13SMTF{:+08.6f}'.format(val)
        response = self._send_receive(cmd)
        return response

    def _send_receive(self,cmd):
        self._sock.sendall(cmd)
        response_length = int(self._sock.recv(2))
        return self._sock.recv(response_length)

    def remove(self):
        self._sock.close()
        print 'removing'
        Instrument.remove(self)

    def reload(self):
        self._sock.close()
        print 'reloading'
        Instrument.reload(self)