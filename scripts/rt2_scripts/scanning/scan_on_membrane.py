import qt
import time
import msvcrt
# import setup
import numpy as np
import os
import h5py
import sys
import hdf5_data as h5


from analysis.lib.fitting import fit, common
reload(common)
reload(fit)


def get_signal_to_noise():

    opt_ins = qt.instruments['opt1d_counts']

    x,y = opt_ins.run(dimension='x', scan_length=1.2, nr_of_points=51, pixel_time=100, return_data=True, gaussian_fit=True)

    fitargs= (np.min(y), np.max(y), x[np.argmax(y)], 0.1)
            #print fitargs, len(p)
    gaussian_fit = fit.fit1d(x, y,common.fit_gauss_pos, *fitargs, do_print=False,ret=True)
    


    print gaussian_fit['success']

    p0=  gaussian_fit['params_dict']
    # plot(x,y,name='sn_measurement',clear=True)
    # xp=linspace(min(x),max(x),100)
    # plot(xp,gaussian_fit['fitfunc'](xp), name='sn_measurement')

    print 'signal/noise : {:.0f}/{:.0f}  = {:.2f}'.format(p0['A'],p0['a'],p0['A']/p0['a'])
    return gaussian_fit

def go_to_membrane(where,**kw):
    save_fit = kw.pop('save_fit',False)

    opt_ins = qt.instruments['opt1d_counts']
    mos_ins = qt.instruments['master_of_space']

    x,y = opt_ins.run(dimension='z', scan_length=8, nr_of_points=61, pixel_time=80, return_data=True, gaussian_fit=False)

    Dx = 1.5
    #g_a1, g_A1, g_x01, g_sigma1, g_A2, g_Dx, g_sigma2
    fitargs= (0, np.max(y), x[np.argmax(y)], 0.5, np.max(y)*0.7,Dx,0.5)
                #print fitargs, len(p)
    gaussian_fit = fit.fit1d(x, y,common.fit_offset_double_gauss, *fitargs,fixed =[5], do_print=False,ret=True)

    if type(gaussian_fit)!=dict:
        print 'double gaussian fit failed'
        return
    print gaussian_fit['success']
    
    # plot(x,y,name='test',clear=True)
    # xp=linspace(min(x),max(x),100)
    # plot(xp,gaussian_fit['fitfunc'](xp), name='test')

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
    

    # fdir = os.path.join(self.datafolder, self.FILES_DIR)
    # if not os.path.isdir(fdir):
    #     os.makedirs(fdir)

    if save_fit:
        dat = h5.HDF5Data(name='optimize_z_double_gauss_fit')
        print dat.filepath()
        fit.write_to_hdf(gaussian_fit,dat.filepath())
        dat.close()

    qt.msleep(1)
    return gaussian_fit


# def goto_surface():
#     zfocus=qt.instruments['opt1d_counts']
#     zfocus.run(dims=['z'], cycles=1, , int_time=50)
#     time.sleep(0.5)


