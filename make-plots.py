import argparse
import gzip
import pickle
import matplotlib.pyplot as plt
import yaml
import io
import os
import numpy as np
import hist
from typing import Any, IO, Dict, List, Iterable
import dctools
from dctools import plot as plotter
import matplotlib.pyplot as plt
import scipy.interpolate as interp
import mplhep as hep
from scipy import stats as st
np.seterr(all='warn')
plt.ioff()

from dctools import dict_to_hist_axis
def plotting(config, variable, channel, rebin=1, xlim=[], blind=False, era="someyear", checksyst=True, combine_fit="pre-combine", combine_total_uncertainty="total_background", combine_channel_group=None) -> None:
    assert combine_fit in ["pre-combine", "prefit", "fit_b", "fit_s"]
    datasets:Dict = dict()
    color_cycle:List = []
    edges:Iterable[str] | Iterable[float] | None = None
    combine_uncertainty_histo: hist.Hist | None = None
    combine_channels: List[str] | None = None
    combine_lumi: int | None = None
    combine_era: str | None = None

    for ng, name in enumerate(config.groups):
        if combine_fit == "pre-combine":
            # handle the plotting of histograms directly from SMQawa
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
        else:
            # handle the combine prefit or postfit inputs similarly to the pre-combine path, with a channel selection ala dctools.datagroup
            if ng == 0:
                if combine_channel_group is not None:
                    combine_channels_config = config.combinehist[name]["channel_groups"][variable][combine_channel_group]
                    combine_channels = combine_channels_config.channels
                    combine_lumi = combine_channels_config.luminosity
                    combine_era = combine_channels_config.era
                else:
                    combine_channels = channel
                    combine_era = era
                combine_uncertainty_histo = config.combinehist[combine_total_uncertainty][combine_fit][variable][{"channel": combine_channels}]
                edges = config.combinehist[name]["edges"][variable]
            p = config.combinehist[name][combine_fit][variable][{"channel": combine_channels}]
            # for the 'systematic' axis and with adding/regularizing the '
            datasets[name] = p
            if config.groups[name].type == "signal":
                signal = name
            if rebin != 1:
                raise NotImplementedError("for combine prefit/fit_b/fit_s plotting the rebin functionality has not been implemented")

        if hasattr(config.groups[name], "color") and (hasattr(p, "shape") and len(p.shape)) or len(p.to_boost().shape):
            color_cycle.append(config.groups[name].color)
    
    if combine_fit == "pre-combine":
        _plot_channel = plotter.add_process_axis(datasets)
    else:
        _plot_channel = dctools.dict_to_hist_axis(datasets, axis_name='process', axis_label=None, axis_type = 'StrCategory')
        combine_uncertainty_histo = combine_uncertainty_histo.project('systematic', variable)
    pred = _plot_channel.project('process', 'systematic', variable)[:hist.loc('data'),:,:]   
    data = _plot_channel[{'systematic':'nominal'}].project('process', variable)[hist.loc('data'),:]
    

    plt.figure(figsize=(6,7))
    ax, bx = plotter.mcplot(
        pred[{'systematic':'nominal'}].stack('process'),
        data=None if blind else data,
        syst=pred.stack('process'),
        colors = color_cycle,
        combine_fit=combine_fit,
        combine_uncertainty_histo=combine_uncertainty_histo[{'systematic':'nominal'}] if combine_uncertainty_histo else None,
        combine_histo_edges=edges,
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
    ax.set_title(f"channel {combine_channel_group or channel}: {combine_era or era}")
    hep.cms.label("", ax=ax, data=not blind, lumi=combine_lumi, year=combine_era or int(era)) #add lumi=lumi, add year=int(era) with handling of APV, etc.
    ax.set_yscale('log')

    cmb_postfix = "-" + combine_fit if combine_fit in ["prefit", "fit_b", "fit_s"] else ""
    plt.savefig(f'plot-{combine_channel_group or channel}-{variable}-{combine_era or era}{cmb_postfix}.pdf')
    plt.savefig(f'plot-{combine_channel_group or channel}-{variable}-{combine_era or era}{cmb_postfix}.png')
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



#config_2016APV = dctools.read_config("config/input_UL_2016APV-amalfi.yaml")
#config_2016    = dctools.read_config("config/input_UL_2016-amalfi.yaml")
#config_2017    = dctools.read_config("config/input_UL_2017-amalfi.yaml")
#config_2018    = dctools.read_config("config/input_UL_2018-amalfi.yaml")


#for channel in config_2018.plotting:
#    ch_cfg = config_2018.plotting[channel]
#    # if channel not in ['vbs-SR', 'vbs-TT', 'vbs-DY', 'vbs-EM', 'vbs-3L']: continue
#    for vname in ch_cfg:
#        # if 'met_pt' not in vname: continue
#        v_cfg = ch_cfg[vname]
#        plotting(
#            config_2018, vname, channel,
#            rebin=v_cfg.rebin,
#            xlim=v_cfg.range,
#            blind=v_cfg.blind,
#            era="2018"
#        )
#        plotting(
#            config_2017, vname, channel,
#            rebin=v_cfg.rebin,
#            xlim=v_cfg.range,
#            blind=v_cfg.blind,
#            era="2017"
#        )
#        plotting(
#            config_2016, vname, channel,
#            rebin=v_cfg.rebin,
#            xlim=v_cfg.range,
#            blind=v_cfg.blind,
#            era="2016"
#        )
#        plotting(
#            config_2016APV, vname, channel,
#            rebin=v_cfg.rebin,
#            xlim=v_cfg.range,
#            blind=v_cfg.blind,
#            era="2016APV"
#        )
def main():
    parser = argparse.ArgumentParser(description='DCTools Plotting Tool')
    parser.add_argument("-i"  , "--input"   , type=str , default="./config/input_UL_2018_timgad-vbs.yaml")
    parser.add_argument("-y"  , "--era"     , type=str , default='2018')
    parser.add_argument("-v"  , "--variables", nargs="*", type=str)
    parser.add_argument("-c"  , "--channels" , nargs='*', type=str)
    parser.add_argument("-b"  , "--blindings" , nargs='*', type=bool, default=[False])
    parser.add_argument('--checksyst', action='store_true')
    parser.add_argument('-cf', "--combine_fit", type=str, default="pre-combine")
    parser.add_argument('-ctu', "--combine_total_uncertainty", type=str, default="total_background")
    parser.add_argument('-ccg', "--combine_channel_groups", nargs="*", type=str, default=None)
    parser.add_argument('-ccgb', "--combine_channel_group_blindings", nargs="*", type=bool, default=[False])

    options = parser.parse_args()
    config = dctools.read_config(options.input)

    if options.combine_fit in ["prefit", "fit_b", "fit_s"]:
        # for combine plotting, for the prefit, background-only fit, or signal + background fit
        do_channels = (isinstance(options.channels, list) and len(options.channels) > 0)
        do_groups = (isinstance(options.combine_channel_groups, list) and len(options.combine_channel_groups) > 0)
        at_least_one = do_channels or do_groups
        assert at_least_one, "In combine output mode, must have a channel or at least one combine_channel_group name"
        assert options.variables, "In combine output mode, must specify variables to be plotted"

        #plot individual channels
        if options.channels:
            iter_blindings = options.blindings
            if len(iter_blindings) == 1 and len(options.channels) > 1:
                iter_blindings = iter_blindings * len(options.channels)
            for channel, blind in zip(options.channels,iter_blindings):
                for vname in options.variables:
                    _ = plotting(config, vname, channel,
                                 rebin = 1,
                                 xlim = [],
                                 blind = blind,
                                 era = options.era,
                                 checksyst = False,
                                 combine_fit = options.combine_fit,
                                 combine_total_uncertainty = options.combine_total_uncertainty,
                                 combine_channel_group = None,
                                )

        #plot stacks of channels
        if options.combine_channel_groups:
            group_blindings = options.combine_channel_group_blindings
            if len(group_blindings) == 1 and len(options.combine_channel_groups) > 1:
                group_blindings = group_blindings * len(options.combine_channel_groups)
            for channel_group, group_blind in zip(options.combine_channel_groups,group_blindings):
                for vname in options.variables:
                    _ = plotting(config, vname, None,
                                 rebin = 1,
                                 xlim = [],
                                 blind = group_blind,
                                 #era = options.era, #picked up from configuration automatically
                                 checksyst = False,
                                 combine_fit = options.combine_fit,
                                 combine_total_uncertainty = options.combine_total_uncertainty,
                                 combine_channel_group = channel_group,
                                )

    elif options.combine_fit == "pre-combine":
        for channel in config.plotting:
            if options.channels and len(options.channels) > 0 and channel not in options.channels:
                continue
            ch_cfg = config.plotting[channel]
            for vname in ch_cfg:
                if options.variables and len(options.variables) > 0 and vname not in options.variables:
                    continue
                v_cfg = ch_cfg[vname]
                _ = plotting(config, vname, channel,
                             rebin = v_cfg.rebin,
                             xlim = v_cfg.range,
                             blind = v_cfg.blind,
                             era = options.era,
                             checksyst = options.checksyst,
                             combine_fit = options.combine_fit,
                            )
    else:
        raise ValueError(f"Invalid combine_fit option {options.combine_fit}, please choose from 'pre-combine' (boost) or 'prefit'/'fit_b'/'fit_s' (combine)")

if __name__ == "__main__":
    main()
