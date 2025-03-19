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
import traceback
from copy import deepcopy
from scipy import interpolate
from typing import Any, Set, List, Dict, Tuple, IO

__all__ = ['datacard', 'datagroup', "plot"]

class config_input:
    def __init__(self, cfg:Dict):
        self._cfg = cfg 
    
    def __getitem__(self, key:str)->Any:
        try:
            v = self._cfg[key]
            if isinstance(v, dict):
                return config_input(v)
        except AttributeError:
            return None
            
    def __setitem__(self, key:str, value:Any)->None:
        self._cfg[key] = value

    def __getattr__(self, k:str) -> Any:
        try:
            v = self._cfg[k]
            if isinstance(v, dict):
                return config_input(v)
            return v
        except AttributeError:
            return None
            
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

def combine_adapter(uprootfile,
                    empty_templates: Dict[str, hist.hist.Hist] | None,
                    combine_fit: str = 'fit_b',
                    group: str = 'DY',
                    channels: List[str] = ['cat3L16', 'catEM16', 'catSR16'],
                    name: str = 'dilep_mt',
                    label: str = '$M_{T}^{\\ell\\ell}$ (GeV)',
                    PFSFW: bool = False
                   ):
    """
    This function's purpose is to load root histograms from a combine fit file
    and build multi-dimensional boost-histograms (hist) from them in the style of the standard SMQawa outputs
    """
    channelhistos = {}
    if empty_templates is None:
        empty_templates = combine_empty_histos(uprootfile,
                                               combine_fit=combine_fit,
                                               channels=channels,
                                               name=name,
                                               label=label,
                                              )
    for channel in channels:
        filter_group = group
        if PFSFW:
            if group == "data":
                filter_group = "data_obs"
            elif group == "total":
                filter_group = "TotalProcs"
            elif group == "total_signal":
                filter_group = "TotalSig"
            elif group == "total_background":
                filter_group = "TotalBkg"
            filter = f'{channel}_{"prefit" if combine_fit == "prefit" else "postfit"}/{filter_group}'
        else:
            filter = f'shapes_{combine_fit}/{channel}/{filter_group}'
        subkeys = uprootfile.keys(filter_name=filter)
        if len(subkeys) == 1:
            subkey = subkeys[0]
            if PFSFW:
                channel_rawtype, rawgroup = subkey.split("/")
                channel, rawtype = channel_rawtype.rsplit("_", maxsplit=1)
            else:
                rawtype, channel, rawgroup = subkey.split("/")
            type = rawtype.replace('shapes_', '')
            derived_group = rawgroup.split(";")[0]
        elif len(subkeys) > 1:
            raise KeyError(f'Too many keys found for filter={filter}: subkeys={subkeys}')
        else:
            # we'll insert an empty template histogram in this case
            subkey = None
        try:
            emptyhisto = deepcopy(empty_templates[channel])
            if subkey is None:
                basehisto = update_axes_meta(emptyhisto, args={'xaxis': {'name': name, 'label': label}})
                basehistos = {'nominal': basehisto, 'statErrorUp': basehisto, 'statErrorDown': basehisto}
            else:
                roothisto = uprootfile[subkey]
                if isinstance(roothisto, uproot.models.TGraph.Model_TGraphAsymmErrors_v3):
                    x_values, ycentral = roothisto.values()
                    ylow = roothisto.errors('low')[1]
                    yhigh = roothisto.errors('high')[1]
                    basehisto = update_axes_meta(emptyhisto,  args={'xaxis': {'name': name, 'label': label}})
                    basehistoup, basehistodown = deepcopy(basehisto),  deepcopy(basehisto)
                    basehisto[:] = np.stack([ycentral, np.zeros_like(ycentral)], axis=1)
                    basehistoup[:] = np.stack([ycentral + yhigh, np.zeros_like(ycentral)], axis=1)
                    basehistodown[:] = np.stack([ycentral - ylow, np.zeros_like(ycentral)], axis=1)
                    basehistos = {'nominal': basehisto, 'statErrorUp': basehistoup, 'statErrorDown': basehistodown}
                    #basehisto[:] = ycentral
                else:
                    rawhisto = roothisto.to_hist()
                    try:
                        tmp = list(fill_with_interpolation_1d(rawhisto.view()))
                        rawhisto[:] = np.stack(tmp, axis=1)
                    except:
                        print(f"combine_adapter failed fill_with_interpolation_1d for group={group} channel={channel} combine_fit={combine_fit}")
                    finally:
                        pass
                    basehisto = update_axes_meta(rawhisto,  args={'xaxis': {'name': name, 'label': label}})
                    basehistos = {'nominal': basehisto, 'statErrorUp': basehisto, 'statErrorDown': basehisto}
            systhisto = dict_to_hist_axis(basehistos, axis_name='systematic', axis_label=None, axis_type = 'StrCategory')
            channelhistos[channel] = systhisto
        except Exception as e:
            print(f"Unable to convert model group={group} channel={channel}...")
            traceback.print_exc()

    try:
        finalhisto = dict_to_hist_axis(channelhistos, axis_name='channel', axis_label=None, axis_type = 'StrCategory')
    except:
        print("channel binning incompatibility, combine_adapter returning dictionary of channel histograms")
        # Incompatible binning can prevent merging this axis, will need to be handled as a potential case
        finalhisto = channelhistos
    return finalhisto

