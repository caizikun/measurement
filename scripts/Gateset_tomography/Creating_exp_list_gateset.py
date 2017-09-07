#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 11:06:22 2017

@author: mruf
"""

import re
import numpy
# import pygsti

#Set matplotlib backend: the ipython "inline" backend cannot pickle
# figures, which is required for generating pyGSTi reports
import matplotlib  
matplotlib.use('Agg')

class gateset_helpers():

    def __init__(self):
     
        return

    def seq_append(self, split):
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
                
        if string=='':
            string +='e'
            
        return [string]
            

    def create_experiment_list_pyGSTi(self, filename):
        """
        Extracting list of experiments from .txt file
        Parameters:
        filename: string
            Name of the .txt file. File must be formatted in the way as done by
            pyGSTi.
            One gatesequence per line, formatted as e.g.:Gx(Gy)^2Gx.
        Returns:
        Nested list of single experiments, 
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
                    
                fiducial.extend(self.seq_append(re.findall("G[xyi]", result[0])))
                germs.extend(self.seq_append(re.findall("G[xyi]", result[1])))
                measfiducial.extend(self.seq_append(re.findall("G[xyi]", result[2])))

            #Otherwise it is a single germ sequence without fiducials
            elif ("Gi" in clean_seq) or ("Gx" in clean_seq) or ("Gy" in clean_seq) and ("(" not in clean_seq) :
                power = 1
                
                fiducial.extend('e')
                germs.extend(self.seq_append(re.findall("G[xyi]", clean_seq)))
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

    def individual_awg_write_ro(self, filename, awg_size = 50):
        
        #Create a list of all experiments that we want to do. Assumes that we created a filename before
        experimentalist = self.create_experiment_list_pyGSTi(filename)
        
        #Determine the number of awg runs we want to run, making sure we always round up so we take all the data we want
        awg_runs = int(len(experimentalist)/awg_size) + (len(experimentalist) % awg_size > 0)
        
        for i in range(awg_runs):

            #Create a sublist of our experimental list in which we have all the current experiments we want to run in the awg
            single_awg_list = experimentalist[i*awg_size:(i+1)*awg_size]

            fid_1   = [pos[0] for pos in single_awg_list]
            germ    = [pos[1] for pos in single_awg_list]
            fid_2   = [pos[2] for pos in single_awg_list]
            N_dec   = [pos[3] for pos in single_awg_list]
            run     = [pos[4] for pos in single_awg_list]
        
        # print len(experimentalist), len(single_awg_list), awg_runs, single_awg_list, '\n'
        # print fid_1, run


        
        return experimentalist



a = gateset_helpers()

a.individual_awg_write_ro("D://measuring//measurement//scripts//Gateset_tomography//MyDataset.txt", awg_size = 10)
    


