
if True:
    _setctrl_gate = lambda x: qt.instruments['ivvi'].set_dac4(x)
    _getval_gate = lambda: qt.instruments['physical_adwin'].Get_FPar(79)
    _getctrl_gate=  lambda: qt.instruments['ivvi'].get_dac4()
    pidgate = qt.instruments.create('pidgate', 'pid_controller_v4', 
            set_ctrl_func=_setctrl_gate , get_val_func=_getval_gate , get_ctrl_func=_getctrl_gate, 
            ctrl_minval=200.0, ctrl_maxval=400.0)

if True:
    _setctrl_yellow_freq = lambda x: qt.instruments['physical_adwin_lt2'].Set_FPar(52,x)
    _getval_yellow_freq = lambda: qt.instruments['physical_adwin'].Get_FPar(78)
    _getctrl_yellow_freq=  lambda: qt.instruments['physical_adwin_lt2'].Get_FPar(42)
    pidgate = qt.instruments.create('pidyellowfrq', 'pid_controller_v4', 
            set_ctrl_func=_setctrl_yellow_freq , get_val_func=_getval_yellow_freq , get_ctrl_func=_getctrl_yellow_freq, 
            ctrl_minval=27., ctrl_maxval=35.)