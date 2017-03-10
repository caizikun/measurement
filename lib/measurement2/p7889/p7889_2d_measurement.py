import os
import qt
import numpy as np
import msvcrt
import hdf5_data as h5
import time


import sys

from measurement.lib.measurement2 import measurement as m2
from measurement.lib.pulsar import pulse,pulselib,pulsar,element

from instrument import Instrument


class P7889Measurement2D(m2.Measurement):

    #def __init__(self, name):
    #    m2.Measurement.__init__(self, name)
    
    def autoconfig(self):
        self._init_p7889()

    def _init_p7889(self):
        self.p7889.set_binwidth(self.params['p7889_binwidth'])
        self.p7889.set_range(self.params['p7889_range'])
        self.p7889.set_ROI_min(self.params['p7889_ROI_max'])
        self.p7889.set_ROI_max(self.params['p7889_ROI_min'])
        
        self.p7889.set_starts_preset(True)
        self.p7889.set_sweepmode_start_event_generation(True)
        self.p7889.set_sweepmode_sequential(True)
        self.p7889.set_sweepmode_wrap_around(False)
        self.p7889.set_sweepmode_DMA(self.params['p7889_use_dma'])
        self.p7889.set_number_of_cycles(self.params['p7889_number_of_cycles'])
        self.p7889.set_number_of_sequences(self.params['p7889_number_of_sequences'])
        self.p7889.set_sweep_preset_number(self.params['p7889_sweep_preset_number'])
        self.p7889.set_starts_preset(True)

    def _get_p7889_data(self):
        return self.p7889.get_2Ddata()

    def run(self):
        self.p7889.Start()
        qt.msleep(0.5)

        while self.p7889.get_state(): 
            qt.msleep(0.1)
            if msvcrt.kbhit():
                kb_char=msvcrt.getch()
                if kb_char == "q": 
                    stop = True
                    break


    def save_2D_data(self, timename='t (ns)', sweepname='sweep_value', ret=False):

        grp=h5.DataGroup('p7889_raw_data',self.h5data,base=self.h5base)
        self.save_params(grp=grp.group)

        x,yint,z = self._get_p7889_data()

        #### convert x to bins.... because this is what we see on the 
        y=self.params['sweep_pts']
        xx, yy = np.meshgrid(x,y)

        #dat=h5.HDF5Data(name=self.name)
        grp.add_coordinate(name='t (ns)',data=x, dtype='f8')
        grp.add_coordinate(name=self.params['sweep_name'],data=y)
        grp.add_value(name='Counts',data=z)

        # m2.save_instrument_settings_file(grp.group)

        #do post-processing
        grp1=h5.DataGroup('processed data',self.h5data,base=self.h5base)

        
        if self.params['Eval_ROI_start']<np.amin(x):
            startind=[0]
        else:
            startind=np.where(x==self.params['Eval_ROI_start'])


        if self.params['Eval_ROI_end']>np.amax(x):
            endind=[x.size-1]
        else:
            endind=np.where(x==self.params['Eval_ROI_end'])

        #strip the count array of points in time that lie outside of the specified ROIs
        # print x
        # print startind,endind
        sliced=z[:,startind[0]:endind[0]]
        # print sliced

        summation=np.array(range(self.params['pts']))

        for i,row in enumerate(sliced):
            summation[i]=np.sum(row)

        grp1.add_coordinate(name=self.params['sweep_name'],data=y)
        grp1.add_value(name='Counts in ROI',data=summation)

        plt=qt.plot(name=self.mprefix+self.name,clear=True)
        plt.add(y,summation,'rO',yerr=np.sqrt(summation))
        plt.add(y,summation,'r-')
        plt.set_plottitle(self.name)
        plt.set_legend(False)
        plt.set_xlabel(self.params['sweep_name'])
        plt.set_ylabel('counts')
        plt.save_png(self.datafolder+'\\'+self.name+'.png')

        self.h5data.flush()

        if ret:
            return x,y,z

        else:
            self.h5data.flush()




