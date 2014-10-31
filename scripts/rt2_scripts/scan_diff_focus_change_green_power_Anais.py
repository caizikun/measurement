import qt
import time
import numpy as np

AOM = qt.instruments['GreenAOM']


zoom=[-1.5,0.0,1.5,3.0,4.5,6.0,7.5]  # delta z compare to focus
optical_power= np.ones(7)*300e-6#[300e-6,300e-6,300e-6,300e-6,300e-6]  # Optical power for the different scans
focus= 58 # z reference position
steps=[501]*len(zoom)
pixeltime =[10]*len(zoom)


scan2d.set_ystart(0)
scan2d.set_ystop(50)
scan2d.set_xstart(-100)
scan2d.set_xstop(0)
j=0
k=0
for i in zoom:
  print '%s_um'%i
  print 'Note: We took out the AOM.set_power() since it is not functional atm 12-8-14 NorbertMachiel'
  #AOM.set_power(optical_power[k])
  #print 'Green power = %.1f uW' % (AOM.get_power()*1e6)
  master_of_space.set_z(focus+i)
  setup_controller.set_keyword('Horst_NVDensityScan_focus=58um_zrel=%s_um'%i)

  scan2d.set_xsteps(steps[j])
  scan2d.set_ysteps(steps[j])
  scan2d.set_pixel_time(pixeltime[j])
  scan2d.set_is_running(True)
  while(not counters.get_is_running()):
      qt.msleep(0.1)
  j=j+1
  k=k+1
  print 'scan ready2' 
  print 'hell222222'
