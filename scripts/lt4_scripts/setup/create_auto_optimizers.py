if True:
    _getval_rej  = lambda: qt.instruments['physical_adwin'].Get_Par(53)
    _getnorm_rej = lambda: qt.instruments['physical_adwin'].Get_Par(73)
    _get_count_rej = lambda: qt.instruments['physical_adwin'].Get_Par(43)
    _get_msmt_running_rej = lambda: qt.instruments['lt4_measurement_helper'].get_is_running()
    rejecter = qt.instruments.create('rejecter', 'laser_reject0r_v3', rotator='rotator',
            rotation_config_name='waveplates_lt3',waveplates = ['zpl_half','zpl_quarter','pulse_half'],
            get_value_f=_getval_rej, get_norm_f=_getnorm_rej, 
            get_count_f = _get_count_rej, get_msmt_running_f = _get_msmt_running_rej)

if True:
    _setctrl_gate = lambda x: qt.instruments['adwin'].set_dac_voltage(('gate',x))
    _getctrl_gate=  lambda: qt.instruments['adwin'].get_dac_voltage('gate')
    _getval  = lambda: qt.instruments['physical_adwin'].Get_Par(70)
    _getnorm = lambda: qt.instruments['physical_adwin'].Get_Par(72)
    gate_optimizer = qt.instruments.create('gate_optimizer', 'simple_optimizer', 
            set_control_f=_setctrl_gate, get_control_f=_getctrl_gate, 
            get_value_f=_getval, get_norm_f=_getnorm, 
            plot_name='gate_plot')

# if True:
#     _setctrl_yellow_freq = lambda x: qt.instruments['physical_adwin'].Set_FPar(52,x)
#     _getctrl_yellow_freq=  lambda: qt.instruments['physical_adwin'].Get_FPar(42)
#     _getval  = lambda: qt.instruments['physical_adwin'].Get_Par(76)
#     _getnorm = lambda: qt.instruments['physical_adwin'].Get_Par(71)
#     yellowfrq_optimizer = qt.instruments.create('yellowfrq_optimizer', 'simple_optimizer',  
#             set_control_f=_setctrl_yellow_freq , get_control_f=_getctrl_yellow_freq,
#             get_value_f=_getval, get_norm_f=_getnorm, 
#             plot_name='yellow_plot')

if True:
    _setctrl_yellow_freq = lambda x: qt.instruments['physical_adwin'].Set_FPar(52,x)
    _getctrl_yellow_freq=  lambda: qt.instruments['physical_adwin'].Get_FPar(42)
    _getval  = lambda: qt.instruments['physical_adwin'].Get_Par(76)
    _getnorm = lambda: qt.instruments['physical_adwin'].Get_Par(71)
    yellowfrq_optimizer = qt.instruments.create('yellowfrq_optimizer', 'extended_optimizer',  
            set_control_f=_setctrl_yellow_freq , get_control_f=_getctrl_yellow_freq,
            get_value_f=_getval, get_norm_f=_getnorm, 
            plot_name='yellow_plot')

if True:
    _get_freq_yellow=lambda: qt.instruments['physical_adwin'].Get_FPar(42)
    _set_freq_yellow=lambda x: qt.instruments['physical_adwin'].Set_FPar(52,x)
    _get_counts_yellow=lambda: qt.instruments['physical_adwin'].Get_Par(76)
    _get_attemps_yellow=lambda: qt.instruments['physical_adwin'].Get_Par(71)

    _get_freq_gate=lambda: qt.instruments['adwin'].get_dac_voltage('gate')
    _set_freq_gate=lambda x: qt.instruments['adwin'].set_dac_voltage(('gate',x))
    _get_counts_gate=lambda: qt.instruments['physical_adwin'].Get_Par(70)
    _get_attemps_gate=lambda: qt.instruments['physical_adwin'].Get_Par(72)

    _get_freq_newfocus=lambda: qt.instruments['physical_adwin'].Get_FPar(41)
    _set_freq_newfocus=lambda x: qt.instruments['physical_adwin'].Set_FPar(51,x)

    auto_optimizer = qt.instruments.create('auto_optimizer', 'auto_optimizer',  
            get_freq_yellow = _get_freq_yellow, set_freq_yellow = _set_freq_yellow, get_counts_yellow = _get_counts_yellow, get_attemps_yellow = _get_attemps_yellow,
            get_freq_gate = _get_freq_gate, set_freq_gate = _set_freq_gate, get_counts_gate = _get_counts_gate, get_attemps_gate = _get_attemps_gate,
            get_freq_newfocus = _get_freq_newfocus, set_freq_newfocus = _set_freq_newfocus, plot_name='opt_plot')                

if True:
    _setctrl_nf = lambda x: qt.instruments['physical_adwin'].Set_FPar(51,x)
    _getctrl_nf = lambda: qt.instruments['physical_adwin'].Get_FPar(41)
    _getval  = lambda: qt.instruments['physical_adwin'].Get_Par(70)
    _getnorm = lambda: qt.instruments['physical_adwin'].Get_Par(72)
    nf_optimizer = qt.instruments.create('nf_optimizer', 'simple_optimizer', 
            set_control_f=_setctrl_nf, get_control_f=_getctrl_nf, 
            get_value_f=_getval, get_norm_f=_getnorm, 
            plot_name='nf_plot')
if True:
    purification_optimizer  = qt.instruments.create('purification_optimizer' , 'purification_optimizer', setup_name='lt4')
