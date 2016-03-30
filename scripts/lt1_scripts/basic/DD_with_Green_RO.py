"""
Script doing DD with green using the qutau.
"""

import numpy as np
import qt
#reload all parameters and modules
execfile(qt.reload_current_setup)
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
from measurement.lib.measurement2.adwin_ssro import ssro
import msvcrt
from measurement.lib.measurement2.adwin_ssro import pulsar_qutau
from measurement.lib.pulsar import pulse, pulselib, element, pulsar
from measurement.scripts.lt1_scripts.basic import espin_with_Green_RO as gro
from measurement.lib.measurement2.adwin_ssro import dynamicaldecoupling as dd
#import measurement.scripts.mbi.mbi_funcs as funcs
reload(dd)
SAMPLE_CFG = qt.exp_params['protocols']['current']
SAMPLE_NAME =  qt.exp_params['samples']['current']

qutau=qt.instruments['QuTau']
GreenAOM=qt.instruments['GreenAOM']
class DD_sequences_Green_RO(dd.SimpleDecoupling):
    '''
    This is a class that only overwrites the combine_to_AWG_sequence function in SimpleDecoupling
    to adapt it for Green_RO. The only things that should be different are the triggers etc and
    it does not need an MBI element.
    TODO:
    This is a work around such that all dd code (previously written on lt2) is also consistent with not doing MBI
    however, those classes mostly add pulses to AWG, so should be made independently of pulsar_msmnt.MBI
    '''
    def _RO_element(self,name ='RO'):
        # define the necessary pulses
        sq_AOMpulse = pulse.SquarePulse(channel='AOM_Green',name='Green_square')
        sq_AOMpulse.amplitude = 1 #sets the marker high
        sq_AOMpulse.length = self.params['GreenAOM_pulse_length']
        sync  =  pulse.SquarePulse(channel = 'sync', length = self.params['pq_sync_length'], amplitude = 1.0)

        adwin_trigger_pulse = pulse.SquarePulse(channel = 'adwin_sync',   length = 1590e-9,   amplitude = 2)
        wait_before_MW = 500e-9
        T=pulse.SquarePulse(channel='MW_Imod',name='Wait',length=wait_before_MW)
        # the actual element
        ro_element = element.Element(name, pulsar=qt.pulsar)
        ro_element.add(adwin_trigger_pulse,name='adwin_trigger')
        ro_element.add(T,name='wait2',refpulse='adwin_trigger',refpoint='end')
        ro_element.add(sq_AOMpulse,name='GreenLight',refpulse='wait2',refpoint='end')
        ro_element.add(sync,name='Sync',refpulse='wait2',refpoint='end')
        ro_element.add(pulse.cp(T,length=self.params['time_between_syncs']),name='wait3',refpulse='Sync',refpoint='end')
        ro_element.add(sync,name='Sync2',refpulse='wait3',refpoint='end')
        
        ro_element.add(pulse.cp(T, length=2.5e-6),name='wait_for_singlet',refpulse='GreenLight',refpoint='end')

        return ro_element
    def _First_element(self,name ='First_element'):
        ## Make it the same as RO, but without syncs
        # define the necessary pulses
        sq_AOMpulse = pulse.SquarePulse(channel='AOM_Green',name='Green_square')
        sq_AOMpulse.amplitude = 1 #sets the marker high
        sq_AOMpulse.length = self.params['GreenAOM_pulse_length']
        sync  =  pulse.SquarePulse(channel = 'sync', length = self.params['pq_sync_length'], amplitude = 1.0)

        adwin_trigger_pulse = pulse.SquarePulse(channel = 'adwin_sync',   length = 1590e-9,   amplitude = 2)
        wait_before_MW = 500e-9
        T=pulse.SquarePulse(channel='MW_Imod',name='Wait',length=wait_before_MW)

        # the actual element
        first_element = element.Element(name, pulsar=qt.pulsar)
        first_element.add(pulse.cp(adwin_trigger_pulse,amplitude=0),name='adwin_trigger')
        first_element.add(T,name='wait2',refpulse='adwin_trigger',refpoint='end')
        first_element.add(sq_AOMpulse,name='GreenLight',refpulse='wait2',refpoint='end')
        first_element.add(pulse.cp(sync,amplitude=0),name='Sync',refpulse='wait2',refpoint='end')
        first_element.add(pulse.cp(T,length=self.params['time_between_syncs']),name='wait3',refpulse='Sync',refpoint='end')
        first_element.add(pulse.cp(sync,amplitude=0),name='Sync2',refpulse='wait3',refpoint='end')
        first_element.add(pulse.cp(T, length=2.5e-6),name='wait_for_singlet',refpulse='GreenLight',refpoint='end')
        return first_element


    ### function for making sequences out of elements
    def combine_to_AWG_sequence(self,gate_seq,explicit = False):
        '''
        Used as last step before uploading, combines all the gates to a sequence the AWG can understand.
        Requires the gates to already have the elements and repetitions and stuff added as arguments.
        NOTE: 'event_jump', 'goto' and 'wait' options only available for certain types of elements
        explicit is a statement that is introduced to maintain backwards compatibility,
        explicit is also required when using jump and goto statements.
        '''
        list_of_elements=[]
        seq = pulsar.Sequence('Decoupling Sequence')

        explicit=True
        
        if explicit == False:  # explicit means that MBI and trigger elements must be given explicitly to the combine to AWG sequence function
            mbi_elt = self._MBI_element()
            list_of_elements.append(mbi_elt)
            seq.append(name=str(mbi_elt.name+gate_seq[0].elements[0].name),
                    wfname=mbi_elt.name, trigger_wait=True,repetitions = 1,
                    goto_target =str(mbi_elt.name+gate_seq[0].elements[0].name),
                    jump_target = gate_seq[0].elements[0].name)

        for i, gate in enumerate(gate_seq):
            # Determine where jump events etc
            if hasattr(gate, 'go_to'):
                if gate.go_to == None:
                    pass
                elif gate.go_to == 'next':
                    gate.go_to = gate_seq[i+1].elements[0].name
                elif gate.go_to == 'self':
                    gate.go_to = gate.elements[0].name
                elif gate.go_to =='start':
                    gate.go_to = gate_seq[0].elements[0].name
                else:
                    ind = self.find_gate_index(gate.go_to,gate_seq)
                    gate.go_to = gate_seq[ind].elements[0].name

            if not(list_of_elements):
                first_element = self._First_element()
                list_of_elements.append(first_element)
                seq.append(name='first', wfname=first_element.name,
                                trigger_wait=True,repetitions = 1)
            

            # Debug print statement:
            # print 'Gate %s, \n  %s \n goto %s, \n jump %s' %(gate.name,gate.elements[0].name,gate.go_to,gate.event_jump)

            single_elements_list = ['NO_Pulses','single_block','single_element']
            #####################
            ### 'special' elements ###
            #####################
            if gate.scheme == 'mbi':
                e = gate.elements[0]
                list_of_elements.append(e)
                seq.append(name =e.name, wfname =e.name,
                        trigger_wait = True,
                        repetitions = 1,
                        goto_target =gate.go_to ,
                        jump_target =gate.event_jump)
            elif gate.scheme =='trigger' :
                e = gate.elements[0]
                list_of_elements.append(e)

                seq.append(name = e.name, wfname =e.name,
                        trigger_wait = gate.wait_for_trigger,
                        repetitions = gate.reps,
                        goto_target = gate.go_to,
                        jump_target= gate.event_jump )

            ####################
            ###  single elements  ###
            ####################
            elif gate.scheme in single_elements_list :
                e = gate.elements[0]
                list_of_elements.append(e)
                if gate.reps ==0:
                    gate.reps = 1
                if (i == 0 and explicit == False ):  #need to check for modularity
                    seq.append(name=e.name, wfname=e.name,
                        trigger_wait=True,repetitions = gate.reps)

                else:
                    seq.append(name=e.name,wfname =e.name,
                            trigger_wait=gate.wait_for_trigger,
                            repetitions=gate.reps,
                            goto_target = gate.go_to,
                            jump_target= gate.event_jump )

            ####################
            ###  RF elements ###
            ####################
            elif gate.scheme == 'RF_pulse':
                list_of_elements.extend(gate.elements)
                # starting envelope element
                seq.append(name=gate.elements[0].name, wfname=gate.elements[0].name,
                    trigger_wait=False,repetitions = 1)
                # repeating period element
                seq.append(name=gate.elements[1].name, wfname=gate.elements[1].name,
                    trigger_wait=False,repetitions = gate.reps)
                 # ending envelope element
                seq.append(name=gate.elements[2].name, wfname=gate.elements[2].name,
                    trigger_wait=False,repetitions = 1)
            ######################
            ### XY4 elements
            ######################
            elif gate.scheme == 'XY4':
                #TODO_THT: (Possibly) fix that last element is XX instead of XY if only 2 final elements
                list_of_elements.extend(gate.elements)
                # initial element
                seq.append(name=gate.elements[0].name, wfname=gate.elements[0].name,
                    trigger_wait=gate.wait_for_trigger,repetitions = 1)
                # repeating element
                seq.append(name=gate.elements[1].name, wfname=gate.elements[1].name,
                    trigger_wait=False,repetitions = gate.reps/2-1)
                # final element
                seq.append(name=gate.elements[2].name, wfname=gate.elements[2].name,
                    trigger_wait=False,
                    goto_target = gate.go_to,
                    jump_target = gate.event_jump,
                    repetitions = 1)
            ######################
            ### XY8 elements
            #-a-b-(c^2-b^2)^(N/8-1)-c-d-
            ######################
            elif gate.scheme =='XY8':
                #TODO_THT: fix that last element is XX instead of XY if only 2 final elements
                list_of_elements.extend(gate.elements)
                a = gate.elements[0]
                b= gate.elements[1]
                c = gate.elements[2]
                d = gate.elements[3]
                seq.append(name=a.name, wfname=a.name,
                    trigger_wait=gate.wait_for_trigger,
                    repetitions = 1)
                seq.append(name=b.name, wfname=b.name,
                    trigger_wait=False,repetitions = 1)
                for i in range(gate.reps/8-1):
                    seq.append(name=(c.name+str(i)), wfname=c.name,
                        trigger_wait=False,repetitions = 2)
                    seq.append(name=(b.name+str(i)), wfname=b.name,
                        trigger_wait=False,repetitions = 2)
                seq.append(name=c.name, wfname=c.name,
                    trigger_wait=False,repetitions = 1)
                seq.append(name=d.name, wfname=d.name,
                    trigger_wait=False,
                    goto_target = gate.go_to,
                    jump_target = gate.event_jump,
                    repetitions = 1)
            ######################
            ### XYn, tau > 2 mus
            # t^n a t^n b t^n
            ######################
            elif gate.scheme =='repeating_T_elt':
                list_of_elements.extend(gate.elements)
                wait_reps = gate.n_wait_reps
                st  = gate.elements[0]
                x   = gate.elements[1]
                y   = gate.elements[2]
                fin = gate.elements[3]
                t   = gate.elements[4]

                #Start elements
                pulse_ct = 0
                red_wait_reps = wait_reps//2
                if red_wait_reps != 0: #Note st.name is name of the repeating t element here because of references
                    seq.append(name=st.name, wfname=t.name,
                        trigger_wait=gate.wait_for_trigger,
                        repetitions = red_wait_reps)#floor divisor
                seq.append(name=st.name+'_', wfname=st.name,
                    trigger_wait=False,repetitions = 1)
                pulse_ct+=1
                #Repeating centre elements
                x_list = [0,2,5,7]
                while pulse_ct < (gate.reps-1):
                    seq.append(name=t.name+'_'+str(pulse_ct), wfname=t.name,
                        trigger_wait=False,repetitions = wait_reps)
                    if pulse_ct%8 in x_list:
                        seq.append(name=x.name+str(pulse_ct), wfname=x.name,
                            trigger_wait=False,repetitions = 1)
                    else:
                        seq.append(name=y.name+str(pulse_ct), wfname=y.name,
                            trigger_wait=False,repetitions = 1)
                    pulse_ct +=1
                #Final elements
                if gate.reps== 1:
                    if red_wait_reps!=0 and red_wait_reps!=1 :
                        seq.append(name=t.name+str(pulse_ct+1), wfname=t.name,
                           trigger_wait=False,
                           goto_target = gate.go_to,
                           jump_target = gate.event_jump,
                           repetitions = red_wait_reps-1) #floor divisor
                else:
                    seq.append(name=t.name+'_'+str(pulse_ct), wfname=t.name,
                        trigger_wait=False,repetitions = wait_reps)
                    if red_wait_reps == 0:
                        seq.append(name=fin.name, wfname=fin.name,
                            trigger_wait=False,
                            goto_target = gate.go_to,
                            jump_target = gate.event_jump,
                            repetitions = 1)
                    else:
                        seq.append(name=fin.name, wfname=fin.name,
                            trigger_wait=False,
                            goto_target = gate.go_to,
                            jump_target = gate.event_jump,
                            repetitions = 1)
                        seq.append(name=t.name+str(pulse_ct+1), wfname=t.name,
                           trigger_wait=False,repetitions = red_wait_reps) #floor divisor
            else:
                print 'Gate %s not added, scheme = %s' %(gate.name,gate.scheme)
        

        ro_elt = self._RO_element()
        list_of_elements.append(ro_elt)
        seq.append(name=str(ro_elt.name+e.name), wfname=ro_elt.name,
                            trigger_wait=False,repetitions = 1,jump_target='first')
        print type(seq)
        return list_of_elements, seq

