"""
"""

import numpy as np
import qt
import msvcrt
import time
# from measurement.lib.measurement2.adwin_ssro import pulsar_msmt

# from measurement.lib.tools import magnet_tools as mt; reload(mt)
mom = qt.instruments['master_of_magnet']; 


if __name__ == '__main__':

    print time.asctime()
    
    #create the data lists
    d_steps = 20
    #turn on magnet stepping in Z
    mom.set_mode('all', 'stp')



    mom.step('X_axis',d_steps)
    mom.step('Y_axis',d_steps)
    mom.step('Z_axis',d_steps)
    mom.step('X_axis',-1*d_steps)
    mom.step('Y_axis',-1*d_steps)
    mom.step('Z_axis',-1*d_steps)

    mom.set_mode('all', 'gnd')