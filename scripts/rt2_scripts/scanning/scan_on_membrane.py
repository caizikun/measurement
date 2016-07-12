import qt
import time
import msvcrt
# import setup
import numpy as np
import os
import h5py
import sys

from analysis.lib.fitting import fit, common
reload(common)


def get_signal_to_noise():

    opt_ins = qt.instruments['opt1d_counts']

    x,y = opt_ins.run(dimension='x', scan_length=1.2, nr_of_points=51, pixel_time=100, return_data=True, gaussian_fit=True)

    fitargs= (np.min(y), np.max(y), x[np.argmax(y)], 0.1)
            #print fitargs, len(p)
    gaussian_fit = fit.fit1d(x, y,common.fit_gauss_pos, *fitargs, do_print=False,ret=True)


    print gaussian_fit['success']

    p0=  gaussian_fit['params_dict']
    plot(x,y,name='sn_measurement',clear=True)
    xp=linspace(min(x),max(x),100)
    plot(xp,gaussian_fit['fitfunc'](xp), name='sn_measurement')

    print 'signal/noise : {:.0f}/{:.0f}  = {:.2f}'.format(p0['A'],p0['a'],p0['A']/p0['a'])
    return gaussian_fit

def go_to_membrane(where):
    
    opt_ins = qt.instruments['opt1d_counts']
    mos_ins = qt.instruments['master_of_space']

    x,y = opt_ins.run(dimension='z', scan_length=6, nr_of_points=40, pixel_time=40, return_data=True, gaussian_fit=False)

    Dx = 1.5
    #g_a1, g_A1, g_x01, g_sigma1, g_A2, g_Dx, g_sigma2
    fitargs= (0, np.max(y), x[np.argmax(y)], 0.5, np.max(y)*0.7,Dx,0.5)
                #print fitargs, len(p)
    gaussian_fit = fit.fit1d(x, y,common.fit_offset_double_gauss, *fitargs,fixed =[5], do_print=False,ret=True)

    print gaussian_fit['success']
    plot(x,y,name='test',clear=True)
    xp=linspace(min(x),max(x),100)
    plot(xp,gaussian_fit['fitfunc'](xp), name='test')


    fits=gaussian_fit['params_dict']
    
    if where == 'middle':
        D=Dx/2.-0.1
    elif where == 'surface':
        D=0
    else:
        D=Dx/2.-0.1
        print'Middle of membrane'

    if gaussian_fit['success']:
        print 'fit succeeded, going to Z=', fits['x01']+D
        mos_ins.set_z(fits['x01']+D)
    else:
        mos_ins.set_z(mos_ins.get_z()+D)
    qt.msleep(1)
    return gaussian_fit


# def goto_surface():
#     zfocus=qt.instruments['opt1d_counts']
#     zfocus.run(dims=['z'], cycles=1, , int_time=50)
#     time.sleep(0.5)

def movey(ums):
    stepper=qt.instruments['AttoPositioner']
    ins=stepper.GetPosition(1)
    cur=ins
    if ums>0:
        ums=ums/10
        ydirec=1
    else: 
        ums=ums/10
        ydirec=-1
    while (abs(ins-cur) <= abs(ums)):
        if (msvcrt.kbhit() and (msvcrt.getch()=='q')):
            aborted=True
            break
        stepper.MoveNSteps(1,ydirec)
        time.sleep(0.1)
        cur=stepper.GetPosition(1)


def movez(ums):
    stepper=qt.instruments['AttoPositioner']
    ins=stepper.GetPosition(0)
    if ums>0:
        ums=ums/10000
        zdirec=1
    else: 
        ums=ums/50000
        zdirec=-1
    while (abs(ins-stepper.GetPosition(0)) <= abs(ums)):
        if (msvcrt.kbhit() and (msvcrt.getch()=='q')):
            aborted=True
            break
        stepper.MoveNSteps(0,zdirec)
        time.sleep(0.5)




def movex(ums):
    stepper=qt.instruments['AttoPositioner']
    ums=ums/10
    if ums>0:
        for x in xrange(0,abs(ums)):
            stepper.MoveNSteps(2,3)
            time.sleep(0.1)
            if (msvcrt.kbhit() and (msvcrt.getch()=='q')):
                aborted=True
                break
    else:
        for x in xrange(0,abs(ums)):
            stepper.MoveNSteps(2,-3)
            time.sleep(0.1)
            if (msvcrt.kbhit() and (msvcrt.getch()=='q')):
                aborted=True
                break

