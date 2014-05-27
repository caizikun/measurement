if objsh.start_glibtcp_client('192.168.0.90', port=12002, nretry=3):
    bs_remote_ins_server = objsh.helper.find_object('qtlab_bs:instrument_server')
    bs_helper = qt.instruments.create('bs_helper', 'Remote_Instrument',remote_name = 'bs_measurement_helper',inssrv=bs_remote_ins_server)
    HH_bs = qt.instruments.create('HH_bs', 'Remote_Instrument',remote_name='HH_400', inssrv=bs_remote_ins_server)
    bs_python_server = objsh.helper.find_object('qtlab_bs:python_server')

def start_bs_counter():
	bs_helper.set_is_running(True)
	print 'Countrates:', HH_bs.get_CountRate1()
	bs_python_server.cmd("execfile(r'D:/measuring/measurement/scripts/bs_scripts/HH_counter_fast.py')", signal=True)

def stop_bs_counter():
	#bs_helper.set_is_running(False)
	bs_python_server.cmd("msvcrt.putch('q')", signal=True)