from __future__ import division

import hist
import io
import os 
import numpy as np
import matplotlib as mlp
import matplotlib.pyplot as plt
from typing import Any, Dict, List, Optional, Tuple, Union
from hist.intervals import ratio_uncertainty
from . import datagroup
from cycler import cycler


_plot_colors_ = [
    '#99B6F7','#46B3A5','#F6D68D',
    '#2E6D92','#580C82','#8E31A1',
    '#FE4773',
]

mlp.rcParams['axes.grid'          ] =  False
mlp.rcParams['axes.labelsize'     ] =  16
mlp.rcParams['axes.linewidth'     ] =  1.4     ## edge linewidth
mlp.rcParams['legend.framealpha'  ] =  0
mlp.rcParams['legend.fancybox'    ] =  False
mlp.rcParams['legend.frameon'     ] =  False
mlp.rcParams['xtick.top'          ] =  True
mlp.rcParams['xtick.labelsize'    ] =  14
mlp.rcParams['xtick.direction'    ] =  'in'     ## direction: in, out, or inout
mlp.rcParams['xtick.minor.visible'] =  True   ## visibility of minor ticks on x-axis
mlp.rcParams['xtick.major.size'   ] =  4.5    ## major tick size in points
mlp.rcParams['xtick.minor.size'   ] =  3      ## minor tick size in points
mlp.rcParams['xtick.major.width'  ] =  1.0    ## major tick width in points
mlp.rcParams['xtick.minor.width'  ] =  0.8    ## minor tick width in points
mlp.rcParams['ytick.right'        ] =  True
mlp.rcParams['ytick.labelsize'    ] =  14
mlp.rcParams['ytick.direction'    ] =  'in'     ## direction: in, out, or inout
mlp.rcParams['ytick.minor.visible'] =  True   ## visibility of minor ticks on x-axis
mlp.rcParams['ytick.major.size'   ] =  4.5    ## major tick size in points
mlp.rcParams['ytick.minor.size'   ] =  3      ## minor tick size in points
mlp.rcParams['ytick.major.width'  ] =  1.0    ## major tick width in points
mlp.rcParams['ytick.minor.width'  ] =  0.8    ## minor tick width in points
mlp.rcParams['axes.prop_cycle'] = cycler(color=_plot_colors_)

def add_process_axis(
        histograms: dict[str, datagroup], 
        axis_name: str = 'process',
        flow: bool = True ) -> hist.Hist:

    storage = None
    histos = {}
    for it, (n, p) in enumerate(histograms.items()):
        # if p.ptype != 'data':
        histos[n] = p.to_boost()
        if it == 0:
            axes = [axis for axis in p.to_boost().axes]
            storage = p.to_boost()._storage_type()
        
            
    iterator = histos.keys()
    new_axis = hist.axis.StrCategory(iterator, name=axis_name, label=axis_name)
    axes.insert(0, new_axis)
    new_hist = hist.hist.Hist(
        *axes,
        storage,
    )
    filled_keys = set()
    for key, val in histos.items():
        idx = new_axis.index(key)
        if idx in filled_keys:
            raise ValueError(
                f"Duplicate key found for Variable type: {key} -> {float(key)}"
            )
        else:
            filled_keys.add(idx)
        new_hist.view(flow=flow)[idx, ...] = val.view(flow=flow)
        
    return new_hist

def make_split(ratio: float, gap: float = 0., ptype: str ="step") -> Any:
    from matplotlib.gridspec import GridSpec
    cax = plt.gca()
    box = cax.get_position()
    xmin, ymin = box.xmin, box.ymin
    xmax, ymax = box.xmax, box.ymax

    gs = GridSpec(
        2, 1, height_ratios=[ratio, 1 - ratio],
        left=xmin, right=xmax,
        bottom=ymin, top=ymax
    )
    gs.update(hspace=gap)
    ax = plt.subplot(gs[0])
    plt.setp(ax.get_xticklabels(), visible=False)
    bx = plt.subplot(gs[1], sharex=ax)

    return ax, bx

