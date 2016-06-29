# Some demo stuff in here, to get the idea

physical_adwin = qt.instruments.create('physical_adwin','ADwin_Gold_II',
                 address=336)
adwin = qt.instruments.create('adwin', 'adwin_lt1', 
        physical_adwin='physical_adwin', init=False, use_cfg=False)

physical_adwin_lt2 = qt.instruments.create('physical_adwin_lt2','ADwin_Pro_II',
        address=352)

# Velocity1 = qt.instruments.create('Velocity1', 'NewfocusVelocity', 
#             address='GPIB::8::INSTR')


rotator = qt.instruments.create('rotator', 'NewportAgilisUC', 
        address = 'COM9', ins_type='UC8')
rejecter = qt.instruments.create('rejecter', 'laser_reject0r_v2', rotator='rotator',rotation_config_name='waveplates_lt1',
        adwin='adwin')

lt1_measurement_helper = qt.instruments.create('lt1_measurement_helper', 'remote_measurement_helper', exec_qtlab_name = 'qtlab_lt1')


if objsh.start_glibtcp_client('192.168.0.80', port=12002, nretry=3):
    remote_ins_server = objsh.helper.find_object('qtlab_lasermeister:instrument_server')

    pidvelocity1 = qt.instruments.create('pidvelocity1', 'Remote_Instrument',
        remote_name='pid_lt1_newfocus1', inssrv=remote_ins_server)
    #pidvelocity2 = qt.instruments.create('pidvelocity2', 'Remote_Instrument',
    #    remote_name='pid_lt1_newfocus2', inssrv=remote_ins_server)
    pidyellow = qt.instruments.create('pidyellow', 'Remote_Instrument',
        remote_name='pidyellow', inssrv=remote_ins_server)
    #ivvi = qt.instruments.create('ivvi', 'Remote_Instrument', remote_name='ivvi', inssrv=remote_ins_server)

#ivvi = qt.instruments.create('ivvi', 'IVVI', address = 'ASRL1::INSTR', numdacs = 4)
#adwin_lt2_monit0r = qt.instruments.create('adwin_lt2_monit0r', 
#    'adwin_monit0r', physical_adwin='physical_adwin_lt2')
#adwin_lt2_monit0r.add_fpar(46, 'Velocity1 Frequency')
#adwin_lt2_monit0r.add_fpar(47, 'Velocity2 Frequency')
#adwin_lt2_monit0r.add_fpar(42, 'Yellow Frequency')
#adwin_lt2_monit0r.start()
