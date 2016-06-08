# counter panel for RT2
#
# Author: Wolfgang Pfaff <w.pfaff@tudelft.nl>

from panel import Panel
from ui_counters import Ui_Panel
import qt
import adwins as adwinscfg
# import adwin


from PyQt4 import QtCore

class CounterPanel(Panel):
    def __init__(self, parent, *arg, **kw):
        Panel.__init__(self, parent, *arg, **kw)

        # designer ui:
        self.ui = Ui_Panel()
        self.ui.setupUi(self)

        # self._adwin = qt.instruments[adwin]

        # adwin = qt.instruments['adwin']
        physical_adwin = qt.instruments.create('physical_adwin','ADwin_Gold_I',address=1)
        # physical_adwin = qt.instruments.create('physical_adwin','adwin',address=1)

        adwin = qt.instruments.create('adwin', 'adwin', 
                adwin=physical_adwin,
                processes = adwinscfg.config['adwin_telecom_processes'],
                default_processes = ['set_dac', 'read_adc'], 
                dacs = adwinscfg.config['adwin_telecom_dacs'],
                tags = ['virtual'],
                process_subfolder = 'adwin_gold_1',)

        for p in [self.ui.plot1, self.ui.plot2]:
            p.left_axis.title = 'counts [Hz]'
            p.plot.padding = 5
            p.plot.padding_bottom = 30
            p.plot.padding_left = 100
            plot = p.plot.plots['trace'][0]
            plot.padding = 0
            plot.color = 'green'
            plot.marker = 'circle'
            plot.marker_size = 3
            

        for c in [self.ui.counts1, self.ui.counts2]:
            c.setText('0.0')

        # set other defaults
        self.ui.plot1.display_time = 20
        self.ui.plot2.display_time = 20
        self.ui.t_range.setValue(20)
        print "Test2"
        # print adwin.Get_FPar(14)
        # print adwin.get_read_adc_var('fpar')[0][1]
        

    def _instrument_changed(self, changes):

        if changes.has_key('cntr1_countrate'):
            self.ui.counts1.setText('%1.2E' % changes['cntr1_countrate'])
            self.ui.plot1.add_point(changes['cntr1_countrate'])

        if changes.has_key('cntr2_countrate'):
            self.ui.counts2.setText('%1.2E' % changes['cntr2_countrate'])
            self.ui.plot2.add_point(changes['cntr2_countrate'])   

