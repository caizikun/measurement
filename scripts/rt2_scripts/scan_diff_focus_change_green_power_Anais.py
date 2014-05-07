import qt
import time
import numpy as np

AOM = qt.instruments['GreenAOM']


zoom=[-2.0,0.0,2.0,4.0,6.0,8.0,10.0]  # delta z compare to focus
optical_power= np.ones(7)*300e-6#[300e-6,300e-6,300e-6,300e-6,300e-6]  # Optical power for the different scans
focus= 61.9 # z reference position
steps=[61]*len(zoom)
pixeltime =[10]*len(zoom)


scan2d.set_ystart(51)
scan2d.set_ystop(60)
scan2d.set_xstart(-26)
scan2d.set_xstop(-17)
j=0
k=0
for i in zoom:
  print '%s_um'%i
  AOM.set_power(optical_power[k])
  print 'Green power = %.1f uW' % (AOM.get_power()*1e6)
  master_of_space.set_z(focus+i)
  setup_controller.set_keyword('The111_no1_SIL5_%s_um'%i)

  scan2d.set_xsteps(steps[j])
  scan2d.set_ysteps(steps[j])
  scan2d.set_pixel_time(pixeltime[j])
  scan2d.set_is_running(True)
  while(not counters.get_is_running()):
      qt.msleep(0.1)
  j=j+1
  k=k+1
  print 'scan ready' 