class Green_RO_DD(gro.Green_RO):

    def generate_sequence(self, upload=True):
        gen_seq=DD_sequences_Green_RO(n)
        gen_seq.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
        gen_seq.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+PQ'])
        gen_seq.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+MBI'])
        #gen_seq.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO+MBI'])
        gen_seq.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

        N=self.params['N'] 
        step_size = self.params['dtau']
        start_point=0
        tot = 1
        final_pulse = '-x'
        mbi = False
        optimize=False
        for kk in range(tot):
            
            ### Set experimental parameters ###
            gen_seq.params['reps_per_ROsequence'] = 500 
            gen_seq.params['Initial_Pulse'] ='-x'
            gen_seq.params['Final_Pulse'] = final_pulse
            gen_seq.params['Decoupling_sequence_scheme'] = 'repeating_T_elt'

            Number_of_pulses = N 
            pts = self.params['pts']
            start    = self.params['start']  + (kk+start_point)     * (pts-1)*step_size 
            end      = self.params['start']   + (kk+1+start_point) * (pts-1)*step_size
            tau_list = np.linspace(start, end, pts)

            ### Start measurement ###

                ### Measurement name
            msmt_name = 'measurement' + str(kk)
            
                ### Optimize position
            
            if optimize:
                qt.msleep(2)
                if mod(kk,2)==0:
                    AWG.clear_visa()
                    stools.turn_off_all_lt2_lasers()
                    qt.msleep(1)
                    GreenAOM.set_power(10e-6)
                    optimiz0r.optimize(dims=['x','y','z','x','y'])

                ### Define and print parameters
            #funcs.prepare(gen_seq)
            gen_seq.params['pts']              = len(tau_list)
            gen_seq.params['Number_of_pulses'] = Number_of_pulses*np.ones(gen_seq.params['pts']).astype(int)
            gen_seq.params['tau_list']         = tau_list
            gen_seq.params['sweep_pts']        = tau_list*1e6
            gen_seq.params['sweep_name']       = 'tau (us)'
            
            if mbi == False:
                gen_seq.params['MBI_threshold'] = 0
                gen_seq.params['Ex_SP_amplitude'] = 0
                gen_seq.params['Ex_MBI_amplitude'] = 0
                gen_seq.params['SP_E_duration'] = 2000
                
                gen_seq.params['repump_after_MBI_A_amplitude'] = [15e-9]
                gen_seq.params['repump_after_MBI_duration'] = [50]    

            print 'run = ' + str(kk) + ' of ' + str(tot)
            print gen_seq.params['sweep_pts']
            print tau_list
        print 'gen_seq'
        seq,el=gen_seq.generate_sequence(upload=False, debug=False,return_combined_seq=True)
        seq.append(name='Final_element', wfname='First_element',jump_target='first',goto_target=el[1].name)
        qt.pulsar.program_awg(seq, *el, debug=False,loop=False)

