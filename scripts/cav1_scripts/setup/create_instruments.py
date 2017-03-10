
physical_adwin = qt.instruments.create('physical_adwin','ADwin_Pro_II',
        address=1)


adwin = qt.instruments.create('adwin', 'adwin_cav1', physical_adwin='physical_adwin')

wavemeter = qt.instruments.create('wavemeter','WS600_WaveMeter')
wavemeter.set_active_channel(2)
broadcast0r = qt.instruments.create('broadcast0r', 'broadcast0r')
broadcast0r.add_broadcast('wm_ch2', lambda: wavemeter.Get_Frequency(2), lambda x: physical_adwin.Set_FPar(42, (x-470.40)*1e3 ))
broadcast0r.start()


jpe = qt.instruments.create ('jpe', 'JPE_CADM')

counters = qt.instruments.create('counters', 'counters_via_adwin', adwin='adwin')

master_of_space = qt.instruments.create('master_of_space','master_of_space', adwin='adwin', dimension_set = 'mos_cav1')

linescan_counts = qt.instruments.create('linescan_counts', 
        'linescan_counts',  adwin='adwin', mos='master_of_space',
        counters='counters')

setup_controller = qt.instruments.create('setup_controller',
         'setup_controller',
        use = { 'master_of_space' : 'mos'} )

scan2d = qt.instruments.create('scan2d', 'scan2d_counts',
         linescan='linescan_counts', mos='master_of_space',
        xdim='x', ydim='y', counters='counters', setup_controller='setup_controller')

opt1d_counts = qt.instruments.create('opt1d_counts', 
         'optimize1d_counts', linescan='linescan_counts', 
        mos='master_of_space', counters='counters')

optimiz0r = qt.instruments.create('optimiz0r', 'optimiz0r', opt1d_ins=
        opt1d_counts, mos_ins=master_of_space, dimension_set='cav1')


newfocus1 = qt.instruments.create('newfocus1', 'NewfocusVelocity', address='GPIB0::10::INSTR')

master_of_cavity = qt.instruments.create('master_of_cavity','master_of_cavity', 
        jpe= 'jpe', adwin='adwin', laser = 'newfocus1', use_cfg = True)

master_of_char_cavity = qt.instruments.create('master_of_char_cavity','master_of_char_cavity', adwin='adwin')

cavity_scan_manager = qt.instruments.create('cavity_scan_manager', 'cavity_scan_manager', adwin='adwin', physical_adwin='physical_adwin')

# instruments for the cavity GUI
# cavity_scan_manager = qt.instruments.create('cavity_scan_manager', 'cavity_scan_manager', )
# cavity_exp_manager = qt.instruments.create('cavity_exp_manager','cavity_exp_manager')



#cyclopean_cavity_laser_scan = qt.instruments.create('cyclopean_cavity_laser_scan', 'cyclopean_cavity_laser_scan', adwin = adwin)

#point_mngr_jpe = qt.instruments.create ('xy_point_jpe', 'xy_point_jpe', adwin = physical_adwin_cav1, moc=master_of_cavity)
#xy_scan_jpe = qt.instruments.create ('xy_scan_jpe', 'xy_scan_jpe', adwin = physical_adwin_cav1, moc=master_of_cavity, point_manager = point_mngr_jpe)

#lockin = qt.instruments.create('lockin','SR830', address='GPIB0::9::INSTR')
cavity_slow_lock = qt.instruments.create('cavity_slow_lock','CavitySlowLock',adwin = 'adwin',master_of_cavity = 'master_of_cavity',control_adc_no=32, value_adc_no=16)