def combine_empty_histos(uprootfile,
                         combine_fit = "prefit",
                         channels: List[str] = ['cat3L16', 'catEM16', 'catSR16'],
                         name: str = 'dilep_mt',
                         label: str = '$M_{T}^{\\ell\\ell}$ (GeV)',
                         PFSFW: bool = False,
                        ):
    """
    This function can generate empty histograms for backfilling multidimensional
    histograms when certain processes are not included in a channel, a typical
    result of having 0 events in a template and needing to disable it in the combine fit
    """
    channelhistos: Dict = {}
    channelemptyhistos: Dict = {}
    for channel in channels:
        if PFSFW:
            filter = f'{channel}_{"prefit" if combine_fit == "prefit" else "postfit"}/*'
        else:
            filter = f'shapes_{combine_fit}/{channel}/*'
        subkeys = uprootfile.keys(filter_name=filter)
        if len(subkeys) > 0:
            subkeys = [key for key in subkeys if "data" not in key]
            subkey = subkeys[0]
            if PFSFW:
                channel_rawtype, rawgroup = subkey.split("/")
                channel, rawtype = channel_rawtype.rsplit("_", maxsplit=1)
            else:
                rawtype, channel, rawgroup = subkey.split("/")
            group = rawgroup.split(";")[0]
            try:
                roothisto = uprootfile[subkey]
                rawhisto = roothisto.to_hist()
                rawhisto.reset()
                channelemptyhistos[channel] = rawhisto
                #basehisto = update_axes_meta(rawhisto,  args={'xaxis': {'name': name, 'label': label}})
                #channelemptyhistos[channel] = basehisto
            except:
                print(f"Unable to generate empty histogram for channel={channel}")
        else:
            print("Found no matching subkeys, but...", [x for x in uprootfile.keys() if channel in x ])
            print(f"Unable to generate empty histogram for channel={channel}")
            return None
    return channelemptyhistos