def do_long_scan(blocknumx,blocknumy):

    stepper=qt.instruments['Attocube_ANC350']
    scan2d_ins=qt.instruments['scan2d'] 
    save=qt.instruments['setup_controller']
    mos_ins = qt.instruments['master_of_space']
    Green = qt.instruments['GreenAOM']

    ystart=10
    ystop=20
    xstart=10
    xstop=20
    ystep=101
    xstep=101

    scan2d_ins.set_ystart(ystart)
    scan2d_ins.set_xstart(xstart)
    scan2d_ins.set_ystop(ystop)
    scan2d_ins.set_xstop(xstop)
    scan2d_ins.set_ysteps(ystep)
    scan2d_ins.set_xsteps(xstep)

    ii=0
    aborted=False
    for x_step in range(blocknumx):
        ydirec= 1 if ii%2==0 else -1 
        for y_step in range(blocknumy):
            save.set_keyword('x=%d,y=%d'%(x_step,y_step))
            fit_ress = go_to_membrane('surface')
            scan2d_ins.set_pixel_time(100)
            Green.turn_on()
            scan2d_ins.set_is_running(True)
            while scan2d_ins.get_is_running():
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                    aborted=True
                    break
                qt.msleep(1)
            qt.msleep(1)            
            last_fp = scan2d_ins.get_last_filepath()
            fit.write_to_hdf(fit_ress,last_fp)
            mos_ins.set_x(xstart)
            qt.msleep(0.5)
            mos_ins.set_y(ystart)
            qt.msleep(0.5)

            fit_res=go_to_membrane('middle')
            scan2d_ins.set_pixel_time(10)
            Green.set_power(100e-6)
            scan2d_ins.set_is_running(True)
            while scan2d_ins.get_is_running():
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
                    aborted=True
                    break
                qt.msleep(1)
            qt.msleep(1)
            last_fp = scan2d_ins.get_last_filepath()
            fit.write_to_hdf(fit_res,last_fp)
            mos_ins.set_x(xstart)
            qt.msleep(0.5)
            mos_ins.set_y(ystart)
            qt.msleep(0.5)
            movey((ystop-ystart)*ydirec)
            if aborted:
                break
        ii+=1
        if blocknumx > 1:
            movex(xstop-xstart)
        if aborted:
            break

    # Move stepper back to original position 

    # movex((xstop-xstart)*9)
    # if blocknumy%2==1:
    #     movey(ystop-ystart)

#if __name__=='__main__':
#    do_long_scan()

'''def markerscan(where):

    stepper=qt.instruments['Attocube_ANC350']
    scan2d_ins=qt.instruments['scan2d'] 
    save=qt.instruments['setup_controller']
    mos_ins = qt.instruments['master_of_space']
    Green = qt.instruments['GreenAOM']

    if where == 'left':
        pos=0
    elif where == 'right':
        pos=1
    elif where == 'up':
        pos=2
    elif where == 'down':
        pos=3
    else:
        sys.exit('Give: \'left\' \'right\' \'up\' or \'down\'')
          
    xstart = [[5,15,25],[0,10,20],[2.5,12.5,22.5],[2.5,12.5,22.5]]
    xstop = [[15,25,35],[10,20,30],[12.5,22.5,32.5],[12.5,22.5,32.5]]
    ystart = [[2.5,12.5,22.5],[2.5,12.5,22.5],[5,15,25],[0,10,20]]
    ystop = [[12.5,22.5,32.5],[12.5,22.5,32.5],[15,25,35],[10,20,30]]
    xstep = 101
    ystep = 101

   
    scan2d_ins.set_ysteps(ystep)
    scan2d_ins.set_xsteps(xstep)

    aborted=False
    for x in range(2):
        for y in range(2):
            save.set_keyword('x=%d,y=%d'%(x,y))

            xstartit=xstart[pos][x]
            xstopit=xstop[pos][x]
            ystartit=ystart[pos][y]
            ystopit=ystop[pos][y]

            scan2d_ins.set_ystart(ystartit)
            scan2d_ins.set_xstart(xstartit)
            scan2d_ins.set_ystop(ystopit)
            scan2d_ins.set_xstop(xstopit)

            scan2d_ins.set_pixel_time(10)

            fit_ress = go_to_membrane('surface')
            Green.turn_on()
            scan2d_ins.set_is_running(True)
            while scan2d_ins.get_is_running():
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                    aborted=True
                    break
                qt.msleep(1)
            qt.msleep(1)
            last_fp = scan2d_ins.get_last_filepath()
            fit.write_to_hdf(fit_ress,last_fp)
            mos_ins.set_x(xstart)
            qt.msleep(0.5)
            mos_ins.set_y(ystart)
            qt.msleep(0.5)
            

            fit_res = go_to_membrane('middle')
            Green.set_power(100e-6)
            scan2d_ins.set_is_running(True)
            while scan2d_ins.get_is_running():
                if (msvcrt.kbhit() and (msvcrt.getch()== 'q')):
                    aborted=True
                    break
                qt.msleep(1)
            qt.msleep(1)
            last_fp = scan2d_ins.get_last_filepath()
            fit.write_to_hdf(fit_ress,last_fp)
            if aborted:
                break
        if aborted:
            break'''


