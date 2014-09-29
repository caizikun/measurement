
if True:
    _setctrl_gate = lambda x: qt.instruments['ivvi'].set_dac3(x)
    _getval_gate = lambda: qt.instruments['physical_adwin'].Get_FPar(79)
    _getctrl_gate=  lambda: qt.instruments['ivvi'].get_dac3()
    pidgate = qt.instruments.create('pidgate', 'pid_controller_v4', 
            set_ctrl_func=_setctrl_gate , get_val_func=_getval_gate , get_ctrl_func=_getctrl_gate, 
            ctrl_minval=-1600, ctrl_maxval=-1200)

if True:
    _setctrl_yellow_freq = lambda x: qt.instruments['physical_adwin'].Set_FPar(52,x)
    _getval_yellow_freq = lambda: qt.instruments['physical_adwin'].Get_FPar(78)
    _getctrl_yellow_freq=  lambda: qt.instruments['physical_adwin'].Get_FPar(42)
    pidyellowfrq = qt.instruments.create('pidyellowfrq', 'pid_controller_v4', 
            set_ctrl_func=_setctrl_yellow_freq , get_val_func=_getval_yellow_freq , get_ctrl_func=_getctrl_yellow_freq, 
            ctrl_minval=15., ctrl_maxval=35.)

if True:
    set_eprime_func = lambda x: qt.instruments['physical_adwin'].Set_FPar(51,x)
    get_eprime_func = lambda: qt.instruments['physical_adwin'].Get_FPar(41)
    get_E_y_func = lambda: qt.instruments['physical_adwin'].Get_FPar(44)
    get_Y_func= lambda: qt.instruments['physical_adwin'].Get_FPar(42)
    e_primer = qt.instruments.create('e_primer', 'E_primer', 
        set_eprime_func=set_eprime_func,
        get_eprime_func=get_eprime_func,
        get_E_func=get_E_y_func,
        get_Y_func=get_Y_func)