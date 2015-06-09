import numpy as np
from instrument import Instrument
import logging
import qt
import ctypes
import os
from lib import config
import types
import comtypes.client as cc
from measurement.hardware.Multi_DM import Multi_DM_interface

#        - Multi_DM_interface: this is the module which contains the interface that allows you to talk to the com object. This is a 
#            python module created from the dll. We fixed intitial errors in this atomatically crated file. 
#            It should be under measurement/hardware/Multi_DM


class Multi_DM(Instrument): 
    '''
    This is the driver for the deformable mirror by Boston Micromachines. 
    It is specific to the Multi DM version with 140 actuators. 
    2014-12-29 Machiel Blok and Hannes Bernien

    Usage:
    Initialize with
    <name> = qt.instruments.create('name', 'Multi_DM',progid)
    

    explanation:
        - progid: this is the ID under which the DLL is registered. You can find it in the Regedit
            e.g. progid = '{615FAAA3-B515-4d4c-9F04-013D13FEB154}'

    status:

    To Do's optional:
        - several DMs per setup
        - usable with mini DM
    '''

    def __init__(self, name, progid = '{615FAAA3-B515-4d4c-9F04-013D13FEB154}'): 
         # Initialize wrapper
        logging.info(__name__ + ' : Initializing instrument Multi_DM')
        Instrument.__init__(self, name, tags=['physical'])

        # Create the interface to the com object
        self._dm = cc.CreateObject(progid, interface=Multi_DM_interface.IHostDrv)

        # find available devices
        self.res =  self._dm.CIUsb_GetAvailableDevices(32)
        self.noof_devices = np.sum(np.array(self.res[0][:31]) == 0)
        if self.noof_devices > 1:
            print  'found more than one DM, please adapt the driver. number of devices found = ', self.noof_devices


        self._dm.CIUsb_SetControl(0,3) # 
        self._dm.CIUsb_SetControl(0,2) # these two lines reset clear data buffer and reset the CPLD, see manual page 18
        self._dm.CIUsb_SetControl(0,4) # this turns on the HV 


        self.add_parameter('cur_voltages',
                flags=Instrument.FLAG_GETSET,
                type=types.ListType,
                doc='')
        
        self.cur_voltages = [0.]*160
        
        #Load the map linking the DAC pin nr to DM element nr
        self._map = np.loadtxt(r'D:\measuring\measurement\hardware\Multi_DM\MultiDM-04.map',dtype=int)

        #Load the flat configuration
        self._flat_hex=np.loadtxt(r'D:\measuring\measurement\hardware\Multi_DM\flat.txt',dtype=str)
        self._flat=[0]*160
        for i in np.arange(160):
            self._flat[i]=100*int(self._flat_hex[i],16)/65535.

        # Distribute the DM in 36 segments of 4 actuators
        self.bigger_segments=[[1,11,12],[2,3,13,14],[4,5,15,16],[6,7,17,18],[8,9,19,20],[10,21,22],
               [23,24,35,36],[25,26,37,38],[27,28,39,40],[29,30,41,42],[31,32,43,44],[33,34,45,46],
               [47,48,59,60],[49,50,61,62],[51,52,63,64],[53,54,65,66],[55,56,67,68],[57,58,69,70],
               [71,72,83,84],[73,74,85,86],[75,76,87,88],[77,78,89,90],[79,80,91,92],[81,82,93,94],
               [95,96,107,108],[97,98,109,110],[99,100,111,112],[101,102,113,114],[103,104,115,116],[105,106,117,118],
               [119,120,131],[121,122,132,133],[123,124,134,135],[125,126,136,137],[127,128,138,139],[129,130,140]]
        # To add functions that are externally available
        self.add_function('set_single_actuator')
        self.add_function('set_flat_dm')
        self.add_function('get_flat_dm')
        self.add_function('get_bigger_segments')
        self.add_function('voltages_from_matrix')
        self.add_function('matrix_from_voltages')
        self.add_function('turn_off_high_voltage')
        self.add_function('turn_on_high_voltage')

        # Load/ Initialize the config
        cfg_fn = os.path.abspath(
                os.path.join(qt.config['cfg_path'], name+'.cfg'))
        if not os.path.exists(cfg_fn):
            _f = open(cfg_fn, 'w')
            _f.write('')
            _f.close()
        
        self._parlist = ['cur_voltages']
        self.ins_cfg = config.Config(cfg_fn)
        self.load_cfg()
        self.save_cfg()

    def turn_on_high_voltage(self):
        self._dm.CIUsb_SetControl(0,4)
    
    def turn_off_high_voltage(self):
        self._dm.CIUsb_SetControl(0,5)


    def get_all(self):
        for n in self._parlist:
            self.get(n)
        
    def load_cfg(self):
        params_from_cfg = self.ins_cfg.get_all()
        for p in params_from_cfg:
            if p in self._parlist:
                self.set(p, value=self.ins_cfg.get(p))

    def save_cfg(self):
        for param in self._parlist:
            value = self.get(param)
            self.ins_cfg[param] = value

    def _from_DM_to_input_list(self,voltages):
        """
        This functions maps an ordered DM list (where the first element corresponds to DM nr 1) 
        to a list that can be used as input for the StepFrameData function.
        The mapping is imported from the MultiDM-04.map file in ..\hardware\Multi_DM

        NOTE: from measuring the actual map we found an anomaly at DM # 40 and 41 (connected to same pin). 
        This means we have to adjust the array, to correct for this. We will send an email to B-micromachines to check up on this.
        """

        input_list=[0.]*160

        
        for i in np.arange(160):
            input_list[i]= voltages[self._map[i]]           
        return input_list    

    def do_set_cur_voltages(self,voltages,do_save_cfg = True):
        """
        sets the voltages of the actuators to specified values. 
        voltages should be a list with 160 floats. the values are between 0 and 100.
        The list is ordered such that the first element sets DM # 1, the last element sets DM # 160
        """
        self.cur_voltages = voltages 
        input_list=self._from_DM_to_input_list(voltages)

        ushort_array = ctypes.c_ushort*160
        ushort_data = ushort_array(0)

        for i in np.arange(160):
            ushort_data[i]= int(round(input_list[i]*65535./100.))

        self._dm.CIUsb_StepFrameData(0,ushort_data,320)
        if do_save_cfg:    
            self.save_cfg()

    def do_get_cur_voltages(self):
        return self.cur_voltages

    def set_single_actuator(self,actuator_nr,voltage, do_save_cfg=True):    
        """
        sets the voltage of a single actuator to a specified value. 
        voltage should be a float with a value between 0 and 100.
        actuator_nr is an integer (1-160) corresponding to the actuator that you want to set.
        """

        set_v=self.get_cur_voltages()
        set_v[actuator_nr-1]=voltage
        self.set_cur_voltages(set_v,do_save_cfg=do_save_cfg)

    def set_flat_dm(self):
        self.set_cur_voltages(self._flat)

    def get_flat_dm(self):
        return self._flat    

    def get_bigger_segments(self):
        return self.bigger_segments

    def voltages_from_matrix(self, matrix):
        """
        sets the voltages of the actuators to the values as specified in the matrix shape. (See DM manual)
        Note that the corner elements of the matrix are ignored.
        The matrix should be a numpy array of floats, swith shape 12 x 12.
        """
        if not matrix.shape == (12,12):
            logging.warning('Matrix has wrong shape:' + str(matrix.shape))
            return 

        voltages = np.array([])
        for col in range(12):
            if col == 0 or col == 11:
                voltages = np.append(voltages,matrix[1:11,col][::-1])#.flatten())
            else:
                voltages = np.append(voltages,matrix[:,col][::-1])#.flatten())#(1-2*col%2)])
        return np.append(voltages,np.zeros(20))

    def matrix_from_voltages(self, voltages):
        matrix=np.ones((12,12))*50.
        for col in range(12):
            if col == 0:
                matrix[1:11,col] = voltages[0:10][::-1]
            elif col == 11:
                matrix[1:11,col] = voltages[140-10:140][::-1]
            else:
                ii=(col-1)*12+10
                matrix[:,col] = voltages[ii:ii+12][::-1]
        return matrix

    def plot_mirror_surf(self,save=False,filepath=None, plot_diff_from_flat=True):
        x = np.linspace(-1,1,12)
        y = np.linspace(-1,1,12)
        X,Y = np.meshgrid(x,y)
        Z = self.matrix_from_voltages(self.get_cur_voltages())
        if plot_diff_from_flat:
            Z = Z - self.matrix_from_voltages(self.get_flat_dm())
        fig = qt.plot3(X.flatten(),Y.flatten(),Z.flatten(), name='Mirror Surface', clear=True)
        if save:
            fig.save_png(filepath = filepath)

    def save_mirror_surf(self,filepath):
        x = np.linspace(-1,1,12)
        y = np.linspace(-1,1,12)
        X,Y = np.meshgrid(x,y)
        Z = self.matrix_from_voltages(self.get_cur_voltages())
        Z_diff = Z - self.matrix_from_voltages(self.get_flat_dm())
        np.savez(filepath, X=X,Y=Y,Z=Z, Z_diff=Z_diff, voltages=self.get_cur_voltages())

    def load_mirror_surf(self,filepath):
        d= np.load(filepath)
        self.set_cur_voltages(d['voltages'])






