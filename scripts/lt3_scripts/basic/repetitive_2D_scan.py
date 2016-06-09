import qt
import time
import numpy as np
import msvcrt

AOM = qt.instruments['GreenAOM']

# counter = [0, 1, 2]
# counter = [0]
z_start = [0.46]*5
xstart = [-7]*len(z_start)
xstop = [7]*len(z_start)
ystart = [-7]*len(z_start)
ystop = [7]*len(z_start)
xpx = 201
ypx = 201


# z_start = [39.40]

# zoom_depth = [2.5, 3.0, 3.5]

counter = 0

for x_start,x_stop,y_start,y_stop in zip(xstart,xstop,ystart,ystop):
  scan2d.set_xstart(x_start)
  scan2d.set_xstop(x_stop)
  scan2d.set_ystart(y_start)
  scan2d.set_ystop(y_stop)
  zoom = [0]*len(z_start)
  # zoom = [2.00]
  # optical_power= np.ones(20)*150e-6#[300e-6,300e-6,300e-6,300e-6,300e-6]  # Optical power for the different scans
  # optical_power = np.ones(4) * 50e-6
  # optical_power[1:4] *= 2 
  focus= z_start[counter] # z reference position
  xsteps=[xpx]*len(zoom)
  ysteps=[ypx]*len(zoom)
  pixeltime =[10.]*len(zoom)
  j=0
  k=0
  stop_scan = False
  for i in zoom:
    print '%s_um'%i
    if i  == 3.5 or i == 4.0:
      AOM.trun_on()
    else:
      AOM.turn_on()
    print 'Green power = %.1f uW' % (AOM.get_power()*1e6)
    master_of_space.set_z(focus+i)
    qt.msleep(5)
    setup_controller.set_keyword('Cavities_NVsearch_focus=%sum_zrel=%s_um'%(np.round(focus,2),i))

    lastline_reached=False
    #print 'xsteps[j]', xsteps[j]
    scan2d.set_xsteps(xsteps[j])
    scan2d.set_ysteps(ysteps[j])
    scan2d.set_pixel_time(pixeltime[j])
    scan2d.set_is_running(True)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): stop_scan=True
    if stop_scan: break

    while(scan2d.get_is_running()):
      qt.msleep(0.1)
      if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): stop_scan=True
      if stop_scan: break

    j=j+1
    k=k+1
    print 'scan ready' 
    counter += 1

AOM.turn_off()
print 'Current coarse position X1, Y_hoog'
print 'Done with scans!'

# for m in counter:
#   if m == 0:
#     zoom=[3.0, 2.5]#[1.5, 3.0, 4.0]#,1.5,3.0]  # delta z compare to focus
#     optical_power= np.ones(7)*100e-6#[300e-6,300e-6,300e-6,300e-6,300e-6]  # Optical power for the different scans
#     # optical_power = np.ones(4) * 50e-6
#     # optical_power[1:4] *= 2 
#     focus= 48.5 # z reference position
#     xsteps=[201]*len(zoom)
#     ysteps=[201]*len(zoom)
#     pixeltime =[10]*len(zoom)

#     scan2d.set_ystart(-10.00)
#     scan2d.set_ystop(10.00)
#     scan2d.set_xstart(-80.00)
#     scan2d.set_xstop(-60.00)
#     j=0
#     k=0
#     stop_scan = False

#     for i in zoom:
#       print '%s_um'%i

#       AOM.set_power(optical_power[k])
#       print 'Green power = %.1f uW' % (AOM.get_power()*1e6)
#       master_of_space.set_z(focus+i)
#       qt.msleep(5)
#       setup_controller.set_keyword('Horst_NVsearch_focus=%sum_zrel=%s_um'%(np.round(focus,2),i))

#       lastline_reached=False

#       scan2d.set_xsteps(xsteps[j])
#       scan2d.set_ysteps(ysteps[j])
#       scan2d.set_pixel_time(pixeltime[j])
#       scan2d.set_is_running(True)
#       if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): stop_scan=True
#       if stop_scan: break

#       while(scan2d.get_is_running()):
#         qt.msleep(0.1)
#         if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): stop_scan=True
#         if stop_scan: break

#       j=j+1
#       k=k+1
#       print 'scan ready' 
#   elif m == 1:
#     zoom=[2.0, 3.0, 3.5]#[1.5, 3.0, 4.0]#,1.5,3.0]  # delta z compare to focus
#     optical_power= np.ones(7)*100e-6#[300e-6,300e-6,300e-6,300e-6,300e-6]  # Optical power for the different scans
#     focus= 47.6 # z reference position
#     xsteps=[201]*len(zoom)
#     ysteps=[201]*len(zoom)
#     pixeltime =[10]*len(zoom)

#     scan2d.set_ystart(-10.00)
#     scan2d.set_ystop(10.00)
#     scan2d.set_xstart(-60.00)
#     scan2d.set_xstop(-40.00)
#     j=0
#     k=0
#     stop_scan = False

#     for i in zoom:
#       print '%s_um'%i

#       AOM.set_power(optical_power[k])
#       print 'Green power = %.1f uW' % (AOM.get_power()*1e6)
#       master_of_space.set_z(focus+i)
#       qt.msleep(5)
#       setup_controller.set_keyword('Horst_NVsearch_focus=%sum_zrel=%s_um'%(np.round(focus,2),i))

#       lastline_reached=False

#       scan2d.set_xsteps(xsteps[j])
#       scan2d.set_ysteps(ysteps[j])
#       scan2d.set_pixel_time(pixeltime[j])
#       scan2d.set_is_running(True)
#       if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): stop_scan=True
#       if stop_scan: break

#       while(scan2d.get_is_running()):
#         qt.msleep(0.1)
#         if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): stop_scan=True
#         if stop_scan: break

#       j=j+1
#       k=k+1
#       print 'scan ready' 
#   elif m == 2:
#     zoom=[2.0, 3.0, 3.5]#[1.5, 3.0, 4.0]#,1.5,3.0]  # delta z compare to focus
#     optical_power= np.ones(7)*100e-6#[300e-6,300e-6,300e-6,300e-6,300e-6]  # Optical power for the different scans
#     focus= 47.1 # z reference position
#     xsteps=[201]*len(zoom)
#     ysteps=[201]*len(zoom)
#     pixeltime =[10]*len(zoom)

#     scan2d.set_ystart(10.00)
#     scan2d.set_ystop(30.00)
#     scan2d.set_xstart(-60.00)
#     scan2d.set_xstop(-40.00)
#     j=0
#     k=0
#     stop_scan = False

#     for i in zoom:
#       print '%s_um'%i

#       AOM.set_power(optical_power[k])
#       print 'Green power = %.1f uW' % (AOM.get_power()*1e6)
#       master_of_space.set_z(focus+i)
#       qt.msleep(5)
#       setup_controller.set_keyword('Horst_NVsearch_focus=%sum_zrel=%s_um'%(np.round(focus,2),i))

#       lastline_reached=False

#       scan2d.set_xsteps(xsteps[j])
#       scan2d.set_ysteps(ysteps[j])
#       scan2d.set_pixel_time(pixeltime[j])
#       scan2d.set_is_running(True)
#       if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): stop_scan=True
#       if stop_scan: break

#       while(scan2d.get_is_running()):
#         qt.msleep(0.1)
#         if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): stop_scan=True
#         if stop_scan: break

#       j=j+1
#       k=k+1
#       print 'scan ready' 