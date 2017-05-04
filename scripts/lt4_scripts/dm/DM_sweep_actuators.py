import qt
import data
from analysis.lib.fitting import fit, common
#from analysis.lib.tools import toolbox as tb
import msvcrt

from scipy import optimize as opt_lib
import logging
import time
import zernike

current_adwin = qt.instruments['adwin']
counter=2
int_time= 200 # in ms  200 usually 200...

def measure_counts(): #fro remote opt.
    if counter == 3:
        old_val=current_adwin.get_countrates()[counter-1]
        
        for i in range(3):
            new_val = current_adwin.get_countrates()[counter-1]
            if new_val!= old_val:
                return new_val
            time.sleep(int_time/1000.)
        return current_adwin.get_countrates()[counter-1]
    else:
        return current_adwin.measure_counts(int_time)[counter-1]/(int_time*1e-3) 

#big_segs=dm.get_bigger_segments()
big_segs=[]
for i in [0,2,4,6,8,10]:
    for j  in [0,2,4,6,8,10]:
        big_segs.append([i,i+1,j,j+1])

def optimize_single_segment(name, seg_nr):
    #measurement parameters
    name = name+ '_step_nr_' + str(seg_nr+1)
    steps=11
    cur_V= dm.get_cur_voltages()[big_segs[seg_nr][0]-1]
    
    V_min=cur_V-2
    V_max=cur_V+2

    int_time=500 # in ms
       
    if V_min<0:
        V_min=0
    if V_max>100:
        V_max=100
    V = linspace(V_min,V_max,steps)

    y_NV = zeros(steps,dtype = float)

    br=False
    for i,voltage in enumerate(V):
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
            br = True
            break
        for act_nr in big_segs[seg_nr]:    
            dm.set_single_actuator(act_nr,voltage,do_save_cfg = False)
 #           if i==0:
#            print act_nr
        qt.msleep(0.1)

        y_NV[i] = measure_counts()

        #print 'step %s, counts %s'%(i,y_NV[i])
    plot_scan(name,V,y_NV)

    highest_cntrate_idx=tb.nearest_idx(y_NV,y_NV.max())
    opt_V=V[highest_cntrate_idx]
    for act_nr in big_segs[seg_nr]:    
            dm.set_single_actuator(act_nr,opt_V)
    counters.set_is_running(True)

def get_countrates_at_zernike_amp(zernike_amps, *initial_voltages):
    if (msvcrt.kbhit() and msvcrt.getch() =='q'):
        raise Exception('User abort')
    new_voltages = initial_voltages
    for i,amp in enumerate(zernike_amps):
        X,Y,Z_matrix = zernike.zernike_grid_i(i, 12)
        new_voltages += amp*dm.voltages_from_matrix(Z_matrix)
    dm.set_cur_voltages(new_voltages)

    crs = measure_counts()
    print 'avg_amplitude : {:.2f}, Countrates: {:.0f}'.format(np.mean(np.abs(zernike_amps)), crs)
    #print zernike_amps[0:10]
    return -1.*crs

def get_countrates_at_sinlge_zernike_amp(zernike_i,amp):
    X,Y,Z_matrix = zernike.zernike_grid_i(i, 12)
    new_voltages = dm.get_cur_voltages() + amp*dm.voltages_from_matrix(Z_matrix)
    dm.set_cur_voltages(new_voltages)
    crs = measure_counts()
    return -1.*crs

def anneal_zernike_amps():
    noof_zernikes = 20
    max_func_evs = 2000
    f = get_countrates_at_zernike_amp
    x0 = np.random.rand(noof_zernikes)-0.5
    res = opt_lib.anneal(f, x0,args = (dm.get_cur_voltages()), schedule='boltzmann',
                          full_output=True, maxeval=max_func_evs, lower=-5.,
                          upper=5., dwell=50, disp=True)
    return res

def newton_zernike():
    noof_zernikes = 50
    max_func_evs = 2000
    bounds = [(-10.,10.)]*noof_zernikes
    x0 = (np.random.rand(noof_zernikes)-0.5)*1.
    f = get_countrates_at_zernike_amp
    res = opt_lib.fmin_tnc(f,x0,approx_grad=True, args = (dm.get_cur_voltages()), maxfun = max_func_evs,bounds=bounds, disp=5)
    return res

