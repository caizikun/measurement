import os
import qt
import numpy as np

from lib.math import fit

from lib.measurement2.measurement import Measurement

CTR = qt.instruments['counters']
GETCTS = CTR.get_cntr1_countrate

AOM = qt.instruments['AOM']

MOS = qt.instruments['master_of_space']
MOV_X = MOS.step_x
MOV_Y = MOS.step_y
def step((x, y)):
    MOV_X(x); MOV_Y(y)
    return

def backstep((x,y)):
    step((-x,-y))
    return

class SaturationMeasurement(Measurement):

    do_bg = True

    def __init__(self, name):
        Measurement.__init__(self, name, mclass='Saturation')

        AOM.set_power(0.)
        qt.msleep(0.1)

    def measure(self, bgstep=(1,1), maxpower=1.5e-3, steps=51):
        d = qt.Data(name=self.save_filebase)
        d.add_coordinate('power (W)')
        d.add_value('counts (Hz)')
        d.create_file()
        self.save_folder = d.get_dir()
        p = qt.plot(d, name='Cts vs power', clear=True)
        
        totalcts = self._loop(maxpower,steps,d)
        
        AOM.set_power(0.)
        qt.msleep(0.1)

        if self.do_bg:
            step(bgstep)
            
            f = qt.Data(name=self.save_filebase+'_background')
            f.add_coordinate('power (W)')
            f.add_value('counts [Hz]')
            f.create_file()
            
            p.add_data(f)

            bgcts = self._loop(maxpower,steps,f)
            
            backstep(bgstep)
            AOM.set_power(0.)
            qt.msleep(0.1)

            return np.linspace(0.,maxpower,steps), totalcts,bgcts
        else:
            return np.linspace(0.,maxpower,steps), totalcts
        
        d.close_file()
        f.close_file()

    def _loop(self,maxpower, steps, data=None):
        cts = np.array([])        
        for p in np.linspace(0.,maxpower,steps):
            AOM.set_power(p)
            qt.msleep(0.1)
            c = GETCTS()
            if data != None:
                data.add_data_point(p,c)
            cts = np.append(cts, c)
            qt.msleep(0.1)
        return cts

    def analyze(self, pwr, cts, bg):
        sig = cts-bg

        ff = lambda p,x: (p[0] * x) / (p[1] + x)
        p0 = [800e3, 20e-6]
        fres = fit.fit(ff, pwr, sig, p0)
        p = fres.get_fit_params()

        print 'fit result:', p

        plt = qt.plot(pwr, sig, name='Saturation Analysis', title='signal',
                clear=True)
        plt.add(pwr, cts, title='total')
        plt.add(pwr, ff(p, pwr), title='fit')
        plt.add(pwr, sig.astype(float)/bg.astype(float), title='s/bg',
                right=True)
        plt.save_png(os.path.join(self.save_folder, self.save_filebase))

        return

if __name__ == '__main__':
    m = SaturationMeasurement('Cavity_membrane_big_nothing')
    p,c,bg = m.measure(bgstep=(1.5,1.5),steps=41,maxpower=400e-6)
    m.analyze(p,c,bg)

