### Instrument class to control the JPE CPSHR cryogenic positiong stage with high mechanical resonance.
### C Bonato (08-2014)

from instrument import Instrument
import types
import logging
import re
import math
import subprocess as sp
import time
import numpy as np
import msvcrt

class JPE_CADM(Instrument):
    #Controller for coarse PiezoKnob positioning
    
    def __init__(self, name):
        Instrument.__init__(self, name)
        print '--- Initializing JPE PiezoKnob high mechanical resonance stage ---- '
        self.type = 'PK1801'
        self.TRQFR = 1

        self.pzknb_command = 'D:\measuring\jpe\pzknb_CMD\pzknb'

        self.add_function('get_type')
        self.add_function('status')
        self.add_function('info')
        # self.add_function('move_cnt')
        self.add_function('move')
        self.add_function('stop')

    def get_type(self):
        print '-------JPE controller: '+self.type

    def status(self, addr = 0):
        out = sp.check_output ([self.pzknb_command, 'S', str(addr)])
        print 'JPE STATUS: \n', out
        return out

    def is_busy (self, addr = 0):
        out = sp.check_output ([self.pzknb_command, 'S', str(addr)])
        if 'STOP' in str(out):
            return False
        elif 'MOVE' in str(out):
            return True
        else: #this option should never occur, since also if in ERROR, out contains STOP. 
            print out


    def info (self, addr, ch):
        output = sp.check_output ([self.pzknb_command, 'i', str(addr), str(ch)])
        print output
        
    # def move_cnt (self, cw = 0):
    #     """function that invokes continuous movement of the JPE
    #     SvD: I don't think this function would work, as no addr and ch are specified.
    #     """
    #     if (cw == 0):
    #         print 'Specify direction (clockwise: > 0, counter-clockwise: <0)'
    #     else:
    #         cw = int((np.sign(cw)+1)/2)
    #         out = sp.check_output [self.pzknb_command, 'M', str(addr), str(ch), self.type, str(self.T), 
    #                                         str(cw), str(self.freq), str(self.rel_step), str(0)]

    def stop (self, addr):
        if ((addr>0)&(addr<4)):
            print 'Stop'
            out = sp.check_output [self.pzknb_command, 'STP', str(addr)]
        else:
            print 'Specified address not available!'
            
    def move (self, addr, ch, steps, T, freq, rel_step):
        cw = int((np.sign(steps)+1)/2)
        steps = abs(steps)
        steps_int = int(steps)
        steps_cent = int(steps*100)-100*int(steps)

        if not(steps==0):
            out = sp.check_output ([self.pzknb_command, 'M', str(addr), str(ch), self.type, str(T), str(cw), str(freq), str(rel_step), str(steps_int)])
            #start = time.time()
            # while(self.is_busy(addr)):  #### wait until the JPE tells you it stopped moving. CANNOT DO THIS SINCE IT REVEALS ERROR
            #     time.sleep(0.005)
            #     if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): ###In here now, since program is in testing phase... can be removed later
            #         print "You hit q, stopping wait time"
            #         break
            #stop = time.time()
            if "ERROR" in out: #TODO: printing error now, but requires better error handling
                print(out)
            sleeptime = (1./freq)*steps_int +0.2
            time.sleep(sleeptime)
            #print "finished moving large steps. time it took in s: ",(stop-start)

            if not (steps_cent==0):
                out = sp.check_output( [self.pzknb_command, 'M', str(addr), str(ch), self.type, str(T), str(cw), str(freq), str(1), str(steps_cent)])
                #start = time.time()
                # while(self.is_busy(addr)):  #### wait until the JPE tells you it stopped moving
                #     time.sleep(0.005)
                #     if (msvcrt.kbhit() and (msvcrt.getch() == 'q')):###In here now, since program is in testing phase... can be removed later
                #         print "You hit q, stopping wait time"
                #         break 
                #stop = time.time()
                if "ERROR" in out:
                    print out
                sleeptime = (1./freq)*steps_cent + 0.2
                time.sleep(sleeptime)
                #print "finished moving small steps. time it took in s: ",(stop-start)
                       
 
