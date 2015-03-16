
#Stabilize the gate using information from the gate modulation:
# tuning D1 with the signal of the D1 gate
if True:
    _setctrl_gate = lambda x: qt.instruments['ivvi'].set_dac3(x)
    _getval_gate = lambda: qt.instruments['physical_adwin'].Get_FPar(79)
    _getctrl_gate=  lambda: qt.instruments['ivvi'].get_dac3()
    pidgate = qt.instruments.create('pidgate', 'pid_controller_v4', 
            set_ctrl_func=_setctrl_gate , get_val_func=_getval_gate , get_ctrl_func=_getctrl_gate, 
            ctrl_minval=-600, ctrl_maxval=0)

#Stabilize the Yellow frequency using information from the yellow AOM modulation:
if True:
    _setctrl_yellow_freq = lambda x: qt.instruments['physical_adwin'].Set_FPar(52,x)
    _getval_yellow_freq = lambda: qt.instruments['physical_adwin'].Get_FPar(78)
    _getctrl_yellow_freq=  lambda: qt.instruments['physical_adwin'].Get_FPar(42)
    pidyellowfrq = qt.instruments.create('pidyellowfrq', 'pid_controller_v4', 
            set_ctrl_func=_setctrl_yellow_freq , get_val_func=_getval_yellow_freq , get_ctrl_func=_getctrl_yellow_freq, 
            ctrl_minval=0., ctrl_maxval=35.)

#Stabilize the Newfocus frequency using information from the taper & yellow frequencies (measured on local WM):
if True:
    set_eprime_func = lambda x: qt.instruments['physical_adwin'].Set_FPar(51,x)
    get_eprime_func = lambda: qt.instruments['physical_adwin'].Get_FPar(41)
    get_E_y_func = lambda: qt.instruments['physical_adwin'].Get_FPar(43)
    get_Y_func= lambda: qt.instruments['physical_adwin'].Get_FPar(42)
    set_strain_splitting_func = lambda x: qt.instruments['physical_adwin'].Set_FPar(77,x)
    e_primer = qt.instruments.create('e_primer', 'E_primer', 
        set_eprime_func=set_eprime_func,
        get_eprime_func=get_eprime_func,
        get_E_func=get_E_y_func,
        get_Y_func=get_Y_func,
        set_strain_splitting_func=set_strain_splitting_func)

####################################################################################


# tuning D3 with the signal of the D1 gate
if False:
    _setctrl_gate = lambda x: qt.instruments['ivvi'].set_dac2(x)
    _getval_gate = lambda: qt.instruments['physical_adwin'].Get_FPar(79)
    _getctrl_gate=  lambda: qt.instruments['ivvi'].get_dac2()
    pidgate = qt.instruments.create('pidgate', 'pid_controller_v4', 
            set_ctrl_func=_setctrl_gate , get_val_func=_getval_gate , get_ctrl_func=_getctrl_gate, 
            ctrl_minval=-400, ctrl_maxval=600)


#Stabilize the gate using information from the gate modulation:
# tuning MW with the signal of the D1 gate
if False:
    _setctrl_gate = lambda x: qt.instruments['ivvi'].set_dac4(x)
    _getval_gate = lambda: qt.instruments['physical_adwin'].Get_FPar(79)
    _getctrl_gate=  lambda: qt.instruments['ivvi'].get_dac4()
    pidgate = qt.instruments.create('pidgate', 'pid_controller_v4', 
            set_ctrl_func=_setctrl_gate , get_val_func=_getval_gate , get_ctrl_func=_getctrl_gate, 
            ctrl_minval=-200, ctrl_maxval=500)




#Stabilize the Taper frequency using information from the gate modulation:
if False:
    _setctrl_taper_freq = lambda x: qt.instruments['physical_adwin'].Set_FPar(53,x)
    _getval_taper_freq = lambda: qt.instruments['physical_adwin'].Get_FPar(79)
    _getctrl_taper_freq=  lambda: qt.instruments['physical_adwin'].Get_FPar(44)
    pidtaperfrq = qt.instruments.create('pidtaperfrq', 'pid_controller_v4', 
            set_ctrl_func=_setctrl_taper_freq , get_val_func=_getval_taper_freq , get_ctrl_func=_getctrl_taper_freq, 
            ctrl_minval=53., ctrl_maxval=62.)