def read_combinehist(config):
    combinehistos:Dict = {}
    for cname in config.combinehist:
        channels = config.combinehist[cname].channels
        observable = config.combinehist[cname].observable
        label = config.combinehist[cname].label
        edges = config.combinehist[cname].edges if "edges" in config.combinehist[cname] else None
        channel_groups = config.combinehist[cname].channel_groups

        fit_file = config.combinehist[cname].fitDiagnostics
        try:
            froot = uproot.open(fit_file)
        except Exception:
            raise IOError(f"Unable to open fitDiagnostics file {fit_file}")

        if "PFSFW_fit_b" in config.combinehist[cname]:
            fit_b_file = config.combinehist[cname].PFSFW_fit_b
            try:
                fit_b_root = uproot.open(fit_b_file)
            except Exception:
                raise IOError(f"Unable to open postfit file {fit_b_file}")
        else:
            fit_b_file = None
            fit_b_root = froot

        if "PFSFW_fit_s" in config.combinehist[cname]:
            fit_s_file = config.combinehist[cname].PFSFW_fit_s
            try:
                fit_s_root = uproot.open(fit_s_file)
            except Exception:
                raise IOError(f"Unable to open postfit file {fit_s_file}")
        else:
            fit_s_file = None
            fit_s_root = froot

        try:
            if fit_s_file and fit_b_file:
                #unc_groups = ["TotalProcs", "TotalSig", "TotalBkg"]
                unc_groups = ['total', 'total_signal', 'total_background'] #'total_covar' is 2d bin-to-bin
                PFSFW = True
            elif fit_s_file or fit_b_file:
                raise NotImplementedError("Both PFSFW_fit_b and PFSFW_fit_s should be specified or neither in this implementation")
                PFSFW = None
            else:
                unc_groups = ['total', 'total_signal', 'total_background'] #'total_covar' is 2d bin-to-bin
                PFSFW = False
            for group in list(config.groups) + unc_groups:
                if group not in combinehistos:
                    combinehistos[group] = {'prefit': {},
                                            'fit_b': {},
                                            'fit_s': {},
                                            'edges': {},
                                            'channel_groups': {},
                                           }
                empty_templates = combine_empty_histos(fit_b_root,
                                                       combine_fit="prefit",
                                                       channels = channels,
                                                       name=observable,
                                                       label=label,
                                                       PFSFW=PFSFW,
                                                       )
                combinehistos[group]['prefit'].update({observable: combine_adapter(fit_b_root,
                                                                                   empty_templates=empty_templates,
                                                                                   combine_fit='prefit',
                                                                                   group=group,
                                                                                   channels=channels,
                                                                                   name=observable,
                                                                                   label=label,
                                                                                   PFSFW=PFSFW,
                                                                                 )})
                combinehistos[group]['fit_b'].update({observable: combine_adapter(fit_b_root,
                                                                                  empty_templates=empty_templates,
                                                                                  combine_fit='fit_b',
                                                                                  group=group,
                                                                                  channels=channels,
                                                                                  name=observable,
                                                                                  label=label,
                                                                                  PFSFW=PFSFW,
                                                                                 )})
                combinehistos[group]['fit_s'].update({observable: combine_adapter(fit_s_root,
                                                                                  empty_templates=empty_templates,
                                                                                  combine_fit='fit_s',
                                                                                  group=group,
                                                                                  channels=channels,
                                                                                  name=observable,
                                                                                  label=label,
                                                                                  PFSFW=PFSFW,
                                                                                 )})
                combinehistos[group]['edges'].update({observable: edges})
                combinehistos[group]['channel_groups'].update({observable: channel_groups})
        except Exception as e:
            print(f"Unable to load combinehist fitDiagnostics file {fit_file} or PostFitShapesFromWorkspace files {fit_b_file}, {fit_s_file} as declared in config.combinehist")
            traceback.print_exc()
    return combinehistos

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
            if "combinehist" in config:
                config.combinehist = read_combinehist(config)
            return config

        except yaml.YAMLError as exc:
            print (exc)