def nelder_mead_zernike():
    noof_zernikes = 50
    max_func_evs = 2000
    x0 = (np.random.rand(noof_zernikes)-0.5)*1.
    f = get_countrates_at_zernike_amp
    res = opt_lib.fmin_powell(f,x0, args = (dm.get_cur_voltages()), maxfun = max_func_evs, disp=True)
    return res

def differential_evolution_zernike_amps():
    noof_zernikes = 50
    max_func_evs = 6000
    popsize = 5
    f = get_countrates_at_zernike_amp
    bounds = [(-1.,1.)]*noof_zernikes
    res = opt_lib.differential_evolution(f, bounds, args = (dm.get_cur_voltages()),  popsize = popsize, maxiter = int(max_func_evs/popsize/noof_zernikes), disp=True)
    return res

            
def plot_scan(name,x,y, fit_func=None):     
    dat = qt.Data(name='DM_sweep_curve_'+name)
    dat.create_file()
    dat.add_coordinate('Voltage [percentage of V max]')
    dat.add_value('Counts [Hz]')
    if fit_func!=None:
        dat.add_value('Fit')
        fd = fit_func(x)
   
    plt = qt.Plot2D(dat, 'rO', name='Optimization curve', coorddim=0, valdim=1, clear=True)
    plt.add_data(dat, coorddim=0, valdim=2)

    plt.set_plottitle(dat.get_time_name())
    if fit_func!=None:
        dat.add_data_point(x,y,fd)
    else:
        dat.add_data_point(x,y)

    plt.set_legend(False)

    plt.save_png(dat.get_filepath()[:-3]+'.png')
    dfp = dat.get_filepath()
    dat.close_file()
    return dfp

def optimize_zernike_amplitude_brent(i):
    f = get_countrates_at_sinlge_zernike_amp
    print opt_lib.fminbound(f,-2.5,2.5,args=(i,),maxfun=25,xtol=0.1, full_output=True)


def optimize_zernike_amplitude(name, zernike_mode, **kw):
    name = name + '_zernike_' + str(zernike_mode)
    X,Y,Z_matrix = zernike.zernike_grid_i(zernike_mode, 12)
    return optimize_matrix_amplitude(name,Z_matrix,**kw)

def optimize_segments(name, imin,imax, jmin, jmax, **kw):
    Z_matrix = np.zeros((12,12))
    Z_matrix[imin:imax+1, jmin:jmax+1] = 1.
    return optimize_matrix_amplitude(name,Z_matrix,**kw)


def optimize_matrix_amplitude(name, Z_matrix, do_fit=True):
    amplitude = 2.0 #V
    steps = 21 #XXXXXXXXXXXX 13
    amps = np.linspace(-amplitude,amplitude, steps)

    Z_voltages = dm.voltages_from_matrix(Z_matrix)
    cur_voltages = dm.get_cur_voltages()
    
    logging.debug('DM: Starting optimisation scan')
    y_NV = np.zeros(steps)
    for i, amp in enumerate(amps):
        new_voltages = cur_voltages + amp*Z_voltages
        dm.set_cur_voltages(new_voltages)
        if i == 0:
            time.sleep(2.*int_time/1000.)
        y_NV[i] = measure_counts()
        #qt.msleep(0.2)
    logging.debug('DM: Starting fit')   
    opt_amp = None

    if do_fit:
        f = common.fit_gauss
        #a + A * exp(-(x-x0)**2/(2*sigma**2))
        #['g_a', 'g_A', 'g_x0', 'g_sigma']
        args = [100,max(y_NV),0,1]
        fitres = fit.fit1d(amps, y_NV, f, *args, fixed = [],
                   do_print = False, ret = True)
        if fitres['success']:
            if fitres['params_dict']['A'] > 0.:
                opt_amp = fitres['params_dict']['x0']
                max_cnts =  fitres['params_dict']['A'] + fitres['params_dict']['a']
                fp = plot_scan(name, amps, y_NV, fitres['fitfunc'])      
    if opt_amp == None:
        print 'fit failed, going to max point'
        opt_amp=amps[np.argmax(y_NV)]
        max_cnts = np.max(y_NV)  
        fp = plot_scan(name, amps, y_NV)

    logging.debug('DM: Fitting scan finished')   
    new_voltages = cur_voltages + opt_amp*Z_voltages
    dm.set_cur_voltages(new_voltages)
    
    dm.plot_mirror_surf(True, fp[:-3])
    dm.save_mirror_surf(fp[:-4]+'_msurf')
    
    
    counters.set_is_running(True)
    return max_cnts, opt_amp

