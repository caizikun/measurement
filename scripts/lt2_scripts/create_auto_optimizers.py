import qt

 
# if True:
#     _setctrl_gate = lambda x: qt.instruments['adwin'].set_dac_voltage(('gate',x))
#     _getctrl_gate=  lambda: qt.instruments['adwin'].get_dac_voltage('gate')
#     _getval  = lambda: qt.instruments['physical_adwin'].Get_Par(70)
#     _getnorm = lambda: qt.instruments['physical_adwin'].Get_Par(72)
#     gate_optimizer = qt.instruments.create('gate_optimizer', 'simple_optimizer', 
#             set_control_f=_setctrl_gate, get_control_f=_getctrl_gate, 
#             get_value_f=_getval, get_norm_f=_getnorm, 
#             plot_name='gate_plot')

if True:
    _setctrl_RO_freq = lambda x: qt.instruments['physical_adwin'].Set_FPar(55,x) 
    _getctrl_RO_freq=  lambda: qt.instruments['physical_adwin'].Get_FPar(45)
    _getval  = lambda: qt.instruments['physical_adwin'].Get_Par(70)
    _getnorm = lambda: qt.instruments['physical_adwin'].Get_Par(72) 
    RO_laser_optimizer = qt.instruments.create('RO_laser_optimizer', 'simple_optimizer',  
            set_control_f=_setctrl_RO_freq , get_control_f=_getctrl_RO_freq,
            get_value_f=_getval, get_norm_f=_getnorm, 
            plot_name='R0_laser_plot')

# if True:
#     _setctrl_nf = lambda x: qt.instruments['physical_adwin'].Set_FPar(51,x)
#     _getctrl_nf = lambda: qt.instruments['physical_adwin'].Get_FPar(41)
#     _getval  = lambda: qt.instruments['physical_adwin'].Get_Par(70)
#     _getnorm = lambda: qt.instruments['physical_adwin'].Get_Par(72)
#     nf_optimizer = qt.instruments.create('nf_optimizer', 'simple_optimizer', 
#             set_control_f=_setctrl_nf, get_control_f=_getctrl_nf, 
#             get_value_f=_getval, get_norm_f=_getnorm, 
#             plot_name='nf_plot')