class P7889PulsarMeasurement(P7889Measurement2D):
    mprefix = 'P7889PulsarMeasurement'
    awg = None
    mwsrc = None 


    #def __init__(self, name):
    #    P7889Measurement2D.__init__(self, name)
    #    self.params['measurement_type'] = self.mprefix

    def autoconfig(self, mw=True, **kw):
        print 'this is the mw frequency!', self.params['mw_frq']
        self.mwsrc.set_iq('on')
        self.mwsrc.set_pulm('on')
        self.mwsrc.set_frequency(self.params['mw_frq'])
        print self.params['mw_power']
        self.mwsrc.set_power(self.params['mw_power'])
        self.mwsrc.set_status('on')

        print 'AWG state before start'
        print self.awg.get_state()

        P7889Measurement2D.autoconfig(self)
   

    def updated_measurement(self):
        """
        Incorporates live plotting for the p7889.
        """
        self.p7889.Start()
        qt.msleep(0.5)
        self.awg.start()
        counter = 0
        opt_ins = qt.instruments['optimiz0r'] # added for long measurements MJD

        GreenAOM = qt.instruments['GreenAOM']

        last_time = time.time()
        sample_time = 5.0

        while self.p7889.get_state(): 
            qt.msleep(0.1)
            counter += 1

            if counter % 1500 == 0: # idem added for long measurement 
                GreenAOM.set_power(self.params['GreenAOM_power'])
                opt_ins.optimize(dims=['x','y','z'], cycles=1)
                opt_ins.optimize(dims=['x','y','z'], cycles=1)
                GreenAOM.turn_off() 
            elif msvcrt.kbhit():
                kb_char=msvcrt.getch()
                if kb_char == "q": 
                    stop = True
                    break
            if (time.time() - last_time) > sample_time:
                last_time = time.time()

                x,z = self.p7889.get_P7889data()
                y=self.params['sweep_pts']

                if self.params['Eval_ROI_start']<np.amin(x):
                    startind=[0]
                else:
                    startind=np.where(x==self.params['Eval_ROI_start'])

                if self.params['Eval_ROI_end']>np.amax(x):
                    endind=[x.size-1]
                else:
                    endind=np.where(x==self.params['Eval_ROI_end'])

                #strip the count array of points in time that lie outside of the specified ROIs
                # print x
                # print startind,endind
                sliced=z[:,startind[0]:endind[0]]
                # print sliced

                summation=np.array(range(self.params['pts']))

                for i,row in enumerate(sliced):
                    summation[i]=np.sum(row)

                plt=qt.plot(name=self.mprefix+self.name,clear=True)
                plt.add(y,summation,'rO',yerr=np.sqrt(summation))
                plt.add(y,summation,'r-')
                plt.set_plottitle(self.name)
                plt.set_legend(False)
                plt.set_xlabel(self.params['sweep_name'])
                plt.set_ylabel('counts')



        self.stop_sequence()

    def run(self):
        GreenAOM = qt.instruments['GreenAOM']
        opt_ins = qt.instruments['optimiz0r'] # added for long measurements MJD
        self.p7889.Start()
        qt.msleep(0.5)
        self.awg.start()
        counter = 0
        while self.p7889.get_state(): 
            qt.msleep(0.1)
            counter += 1
            if counter % 1500 == 0: # idem added for long measurement 
                GreenAOM.set_power(400e-6)
                opt_ins.optimize(dims=['x','y','z'], cycles=1)
                opt_ins.optimize(dims=['x','y','z'], cycles=1)
                GreenAOM.turn_off()    
            elif msvcrt.kbhit():
                kb_char=msvcrt.getch()
                if kb_char == "q": 
                    stop = True
                    break

        self.stop_sequence()

    def generate_sequence(self):
        pass

    def stop_sequence(self):
        self.awg.stop()

    def save(self,**kw):

        grp=self.h5basegroup.create_group('pulsar_settings')
        pulsar = kw.pop('pulsar', qt.pulsar)

        for k in pulsar.channels:
            grpc=grp.create_group(k)
            for ck in pulsar.channels[k]:
                grpc.attrs[ck] = pulsar.channels[k][ck]

        grpa=grp.create_group('AWG_sequence_cfg')
        for k in pulsar.AWG_sequence_cfg:
            grpa.attrs[k] = pulsar.AWG_sequence_cfg[k]


        self.h5data.flush()

    def finish(self,**kw):
        # P7889Measurement2D.finish(self,**kw)

        self.awg.stop()
        self.awg.set_runmode('CONT')

        self.mwsrc.set_status('off')
        self.mwsrc.set_iq('off')
        self.mwsrc.set_pulm('off')