if __name__ == '__main__':
    green_power = 40e-6
    GreenAOM.turn_on()#set_power(green_power)

    name = '111no2_lt4_localgreen_new_dm'
    dat_tot = qt.Data(name='DM_total_curve_'+name)
    dat_tot.create_file()
    dat_tot.add_coordinate('segment_zernike_nr')
    dat_tot.add_value('Counts [Hz]')
    #dat_tot.add_value('Optimum amp [Hz]') 
    dat_tot.add_coordinate('cycle_nr')

    plt = qt.Plot2D(dat_tot, 'rO', name='DM_total_curve', coorddim=0, valdim=1, clear=True)
    #plt.add(dat_tot, 'bo', coorddim=0, valdim=2, right=True)
    #plt.set_y2tics(True)
    #plt.set_y2label('Optimum amplitude')

    scan_mode = 'zernike'

    try:
        for j in np.arange(1):
            stop_scan=False
            print 'cur cycle = ' , j
            if scan_mode == 'segment':
                for i,(imin,imax,jmin,jmax) in enumerate(big_segs):
                #[(5,5,5,5),(6,6,6,6),(5,5,6,6),(6,6,5,5), (0,1,0,1), (10,11,10,11), (0,1,10,11),(10,11,0,1)]): #lets sweep 75 zernike modes!
                    if msvcrt.kbhit():
                        if msvcrt.getch() == 'c': 
                            stop_scan=True
                            break
                        if msvcrt.getch() == 'q':
                            break
                    cnts,opt_amp = optimize_segments(name, imin,imax,jmin,jmax,do_fit=False)
                    #cnts=measure_counts()
                    dat_tot.add_data_point(i,cnts,j)
                    plt.update()
            elif scan_mode == 'zernike':
                # for i in np.arange(2,38): #first half of the 75 zernike modes!
                #for i in np.arange(38,75): #second half of the 75 zernike modes!
                for i in np.arange(2,38): #2,38#array can go up to 75 zernike modes!
                    if msvcrt.kbhit():
                        if msvcrt.getch() == 'c': 
                            stop_scan=True
                            break
                        if msvcrt.getch() == 'q':
                            break
                    cnts,opt_amp=optimize_zernike_amplitude(name, i)
                    #cnts=measure_counts()

                    dat_tot.add_data_point(i,cnts,j)
                    plt.update()
                    print 'finished zernike' , i

            elif scan_mode == 'zernike_brent':
                for i in np.arange(2,25): #lets sweep 75 zernike modes!
                    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): 
                        stop_scan=True
                        break
                    optimize_zernike_amplitude_brent(i)
                    cnts=measure_counts()
                    dat_tot.add_data_point(i,cnts,j)
                    plt.update()
            elif scan_mode == 'evolution':
                result = differential_evolution_zernike_amps()
            elif scan_mode == 'nelder-mead':
                result = nelder_mead_zernike()
            elif scan_mode == 'newton':
                result = newton_zernike()

            print 'before new block'
            dat_tot.new_block() 
            print 'after new block'
            if stop_scan: break
            #qt.msleep(2)
            #optimiz0r.optimize(dims=['x','y','z'],cnt=counter,cycles=2,int_time=100)
            #stools.recalibrate_lt3_lasers(names=['GreenAOM'],awg_names=[])
            #GreenAOM.set_power(green_power)
    finally:
        print 'before close file'
        dat_tot.close_file()
        print 'after close file'

        