from __future__ import division

import numpy as np
import os
import uproot
import boost_histogram as bh
#import plot
import hist
import yaml
import json
import gzip
import pickle
from typing import Any, Set, List, Dict, Tuple, IO

__all__ = ['datacard', 'datagroup', "plot"]

class config_input:
    def __init__(self, cfg:Dict):
        self._cfg = cfg 
    
    def __getitem__(self, key:str)->Any:
        v = self._cfg[key]
        if isinstance(v, dict):
            return config_input(v)
    
    def __setitem__(self, key:str, value:Any)->None:
        self._cfg[key] = value

    def __getattr__(self, k:str) -> Any:
        try:
            v = self._cfg[k]
            if isinstance(v, dict):
                return config_input(v)
            return v
        except AttributeError:
            pass
            
    def __iter__(self):
        return iter(self._cfg)
    
class config_loader(yaml.SafeLoader):
    """YAML Loader with `!include` constructor."""
    def __init__(self, stream: IO) -> None:
        """Initialise Loader."""
        try:
            self._root = os.path.split(stream.name)[0]
        except AttributeError:
            self._root = os.path.curdir
        super().__init__(stream)

def construct_include(loader: config_loader, node: yaml.Node) -> Any:
    """Include file referenced at node."""
    filename = os.path.abspath(
        os.path.join(loader._root, loader.construct_scalar(node))
    )
    extension = os.path.splitext(filename)[1].lstrip('.')

    with open(filename, 'r') as f:
        if extension in ('yaml', 'yml'):
            return yaml.load(f, config_loader)
        elif extension in ('json', ):
            return json.load(f)
        else:
            return ''.join(f.readlines())

yaml.add_constructor('!include', construct_include, config_loader)

def read_config(file: str):
    with open(file) as f:
        try:
            config = config_input(
                yaml.load(f.read(), config_loader)
            )
            boosthist:Dict = {}
            for fname in config.boosthist:
                if '.gz' in fname:
                    with gzip.open(fname, "rb") as fn_:
                        boosthist.update(pickle.load(fn_))
                else:
                    with open(fname, 'rb') as fn_:
                        boosthist.update(pickle.load(fn_))
            config.boosthist = boosthist 
            return config
        except yaml.YAMLError as exc:
            print (exc)

class datagroup:
    def __init__(self, histograms, observable:str="MT", name:str="DY",
                 channel:str="catSR_VBS", ptype:str="background", 
                 luminosity:float=1.0, rebin:int=1, 
                 xsections:Dict={}, binrange:List=[]):

        self.histograms = histograms
        self.name  = name
        self.ptype = ptype
        self.lumi  = luminosity
        self.xsec  = xsections
        self.outfile: str = ""
        self.channel = channel
        self.nominal: Dict = {}
        self.systvar = Set
        self.rebin = rebin
        self.observable = observable
        # droping bins the same way as droping elements in numpy arrays a[1:3]
        self.binrange = binrange

        self.stacked:hist.Hist = hist.Hist() 
        if isinstance(list(self.histograms.values())[0]["hist"], dict):
            self.histograms = {
                    k: {
                        "hist": v["hist"][self.observable], 
                        "sumw":v["sumw"]
                    } for k, v in self.histograms.items()
            }

        for proc, _hist in self.histograms.items():
            # skip empty catgeories
            if self.channel not in _hist['hist'].axes['channel']:
                #print(f'[WARNING] : {self.name}: {self.observable}: {self.channel} not present in axes. available channels:')
                #print(list(_hist['hist'].axes['channel']))
                continue
            
            bh_hist:hist.Hist = _hist['hist'][{
                "channel" : self.channel,
                self.observable : hist.rebin(self.rebin)
            }]

            _scale = 1 
            if ptype.lower() != "data": 
                _scale = self.xs_scale(
                    sumw=_hist['sumw'], 
                    proc=proc
                )
                bh_hist = bh_hist * _scale

            # To use more elegant slicing switch to Hist
            # bh_hist = hist.Hist(bh_hist)
            
                        
            # Select one channel
            # bh_hist = bh_hist[{
            #     "channel" : self.channel,
            #     self.observable : hist.rebin(self.rebin)
            # }]
            
            if self.stacked.ndim:
                self.stacked += bh_hist
            else:
                self.stacked = bh_hist
            
    def merge_categories(self):
        pass


    def get(self, systvar) -> hist.Hist:
        shapeUp, shapeDown = None, None
        if "nominal" in systvar:
            #print("get() : ", type(self.stacked))
            return self.stacked[{'systematic': systvar}].project(self.observable)
        else:
            try:
                shapeUp = self.stacked[
                    {'systematic': systvar + 'Up'}
                ].project(self.observable)
                shapeDown = self.stacked[
                    {'systematic': systvar + 'Down'}
                ].project(self.observable)
                return (shapeUp, shapeDown)
            except ValueError:
                print(f'{systvar} is not present in the boost histogram')
                return hist.Hist()
  
    def to_boost(self) -> hist.Hist:
        return self.stacked

    def xs_scale(self, sumw, proc):
        xsec = 1.0
        if self.xsec is not None:
            xsec  = self.xsec[proc].xsec
            xsec *= self.xsec[proc].kr
            xsec *= self.xsec[proc].br
        else:
            print("[WARNING] cross-section file is empty ... ")
            
        # to get to femtobarn
        xsec *= 1000.0 
        assert xsec > 0, f"{proc} has a null cross section!"
        assert sumw > 0, f"{proc} sum of weights is null!"
        scale = 1.0
        scale = xsec * self.lumi/sumw
        return scale


