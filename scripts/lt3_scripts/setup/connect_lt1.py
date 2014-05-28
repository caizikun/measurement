if objsh.start_glibtcp_client('192.168.0.20', port=12003, nretry=3):
    lt1_remote_ins_server = objsh.helper.find_object('qtlab_monitor_lt1:instrument_server')
    lt1_helper = qt.instruments.create('lt1_helper', 'Remote_Instrument', remote_name = 'lt1_measurement_helper',inssrv=lt1_remote_ins_server)
