import msvcrt
import time
import qt
import os
import numpy as np
import measurement.lib.config.adwins as adwins_cfg

class LaserFrequencyScan:

    mprefix = 'LaserFrequencyScan'    

    def __init__(self, name):
        self.name = name
        
        self.set_laser_power = None
        self.set_repump_power = None
        self.set_laser_voltage = None   # callable with voltage as argument
        self.get_frequency = None       # callable with WM channel as argument
        self.get_counts = None          # callable with integration time as argument,
                                        # returning an array (one val per
                                        # channel)
        self.get_laser_voltage = None

    def repump_pulse(self, stabilizing_time=0.01):
        qt.msleep(stabilizing_time)
        self.set_repump_power(self.repump_power)
        qt.msleep(self.repump_duration)
        self.set_repump_power(0)
        qt.msleep(stabilizing_time)
    
    def scan_to_voltage(self, target_voltage, get_voltage_method, set_voltage_method, 
            voltage_step=0.05, dwell_time=0.01):
        cur_v = get_voltage_method()

        if ((target_voltage > self.max_v - 0.3) or (target_voltage < self.min_v + 0.3)):
            print 'WARNING: target voltage ', target_voltage ,' is out of range. Need: ', self.min_v + 0.3, '< target voltage < ' , self.max_v-0.3
            print 'setting to min or max instead'
            if target_voltage < self.min_v+0.3:
                target_voltage = self.min_v+0.3
            elif target_voltage > self.max_v - 0.3:
                target_voltage = self.max_v - 0.3
            print 'new target voltage', target_voltage

        print 'scanning from ', cur_v, ' to ', target_voltage
        steps = np.arange(get_voltage_method(), target_voltage, voltage_step)
        steps = np.append(steps,target_voltage)
        for s in steps:
            if (msvcrt.kbhit() and msvcrt.getch()=='q'): 
                break
            set_voltage_method(s)
            qt.msleep(dwell_time)
        print 'reached voltage ', get_voltage_method()

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
        
        print 'scan to frequency', f
        
        v = get_voltage()

        success = False

        set_power(power)
        # print self.max_v
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
        else:
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

                plt_frq = qt.Plot2D(data, ('bO' if suffix=='yellow' else 'rO'),
                    name='Laserscan_Frequency' + ('_{}'.format(suffix) if suffix != None else ''), 
                    clear=True, coorddim=0, valdim=1, maxtraces=1)
            else:
                data_obj_supplied = True

        print 'scan_to_frequency'
        self.scan_to_frequency(start_f, **kw)
        #print 'get_voltage'
        v = get_voltage()
        #print 'set_power'
        set_power(power)
        while ((v < self.max_v - 0.3) and (v > self.min_v + 0.3)):
            if (msvcrt.kbhit() and msvcrt.getch()=='q'): 
                break

            set_voltage(v)
            #qt.msleep(stabilizing_time)

            cur_f = self.get_frequency(wm_channel)
            if cur_f < -300: #######SvD: I changed this -100 -> -300. 
                continue

            if (stop_f > start_f) and (cur_f > stop_f):
                break
            elif (stop_f <= start_f) and (cur_f < stop_f):
                break  

            cts = float(self.get_counts(integration_time_ms)[self.counter_channel]) #/ \
                #(integration_time_ms*1e-3)

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

    def single_line_scan_v(self, start_v, stop_v, 
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

                plt_frq = qt.Plot2D(data, ('bO' if suffix=='yellow' else 'rO'),
                    name='Laserscan_Frequency' + ('_{}'.format(suffix) if suffix != None else ''), 
                    clear=True, coorddim=0, valdim=1, maxtraces=1)
            else:
                data_obj_supplied = True

        print 'scan to voltage'
        self.scan_to_voltage(start_v, get_voltage, set_voltage)
        qt.msleep(0.1)
        #print 'get_voltage'
        v = get_voltage()
        #print 'set_power'
        set_power(power)
        print 'starting laser scan ...' 
        while ((v < self.max_v - 0.3) and (v > self.min_v + 0.3)):
            if (msvcrt.kbhit() and msvcrt.getch()=='q'): 
                break
            set_voltage(v)
            qt.msleep(stabilizing_time)

            cur_f = self.get_frequency(wm_channel)
            cur_v = get_voltage()
            if cur_f < -300: #######SvD: I changed this -100 -> -300. 
                continue

            if (stop_v > start_v) and (cur_v > stop_v):
                break
            elif (stop_v <= start_v) and (cur_v < stop_v):
                break  

            cts = float(self.get_counts(integration_time_ms)[self.counter_channel]) #/ \
                #(integration_time_ms*1e-3)

            v = v + voltage_step * np.sign(stop_v - cur_v) 

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

    def __init__(self, name='LT1', red_labjack_dac_nr=6, yellow_labjack_dac_nr = 0, red_wm_channel = 6, yellow_wm_channel = 2):
        LaserFrequencyScan.__init__(self, name)
        
        self.adwin = qt.get_setup_instrument('adwin')
        self.physical_adwin=qt.get_setup_instrument('physical_adwin')
        self.mw = qt.get_setup_instrument('SMB100')
        self.labjack= qt.get_setup_instrument('labjack')

        self.set_red_laser_voltage = lambda x: self.labjack.__dict__['set_bipolar_dac'+str(red_labjack_dac_nr)](x)
        self.get_red_laser_voltage = lambda : self.labjack.__dict__['get_bipolar_dac'+str(red_labjack_dac_nr)]()
        self.set_red_power = qt.get_setup_instrument('NewfocusAOM').set_power


        self.set_yellow_laser_voltage = lambda x: self.labjack.__dict__['set_bipolar_dac'+str(yellow_labjack_dac_nr)](x)
        self.get_yellow_laser_voltage = lambda : self.labjack.__dict__['get_bipolar_dac'+str(yellow_labjack_dac_nr)]()
        self.set_yellow_power = qt.get_setup_instrument('YellowAOM').set_power

        self.set_repump_power = qt.get_setup_instrument('GreenAOM').set_power

        self.get_frequency = lambda x : self.physical_adwin.Get_FPar(x+40)
        self.get_counts = lambda x: self.adwin.get_countrates()#self.adwin.measure_counts
        self.counter_channel = 0
        self.red_wm_channel = red_wm_channel
        self.red_voltage_frequency_relation_sign = -1


        self.yellow_voltage_frequency_relation_sign = 1
        self.yellow_wm_channel = yellow_wm_channel

        self.max_v = 9.5
        self.min_v = -9.5

        self.set_gate_voltage = lambda x: qt.get_setup_instrument('ivvi').set_dac3(x)

    def yellow_scan(self, start_f, stop_f, power=0.5e-9, **kw):
        voltage_step = kw.pop('voltage_step', 0.01)

        self.single_line_scan(start_f, stop_f,
            voltage_step = voltage_step, 
            integration_time_ms=50, 
            power=power,
            suffix = 'yellow', 
            set_voltage = self.set_yellow_laser_voltage,
            get_voltage = self.get_yellow_laser_voltage,
            wm_channel = self.yellow_wm_channel,
            voltage_frequency_relation_sign = self.yellow_voltage_frequency_relation_sign,
            set_power = self.set_yellow_power,
            **kw)

    def yellow_ionization_scan(self, start_f, stop_f, power=70e-9, **kw):
        self.single_line_scan(start_f, stop_f,
            voltage_step=0.03, integration_time_ms=5, power=power,
            suffix = 'yellow', 
            set_voltage = self.set_yellow_laser_voltage,
            get_voltage = self.get_yellow_laser_voltage,
            wm_channel = self.yellow_wm_channel,
            voltage_frequency_relation_sign = self.yellow_voltage_frequency_relation_sign,
            set_power = self.set_yellow_power,
            save = False)

    def red_scan(self, start_f, stop_f, power=0.5e-9, **kw):
        voltage_step = kw.pop('voltage_step', 0.005)
        integration_time_ms = kw.pop('integration_time_ms', 50)
        print 'scanning from ', start_f,' GHz to ', stop_f,' GHz'
        self.single_line_scan(start_f, stop_f, voltage_step, integration_time_ms, power, **kw)

    def red_scan_v(self, start_v, stop_v, power=0.5e-9, **kw):
        voltage_step = kw.pop('voltage_step', 0.005)
        integration_time_ms = kw.pop('integration_time_ms', 50)
        print 'scanning from ', start_v,' V to ', stop_v,' V'
        self.single_line_scan_v(start_v, stop_v, voltage_step, integration_time_ms, power, **kw)

    def red_ionization_scan(self, start_f, stop_f, power=30e-9, **kw):
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

    m.mw.set_power(-7)
    m.mw.set_frequency(2.878e9)
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
                m.set_gate_voltage(gate_x[i])
                ix=gate_x[i]*45./1000
            m.yellow_red(0, 20, 0.03, 2e-9, 40, 90, 0.02, 20, 0.3e-9, 
                red_data = red_data, 
                yellow_data = yellow_data,
                data_args=[ix, time.time()-t0])
        #def yellow_red(self, y_start, y_stop, y_step ,y_power, r_start, r_stop, r_step, r_int, r_power, **kw):

        plt_red_cts.update()
        plt_red_frq.update()

        plt_yellow_cts.update()
        plt_yellow_frq.update() 


        red_data.new_block()
        yellow_data.new_block()
        plot3d_red.update()
        plot3d_yellow.update()

    if gate_scan:
        m.set_gate_voltage(0)
    m.mw.set_status('off')
    red_data.close_file()
    yellow_data.close_file()
    plot3d_red.save_png()
    plot3d_yellow.save_png()
    return ret

def repeated_red_scans_hannes(**kw):
    m = Scan()


    pts = kw.pop('pts', 5)
    green_powers = kw.pop('green_powers', [0.0e-6])
    red_powers = kw.pop('red_powers', [2.e-9]*pts)
    pts_tot = len(green_powers)*len(red_powers)

    m.mw.set_power(-20)
    m.mw.set_frequency(2.817e9)
    m.mw.set_iq('off')
    m.mw.set_pulm('off')
    m.mw.set_status('on')

    red_data = qt.Data(name = 'LaserScansGreenRepump_membrane')
    red_data.add_coordinate('Voltage (V)')
    red_data.add_coordinate('Frequency (GHz)')
    red_data.add_coordinate('Counts (Hz)')
    red_data.add_coordinate('index')
    red_data.add_coordinate('green power (W)')
    red_data.add_coordinate('red power (W)')
    red_data.add_coordinate('start time')
    red_data.create_file()

    plt_red_cts = qt.Plot2D(red_data, 'r-',
        name='Laserscan_Counts', 
        clear=True, coorddim=1, valdim=2, maxtraces=5, traceofs=5000)

    plt_red_frq = qt.Plot2D(red_data, 'rO',
        name='Laserscan_Frequency', 
        clear=True, coorddim=0, valdim=1, maxtraces=1)

    plot3d_red = qt.Plot3D(red_data, name='Laserscan_Counts_Reps', 
        clear=True, coorddims=(1,3), valdim=2)

    print 'starting a scan with ', pts_tot ,'points'
    print 'red', red_powers
    print 'green', green_powers

    k = 0 
    ret=True
    t0 = time.time()
    for i,g_p in enumerate(green_powers):

        for j,r_p in enumerate(red_powers):
            qt.msleep(2)
            if (msvcrt.kbhit() and msvcrt.getch()=='q'): 
                ret=False
                break

            k+=1

            print ' i ', i, ' j ',j
            print ' green ', g_p, ' red ', r_p
            #YellowAOM.set_power(250e-9)
            GreenAOM.set_power(200e-6) # previously (<18-05-2015) set to 70uW; not possible with current alignment
            optimiz0r.optimize(dims = ['z','y','x'], cycles = 1, int_time = 50) 
            qt.msleep(1)
            #YellowAOM.set_power(00.0e-9)
            GreenAOM.set_power(g_p)

            if np.mod(k,2)==1:
                start_f = -10
                stop_f = 45
            else:
                start_f = 45
                stop_f = -10

            m.red_scan(start_f, stop_f, voltage_step=0.01, integration_time_ms=10, power = r_p,
                data = red_data,
                data_args=[k, g_p, r_p, time.time()-t0]
                )
            print 'done red scan nr ', k, ' out of ', pts_tot
            red_data.new_block()
            plt_red_cts.update()
            plt_red_frq.update()
            plot3d_red.update()

            qt.msleep(1)
            if (msvcrt.kbhit() and msvcrt.getch()=='q'): 
                ret=False
                break

            GreenAOM.set_power(200e-6)
            qt.msleep(5)
            # qt.instruments['optimiz0r'].optimize(dims=['x','y','z','y','x'], cnt=1, int_time=50, cycles=1)
            GreenAOM.set_power(0.0e-6)


    m.mw.set_status('off')
    red_data.close_file()

    plot3d_red.save_png()

    return ret

def set_gate_voltage(v):
    if v>2000. or v<-2000.:
        print 'Gate voltage too high:',v
        return False
    return qt.instruments['ivvi'].set_dac3(v)

def fast_gate_scan(name, vmax):
    for v in np.linspace(0.,vmax,6):
        if (msvcrt.kbhit() and msvcrt.getch()=='c'): 
                break
        set_gate_voltage(v)
        qt.instruments['counters'].set_is_running(True)
        qt.instruments['YellowAOM'].set_power(30e-9)
        while qt.instruments['adwin'].get_countrates()[0]<1000:
            if (msvcrt.kbhit() and msvcrt.getch()=='q'): 
                break
            #print 'countrates:',qt.instruments['adwin'].get_countrates()[0]
            qt.msleep(0.1)
        print 'countrates:',qt.instruments['adwin'].get_countrates()[0]
        qt.instruments['YellowAOM'].turn_off()

        vname=name+'_{:.1f}V'.format(v*45.e-3)
        print 'Running scan ', vname
        single_scan(vname)
        qt.msleep(1)
    set_gate_voltage(0)

def gate_scan_with_c_optimize():
    if repeated_red_scans(gate_scan=True, gate_range=(0,1200),pts=19):
        qt.get_setup_instrument('GreenAOM').set_power(20e-6)
        qt.get_setup_instrument('c_optimiz0r').optimize(xyz_range=[.2,.2,.5], cnt=1, int_time=50, max_cycles=20)
        qt.get_setup_instrument('c_optimiz0r').optimize(xyz_range=[.05,.1,.2], cnt=1, int_time=50, max_cycles=20)
        qt.get_setup_instrument('optimiz0r').optimize(cnt=1, dims=['x','y'], cycles=3, int_time=50)
        qt.get_setup_instrument('GreenAOM').set_power(0e-6)
        repeated_red_scans(gate_scan=True, gate_range=(0,-1200),pts=19)

def single_scan(name):
    m = Scan(name)

    MW = False

    GreenAOM.set_power(100e-6) # previously (<18-05-2015) set to 70uW; not possible with current alignment
    # optimiz0r.optimize(dims = ['z','x','y'], cycles = 1, int_time = 100) 
    qt.msleep(0.5)
    GreenAOM.set_power(2.e-6)

    if MW:
        m.mw.set_power(-15)
        m.mw.set_frequency(2.817e9) # 2.838e9 for SIL3
        m.mw.set_iq('off')
        m.mw.set_pulm('off')
        m.mw.set_status('on')
    m.red_scan(60,100, voltage_step=0.005, integration_time_ms=10, power = 100.e-9)
    # m.red_scan(48,80, voltage_step=0.02, integration_time_ms=10, power = 2e-9)
    #m.yellow_red(62, 80, 0.02, 0.5e-9, 74, 92, 0.02, 20, 3e-9)
    #m.yellow_scan(5, 20, power = 2e-9, voltage_step=0.02, voltage_step_scan=0.03)
    # m.oldschool_red_scan(55, 75, 0.01, 20, 0.5e-9)

    m.mw.set_status('off')

def single_scan_v(name):
    m = Scan(name)

    MW = False

    GreenAOM.set_power(100e-6) # previously (<18-05-2015) set to 70uW; not possible with current alignment
    optimiz0r.optimize(dims = ['z','x','y'], cycles = 1, int_time = 100) 
    qt.msleep(0.5)
    GreenAOM.set_power(2.5e-6)

    if MW:
        m.mw.set_power(-15)
        m.mw.set_frequency(2.817e9) # 2.838e9 for SIL3
        m.mw.set_iq('off')
        m.mw.set_pulm('off')
        m.mw.set_status('on')
    m.red_scan_v(-9,9, voltage_step=0.01, integration_time_ms=10, power = 47.e-9)

    # m.red_scan(48,80, voltage_step=0.02, integration_time_ms=10, power = 2e-9)
    #m.yellow_red(62, 80, 0.02, 0.5e-9, 74, 92, 0.02, 20, 3e-9)
    #m.yellow_scan(5, 20, power = 2e-9, voltage_step=0.02, voltage_step_scan=0.03)
    # m.oldschool_red_scan(55, 75, 0.01, 20, 0.5e-9)

    m.mw.set_status('off')


def debug_scan(name):

    m = Scan(name)
    m.yellow_scan(4, 6, 50e-9, voltage_step=0.03)

def long_scan(name):
    wls = np.linspace(637.26,636.62,9)
    #wls = np.linspace(637.26,637.22,2)
    print wls
    fs_centre = np.linspace(-230,250,9)
    #fs_centre = np.linspace(-230,-200,2)
    print fs_centre

    for ii,wl in enumerate(wls):
        NewfocusLaser.set_wavelength(wl)

        m = Scan(name+str(int(fs_centre[ii])))

        MW = False 

        GreenAOM.set_power(600e-6) # previously (<18-05-2015) set to 70uW; not possible with current alignment
        # opt1d_ins.run(dimension='z', scan_length=5, nr_of_points=31, pixel_time=100, return_data=False, gaussian_fit=True)
        # mos_ins.set_z(mos_ins.get_z()+0.6)
        # optimiz0r.optimize(dims = ['x','y'], cycles = 1, int_time = 100) 
        qt.msleep(3)
        GreenAOM.set_power(2.e-6)

        if MW:
            m.mw.set_power(-15)
            m.mw.set_frequency(2.817e9) # 2.838e9 for SIL3
            m.mw.set_iq('off')
            m.mw.set_pulm('off')
            m.mw.set_status('on')


        m.red_scan_v(9,-9, voltage_step=0.005, integration_time_ms=10, power = 100.e-9)
       
        m.mw.set_status('off')


if __name__ == '__main__':
    #qt.get_setup_instrument('GreenAOM').set_power(.0e-6)
    # repeated_red_scans_hannes()
    single_scan('membrane_Harvard_g_2uW_r_100nW')
    #fast_gate_scan('The111no1_Sil8_dac3_on22',2000)
    #qt.get_setup_instrument('GreenAOM').set_power(10e-6)
    # qt.instruments['optimiz0r'].optimize(dims=['x','y','z','y','x'], cnt=1, int_time=50, cycles=3)
    #qt.get_setup_instrument('GreenAOM').set_power(0e-6)
    #fast_gate_scan('The111no1_Sil8_dac3_on24',2000)
    
    #repeated_red_scans_hannes(pts = 3, green_powers = [5.e-6], red_powers = np.linspace(50e-9,150.e-9,3))

    #green_yellow_during_scan()
    #yellow_ionization_scan(13,20)
    # repeated_red_scans(spectral_diffusion=True)
    #
    #repeated_red_scans(gate_scan=True, gate_range=(0,50),pts=2)
    #gate_scan_with_c_optimize()

    #long_scan('membrane_Harvard_longscan')
    #single_scan_v('membrane_scanv_test_g_2p5uW_r_49nW')