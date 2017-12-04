"""
Script for e-spin Hahn echo. Uses pulsar sequencer
"""
import time
import qt
import numpy as np
import msvcrt
# from Creating_exp_list_gateset import gateset_helpers
import measurement.scripts.mbi.mbi_funcs as funcs
# import Creating_exp_list_gateset

#reload all parameters and modules


from measurement.scripts.mbi import mbi_funcs
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
from measurement.lib.measurement2.adwin_ssro import pulse_select as ps
reload(mbi_funcs)

# from darkesr, use of some of these is hidden. Not relevant
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2

from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt, pulsar_delay
from measurement.lib.measurement2.adwin_ssro import pulse_select as ps



import re
import numpy
# import pygsti

#Set matplotlib backend: the ipython "inline" backend cannot pickle
# figures, which is required for generating pyGSTi reports
import matplotlib  
matplotlib.use('Agg')



execfile(qt.reload_current_setup)

#name = 'HANS_sil4'
SAMPLE = qt.exp_params['samples']['current']
SAMPLE_CFG = qt.exp_params['protocols']['current']
name=SAMPLE_CFG

def show_stopper():
    print '---------------------------'            
    print 'Press q to stop measurement'
    print '---------------------------'
    qt.msleep(1)
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
        return True
    else: 
        return False


def electronT2_NoTriggers(name, debug = False, range_start = 0e-6, range_end=1000e-6):
    m = pulsar_delay.ElectronT2NoTriggers(name)

    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    m.params['pulse_type'] = 'Hermite'

    m.params['Ex_SP_amplitude']=0
    m.params['AWG_to_adwin_ttl_trigger_duration']=2e-6  # commenting this out gives an erro
    m.params['wait_for_AWG_done']=1
    m.params['sequence_wait_time']=1

    pts = 51
    m.params['pts'] = pts
    m.params['repetitions'] = 500
    #m.params['wait_for_AWG_done']=1
    #m.params['evolution_times'] = np.linspace(0,0.25*(pts-1)*1/m.params['N_HF_frq'],pts)
    # range from 0 to 1000 us
    m.params['evolution_times'] = np.linspace(range_start,range_end,pts) 

    # MW pulses
    m.params['detuning']  = 0 #-1e6 #0.5e6
    X_pi2 = ps.Xpi2_pulse(m)
    X_pi = ps.X_pulse(m)
    m.params['pulse_sweep_pi2_phases1'] = np.ones(pts) * m.params['X_phase']    # First pi/2 = +X
    # m.params['pulse_sweep_pi2_phases2'] = np.ones(pts) * (m.params['X_phase']+180 )   # Second pi/2 = mX
    m.params['pulse_sweep_pi2_phases2'] = np.ones(pts) * m.params['X_phase']
    m.params['pulse_sweep_pi_phases'] = np.ones(pts) * m.params['X_phase']


    # for the autoanalysis
    m.params['sweep_name'] = 'evolution time (ns)'
    m.params['sweep_pts'] = (m.params['evolution_times'] + 2*m.params['Hermite_pi2_length'] + m.params['Hermite_pi_length'])* 1e9

    # for the self-triggering through the delay line
    # m.params['self_trigger_delay'] = 500e-9 # 0.5 us
    # m.params['self_trigger_duration'] = 100e-9

    # Start measurement
    m.autoconfig()
    m.generate_sequence(upload=True, pulse_pi2 = X_pi2, pulse_pi = X_pi)

    if not debug:
        m.run(autoconfig=False)
        m.save()
        m.finish()




def seq_append(split):
    """
    Help function to make single fiducial / germ sequences
    """
    string = ''

    for i in range(len(split)):
        if split[i] == "Gi":
            string +='e'
        elif split[i] == "Gx":
            string +='x'
        elif split[i] == "Gy":
            string +='y'   
        elif split[i] == "Gu":
            string +='u' 
        elif split[i] == "Gv":
            string +='v' 
            
    if string=='':
        string +='e'
        
    return [string]
        

