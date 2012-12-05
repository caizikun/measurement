# general AOM instrument class
# assumes AOM connected to either ADwin DAC or AWG channel
# if connected to AWG, the corresponding channel's offset (analog channels) 
#    or low value (marker channels) will be used to set the power.
# parameters are stored in the setup configuration file (defined as setup_cfg in qtlab.cfg,
# and will automatically be reloaded with qtlab start.
#
# if a new AOM instrument is added, initial (not necessary useful) parameters will be used.
# channel configuration, maximum allowed voltages etc. should be immediately set after 
# loading new AOM instrument for first time.


from instrument import Instrument
from numpy import *
from analysis import fit, common
import os,sys,time
import qt
import types
from lib import config


# needed instruments
# ins_pm = qt.instruments['powermeter']
# ins_adwin = qt.instruments['adwin']
# ins_awg = qt.instruments['AWG']

class AOM(Instrument):

    def __init__(self, name, use_adwin='adwin', 
            use_pm = 'powermeter'):
        Instrument.__init__(self, name)
        
        self.add_parameter('wavelength',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='m',
                           minval=500e-9,maxval=1000e-9)
        
        self.add_parameter('cur_controller', 
                           type = types.StringType, 
                           option_list = ('AWG', 'ADWIN'), 
                           flags = Instrument.FLAG_GETSET)
        
        self.add_parameter('pri_controller', 
                           type = types.StringType, 
                           option_list = ('AWG', 'ADWIN'), 
                           flags = Instrument.FLAG_GETSET)
        
        self.add_parameter('pri_channel', 
                           type = types.StringType, 
                           flags = Instrument.FLAG_GETSET)
        
        self.add_parameter('pri_cal_a',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='W',
                           minval=0,maxval=1.0)
        
        self.add_parameter('pri_cal_xc',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='V',
                           minval=-10.0,maxval=10.0)
        
        self.add_parameter('pri_cal_k',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           minval=-100.0,maxval=100.0)
        
        self.add_parameter('pri_V_max',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='V',
                           minval=0,maxval=10.0)
        
        self.add_parameter('pri_V_min',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='V',
                           minval=-10.0,maxval=0)
        
        self.add_parameter('sec_controller', 
                           type = types.StringType, 
                           option_list = ('AWG', 'ADWIN'), 
                           flags = Instrument.FLAG_GETSET)
        
        self.add_parameter('sec_channel',
                type=types.StringType,
                flags = Instrument.FLAG_GETSET)
        
        self.add_parameter('sec_cal_a',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='W',
                           minval=0,maxval=1.0)
        
        self.add_parameter('sec_cal_xc',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='V',
                           minval=-10.0,maxval=10.0)
        
        self.add_parameter('sec_cal_k',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           minval=-100.0,maxval=100.0)
        
        self.add_parameter('sec_V_max',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='V',
                           minval=0,maxval=10.0)
        
        self.add_parameter('sec_V_min',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='V',
                           minval=-10.0,maxval=0)

        self.add_parameter('switchable',
                           type=types.BooleanType,
                           flags=Instrument.FLAG_GETSET)
        
        self.add_parameter('switch_DO',
                           type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           minval=0,maxval=31)
        
    #FIXME: this function should be in here to compensate for buffer amplifier offset.
     #   self.add_parameter('V_zero_power',
     #                      type=types.FloatType,
     #                      flags=Instrument.FLAG_GETSET,
     #                      units='V',
     #                      minval=0,maxval=10.0)

        self.ins_adwin=qt.instruments[use_adwin]
        self.ins_pm=qt.instruments[use_pm]

        # set defaults
        self._wavelength = 637e-9
        self._pri_controller =  "ADWIN"
        self._cur_controller =  "ADWIN"
        self._pri_channel =     "newfocus_aom"
        self._pri_cal_a =       0.823
        self._pri_cal_xc =      0.588
        self._pri_cal_k =       6.855
        self._pri_V_max =       1.0
        self._pri_V_min =       0
        self._switchable =      False
        self._switch_DO =       16
        self._sec_controller =  "AWG"
        self._sec_channel =     "ch1"
        self._sec_cal_a =       0.823
        self._sec_cal_xc =      0.588
        self._sec_cal_k =       6.855
        self._sec_V_max =       1.0
        self._sec_V_min =       0
        self._V_zero_power =    0.
        self.get_all()
       
        # override from config       
        cfg_fn = os.path.join(qt.config['ins_cfg_path'], name+'.cfg')
        if not os.path.exists(cfg_fn):
            _f = open(cfg_fn, 'w')
            _f.write('')
            _f.close()

        self.ins_cfg = config.Config(cfg_fn)     
        self.load_cfg()
        self.save_cfg()

    def get_all(self):
        for n in self.get_parameter_names():
            self.get(n)
        
    
    def load_cfg(self):
        params_from_cfg = self.ins_cfg.get_all()
        for p in params_from_cfg:
            val = self.ins_cfg.get(p)
            if type(val) == unicode:
                val = str(val)
            self.set(p, value=val)

    def save_cfg(self):
        parlist = self.get_parameters()
        for param in parlist:
            value = self.get(param)
            self.ins_cfg[param] = value
    #FIXME: this function should be in here
    #def set_zero_power(self):
    #    self.apply_voltage(self.get(param))

    def apply_voltage(self, U):
        controller = self.get_cur_controller()
        channel = self.get_channel()
        V_max = self.get_V_max()
        V_min = self.get_V_min()
        AWG_instr = qt.instruments['AWG']
        
        if not(V_min <= U <= V_max):
            print('Error: extreme voltage of this channel exceeded: ')
            print 'U is not %.2f =< %.2f =< %.2f' % (V_min, U, V_max)
            return
        if controller in ('AWG'):
            if qt.instruments['AWG'].get_runmode() != 'CONT':
                print('Warning: AWG not in continuous mode!')
           
            apply = {'ch1': AWG_instr.set_ch1_offset,
                     'ch1m1': AWG_instr.set_ch1_marker1_low,
                     'ch1m2': AWG_instr.set_ch1_marker2_low,
                     'ch2': AWG_instr.set_ch2_offset,
                     'ch2m1': AWG_instr.set_ch2_marker1_low,
                     'ch2m2': AWG_instr.set_ch2_marker2_low,
                     'ch3': AWG_instr.set_ch3_offset,
                     'ch3m1': AWG_instr.set_ch3_marker1_low,
                     'ch3m2': AWG_instr.set_ch3_marker2_low,
                     'ch4': AWG_instr.set_ch4_offset,
                     'ch4m1': AWG_instr.set_ch4_marker1_low,
                     'ch4m2': AWG_instr.set_ch4_marker2_low,
                     }
            apply[channel](U)
        elif controller in ('ADWIN'):
            self.ins_adwin.set_dac_voltage([channel,U])
            #print 'Applying voltage: channel %s, voltage %s'%(channel,U)
        else:
            print('Error: unknown AOM controller %s'%controller)
        return

    def get_voltage(self):
        controller = self.get_cur_controller()
        channel = self.get_channel()
        AWG_instr = qt.instruments['AWG']
        if controller in ('AWG'):
            if qt.instruments['AWG'].get_runmode() != 'CONT':
                print('Warning: AWG not in continuous mode!')
           
            get_ch = {'ch1': AWG_instr.get_ch1_offset,
                     'ch1m1': AWG_instr.get_ch1_marker1_low,
                     'ch1m2': AWG_instr.get_ch1_marker2_low,
                     'ch2': AWG_instr.get_ch2_offset,
                     'ch2m1': AWG_instr.get_ch2_marker1_low,
                     'ch2m2': AWG_instr.get_ch2_marker2_low,
                     'ch3': AWG_instr.get_ch3_offset,
                     'ch3m1': AWG_instr.get_ch3_marker1_low,
                     'ch3m2': AWG_instr.get_ch3_marker2_low,
                     'ch4': AWG_instr.get_ch4_offset,
                     'ch4m1': AWG_instr.get_ch4_marker1_low,
                     'ch4m2': AWG_instr.get_ch4_marker2_low,
                     }
            return get_ch[channel]()
        elif controller in ('ADWIN'):
            return self.ins_adwin.get_dac_voltage(channel)
        else:
            print('Error: unknown AOM controller %s'%controller)
        return

    def calibrate(self, steps): # calibration values in uW
        rng = arange(0,steps)
        x = zeros(steps,dtype = float)
        y = zeros(steps,dtype = float)
        
        self.apply_voltage(0)
        self.ins_pm.set_wavelength(self._wavelength*1e9)
        time.sleep(2)
        bg = self.ins_pm.get_power()

        print 'background power: %.4f uW' % (bg*1e6)

        time.sleep(2)

        V_max = self.get_V_max()
        V_min = self.get_V_min()
        
        if V_max + V_min < 0: rng=flipud(rng)
        
        for a in rng:
            x[a] = a*(V_max-V_min)/float(steps-1)+V_min
            self.apply_voltage(x[a])
            time.sleep(1)
            y[a] = self.ins_pm.get_power() - bg
            
            print 'measured power at %.2f V: %.4f uW' % \
                    (a*(V_max-V_min)/float(steps-1)+V_min, y[a]*1e6)
        
        #x= x*(V_max-V_min)/float(steps-1)+V_min 
        a, xc, k = copysign(max(y), V_max + V_min), copysign(.5, V_max + V_min), copysign(5., V_max + V_min)
        fitres = fit.fit1d(x,y, common.fit_AOM_powerdependence, 
                a, xc, k, do_print=True, do_plot=False, ret=True)
     
        fd = zeros(len(x))        
        if type(fitres) != type(False):
            p1 = fitres['params_dict']
            self.set_cal_a(p1['a'])
            self.set_cal_xc(p1['xc'])
            self.set_cal_k(p1['k'])
            fd = fitres['fitdata']
        else:
            print 'could not fit calibration curve!'
        
        dat = qt.Data(name= 'aom_calibration_'+self._name+'_'+\
                self._cur_controller)
        dat.add_coordinate('Voltage [V]')
        dat.add_value('Power [W]')
        dat.add_value('fit')
        dat.create_file()
        plt = qt.Plot2D(dat, 'rO', name='aom calibration', coorddim=0, valdim=1, 
                clear=True)
        plt.add_data(dat, coorddim=0, valdim=2)
        dat.add_data_point(x,y,fd)
        dat.close_file()
        plt.save_png(dat.get_filepath()+'png')

        self.save_cfg()
        print (self._name+' calibration finished')

    def power_to_voltage(self, p):
        a = self.get_cal_a()
        xc = self.get_cal_xc()
        k = self.get_cal_k()

        if p <= 0:
            voltage = 0
        else:
            voltage = xc-log(log(a/float(p)))/k
        
        return voltage

    def voltage_to_power(self, u):
        a = self.get_cal_a()
        xc = self.get_cal_xc()
        k = self.get_cal_k()

        #if u <= 0:
        #    power = 0
        #else:
        power=a/(exp(exp(k*(-float(u)+xc))))
        return power

    def set_power(self,p): # power in Watt
        self.apply_voltage(self.power_to_voltage(p))

    def get_power(self):
        return self.voltage_to_power(self.get_voltage())

    def do_set_cur_controller(self, val):
        # print val
        
        if self.get_voltage() != 0:
             print 'To change controller, please set output voltage to 0 V first.'
             print 'Current output:', self.get_voltage() , 'V'
             print 'Controller not changed.'
             return

        if (val != self._pri_controller) & (val != self._sec_controller):
            print ('Error: controller %s not registered, using %s instead'%(val, 
                self._pri_controller))
            self._cur_controller = self._pri_controller

        if self._switchable == True:
            if val == self._pri_controller:
                qt.instruments['ADWIN'].Set_DO(self._switch_DO,0)
            else:
                qt.instruments['ADWIN'].Set_DO(self._switch_DO,1)

        self._cur_controller = val
        # self.save_cfg()

    def do_set_wavelength(self, val):
        self._wavelength = val
        # self.save_cfg()

    def do_get_wavelength(self):
        return self._wavelength

    def do_get_cur_controller(self):
        return self._cur_controller

    def do_set_pri_controller(self, val):
        self._pri_controller = val
        # self.save_cfg()

    def do_get_pri_controller(self):
        return self._pri_controller

    def do_set_sec_controller(self, val):
        self._sec_controller = val
        # self.save_cfg()

    def do_get_sec_controller(self):
        return self._sec_controller

    def do_get_switchable(self):
        return self._switchable

    def do_set_switchable(self, val):
        self._switchable = val
        # self.save_cfg()

    def do_get_switch_DO(self):
        return self._switch_DO

    def do_set_switch_DO(self, val):
        self._switch_DO = val
        # self.save_cfg()

    def set_cal_a(self, val):
        if self._cur_controller == self._pri_controller:
            self.do_set_pri_cal_a(val)
        else:
            self.do_set_sec_cal_a(val)

    def set_cal_xc(self, val):
        if self._cur_controller == self._pri_controller:
            self.do_set_pri_cal_xc(val)
        else:
            self.do_set_sec_cal_xc(val)

    def set_cal_k(self, val):
        if self._cur_controller == self._pri_controller:
            self.do_set_pri_cal_k(val)
        else:
            self.do_set_sec_cal_k(val)

    def get_cal_a(self):
        if self._cur_controller == self._pri_controller:
            return self.do_get_pri_cal_a()
        else:
            return self.do_get_sec_cal_a()

    def get_cal_xc(self):
        if self._cur_controller == self._pri_controller:
            return self.do_get_pri_cal_xc()
        else:
            return self.do_get_sec_cal_xc()

    def get_cal_k(self):
        if self._cur_controller == self._pri_controller:
            return self.do_get_pri_cal_k()
        else:
            return self.do_get_sec_cal_k()

    def do_set_pri_cal_a(self, val):
        self._pri_cal_a = val
        # self.save_cfg()

    def do_set_sec_cal_a(self, val):
        self._sec_cal_a = val
        # self.save_cfg()

    def do_set_pri_cal_xc(self, val):
        self._pri_cal_xc = val
        # self.save_cfg()

    def do_set_sec_cal_xc(self, val):
        self._sec_cal_xc = val
        # self.save_cfg()

    def do_set_pri_cal_k(self, val):
        self._pri_cal_k = val
        # self.save_cfg()

    def do_set_sec_cal_k(self, val):
        self._sec_cal_k = val
        # self.save_cfg()

    def do_get_pri_cal_a(self):
        return self._pri_cal_a

    def do_get_sec_cal_a(self):
        return self._sec_cal_a

    def do_get_pri_cal_xc(self):
        return self._pri_cal_xc

    def do_get_sec_cal_xc(self):
        return self._sec_cal_xc

    def do_get_pri_cal_k(self):
        return self._pri_cal_k

    def do_get_sec_cal_k(self):
        return self._sec_cal_k

    def set_V_max(self, val):
        if self._cur_controller == self._pri_controller:
            self.do_set_pri_V_max(val)
        else:
            self.do_set_sec_V_max(val)

    def get_V_max(self):
        if self._cur_controller == self._pri_controller:
            return self.do_get_pri_V_max()
        else:
            return self.do_get_sec_V_max()

    def set_V_min(self, val):
        if self._cur_controller == self._pri_controller:
            self.do_set_pri_V_min(val)
        else:
            self.do_set_sec_V_min(val)

    def get_V_min(self):
        if self._cur_controller == self._pri_controller:
            return self.do_get_pri_V_min()
        else:
            return self.do_get_sec_V_min()

    def do_set_pri_V_max(self, val):
        self._pri_V_max = val
        # self.save_cfg()

    def do_set_sec_V_max(self, val):
        self._sec_V_max = val
        # self.save_cfg()

    def do_get_pri_V_max(self):
        return self._pri_V_max

    def do_get_sec_V_max(self):
        return self._sec_V_max

    def do_set_pri_V_min(self, val):
        self._pri_V_min = val
        # self.save_cfg()

    def do_set_sec_V_min(self, val):
        self._sec_V_min = val
        # self.save_cfg()

    def do_get_pri_V_min(self):
        return self._pri_V_min

    def do_get_sec_V_min(self):
        return self._sec_V_min

    def set_channel(self, val):
        if self._cur_controller == self._pri_controller:
            self.do_set_pri_channel(val)
        else:
            self.do_set_sec_channel(val)

    def get_channel(self):
        if self._cur_controller == self._pri_controller:
            return self.do_get_pri_channel()
        else:
            return self.do_get_sec_channel()

    def do_set_pri_channel(self, val):
        self._pri_channel = val
        # self.save_cfg()

    def do_set_sec_channel(self, val):
        self._sec_channel = val
        # self.save_cfg()

    def do_get_pri_channel(self):
        return self._pri_channel

    def do_get_sec_channel(self):
        return self._sec_channel

