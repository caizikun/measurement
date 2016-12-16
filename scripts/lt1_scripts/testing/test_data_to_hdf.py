import qt
import measurement.lib.measurement2.measurement as m2
import os

m=m2.Measurement('test_hd_qtdat')

dat = qt.Data(name= m.name+'qtdata', infile=False, inmem=True)
dat.add_coordinate('Voltage [V]')
dat.add_coordinate('Frequency [GHz]')
dat.add_value('Counts [Hz]')
#dat.create_file(filepath=os.path.splitext(m.h5data.filepath())[0]+'.dat')
plt = qt.Plot2D(dat, 'rO', coorddim=1, valdim=2, clear=True)

plt.add_data(dat,coorddim=1, valdim=0, right=True)

for i in range(100):

    dat.add_data_point(i,i**2,sqrt(i))

m.h5data.create_datagroup_from_qtdata(dat)
m.finish()