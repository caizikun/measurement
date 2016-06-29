# Some demo stuff in here, to get the idea

#Hardware
lt1_remote=False

# if not lt1_remote:
physical_adwin = qt.instruments.create('physical_adwin','ADwin_Gold_II',
        address=336)
#physical_adwin_lt2 = qt.instruments.create('physical_adwin_lt2','ADwin_Pro_II',
#        address=352)

# AWG = qt.instruments.create('AWG', 'Tektronix_AWG5014', 
#         address='GPIB::1::INSTR' ,reset=False, numpoints=1e3)

SMB100 = qt.instruments.create('SMB100', 'RS_SMB100', 
        address='GPIB::28::INSTR', reset=False)

#PH_300 = qt.instruments.create('PH_300', 'PicoHarp_PH300')
#TH_260N=qt.instruments.create('TH_260N', 'TimeHarp_TH260N')
powermeter = qt.instruments.create('powermeter','Thorlabs_PM100', address='ASRL5::INSTR')

# MillenniaLaser = qt.instruments.create('MillenniaLaser', 'Millennia_Pro', 
#         address='COM1')

TemperatureController = qt.instruments.create('TemperatureController', 
     'Lakeshore_340', address = 'GPIB::12::INSTR')

AttoPositioner = qt.instruments.create('AttoPositioner', 'Attocube_ANC350')
# Velocity1 = qt.instruments.create('Velocity1', 'NewfocusVelocity', address='GPIB::8::INSTR')

#ivvi = qt.instruments.create('ivvi', 'IVVI', address = 'ASRL1::INSTR', numdacs = 4)
servo_ctrl=qt.instruments.create('ServoController', 'ParallaxServoController', address=3)
ZPLServo=qt.instruments.create('ZPLServo','ServoMotor', servo_controller='ServoController')
PMServo=qt.instruments.create('PMServo','ServoMotor', servo_controller='ServoController')
#qutau = qt.instruments.create('QuTau', 'QuTau') # will give issues when combined with Attocube_ANC350
if not lt1_remote:

    AWG = qt.instruments.create('AWG', 'Tektronix_AWG5014', 
        address='TCPIP0::192.168.0.22::inst0::INSTR', 
        reset=False, numpoints=1e3)
    from measurement.lib.config import adwins as adwinscfg
    adwin = qt.instruments.create('adwin', 'adwin', 
                 adwin = qt.instruments['physical_adwin'], 
                 processes = adwinscfg.config['adwin_lt1_processes'],
                 default_processes=['counter', 'set_dac', 'set_dio', 'linescan'], 
                 dacs=adwinscfg.config['adwin_lt1_dacs'], 
                 tags=['virtual'],
                 process_subfolder = 'adwin_gold_2_lt1')

    
    counters = qt.instruments.create('counters', 'counters_via_adwin',
            adwin='adwin')
    counters.set_avg_periods(1)
    counters.set_integration_time(100)
    counters.set_is_running(True)
    
    master_of_space = qt.instruments.create('master_of_space', 
            'master_of_space', adwin='adwin', dimension_set='mos_lt1')
    master_of_space.set_lt_settings(False)

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
            opt1d_counts, mos_ins=master_of_space, dimension_set='lt1')

    c_optimiz0r = qt.instruments.create('c_optimiz0r', 'convex_optimiz0r', 
        mos_ins=master_of_space, adwin_ins = adwin)
    
  
    GreenAOM = qt.instruments.create('GreenAOM', 'AOM', 
            use_adwin='adwin', use_pm= 'powermeter')
    NewfocusAOM = qt.instruments.create('NewfocusAOM', 'AOM', 
            use_adwin='adwin', use_pm = 'powermeter')         
    MatisseAOM = qt.instruments.create('MatisseAOM', 'AOM', 
            use_adwin='adwin', use_pm = 'powermeter')
    YellowAOM = qt.instruments.create('YellowAOM', 'AOM', 
            use_adwin='adwin', use_pm ='powermeter')
    PulseAOM = qt.instruments.create('PulseAOM', 'AOM', 
            use_adwin='adwin', use_pm ='powermeter')
    
    #laser_scan = qt.instruments.create('laser_scan', 'laser_scan')
     
    setup_controller = qt.instruments.create('setup_controller',
             'setup_controller',
            use = { 'master_of_space' : 'mos'} )
    
if objsh.start_glibtcp_client('192.168.0.80', port=12002, nretry=3):
    remote_ins_server = objsh.helper.find_object('qtlab_lasermeister:instrument_server')
    labjack = qt.instruments.create('labjack', 'Remote_Instrument',
    remote_name='labjack', inssrv=remote_ins_server)
    NewfocusLaser = qt.instruments.create('NewfocusLaser', 'Remote_Instrument',
    remote_name='NewfocusLT1_1', inssrv=remote_ins_server)
    #ivvi = qt.instruments.create('ivvi', 'Remote_Instrument', remote_name='ivvi', inssrv=remote_ins_server)

if objsh.start_glibtcp_client('localhost', port=12003, nretry=2):
    remote_ins_server_mon = objsh.helper.find_object('qtlab_monitor_lt1:instrument_server')
    remote_measurement_helper = qt.instruments.create('remote_measurement_helper', 'Remote_Instrument',
            remote_name='lt1_measurement_helper', inssrv=remote_ins_server_mon)
    
#positioner = qt.instruments.create('positioner', 'NewportAgilisUC2_v2', 
#        address = 'COM14')
#rejecter = qt.instruments.create('rejecter', 'laser_reject0r')


