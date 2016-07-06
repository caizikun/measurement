wp='zpl_half'
quick_scan = False
for i in range(10):
	rejecter.move(wp,1,quick_scan=quick_scan)
	qt.msleep(0.1)
for i in range(10):
	rejecter.move(wp,-1,quick_scan=quick_scan)
	qt.msleep(0.1)