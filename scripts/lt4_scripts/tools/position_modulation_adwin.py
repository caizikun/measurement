import qt
def start_optimize_position_dacs():
    adwin=qt.instruments['adwin']
    cur_pos=[adwin.get_dac_voltage('atto_x'), adwin.get_dac_voltage('atto_y'), adwin.get_dac_voltage('atto_z')]
    adwin.start_mod_position(atto_positions=cur_pos, counter_value=0,pos_mod_activate=0)

def stop_optimize_position_dacs():
    adwin=qt.instruments['adwin']
    adwin.stop_mod_position()
    new_pos = adwin.get_mod_position_var('atto_positions',length=3)
    adwin.set_dac_voltage(('atto_x',new_pos[0]))
    adwin.set_dac_voltage(('atto_y',new_pos[1]))
    adwin.set_dac_voltage(('atto_z',new_pos[2]))
    #qt.instruments['master_of_space'].init_positions_from_adwin_dacs()