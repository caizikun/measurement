pidtaper.save_cfg()
pidtaper.stop()
taper_local=True
if taper_local:
    _getval_ta = lambda: ((wavemeter.Get_Frequency(wm_channel_ta)-470.40)*1e3) 
    pidtaper = qt.instruments.create('pidtaper', 'pid_controller_v4', \
        set_ctrl_func=_setfrq_ta, get_ctrl_func=_getfrq_ta, \
        set_ctrl_func_coarse=_setfrq_coarse_ta, get_ctrl_func_coarse=_getfrq_coarse_ta, \
        get_val_func=_getval_ta)
else:
    _getval_ta = lambda: ((wavemeter.Get_Frequency(wm_channel_ta)-470.40)*1e3) 
    _getval_ta_fine  = lambda: physical_adwin_lt3.Get_FPar(44)
    pidtaper = qt.instruments.create('pidtaper', 'pid_controller_v5', \
        set_ctrl_func=_setfrq_ta, get_ctrl_func=_getfrq_ta, \
        set_ctrl_func_coarse=_setfrq_coarse_ta, get_ctrl_func_coarse=_getfrq_coarse_ta, \
        get_val_func=_getval_ta,get_val_func_fine=_getval_ta_fine)
    

    #_getval_ta = lambda: physical_adwin_lt3.Get_FPar(48)
    #pidtaper = qt.instruments.create('pidtaper', 'pid_controller_v4', \
    #    set_ctrl_func=_setfrq_ta, get_ctrl_func=_getfrq_ta, \
    #    set_ctrl_func_coarse=_setfrq_coarse_ta, get_ctrl_func_coarse=_getfrq_coarse_ta, \
    #    get_val_func=_getval_ta)