def fill_with_interpolation_1d(hview):
    '''
    interpolate to fill nan and infinite values values
    This function removes as well the negative bins 
    as this produces a bogus normalisation error in 
    cobine tool
    '''
    inds = np.arange(hview.value.shape[0])
    mask = (
        np.isfinite(hview.value) & 
        np.isfinite(hview.variance) & 
        (hview.value > 0) & 
        (np.abs(hview.value) < 1e30) 
    )
    good = np.where(mask)
    fval = interpolate.interp1d(inds[good], hview.value[good],bounds_error=False)
    fvar = interpolate.interp1d(inds[good], hview.variance[good],bounds_error=False)
    new_val = np.where(mask,hview.value   ,fval(inds))
    new_var = np.where(mask,hview.variance,fvar(inds))
    return new_val, new_var
            
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
            
            if self.stacked.ndim:
                self.stacked += bh_hist
            else:
                self.stacked = bh_hist
            
    def merge_categories(self):
        pass

    def get(self, systvar) -> hist.Hist:
        shapeUp, shapeDown = None, None
        if "nominal" in systvar:
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
    
    def get_eft(self, name) -> hist.Hist:
        try:
            return self.stacked[
                {'systematic': name + 'Up'}
            ].project(self.observable)
        except ValueError:
            print(f'{name} is not present in the boost histogram')
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
    
    def __add__(self, other)-> Any:
        new_datagroup = deepcopy(other)
        new_datagroup.stacked = self.stacked + other.stacked
        return new_datagroup


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

    def assure_positive_definit_shape(self, shape):
        if np.any(shape.values(0)<0):
            updated_value = np.where(
                shape.values(0) <= 0,  
                np.zeros_like(shape.values(0)), 
                shape.values(0)
            )
            pos_shape = hist.Hist(
                hist.axis.Variable(shape.axes[0].edges),
            ).fill(
              shape.axes[0].centers,
              weight=updated_value
            )
        else:
            pos_shape = shape
        return pos_shape

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

    def add_nominal(self, process, shape, ptype):
        if shape.sum().value <= 0:
            print("[WARNING] bogus normalisation", process, shape.sum())
            return False
        else:
            shape = self.assure_positive_definit_shape(shape)
            if hasattr(shape.sum(), 'value'):
                value = shape.sum().value
            else:
                value = shape.sum()

            self.rates.append((process, value, ptype))
            self.shape_file[process] = shape
            self.nominal_hist = shape
            return True

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
        
        if shape[0] is not None and (
            (shape[0].values(0)[shape[0].values(0) >= 0].shape[0]) and
            (shape[1].values(0)[shape[1].values(0) >= 0].shape[0])
        ):
            var_up = np.where(
                np.divide(
                    np.abs(shape[0].values(0) - self.nominal_hist.values(0)), 
                    self.nominal_hist.values(0), 
                    where=self.nominal_hist.values(0)!=0
                )>10,
                self.nominal_hist.values(0) - np.abs(shape[1].values(0) - self.nominal_hist.values(0)), 
                shape[0].values(0)
            )
            
            var_dw = np.where(
                np.divide(
                    np.abs(shape[1].values(0) - self.nominal_hist.values(0)), 
                    self.nominal_hist.values(0), 
                    where=self.nominal_hist.values(0)!=0
                )>10,
                self.nominal_hist.values(0) - np.abs(shape[0].values(0) - self.nominal_hist.values(0)), 
                shape[1].values(0)
            )
            
            # removing bogus normalisations
            var_up = np.where((var_up <= 0) | np.isinf(var_up), self.nominal_hist.values(0), var_up)
            var_dw = np.where((var_dw <= 0) | np.isinf(var_dw), self.nominal_hist.values(0), var_dw)
            
            #if np.all(np.sign(var_up-self.nominal_hist.values(0))*np.sign(var_dw-self.nominal_hist.values(0))>0):
            #    print(f"WARNING: variations {process}:{cardname} are on the same dirrection")
            #    print("nom : ", np.round(self.nominal_hist.values(0), 5))
            #    print("up  : ", np.round(var_up, 5))
            #    print("down: ", np.round(var_dw, 5))

            
            if symmetrise:
                uncert = np.maximum(
                    np.abs(self.nominal_hist.values(0) - var_up),
                    np.abs(self.nominal_hist.values(0) - var_dw)
                )
                var_up = self.nominal_hist.values(0) - uncert
                var_dw = self.nominal_hist.values(0) + uncert
                
            h_uncert_up = bh.Histogram(
                bh.axis.Variable(self.nominal_hist.axes[0].edges),
            ).fill(
              self.nominal_hist.axes[0].centers,
              weight=var_up
            )
            h_uncert_dw = bh.Histogram(
                bh.axis.Variable(self.nominal_hist.axes[0].edges),
            ).fill(
              self.nominal_hist.axes[0].centers,
              weight=var_dw
            )
            
            shape = (
                self.assure_positive_definit_shape(h_uncert_dw), 
                self.assure_positive_definit_shape(h_uncert_up)
            )

            self.add_nuisance(process, nuisance, 1.0)
            self.shape_file[process + "_" + cardname + "Up"] = shape[1]
            self.shape_file[process + "_" + cardname + "Down"] = shape[0]
            
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

            print("debug: ", indx_line, " : ", tup)

        self.dc_file.append(bins_line)
        self.dc_file.append(proc_line)
        self.dc_file.append(indx_line)
        self.dc_file.append(rate_line)
        self.dc_file.append("-"*30)
        for nuisance in sorted(self.nuisances.keys()):
            scale = self.nuisances[nuisance]
            line_ = "{0:<10}".format(nuisance)
            for process, _, _ in self.rates:
                if process in scale:
                    line_ += "{0:>15}".format("%.3f" % scale[process])
                else:
                    line_ += "{0:>15}".format("-")
            self.dc_file.append(line_)
        self.dc_file += self.extras
        # adding groups in the the datacards
        # for gname, group in self.groups.items():
        #    self.dc_file.append(f"{gname} group="+" ".join(group))

        with open(self.dc_name, "w") as fout:
            fout.write("\n".join(self.dc_file))

