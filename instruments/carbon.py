"""
general carbon object
comes with necessary frequencies and gate parameters.

Methods:
get_optimize_gate_sweeps(N_range, tau_range)
write_attributes_to_msmt_params()
get_frequencies(el_transition)
load_cfg()
save_cfg()
"""


from instrument import Instrument
import types
import qt
import numpy as np
import msvcrt, os, sys, time, gobject
from analysis.lib.fitting import fit, common
import instrument_helper
from lib import config

class carbon(Instrument):  

    def __init__(self, name,SAMPLE_SIL = 'MyTestSample'):
        Instrument.__init__(self, name)
        self.name = name
        self._SAMPLE_SIL = SAMPLE_SIL
        self._carbon_number = name[-1]


        ####
        #init necessary parameters

        ins_pars  = {
                    'freq_1_m1'   : {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':10, 'units': 'Hz'},
                    'freq_m1'   : {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':10, 'units': 'Hz'},
                    'freq_1_p1'   : {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':10, 'units': 'Hz'},
                    'freq_p1'   : {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':10, 'units': 'Hz'},
                    'freq_0'   : {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':10, 'units': 'Hz'},
                    'Ren_tau_m1' : {'type':types.ListType,'flags':Instrument.FLAG_GETSET, 'val':[0]},
                    'Ren_N_m1' : {'type':types.ListType,'flags':Instrument.FLAG_GETSET, 'val':[0]},
                    'Ren_tau_p1' : {'type':types.ListType,'flags':Instrument.FLAG_GETSET, 'val':[0]},
                    'Ren_N_p1' : {'type':types.ListType,'flags':Instrument.FLAG_GETSET, 'val':[0]},
                    'Ren_comp_phase_m1' : {'type':types.ListType,'flags':Instrument.FLAG_GETSET, 'val':[0]}, #output to msmt params is an np.array
                    'Ren_comp_phase_p1' : {'type':types.ListType,'flags':Instrument.FLAG_GETSET, 'val':[0]}, #output to msmt params is an np.array
                    'Ren_flip_electron_for_comp_gate_list_m1' : {'type':types.ListType,'flags':Instrument.FLAG_GETSET, 'val':[False]},
                    'Ren_flip_electron_for_comp_gate_list_p1' : {'type':types.ListType,'flags':Instrument.FLAG_GETSET, 'val':[False]},
                    'Ren_extra_phase_correction_list_m1': {'type':types.ListType,'flags':Instrument.FLAG_GETSET, 'val':[0]*10}, #output to msmt params is an np.array
                    'Ren_extra_phase_correction_list_p1': {'type':types.ListType,'flags':Instrument.FLAG_GETSET, 'val':[0]*10} #output to msmt params is an np.array
                    }
        instrument_helper.create_get_set(self,ins_pars)

        self.add_function('write_attributes_to_msmt_params')
        self.add_function('get_optimize_gate_sweep')
        self.add_function('get_frequencies')
        self.add_function('get_sample_name')
        # self.add_fucntion('get_carbon_number')

        cfg_fn = os.path.join(qt.config['ins_cfg_path']+'\\'+self._SAMPLE_SIL, name+'.cfg')
        cfg_dir = os.path.dirname(cfg_fn)

        ### does the sample folder exist?
        if not os.path.exists(cfg_dir):
            os.makedirs(cfg_dir)
        # print cfg_fn

        ### does the carbon exist?
        if not os.path.exists(cfg_fn):
            _f = open(cfg_fn, 'w')
            _f.write('')
            _f.close()

        self._ins_cfg = config.Config(cfg_fn)     
        self.load_cfg()
        self.save_cfg()


    # def get_carbon_number(self):
    #     return self._carbon_number

    def get_all(self):
        for n in self.get_parameter_names():
            self.get(n)
        
    
    def load_cfg(self):
        params_from_cfg = self._ins_cfg.get_all()

        for p in params_from_cfg:
            val = self._ins_cfg.get(p)
            if type(val) == unicode:
                val = str(val)
            
            try:
                self.set(p, value=val)
            except:
                pass

    def save_cfg(self):
        parlist = self.get_parameters()
        for param in parlist:
            value = self.get(param)
            self._ins_cfg[param] = value

        ### public methods

    def write_attributes_to_msmt_params(self,msmt_params):
        """
        should be executed before every measurement.
        Uses the carbon insrument as a dictionary and writes all parameters to the msmt_params.
        """

        for p in self.get_parameter_names():
            param = self.get(p)

            #### every list with phase in the name needs to converted to an array for easy division from rad to degrees
            if type(param) == list and 'phase' in p:
                param = np.array(param)

            msmt_params['samples'][msmt_params['samples']['current']]['C'+self._carbon_number+'_'+p] = param
        

    def set_carbon_params_from_msmt_params(self,msmt_params,verbose=False):
        """
        goes through msmt params and writes relevant parameters to the carbon instrument
        """

        for p in self.get_parameter_names():
            try:
                self.set(p, value = msmt_params['samples'][msmt_params['samples']['current']]['C' + self._carbon_number+'_'+p])
            except:
                if verbose:
                    print 'Could not find parameter %s in msmt params! Therefore OMITTED!' %('C' + self._carbon_number+'_'+p)


    def get_optimize_gate_sweep(self,N_range,tau_range,el_transition):
        """
        Returns sweeps for the carbon gate optimization routine. 
        --> Sweep N for a number of tau values.
        Returns tau_list, N_list
        Does not work for composite gates yet.
        """


        if tau_range%2e-9 != 0 or N_range%2 !=0:
            print 'range not divisible by 2 ns/pulses. gate optimization stopped'
            return

        tau = self.get('Ren_tau_'+el_transition)[0]
        N = self.get('Ren_N_'+el_transition)[0]

        ## make this a function that returns a custom msmt dict for each carbon
        raw_tau_arr = np.arange(tau - tau_range, tau + tau_range, 2e-9)
        raw_N_arr = np.arange(N - N_range, N + N_range+1, 2)
        sweep_len = len(raw_tau_arr) * len(raw_N_arr)
        tau_arr = []
        N_arr = []

        #put comeplete list together.

        for i in range(len(raw_tau_arr)):
            tau_arr = tau_arr + [raw_tau_arr[i]]*(N_range+1)

        N_arr = raw_N_arr

        for i in range( int(tau_range / 2e-9 * 2) - 1):
            N_arr = np.concatenate((N_arr,raw_N_arr))

        return tau_arr,N_arr


    def get_frequencies(self, el_transition = None):
        """
        Returns all relevant frequencies for a given electron transition (string)
        """

        #return all frequencies
        if el_transition == None:
            return self.get_freq_0(), self.get_freq_1_m1(), self.get_freq_m1(), self.get_freq_1_p1(), self.get_freq_p1()

        #+1
        elif 'p' in el_transition or '+' in el_transition:
            return self.get_freq_0(),self.get_freq_1_p1(),self.get_freq_p1()

        #-1
        elif 'm' in el_transition or '-' in el_transition:
            return self.get_freq_0(), self.get_freq_1_m1(), self.get_freq_m1()

        else:
            print 'Wrong electron transition given to get_frequencies'
            return False

    def get_sample_name(self):
        return self._SAMPLE_SIL

    def remove(self):
        self.save_cfg()
        print 'removing'
        Instrument.remove(self)

    def reload(self):
        self.save_cfg()
        print 'reloading'
        Instrument.reload(self)




