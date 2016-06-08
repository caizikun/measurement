# optimizer for LT2
#
# author: wolfgang <w dot pfaff at tudelft dot nl>

from instrument import Instrument
import types
import qt
import msvcrt

from measurement.lib.config import optimiz0rs as optcfg
reload(optcfg)

class optimiz0r(Instrument):
    
   
    def __init__(self, name, opt1d_ins=qt.instruments['opt1d_counts'], 
            mos_ins=qt.instruments['master_of_space'],
            dimension_set='lt2'):
        Instrument.__init__(self, name)

        self.add_function('optimize')
        self.opt1d_ins = opt1d_ins
        self.dimensions = optcfg.dimension_sets[dimension_set]

        self.mos = mos_ins
       
    def optimize(self, cycles=1, cnt=1, int_time=50, dims=[], order='xyz', **kw):
        ret=True
        for c in range(cycles):
           
            if len(dims) == 0:
                dims = self.dimensions[order]

            gaussian_fit_init = self.opt1d_ins.get_gaussian_fit()

            for d in dims:
                if d == 'z':
                    gaussian_fit = kw.pop('gaussian_fit_Z', gaussian_fit_init)
                else:
                    gaussian_fit = gaussian_fit_init
                
                ret=ret and self.opt1d_ins.run(dimension=d, counter = cnt, 
                        pixel_time=int_time, gaussian_fit = gaussian_fit, **self.dimensions[d])
                qt.msleep(1.0)

                

                if msvcrt.kbhit():
                    kb_char=msvcrt.getch()
                    if kb_char == "q" : break
                    
            if msvcrt.kbhit():
                kb_char=msvcrt.getch()
                if kb_char == "q" : break

            self.opt1d_ins.set_gaussian_fit(gaussian_fit_init)
        
        return ret
    
