

int_time = 100
counter = 1
max_cycles = 200
tolerance = 0.01



pos = okotech_dm.get_voltages()


def f(pos):
	okotech_dm.set_voltage_all_pins(pos)
	qt.msleep(0.1)
	cnt_rts = adwin.measure_counts(int_time)[counter-1]/(int_time*1e-3)
	print 'count rate', cnt_rts
	return cnt_rts


new_pos = optimize.fmin(f,pos,maxfun=max_cycles, xtol=tolerance, retall=False)
#new_pos = optimize.fmin_powell(f,pos,maxfun=max_cycles, xtol=tolerance, retall=False)