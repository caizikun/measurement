import scipy.misc as ms

picture_fp = r'D:\dm.png'

im = ms.imread(picture_fp, flatten=True)
im_sml=ms.imresize(im,(12,12)).astype(np.uint8)
imnorm = im_sml/3
im_v=dm.voltages_from_matrix(imnorm)
dm.set_cur_voltages(im_v)