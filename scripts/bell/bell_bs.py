import qt
import numpy as np
import bell

bell.Bell_BS.remote_measurement_helper = qt.instruments['remote_measurement_helper']
def remote_HH_measurement(name):

    m=bell.Bell_BS(qt.instruments['remote_measurement_helper'].get_measurement_name())
    m.params['MAX_DATA_LEN']        =   int(100e6)
    m.params['BINSIZE']             =   1  #2**BINSIZE*BASERESOLUTION
    m.params['MIN_SYNC_BIN']        =   5000 
    m.params['MAX_SYNC_BIN']        =   7000 
    m.params['measurement_time']    =   1200 #sec
    m.params['measurement_abort_check_interval']    = 1. #sec
    m.run()
    m.finish()
    
if __name__ == '__main__':
    remote_HH_measurement('test')