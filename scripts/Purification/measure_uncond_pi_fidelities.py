
import numpy as np
import qt 
import analysis.lib.QEC.Tomo_dict as TD; reload(TD)
import msvcrt

### reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.DD_2 as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs; reload(funcs)

# import measurement.scripts.lt2_scripts.tools.stools

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

class Uncond_Pi_Sweep(DD.MBI_C13):
    '''
    #Sequence
                              
    |N-MBI| -|Cinits|-|C Gate|  --|Tomo|
                              

    '''
    mprefix = 'Uncond_Pi_Sweep'
    adwin_process = 'MBI_multiple_C13'

    def generate_sequence(self, upload=True, debug=False):
        pts = self.params['pts']

        ### initialize empty sequence and elements
        combined_list_of_elements =[]
        combined_seq = pulsar.Sequence('Uncond Pi Sweep')

        for pt in range(pts): ### Sweep over RO basis


            gate_seq = []

            ### Nitrogen MBI
            mbi = DD.Gate('MBI_'+str(pt),'MBI')
            mbi_seq = [mbi]; gate_seq.extend(mbi_seq)

            ### Carbon initialization
            init_wait_for_trigger = True
            
            for kk in range(self.params['Nr_C13_init']):

                if self.params['el_after_init']                == '1':
                    self.params['do_wait_after_pi']            = True
                else: 
                    self.params['do_wait_after_pi']            = False

                
                carbon_init_seq = self.initialize_carbon_sequence(go_to_element = mbi,
                    prefix = 'C_' + self.params['init_method_list'][kk] + str(kk+1) + '_C',
                    wait_for_trigger      = init_wait_for_trigger, pt =pt,
                    initialization_method = self.params['init_method_list'][kk],
                    C_init_state          = self.params['init_state_list'][kk],
                    addressed_carbon      = self.params['carbon_init_list'][kk],
                    el_after_init         = self.params['el_after_init'],
                    do_wait_after_pi      = self.params['do_wait_after_pi'])
                gate_seq.extend(carbon_init_seq)
                init_wait_for_trigger = False

            C_Echo = DD.Gate('C_echo'+str(pt), 'Carbon_Gate',
                    Carbon_ind =self.params['carbon_list'][0],
                    phase = self.params['C13_X_phase']) #Wellicht reset?
            
            C_Echo_2 = DD.Gate('C_echo2_'+str(pt), 'Carbon_Gate',
                    Carbon_ind =self.params['carbon_list'][0],
                    phase = self.params['C13_X_phase'])
            # self.params['Carbon_pi_duration'] += 2 * C_Echo_2.N * C_Echo_2.tau

            gate_seq.extend([C_Echo,C_Echo_2])

            carbon_tomo_seq = self.readout_carbon_sequence(
                    prefix              = 'Tomo',
                    pt                  = pt,
                    go_to_element       = None,
                    event_jump_element  = None,
                    RO_trigger_duration = 10e-6,
                    carbon_list         = self.params['carbon_list'],
                    RO_basis_list       = self.params['Tomography Bases'][pt],
                    readout_orientation = self.params['electron_readout_orientation'])
            gate_seq.extend(carbon_tomo_seq)

            gate_seq = self.generate_AWG_elements(gate_seq,pt)

            ### Convert elements to AWG sequence and add to combined list`
            list_of_elements, seq = self.combine_to_AWG_sequence(gate_seq, explicit=True)
            combined_list_of_elements.extend(list_of_elements)

            for seq_el in seq.elements:
                combined_seq.append_element(seq_el)


            if debug:
                for g in gate_seq:
                    print g.name
                    self.print_carbon_phases(g,self.params['carbon_list'])
        if upload:
            print ' uploading sequence'
            qt.pulsar.program_awg(combined_seq, *combined_list_of_elements, debug=debug)

        else:
            print 'upload = false, no sequence uploaded to AWG'

def show_stopper():
    print '-----------------------------------'            
    print 'press q to stop measurement cleanly'
    print '-----------------------------------'
    qt.msleep(1)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        return True
    else: return False

