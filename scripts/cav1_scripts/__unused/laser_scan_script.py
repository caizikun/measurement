import msvcrt
import time
import qt
import os
import numpy as np
import measurement.lib.config.adwins as adwins_cfg
reload (adwins_cfg)
import measurement.lib.measurement2.measurement as m2
reload(m2)


class LaserScan_Photodiode_Msmnt (m2.AdwinControlledMeasurement):

    mprefix = 'LaserFrequencyScan'
    adwin_process = 'laserscan_photodiode'
    adwin_dict = adwins_cfg.config


    mprefix = 'AdwinSSRO'
    max_repetitions = 20000
    max_SP_bins = 500
    max_SSRO_dim = 1000000
    adwin_process = 'singleshot'
    adwin_dict = adwins_cfg.config
    adwin_processes_key = ''
    E_aom = None
    A_aom = None
    repump_aom = None
    adwin = None
        
    def autoconfig(self):
        """
        sets/computes parameters (can be from other, user-set params)
        as required by the specific type of measurement.
        E.g., compute AOM voltages from desired laser power, or get
        the correct AOM DAC channel from the specified AOM instrument.
        """
        self.params['Ex_laser_DAC_channel'] = self.adwin.get_dac_channels()\
                [self.E_aom.get_pri_channel()]
        self.params['A_laser_DAC_channel'] = self.adwin.get_dac_channels()\
                [self.A_aom.get_pri_channel()]
        self.params['repump_laser_DAC_channel'] = self.adwin.get_dac_channels()\
                [self.repump_aom.get_pri_channel()]    

        if self.params['cr_mod']:
            self.params['repump_mod_DAC_channel'] = self.adwin.get_dac_channels()[self.params['repump_mod_control_dac']]
            self.params['repump_mod_control_offset'] = self.adwin.get_dac_voltage(self.params['repump_mod_control_dac'])
            self.params['cr_mod_DAC_channel']     = self.adwin.get_dac_channels()[self.params['cr_mod_control_dac']]#ssro.AdwinSSRO.adwin.get_dac_channels()['gate']

        self.params['Ex_CR_voltage'] = \
                self.E_aom.power_to_voltage(
                        self.params['Ex_CR_amplitude'])
        
        self.params['A_CR_voltage'] = \
                self.A_aom.power_to_voltage(
                        self.params['A_CR_amplitude'])

        self.params['Ex_SP_voltage'] = \
                self.E_aom.power_to_voltage(
                        self.params['Ex_SP_amplitude'])

        self.params['A_SP_voltage'] = \
                self.A_aom.power_to_voltage(
                        self.params['A_SP_amplitude'])

        self.params['Ex_RO_voltage'] = \
                self.E_aom.power_to_voltage(
                        self.params['Ex_RO_amplitude'])

        self.params['A_RO_voltage'] = \
                self.A_aom.power_to_voltage(
                        self.params['A_RO_amplitude'])
                       
        self.params['repump_voltage'] = \
                self.repump_aom.power_to_voltage(
                        self.params['repump_amplitude'])

        self.params['repump_off_voltage'] = \
                self.repump_aom.get_pri_V_off()
        self.params['A_off_voltage'] = \
                self.A_aom.get_pri_V_off()
        self.params['Ex_off_voltage'] = \
                self.E_aom.get_pri_V_off()

        for key,_val in self.adwin_dict[self.adwin_processes_key]\
                [self.adwin_process]['params_long']:              
            self.set_adwin_process_variable_from_params(key)

        for key,_val in self.adwin_dict[self.adwin_processes_key]\
                [self.adwin_process]['params_float']:              
            self.set_adwin_process_variable_from_params(key)

        if 'include_cr_process' in self.adwin_dict[self.adwin_processes_key]\
                [self.adwin_process]:
            for key,_val in self.adwin_dict[self.adwin_processes_key]\
                    [self.adwin_dict[self.adwin_processes_key]\
                [self.adwin_process]['include_cr_process']]['params_long']:              
                self.set_adwin_process_variable_from_params(key)
            for key,_val in self.adwin_dict[self.adwin_processes_key]\
                    [self.adwin_dict[self.adwin_processes_key]\
                [self.adwin_process]['include_cr_process']]['params_float']:              
                self.set_adwin_process_variable_from_params(key)

        

    def setup(self):
        """
        sets up the hardware such that the msmt can be run
        (i.e., turn off the lasers, prepare MW src, etc)
        """
        
        self.repump_aom.set_power(0.)
        self.E_aom.set_power(0.)
        self.A_aom.set_power(0.)
        self.repump_aom.set_cur_controller('ADWIN')
        self.E_aom.set_cur_controller('ADWIN')
        self.A_aom.set_cur_controller('ADWIN')
        self.repump_aom.set_power(0.)
        self.E_aom.set_power(0.)
        self.A_aom.set_power(0.)        
    
    def set_adwin_process_variable_from_params(self,key):
        try:
            # Here we can do some checks on the settings in the adwin
            if np.isnan(self.params[key]):
                raise Exception('Adwin process variable {} contains NAN'.format(key))
            self.adwin_process_params[key] = self.params[key]
        except:
            logging.error("Cannot set adwin process variable '%s'" \
                    % key)
            raise Exception('Adwin process variable {} has not been set \
                                in the measurement params dictionary!'.format(key))

    def run(self, autoconfig=True, setup=True):
        if autoconfig:
            self.autoconfig()
            
        if setup:
            self.setup()
        print self.adwin_process
        self.start_adwin_process(stop_processes=['counter'])
        qt.msleep(1)
        self.start_keystroke_monitor('abort',timer=False)
        
        CR_counts = 0
        while self.adwin_process_running():
            self._keystroke_check('abort')
            if self.keystroke('abort') in ['q','Q']:
                print 'aborted.'
                self.stop_keystroke_monitor('abort')
                break
            
            reps_completed = self.adwin_var('completed_reps')
            #print self.adwin_var('total_CR_counts')
            CR_counts = self.adwin_var('total_CR_counts') - CR_counts
            
            print('completed %s / %s readout repetitions' % \
                    (reps_completed, self.params['SSRO_repetitions']))
            # print('threshold: %s cts, last CR check: %s cts' % (trh, cts))
            
            qt.msleep(1)

        try:
            self.stop_keystroke_monitor('abort')
        except KeyError:
            pass # means it's already stopped
        self.stop_adwin_process()
        # qt.msleep(1)
        reps_completed = self.adwin_var('completed_reps')
        print('completed %s / %s readout repetitions' % \
                (reps_completed, self.params['SSRO_repetitions']))

    def save(self, name='ssro'):
        reps = self.adwin_var('completed_reps')
        self.save_adwin_data(name,
                [   ('CR_before', reps),
                    ('CR_after', reps),
                    ('SP_hist', self.params['SP_duration']),
                    ('RO_data', reps * self.params['SSRO_duration']),
                    ('statistics', 10),
                    'completed_reps',
                    'total_CR_counts'])

    def finish(self, save_params=True, save_stack=True, 
            stack_depth=4, save_cfg=True, save_ins_settings=True):
               
        if save_params:
            self.save_params()
            
        if save_stack:
            self.save_stack(depth=stack_depth)
            
        if save_ins_settings:
            self.save_instrument_settings_file()
        qt.instruments['counters'].set_is_running(True)
        self.repump_aom.set_power(0)
        self.E_aom.set_power(0)
        self.A_aom.set_power(0)
        
        m2.AdwinControlledMeasurement.finish(self)





