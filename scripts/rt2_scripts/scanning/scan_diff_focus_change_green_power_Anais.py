import qt
import time
import numpy as np
import msvcrt

AOM = qt.instruments['GreenAOM']

# counter = [0, 1, 2]
# counter = [0]
z_start = [37.5]#,37.5,36.5]
xstart = [-62.5]*len(z_start)
xstop = [-37.5]*len(z_start)
ystart = [37.5]*len(z_start)
ystop = [62.5]*len(z_start)
xpx = 251
ypx = 251
bleaching = True

# z_start = [39.40]

# zoom_depth = [2.5, 3.0, 3.5]

counter = 0

for i,x in enumerate(xstart):
  scan2d.set_xstart(x)
  scan2d.set_xstop(xstop[i])
  for jj,y in enumerate(ystart):
    scan2d.set_ystart(y)
    scan2d.set_ystop(ystop[jj])
    zoom = np.array([1.,-1.5,-2.5])  # delta z compare to focus
    # zoom = [2.00]
    optical_power= np.ones(20)*400e-6#[300e-6,300e-6,300e-6,300e-6,300e-6]  # Optical power for the different scans
    # optical_power = np.ones(4) * 50e-6
    # optical_power[1:4] *= 2 
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
        setup_controller.set_keyword('Sophie_NVsearch_bleach_focus=%sum_zrel=%s_um'%(np.round(focus,2),i))

        lastline_reached=False
        #print 'xsteps[j]', xsteps[j]
        scan2d.set_xsteps(xsteps[j])
        scan2d.set_ysteps(ysteps[j])
        scan2d.set_pixel_time(bleaching_pixeltime[j])
        qt.msleep(5)

        scan2d.set_is_running(True)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): stop_scan=True
        if stop_scan: break

        while(scan2d.get_is_running()):
          qt.msleep(0.1)
          if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): stop_scan=True
          if stop_scan: break
        qt.msleep(5)

      AOM.set_power(optical_power[k])
      print 'Green power = %.1f uW' % (AOM.get_power()*1e6)
      
      setup_controller.set_keyword('Sophie_NVsearch_focus=%sum_zrel=%s_um'%(np.round(focus,2),i))

      lastline_reached=False
      #print 'xsteps[j]', xsteps[j]
      scan2d.set_xsteps(xsteps[j])
      scan2d.set_ysteps(ysteps[j])
      scan2d.set_pixel_time(pixeltime[j])
      qt.msleep(5)

      scan2d.set_is_running(True)
      if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): stop_scan=True
      if stop_scan: break

      while(scan2d.get_is_running()):
        qt.msleep(0.1)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): stop_scan=True
        if stop_scan: break
      qt.msleep(5)

      j=j+1
      k=k+1
      print 'scan ready' 
    counter += 1

AOM.set_power(1e-9)
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