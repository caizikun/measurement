from analysis.lib.fitting import common,fit

qt.instruments['signalhound'].set_frequency_center(135e6)
qt.instruments['signalhound'].set_frequency_span(5e6) 
qt.instruments['signalhound'].set_rbw(25e3)
qt.instruments['signalhound'].set_vbw(25e3)
qt.instruments['signalhound'].ConfigSweepMode()
freq,mi,ma=qt.instruments['signalhound'].GetSweep(do_plot=True, max_points=650)

f = common.fit_lorentz

#f = a + 2*A/np.pi*gamma/(4*(x-x0)**2+gamma**2)
#args = ['g_a', 'g_A', 'g_x0', 'g_gamma']
x = freq/1e6
y = mi


args=[y[0], np.max(y), x[np.argmax(y)], 0.4]
fitres = fit.fit1d(x, y, f, *args, fixed = [],
                   do_print = True, ret = True, maxfev=100)