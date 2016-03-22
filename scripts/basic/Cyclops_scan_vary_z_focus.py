import qt
import time
import numpy as np
import msvcrt


AOM = qt.instruments['GreenAOM']


zoom=[1.5,2.5]#[0.0,1.0,5.0,4.0,3.0,2.0,1.0]  # delta z compare to focus
# optical_power= np.ones(len(zoom))*300e-6#[300e-6,300e-6,300e-6,300e-6,300e-6]  # Optical power for the different scans
focus= 4.00 # z reference position
steps=[361]*len(zoom)
pixeltime =[10]*len(zoom)

stop_scan=False

# at RT , the scanning range is ((0,40),(0,40))
scan2d.set_ystart(0.5)
#scan2d.set_ystop(9.5)
scan2d.set_ystop(27.5)
scan2d.set_xstart(0.5)
#scan2d.set_xstop(9.5)
scan2d.set_xstop(27.5)
j=0
k=0
for i in zoom:
    if stop_scan:
        break
    scan_done=False

    print '%s um'%i
    AOM.set_power(450e-6)
    #print 'Green power = %.1f uW' % (AOM.get_power()*1e6)
    master_of_space.set_z(focus+i)
    setup_controller.set_keyword('Membrane_NVDensityScan_focus=4.00um_zrel=%s_um'%i)

    scan2d.set_xsteps(steps[j])
    scan2d.set_ysteps(steps[j])
    scan2d.set_pixel_time(pixeltime[j])
    qt.msleep(1)
    scan2d.set_is_running(True)
    while(scan_done==False):#scan2d.get_is_running()):
        qt.msleep(0.1)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
            stop_scan=True
        if stop_scan: 
            break
        if scan2d.get_current_line()[0]==(steps[j]-1):
            scan_done=True
            print 'scan done'
            qt.msleep(pixeltime[j]*(steps[j]+10)*0.001)
    qt.msleep(1)#it needs this second rest to save the right instrument settings.
    j=j+1
    k=k+1