class DarkESR_p7889(P7889PulsarMeasurement):
    mprefix='DarkESR_p7889'

    #def __init__(self, name):
    #    P7889Measurement2D.__init__(self, name) 

    def autoconfig(self):

        self.params['sweep_name']='MW frq (GHz)'

        self.params['sweep_pts']=(np.linspace(self.params['ssbmod_frq_start'],self.params['ssbmod_frq_stop'],self.params['pts']) +  self.params['mw_frq'])*1e-9
        self.params['MW_pulse_mod_risetime']= 30e-9 #not too sure about this value.


        self.params['p7889_number_of_cycles'] = self.params['pts']
        self.params['p7889_number_of_sequences'] = self.params['repetitions']
        P7889PulsarMeasurement.autoconfig(self)

        qt.pulsar.set_channel_opt('AOM_Green','high', qt.instruments['GreenAOM'].power_to_voltage(self.params['GreenAOM_power'],controller='sec'))

    def generate_sequence(self):

        #define the pulses
        sq_p7889=pulse.SquarePulse(channel='p7889_start',name='p7889_square',amplitude=1) 
        sq_p7889.length=2e-6 #that is pretty long, can be reduced in the future.

        wait = pulse.SquarePulse(channel='AOM_Green',name='Green_square')
        wait.amplitude = 0
        wait.length=2e-6
        
        
        sq_AOMpulse=pulse.SquarePulse(channel='AOM_Green',name='Green_square')
        sq_AOMpulse.amplitude=1 #just set the marker high
        sq_AOMpulse.length=self.params['GreenAOM_pulse_length']
        
        X = pulselib.MW_IQmod_pulse('Weak pi-pulse',
            I_channel='MW_Imod', Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod',
            amplitude = self.params['ssbmod_amplitude'],
            length = self.params['MW_pulse_length'],
            PM_risetime = self.params['MW_pulse_mod_risetime'])

        #need one spin polarization pulse at the beginning.
        init=element.Element('initialize',pulsar=qt.pulsar)
        init.add(pulse.cp(sq_AOMpulse,length=1e-6,amplitude=0),name='wait')
        init.add(sq_AOMpulse,name='init',refpulse='wait')

        #generate a list of pulse elements. One for each modulation freuqency
        elements=[]
        elements.append(init)
        
        for k,f in enumerate(np.linspace(self.params['ssbmod_frq_start'],self.params['ssbmod_frq_stop'],self.params['pts'])):

            e=element.Element('DarkESR_frq-%d' % k,pulsar=qt.pulsar)
            e.add(pulse.cp(wait,length=-1e-6,amplitude=0),name='wait_int')
            e.add(X(frequency=f),name='MWpulse',refpulse='wait_int',refpoint='end')
            e.add(sq_p7889,name='p7889Start',start=0.4e-6,refpulse='MWpulse',refpoint='end')
            e.add(sq_AOMpulse,name='GreenLight',start=2.1e-6,refpulse='p7889Start',refpoint='start')
            elements.append(e)
        # was 1.7 before the AOM greenlight pulse
        # was 0.8 before the p7889Start
        # wait length before was 1 e-6 but because there is a false delay in the green line (i guess, it doesn't work)
        # wait length adjusted was -1.6e-6
        # Start p7889start adjusted 0.4e-6
        # Greenlight start adjusted 2.1e-6





        #insert a delay at the end of the sequence such that all outputs of the AWG stay low.
        end=element.Element('ending delay',pulsar=qt.pulsar)
        end.add(pulse.cp(sq_AOMpulse,length=1e-6,amplitude=0),name='delay')
        elements.append(end)

        #create a sequence from the gathered elements
        seq=pulsar.Sequence('DarkESR sequence p7889')
        for e in elements:
            seq.append(name=e.name,wfname=e.name)

        #upload to AWG
        qt.pulsar.program_awg(seq,*elements)

       
