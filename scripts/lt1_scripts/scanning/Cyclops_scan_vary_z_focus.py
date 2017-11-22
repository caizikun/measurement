import qt
import time
import numpy as np
import msvcrt


_green_AOM = qt.instruments['GreenAOM']
_newfocus_AOM = qt.instruments['NewfocusAOM']

zoom=[0.0,0.0]#,1.0,5.0,4.0,3.0,2.0,1.0]  # delta z compare to focus
# optical_power= np.ones(len(zoom))*300e-6#[300e-6,300e-6,300e-6,300e-6,300e-6]  # Optical power for the different scans
focus= 4.51# z reference position
steps=[51]*len(zoom)
pixeltime =[10]*len(zoom)

green_powers=[100e-6,200e-6]
red_powers = [0.e-9,0.e-9]
stop_scan=False

# at RT , the scanning range is ((0,40),(0,40))
scan2d.set_xstart(12.5)
#scan2d.set_xstop(9.5)
scan2d.set_xstop(17.5)
scan2d.set_ystart(7.5)
#scan2d.set_ystop(9.5)
scan2d.set_ystop(12.5)


for i,z in enumerate(zoom):
    if stop_scan:
        break
    scan_done=False

    print '%s um'%z
    _green_AOM.set_power(green_powers[i])
    _newfocus_AOM.set_power(red_powers[i])
    #print 'Green power = %.1f uW' % (AOM.get_power()*1e6)
    master_of_space.set_z(focus+z)
    setup_controller.set_keyword('Membrane_NVDensityScan_focus=%sum_zrel=%s_um'%(focus,z))

    scan2d.set_xsteps(steps[i])
    scan2d.set_ysteps(steps[i])
    scan2d.set_pixel_time(pixeltime[i])
    qt.msleep(1)
    scan2d.set_is_running(True)
    while(scan_done==False):#scan2d.get_is_running()):
        qt.msleep(0.1)
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
            stop_scan=True
        if stop_scan: 
            break
        if scan2d.get_current_line()[0]==(steps[i]-1):
            scan_done=True
            print 'scan done'
            qt.msleep(pixeltime[i]*(steps[i]+10)*0.001)
    qt.msleep(1)#it needs this second rest to save the right instrument settings.


