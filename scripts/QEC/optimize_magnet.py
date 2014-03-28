"""
Script for optimizing the magnet position in Z-direction.
Important: choose the right domain for the range of positions in get_magnet_position in magnet tools!

"""
import numpy as np
import qt
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt

# import the dESR fit
from analysis.lib.fitting import dark_esr_auto_analysis

# import magnet tools and master of magnet
from measurement.lib.tools import magnet_tools as mt
from measurement.instruments import Master_of_magnet

execfile(qt.reload_current_setup)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

nm_per_step = qt.exp_params['magnet']['nm_per_step']

# Define the wanted magnet position
B_field_ideal = mt.convert_f_to_Bz(freq=current_f_msp1)
position_ideal = mt.get_magnet_position(msp1_freq=current_f_msp1,ms = 'plus',solve_by = 'list')
B_error_range = 5e-3 # allowed error in B_field (it was 7mG in RT experiment, can be changed)

def darkesr(name):

    m = pulsar_msmt.DarkESR(name)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])


    #m.params['mw_frq'] = m.params['ms+1_cntr_frq']-43e6 #MW source frequency
    m.params['mw_frq'] = 2*m.params['zero_field_splitting'] - m.params['ms-1_cntr_frq'] -43e6

    m.params['mw_power'] = 20
    m.params['repetitions'] = 3000

    m.params['ssbmod_frq_start'] = 43e6 - 6.5e6
    m.params['ssbmod_frq_stop'] = 43e6 + 6.5e6
    m.params['pts'] = 41
    m.params['pulse_length'] = 2e-6
    m.params['ssbmod_amplitude'] = 0.05

    m.autoconfig()
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()

# as long as you are in similar frequency range the freq does not need
# to be changed: do not need to reload the measurement to the AWG
def darkesr_auto(name):

    m = pulsar_msmt.DarkESR(name)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])

    #m.params['mw_frq'] = m.params['ms+1_cntr_frq']-43e6 #MW source frequency
    m.params['mw_frq'] = 2*m.params['zero_field_splitting'] - m.params['ms-1_cntr_frq'] -43e6

    m.params['mw_power'] = 20
    m.params['repetitions'] = 3000

    m.params['ssbmod_frq_start'] = 43e6 - 6.5e6
    m.params['ssbmod_frq_stop'] = 43e6 + 6.5e6
    m.params['pts'] = 41
    m.params['pulse_length'] = 2e-6
    m.params['ssbmod_amplitude'] = 0.05

    m.autoconfig()
    m.generate_sequence(upload=False)
    m.run()
    m.save()
    m.finish()

if __name__ == '__main__':

    #create a file to save data to --> what is a good way to save this, because other
    # files will follow and we want to update all the time?
    d = qt.Data(name=name)
    d.add_coordinate('iteration')
    d.add_value('frequency [GHz]')
    d.add_value('frequency error [GHz]')
    d.add_value('Bfield [G]')
    d.add_value('number of steps')
    d.create_file()
    filename=d.get_filepath()[:-4]

    #create the lists to save the data to
    d_steps = []
    f0 = []
    u_f0 = []
    B_field_measured = []

    # start: define B-field and position by first ESR measurement
    total_d_position_nm = 0
    iterations = 0
    d_steps[iterations] = 0
    darkesr(SAMPLE_CFG)
    f0[iterations],u_f0[iterations] = dark_esr_auto_analysis.analyze_dark_esr(m.params['ms+1_cntr_frq']*1e-9,
        m.params['N_HF_frq']*1e-9 )

    B_field_measured[iterations] = convert_f_to_Bz(freq=f0*1e9)

    # start loop to optimize the field if field is out of set range
    while B_field_measured > B_field_ideal+B_error_range or B_field_measured < B_field_ideal-B_error_range

        # determine magnet position and error wrt ideal position
        position = mt.get_magnet_position(msp1_freq=f0*1e9,ms = 'plus',solve_by = 'list')
        d_position_nm = (position - position_ideal)*1e6

        # Step the magnet
        d_steps[iterations] = d_position_nm/nm_per_step
        print 'move magnet in Z with '+ str(d_steps) + ' steps'
        Master_of_magnet.step('Z_axis',d_steps[iterations]) # position further than ideal position -> go closer
        
        #do dESR without reloading to the AWG
        Darkesr_auto(SAMPLE_CFG)

        #Determine frequency and B-field again
        f0[iterations],u_f0[iterations] = dark_esr_auto_analysis.analyze_dark_esr(m.params['ms+1_cntr_frq']*1e-9,
            m.params['N_HF_frq']*1e-9 )

        B_field_measured[iterations] = convert_f_to_Bz(freq=f0*1e9)

        # keep track of the movement
        total_d_position_nm = total_d_position_nm + d_position_nm

        iterations = iterations + 1

    d.add_data_point(iterations, f0,u_f0,B_field_measured,d_steps)
    d.close_file()

    print 'B_field optimized, stepped: '+ str(total_d_position_nm) + ' in '+str(iterations) +' iterations in Z direction'


## Because of reloading I'm more in favour of keeping the same freq domain for the msmt