def do_long_scan(bleaching_scan = False,save_fits=False, name = ''):
    scan2d_ins=qt.instruments['scan2d'] 
    save=qt.instruments['setup_controller']
    mos_ins = qt.instruments['master_of_space']
    GreenAOM = qt.instruments['GreenAOM']
    opt1d_ins = qt.instruments['opt1d_counts']

    ystarts=[20,40,60,80]#np.linspace(-10,70,5)
    delta_y = 20
    xstarts=[-60]#np.linspace(-90,-10,5)
    delta_x = 20
    ystep=delta_y*10+1
    xstep=delta_x*10+1
    bleaching_time = 20
    depths = np.array([0,-2,-3])

    aborted = False

    #testing
    # ystarts=np.linspace(-20,0,2)
    # xstarts=np.linspace(-100,-80,2)
    # ystep=21
    # xstep=21
    # bleaching_time = 10

    for ystart in ystarts: 
        print 'y start=',ystart
        ystop = ystart+delta_y

        for xstart in xstarts: 
            print 'x start=',xstart
            xstop = xstart+delta_x

            scan2d_ins.set_ystart(ystart)
            scan2d_ins.set_xstart(xstart)
            scan2d_ins.set_ystop(ystop)
            scan2d_ins.set_xstop(xstop)
            scan2d_ins.set_ysteps(ystep)
            scan2d_ins.set_xsteps(xstep)

            mos_ins.set_x(xstart)
            qt.msleep(1)
            mos_ins.set_y(ystart)
            qt.msleep(1)
            
            GreenAOM.set_power(400.e-6)

            #if xstart == xstarts[0]:
            #    qt.msleep(4)
            #    fitres = opt1d_ins.run(dimension='z', scan_length=15, nr_of_points=101, pixel_time=100, gaussian_fit=False, return_fitresult = False)
            #    qt.msleep(4)

            #    if save_fits and type(fitres)==dict:
            #        dat = h5.HDF5Data(name='optimize_z_gauss_fit'+'_y_'+str(ystart))
            #        print dat.filepath()
            #        fit.write_to_hdf(fitres,dat.filepath())
            #        dat.close()

            qt.msleep(3)
            opt1d_ins.run(dimension='z', scan_length=15, nr_of_points=151, pixel_time=100, gaussian_fit=False)
            qt.msleep(5)
            # fitres = opt1d_ins.run(dimension='z', scan_length=5, nr_of_points=51, pixel_time=100, gaussian_fit=True, return_fitresult = True)
            # qt.msleep(2)
            z_surface = mos_ins.get_z()



            if save_fits and type(fitres)==dict:
                dat = h5.HDF5Data(name='optimize_z_gauss_fit'+'_y_'+str(ystart)+'_x_'+str(xstart))
                print dat.filepath()
                fit.write_to_hdf(fitres,dat.filepath())
                dat.close()

            # fit_ress = go_to_membrane('surface',save_fit=True)
 


            for depth in depths:
                print 'depth under surface', depth
                mos_ins.set_z(z_surface+depth)


                if bleaching_scan:
                    save.set_keyword(name+'_bleaching_x=%d,y=%d,z=%.1f+%.1f'%(xstart,ystart,z_surface,depth))
                    scan2d_ins.set_pixel_time(bleaching_time)

                    GreenAOM.turn_on()
                    scan2d_ins.set_is_running(True)
                    while scan2d_ins.get_is_running():
                        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                            aborted=True
                            break
                        qt.msleep(1)
                    qt.msleep(3)   
                    if aborted==True:
                        break

                mos_ins.set_x(xstart)
                qt.msleep(0.5)
                mos_ins.set_y(ystart)
                qt.msleep(0.5)


                save.set_keyword(name+'x=%d,y=%d,z=%.1f+%.1f'%(xstart,ystart,z_surface,depth))

                # fit_res=go_to_membrane('middle', save_fit = True)
                # qt.msleep(2)

                scan2d_ins.set_pixel_time(10)
                GreenAOM.set_power(400e-6)

                scan2d_ins.set_is_running(True)
                while scan2d_ins.get_is_running():
                    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
                        aborted=True
                        break
                    qt.msleep(1)
                qt.msleep(3)
                if aborted==True:
                    break

                mos_ins.set_x(xstart)
                qt.msleep(0.5)
                mos_ins.set_y(ystart)
                qt.msleep(0.5)

            #set z back so that for the next scan it will be easier to find the surface
            mos_ins.set_z(z_surface)

            if aborted==True:
                break

                mos_ins.set_x(xstart)
                qt.msleep(0.5)
                mos_ins.set_y(ystart)
                qt.msleep(0.5)

        if aborted==True:
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
        current_z = mos_ins.get_z()
        save.set_keyword('z=%.2f'%(current_z))
        qt.msleep(1)
        scan2d_ins.set_is_running(True)
        while scan2d_ins.get_is_running():
            if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
                aborted=True
                break
            qt.msleep(1)
        qt.msleep(1)
        mos_ins.set_z(current_z+zstep)
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





# def movey(ums):
#     stepper=qt.instruments['AttoPositioner']
#     ins=stepper.GetPosition(1)
#     cur=ins
#     if ums>0:
#         ums=ums/10
#         ydirec=1
#     else: 
#         ums=ums/10
#         ydirec=-1
#     while (abs(ins-cur) <= abs(ums)):
#         if (msvcrt.kbhit() and (msvcrt.getch()=='q')):
#             aborted=True
#             break
#         stepper.MoveNSteps(1,ydirec)
#         time.sleep(0.1)
#         cur=stepper.GetPosition(1)


# def movez(ums):
#     stepper=qt.instruments['AttoPositioner']
#     ins=stepper.GetPosition(0)
#     if ums>0:
#         ums=ums/10000
#         zdirec=1
#     else: 
#         ums=ums/50000
#         zdirec=-1
#     while (abs(ins-stepper.GetPosition(0)) <= abs(ums)):
#         if (msvcrt.kbhit() and (msvcrt.getch()=='q')):
#             aborted=True
#             break
#         stepper.MoveNSteps(0,zdirec)
#         time.sleep(0.5)




# def movex(ums):
#     stepper=qt.instruments['AttoPositioner']
#     ums=ums/10
#     if ums>0:
#         for x in xrange(0,abs(ums)):
#             stepper.MoveNSteps(2,3)
#             time.sleep(0.1)
#             if (msvcrt.kbhit() and (msvcrt.getch()=='q')):
#                 aborted=True
#                 break
#     else:
#         for x in xrange(0,abs(ums)):
#             stepper.MoveNSteps(2,-3)
#             time.sleep(0.1)
#             if (msvcrt.kbhit() and (msvcrt.getch()=='q')):
#                 aborted=True
#                 break