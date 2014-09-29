import msvcrt
import gobject

def do_optimize():
	print 'optimizing'
	physical_adwin.Set_Par(59,1)
	qt.msleep(20)
	physical_adwin.Set_Par(59,0)
	return False

physical_adwin.Set_Par(59,0)

for j in range(100):
	if (msvcrt.kbhit() and (msvcrt.getch() == 'x')): 
		break
	gobject.timeout_add(int(20*60*1e3),\
            do_optimize)
	
	if not optimiz0r.optimize(dims=['x','y','z'],cnt=1,int_time=100,cycles=1):
		break
	qt.msleep(10)
	counters.set_is_running(False)
	qt.msleep(1)