def mcplot(
    pred: List[hist.Hist] | hist.Hist, # either a list of MC or a boost hist with sample axis
    data: List[hist.Hist] | hist.Hist = None, 
    syst: List[hist.Hist] | hist.Hist = None, 
    proc_axis_name: str = 'process', 
    syst_axis_name: str = 'systematic', 
    **kwargs) -> Any:
    # inspired from boost Hist
    ax, bx = make_split(0.7)
    
    x_vals = None
    l_edge = None
    r_edge = None
    pred_values = None
    
    if isinstance(pred, hist.Stack):
        pred_hstk = pred
        pred_ksum = sum(pred)
        pred_values = pred_ksum.values(0)
        x_vals = pred_ksum.axes.centers[0]
        l_edge = pred_ksum.axes.edges[0][0]
        r_edge = pred_ksum.axes.edges[-1][-1]
    if isinstance(pred, hist.Hist):
        pred_hstk = pred
        pred_ksum = pred
        pred_values = pred.values(0)
        x_vals = pred.axes.centers[0]
        l_edge = pred.axes.edges[0][0]
        r_edge = pred.axes.edges[-1][-1]
    if isinstance(pred, List):
        pass
        
    pred_hstk.plot(ax=ax, stack=True, histtype="fill")
    pred_stat_error = np.sqrt(pred_ksum.values(0))
    
    ax.bar( 
        x_vals, 
        height= 2*pred_stat_error,
        width=(r_edge - l_edge) / len(x_vals),
        bottom= pred_ksum.values(0) - pred_stat_error,
        fill=False,
        linewidth=0,
        edgecolor="gray",
        hatch=4 * "/",
    )
    
    bx.axhline(
        1, color="black", linestyle="dashed", linewidth=1.0
    )
    
    # MC stat error bars
    ratio = np.ones_like(pred_values)
    ratio_uncert = np.zeros_like(pred_values)
    
    bx.bar( 
        x_vals, 
        height = 2*pred_stat_error/pred_values,
        width  = (r_edge - l_edge) / len(x_vals),
        bottom = 1 - pred_stat_error/pred_values,
        color  = "red",
        alpha  = 0.4,
    )
    
    if data is not None:
        data.plot(ax=ax, color='black', histtype='errorbar')
        ratio = data.values(0)/pred_values
        ratio_uncert = ratio_uncertainty(
            num=data.values(0),
            denom=pred_values,
        )
        bx.errorbar(
            x_vals,
            ratio,
            yerr=ratio_uncert,
            color="black",
            marker="o",
            linestyle="none",
        )
        
    if syst is not None:
        syst_list = set([
            i.replace('Up','').replace('Down','') for i in syst.axes[syst_axis_name]
        ])
        syst_up = []
        syst_dw = []
        print(len(syst_list))
        for s in syst_list:
            if 'nominal'==s: continue
            if 'PDF' in s: continue
            syst_uncert_up = sum([_hs[{syst_axis_name : s + 'Up'  }] for _hs in syst]).values(0)
            syst_uncert_dw = sum([_hs[{syst_axis_name : s + 'Down'}] for _hs in syst]).values(0)
            syst_uncert_up[np.isnan(syst_uncert_up)] = 0
            syst_uncert_dw[np.isnan(syst_uncert_dw)] = 0
            syst_up.append((pred_values-syst_uncert_up))
            syst_dw.append((pred_values-syst_uncert_dw))
            
        syst_up = np.array(syst_up)
        syst_dw = np.array(syst_dw)
        
        syst_uncert_up = np.sqrt(np.sum(syst_up**2, axis=0) + (pred_stat_error/2)**2) 
        syst_uncert_dw = np.sqrt(np.sum(syst_dw**2, axis=0) + (pred_stat_error/2)**2)
        
        bx.bar( 
            x_vals, 
            height = (syst_uncert_up + syst_uncert_dw)/pred_values,
            width  = (r_edge - l_edge) / len(x_vals),
            bottom = 1 - syst_uncert_dw/pred_values,
            color  = "blue",
            alpha  = 0.2,
            zorder = 0
        ) 
    
    if isinstance(pred, hist.Hist):
        print("input is a Hist")
        if proc_axis_name in pred.axes.name:
            pred.stack(proc_axis_name).plot(
                ax=ax, stack=True, histtype="fill"
            )
    if (data is not None) and isinstance(pred, hist.Hist):
        data.plot(ax=ax, color='black', histtype='errorbar')
    
    ax.set_xlim(l_edge, r_edge)
    # bx.set_ylim([0,2])
    ax.legend(ncol=2, loc='upper right')
    bx.set_xlabel(pred_ksum.axes[0].label)
    bx.set_ylabel('data/mc')
    ax.set_ylabel('events')
    
    return ax, bx


