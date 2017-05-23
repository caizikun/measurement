# Virtual adwin instrument, adapted from lt2 to fit qn1, may 2017
import os
import types
import qt
import numpy as np
from instrument import Instrument
import time
from lib import config

from measurement.instruments.adwin import adwin
from measurement.lib.config import adwins as adwinscfg


class adwin_qn1(adwin):
    def __init__(self, name, **kw):
        adwin.__init__(self, name, 
                adwin = qt.instruments['physical_adwin'], 
                processes = adwinscfg.config['adwin_pro_processes'],
                default_processes=['set_dac', 'set_dio'], 
                dacs=adwinscfg.config['adwin_qn1_dacs'], 
                tags=['virtual'],
                process_subfolder = qt.config['adwin_pro_subfolder'], **kw)
        