
import numpy as np
import pylab as plt

adwin = qt.instruments.get_instruments()['adwin']
nr_points = 1000
values = np.zeros(nr_points)
time_stamp = np.zeros(nr_points)

t0 = time.time()
for i in np.arange(nr_points):
	adwin.start_read_adc (adc_no = adwin.adcs['photodiode'])
	values[i] = adwin.get_read_adc_var ('fpar')[0][1]
	time_stamp[i] = time.time()-t0

fName = time.strftime ('%Y%m%d_%H%M%S')+ '_PDtrace'
f0 = os.path.join('D:/measuring/data/', time.strftime('%Y%m%d'))
directory = os.path.join(f0, fName)

if not os.path.exists(directory):
    os.makedirs(directory)

f = plt.figure()
ax = f.add_subplot(1,1,1)
ax.plot (time_stamp, values, '.b', linewidth = 2)
ax.set_xlabel ('time [s]')
ax.set_ylabel ('photodiode signal [a.u.]')
f.savefig(os.path.join(directory, fName+'.png'))

f = h5py.File(os.path.join(directory, fName+'.hdf5'))
scan_grp = f.create_group('photodiode_trace')
scan_grp.create_dataset('PD_signal', data = values)
scan_grp.create_dataset('time', data = time_stamp)
f.close()