'''





    def __init__(self, name):
        self.name = name
        
        self.adwin = qt.get_setup_instrument('adwin')
        self.physical_adwin = qt.get_setup_instrument('physical_adwin_cav1')
        self.wavemeter_adwin = qt.get_setup_instrument('physical_adwin_lt3')
        self.wavemeter_fpar = 45
        self.adc_channel = 

    
    def scan_to_voltage(self, target_voltage, get_voltage_method, set_voltage_method, 
            voltage_step=0.01, dwell_time=0.01):
        steps = np.append(np.arange(get_voltage_method(), target_voltage, voltage_step), target_voltage)
        for s in steps:
            set_voltage_method(s)
            qt.msleep(dwell_time)
    
    def prepare_scan(self):
        pass

    def finish_scan(self):
        pass

    def scan_to_frequency(self, f, voltage_step_scan=0.05, dwell_time=0.01, tolerance=0.3, power = 0, **kw):

        set_voltage = kw.pop('set_voltage', self.set_red_laser_voltage)
        get_voltage = kw.pop('get_voltage', self.get_red_laser_voltage)
        wm_channel = kw.pop('wm_channel', self.red_wm_channel)
        voltage_frequency_relation_sign = kw.pop('voltage_frequency_relation_sign', 
            self.red_voltage_frequency_relation_sign)
        set_power = kw.get('set_power', self.set_red_power)
        
        # print 'scan to frequency', f
        
        v = get_voltage()
        success = False

        set_power(power)
        cur_f = self.get_frequency(wm_channel)
        while ((v < self.max_v - 0.3) and (v > self.min_v + 0.3)):
            if (msvcrt.kbhit() and msvcrt.getch()=='q'): 
                break
            
            cur_f = self.get_frequency(wm_channel)
            set_voltage(v)
            v = v + voltage_step_scan * np.sign(f-cur_f) * voltage_frequency_relation_sign
            qt.msleep(dwell_time)
            
            if abs(cur_f-f) < tolerance:
                success = True
                break
        
        if not success:
            print 'WARNING: could not reach target frequency', f
        print 'current frequency:', cur_f

        set_power(0)
        
        return v
    
    def single_line_scan(self, start_f, stop_f, 
        voltage_step, integration_time_ms, power, **kw):

        stabilizing_time = kw.pop('stabilizing_time', 0.01)
        save = kw.pop('save', True)
        data = kw.pop('data', None)

        suffix = kw.pop('suffix', None)

        set_voltage = kw.get('set_voltage', self.set_red_laser_voltage)
        get_voltage = kw.get('get_voltage', self.get_red_laser_voltage)
        wm_channel = kw.get('wm_channel', self.red_wm_channel)
        voltage_frequency_relation_sign = kw.get('voltage_frequency_relation_sign', 
            self.red_voltage_frequency_relation_sign)
        set_power = kw.get('set_power', self.set_red_power)

        data_args = kw.get('data_args', [])

        data_obj_supplied = False
        if save:
            if data == None:
                data_obj_supplied = False

                data = qt.Data(name = self.mprefix + '_' + self.name + ('_{}'.format(suffix) if suffix != None else ''))
                data.add_coordinate('Voltage (V)')
                data.add_coordinate('Frequency (GHz)')
                data.add_coordinate('Counts [Hz]')

                plt_cts = qt.Plot2D(data, ('b-' if suffix=='yellow' else 'r-'),
                    name='Laserscan_Counts' + ('_{}'.format(suffix) if suffix != None else ''), 
                    clear=True, coorddim=1, valdim=2, maxtraces=1)

                plt_frq = qt.Plot2D(data, ('b-' if suffix=='yellow' else 'r-'),
                    name='Laserscan_Frequency' + ('_{}'.format(suffix) if suffix != None else ''), 
                    clear=True, coorddim=0, valdim=1, maxtraces=1)
            else:
                data_obj_supplied = True

        self.scan_to_frequency(start_f, **kw)
        
        v = get_voltage()

        set_power(power)
        while ((v < self.max_v - 0.3) and (v > self.min_v + 0.3)):
            if (msvcrt.kbhit() and msvcrt.getch()=='q'): 
                break

            set_voltage(v)
            qt.msleep(stabilizing_time)

            cur_f = self.get_frequency(wm_channel)
            if cur_f < -100:
                continue

            if (stop_f > start_f) and (cur_f > stop_f):
                break
            elif (stop_f <= start_f) and (cur_f < stop_f):
                break  

            cts = float(self.get_counts(integration_time_ms)[self.counter_channel]) / \
                (integration_time_ms*1e-3)

            v = v + voltage_step * np.sign(stop_f - cur_f) * voltage_frequency_relation_sign

            if save:
                if not data_obj_supplied:
                    data.add_data_point(v, cur_f, cts)
                else:
                    data.add_data_point(v, cur_f, cts, *data_args)

                if not data_obj_supplied:
                    plt_cts.update()
                    plt_frq.update()


        set_power(0)

        if save and not data_obj_supplied:
            plt_cts.save_png()
            plt_frq.save_png()


class Scan(LaserFrequencyScan):

    def __init__(self, name='LT1', red_labjack_dac_nr=2, yellow_labjack_dac_nr = 4, red_wm_channel = 1, yellow_wm_channel = 2):
        LaserFrequencyScan.__init__(self, name)
        
        self.adwin = qt.get_setup_instrument('adwin')
        self.physical_adwin=qt.get_setup_instrument('physical_adwin_lt2')
        self.mw = qt.get_setup_instrument('SMB100')
        self.labjack= qt.get_setup_instrument('labjack')
        self.wavemeter=qt.instruments['wavemeter']

        self.set_red_laser_voltage = lambda x: self.labjack.__dict__['set_bipolar_dac'+str(red_labjack_dac_nr)](x)
        self.get_red_laser_voltage = lambda : self.labjack.__dict__['get_bipolar_dac'+str(red_labjack_dac_nr)]()
        self.set_red_power = qt.get_setup_instrument('NewfocusAOM').set_power


        self.set_yellow_laser_voltage = lambda x: self.labjack.__dict__['set_bipolar_dac'+str(yellow_labjack_dac_nr)](x)
        self.get_yellow_laser_voltage = lambda : self.labjack.__dict__['get_bipolar_dac'+str(yellow_labjack_dac_nr)]()
        self.set_yellow_power = qt.get_setup_instrument('YellowAOM').set_power

        self.set_repump_power = qt.get_setup_instrument('GreenAOM').set_power

        self.get_frequency = lambda x : (self.wavemeter.Get_Frequency(x)-470.4)*1000.
        self.get_counts = self.adwin.measure_counts
        self.counter_channel = 0
        self.red_wm_channel = red_wm_channel
        self.red_voltage_frequency_relation_sign = -1


        self.yellow_voltage_frequency_relation_sign = 1
        self.yellow_wm_channel = yellow_wm_channel

        self.max_v = 9.
        self.min_v = -9.



    def yellow_scan(self, start_f, stop_f, power=0.5e-9, **kw):
        self.get_frequency = lambda x : (self.wavemeter.Get_Frequency(x)-521.22)*1000.
        voltage_step = kw.pop('voltage_step', 0.01)

        self.single_line_scan(start_f, stop_f,
            voltage_step = voltage_step, 
            oltage_step_scan=0.02,
            integration_time_ms=50, 
            power=power,
            suffix = 'yellow', 
            set_voltage = self.set_yellow_laser_voltage,
            get_voltage = self.get_yellow_laser_voltage,
            wm_channel = self.yellow_wm_channel,
            voltage_frequency_relation_sign = self.yellow_voltage_frequency_relation_sign,
            set_power = self.set_yellow_power,
            **kw)

    def yellow_ionization_scan(self, start_f, stop_f, power=50e-9, **kw):
        self.get_frequency = lambda x : (self.wavemeter.Get_Frequency(x)-521.22)*1000.
        self.single_line_scan(start_f, stop_f,
            voltage_step=0.02, integration_time_ms=5, power=power,
            voltage_step_scan=0.02,
            suffix = 'yellow', 
            set_voltage = self.set_yellow_laser_voltage,
            get_voltage = self.get_yellow_laser_voltage,
            wm_channel = self.yellow_wm_channel,
            voltage_frequency_relation_sign = self.yellow_voltage_frequency_relation_sign,
            set_power = self.set_yellow_power,
            save = False)

    def red_scan(self, start_f, stop_f, power=0.5e-9, **kw):
        self.get_frequency = lambda x : (self.wavemeter.Get_Frequency(x)-470.4)*1000.
        voltage_step = kw.pop('voltage_step', 0.005)
        integration_time_ms = kw.pop('integration_time_ms', 50)
        
        self.single_line_scan(start_f, stop_f, voltage_step, integration_time_ms, power, **kw)\

    def red_ionization_scan(self, start_f, stop_f, power=30e-9, **kw):
        self.get_frequency = lambda x : (self.wavemeter.Get_Frequency(x)-470.4)*1000.
        voltage_step = kw.pop('voltage_step', 0.04)
        integration_time_ms = kw.pop('integration_time_ms', 20)
        _save=kw.pop('save', False)        
        MatisseAOM.turn_on()
        self.single_line_scan(start_f, stop_f, voltage_step, integration_time_ms, power, 
            save=False, **kw)    
        MatisseAOM.turn_off()

    def yellow_red(self, y_start, y_stop, y_step ,y_power, r_start, r_stop, r_step, r_int, r_power, **kw):
        red_data = kw.pop('red_data', None)
        yellow_data = kw.pop('yellow_data', None)

        print 'ionization scan yellow...'
        self.yellow_ionization_scan(y_stop, y_start)

        print 'red scan...'
        self.red_scan(r_start, r_stop, 
            voltage_step=r_step, 
            integration_time_ms=r_int, 
            power=r_power, 
            data = red_data,
            **kw)
        
        print 'ionization scan red...'
        self.red_ionization_scan(r_stop, r_start)
        
        print 'yellow scan...'
        self.yellow_scan(y_start, y_stop, y_power, voltage_step=y_step,
            data = yellow_data,
            **kw)

    def spectral_diffusion(self, y_start, y_stop, y_power, r_start, r_stop, r_step, r_int, r_power, **kw):
        red_data = kw.pop('red_data', None)
        yellow_data = kw.pop('yellow_data', None)

        print 'green repump pulse'
        qt.msleep(1)
        self.set_repump_power(10e-6)
        qt.msleep(0.5)
        self.set_repump_power(0)
        qt.msleep(1)

        print 'red scan...'
        self.red_scan(r_start, r_stop, 
            voltage_step=r_step, 
            integration_time_ms=r_int, 
            power=r_power, 
            data = red_data,
            **kw)
        
        print 'ionization scan red...'
        self.red_ionization_scan(r_stop, r_start)
        
        print 'yellow scan...'
        self.yellow_scan(y_start, y_stop, y_power,
            data = yellow_data,
            **kw)        

    def green_yellow_during(self, y_start, y_stop, y_power, r_start, r_stop, r_step, r_int, r_power, g_p_during, y_p_during, **kw):
        red_data = kw.pop('red_data', None)
        yellow_data = kw.pop('yellow_data', None)
        red_data_w_green = kw.pop('red_data', None)
        yellow_data_green = kw.pop('yellow_data', None)
        red_data_w_yellow = kw.pop('red_data', None)
        yellow_data_yellow = kw.pop('yellow_data', None)


        print 'green repump pulse'
        qt.msleep(1)
        self.set_repump_power(10e-6)
        qt.msleep(0.5)
        self.set_repump_power(0)
        qt.msleep(1)

        print 'red scan...'
        self.red_scan(r_start, r_stop, 
            voltage_step=r_step, 
            integration_time_ms=r_int, 
            power=r_power, 
            data = red_data,
            **kw)
       
        print 'ionization scan red...'
        self.red_ionization_scan(r_stop, r_start)
        
        print 'yellow scan...'
        self.yellow_scan(y_start, y_stop, y_power,
            data = yellow_data,
            **kw)

        print 'green repump pulse'
        qt.msleep(1)
        self.set_repump_power(10e-6)
        qt.msleep(0.5)
        self.set_repump_power(0)
        qt.msleep(1)

        print 'red scan with green...'
        self.set_repump_power(g_p_during)

        self.red_scan(r_start, r_stop, 
            voltage_step=r_step, 
            integration_time_ms=r_int, 
            power=r_power, 
            data = red_data_w_green,
            **kw)

        self.set_repump_power(0.)
        
        print 'ionization scan red...'
        self.red_ionization_scan(r_stop, r_start)
        
        print 'yellow scan...'
        self.yellow_scan(y_start, y_stop, y_power,
            data = yellow_data_green,
            **kw)

        print 'ionization scan yellow...'
        self.yellow_ionization_scan(y_stop, y_start)

        print 'red scan with yellow...'
        self.set_yellow_power(y_p_during)

        self.red_scan(r_start, r_stop, 
            voltage_step=r_step, 
            integration_time_ms=r_int, 
            power=r_power, 
            data = red_data_w_yellow,
            **kw)
    
        self.set_yellow_power(0.)

        print 'ionization scan red...'
        self.red_ionization_scan(r_stop, r_start)
        
        print 'yellow scan...'
        self.yellow_scan(y_start, y_stop, y_power,
            data = yellow_data_yellow,
            **kw)

    def oldschool_red_scan(self, r_start, r_stop, r_step, r_int, r_power, **kw):
        red_data = kw.pop('red_data', None)

        print 'green repump pulse'
        qt.msleep(1)
        self.set_repump_power(0e-6)
        qt.msleep(1)
        self.set_repump_power(0)
        qt.msleep(1)

        print 'red scan...'
        self.red_scan(r_start, r_stop, 
            voltage_step=r_step, 
            integration_time_ms=r_int, 
            power = r_power, 
            data = red_data,
            **kw)
        


def green_yellow_during_scan():
    m = Scan()

    m.mw.set_power(-9)
    m.mw.set_frequency(2.8265e9)
    m.mw.set_iq('off')
    m.mw.set_pulm('off')
    m.mw.set_status('on')

    m.green_yellow_during(20, 23, 0.2e-9, 55, 75, 0.01, 20, 1e-9, 0.2e-6, 30e-9)

    m.mw.set_status('off')

def repeated_red_scans(**kw):
    m = Scan()

    spectral_diffusion = kw.pop('spectral_diffusion', False)
    gate_scan = kw.pop('gate_scan', False)
    gate_range=kw.pop('gate_range', None)
    pts = kw.pop('pts', 100)

    m.mw.set_power(-9)
    m.mw.set_frequency(2.8265e9)
    m.mw.set_iq('off')
    m.mw.set_pulm('off')
    m.mw.set_status('on')

    red_data = qt.Data(name = 'LaserScansYellowRepump_LT1_Red')
    red_data.add_coordinate('Voltage (V)')
    red_data.add_coordinate('Frequency (GHz)')
    red_data.add_coordinate('Counts (Hz)')
    if gate_scan:
        red_data.add_coordinate('Gate voltage (V)')
    else:
        red_data.add_coordinate('index')
    red_data.add_coordinate('start time')
    red_data.create_file()

    yellow_data = qt.Data(name = 'LaserScansYellowRepump_LT1_Yellow')
    yellow_data.add_coordinate('Voltage (V)')
    yellow_data.add_coordinate('Frequency (GHz)')
    yellow_data.add_coordinate('Counts (Hz)')
    if gate_scan:
        yellow_data.add_coordinate('Gate voltage (V)')
    else:
        yellow_data.add_coordinate('index')
    yellow_data.add_coordinate('start time')
    yellow_data.create_file()

    plt_red_cts = qt.Plot2D(red_data, 'r-',
        name='Laserscan_Counts', 
        clear=True, coorddim=1, valdim=2, maxtraces=5, traceofs=5000)

    plt_red_frq = qt.Plot2D(red_data, 'rO',
        name='Laserscan_Frequency', 
        clear=True, coorddim=0, valdim=1, maxtraces=1)

    plot3d_red = qt.Plot3D(red_data, name='Laserscan_Counts_Reps', 
        clear=True, coorddims=(1,3), valdim=2)

    plt_yellow_cts = qt.Plot2D(yellow_data, 'b-',
        name='Laserscan_Counts_Y', 
        clear=True, coorddim=1, valdim=2, maxtraces=5, traceofs=5000)

    plt_yellow_frq = qt.Plot2D(yellow_data, 'bO',
        name='Laserscan_Frequency_Y', 
        clear=True, coorddim=0, valdim=1, maxtraces=1)

    plot3d_yellow = qt.Plot3D(yellow_data, name='Laserscan_Counts_Reps_Y', 
        clear=True, coorddims=(1,3), valdim=2)

    if gate_scan:
        gate_x=np.linspace(gate_range[0],gate_range[1],pts)
    ret=True
    t0 = time.time()
    for i in range(pts):
        if (msvcrt.kbhit() and msvcrt.getch()=='x'): 
            ret=False
            break

        # tpulse = 10
        # print "{} seconds of red power...".format(tpulse)
        # stools.apply_awg_voltage('AWG', 'ch4_marker1', 0.52)
        # qt.msleep(tpulse)
        # stools.apply_awg_voltage('AWG', 'ch4_marker1', 0.02)

        if spectral_diffusion:
            m.spectral_diffusion(20, 25, 0.2e-9, 58, 65, 0.01, 20, 1e-9, 
                red_data = red_data, 
                yellow_data = yellow_data,
                data_args=[i, time.time()-t0])

        else:
            ix=i
            if gate_scan: 
                set_gate_voltage(gate_x[i])
                ix=gate_x[i]*45./1000
            m.yellow_red(60, 75, 0.03, 2e-9, 72, 94, 0.02, 20, 3e-9, 
                red_data = red_data, 
                yellow_data = yellow_data,
                data_args=[ix, time.time()-t0])
        
        red_data.new_block()
        yellow_data.new_block()
        plot3d_red.update()
        plot3d_yellow.update()

    if gate_scan:
        set_gate_voltage(0)
    m.mw.set_status('off')
    red_data.close_file()
    yellow_data.close_file()
    plot3d_red.save_png()
    plot3d_yellow.save_png()
    return ret

def gate_scan_with_optimize():
    if repeated_red_scans(gate_scan=True, gate_range=(0,1800),pts=19):
        qt.get_setup_instrument('GreenAOM').set_power(20e-6)
        qt.msleep(120)
        #qt.get_setup_instrument('c_optimiz0r').optimize(xyz_range=[.2,.2,.5], cnt=1, int_time=50, max_cycles=20)
        #qt.get_setup_instrument('c_optimiz0r').optimize(xyz_range=[.05,.1,.2], cnt=1, int_time=50, max_cycles=20)
        qt.get_setup_instrument('optimiz0r').optimize(cnt=1, dims=['z','x','y'], cycles=6, int_time=50)
        qt.get_setup_instrument('GreenAOM').set_power(0e-6)
        repeated_red_scans(gate_scan=True, gate_range=(0,-1800),pts=19)

def fast_gate_scan(name):
    for v in np.linspace(0.,-1,6):
        if (msvcrt.kbhit() and msvcrt.getch()=='c'): 
                break
        set_gate_voltage(v)
        qt.instruments['counters'].set_is_running(True)
        qt.instruments['YellowAOM'].turn_on()
        while qt.instruments['adwin'].get_countrates()[0]<3000:
            if (msvcrt.kbhit() and msvcrt.getch()=='q'): 
                break
            print 'countrates:',qt.instruments['adwin'].get_countrates()[0]
            qt.msleep(0.1)
        qt.instruments['YellowAOM'].turn_off()

        vname=name+'_{:.1f}V'.format(v*45.)
        print 'Running scan ', vname
        single_scan(vname)
        qt.msleep(1)

def single_scan(name):
    m = Scan()
    m.name=name
    do_MW=True
    if do_MW:
        m.mw.set_power(-7)
        m.mw.set_frequency(2.809e9)
        m.mw.set_iq('off')
        m.mw.set_pulm('off')
        m.mw.set_status('on')

    m.red_scan(39, 70, voltage_step=0.02, integration_time_ms=20, power = 0.2e-9)  #0.6e-9
    #m.yellow_red(0,30, 0.02, 0.3e-9, 65, 75, 0.02, 20, 0.5e-9)
    #m.yellow_scan(0, 30, power = 2e-9, voltage_step=0.02, voltage_step_scan=0.02)
    # m.oldschool_red_scan(55, 75, 0.01, 20, 0.5e-9)

    if do_MW:
        m.mw.set_status('off')

def set_gate_voltage(v):
    if v>2. or v<-2.:
        print 'Gate voltage too high:',v
        return False
    return qt.instruments['adwin'].set_dac_voltage(('gate',v))


if __name__ == '__main__':
    qt.get_setup_instrument('GreenAOM').set_power(0e-6)

    single_scan('Pippin_SIL3_MW')
    #fast_gate_scan('Sam_SIL5_Green')
    #green_yellow_during_scan()
    #yellow_ionization_scan(13,20)
    # repeated_red_scans()
    # repeated_red_scans(spectral_diffusion=True)
    #repeated_red_scans(gate_scan=True, gate_range=(0,-1100),pts=12)
    #gate_scan_with_c_optimize()
'''