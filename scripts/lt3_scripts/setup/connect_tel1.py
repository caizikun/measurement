if objsh.start_glibtcp_client('192.168.0.130', port=12003, nretry=3):
    tel1_remote_ins_server = objsh.helper.find_object('qtlab_tel1:instrument_server')
    print tel1_remote_ins_server
    tel1_helper = qt.instruments.create('tel1_helper', 'Remote_Instrument', remote_name = 'tel1_measurement_helper',inssrv=tel1_remote_ins_server)

