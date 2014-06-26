import qt
import numpy as np
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.pq.pq_measurement as pq

debug=False
m=pq.PQMeasurement('test')
m.params['MAX_DATA_LEN']        =   int(100e6)
m.params['BINSIZE']             =   1  #2**BINSIZE*(BASERESOLUTION = 1 ps for HH)
m.params['MIN_SYNC_BIN']        =   0 #5 us 
m.params['MAX_SYNC_BIN']        =   3000 #1 us per opt pi pulse
m.params['measurement_time']    =   24*60*60 #sec = 24H
m.params['measurement_abort_check_interval']    = 1 #sec
m.run(debug=debug)
m.finish()