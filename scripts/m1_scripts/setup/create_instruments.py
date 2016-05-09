

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

SGS100A_1 = qt.instruments.create('SGS100A_1', 'RS_SGS100A', address='TCPIP0::192.168.0.116', reset=False,max_cw_pwr = -5) #still think of maximum power allowed
SGS100A_2 = qt.instruments.create('SGS100A_2', 'RS_SGS100A', address='TCPIP0::192.168.0.115', reset=False,max_cw_pwr = -5)

powermeter = qt.instruments.create('powermeter', 'Thorlabs_PM100D',
    address='USB0::0x1313::0x8072::P2005677::INSTR')

# AOM and laser control
GreenAOM  = qt.instruments.create('GreenAOM', 'AOM')            #Direct current modulation of laser, but can probably use aom instrument?
NewfocusAOM  = qt.instruments.create('NewfocusAOM', 'AOM')
DLProAOM  = qt.instruments.create('DLProAOM', 'AOM')


 
if False:

    counters = qt.instruments.create('counters', 'counters_via_adwin',
            adwin='adwin')
    # counters.set_is_running(True)

    master_of_space = qt.instruments.create('master_of_space', 
            'master_of_space', adwin='adwin', dimension_set='mos_lt3')

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
            opt1d_counts, mos_ins=master_of_space, dimension_set='lt3')

    setup_controller = qt.instruments.create('setup_controller',
             'setup_controller',
            use = { 'master_of_space' : 'mos'} )


    #execfile('D:\measuring\measurement\scripts\lt3_scripts\setup_m1.py')