def markerscan(xy,rlud):

    
    scan2d_ins=qt.instruments['scan2d'] 
    save=qt.instruments['setup_controller']
    mos_ins = qt.instruments['master_of_space']
    Green = qt.instruments['GreenAOM']
    opt_ins = qt.instruments['optimiz0r']
    opt1d_ins = qt.instruments['opt1d_counts']

    maxy = 25
    if rlud == 'right':
        xspace = xy
        yspace = maxy
        xscan = [xy-10,xy]
        xdirec=-1
        yscan = [2.5,12.5]
        ydirec = 1
    elif rlud == 'left':
        xspace = maxy-xy
        yspace = maxy
        xscan = [xy,xy+10]
        xdirec = 1
        yscan = [2.5,12.5]
        ydirec = 1
    elif rlud == 'down':
        xspace = maxy
        yspace = maxy-xy
        xscan = [2.5,12.5]
        xdirec=1
        yscan = [xy,xy+10]
        ydirec = 1
    elif rlud == 'up':
        xspace = maxy
        yspace = xy
        xscan = [2.5,12.5]
        xdirec = 1
        yscan = [xy-10,xy]
        ydirec = -1
    else:
        sys.exit('Give the x or y coordinate and location (\'left\', \'right\', \'up\' or \'down\') of the marker')

    xstep = 101
    ystep = 101

    Green.turn_on()
    scan2d_ins.set_ysteps(ystep)
    scan2d_ins.set_xsteps(xstep)

    blockn=0
    aborted=False
    for x in range(xspace//10):
        for y in range(yspace//10):
            save.set_keyword('x=%d,y=%d'%(xscan[0],yscan[0]))

            qt.msleep(1)
            opt1d_ins.run(dimension='z', scan_length=5, nr_of_points=31, pixel_time=100, return_data=False, gaussian_fit=True)
            qt.msleep(3)

            scan2d_ins.set_xstart(xscan[0])
            scan2d_ins.set_ystart(yscan[0])
            scan2d_ins.set_xstop(xscan[1])
            scan2d_ins.set_ystop(yscan[1])
            scan2d_ins.set_pixel_time(100)

            
            scan2d_ins.set_is_running(True)
            while scan2d_ins.get_is_running():
                if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                    aborted=True
                    break
                qt.msleep(1)
            qt.msleep(1)

            # last_fp = scan2d_ins.get_last_filepath()
            # fit.write_to_hdf(fit_ress,last_fp)

            mos_ins.set_x(xscan[0])
            qt.msleep(0.5)
            mos_ins.set_y(yscan[0])
            qt.msleep(2)
            
            opt1d_ins.run(dimension='z', scan_length=5, nr_of_points=31, pixel_time=100, return_data=False, gaussian_fit=True)
            qt.msleep(3)
            mos_ins.set_z(mos_ins.get_z()+0.6)
            qt.msleep(1)
            # Green.set_power(100e-6)
            scan2d_ins.set_pixel_time(10)
            scan2d_ins.set_is_running(True)

            while scan2d_ins.get_is_running():
                if (msvcrt.kbhit() and (msvcrt.getch()== 'q')):
                    aborted=True
                    break
                qt.msleep(1)

            qt.msleep(1)
            # last_fp = scan2d_ins.get_last_filepath()
            # fit.write_to_hdf(fit_res,last_fp)

            yscan[0]=yscan[0]+10*ydirec
            yscan[1]=yscan[1]+10*ydirec

            if aborted:
                break

        yscan[0]=yscan[0]-10*ydirec*(y+1)
        yscan[1]=yscan[1]-10*ydirec*(y+1)

        xscan[0]=xscan[0]+10*xdirec
        xscan[1]=xscan[1]+10*xdirec
        if aborted:
            break


def depthscan(zmin,zmax,steps):
    scan2d_ins=qt.instruments['scan2d'] 
    save=qt.instruments['setup_controller']
    mos_ins = qt.instruments['master_of_space']

    '''scan2d_ins.set_xstart(1)
    scan2d_ins.set_ystart(1)
    scan2d_ins.set_xstop(39)
    scan2d_ins.set_ystop(39)
    scan2d_ins.set_ysteps(501)
    scan2d_ins.set_xsteps(501)
    scan2d_ins.set_pixel_time(10)'''
    zstep=(zmax-zmin)/float(steps)
    aborted=False
    mos_ins.set_z(zmin)
    for x in range(steps):
        qt.msleep(1)
        scan2d_ins.set_is_running(True)
        while scan2d_ins.get_is_running():
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                aborted=True
                break
            qt.msleep(1)
        qt.msleep(1)
        mos_ins.set_z(mos_ins.get_z()+zstep)
        if aborted: 
            break

def contopt(interval):
    opt_ins = qt.instruments['optimiz0r']
    opt1d_ins = qt.instruments['opt1d_counts']
    mos_ins = qt.instruments['master_of_space']
    aborted=False
    x=1
    while aborted==False:
        # print x        
        # GreenAOM.set_power(200e-6)
        # mos_ins.set_x(mos_ins.get_x()-1)
        # qt.msleep(0.5)
        opt1d_ins.run(dimension='z', scan_length=4, nr_of_points=31, pixel_time=100, return_data=False, gaussian_fit=True, blocking=True)
        # mos_ins.set_x(mos_ins.get_x()+1)
        mos_ins.set_z(mos_ins.get_z()+0.3)
        qt.msleep(3)
        opt_ins.optimize(dims=['x','y'], cycles = 3, int_time = 100, cnt=3)
        t0=time.clock()
        while abs(t0-time.clock())<interval:
            qt.msleep(1)
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                aborted=True
                break
        if aborted==True:
            break
        x=x+1
