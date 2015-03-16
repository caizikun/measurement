if True:
    _setctrl_gate = lambda x: qt.instruments['adwin'].set_dac_voltage(('gate',x))
    _getctrl_gate=  lambda: qt.instruments['adwin'].get_dac_voltage('gate')
    _getval  = lambda: qt.instruments['physical_adwin'].Get_Par(70)
    _getnorm = lambda: qt.instruments['physical_adwin'].Get_Par(72)
    gate_optimizer = qt.instruments.create('gate_optimizer', 'simple_optimizer', 
            set_control_f=_setctrl_gate, get_control_f=_getctrl_gate, 
            get_value_f=_getval, get_norm_f=_getnorm, 
            plot_name='gate_plot')

#if True:
    _setctrl_yellow_freq = lambda x: qt.instruments['physical_adwin'].Set_FPar(52,x)
    _getctrl_yellow_freq=  lambda: qt.instruments['physical_adwin'].Get_FPar(42)
    _getval  = lambda: qt.instruments['physical_adwin'].Get_Par(76)
    _getnorm = lambda: qt.instruments['physical_adwin'].Get_Par(71)
    yellowfrq_optimizer = qt.instruments.create('yellowfrq_optimizer', 'simple_optimizer',  
            set_control_f=_setctrl_yellow_freq , get_control_f=_getctrl_yellow_freq,
            get_value_f=_getval, get_norm_f=_getnorm, 
            plot_name='yellow_plot')

#if True:
    _setctrl_nf = lambda x: qt.instruments['physical_adwin'].Set_FPar(51,x)
    _getctrl_nf = lambda: qt.instruments['physical_adwin'].Get_FPar(41)
    _getval  = lambda: qt.instruments['physical_adwin'].Get_Par(70)
    _getnorm = lambda: qt.instruments['physical_adwin'].Get_Par(72)
    nf_optimizer = qt.instruments.create('nf_optimizer', 'simple_optimizer', 
            set_control_f=_setctrl_nf, get_control_f=_getctrl_nf, 
            get_value_f=_getval, get_norm_f=_getnorm, 
            plot_name='nf_plot')
#if True:
    bell_optimizer  = qt.instruments.create('bell_optimizer' , 'bell_optimizer')


if False:
    qt.instruments['rejecter']._ctrl_half_x0 = 0.
    def _setctrl_half(x):
        #print qt.instruments['rejecter']._ctrl_half_x0, x
        qt.instruments['rejecter'].move('zpl_half', x-qt.instruments['rejecter']._ctrl_half_x0)
        qt.instruments['rejecter']._ctrl_half_x0 = x
    def _getctrl_half():
        return qt.instruments['rejecter']._ctrl_half_x0
    _getval_half  = lambda: -80.0*qt.instruments['physical_adwin'].Get_Par(53)
    _getnorm_half = lambda: qt.instruments['physical_adwin'].Get_Par(73)
    half_optimizer = qt.instruments.create('half_optimizer', 'simple_optimizer', 
            set_control_f=_setctrl_half, get_control_f=_getctrl_half, 
            get_value_f=_getval_half, get_norm_f=_getnorm_half, 
            plot_name='half_plot')


    qt.instruments['rejecter']._ctrl_quarter_x0 = 0.
    def _setctrl_quarter(x):
         qt.instruments['rejecter'].move('zpl_quarter', x-qt.instruments['rejecter']._ctrl_quarter_x0)
         qt.instruments['rejecter']._ctrl_quarter_x0 = x
    def _getctrl_quarter():
        return qt.instruments['rejecter']._ctrl_quarter_x0
    _getval_quarter  = lambda: -80.0*qt.instruments['physical_adwin'].Get_Par(53)
    _getnorm_quarter = lambda: qt.instruments['physical_adwin'].Get_Par(73)
    quarter_optimizer = qt.instruments.create('quarter_optimizer', 'simple_optimizer', 
            set_control_f=_setctrl_quarter, get_control_f=_getctrl_quarter, 
            get_value_f=_getval_quarter, get_norm_f=_getnorm_quarter, 
            plot_name='quarter_plot')

