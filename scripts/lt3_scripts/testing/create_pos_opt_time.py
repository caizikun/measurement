import gobject
import qt

def optimize_postions():
	if qt.instruments['adwin'].get_process_status('singleshot') !=0:
	
		qt.instruments['physical_adwin'].Set_Par(64,1)
		qt.instruments['physical_adwin'].Set_Par(65,1)
		qt.msleep(2)
		qt.instruments['physical_adwin'].Set_Par(64,1)
		qt.instruments['physical_adwin'].Set_Par(65,1)
		qt.msleep(2)
		qt.instruments['physical_adwin'].Set_Par(64,1)
		qt.instruments['physical_adwin'].Set_Par(65,1)
		print 'position optimizing...'
		return True
	print 'position opt stopped.'
	return False

gobject.timeout_add(int(30*1e3), optimize_postions)