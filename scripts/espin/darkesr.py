"""
Script for e-spin manipulations using the pulsar sequencer
"""
import numpy as np
import qt
import msvcrt

#reload all parameters and modules
execfile(qt.reload_current_setup)

import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
#reload(pulsar_msmt)
SAMPLE= qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']

def darkesr(name,width=16,upload=True):
    '''dark ESR on the 0 <-> -1 transition
    '''

    m = pulsar_msmt.DarkESR(name)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols']['Gretel_sil10']['Magnetometry'])
    stools.turn_off_all_lasers()
    
    m.params['ssmod_detuning'] = m.params['MW_modulation_frequency']
    m.params['mw_frq']       = m.params['ms-1_cntr_frq'] - m.params['ssmod_detuning'] #MW source frequency, detuned from the target
    m.params['repetitions']  = 300
    m.params['pts'] = 51#109
    
    m.params['Ex_SP_amplitude']=0
             # Power broadening of pulse in kHz
    if width==700:
        m.params['range']        = 12.e6
        m.params['mw_power']=7
        m.params['pulse_length'] = 0.5e-6
        m.params['ssbmod_amplitude'] = 0.032

    if width==350:
        m.params['range']        = 0.35e6
        m.params['mw_power']=7
        m.params['pulse_length'] = 5e-6
        m.params['ssbmod_amplitude'] = 0.016
    if width==40:
        m.params['range']        = 0.05e6
        m.params['mw_power']=-11
        m.params['pulse_length'] = 40e-6
        m.params['ssbmod_amplitude'] = 0.008
    if width==16:
        m.params['range']        = 0.05e6
        m.params['mw_power']=-17
        m.params['pulse_length'] = 80e-6
        m.params['ssbmod_amplitude'] = 0.008   


    m.params['ssbmod_frq_start'] = m.params['ssmod_detuning'] - m.params['range']
    m.params['ssbmod_frq_stop']  = m.params['ssmod_detuning'] + m.params['range']
    mIzero=np.linspace(m.params['ssbmod_frq_start'],m.params['ssbmod_frq_stop'], m.params['pts'])
    mIm1=mIzero-m.params['N_HF_frq']
    mIp1=mIzero+m.params['N_HF_frq']

    list_swp_pts=list(mIm1)+list(mIzero)+list(mIp1)
    list_swp_pts=list(mIzero)
    m.params['sweep_pts'] = (np.array(list_swp_pts) +  m.params['mw_frq'])*1e-9
    
    m.autoconfig()
    m.generate_sequence(upload=upload)
    if upload==False:
        AWG.set_runmode('SEQ')
        qt.msleep(10)
        AWG.start()
        qt.msleep(20)   
    m.run()
    m.save()
    m.finish()

def darkesrp1(name):
    '''dark ESR on the 0 <-> +1 transition
    '''

    m = pulsar_msmt.DarkESR(name+'_p1')
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols']['Gretel_sil10']['Magnetometry'])

    m.params['ssmod_detuning'] = m.params['MW_modulation_frequency']
    m.params['mw_frq']         = m.params['ms+1_cntr_frq'] - m.params['ssmod_detuning'] # MW source frequency, detuned from the target
    #m.params['mw_power'] = 20
    m.params['repetitions'] = 500
    m.params['range']        = 10e6
    m.params['pts'] = 101
    m.params['pulse_length'] = 2e-6
    m.params['ssbmod_amplitude'] = 0.005
    m.params['Ex_SP_amplitude']=0

    m.params['ssbmod_frq_start'] = m.params['ssmod_detuning'] - m.params['range']
    m.params['ssbmod_frq_stop']  = m.params['ssmod_detuning'] + m.params['range']

    m.autoconfig()
    m.generate_sequence(upload=True)
    m.run()
    m.save()
    m.finish()

