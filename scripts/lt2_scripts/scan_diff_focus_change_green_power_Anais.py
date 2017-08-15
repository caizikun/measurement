import qt
import time
import numpy as np
import msvcrt

AOM = qt.instruments['GreenAOM']

# counter = [0, 1, 2]
# counter = [0]
z_start = [12.2]#,12.2]
xstart = [19.]#[0.1,19.]
xstop = [39.]#[19,39.]
ystart = [0.1]*len(z_start)
ystop = [21.9]*len(z_start)
xpx = 201
ypx = 201
bleaching = False

# z_start = [39.40]

# zoom_depth = [2.5, 3.0, 3.5]

counter = 0

# for i,x in enumerate(xstart):

for jj,y in enumerate(ystart):
  scan2d_stage.set_xstart(xstart[jj])
  scan2d_stage.set_xstop(xstop[jj])
  scan2d_stage.set_ystart(ystart[jj])
  scan2d_stage.set_ystop(ystop[jj])
  zoom = np.arange(1.,6.)  # delta z compared to focus
  # zoom = np.array([4.,5.])

  optical_power= [640.e-6]*len(zoom)  # Optical power for the different scans


  focus= z_start[counter] # z reference position
  xsteps=[xpx]*len(zoom)
  ysteps=[ypx]*len(zoom)
  pixeltime =[10.]*len(zoom)
  bleaching_pixeltime = [100.]*len(zoom)

  j=0
  k=0
  stop_scan = False
  for i in zoom:
    print '%s_um'%i

    master_of_space.set_z(focus+i)
    qt.msleep(5)

    if bleaching:
      AOM.turn_on()
      setup_controller.set_keyword('Donald_bleaching_focus=%sum_zrel=%s_um'%(np.round(focus,2),i))

      lastline_reached=False
      #print 'xsteps[j]', xsteps[j]
      scan2d_stage.set_xsteps(xsteps[j])
      scan2d_stage.set_ysteps(ysteps[j])
      scan2d_stage.set_pixel_time(bleaching_pixeltime[j])
      qt.msleep(5)

      scan2d_stage.set_is_running(True)
      if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): stop_scan=True
      if stop_scan: break

      while(scan2d_stage.get_is_running()):
        qt.msleep(0.1)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): stop_scan=True
        if stop_scan: break
      qt.msleep(5)

    AOM.set_power(optical_power[k])
    print 'Green power = %.1f uW' % (AOM.get_power()*1e6)
    
    setup_controller.set_keyword('Donald_Scan5_focus=%sum_zrel=%s_um'%(np.round(focus,2),i))

    lastline_reached=False
    #print 'xsteps[j]', xsteps[j]
    scan2d_stage.set_xsteps(xsteps[j])
    scan2d_stage.set_ysteps(ysteps[j])
    scan2d_stage.set_pixel_time(pixeltime[j])
    qt.msleep(5)

    scan2d_stage.set_is_running(True)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): stop_scan=True
    if stop_scan: break

    while(scan2d_stage.get_is_running()):
      qt.msleep(0.1)
      if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): stop_scan=True
      if stop_scan: break
    qt.msleep(5)

    j=j+1
    k=k+1
    print 'scan ready' 
  counter += 1

AOM.set_power(0.1e-6)
#print 'Current coarse position X1, Y_hoog'
print 'Done with scans!'