
import numpy as np
from measurement.lib.cavity import simple_XY_scan as XYscan

scan = XYscan.simple_XY_scan (name='')
scan.set_integration_time()
scan.scan (x_min=0., x_max=0.010, y_min=0., y_max=0.010, z=0.05, nr_x_points=11, nr_y_points=11, do_save=True)