# borrowed from https://github.com/NJManganelli/chai/blob/main/src/chai/histtools/manipulation.py
def dict_to_hist_axis(
    histos: dict[str, hist.hist.Hist],
    axis_name: str,
    axis_label: str | None = None,
    axis_type: str = "StrCategory",
    axis_storage: str | None = None,
    axis_args: dict[str, Any] | None = None,
    axis_iter_override: Any | None = None,
) -> hist.hist.Hist:
    keys = []
    storage = None
    for it, (key, val) in enumerate(histos.items()):
        keys.append(key)
        if it == 0:
            try:
                axes = list(val.axes)
            except Exception:
                axes = []
            try:
                storage = val._storage_type()
            except Exception:
                storage = None
    if axis_storage is None:
        pass  # use storage of the first histogram type
    elif isinstance(axis_storage, str):
        try:
            storage = getattr(hist.storage, axis_storage)()
        except Exception as err:
            available_storages = get_hist_storages(string=True)
            msg = f"{axis_storage} not a valid type, choose from {available_storages}"
            raise ValueError(msg) from err
    # elif isinstance(axis_storage, get_hist_storages(string=False)):
    #     storage = axis_storage
    # else:
    #     msg = f"Unsupported storage type requested: {axis_storage}"
    #     raise ValueError(msg)

    all_args: dict[str, Any] = {
        "name": axis_name,
        "label": axis_label if axis_label else axis_name,
    }
    if axis_args:
        all_args.update(axis_args)

    flow = True
    # if "flow" in all_args:
    #     flow = all_args["flow"]

    # Determine iterable categories

    if axis_type == "Boolean":
        # Boolean(*, name: 'str' = '', label: 'str' = '', metadata: 'Any' = None, __dict__: 'dict[str, Any] | None' = None) -> 'None'
        new_axis = hist.axis.Boolean(**all_args)
        axes.insert(0, new_axis)
        h = hist.hist.Hist(
            *axes,
            storage,
        )
        for key, val in histos.items():
            if key.lower() == "true":
                idx = new_axis.index(True)
            elif key.lower() == "false":
                idx = new_axis.index(False)
            else:
                msg = f"Unsupported axis value or type for Boolean axis: {key} (type: {type(key)}"
                raise ValueError(msg)
            if val is not None:
                if len(axes) > 1:
                    h.view(flow=flow)[idx, ...] = val.view(flow=flow)
                else:
                    h.view(flow=flow)[idx] = val.view(flow=flow)
    elif axis_type == "IntCategory":
        # IntCategory(categories: 'Iterable[int]', *, name: 'str' = '', label: 'str' = '', metadata: 'Any' = None, growth: 'bool' = False, __dict__: 'dict[str, Any] | None' = None) -> 'None'
        if axis_iter_override:
            iterator = axis_iter_override
        else:
            iterator = [int(key) for key in keys]
        new_axis = hist.axis.IntCategory(iterator, **all_args)
        axes.insert(0, new_axis)
        h = hist.hist.Hist(
            *axes,
            storage,
        )
        filled_keys = set()
        for key, val in histos.items():
            idx = new_axis.index(int(key))
            if idx in filled_keys:
                msg = f"Duplicate key found for IntCategory type: {key} -> {int(key)}"
                raise ValueError(msg)
            filled_keys.add(idx)
            if val is not None:
                if len(axes) > 1:
                    h.view(flow=flow)[idx, ...] = val.view(flow=flow)
                else:
                    h.view(flow=flow)[idx] = val.view(flow=flow)
    elif axis_type == "Integer":
        # Integer(start: 'int', stop: 'int', *, name: 'str' = '', label: 'str' = '', metadata: 'Any' = None, flow: 'bool' = True, underflow: 'bool | None' = None, overflow: 'bool | None' = None, growth: 'bool' = False, circular: 'bool' = False, __dict__: 'dict[str, Any] | None' = None) -> 'None'
        if axis_iter_override:
            iterator = axis_iter_override
        else:
            iterator = [
                int(key) for key in keys if key.lower() not in ["underflow", "overflow"]
            ]
        if "start" not in all_args:
            all_args["start"] = min(iterator)
        if "stop" not in all_args:
            all_args["stop"] = max(iterator)
        new_axis = hist.axis.Integer(**all_args)
        axes.insert(0, new_axis)
        h = hist.hist.Hist(
            *axes,
            storage,
        )
        filled_keys = set()
        for key, val in histos.items():
            if key.lower() == "underflow":
                idx = new_axis.underflow
            elif key.lower() == "overflow":
                idx = new_axis.overflow
            else:
                idx = new_axis.index(int(key))
            if idx in filled_keys:
                msg = f"Duplicate key found for Integer type: {key} -> {int(key)}"
                raise ValueError(msg)
            filled_keys.add(idx)
            if val is not None:
                if len(axes) > 1:
                    h.view(flow=flow)[idx, ...] = val.view(flow=flow)
                else:
                    h.view(flow=flow)[idx] = val.view(flow=flow)
    elif axis_type == "Regular":
        # Regular(bins: 'int', start: 'float', stop: 'float', *, name: 'str' = '', label: 'str' = '', metadata: 'Any' = None, flow: 'bool' = True, underflow: 'bool | None' = None, overflow: 'bool | None' = None, growth: 'bool' = False, circular: 'bool' = False, transform: 'bha.transform.AxisTransform | None' = None, __dict__: 'dict[str, Any] | None' = None) -> 'None'
        if axis_iter_override:
            iterator = axis_iter_override
        else:
            iterator = [
                float(key)
                for key in keys
                if key.lower() not in ["underflow", "overflow"]
            ]
        if "bins" not in all_args:
            all_args["bins"] = len(iterator)
        if "start" not in all_args:
            all_args["start"] = min(iterator)
        if "stop" not in all_args:
            all_args["stop"] = max(iterator)
        new_axis = hist.axis.Regular(**all_args)
        axes.insert(0, new_axis)
        h = hist.hist.Hist(
            *axes,
            storage,
        )
        filled_keys = set()
        for key, val in histos.items():
            if key.lower() == "underflow" and flow:
                idx = 0
            elif key.lower() == "overflow" and flow:
                idx = new_axis.extent - 1
            else:
                idx = new_axis.index(float(key))

            if idx in filled_keys:
                msg = f"Duplicate key found for Integer type: {key} -> {float(key)}"
                raise ValueError(msg)
            filled_keys.add(idx)
            if val is not None:
                if len(axes) > 1:
                    h.view(flow=flow)[idx, ...] = val.view(flow=flow)
                else:
                    h.view(flow=flow)[idx] = val.view(flow=flow)
    elif axis_type == "StrCategory":
        # StrCategory(categories: 'Iterable[str]', *, name: 'str' = '', label: 'str' = '', metadata: 'Any' = None, growth: 'bool' = False, __dict__: 'dict[str, Any] | None' = None) -> 'None'
        iterator = axis_iter_override if axis_iter_override else list(keys)
        new_axis = hist.axis.StrCategory(iterator, **all_args)
        axes.insert(0, new_axis)
        h = hist.hist.Hist(
            *axes,
            storage,
        )
        filled_keys = set()
        for key, val in histos.items():
            idx = new_axis.index(key)

            if idx in filled_keys:
                msg = f"Duplicate key found for StrCategory type: {key} -> {float(key)}"
                raise ValueError(msg)
            filled_keys.add(idx)
            if val is not None:
                if len(axes) > 1:
                    h.view(flow=flow)[idx, ...] = val.view(flow=flow)
                else:
                    h.view(flow=flow)[idx] = val.view(flow=flow)
    elif axis_type == "Variable":
        # Variable(edges: 'Iterable[float]', *, name: 'str' = '', label: 'str' = '', metadata: 'Any' = None, flow: 'bool' = True, underflow: 'bool | None' = None, overflow: 'bool | None' = None, growth: 'bool' = False, circular: 'bool' = False, __dict__: 'dict[str, Any] | None' = None) -> 'None'
        if axis_iter_override:
            iterator = axis_iter_override
        else:
            iterator = sorted(
                [
                    float(key)
                    for key in keys
                    if key.lower() not in ["underflow", "overflow"]
                ]
            )
        new_axis = hist.axis.Variable(**all_args)
        axes.insert(0, new_axis)
        h = hist.hist.Hist(
            *axes,
            storage,
        )
        filled_keys = set()
        for key, val in histos.items():
            if key.lower() == "underflow" and flow:
                idx = 0
            elif key.lower() == "overflow" and flow:
                idx = new_axis.extent - 1
            else:
                idx = new_axis.index(float(key))

            if idx in filled_keys:
                msg = f"Duplicate key found for Variable type: {key} -> {float(key)}"
                raise ValueError(msg)
            filled_keys.add(idx)
            if val is not None:
                if len(axes) > 1:
                    h.view(flow=flow)[idx, ...] = val.view(flow=flow)
                else:
                    h.view(flow=flow)[idx] = val.view(flow=flow)
    else:
        msg = f"Unsupported axis_type {axis_type}"
        raise ValueError(msg)

    return h

# borrowed from https://github.com/NJManganelli/chai/blob/main/src/chai/histtools/manipulation.py
def update_axes_meta(
    histo: hist.hist.Hist,
    args: dict[str, dict[str, str]],
    verbose: bool = False,
) -> hist.hist.Hist:
    """Update a hist name or label.

    args: dictionary of old-axis name: dictionary('name': new-axis-name, 'label': new-axis-label)
    """
    old_axes = {axis.name: axis for axis in histo.axes}
    for old_axis_name, attributes in args.items():
        if old_axis_name not in old_axes:
            if verbose:
                print(  # noqa: T201
                    f"{old_axis_name} not in the axes names: {old_axes.keys()}"
                )
            continue
        to_up = old_axes[old_axis_name].__dict__
        for key, val in attributes.items():
            to_up[key] = val
    return histo
