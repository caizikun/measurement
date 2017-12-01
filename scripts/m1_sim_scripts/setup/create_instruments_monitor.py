from measurement.lib.config import adwins as adwinscfg

### Keithley 2000 DMM for monitoring temperatures
# kei2000 = qt.instruments.create('kei2000', 'Keithley_2000', address = 'GPIB::16::INSTR')
# kei2000.set_channel(5)
# kei2000.set_mode_fres()
# kei2000.set_range(100)
# kei2000.set_nplc(10)
# kei2000.set_trigger_continuous(True)
# kei2000.set_averaging(True)
# kei2000.set_averaging_type('moving')
# kei2000.set_averaging_count(50)

# physical_adwin = qt.instruments.create('physical_adwin','ADwin_Pro_II',
#         address=1,processor_type=1012)

# adwin = qt.instruments.create('adwin', 'adwin', 
#                 adwin = qt.instruments['physical_adwin'], 
#                 processes = adwinscfg.config['adwin_m1_processes'],
#                 default_processes=['counter', 'set_dac', 'set_dio', 'linescan'], 
#                 dacs=adwinscfg.config['adwin_m1_dacs'], 
#                 tags=['virtual'],
#                 process_subfolder = 'adwin_pro_2_m1')

# ## why "default_processes=['set_dac', 'set_dio']," and "use_cfg=False" were added/changed here? THT

# wavemeter = qt.instruments.create('wavemeter','WSU_WaveMeter')

# repump_laser = qt.instruments.create('repump_laser','toptica_DLpro',
#     address = '192.168.0.113')

# wm_channel_nf = 1
# _setfrq_nf = lambda x: adwin.set_dac_voltage(('newfocus_frq',x))
# _getfrq_nf = lambda: adwin.get_dac_voltage('newfocus_frq')
# #_setfrq_coarse_nf = lambda x: labjack.set_bipolar_dac2(x)
# #_getfrq_coarse_nf = lambda: labjack.get_bipolar_dac2()
# _getval_nf = lambda: wavemeter.Get_Frequency(wm_channel_nf)
# pidnewfocus = qt.instruments.create('pidnewfocus', 'pid_controller_v4', \
#         set_ctrl_func=_setfrq_nf, get_ctrl_func=_getfrq_nf, \
#         ctrl_minval=-9,ctrl_maxval=9 ,
#         get_val_func=_getval_nf)
#         #set_ctrl_func_coarse=_setfrq_coarse_nf, get_ctrl_func_coarse=_getfrq_coarse_nf, \

# ### There are two options for the DL PRO frequency stabilization 
# ### 1. use the adwin
# # wm_channel_DLpro = 2
# # _setfrq_DLpro = lambda x: adwin.set_dac_voltage(('DLpro_frq',x))
# # _getfrq_DLpro = lambda: adwin.get_dac_voltage('DLpro_frq')
# # _getval_DLpro = lambda: wavemeter.Get_Frequency(wm_channel_DLpro)
# # pidDLpro = qt.instruments.create('pidDLpro', 'pid_controller_v4', \
# #         set_ctrl_func=_setfrq_DLpro, get_ctrl_func=_getfrq_DLpro, \
# #         ctrl_minval=-4,ctrl_maxval=4,
# #         get_val_func=_getval_DLpro)

# ### 2. directly from the computer
# wm_channel_DLpro = 2
# conversion_factor = 14. # factor inserted to match the discrepancy between pid range 10V and V range 150V. Maximum at 10V
# _setfrq_DLpro = lambda x: repump_laser.set_piezo_voltage(conversion_factor*x)
# _getfrq_DLpro = lambda: repump_laser.get_piezo_voltage()/conversion_factor
# #_getval_DLpro = lambda: physical_adwin.Get_FPar(43)
# _getval_DLpro = lambda: wavemeter.Get_Frequency(wm_channel_DLpro)
# pidDLpro = qt.instruments.create('pidDLpro', 'pid_controller_v4', \
#         set_ctrl_func=_setfrq_DLpro, get_ctrl_func=_getfrq_DLpro, \
#         set_ctrl_func_coarse=None, get_ctrl_func_coarse=None,
#         ctrl_minval=0,ctrl_maxval=10, \
#         get_val_func=_getval_DLpro)




# broadcast0r = qt.instruments.create('broadcast0r', 'broadcast0r')
# broadcast0r.add_broadcast('wm_ch1', lambda: wavemeter.Get_Frequency(1), lambda x: physical_adwin.Set_FPar(41, (x-470.40)*1e3 ))
# broadcast0r.add_broadcast('wm_ch2', lambda: wavemeter.Get_Frequency(2), lambda x: physical_adwin.Set_FPar(43, (x-470.40)*1e3 ))
# # broadcast0r.add_broadcast('wm_ch2', lambda: wavemeter.Get_Frequency(2), lambda x: physical_adwin.Set_FPar(42, (x-521.22)*1e3 ))
# #broadcast0r.add_broadcast('wm_ch3', lambda: wavemeter.Get_Frequency(3), lambda x: physical_adwin_lt2.Set_FPar(43, (x-470.40)*1e3 ))
# #broadcast0r.add_broadcast('wm_ch4', lambda: wavemeter.Get_Frequency(4), lambda x: physical_adwin_lt3.Set_FPar(44, (x-470.40)*1e3 ))
# #broadcast0r.add_broadcast('wm_ch5', lambda: wavemeter.Get_Frequency(5), lambda x: physical_adwin_lt2.Set_FPar(45, (x-470.40)*1e3 ))
# #broadcast0r.add_broadcast('wm_ch6', lambda: wavemeter.Get_Frequency(6), lambda x: physical_adwin_lt1.Set_FPar(46, (x-470.40)*1e3 ))
# #broadcast0r.add_broadcast('wm_ch8', lambda: wavemeter.Get_Frequency(8), lambda x: physical_adwin_lt3.Set_FPar(48, (x-470.40)*1e3 ))
# broadcast0r.add_broadcast('pidnewfocus_setpoint', lambda: physical_adwin.Get_FPar(51), lambda x: pidnewfocus.set_setpoint(x), lambda x: x != 0.)
# broadcast0r.add_broadcast('pidDLpro_setpoint', lambda: physical_adwin.Get_FPar(53), lambda x: pidDLpro.set_setpoint(x), lambda x: x != 0.)
# broadcast0r.start()