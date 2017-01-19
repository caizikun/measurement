import numpy as np
import matplotlib.pyplot as plt
import h5py
import sys
import os
# %matplotlib inline
sys.path.append('D:/measuring')
execfile('D:/measuring/analysis/scripts/setup_analysis.py')

import analysis.scripts.Fabrication.Display_scan2d as ds
from skimage.feature import blob_dog #, blob_log, blob_doh

folder = 'D:\measuring\data/20161220/132350_scan2d_'
d = ds.DisplayScan(folder)
x,y,c = d.get_data()
plt.imshow(c)
im = c/np.max(c)

blobs_dog = blob_dog(im, max_sigma=2.5,min_sigma = 0.5, threshold=.1, overlap = 0.5)

blobs_dog[:, 2] = blobs_dog[:, 2] * np.sqrt(2)

fig,ax = plt.subplots(1, 1,subplot_kw={'adjustable':'box-forced'})
ax.imshow(im, interpolation='nearest')
for blob in blobs_dog:
        ys, xs, r = blob
        c = plt.Circle((xs, ys), r, color='red', linewidth=2, fill=False)
        ax.add_patch(c)

plt.show()

from measurement.scripts.rt2_scripts.scanning.scan_diff_focus_change_green_power_MJD import scan_diff_focus_change_green_power
scan_diff_focus_change_green_power(50,10,100,1000,10000)