if objsh.start_glibtcp_client('192.168.0.40', port=12003, nretry=3):
    lt3_remote_ins_server = objsh.helper.find_object('qtlab_lt3_monitor:instrument_server')
    lt3_helper = qt.instruments.create('lt3_helper', 'Remote_Instrument', remote_name = 'lt3_measurement_helper',inssrv=lt3_remote_ins_server)

physical_adwin_lt3 = qt.instruments.create('physical_adwin_lt3','ADwin_Pro_II', address=337)