#
# Do a few calibration runs
#
import pickle


dirname='D:\\measuring\\data\\20151105\\115556_DM_total_curve_PippinSil1_lt3_local_new_dm\\'

if __name__ == '__main__':

	if 1==1:
		# Show the counts
		qt.plots.clear()

		confname = dirname+'dmresults_1_test1.pkl'
		fs = open(confname, 'rb')
		res = pickle.load(fs)
		fs.close()
		plot(res[0][0])
		confname = dirname+'dmresults_2_test1.pkl'
		fs = open(confname, 'rb')
		res = pickle.load(fs)
		fs.close()
		plot(res[0][0])
		confname = dirname+'dmresults_3_test1.pkl'
		fs = open(confname, 'rb')
		res = pickle.load(fs)
		fs.close()
		plot(res[0][0])
		confname = dirname+'dmresults_4_test1.pkl'
		fs = open(confname, 'rb')
		res = pickle.load(fs)
		fs.close()
		plot(res[0][0])


	# Test the mean converged DM shapes
	if 1==0:
		confname = 'dmresults_1_test2_500ms.pkl'
		fs = open(confname, 'rb')
		res = pickle.load(fs)
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
		ncounts = 100
		goodcounts = np.zeros(ncounts)
		for ii in range(0,ncounts):
			cnt = measure_counts()
			print('counts: ' + str(cnt))
			goodcounts[ii] = cnt

		fs = open(confname+'goodcounts.pkl', 'wb')
		res = pickle.dump(goodcounts, fs)
		fs.close()

		# Save the good DM commands
		fname = 'D:\\measuring\\data\\20151105\\115556_DM_total_curve_PippinSil1_lt3_local_new_dm\\goodcmds_500ms_400it'
		dm.save_mirror_surf(fname)


	# Compare the DM commands
	if 1==0:
		ncounts = 100
		fname = 'D:\\measuring\\data\\20151105\\115556_DM_total_curve_PippinSil1_lt3_local_new_dm\\goodcmds_500ms_400it.npz'
		dm.load_mirror_surf(fname)
		goodcounts1 = np.zeros(ncounts)
		for ii in range(0,ncounts):
			cnt = measure_counts()
			print('counts: ' + str(cnt))
			goodcounts1[ii] = cnt


		fname = 'D:\\measuring\\data\\20151105\\115556_DM_total_curve_PippinSil1_lt3_local_new_dm\\goodcmds_100ms_5000it.npz'
		dm.load_mirror_surf(fname)
		goodcounts2 = np.zeros(ncounts)
		for ii in range(0,ncounts):
			cnt = measure_counts()
			print('counts: ' + str(cnt))
			goodcounts2[ii] = cnt

		print('Mean1: '+str(np.mean(goodcounts1)))
		print('Mean2: '+str(np.mean(goodcounts2)))


		fs = open('goodcounts_cmp_bests_100ms_vs_500ms.pkl', 'wb')
		res = pickle.dump((goodcounts1, goodcounts2), fs)
		fs.close()



# Every half an hour
# optimiz0r.optimize(dimanesion = [x,y,z], int_time =100 , cnt=2)
# Good to know:
#dm.plot_mirror_surface()