class Rabi_p7889(P7889PulsarMeasurement):
    mprefix='Rabi_p7889'

    def __init__(self, name):
        P7889PulsarMeasurement.__init__(self, name) 

    def autoconfig(self):

        self.params['sweep_name']='MW pulse length (us)'

        self.params['sweep_pts']=(np.linspace(self.params['MW_pulse_length_start'],self.params['MW_pulse_length_stop'],self.params['pts']))*1.e6
        self.params['MW_pulse_mod_risetime']=30e-9 #not too sure what this value does.


        self.params['p7889_number_of_cycles'] = self.params['pts']
        self.params['p7889_number_of_sequences'] = self.params['repetitions']
        P7889PulsarMeasurement.autoconfig(self)
        
        # GreenAOM.turn_off()
        
        qt.pulsar.set_channel_opt('AOM_Green','high', qt.instruments['GreenAOM'].power_to_voltage(self.params['GreenAOM_power'],controller='sec'))

    def generate_sequence(self):

        #define the pulses
        sq_p7889=pulse.SquarePulse(channel='p7889_start',name='p7889_square',amplitude=1) 
        sq_p7889.length=1e-6 #is the length of the p7889 start pulse a problem?? ## changed from 2e-6 to 1e-6

        sq_AOMpulse=pulse.SquarePulse(channel='AOM_Green',name='Green_square')
        sq_AOMpulse.amplitude=1 #sets the marker high
        sq_AOMpulse.length=self.params['GreenAOM_pulse_length']
        wait = pulse.SquarePulse(channel='AOM_Green',name='Green_square')
        wait.amplitude = 0
        wait.length=2e-6

        X = pulselib.MW_IQmod_pulse('Rabi_MW_pulse',
            I_channel='MW_Imod', Q_channel='MW_Qmod',
            PM_channel='MW_pulsemod',
            amplitude = self.params['ssbmod_amplitude'],
            frequency = self.params['ssbmod_frequency'],
            PM_risetime = self.params['MW_pulse_mod_risetime'])

        #need one spin polarization pulse at the beginning.
        init=element.Element('initialize',pulsar=qt.pulsar)
        init.add(pulse.cp(sq_AOMpulse,length=1e-6,amplitude=0),name='wait')
        init.add(sq_AOMpulse,name='init',refpulse='wait')
        init.add(wait,name='init_wait',refpulse='init')

        #generate a list of pulse elements. One for each modulation freuqency
        elements=[]
        elements.append(init)
        
            # old sequence MJD
            # e=element.Element('Rabi_length-%d' % k,pulsar=qt.pulsar)
            # e.add(pulse.cp(wait,length=2e-6,amplitude=0),name='wait_int')
            # e.add(X(length=t),name='MWpulse',refpulse='wait_int',refpoint='end')
            # e.add(sq_p7889,name='p7889Start',refpulse='MWpulse',refpoint='end')
            # e.add(sq_AOMpulse,start=1e-6,name='GreenLight',refpulse='p7889Start',refpoint='end')
            # e.add(pulse.cp(sq_AOMpulse,length=50e-9,amplitude=0),name='wait',refpulse='GreenLight')
            # elements.append(e)
        


        for k,t in enumerate(self.params['sweep_pts']/1.e6):

            e=element.Element('Rabi_length-%d' % k,pulsar=qt.pulsar)
            e.add(pulse.cp(wait,length=-1e-6,amplitude=0),name='wait_int')
            e.add(X(length=t),name='MWpulse',refpulse='wait_int',refpoint='end')
            e.add(sq_p7889,name='p7889Start',start=0.4e-6,refpulse='MWpulse',refpoint='end')
            e.add(sq_AOMpulse,start=2.1e-6,name='GreenLight',refpulse='p7889Start',refpoint='start')
            elements.append(e)
        # was 1.7 before the AOM greenlight pulse
        # was 0.8 before the p7889Start
        # wait length before was 1 e-6 but because there is a false delay in the green line (i guess, it doesn't work)
        # wait length adjusted was -1.6e-6
        # Start p7889start adjusted 0.4e-6
        # Greenlight start adjusted 2.1e-6


        #insert a delay at the end of the sequence such that all outputs of the AWG stay low.
        end=element.Element('ending delay',pulsar=qt.pulsar)
        end.add(pulse.cp(sq_AOMpulse,length=1e-6,amplitude=0),name='delay')
        elements.append(end)

        #create a sequence from the gathered elements
        seq=pulsar.Sequence('RabiOsci sequence p7889')
        for e in elements:
            seq.append(name=e.name,wfname=e.name)

        #upload to AWG
        qt.pulsar.program_awg(seq,*elements)