def darkesr_FM(name,width,upload=True,f_msm1_cntr=None):
    '''dark ESR on the 0 <-> -1 transition with freq mod of vector source and fixed IQ mod freq
    '''

    m = pulsar_msmt.DarkESR_FM(name)
    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols']['Magnetometry'])
    m.params.from_dict(qt.exp_params['protocols']['Gretel_sil10']['Magnetometry'])
    stools.turn_off_all_lasers()
    
    
    m.params['ssmod_detuning'] = m.params['MW_modulation_frequency']
    m.params['repetitions']  = 750
    #m.params['wait_for_AWG_done']=1
    m.params['pts'] = 3*26

    if f_msm1_cntr:
        m.params['mw_frq']=f_msm1_cntr-m.params['ssmod_detuning']
    # Power broadening of pulse in kHz
    if width==6000:
        m.params['pts'] = 51
        m.params['range']        = 3e6
        m.params['mw_power']=7
        m.params['pulse_length'] = 2.5e-6
        m.params['ssbmod_amplitude'] = 0.032

    if width==350:
        m.params['pts'] = 26
        m.params['range']        = 0.35e6
        m.params['mw_power']=7
        m.params['pulse_length'] = 5e-6
        m.params['ssbmod_amplitude'] = 0.016
    if width==40:
        m.params['range']        = 0.05e6
        m.params['mw_power']=-11
        m.params['pulse_length'] = 40e-6
        m.params['ssbmod_amplitude'] = 0.016
    if width==4:
        m.params['pts'] = 3*26
        m.params['repetitions']  = 500
        m.params['range']        = 5*0.015e6
        m.params['mw_power']=-17
        m.params['pulse_length'] = 160e-6
        m.params['ssbmod_amplitude'] = 0.008    

    m.params['Ex_SP_amplitude']=0

    m.params['ssbmod_frq_start'] = m.params['ssmod_detuning'] - m.params['range']
    m.params['ssbmod_frq_stop']  = m.params['ssmod_detuning'] + m.params['range']
    mIzero=np.linspace(m.params['ssbmod_frq_start'],m.params['ssbmod_frq_stop'], m.params['pts'])
    mIm1=mIzero-m.params['N_HF_frq']
    mIp1=mIzero+m.params['N_HF_frq']

    list_swp_pts=list(mIm1)+list(mIzero)+list(mIp1)
    list_swp_pts=list(mIzero)

    
    m.params['FM_amplitude'] = (np.array(list_swp_pts) - m.params['ssmod_detuning'])/m.params['FM_sensitivity']
    m.params['sweep_pts'] = (np.array(list_swp_pts) +  m.params['mw_frq'])*1e-9
    
    m.autoconfig()
    m.generate_sequence(upload=upload)
    m.run()
    m.save()
    m.finish()

def measure_Bfield_stability():
    stop_scan=False
    optimized_pos_after=[]
    for i in np.arange(500):
        if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): stop_scan=True
        name_file = 'B_stab_nr_'+str(i)+'_'
        darkesr(name=name_file, width=16,upload=True)
        counters.set_is_running(True)
        qt.msleep(0.5)
        GreenAOM.set_power(5e-6)
        qt.msleep(0.5)
        cnts=counters.get_cntr1_countrate()
        if cnts<195000:
            optimiz0r.optimize(dims=['x','y','z','y','x'],cnt=1,int_time=100,cycles=1)
            optimized_pos_after.append(i)
        #else:
        #    optimized_pos_after.append(-42)    
        GreenAOM.turn_off()    
        if stop_scan: break
    return optimized_pos_after    
if __name__ == '__main__':
    #darkesr_FM(SAMPLE_CFG,width=4,upload=True)
    darkesr_FM(SAMPLE_CFG,width=4,upload=True,f_msm1_cntr=None)
    #darkesr(SAMPLE_CFG,width=700)
    #darkesr_FM(SAMPLE_CFG)
    #raw_input ('Do the fitting...')
    #darkesrp1(SAMPLE_CFG)
    #opt_pos_array=measure_Bfield_stability()