def create_experiment_list_pyGSTi(filename):
    """
    Extracting list of experiments from .txt file
    Parameters:
    filename: string
        Name of the .txt file. File must be formatted in the way as done by
        pyGSTi.
        One gatesequence per line, formatted as e.g.:Gx(Gy)^2Gx. This is usually created
        with the simulateGST ipython notebook, and saved as MyDataTemplate.txt
    Returns:
    Nested list of single experiment in a format the code below can understand it 
    """

    try:
        experiments = open(filename)
        sequences = experiments.read().split("\n")
        experiments.close()   
    except:
        print "Could not open the filename you provided."
        return
    
    experimentlist = []

    #A parameter to label our experimental runs 
    a = 1

    for i in range(len(sequences)):
        clean_seq = sequences[i].strip()
        gateseq = []
        fiducial = []
        germs = []
        measfiducial = []
        power = 0
        
        # Special case of no fiducials and no germs
        if "{}" in clean_seq:
            fiducial.extend('e')
            measfiducial.extend('e')
            germs.extend('e')
            power = 1
        
        # Case of a germ sequence with at least one fiducial around
        elif "(" in clean_seq:
            #Case of repeated germs
            if "^" in clean_seq:
                power = int(re.findall("\d+", clean_seq)[0])
                result = re.split("[(]|\)\^\d", clean_seq)
            
            #Only one germ
            else:
                power = 1
                result = re.split("[()]", clean_seq)
                
            fiducial.extend(seq_append(re.findall("G[xyuvi]", result[0])))
            germs.extend(seq_append(re.findall("G[xyuvi]", result[1])))
            measfiducial.extend(seq_append(re.findall("G[xyuvi]", result[2])))

        #Otherwise it is a single germ sequence without fiducials
        elif ("Gi" in clean_seq) or ("Gx" in clean_seq) or ("Gy" in clean_seq) or ("Gu" in clean_seq) or ("Gv" in clean_seq) and ("(" not in clean_seq) :
            power = 1
            
            fiducial.extend('e')
            germs.extend(seq_append(re.findall("G[xyuvi]", clean_seq)))
            measfiducial.extend('e')

        #Make sure we only extend the experimentlist in case we did not look at a comment line or empty line
        if power !=0:
            gateseq.extend(fiducial)           
            gateseq.extend(germs)  
            gateseq.extend(measfiducial)
            gateseq.append(power)
            gateseq.append(a)
            
            a+=1

            experimentlist.append(gateseq)
       
    #Make sure everything worked. -2 for sequences as first line is comments and last line is empty
    if len(experimentlist) < (len(sequences)-2):
        print("Lenght list of experiments too short, something went wrong. Check your mess.")
        return
    
    return experimentlist




