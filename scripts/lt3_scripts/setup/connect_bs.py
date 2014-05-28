if objsh.start_glibtcp_client('192.168.0.90', port=12003, nretry=3):
    bs_remote_ins_server = objsh.helper.find_object('qtlab_bs_monitor:instrument_server')
    bs_helper = qt.instruments.create('bs_helper', 'Remote_Instrument', remote_name = 'bs_measurement_helper',inssrv=bs_remote_ins_server)
