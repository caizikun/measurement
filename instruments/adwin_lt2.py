# Virtual adwin instrument, adapted from rt2 to fit lt2, dec 2011 
import os
import types
import qt
import numpy as np
from instrument import Instrument
import time
from lib import config

from measurement.instruments.adwin import adwin
from measurement.lib.config import adwins as adwinscfg


class adwin_lt2(adwin):
    def __init__(self, name, **kw):
        adwin.__init__(self, name, 
                adwin = qt.instruments['physical_adwin'], 
                processes = adwinscfg.config['adwin_lt2_processes'],
                default_processes=['counter', 'set_dac', 'set_dio', 'linescan',
                    'DIO_test'], 
                dacs=adwinscfg.config['adwin_lt2_dacs'], 
                tags=['virtual'],
                process_subfolder = qt.config['adwin_lt2_subfolder'], **kw)