def gateset(m, debug = False, decoupling = True, multiple=False, pi=True, single_decoupling = False, last_seq = False, fid_1 = ['e'], fid_2 = ['e'], sequence_type = 'all', germ = ['e'], germ_position = [1,3], N_decoupling = [4], run_numbers=[1,2,3]):
    """
    Function used to run GST on the individual experiment level.
    """

    if sequence_type == 'specific_germ_position':
        m = pulsar_delay.GateSetWithDecoupling(name)
        mbi_funcs.prepare(m) # load msmt params

    

    #from mbi_funcs.py
    m.params['E_RO_durations']      = [m.params['SSRO_duration']]
    m.params['E_RO_amplitudes']     = [m.params['Ex_RO_amplitude']]
    m.params['send_AWG_start']      = [1]
    m.params['sequence_wait_time']  = [0]


    #Specific to make it work on LT2
    m.params['initial_msmt_delay'] = 5000.0e-9

    #The total number of sequence repetitions
    m.params['reps_per_ROsequence'] = 5000

    m.params['fid_1']               = fid_1
    m.params['fid_2']               = fid_2
    m.params['sequence_type']       = sequence_type
    m.params['germ']                = germ
    m.params['germ_position']       = germ_position
    m.params['N_decoupling']        = N_decoupling
    m.params['run_numbers']         = run_numbers

    #Muss auch nicht imer definiert werden
    
    #Calculae the larmor frequency, since we want to sit on larmor revival points for this experiment
    tau_larmor = np.round(1/m.params['C1_freq_0'],9)
    m.params['tau_larmor'] = tau_larmor

    if decoupling:

        #The spacing in between germ pulses
        t_bw_germs = 50e-9
        m.params['wait_time'] = t_bw_germs
        
        #We need to check that our germ / fiducial pulses fit between two larmor times, and otherwise make it an
        #integer multiple of the initial value. Strictly the fiducial does not go in here. In the end this is probably not necessary since
        #our sequences are very short.
        sequence_length = max(len(max(fid_1, key=len)), len(max(fid_2, key=len)), len(max(germ, key=len)))*(m.params['Hermite_pi2_length']+t_bw_germs)+t_bw_germs

        if 2*tau_larmor <= sequence_length:
            tau_larmor *= np.ceil(sequence_length/(2*tau_larmor))
            print "Adjusted larmor frequency to multiple", tau_larmor
        # tau_larmor *= 4
        # print tau_larmor

        m.params['tau_larmor'] = tau_larmor

        m.params['sweep_name'] = 'Total evolution time [ms]'
        m.params['sweep_pts'] = run_numbers*np.ones(len(run_numbers))*tau_larmor*1.e3

    else:
        m.params['sweep_name'] = 'Germ repetitions'
        m.params['sweep_pts'] = run_numbers

    #Set up the pulses we want to use in the experiment. First all the pi2 pulses.
    X_pi2   = ps.Xpi2_pulse(m)
    Y_pi2   = ps.Ypi2_pulse(m)
    mX_pi2  = ps.mXpi2_pulse(m)
    mY_pi2  = ps.mYpi2_pulse(m)

    #Set up all the pi pulses.
    X_pi    = ps.X_pulse(m)
    Y_pi    = ps.Y_pulse(m)
    mX_pi   = ps.mX_pulse(m)
    mY_pi   = ps.mY_pulse(m)

    # for the autoanalysis
    # m.params['sweep_name']  = 'Run number'
    # m.params['sweep_pts']   = 1

    # Now calculate how many sweeps we want to do. For now we want to put a germ pulse at different subsequent 
    # locations. Later, we want to make this random
    if sequence_type == "all":
        if len(fid_1) == len (fid_2) == len(germ) == len(N_decoupling) == len(run_numbers):
            m.params['pts'] = len(fid_1)
        else: 
            sys.exit("A mistake happened. Check your fiducials and germ lists have the same length.")

    else:
        m.params['pts'] = len(germ_position)


    # Start measurement
    m.autoconfig()
    m.generate_sequence(pi = pi, decoupling = decoupling, upload=True, single_decoupling = single_decoupling, x_pulse_pi2 = X_pi2, y_pulse_pi2 = Y_pi2, x_pulse_mpi2 = mX_pi2, y_pulse_mpi2 = mY_pi2, x_pulse_pi = X_pi, y_pulse_pi = Y_pi, x_pulse_mpi = mX_pi, y_pulse_mpi = mY_pi)


    if not debug:
        m.run(autoconfig=False)

        if multiple:
            print run_numbers[0]
            m.save(name='Start_run%d' %run_numbers[0])

        else:
            m.save()

        if not multiple:
            m.finish()

        else:
            if last_seq == True:
                m.finish()
        # if sequence_type == 'specific_germ_position':
        #     m.finish()

def reoptimize():
    """
    Function used for reoptimizing on the NV center position
    """
    GreenAOM.set_power(10e-6)
    optimiz0r.optimize(dims=['x','y','z'], cycles=2)
    GreenAOM.turn_off()

