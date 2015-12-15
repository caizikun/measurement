"""
Carbon gate optimization.
Initializes carbons via COMP and measures the Bloch vector length
Gate parameters are being swept.
Should result in less overhead from reprogramming and a faster calibration routine.

NK 2015

TODO:
Positive and negative RO into the AWG in one go.
This method would fit for carbons with less than 52 electron pulses per gate.
"""

import numpy as np
import qt
import msvcrt

execfile(qt.reload_current_setup)
import measurement.lib.measurement2.adwin_ssro.dynamicaldecoupling as DD
import measurement.scripts.mbi.mbi_funcs as funcs; reload(funcs)
import analysis.lib.QEC.Tomo_dict as TD; reload(TD)

reload(DD)

ins_counters = qt.instruments['counters']

SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def compsweep(tres,hwidth,Nres,Ndiff):
    tmin=tres-hwidth
    tmax=tres+hwidth
    tpairs=[]
    for phases in [293,315,337,0,23,45,67]:
            tpairs.append([round(((Nres/4)+hwidth/(4e-9)),-1)*2+Ndiff,round(tmin,10),round(((Nres/4)+hwidth/(4e-9)),-1)*2-Ndiff,round(tmax,10),phases])
            
    return transpose(tpairs).tolist()
            

def put_sweep_together(N1s,tau1s,N2s,tau2s,phases):
    ### put together into one sweep parameter
    px_list = ['pX_'+str(N1s[i])+'_'+str(tau1s[i])+'_'+str(N2s[i])+'_'+str(tau2s[i])+'_'+str(phases[i]) for i in range(len(N1s))]
    py_list = ['pY_'+str(N1s[i])+'_'+str(tau1s[i])+'_'+str(N2s[i])+'_'+str(tau2s[i])+'_'+str(phases[i]) for i in range(len(N1s))]
    mx_list = ['mX_'+str(N1s[i])+'_'+str(tau1s[i])+'_'+str(N2s[i])+'_'+str(tau2s[i])+'_'+str(phases[i]) for i in range(len(N1s))]
    my_list = ['mY_'+str(N1s[i])+'_'+str(tau1s[i])+'_'+str(N2s[i])+'_'+str(tau2s[i])+'_'+str(phases[i]) for i in range(len(N1s))]
    ## having fun with slices
    com_list = px_list + py_list + mx_list + my_list

    tomos = len(px_list)*[['X'],['Y'],['-X'],['-Y']]

    return com_list,4*N1s,4*tau1s,4*N2s,4*tau2s,4*phases,tomos

  


def SweepGates(name,**kw):

    debug = kw.pop('debug',False)
    carbon = kw.pop('carbon',False)
    el_RO = kw.pop('el_RO','positive')
    Ndiff = kw.pop('Ndiff',0)



    m = DD.Sweep_Carbon_Gate_COMP(name)
    funcs.prepare(m)

    m.params['C13_MBI_threshold_list'] = [1]
    m.params['el_after_init'] = '0'

  

    ''' set experimental parameters '''

    m.params['reps_per_ROsequence']=750

    ### Carbons to be used
    m.params['carbon_list']         =[carbon]

    ### Carbon Initialization settings
    m.params['carbon_init_list']    = [carbon]
    m.params['init_method_list']    = ['COMP']    
    m.params['init_state_list']     = ['up']
    m.params['Nr_C13_init']         = 1
    
    m.params['hwidth']=kw.pop('width',0)/2
   
    m.params['C1_tres']=[7.214e-6][0]
    m.params['C1_Nres']=[42][0]   


    m.params['C2_tres']=[13.602e-6][0]
    m.params['C2_Nres']=[34][0]

    

    m.params['C5_tres']=[11.296e-6][0]
    m.params['C5_Nres']=[44][0]


    ##################################
    ### RO bases,timing and number of pulses (sweep parameters) ###
    ##################################


    com_list,m.params['N1_list'],m.params['tau1_list'],m.params['N2_list'],m.params['tau2_list'],m.params['extra_phase_list'],m.params['Tomography Bases'] = put_sweep_together(compsweep(m.params['C'+str(carbon)+'_tres'],m.params['hwidth'],m.params['C'+str(carbon)+'_Nres'],Ndiff)[0],compsweep(m.params['C'+str(carbon)+'_tres'],m.params['hwidth'],m.params['C'+str(carbon)+'_Nres'],Ndiff)[1],compsweep(m.params['C'+str(carbon)+'_tres'],m.params['hwidth'],m.params['C'+str(carbon)+'_Nres'],Ndiff)[2],compsweep(m.params['C'+str(carbon)+'_tres'],m.params['hwidth'],m.params['C'+str(carbon)+'_Nres'],Ndiff)[3],compsweep(m.params['C'+str(carbon)+'_tres'],m.params['hwidth'],m.params['C'+str(carbon)+'_Nres'],Ndiff)[4])


    ###################
    ### Measurement settings###
    ###################
   
    print(m.params['tau1_list'])
    print('###############')
    print(m.params['Tomography Bases'])

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
  
    m.params['pts']                 = len(com_list)
    m.params['sweep_name']          = 'Tomo N and tau' 
    m.params['sweep_pts']           = com_list
   
     
    ### RO params
    m.params['electron_readout_orientation'] = el_RO
    
    funcs.finish(m, upload =True, debug=debug)

def show_stopper():
    print '-----------------------------------'            
    print 'press q to stop measurement cleanly'
    print '-----------------------------------'
    qt.msleep(1)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        return True
    else: return False

def optimize():
    GreenAOM.set_power(10e-6)
    counters.set_is_running(1)
    optimiz0r.optimize(dims = ['x','y','z','y','x'])


if __name__ == '__main__':
    carbons = [2,5]


    brekast = False
    for c in carbons:

        breakst = show_stopper()
        if breakst: break

        optimize()

        for w in [4e-9,8e-9,16e-9,20e-9]:
            
            for Ndiff in [0,2,4,6,-2,-4,-6]:
                
                for el_RO in ['positive','negative']:

                    breakst = show_stopper()
                    if breakst: break
                        
                    print(w)
                    SweepGates(el_RO+'_C'+str(c)+'_width_'+str(w*1000000000)+'nas_Ndiff_'+str(Ndiff),carbon=c, el_RO = el_RO, debug = False, width = w, Ndiff = Ndiff)
                  



