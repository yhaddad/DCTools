from __future__ import division

import numpy as np
import uproot
import os
import re
import boost_histogram as bh

__all__ = ['datacard', 'datagroup', "plot"]


class datagroup:
    def __init__(self, files, observable="measMET", name="DY",
                 channel="", kfactor=1.0, ptype="background",
                 luminosity=1.0, rebin=1, normalise=True,
                 xsections=None, mergecat=True, binrange=None):
        self._files = files
        self.name = name
        self.ptype = ptype
        self.lumi = luminosity
        self.xsec = xsections
        self.outfile = None
        self.channel = channel
        self.nominal = {}
        self.systvar = set()
        self.rebin = rebin

        # droping bins the same way as droping elements in numpy arrays a[1:3]
        self.binrange = binrange

        for fn in self._files:
            _file = uproot.open(fn)
            if not _file:
              raise ValueError("%s is not a valid rootfile" % fn)

            histograms = None
            if isinstance(channel, str):
                histograms = _file.items(
                  filter_classname="TH1*", 
                  filter_name='*' + observable + "*" + channel + "*"
                )
                histograms.sort(reverse=True)
                mergecat = False
            else:
                raise ValueError("%s DCTools not not accept yet list of channels" % self.name)
            
            # this is temporary
            histograms = list(filter(lambda hh: '_flat' not in hh[0], histograms))


            if len(histograms) == 0:
              raise ValueError(f"ERROR: there is no histogram found in {fn}")
            else:
              _proc = re.search(f"{observable}_(.+?)_{channel}", histograms[0][0]).group(1)

            _scale = 1
            if ptype.lower() != "data":
                _scale = self.xs_scale(ufile=_file, proc=_proc)
                _scale *= kfactor

            for name, roothist in histograms:
              name = name.replace(_proc, self.name)
              name = name.replace(";1", "")
              
              print("before:", name)
              if ptype.lower() == "signal":
                  name = name.replace(self.name, "signal")
              if "catSignal-0jet" in name:
                  name = name.replace("catSignal-0jet", "cat0Jet")
              if "catSignal-1jet" in name:
                  name = name.replace("catSignal-1jet", "cat1Jet")
              
              print("name : ", name)
              #roothist = self.check_shape(roothist)
              ph_hist = roothist.to_boost() * _scale

              ph_hist.name = name
              ph_hist.axes[0].name = observable
              ph_hist.title = name
              
              # rebin / re-range
              if not isinstance(self.binrange, list):
                  self.binrange = [
                      ph_hist.axes[0].edges[ 0], 
                      ph_hist.axes[0].edges[-1]]

              if isinstance(self.binrange, list) or self.rebin >= 1:
                  ph_hist = ph_hist[
                      bh.loc(self.binrange[0]):bh.loc(self.binrange[1]):bh.rebin(self.rebin)
                  ]

              if name in self.nominal.keys():
                self.nominal[name] = self.nominal[name] + ph_hist
              else:
                self.nominal[name] = ph_hist

              try:
                self.systvar.add(re.search("sys_[\w.]+", name).group())
              except:
                pass

        if mergecat:
          # merging the nominal
          self.merged = {}
          for syst in self.systvar:
            m_hist = self.merge_cat(self.nominal, lambda elem: syst in elem[0])
            self.merged[m_hist[0]] = m_hist
          m_hist = self.merge_cat(self.nominal, lambda elem: "sys" not in elem[0])
          self.merged[m_hist[0]] = m_hist
        else:
          self.merged = {i: (i, c) for i, c in self.nominal.items()}

    def check_shape(self, histogram):
        for ibin in range(histogram.numbins+1):
            if histogram[ibin] < 0:
                histogram[ibin] = 0
        return histogram

    def merge_cat(self, hitograms, callback):
        filtredhist = dict()
        for (key, value) in hitograms.items():
            if callback((key, value)):
                filtredhist[key] = value
        merged_hist = []
        merged_bins = []
        merged_cent = []
        first = True
        # return filtredhist
        iteration = sorted(
            filtredhist.items(),
            key=lambda pair: self.channel.index(pair[0].split("_")[2])
        )
        print("how many histos : ", iteration)
        for name, h in iteration:

            if first:
                merged_bins = h.numpy_bins
                merged_cent = h.bin_centers
                merged_hist = h.frequencies
                merged_var = h.errors2
                first = False
            else:
                new_bins = h.numpy_bins
                new_bin_cent = h.bin_centers

                if merged_bins[-1] == new_bins[-1]:
                    new_bins = new_bins + merged_bins[-1] + 10
                else:
                    new_bins = new_bins + merged_bins[-1]

                merged_bins = np.concatenate([merged_bins, new_bins])
                merged_cent = np.array(
                    [0.5*(merged_bins[i+1] + merged_bins[i]) for i in range(merged_bins.shape[0]-1)])
                new_frequencies = h.frequencies
                new_frequencies = [0.0, *new_frequencies]
                merged_hist = np.concatenate([merged_hist, new_frequencies])
                new_error = h.errors2
                new_error = [0.0, *new_error]
                merged_var = np.concatenate([merged_var, new_error])

        cat = re.search('cat(.*)', name).group().split("_")[0]
        print("binning : ", merged_bins)
        print("centers : ", merged_cent)
        print("histogr : ", merged_hist)
        print("var     : ", merged_var)
        physt.binnings.NumpyBinning(merged_cent)
        physt.binnings.NumpyBinning(merged_bins)
        if len(merged_hist):
            new_hist = physt.histogram1d.Histogram1D(
                bin_centers=physt.binnings.NumpyBinning(merged_cent),
                #bin_centers= merged_cent,
                frequencies=merged_hist,
                binning=physt.binnings.NumpyBinning(merged_bins),
                errors2=merged_var
            )

            return name.replace("_" + cat, ""), new_hist
        else:
            return

    def get(self, systvar, merged=True):
        shapeUp, shapeDown = None, None
        print(" SYS : ", systvar)
        for n, hist in self.merged.items():
          if "sys" not in n and systvar == "nom":
            return hist[1]
          elif systvar in n:
            if "Up" in n:
              # print("---> Up   : ", n)
              shapeUp = hist[1]
            if "Down" in n:
              # print("---> Down : ", n)
              shapeDown = hist[1]
        if shapeUp is None or shapeDown is None:
          print(f"[WARNING] {systvar} is not found in the input file, please check!")        
        return (shapeUp, shapeDown)

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
                fout[name] = uproot_methods.classes.TH1.from_numpy(hist)
            fout.close()

    def xs_scale(self, ufile, proc):
        xsec  = self.xsec[proc]["xsec"]
        xsec *= self.xsec[proc]["kr"]
        xsec *= self.xsec[proc]["br"]
        xsec *= 1000.0
        #print (proc, xsec)
        assert xsec > 0, "{} has a null cross section!".format(proc)
        scale = 1.0
        try:
            scale = xsec * self.lumi/ufile["genEventSumw"].to_boost().sum().value
        except:
            scale = xsec * self.lumi/ufile["genEventSumw"].to_boost().sum().value
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
        # print("dc_name: ", self.dc_name, " --> ", name, channel)
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

    def add_nominal(self, process, shape):
        value = shape.sum().value
        self.rates.append((process, value))
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
        bins_line = "{0:<8}".format("bin")
        proc_line = "{0:<8}".format("process")
        indx_line = "{0:<8}".format("process")
        rate_line = "{0:<8}".format("rate")
        for i, tup in enumerate(self.rates):
            bins_line += "{0:>15}".format(self.channel)
            proc_line += "{0:>15}".format(tup[0])
            indx_line += "{0:>15}".format(i - self.nsignal + 1)
            rate_line += "{0:>15}".format("%.3f" % tup[1])
        self.dc_file.append(bins_line)
        self.dc_file.append(proc_line)
        self.dc_file.append(indx_line)
        self.dc_file.append(rate_line)
        self.dc_file.append("-"*30)
        for nuisance in sorted(self.nuisances.keys()):
          print(" source --> ", nuisance)
          scale = self.nuisances[nuisance]
          line_ = "{0:<8}".format(nuisance)
          for process, _ in self.rates:
              if process in scale:
                  line_ += "{0:>15}".format("%.3f" % scale[process])
              else:
                  line_ += "{0:>15}".format("-")
          self.dc_file.append(line_)
        self.dc_file += self.extras
        with open(self.dc_name, "w") as fout:
            fout.write("\n".join(self.dc_file))