def individual_awg_write_ro(filename, debug = True, pi=True, decoupling = True, awg_size = 50):
    """
    Function used to set up a long sequence of experiments. 
    Inputs are: filename,   a filename that corresponds to the list of experiments as output by the pygsti package. Foir this use the ipython notebook SimulateGST.
                debug,      wether we want to run the seuqnece just for debugging, or for real
                pi,         wether we want to run pi or pi/2 pulses. Irrelevant when using the self-focusing mechanism.
                decoupling, If we want our code to come up with a decoupling sequence (currently only XY8 implemented) for us to decouple in between germ pulses
                awg_size    the size of individual measurements that we break our overall length of experimental runs saved in filename into. This is needed as to not 
                            freeze the AWG with a memory error.
    This function then calls the gateset function, which handles individual awg runs.
    """
    
    #Variable I need to check wether we are running the last sequence
    last_seq = False

    #Create a list of all experiments that we want to do. Assumes that we created a filename before with our ipython notebook Simulating GST.
    experimentalist = create_experiment_list_pyGSTi(filename)
    global experimentalist
    
    #Determine the number of awg runs we want to run, making sure we always round up so we take all the data we want
    if debug:
        awg_runs = 1
    else:
        awg_runs = int(len(experimentalist)/awg_size) + (len(experimentalist) % awg_size > 0)
    
    print "This experiment will have", awg_runs, "runs"

    #To keep track what we need to do for the save name
    if awg_runs >1:
        multiple = True

    else: multiple = False


    if decoupling:
        m = pulsar_delay.GateSetWithDecoupling(name)

    else:
        print "No decoupling"
        # m = pulsar_delay.GateSetNoDecoupling(name)
        m = pulsar_delay.GateSetNoDecouplingTiming(name)


    mbi_funcs.prepare(m)
    run_names = []

    for i in range(awg_runs):

        #If we are not debugging and we are runnign a real sequence, then reoptimize the NV counts signal every twenty sequences to counteract drift 
        if i % 20 == 0 and debug == False:
            reoptimize()

        if i == awg_runs:
            last_seq = True

        ## Option to stop the measurement in a clean fashion every awg_size measurements
        breakst = show_stopper()
        if breakst: break

        #Create a sublist of our experimental list in which we have all the current experiments we want to run in the awg
        single_awg_list = experimentalist[i*awg_size:(i+1)*awg_size]

        fid_1   = [pos[0]   for pos in single_awg_list]
        germ    = [pos[1]   for pos in single_awg_list]
        fid_2   = [pos[2]   for pos in single_awg_list]
        if decoupling:
            N_dec   = [pos[3]+1 for pos in single_awg_list]
        else:
            N_dec   = [pos[3] for pos in single_awg_list]
        run     = [pos[4] for pos in single_awg_list]

        #Print progress updates since these are very long measurements
        print "Currently working on run numbers", run
        print float(100*i/awg_runs), "% of measurements are finished"

        run_names.extend(['Start_run%d' %run[0]])

        #Optimierungspotential!
        m.params['all_run_names'] = run_names

        #Finally pass everything to the gateset function
        gateset(m, debug = debug, decoupling = decoupling, multiple = multiple, pi = pi, last_seq = last_seq, fid_1 = fid_1, fid_2 = fid_2, sequence_type = 'all', germ = germ, N_decoupling = N_dec, run_numbers=run)
   
    if not debug:
        m.finish()


def electronRefocussingTriggered(name, debug = False, range_start = -2e-6, range_end = 2e-6, 
    evolution_1_self_trigger=True, evolution_2_self_trigger=False, vary_refocussing_time=False,
    refocussing_time = 200e-6):
    m = pulsar_delay.ElectronRefocussingTriggered(name)

    m.params.from_dict(qt.exp_params['samples'][SAMPLE])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['AdwinSSRO-integrated'])
    m.params.from_dict(qt.exp_params['protocols']['AdwinSSRO+espin'])
    m.params.from_dict(qt.exp_params['protocols']['cr_mod'])
    m.params.from_dict(qt.exp_params['protocols'][SAMPLE_CFG]['pulses'])

    m.params['pulse_type'] = 'Hermite'

    m.params['Ex_SP_amplitude']=0
    m.params['AWG_to_adwin_ttl_trigger_duration']=2e-6  # commenting this out gives an erro
    m.params['wait_for_AWG_done']=1
    m.params['sequence_wait_time']=1

    m.params['do_delay_voltage_control']=0
    m.params['delay_voltage_DAC_channel'] = 14

    pts = 51
    m.params['pts'] = pts
    m.params['repetitions'] = 1000





    #m.params['wait_for_AWG_done']=1
    #m.params['evolution_times'] = np.linspace(0,0.25*(pts-1)*1/m.params['N_HF_frq'],pts)
    # range from 0 to 1000 us

    # calibrated using Hahn echo
    m.params['self_trigger_delay'] = 2.950e-6 * np.ones(pts)
    m.params['self_trigger_duration'] = 100e-9

    if vary_refocussing_time:
        m.params['refocussing_time'] = np.linspace(range_start, range_end, pts)
        m.params['defocussing_offset'] = 0.0 * np.ones(pts)

        m.params['sweep_name'] = 'single-sided free evolution time (us)'
        m.params['sweep_pts'] = (m.params['refocussing_time']) * 1e6

    else:
        m.params['refocussing_time'] = np.ones(pts) * refocussing_time
        m.params['defocussing_offset'] = np.linspace(range_start,range_end,pts)

        m.params['sweep_name'] = 'defocussing offset (us)'
        m.params['sweep_pts'] = (m.params['defocussing_offset']) * 1e6

    # MW pulses
    X_pi2 = ps.Xpi2_pulse(m)
    X_pi = ps.X_pulse(m)

    # for the self-triggering through the delay line
    # m.params['self_trigger_delay'] = 500e-9 # 0.5 us
    # m.params['self_trigger_duration'] = 100e-9

    # Start measurement
    m.autoconfig()
    m.generate_sequence(upload=True, pulse_pi2 = X_pi2, pulse_pi = X_pi, evolution_1_self_trigger=evolution_1_self_trigger, evolution_2_self_trigger=evolution_2_self_trigger)

    if not debug:
        m.run(autoconfig=False)
        m.save()
        m.finish()



