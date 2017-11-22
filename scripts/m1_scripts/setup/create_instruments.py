###############################
#                M1
###############################


physical_adwin = qt.instruments.create('physical_adwin','ADwin_Pro_II',
        address=1,processor_type=1012)

from measurement.lib.config import adwins as adwinscfg
adwin = qt.instruments.create('adwin', 'adwin', 
                 adwin = qt.instruments['physical_adwin'], 
                 processes = adwinscfg.config['adwin_m1_processes'],
                 default_processes=['counter', 'set_dac', 'set_dio', 'linescan'], 
                 dacs=adwinscfg.config['adwin_m1_dacs'], 
                 tags=['virtual'],
                 process_subfolder = 'adwin_pro_2_m1')

AWG = qt.instruments.create('AWG', 'Tektronix_AWG5014_09', 
    address='TCPIP0::192.168.0.111::inst0::INSTR', 
    reset=False, numpoints=1e3)

wavemeter = qt.instruments.create('wavemeter','WSU_WaveMeter')

SGS100A_1 = qt.instruments.create('SGS100A_1', 'RS_SGS100A', address='TCPIP0::192.168.0.116', reset=False,max_cw_pwr = -15) #still think of maximum power allowed
SGS100A_2 = qt.instruments.create('SGS100A_2', 'RS_SGS100A', address='TCPIP0::192.168.0.115', reset=False,max_cw_pwr = -10)

powermeter = qt.instruments.create('powermeter', 'Thorlabs_PM100D',
    address='USB0::0x1313::0x8072::P2005677::INSTR')

# AOM and laser control
GreenAOM  = qt.instruments.create('GreenAOM', 'AOM')            #Direct current modulation of laser, but can probably use aom instrument?
NewfocusAOM  = qt.instruments.create('NewfocusAOM', 'AOM')
DLProAOM  = qt.instruments.create('DLProAOM', 'AOM')

#counters
counters = qt.instruments.create('counters', 'counters_via_adwin',adwin='adwin')
 

master_of_space = qt.instruments.create('master_of_space', 
        'master_of_space', adwin='adwin', dimension_set='mos_m1')

linescan_counts = qt.instruments.create('linescan_counts', 
        'linescan_counts',  adwin='adwin', mos='master_of_space',
        counters='counters')

scan2d = qt.instruments.create('scan2d', 'scan2d_counts',
         linescan='linescan_counts', mos='master_of_space',
        xdim='x', ydim='y', counters='counters')
 
opt1d_counts = qt.instruments.create('opt1d_counts', 
         'optimize1d_counts', linescan='linescan_counts', 
        mos='master_of_space', counters='counters')

optimiz0r = qt.instruments.create('optimiz0r', 'optimiz0r', opt1d_ins=
        opt1d_counts, mos_ins=master_of_space, dimension_set='m1')

setup_controller = qt.instruments.create('setup_controller',
         'setup_controller',
        use = { 'master_of_space' : 'mos'} )

# Magnet
if 1:
    conex_scanner_Z = qt.instruments.create('conex_scanner_Z', 'NewportConexCC', address = 'COM7') #Previously Com17
    conex_scanner_X = qt.instruments.create('conex_scanner_X', 'NewportConexCC', address = 'COM5') #Previously Com16
    conex_scanner_X.SetPositiveLimit(5.)
    conex_scanner_Y = qt.instruments.create('conex_scanner_Y', 'NewportConexCC', address = 'COM6') #Previously Com18
    conex_scanner_Y.SetPositiveLimit(2.)

### master_of_magnet
    # maxter_of_magnet = qt.instruments.create('master_of_magnet', 'MagnetXaxis', 'MagnetYaxis', 'MagnetZaxis')

# servo controller and power meter
if 1:
    servo_ctrl=qt.instruments.create('ServoController', 'MaestroServoController', address='COM15') #previously COM20
    servo_ctrl.Set_Acceleration(0, 0)
    servo_ctrl.Set_Speed(0, 0)
    PMServo = qt.instruments.create('PMServo','ServoMotor',servo_controller='ServoController', min_pos=3900, max_pos=4800, in_pos=3968, out_pos=4600)
    PMServo.move_out()

# execfile('D:\measuring\measurement\scripts\lt3_scripts\setup_m1.py')

### Keithley 2000 DMM for monitoring temperatures
kei2000 = qt.instruments.create('kei2000', 'Keithley_2000', address = 'GPIB::16::INSTR')
kei2000.set_mode_fres()
#kei2000.set_range(100)
#kei2000.set_nplc(10)
#kei2000.set_trigger_continuous(True)
#kei2000.set_averaging(True)
#kei2000.set_averaging_type('moving')
#kei2000.set_averaging_count(50)

