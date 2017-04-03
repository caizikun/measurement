import qt
import msvcrt
import time
import scipy
import numpy as np
import os

import measurement.lib.measurement2.measurement as m2

class LaserScanGreenRed(m2.AdwinControlledMeasurement):
    mprefix = 'LaserScanGreenRed'

    adwin_process = 'laserscan_green_red'
    green_aom = qt.instruments['GreenAOM']
    red_aom = qt.instruments['NewfocusAOM']
    adwin = qt.instruments['adwin']
    mw_src = qt.instruments['SMB100']
        
    def autoconfig(self):

        """
        sets/computes parameters (can be from other, user-set params)
        as required by the specific type of measurement.
        E.g., compute AOM voltages from desired laser power, or get
        the correct AOM DAC channel from the specified AOM instrument.
        """
        # print self.E_aom.get.name()
        self.params['green_aom_dac_channel'] = self.adwin.get_dac_channels()\
                [self.green_aom.get_pri_channel()]
        self.params['red_aom_dac_channel'] = self.adwin.get_dac_channels()\
                [self.red_aom.get_pri_channel()]
 
        self.params['green_voltage'] = self.green_aom.power_to_voltage(self.params['green_amplitude'])
        self.params['red_voltage'] = self.red_aom.power_to_voltage(self.params['red_amplitude'])
        self.params['green_off_voltage'] = self.green_aom.get_pri_V_off()
        self.params['red_off_voltage'] = self.red_aom.get_pri_V_off()
        
        m2.AdwinControlledMeasurement.autoconfig(self)


    def setup(self):
        """
        sets up the hardware such that the msmt can be run
        (i.e., turn off the lasers, prepare MW src, etc)
        """
        if self.params['mw']:
            self.mw_src.set_frequency(self.params['mw_frequency'])
            self.mw_src.set_power(self.params['mw_power'])
            self.mw_src.set_iq('off')
            self.mw_src.set_pulm('off')
            self.mw_src.set_status('on')

    def run(self, autoconfig=True, setup=True):
        
        if autoconfig:
            self.autoconfig()         
        if setup:
            self.setup()

        self.dat = qt.Data(name= self.name+'_data')#, inmem=True, infile=False )
        self.dat.add_coordinate('Voltage [V]')
        self.dat.add_coordinate('Frequency [GHz]')
        self.dat.add_value('Counts [Hz]')
        self.dat.create_file(filepath=os.path.splitext(self.h5data.filepath())[0]+'.dat')
        self.plt = qt.Plot2D(self.dat, 'r-', name='laser_scan', coorddim=1, valdim=2, 
                        clear=True)
        if self.params['plot_voltage']:
            self.plt.add_data(self.dat,coorddim=1, valdim=0, right=True)

        self.start_adwin_process(stop_processes=['counter'])
        qt.msleep(1)
        self.start_keystroke_monitor('abort',timer=False)
        
        prev_px_clock = 0
        aborted=False
        while self.adwin_process_running():
            self._keystroke_check('abort')
            if self.keystroke('abort') in ['q','Q']:
                print 'aborted.'
                aborted = True
                self.stop_keystroke_monitor('abort')
                break
            px_clock = self.adwin_var('pixel_clock')
            start = prev_px_clock+1
            length  = px_clock-prev_px_clock
            if length > 0:
                
                f = self.adwin_var(('laser_frequencies',start, length))
                valid_range = f>-3000
                v = self.adwin_var(('voltages',start, length))
                cs = self.adwin_var(('counts',start, length))
                c = (cs[0]+cs[1])/(self.params['pixel_time']*1.e-6)
                if np.sum(valid_range)>1:
                    self.dat.add_data_point(v[valid_range],f[valid_range],c[valid_range])
                    prev_px_clock = px_clock
            qt.msleep(0.2)

            self.plt.update()
        try:
            self.stop_keystroke_monitor('abort')
        except KeyError:
            pass # means it's already stopped
        self.stop_adwin_process()
        return not(aborted)

    def save(self):
        self.plt.save_png(os.path.splitext(self.h5data.filepath())[0]+'.png')
        if len(self.dat.get_data()) > 0:
            self.h5data.create_datagroup_from_qtdata(self.dat)

    def finish(self):
        if self.params['mw']:
            self.mw_src.set_status('off')
        self.dat.close_file()
        m2.AdwinControlledMeasurement.finish(self)


def laser_scan_green_red(name,green_power,red_power):

    m = LaserScanGreenRed(name+'_g_'+str(green_power*1.e6)+'_r_'+str(red_power*1.e9))
    m.params['freq_dac_channel'] = m.adwin.get_dac_channels()['newfocus_frq']
    m.params['plot_voltage'] = True

    m.params['scan_start_voltage'] =1.8# 0.2
    m.params['scan_stop_voltage'] = -1.3#-1.3
    m.params['noof_pixels'] = int(20e9/10e6) # 60 GHz (approx newfocus range) / (stepsize 100 MHz)
    m.params['pixel_time'] = 100 *1000 #us

    m.params['green_time'] = 10 # us
    m.params['wait_after_green_time'] = 10 #us
    m.params['red_time'] =  50 # us
    
    m.params['mw'] = False
    m.params['green_amplitude'] = green_power#30e-6#12.5
    m.params['red_amplitude'] = red_power#10e-9

    print 'expected time:', float(m.params['noof_pixels'])*m.params['pixel_time']*1e-6/60., 'minutes'

    m.run()
    m.save()
    m.finish()
    print 'Finished'

def long_fast_laser_scan_green_red(name):
    '''
    Repeats full voltage range scans for coarse wavelength steps
    '''
    opt_ins = qt.instruments['optimiz0r']
    opt1d_ins = qt.instruments['opt1d_counts']
    mos_ins = qt.instruments['master_of_space']
    green_powers = np.array([30.e-6,50.e-6,20.e-6])
    red_powers = np.array([2.e-9,5.e-9,10.e-9,20.e-9])
    red_power,green_power = np.meshgrid(red_powers,green_powers)
    green_power= green_power.flatten()
    red_power= red_power.flatten()
    #green_power = np.array([10.e-6,10.e-6,10.e-6,20.e-6,20.e-6,20.e-6,])



    #fs = np.arange(-400,400,50)
    #wls = np.linspace(637.26,637.22,2)
    #print fs

    for ii in np.arange(len(green_power)):
        # for j in range(3):
        #     set_nf_frequency_coarse(f)
        #     qt.msleep(1)
        if i==0:
            continue
        print i+1,'out of',len(green_power)+1,green_power[ii],red_power[ii]
        #qt.msleep(1)
        laser_scan_green_red(name,green_power[ii],red_power[ii])
        #mos_ins.set_x(mos_ins.get_x()-1)
        #opt_ins.optimize(dims=['z'], cycles = 1, int_time = 100)
        #opt1d_ins.run(dimension='z', scan_length=5, nr_of_points=31, pixel_time=100, return_data=False, gaussian_fit=True)
        #mos_ins.set_x(mos_ins.get_x()+1)
        #mos_ins.set_z(mos_ins.get_z()+0.6)
        #qt.msleep(1)
        GreenAOM.set_power(180e-6)
        opt_ins.optimize(dims=['x','y','z','x','y'], cycles = 1, int_time = 100, cnt=2)

        
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
            break 


if __name__ == '__main__':
   name = 'SiriusII_NV3'
   laser_scan_green_red(name, 30e-6,8e-9)
   #long_fast_laser_scan_green_red(name)


 