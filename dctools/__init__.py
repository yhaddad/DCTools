from __future__ import division

import numpy as np
import uproot
import os
import re
import boost_histogram as bh
import hist

__all__ = ['datacard', 'datagroup', "plot"]


class datagroup:
    def __init__(self, histograms, observable="MT", name="DY",
                 channel="catSR_VBS", ptype="background",
                 luminosity=1.0, rebin=1, normalise=True,
                 xsections=None, mergecat=True, binrange=None):
        self.histograms = histograms
        self.name  = name
        self.ptype = ptype
        self.lumi  = luminosity
        self.xsec  = xsections
        self.outfile = None
        self.channel = channel
        self.nominal = {}
        self.systvar = set()
        self.rebin = rebin
        self.observable = observable
        # droping bins the same way as droping elements in numpy arrays a[1:3]
        self.binrange = binrange

        self.stacked = None 
        for proc, _hist in self.histograms.items():    
            bh_hist = _hist['hist']
            _scale = 1 
            if ptype.lower() != "data": 
                _scale = self.xs_scale(
                    sumw=_hist['sumw'], 
                    proc=proc
                )
                bh_hist = bh_hist * _scale

            # To use more elegant slicing switch to Hist
            bh_hist = hist.Hist(bh_hist)
            
            print(proc, ": ", _hist['sumw'], _scale)
            # skip empty catgeories
            if self.channel not in bh_hist.axes['channel']:
                continue

            # Select one channel
            bh_hist = bh_hist[{
                "channel" : self.channel,
            }]
            
            if self.stacked is None:
                self.stacked = bh_hist
            else:
                self.stacked += bh_hist
            

    def get(self, systvar, merged=True):
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
                
    def save(self, filename=None, working_dir="fitroom", force=True):
        if not filename:
            filename = "histograms-" + self.name + ".root"
            if "signal" in self.ptype:
                filename = filename.replace(self.name, "signal")
                self.name = self.name.replace(self.name, "signal")
        self.outfile = working_dir + "/" + filename
        if os.path.isdir(self.outfile) or force:
            fout = uproot.recreate(self.outfile, compression=uproot.ZLIB(4))
            for name, hist in self.merged.items():
                name = name.replace("_sys", "")
                if "data" in name:
                    name = name.replace("data", "data_obs")
                fout[name] = hist
            fout.close()

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
        assert xsec > 0, "{} has a null cross section!".format(proc)
        assert sumw > 0, "{} sum of weights is null!".format(proc)
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

    def add_nominal(self, process, shape, type):
        value = shape.sum().value
        self.rates.append((process, value, type))
        self.shape_file[process] = shape
        self.nominal_hist = shape

    def add_qcd_scales(self, process, cardname, qcd_scales):
        nuisance = "{:<20} shape".format(cardname)
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

                uncert_r = np.divide(
                    uncert, self.nominal_hist.values(0),
                    out=np.zeros_like(uncert)*-1,
                    where=self.nominal_hist.values(0) != 0
                )
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
        nuisance = "{:<20} shape".format(cardname)
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
        bins_line = "{0:<10}".format("bin")
        proc_line = "{0:<10}".format("process")
        indx_line = "{0:<10}".format("process")
        rate_line = "{0:<10}".format("rate")

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
