import gzip
import pickle
import matplotlib.pyplot as plt
import yaml
import io
import os
import numpy as np
import hist
from typing import Any, IO, Dict, List
import dctools
from dctools import plot as plotter
import matplotlib.pyplot as plt
import scipy.interpolate as interp
from scipy import stats as st
np.seterr(all='warn')
plt.ioff()

def plotting(config, variable, channel, rebin=1, xlim=[], blind=False, era="someyear", checksyst=True) -> None:
    datasets:Dict = dict()
    color_cycle:List = []
    for name in config.groups:
        histograms = dict(
            filter(
                lambda _n: _n[0] in config.groups[name].processes,
                config.boosthist.items()
            )
        )
        p = dctools.datagroup(
            histograms = histograms,
            ptype      = config.groups[name].type,
            observable = variable,
            name       = name,
            xsections  = config.xsections,
            channel    = channel,
            luminosity = config.luminosity.value,
            rebin      = rebin
        )
        
        datasets[p.name] = p
        if p.ptype == "signal":
            signal = p.name
            
        if hasattr(config.groups[name], "color") and len(p.to_boost().shape):
            color_cycle.append(config.groups[name].color)
    
    _plot_channel = plotter.add_process_axis(datasets)
    pred = _plot_channel.project('process', 'systematic', variable)[:hist.loc('data'),:,:]   
    data = _plot_channel[{'systematic':'nominal'}].project('process', variable)[hist.loc('data'),:]
    

    plt.figure(figsize=(6,7))
    ax, bx = plotter.mcplot(
        pred[{'systematic':'nominal'}].stack('process'),
        data=None if blind else data,
        syst=pred.stack('process'),
        colors = color_cycle
    )
    
    ymax = np.max([10000]+[c.get_height() for c in ax.containers[0] if ~np.isnan(c.get_height())])
    ymin = np.min([0.001]+[c.get_height() for c in ax.containers[0] if ~np.isnan(c.get_height())])
    
    ax.set_ylim(0.001, 1000*ymax)
    
    try:
        sig_ewk = _plot_channel[{'systematic':'nominal'}].project('process', variable)[hist.loc('VBSZZ2l2nu'),:]   
        sig_qcd = _plot_channel[{'systematic':'nominal'}].project('process', variable)[hist.loc('ZZ2l2nu'),:]   
        sig_ewk.plot(ax=ax, histtype='step', color='red')
        sig_qcd.plot(ax=ax, histtype='step', color='purple')
    except:
        pass
    bx.set_ylim([0.1, 1.9])
    if len(xlim) > 0:
        bx.set_xlim(xlim)
        
    ax.set_title(f"channel {channel}: {era}")
    ax.set_yscale('log')
    
    plt.savefig(f'plot-{channel}-{variable}-{era}.pdf')
    plt.savefig(f'plot-{channel}-{variable}-{era}.png')
    plt.clf() 
    
    if checksyst:
        pred = _plot_channel.project('process','systematic', variable)[:hist.loc('data'),:,:]
        data = _plot_channel[{'systematic':'nominal'}].project('process',variable)[hist.loc('data'),:] 
        plotter.check_systematic(
            pred[{'systematic':'nominal'}].stack('process'),
            syst=pred.stack('process'),
            plot_file_name=f'check-sys-{channel}-{era}', 
            xrange=xlim
        )
        plt.clf()
    return _plot_channel, datasets


config_2016APV = dctools.read_config("config/input_UL_2016APV-amalfi.yaml")
config_2016    = dctools.read_config("config/input_UL_2016-amalfi.yaml")
config_2017    = dctools.read_config("config/input_UL_2017-amalfi.yaml")
config_2018    = dctools.read_config("config/input_UL_2018-amalfi.yaml")


for channel in config_2018.plotting:
    ch_cfg = config_2018.plotting[channel]
    # if channel not in ['vbs-SR', 'vbs-TT', 'vbs-DY', 'vbs-EM', 'vbs-3L']: continue
    for vname in ch_cfg:
        # if 'met_pt' not in vname: continue
        v_cfg = ch_cfg[vname]
        plotting(
            config_2018, vname, channel, 
            rebin=v_cfg.rebin, 
            xlim=v_cfg.range, 
            blind=v_cfg.blind,
            era="2018"
        )
        plotting(
            config_2017, vname, channel, 
            rebin=v_cfg.rebin, 
            xlim=v_cfg.range, 
            blind=v_cfg.blind,
            era="2017"
        )
        plotting(
            config_2016, vname, channel, 
            rebin=v_cfg.rebin, 
            xlim=v_cfg.range, 
            blind=v_cfg.blind,
            era="2016"
        )
        plotting(
            config_2016APV, vname, channel, 
            rebin=v_cfg.rebin, 
            xlim=v_cfg.range, 
            blind=v_cfg.blind,
            era="2016APV"
        )
