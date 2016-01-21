import numpy as np
import qt 
import analysis.lib.QEC.Tomo_dict as TD; reload(TD)

### reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.DD_2 as DD; reload(DD)
import measurement.scripts.mbi.mbi_funcs as funcs; reload(funcs)

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def MBE(name, carbon_list            =   1,               
        
        carbon_init_list        =   [1],
        carbon_init_states      =   ['up'], 
        carbon_init_methods     =   ['swap'], 
        carbon_init_thresholds  =   [0],  

        tomo_bases = [['Z']],
        repetitions = 1000,

        el_RO               = 'positive',
        debug               = False):

    m = DD.Two_QB_Probabilistic_MBE(name)
    funcs.prepare(m)


    m.params['el_after_init']                = '0'


    m.params['C13_MBI_threshold_list'] = carbon_init_thresholds

    ''' set experimental parameters '''

    m.params['reps_per_ROsequence'] = repetitions

    ### Carbons to be used
    m.params['carbon_list']         = carbon_list

    ### Carbon Initialization settings 
    m.params['carbon_init_list']    = carbon_init_list
    m.params['init_method_list']    = carbon_init_methods    
    m.params['init_state_list']     = carbon_init_states    
    m.params['Nr_C13_init']         = len(carbon_init_list)

    ##################################
    ### RO bases (sweep parameter) ###
    ##################################

    m.params['Tomography Bases'] = tomo_bases
    # m.params['Tomography Bases'] = [['X'],['Y'],['Z']]
    # m.params['Tomography Bases'] = [['X'],['Y']]
    # m.params['Tomography Bases'] = [['X']]
        
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
    sweep_pts = ['','Z','ZZ','ZZZ']
    m.params['sweep_pts']           = [sweep_pts[len(carbon_list)]]
    
    ### RO params
    m.params['electron_readout_orientation'] = el_RO
    for BP in m.params['Tomography Bases']:
        m.params['sweep_pts'].append(BP[0])
    
    funcs.finish(m, upload =True, debug=debug)


def take_RO_value(carbons,tomo,repetitions = 400):
    carbon_string = ''
    for c in carbons:
        carbon_string += str(c)

    for RO in ['positive','negative']:
        MBE(SAMPLE + '_CarbonRO_'+carbon_string+'_'+ RO +'_'+str(len(carbons))+'_carbons', el_RO= RO, carbon_list = carbons, carbon_init_list = carbons
                                        ,carbon_init_methods     =   ['swap']*len(carbons), 
                                        carbon_init_thresholds  =  len(carbons)*[0],
                                        carbon_init_states      =    len(carbons)*['up'],
                                        debug = False, repetitions = repetitions,
                                        tomo_bases = tomo)

def show_stopper():
    print '-----------------------------------'            
    print 'press q to stop measurement cleanly'
    print '-----------------------------------'
    qt.msleep(1)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        return True
    else: return False

def optimize():
    GreenAOM.set_power(15e-6)
    counters.set_is_running(1)
    optimiz0r.optimize(dims = ['x','y','z','y','x'])
    
if __name__ == '__main__':

    carbon_list = [1,2,5]
    tomo = [[['Z']],[['Z','Z']],[['Z','Z','Z']]]
    reps = 3000


    breakstatement = False

    last_optimize = time.time()
    start_time = time.time()

    # optimize()
    ### commented out. used for debugging!
    # take_RO_value(carbon_list,[['Z','Z','Z']],repetitions = reps)

    # while abs(time.time()- start_time) < 6*60*60: ### 6 hours of measurement. HOOORAY!
    #     #some info
    #     print 'Time until I stop ', 6*60*60 - (time.time()- start_time)

    #     ### stop experiment? Press q.
    #     breakstatement = show_stopper()
    #     if breakstatement: break

    #     ## run experiment
    #     for carbon in carbon_list:

    #         take_RO_value([carbon],[['Z']],repetitions = reps)

    #         ### stop experiment? Press q.
    #         breakstatement = show_stopper()
    #         if breakstatement: break

    #         carbons_cross = copy.deepcopy(carbon_list)
    #         carbons_cross.remove(c)

    #         ### get two qubit inits and ROs
    #         take_RO_value(carbons_cross,[['Z','Z']],repetitions = reps)

    #         ### stop experiment? Press q.
    #         breakstatement = show_stopper()
    #         if breakstatement: break

    #     if breakstatement: break    

    #     ### get three qubit init/ro
    #     take_RO_value(carbon_list,[['Z','Z','Z']],repetitions = reps)

    #     ### stop experiment? Press q.
    #     breakstatement = show_stopper()
    #     if breakstatement: break


    #     ### optimize on NV every 30 minutes.

    #     print 'time until optimize ', 0.5*60*60 - (time.time()-last_optimize)
    #     if abs(time.time()-last_optimize) > 0.5*60*60:
    #         optimize()
    #         last_optimize = time.time()


    while abs(time.time()- start_time) < 6*60*60: ### 6 hours of measurement. HOOORAY!
        #some info
        print 'Time until I stop ', 6*60*60 - (time.time()- start_time)

        ### stop experiment? Press q.
        breakstatement = show_stopper()
        if breakstatement: break

        ## run experiment
        
        carbons_cross1 = [1,5]

        ### get two qubit inits and ROs
        take_RO_value(carbons_cross1,[['Z','Z']],repetitions = reps)

        ### stop experiment? Press q.
        breakstatement = show_stopper()
        if breakstatement: break

        carbons_cross2 = [2,5]

        ### get two qubit inits and ROs
        take_RO_value(carbons_cross2,[['Z','Z']],repetitions = reps)



        ### optimize on NV every 30 minutes.

        print 'time until optimize ', 0.5*60*60 - (time.time()-last_optimize)
        if abs(time.time()-last_optimize) > 0.5*60*60:
            optimize()
            last_optimize = time.time()