if __name__ == '__main__':

    # reoptimize()

    # electronT2_NoTriggers(name, debug=False)
    # bins = np.linspace(-5e-6, 5e-6, 11)[2:]

    # for i in range(len(bins) - 1):
    #     if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
    #         print 'aborting'
    #         break
    #     reoptimize()
    #     print('Starting delay line refocussing run with self-trigger offsets from {} ns to {} ns'.format(bins[i] * 1e9, bins[i+1] * 1e9))
    #     electronRefocussingTriggered("OneTrigger_" + name, debug=False, range_start = bins[i], range_end = bins[i+1], evolution_1_self_trigger = True)

    # for i in range(len(bins) - 1):
    #     if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):
    #         print 'aborting'
    #         break
    #     reoptimize()
    #     print('Starting delay line refocussing run with no trigger offsets from {} ns to {} ns'.format(bins[i] * 1e9, bins[i+1] * 1e9))
    #     electronRefocussingTriggered("NoTrigger_" + name, debug=False, range_start = bins[i], range_end = bins[i+1], evolution_1_self_trigger = False)

    # hahn_echo_range = [1.0e-6, 10.0e-6]
    # defocussing_range = [-0.5e-6, 0.5e-6]

    # electronT2_NoTriggers(name, debug=True, range_start = hahn_echo_range[0], range_end = hahn_echo_range[1])


    individual_awg_write_ro("D://measuring//measurement//scripts//Gateset_tomography//MyDataTemplate.txt", 
        debug = True, 
        decoupling = False, 
        pi=True, awg_size = 40)

    # gateset(pulsar_delay.GateSetWithDecoupling(name), debug = False, pi=True, single_decoupling = False,  fid_1 = ['x', 'x', 'x', 'x', 'x'], fid_2 = [ 'm', 'm', 'm', 'm', 'm'], sequence_type = 'all', germ = ['e', 'e', 'e', 'e', 'e'], N_decoupling = [1, 2, 4, 8, 16] ,run_numbers=[1, 2, 4, 8, 16])
#
    # individual_awg_write_ro("D://measuring//measurement//scripts//Gateset_tomography//MyDataset.txt", debug = False, decoupling = True, pi=True, awg_size = 10)

    # gateset(pulsar_delay.GateSetNoDecoupling(name), debug = True, fid_1 = ['xx'], fid_2 = [ 'm'], sequence_type = 'all', germ = ['xx'], N_decoupling = [2] ,run_numbers=[2])

    # individual_awg_write_ro("D://measuring//measurement//scripts//Gateset_tomography//MyDataset.txt", debug = False, decoupling = True, pi=False, awg_size = 10)
# 
    # gateset(pulsar_delay.GateSetWithDecoupling(name), debug = True, fid_1 = ['x', 'x', 'x'], fid_2 = ['m', 'm', 'm'], sequence_type = 'all', germ = ['e', 'e', 'e'], N_decoupling = [2, 4, 8], run_numbers=[2, 4, 8])

