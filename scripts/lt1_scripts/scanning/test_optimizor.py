from analysis.lib.fitting import fit, common
reload(common)


def go_to_middle_of_membrane():
    
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
    print fits['x01']+Dx/2
    if gaussian_fit['success']:
        mos_ins.set_z(fits['x01']+Dx/2.-0.1)