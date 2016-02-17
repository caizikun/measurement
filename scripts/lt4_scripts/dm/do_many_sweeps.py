#
# Do a few calibration runs
#
import pickle



if __name__ == '__main__':

	mesid = '_test2_500ms'

	#dm.set_flat_dm()
	dm.set_cur_voltages(goodcmds)
	extremum_seek_opts  = Struct()
	extremum_seek_opts.h      = 0.99
	extremum_seek_opts.A1     = 0.1/2*4
	extremum_seek_opts.A2     = 0.1/2*4
	extremum_seek_opts.gamma  = 5e-6
	extremum_seek_opts.maxfev = 400
	extremum_seek_opts.nact   = 160
	execfile('DM_sweep_actuators2.py')

	fs = open('dmresults_1'+mesid+'.pkl', 'wb')
	pickle.dump((result, extremum_seek_opts), fs)
	fs.close()
	

	#dm.set_flat_dm()
	dm.set_cur_voltages(goodcmds)
	extremum_seek_opts  = Struct()
	extremum_seek_opts.h      = 0.99
	extremum_seek_opts.A1     = 0.1/2
	extremum_seek_opts.A2     = 0.1/2
	extremum_seek_opts.gamma  = 5e-6
	extremum_seek_opts.maxfev = 400
	extremum_seek_opts.nact   = 160
	execfile('DM_sweep_actuators2.py')

	fs = open('dmresults_2'+mesid+'.pkl', 'wb')
	pickle.dump((result, extremum_seek_opts), fs)
	fs.close()

	if 1==0:
		#dm.set_flat_dm()
		dm.set_cur_voltages(goodcmds)
		extremum_seek_opts  = Struct()
		extremum_seek_opts.h      = 0.99
		extremum_seek_opts.A1     = 0.1/2*12
		extremum_seek_opts.A2     = 0.1/2*12
		extremum_seek_opts.gamma  = 5e-6
		extremum_seek_opts.maxfev = 400
		extremum_seek_opts.nact   = 160
		execfile('DM_sweep_actuators2.py')

		fs = open('dmresults_3'+mesid+'.pkl', 'wb')
		pickle.dump((result, extremum_seek_opts), fs)
		fs.close()

		#dm.set_flat_dm()
		dm.set_cur_voltages(goodcmds)
		extremum_seek_opts  = Struct()
		extremum_seek_opts.h      = 0.99
		extremum_seek_opts.A1     = 0.1/2*12
		extremum_seek_opts.A2     = 0.1/2*12
		extremum_seek_opts.gamma  = 1e-6
		extremum_seek_opts.maxfev = 400
		extremum_seek_opts.nact   = 160
		execfile('DM_sweep_actuators2.py')

		fs = open('dmresults_4'+mesid+'.pkl', 'wb')
		pickle.dump((result, extremum_seek_opts), fs)
		fs.close()



	# Test the mean converged DM shapes
	if 1==0:
		confname = 'dmresults_1_test0.pkl'
		fs = open(confname, 'rb')
		res = pickle.open(fs)
		fs.close()

		# resu = (y, u, s, e, u, u_i, d)
		resdata = res[0]
		y   = resdata[0]
		u   = resdata[1]
		u_i = resdata[5]

		# Apply the converged commands (without dither)
		goodcmds = u_i[-1,:]
		dm.set_cur_voltages(goodcmds)
		# Collect photon counts