def uncond_Pi_Sweep(name, carbon=   1,               
        carbon_init_list        =   [1],
        desired_carbon_init_states      =   ['X'], 
        el_RO               = 'positive',
        debug               = False):

    m = Uncond_Pi_Sweep(name)
    funcs.prepare(m)

    carbon_init_methods = []
    carbon_init_thresholds = []
    carbon_init_states = []

    print desired_carbon_init_states

    for init_state in desired_carbon_init_states:
        
        if init_state == 'X':
            carbon_init_methods.append('MBI')
            carbon_init_thresholds.append(1)
            carbon_init_states.append('up')
        elif init_state == 'mX':
            carbon_init_methods.append('MBI')
            carbon_init_thresholds.append(1)
            carbon_init_states.append('down')
        elif init_state == 'Y':
            carbon_init_methods.append('MBI_y')
            carbon_init_thresholds.append(1)
            carbon_init_states.append('up')
        elif init_state == 'mY':
            carbon_init_methods.append('MBI_y')
            carbon_init_thresholds.append(1)
            carbon_init_states.append('down')
        elif init_state == 'Z':
            carbon_init_methods.append('MBI_w_gate')
            carbon_init_thresholds.append(1)
            carbon_init_states.append('up')
        elif init_state == 'mZ':
            carbon_init_methods.append('MBI_w_gate')
            carbon_init_thresholds.append(1)
            carbon_init_states.append('down')
        else:
            print "Invalid state"
            return



    m.params['el_after_init']                = '0'


    m.params['C13_MBI_threshold_list'] = carbon_init_thresholds

    ''' set experimental parameters '''

    m.params['reps_per_ROsequence'] = 1000

    ### Carbons to be used
    m.params['carbon_list']         = [carbon]

    ### Carbon Initialization settings 
    m.params['carbon_init_list']    = carbon_init_list
    m.params['init_method_list']    = carbon_init_methods    
    m.params['init_state_list']     = carbon_init_states    
    m.params['Nr_C13_init']         = len(carbon_init_list)


    ##################################
    ### RO bases (sweep parameter) ###
    ##################################

    m.params['Tomography Bases'] = TD.get_tomo_bases(nr_of_qubits = 1)
    # m.params['Tomography Bases'] = [['X'],['Y'],['Z']]
    # m.params['Tomography Bases'] = [['X'],['Y']]
    # m.params['Tomography Bases'] = [['Z']]
        
    ####################
    ### MBE settings ###
    ####################

    m.params['Nr_MBE']              = 0 
    m.params['MBE_bases']           = []
    m.params['MBE_threshold']       = 1
    
    ###################################
    ### Parity measurement settings ###
    ###################################

    m.params['Nr_parity_msmts']     = 0
    m.params['Parity_threshold']    = 1
    
    ### Derive other parameters
    m.params['pts']                 = len(m.params['Tomography Bases'])
    m.params['sweep_name']          = 'Tomography Bases' 
    m.params['sweep_pts']           = []
    
    ### RO params
    m.params['electron_readout_orientation'] = el_RO
    for BP in m.params['Tomography Bases']:
        m.params['sweep_pts'].append(BP[0])
    
    funcs.finish(m, upload =True, debug=debug)
    
def optimize():
    GreenAOM.set_power(10e-6)
    optimiz0r.optimize(dims=['x','y','z'], int_time=100)
    GreenAOM.set_power(0e-6)

if __name__ == '__main__':
    carbons = [1]
    debug = False
    breakst = False

    #carbon_init_states = ['X','mX','Y','mY','Z','mZ']
    carbon_init_states = ['Z','mZ']

    for c in carbons:

        optimize()

        for init_state in carbon_init_states:

            breakst = show_stopper()
            if breakst:
                break

            
            uncond_Pi_Sweep(SAMPLE + '_positive_'+str(c)+'_'+ init_state, el_RO= 'positive', carbon = c, carbon_init_list = [c]
                                                ,debug = debug, desired_carbon_init_states = [init_state])


            breakst = show_stopper()
            if breakst:
                break

            uncond_Pi_Sweep(SAMPLE + '_negative_'+str(c)+'_'+ init_state, el_RO= 'negative', carbon = c, carbon_init_list = [c]
                                                ,debug = debug,desired_carbon_init_states = [init_state])
            
       