def check_systematic(
    pred: List[hist.Hist] | hist.Hist | hist.Stack, # either a list of MC or a boost hist with sample axis
    syst: List[hist.Hist] | hist.Hist | hist.Stack = None, 
    syst_axis_name: str = 'systematic',
    plot_file_name: str = 'check-sys',
    output_dir: str = './systematic-check/', 
    **kwargs) -> Any:
    # inspired from boost Hist
    
    if not os.path.isdir(os.path.dirname(output_dir)):
        os.mkdir(os.path.dirname(output_dir))

    if isinstance(pred, hist.Stack) or isinstance(pred, List):
        pred = sum(pred)
        
    pred_values = pred.values(0)   
    x_vals = pred.axes.centers[0]
    l_edge = pred.axes.edges[0][0]
    r_edge = pred.axes.edges[-1][-1]
    
    pred_stat_error = np.sqrt(pred.values(0))
        
    if syst is not None:
        syst_list = set([
            i.replace('Up','').replace('Down','') for i in syst.axes[syst_axis_name]
        ])
        print(len(syst_list))
        for s in syst_list:
            if 'nominal'==s: continue
            # if 'PDF'==s: continue
            syst_uncert_up = sum([_hs[{syst_axis_name : s + 'Up'  }] for _hs in syst]).values(0)
            syst_uncert_dw = sum([_hs[{syst_axis_name : s + 'Down'}] for _hs in syst]).values(0)
            syst_uncert_up[np.isnan(syst_uncert_up)] = 0
            syst_uncert_dw[np.isnan(syst_uncert_dw)] = 0
            
            # drawing the plots
            fig = plt.figure(figsize=(6,7))
            ax, bx = make_split(0.7)
            
            ax.set_title(f'{plot_file_name} : {s}')
            pred.plot(ax=ax, color='black', histtype='step', label='nominal')
            ax.hist(
                x_vals, bins=pred.axes[0].edges,
                weights= syst_uncert_up, lw=1.5,
                color='red', histtype='step', 
                label='Up'
            )
            ax.hist(
                x_vals, bins=pred.axes[0].edges,
                weights= syst_uncert_dw, lw=1.5,
                color='blue', histtype='step', 
                label='Down'
            )
            
            ax.bar( 
                x_vals, 
                height= 2*pred_stat_error,
                width=(r_edge - l_edge) / len(x_vals),
                bottom= pred.values(0) - pred_stat_error,
                fill=False,
                linewidth=0,
                edgecolor="gray",
                hatch=4 * "/",
            )
            bx.axhline(
                1, color="black", linestyle="dashed", linewidth=1.0
            )
            bx.bar( 
                x_vals, 
                height = 2*pred_stat_error/pred_values,
                width  = (r_edge - l_edge) / len(x_vals),
                bottom = 1 - pred_stat_error/pred_values,
                color  = "grey",
                alpha  = 0.4,
            )
            
            bx.hist(
                x_vals, bins=pred.axes[0].edges,
                weights= syst_uncert_up/pred_values, lw=1.5,
                color='red', histtype='step', 
                label='Up'
            )
            bx.hist(
                x_vals, bins=pred.axes[0].edges,
                weights= syst_uncert_dw/pred_values, lw=1.5,
                color='blue', histtype='step', 
                label='Down'
            )
            
            ax.set_xlim(l_edge, r_edge)
            bx.set_ylim([0.4,1.6])
            ax.legend(ncol=2, loc='upper right')
            bx.set_xlabel(pred.axes[0].label)
            bx.set_ylabel('data/mc')
            ax.set_ylabel('events')
            ax.set_yscale('log')
            
            
            fig.savefig(f'{output_dir}/{plot_file_name}-{pred.axes[0].name}-{s}.pdf')