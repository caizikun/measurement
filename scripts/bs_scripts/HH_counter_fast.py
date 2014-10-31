import msvcrt
from measurement.lib.measurement2.pq import pq_measurement
import numpy as np

def measure_and_broadcast_countrates(): #TODO clean up print and debug statements

	meas_time = 10000 * 1e3 #s
	approx_int_time  = 0.1#s
	PQ_ins = qt.instruments['HH_400']

	adwin_ins_lt1 = qt.instruments['physical_adwin_lt1']
	adwin_ins_lt3 = qt.instruments['physical_adwin_lt3']

	adwin_par_lt1 = 43
	adwin_par_lt3 = 43

	meas_helper = qt.instruments['remote_measurement_helper']



	if PQ_ins.OpenDevice():
	    PQ_ins.start_T2_mode()
	    if hasattr(PQ_ins,'calibrate'):
	        PQ_ins.calibrate()
	    PQ_ins.set_Binning(10)
	    #print PQ_ins.get_ResolutionPS()
	else:
	    raise(Exception('Picoquant instrument '+PQ_ins.get_name()+ ' cannot be opened: Close the gui?'))

	bin_time=PQ_ins.get_BaseResolutionPS()*1e-12
	wraparound = PQ_ins.get_T2_WRAPAROUND()
	t2_time_factor = PQ_ins.get_T2_TIMEFACTOR()
	ttrreadmax= 131072

	PQ_ins.StartMeas(int(meas_time))
	qt.msleep(approx_int_time)
	#ofl=0
	#cts0=0
	#cts1=0
	#ii=0
	while(PQ_ins.get_MeasRunning()):
		if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
		if not(meas_helper.get_is_running()): break

		length, data = PQ_ins.get_TTTR_Data()
		event_time, channel, special = pq_measurement.PQ_decode(data[:length])
		if length > 2:
			if length > 131070:
				print 'WARNING: TTTR length == max TTTR length. get TTTR rate to slow?'
			#for i in range(length):
			#	if special[i] == 0 and channel[i]==0:
			#		cts0+=1
			#	if special[i] == 0 and channel[i]==1:
			#		cts1+=1
			#		#print event_time[i]
			#		#break
			#	if len(special)!=len(channel):
			#		print 'len_error'
			#ofl=special
			#cts0=channel

			#ii+=len(special)
			
			#ofl+=len(np.where(np.logical_and(special == 1, channel == 63))[0])
			#cts0+=len(np.where(np.logical_and(special == 0, channel == 0))[0])
			#cts1+=len(np.where(np.logical_and(special == 0, channel == 1))[0])
			#print np.sum(event_time)
			#print len(np.where(channel == 63)[0])

			#print event_time[1:20]
			#print len(np.where(special == 1)[0])
			#print len(np.where(special == 0)[0])
			#print len(np.where(np.logical_and(special == 0, channel == 0))[0])
			#print len(np.where(np.logical_and(special == 0, channel == 1))[0])
			#print len(np.where(np.logical_and(special == 0, channel > 1))[0])

			int_time = wraparound * len(np.where(channel == 63)[0]) / t2_time_factor * bin_time
			ch0_countrates = float(len(np.where(np.logical_and(special == 0, channel == 0))[0]))/(int_time)
			ch1_countrates = float(len(np.where(np.logical_and(special == 0, channel == 1))[0]))/(int_time)
			#print ch0_countrates, ch1_countrates
			adwin_ins_lt1.Set_Par(adwin_par_lt1, int(ch0_countrates+ch1_countrates))
			adwin_ins_lt3.Set_Par(adwin_par_lt3, int(ch0_countrates+ch1_countrates))
			qt.msleep(approx_int_time)

	#print ofl, cts0, cts1, ii
	PQ_ins.StopMeas()
	meas_helper.set_is_running(False)


if __name__=='__main__':
	qt.instruments['broadcast0r'].stop()
	measure_and_broadcast_countrates()
	#qt.instruments['broadcast0r'].start()