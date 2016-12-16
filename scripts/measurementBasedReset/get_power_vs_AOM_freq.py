import numpy as np
from analysis.lib.fitting import fit, common
reload(common)
import os,sys,time
import qt
import types
from lib import config
import logging

chan = 'yellow_aom_frq'
vs = np.arange(6,9,0.1)
pows = np.zeros(np.shape(vs)[0], dtype = np.float64)

power_meter =  qt.instruments.get('powermeter')

old_v = adwin.get_dac_voltage(chan)
for i,v in enumerate(vs):
    print 'Trying v: ', v
    adwin.set_dac_voltage((chan,v))
    qt.msleep(0.1)
    pows[i] =power_meter.get_power()*1e9

adwin.set_dac_voltage((chan,old_v))
dat = qt.Data(name= chan + '_sweep')
dat.add_coordinate('Voltage [V]')
dat.add_value('Power [nW]')
dat.create_file()
plt = qt.Plot2D(dat, 'rO', name='freq_sweep', coorddim=0, valdim=1, 
        clear=True)
plt.add_data(dat, coorddim=0, valdim=2)

dat.add_data_point(vs,pows)
dat.close_file()
plt.save_png(dat.get_filepath()+'png')
