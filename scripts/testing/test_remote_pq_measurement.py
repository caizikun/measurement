if objsh.start_glibtcp_client('192.168.0.90', port=12002, nretry=1):
    remote_ins_server = objsh.helper.find_object('qtlab_bs:instrument_server')
    bs_meas = qt.instruments.create('bs_meas', 'Remote_Instrument',
            remote_name='remote_measurement_helper', inssrv=remote_ins_server)
    remote_cmd=objsh.helper.find_object('qtlab_bs:python_server')