def test_p7789_pulsar_msmt(name):

    m = AdwinSSRO('SSROCalibration_'+name)
    m.params['p7889_use_dma'] = False
    m.params['p7889_sweep_preset_number'] = 1
    m.params['p7889_number_of_cycles'] = 1
    m.params['p7889_number_of_sequences'] = 10000
    m.params['p7889_ROI_min'] = 1
    m.params['p7889_ROI_max'] = 6000
    m.params['p7889_range'] = 4000
    m.params['p7889_binwidth'] = 1 #100 ps
















####################
#Old stuff below!!!#
####################

"""

    def save(self, timename='t (ns)', sweepname='sweep_value',  ret=False, plot_ro=False):

        x,y,z = self.save_2D_data(timename, sweepname, ret=True)
        self.save_ROI_data(x,y,z, sweepname=sweepname)
        self.save_script()
        self.save_parameters()
                
        if plot_ro:
            self.plot_RO_axis(x,y,z)

        if ret:
            return x,y,z


    def save_ROI_data(self, x, y, z, sweepname='sweep_value'):
        roix = y
        roiy = z[:,self.ROI_min:self.ROI_max].sum(axis=1)
        np.savetxt(os.path.join(self.save_folder, 
            self.save_filebase+'_ROI_sum.dat'), np.vstack((roix,roiy)).T)

        p = qt.plot(roix, roiy, 'rO-', name='ROI_summed', clear=True,
                xlabel=sweepname, ylabel='counts', title='ROI summed')

        p.reset()

        h,ts = os.path.split(self.save_folder)
        h,date = os.path.split(h)

        p.set_plottitle(date+'/'+ts+': '+'ROI_summed')
        p.save_png(os.path.join(self.save_folder, self.save_filebase))
    
    def plot_RO_axis(self,x,y,z):
        ysum=z.sum(axis=-0)
        p = qt.plot(x, ysum, 'rO-', name='RO_summed', clear=True,
                xlabel='time', ylabel='counts', title='RO summed')
        
        p.reset()
        p.save_png(os.path.join(self.save_folder, self.save_filebase))




    def get_accumulated_counts(self, z_tot):
        x,yint,z = self._get_p7889_data()
        z_tot += z
        return x, yint ,z_tot

    def save_2D_accumulated_data(self, x, y, z_tot, timename='t (ns)', sweepname='sweep_value', ret=False):
        
        xx, yy = np.meshgrid(x,y)
        
        d = qt.Data(name=self.save_filebase)
        d.add_coordinate(timename)
        d.add_coordinate(sweepname)
        d.add_value('counts')

        p = qt.plot3(d, name='2D_Histogram', clear=True)
        p.reset()
        

        d.create_file()
        
        for i,row in enumerate(z_tot):
            d.add_data_point(xx[i,:], yy[i,:], row)
            d.new_block()        
        d.close_file()

        self.save_folder = d.get_dir()
        self.timestamp = d.get_time_name()[:6]
        self.save_filebase = d.get_time_name()

        # p.reset()
        # qt.msleep(0.1)
        p.save_png(os.path.join(self.save_folder, self.save_filebase))
        
        if ret:
            return x,y,z_tot




class P7889TestMeasurement2D(P7889Measurement2D):

    def __init__(self):
        P7889Measurement2D.__init__(self, 'testing')

        self.p7889_number_of_cycles = 10
        self.p7889_number_of_sequences = 100000
        self.ROI_min = 1200
        self.ROI_max = 4600

    def setup(self):
        P7889Measurement2D.setup(self)

        ADWIN.stop_p7889_Vsweep_triggered()
    
    def measure(self):
        P7889Measurement2D.measure(self)
        
        ADWIN.start_p7889_Vsweep_triggered(stop=True, load=True)
        qt.msleep(1)
        while DP.get_server_running():
            qt.msleep(2)
            print 'running'
            if msvcrt.kbhit():
                    kb_char=msvcrt.getch()
                    if kb_char == "q": 
                        stop = True
                        break
        
        ADWIN.stop_p7889_Vsweep_triggered()
        DP.Stop()

if __name__ == "__main__":
    m = P7889TestMeasurement2D()
    m.setup()
    m.measure()
    m.save()
""" 

