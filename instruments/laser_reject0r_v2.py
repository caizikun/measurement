from instrument import Instrument
import types
import qt
import numpy as np
import msvcrt, os, sys, time, gobject
from analysis.lib.fitting import fit, common
import instrument_helper
from lib import config
from measurement.lib.config import rotation_mounts as rotcfg
reload(rotcfg)
from scipy import optimize

class laser_reject0r_v2(Instrument):  

    def __init__(self, name, rotator, adwin, red_laser=None, rotation_config_name='',
                waveplates=['zpl_half','zpl_quarter']):
        Instrument.__init__(self, name)


        self._rotator = qt.instruments[rotator]
        if red_laser != None:
            self._red_laser = qt.instruments[red_laser]
        else:
            self._red_laser = None
        self._adwin = qt.instruments[adwin]
        self._waveplates=waveplates
        self._rotation_cfg=rotcfg.config[rotation_config_name]
        self._prev_wp_channel='none'

        self.add_function('optimize')
        self.add_function('jog_optimize')
        self.add_function('optimize_all')
        self.add_function('first_time_run')
        self.add_function('move')
        self.add_function('get_waveplates')
        self.add_function('reset_wp_channel')
        self.add_function('nd_optimize')

        ins_pars  = {'opt_range'              : {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':4, 'units': 'deg'},
                    'opt_noof_points'         : {'type':types.IntType,'flags':Instrument.FLAG_GETSET,   'val':11},
                    'opt_red_power'           : {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':10e-9}, 
                    'first_time_range'        : {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':45,  'units': 'deg'},
                    'first_time_noof_points'  : {'type':types.IntType,'flags':Instrument.FLAG_GETSET,   'val':11},
                    'first_time_red_power'    : {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':1e-9, 'units': 'W'},
                    'cnt_threshold'           : {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':5E5},
                    'zpl_counter'             : {'type':types.IntType,'flags':Instrument.FLAG_GETSET,   'val':2},
                    }
        instrument_helper.create_get_set(self,ins_pars)

        self._powell_direc=None

        cfg_fn = os.path.join(qt.config['ins_cfg_path'], name+'.cfg')

        if not os.path.exists(cfg_fn):
            _f = open(cfg_fn, 'w')
            _f.write('')
            _f.close()

        self._ins_cfg = config.Config(cfg_fn)     
        self.load_cfg()
        self.save_cfg()

    def get_all(self):
        for n in self.get_parameter_names():
            self.get(n)
        
    
    def load_cfg(self):
        params_from_cfg = self._ins_cfg.get_all()

        for p in params_from_cfg:
            val = self._ins_cfg.get(p)
            if type(val) == unicode:
                val = str(val)
            
            try:
                self.set(p, value=val)
            except:
                pass

    def save_cfg(self):
        parlist = self.get_parameters()
        for param in parlist:
            value = self.get(param)
            self._ins_cfg[param] = value

    def get_waveplates(self):
        return self._waveplates

    def move(self,waveplate,degrees, quick_scan=False):
        if waveplate not in self._rotation_cfg.keys():
            print 'Unknown waveplate', waveplate
            return False
        if degrees == 0.:
            return

        wp_channel = self._rotation_cfg[waveplate]['channel']
        wp_axis = self._rotation_cfg[waveplate]['axis']
        #print 'boo1', wp_channel
        if self._prev_wp_channel!=wp_channel:
            #print 'boo2', wp_channel
            self._prev_wp_channel = wp_channel
            self._rotator.set_current_channel(wp_channel)
            qt.msleep(1)

        if quick_scan:
            if np.sign(degrees) == +1:
                steps = int(self._rotation_cfg[waveplate]['pos_calib_quick'] * degrees)
            elif np.sign(degrees) == -1:
                steps = int(self._rotation_cfg[waveplate]['neg_calib_quick'] *degrees)
            self._rotator.quick_scan(steps, wp_axis)
        else:
            if np.sign(degrees) == +1:
                steps = int(self._rotation_cfg[waveplate]['pos_calib_precise'] *degrees)
            elif np.sign(degrees) == -1:
                steps = int(self._rotation_cfg[waveplate]['neg_calib_precise'] *degrees)
            self._rotator.precise_scan(steps, wp_axis)
        return True

    def first_time_run(self, waveplate):
        """
        For the first time, trace large range with waveplates and go to minimum value point
        """
        if waveplate not in self._rotation_cfg.keys():
            print 'Unknown waveplate', waveplate
            return False
        
        qtdata, qtplot = self._create_data_plots('first_time_run_'+waveplate)

        X = np.linspace(0., self.get_first_time_range(), self.get_first_time_noof_points())
        self.move(waveplate,X[0], quick_scan=True)

        Y = np.zeros(len(X))

        self._set_red_power(self.get_first_time_red_power())
        premature_quit = False
        for i,x in enumerate(X):
            if i>0:
                dx = X[i]-X[i-1]
                self.move(waveplate, dx , quick_scan=True)
            qt.msleep(0.01) 

            y = self._measure_counts()
            
            Y[i]=y
            qtdata.add_data_point(x, y)

            if (y > self.get_cnt_threshold())  or  (msvcrt.kbhit() and msvcrt.getch() =='q'):
                self._set_red_power(0)
                premature_quit = True
                break
        qtdata.close_file()
        qt.msleep(0.1)

        if not premature_quit:
            xmin=X[np.argmin(Y)]
            self.move(waveplate,-X[-1]+xmin+90, quick_scan=True)
            print 'New position set to {:.3f} degrees'.format(xmin)
            return True

        return False

    def optimize(self, waveplate, counts_avg=1, **kw):
        """
        Make a detailed scan around the current position of the waveplate, fit the resulting counts vs deg with a parabola, and go to minimum value
        known - keywords : opt_range : optimisation range, defaults to self.opt_range
              - quick_scan: use quick scan

        """
        if waveplate not in self._rotation_cfg.keys():
            print 'Unknown waveplate', waveplate
            return False
        opt_range=kw.pop('opt_range',self.get_opt_range())

        qtdata, qtplot = self._create_data_plots('optimize_'+waveplate)

        X = np.linspace(-opt_range/2., opt_range/2., self.get_opt_noof_points())

        self.move(waveplate,X[0], **kw)

        Y = np.zeros(len(X))
        self._set_red_power(self.get_opt_red_power())
        premature_quit = False
        for i,x in enumerate(X):
            if i > 0:
                dx = X[i]-X[i-1]
                self.move(waveplate, dx , **kw)
            qt.msleep(0.5)
            avg=0.
            for j in range(counts_avg):
                avg=avg+self._measure_counts()
                qt.msleep(0.1)
            avg=avg/counts_avg
            y = avg
            
            Y[i]=y
            qtdata.add_data_point(x, y)

            if (y > self.get_cnt_threshold())  or  (msvcrt.kbhit() and msvcrt.getch() =='q'):
                self._set_red_power(0)
                premature_quit = True
                break
        qtdata.close_file()
        qt.msleep(0.1)

        newpos=-X[-1]
        if not premature_quit:
            fit_res = self._fit(X,Y, qtplot)
            if fit_res != None:
                if np.sign(fit_res['a2']) != -1:
                    fitmin = -fit_res['a1']/(2.*fit_res['a2'])
                else:
                    print '\tFitting a maximum instead of a minimum.'
                    fitmin = 0
                    
            else:
                print '\tGuessing optimal waveplate position...'
                fitmin = X[np.argmin(Y)]

            if (-self.get_opt_range()<fitmin < self.get_opt_range()):
                    #set the position to the optimal position
                    newpos = newpos + fitmin
            else:
                print '\tWARNING: Optimal position differs %s deg\
                        from initial position'%fitmin
                check = raw_input('\tPress "ENTER" to continue, q to quit\n')
                    
                if check == '':
                    #set the position to the optimal position
                    newpos = newpos + fitmin
                    
                elif check == 'q':
                    print 'Process aborted by user'
                    pass
                else:
                    print 'Response to question is not \
                            understood. Not taking any action.'
                    newpos=0.
                
        print 'New position set to {:.3f} degrees'.format(X[-1]+newpos)
        self.move(waveplate,newpos,**kw)
        return True
    
    def optimize_all(self, cycles, **kw):

        opt_method = kw.pop('opt_method','optimize')

        for i in range(cycles):
            for wp in self._waveplates:
                if msvcrt.kbhit() and msvcrt.getch() =='c':
                    return False
                getattr(self,opt_method)(wp, **kw)
        return True

    def _measure_counts(self, counts_avg=1):
         return self._adwin.get_countrates()[self._zpl_counter-1]

    def _fit(self,X,Y, qtplot):
        
        fitres = fit.fit1d(X, Y, common.fit_poly, 
                [X[np.argmin(Y)], 1, 1], do_print = False, ret = True)

        if type(fitres) != type(False):
            p1 = fitres['params_dict']
            fd = fitres['fitfunc'](X)
            qtplot.add(X, fd, '-b')   
        else:
            print '\tCould not fit curve!'
            return None
        return p1    

    def _set_red_power(self,power):
        if self._red_laser!=None:
            self._red_laser.set_power(power)

    def _create_data_plots(self,name):
        qtdata = qt.Data(name = name)
        qtdata.add_coordinate('Degrees')
        qtdata.add_value('Counts')
        dataplot = qt.Plot2D(qtdata, 'rO', name = name, coorddim = 0, 
                valdim = 1, clear = True)
        dataplot.add(qtdata, 'b-', coorddim = 0, valdim = 2)
        return qtdata, dataplot

    def jog_optimize(self, waveplate, directions=[1,-1], counts_avg=10, min_count_break=20):
        """
        For each given direction, scan the given waveplate at given speed
        until the counts start rising or a minimum number of counts (min_count_break) is reached
        The counts can be averaged to reduce noise.
        """
        if waveplate not in self._rotation_cfg.keys():
            print 'Unknown waveplate', waveplate
            return False
        speed=3
        wp_channel = self._rotation_cfg[waveplate]['channel']
        wp_axis = self._rotation_cfg[waveplate]['axis']
        if self._prev_wp_channel!=wp_channel:
            self._prev_wp_channel = wp_channel
            self._rotator.set_current_channel(wp_channel)
            qt.msleep(1)
            
        self._set_red_power(self.get_first_time_red_power())
        for d in directions:
            avg=0.
            for j in range(counts_avg):
                avg=avg+self._measure_counts()
                qt.msleep(0.1)
            avg=avg/counts_avg
            y = avg
            y1=y
            self._rotator.set('jog%d'%wp_axis,np.sign(d)*int(speed))
            qt.msleep(0.2)
            i=0
            while 1:
                for j in range(counts_avg):
                    cts=self._measure_counts()
                    if cts < min_count_break:
                        break
                        i=10 #stop we found a good spot!
                    avg=avg+cts
                    qt.msleep(0.1)
                avg=avg/counts_avg
                y = avg
                if (y > self.get_cnt_threshold())  or  (msvcrt.kbhit() and msvcrt.getch() =='q'):
                    self._set_red_power(0)
                    i=10 #stop!
                    break
                if(y>y1): break
                y1=y
                qt.msleep(0.1)
                i=i+1
                #print i
            if i>2: break
        self._rotator.set('jog%d'%wp_axis,0)

    def step_optimize(self, waveplate, stepsize=1.0, directions=[1,-1],counts_avg=30,min_count_break=20, **kw):
        """
        For each given direction, step the given waveplate with given stepsize (deg)
        until the counts start rising, or a minimum number of counts (min_count_break) is reached
        The counts can be averaged to reduce noise.
        """
        if waveplate not in self._rotation_cfg.keys():
            print 'Unknown waveplate', waveplate
            return False
        self._set_red_power(self.get_first_time_red_power())
        for d in directions:
            avg=0.
            for j in range(counts_avg):
                avg=avg+self._measure_counts()
                qt.msleep(0.1)
            avg=avg/counts_avg
            y = avg
            y1=y
            
            i=0
            while 1:
                self.move(waveplate,d*stepsize, **kw)
                qt.msleep(0.1)
                for j in range(counts_avg):
                    avg=avg+self._measure_counts()
                    qt.msleep(0.1)
                avg=avg/counts_avg
                y = avg
                if (y<min_count_break) or (y > self.get_cnt_threshold())  or  (msvcrt.kbhit() and msvcrt.getch() =='q'):
                    self._set_red_power(0)
                    i=-1 #stop!
                    break
                if(y>y1): break
                y1=y
                qt.msleep(0.1)
                i=i+1
                #print i
            if i>2: 
                self.move(waveplate,-d*stepsize, **kw)
                break
            if i<0:
                break

    def brent_bound_optimize(self,waveplate,max_range=10.,tolerance=0.5,max_cycles=20,counts_avg=30,**kw):
        self._x0=0
        def f(x):
            if (msvcrt.kbhit() and msvcrt.getch() =='q'):
                raise Exception('User abort')
            avg = 0.
            print x
            self.move(waveplate,x-self._x0, **kw)
            self._x0=x
            for j in range(counts_avg):
                    avg=avg+self._measure_counts()
                    qt.msleep(0.1)
            avg=avg/counts_avg
            print avg
            return avg
        try: 
            optimize.fminbound(f,-max_range/2.,max_range/2.,xtol=tolerance, maxfun=max_cycles)
        except:
            print "error:", sys.exc_info()[0]

    def nd_optimize(self,max_range=10.,stepsize=1.0,max_cycles=20,counts_avg=30,min_counts=20,method=0,**kw):
        self._x0=np.zeros(len(self._waveplates))
        def f(x):
            if (msvcrt.kbhit() and msvcrt.getch() =='q'):
                raise Exception('User abort')
            avg = 0.
            print x
            for i,wp in enumerate(self._waveplates):
                self.move(wp,x[i]-self._x0[i], **kw)
            self._x0=x
            for j in range(counts_avg):
                    avg=avg+self._measure_counts()
                    qt.msleep(0.1)
            avg=avg/counts_avg
            print avg
            return avg
       # try: 
        xg=np.zeros(len(self._waveplates))
        bounds=[(-max_range/2.,max_range/2.) for i in range(len(self._waveplates))]
        #optimize.fmin(f,xg,xtol=stepsize, maxfun=max_cycles)
        if method == 0:
            x_opt,f_opt,self._powell_direc,_tmp0,_tmp1,_tmp2 = optimize.fmin_powell(f, xg, xtol=stepsize, maxfun=max_cycles, direc=self._powell_direc)
        elif method==1:
            x_opt,f_opt,_tmp1 = optimize.fmin_tnc(f, xg, approx_grad=True, bounds=bounds, epsilon=stepsize, xtol=stepsize)
        elif method==2:
            x_opt, f_opt,self._powell_direc = self._nd_optimize_user(f, xg, stepsize=stepsize,max_range=max_range,min_val=min_counts)

        print 'optimize result: ', x_opt, f_opt
        #print 'current position: ', self._x0
        #except:
        #    print "error:", sys.exc_info()[0]

    def reset_wp_channel(self):
        self._prev_wp_channel = 'none'

    def _nd_optimize_user(self,f,xg, stepsize=1.,max_range=10, min_val=20):
        D= len(xg)
        f0 = f(xg)
        if f0 < min_val:
            return xg, f0, np.zeros(D)
        fcur = f0
        X = xg
        fgrad=np.zeros(D)
        for d in range(D):
            X=X+np.eye(D)[d]*stepsize*2.
            fval = f(X)
            fgrad[d] = (fcur-fval)
            fcur=fval
        fgrad_norm = fgrad / np.linalg.norm(fgrad)

        for i in np.arange(np.floor(max_range/stepsize)):
            X = X + fgrad_norm*stepsize
            fval = f(X)
            if (fval<min_val) or (fval > self.get_cnt_threshold())  or  (msvcrt.kbhit() and msvcrt.getch() =='q'):
                        self._set_red_power(0)
                        i=-1 #stop!
                        break
            if(fval>fcur): break
            fcur=fval
            qt.msleep(0.05)

                    #print i
        if i>0: 
            X = X - fgrad_norm*stepsize
            fval = f(X)

        return X, fval, fgrad_norm