def DD(name,start):

    m = Green_RO_DD('GreenRO_DD'+name)
    
    m.AWG_RO_AOM = qt.instruments['PulseAOM']

    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+PQ'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['GreenRO+PQ'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])


    m.params['pts'] = 51
    m.params['repetitions'] =  0.5e6/m.params['pts']/2  #nr of repetitions per cycle
    m.params['nr_of_cycles'] = 30                       # nr of times we read out the qutau
                                                        # nr of reps per datapoint is nr_of_cycles*repetitions/pts/2 (2 comes from 2 syncs per RO)
    m.params['N'] = 16
    m.params['dtau'] = 0.02e-6
    m.params['start'] = start
    # Sweep settings for your conventional Ramsey measurement with an artifical detuning (sweeping phase of second pi/2)
    m.params['sweep_name'] = 'tau [us]'
    m.params['detuning']=0e3
    #m.params['free_evolution_times'] = np.linspace(2*m.params['N']*71,2*m.params['N']*(2+(m.params['pts']-1)*m.params['dtau']*1e6),m.params['pts'])*1e-6
    m.params['free_evolution_times'] = np.linspace(1e6*m.params['start'],(1e6*m.params['start']+(m.params['pts']-1)*m.params['dtau']*1e6),m.params['pts'])*1e-6
    m.params['sweep_pts']  = m.params['free_evolution_times']*1e6
    m.params['second_pi2_phases'] = mod(360*m.params['detuning']*m.params['free_evolution_times'] ,360)
    m.params['do_spatial_optimize'] = True


    # About the MW's
    m.params['mw_power']=21
    #m.params['Square_pi2_amp']=0.04*6
    m.params['MW_modulation_frequencies'] = np.ones(m.params['pts'])*m.params['MW_modulation_frequency']

    
    # The RO
    m.params['total_sync_nr'] = m.params['pts'] * m.params['repetitions']
    m.params['SSRO_repetitions'] = m.params['total_sync_nr']


    missed_syncs,total_syncs=m.measure(debug=False,upload=True)
    return missed_syncs,total_syncs
    
if __name__ == '__main__':
    starts=np.array([8,9,10,11,12])*1e-6
    for s in starts:    
    # s=2e-6
        GreenAOM.turn_off()
        n=SAMPLE_CFG+'_'+str(s)+'us'
        DD(n,start=s)
    #m = Green_RO_DD('GreenRO_DD'+name)
    #gen_seq=dd.SimpleDecoupling(name)