class datacard:
    def __init__(self, name, channel="ch1"):
        self.dc_file = []
        self.name = []
        self.nsignal = 1
        self.channel = channel
        self.dc_file.append("imax * number of categories")
        self.dc_file.append("jmax * number of samples minus one")
        self.dc_file.append("kmax * number of nuisance parameters")
        self.dc_file.append("-" * 30)

        self.shapes = []
        self.observation = []
        self.rates = []
        self.nuisances = {}
        self.extras = set()
        self.dc_name = "cards-{}/shapes-{}.dat".format(name, channel)
        
        if not os.path.isdir(os.path.dirname(self.dc_name)):
            os.mkdir(os.path.dirname(self.dc_name))

        self.shape_file = uproot.recreate(
            "cards-{}/shapes-{}.root".format(name, channel)
        )

    def shapes_headers(self):
        filename = self.dc_name.replace("dat", "root")
        lines = "shapes * * {file:<20} $PROCESS $PROCESS_$SYSTEMATIC"
        lines = lines.format(file=os.path.basename(filename))
        self.dc_file.append(lines)

    def add_observation(self, shape):
        value = shape.sum().value
        self.dc_file.append("bin          {0:>10}".format(self.channel))
        self.dc_file.append("observation  {0:>10}".format(value))
        self.shape_file["data_obs"] = shape

    def add_nuisance(self, process, name, value):
        if name not in self.nuisances:
            self.nuisances[name] = {}
        self.nuisances[name][process] = value

    def add_log_normal(self, process, name, value): 
        nuisance = "{:<32} lnN".format(name)
        if name not in self.nuisances:
            self.nuisances[nuisance] = {}
        self.nuisances[nuisance][process] = value

    def add_nominal(self, process, shape, type):
        value = shape.sum().value
        self.rates.append((process, value, type))
        self.shape_file[process] = shape
        self.nominal_hist = shape

    def add_qcd_scales(self, process, cardname, qcd_scales):
        nuisance = "{:<30} shape".format(cardname)
        if isinstance(qcd_scales, list):
            shapes = []
            for sh in qcd_scales:
                uncert_up = np.abs(self.nominal_hist.values(0) - sh[0].values(0))
                uncert_dw = np.abs(self.nominal_hist.values(0) - sh[1].values(0))

                var_up = np.divide(
                    uncert_up, self.nominal_hist.values(0),
                    out=np.zeros_like(uncert_up),
                    where=self.nominal_hist.values(0) != 0
                )
                var_dw = np.divide(
                    uncert_dw, self.nominal_hist.values(0),
                    out=np.zeros_like(uncert_up),
                    where=self.nominal_hist.values(0) != 0
                )
                uncert_up[var_up >= 0.95] = 0
                uncert_dw[var_dw >= 0.95] = 0

                uncert = np.maximum(uncert_up, uncert_dw)

                # uncert_r = np.divide(
                #     uncert, self.nominal_hist.values(0),
                #     out=np.zeros_like(uncert)*-1,
                #     where=self.nominal_hist.values(0) != 0
                # )
                shapes.append(uncert)
            shapes = np.array(shapes)
            uncert = shapes.max(axis=0)
            
            h_uncert_up = bh.Histogram(
              bh.axis.Variable(self.nominal_hist.axes[0].edges),
            ).fill(
              self.nominal_hist.axes[0].centers,
              weight=self.nominal_hist.values(0) + uncert
            )
            
            h_uncert_dw = bh.Histogram(
              bh.axis.Variable(self.nominal_hist.axes[0].edges),
            ).fill(
              self.nominal_hist.axes[0].centers,
              weight=self.nominal_hist.values(0) - uncert
            )

            shape = (h_uncert_dw,h_uncert_up)
            self.add_nuisance(process, nuisance, 1.0)
            self.shape_file[process + "_" + cardname + "Up"] = shape[0]
            self.shape_file[process + "_" + cardname + "Down"] = shape[1]
        else:
            raise ValueError(
                "add_qcd_scales: the qcd_scales should be a list!")

    def add_shape_nuisance(self, process, cardname, shape, symmetrise=False):
        nuisance = "{:<30} shape".format(cardname)
        # print("shape[0] : ", shape[0].values(0))
        # print("shape[1] : ", shape[1].values(0)) 
        if shape[0] is not None and (
            (shape[0].values(0)[shape[0].values(0) >= 0].shape[0]) and
            (shape[1].values(0)[shape[1].values(0) >= 0].shape[0])
        ):
            if symmetrise:
                uncert = np.maximum(np.abs(self.nominal_hist.values(0) - shape[0].values(0)),
                                    np.abs(self.nominal_hist.values(0) - shape[1].values(0)))
                
                h_uncert_up = bh.Histogram(
                    bh.axis.Variable(self.nominal_hist.axes[0].edges),
                ).fill(
                  self.nominal_hist.axes[0].centers,
                  weight=self.nominal_hist.values(0) + uncert
                )
                h_uncert_dw = bh.Histogram(
                    bh.axis.Variable(self.nominal_hist.axes[0].edges),
                ).fill(
                  self.nominal_hist.axes[0].centers,
                  weight=self.nominal_hist.values(0) - uncert
                )
                h_uncert_up.name = self.nominal_hist.name
                h_uncert_up.axes[0].name = self.nominal_hist.name
                h_uncert_dw.name = self.nominal_hist.name
                h_uncert_dw.axes[0].name = self.nominal_hist.name

                shape = (h_uncert_dw, h_uncert_up)
            self.add_nuisance(process, nuisance, 1.0)
            #print('-- add shape : ',process, cardname, shape[0].name, shape[1].name)
            self.shape_file[process + "_" + cardname + "Up"] = shape[0]
            self.shape_file[process + "_" + cardname + "Down"] = shape[1]
            
    def add_rate_param(self, name, channel, process, vmin=0.1, vmax=10):
        # name rateParam bin process initial_value [min,max]
        template = "{name} rateParam {channel} {process} 1 [{vmin},{vmax}]"
        template = template.format(
            name=name,
            channel=channel,
            process=process,
            vmin=vmin,
            vmax=vmax
        )
        self.extras.add(template)

    def add_auto_stat(self):
        self.extras.add(
            "{} autoMCStats 0 0 1".format(self.channel)
        )

    def dump(self):
        # adding shapes
        for line in self.shapes:
            self.dc_file.append(line)
        self.dc_file.append("-"*30)
        # adding observation
        for line in self.observation:
            self.dc_file.append(line)
        self.dc_file.append("-"*30)
        # bin lines
        bins_line = "{0:<36}".format("bin")
        proc_line = "{0:<36}".format("process")
        indx_line = "{0:<36}".format("process")
        rate_line = "{0:<36}".format("rate")

        i_signal = 0
        i_backgr = 1 
        for tup in self.rates:
            bins_line += "{0:>15}".format(self.channel)
            proc_line += "{0:>15}".format(tup[0])
            if 'signal' in tup[2]:
                indx_line += "{0:>15}".format(i_signal)
            else:
                indx_line += "{0:>15}".format(i_backgr)
            rate_line += "{0:>15}".format("%.3f" % tup[1])
            if 'signal' in tup[2]:
                i_signal -= 1
            else:
                i_backgr += 1

        self.dc_file.append(bins_line)
        self.dc_file.append(proc_line)
        self.dc_file.append(indx_line)
        self.dc_file.append(rate_line)
        self.dc_file.append("-"*30)
        for nuisance in sorted(self.nuisances.keys()):
          # print(" source --> ", nuisance)
          scale = self.nuisances[nuisance]
          line_ = "{0:<10}".format(nuisance)
          for process, _, _ in self.rates:
              if process in scale:
                  line_ += "{0:>15}".format("%.3f" % scale[process])
              else:
                  line_ += "{0:>15}".format("-")
          self.dc_file.append(line_)
        self.dc_file += self.extras
        with open(self.dc_name, "w") as fout:
            fout.write("\n".join(self.dc_file))
