
import sys
import os
sys.path.append("d:/measuring")
import numpy as np
import h5py

from matplotlib import pyplot as plt

from analysis.lib.tools import toolbox as tb
from analysis.lib.m2 import m2
from analysis.lib.m2.ssro import ssro, mbi, sequence, pqsequence
from analysis.lib.nv import nvlevels
from analysis.lib.lde import tail_cts_per_shot_v4 as tail
from analysis.lib.pq import pq_tools, pq_plots
from analysis.lib.math import readout_correction as roc
from analysis.lib.math import error
from analysis.lib.fitting import fit, common
from analysis.lib.tools import plot
reload(m2)
reload(tb)
reload(ssro)
reload(mbi)
reload(sequence)
reload(pqsequence)
reload(tail)
reload(pq_tools)
reload(pq_plots)

def fit_ramsey(folder=None, ax = None, Rmbi_guess=0.9, theta_guess= 1.5705, phi_guess=1.5705):

    """
    fit Rmbi**2Cos(theta)**2 + Rmbi**2Sin(theta)**2(cos(x+phi)+sin(x+phi)
    """
    a, ax, x, y = plot_result(folder,ax)

    Rmbi = fit.Parameter(Rmbi_guess, 'Rmbi')
    theta = fit.Parameter(theta_guess, 'theta')
    phi = fit.Parameter(phi_guess, 'phi')
    
    p0 = [f, A]
    if fit_phi:
        p0.append(x0)
    if fit_k:
        p0.append(k)
    fitfunc_str = 'Rmbi^2 * Cos(theta)^2 + Rmbi^2 * Sin(theta)^2 * (Cos(x+phi)+Cin(x+phi)'

    def fitfunc(x) : 
        return (Rmbi**2)*(np.os(theta))**2 + (Rmbi**2)*(np.sin(theta)**2)*(np.cos(x+phi)+np.sin(x+phi))

    fit_result = fit.fit1d(x,y, None, p0=p0, fitfunc=fitfunc,
        fitfunc_str=fitfunc_str, do_print=True, ret=True)
    plot.plot_fit1d(fit_result, np.linspace(x[0],x[-1],201), ax=ax,
        plot_data=False, print_info=False)