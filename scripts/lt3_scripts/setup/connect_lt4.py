if objsh.start_glibtcp_client('192.168.0.50', port=12003, nretry=3):
    tel1_remote_ins_server = objsh.helper.find_object('qtlab_lt4_monitor:instrument_server')
    print tel1_remote_ins_server
    tel1_helper = qt.instruments.create('tel1_helper', 'Remote_Instrument', remote_name = 'lt4_measurement_helper',inssrv=tel1_remote_ins_server)

