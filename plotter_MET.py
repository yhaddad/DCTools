#!/usr/bin/env python3

import ROOT
import uproot
import collections
from termcolor import colored
import math
import argparse
import yaml
import os
import numpy as np

ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.gROOT.ProcessLine(".x rootlogon.C")
ROOT.gErrorIgnoreLevel=ROOT.kError

parser = argparse.ArgumentParser("")
parser.add_argument('-era', '--era', type=str, default="2018", help="")
parser.add_argument('-cfg', '--cfg', type=str, default="./config/inputs-NanoAODv5-2018.yaml", help="")
parser.add_argument('-tag', '--tag', type=str, default="VBS")
parser.add_argument('-debug', '--debug', action='store_true')
options  = parser.parse_args()

processes = {}
with open(options.cfg, 'r') as stream:
    processes = yaml.safe_load(stream)

xsections = {}
with open("./config/xsections_{}.yaml".format(options.era), 'r') as stream:
    xsections = yaml.safe_load(stream)
genEventSumw = {}
with open("./config/genEventSumw_UL_{}.yaml".format(options.era), 'r') as stream:
    genEventSumw = yaml.safe_load(stream)

controlreg = ["catMM","catEE", "catEM", "cat3L","catWW", "DY","cat4Jet"]

error_band_color           = 138
error_band_style           = 3357
error_band_opacity         = 1

syst_error_band_color      = 139
syst_error_band_style      = 3357
syst_error_band_opacity    = 1

canvas_width               = 600
canvas_height              = 600+100
ratio_error_same           = False
ratio_syst_band_color      = 138
ratio_syst_band_style      = 1001
ratio_error_band_color     = 139
ratio_error_band_style     = 1001
ratio_error_band_opacity   = 0.7
ratio_draw_signal          = False
ratio_precision_range      = [0, 2.6]
ratio_plot_grid            = True
text_font                  = 43
text_size                  = 18

# systematics_sources = [
#     "ElectronEn",
#     # "MuonEn",
#     # "jesTotal",
#     # "jer"
# ]
systematics_sources = [
    # "puWeight", "PDF", "MuonSF", "ElecronSF", "EWK",
    # "nvtxWeight","TriggerSFWeight","btagEventWeight",
    # "QCDScale0w", "QCDScale1w", "QCDScale2w"
]

observable = {
    "signal"  : "measMET",
    "catEM"           : "measMET",
    "catSignal-0jet"  : "measMET",
    "catSignal-1jet"  : "measMET",
    "cat3L"           : "measMET",
#    "cat4L"           : "measMET",
    "catNRB"          : "measMET",
    "catTOP"          : "measMET",
    "catDY"           : "measMET",
    "cat4Jet"         : "measMET",
    "catWW"           : "measMET",
    "njet"            : "njet",
    "balance"         : "balance",
    "phizmet"         : "phizmet"
}

# observable = {
#     "catSignal-0jet"  : "MT",
#     "catEM"           : "MT",
#     "catSignal-1jet"  : "MT",
#     "cat3L"           : "MT",
#     "cat4L"           : "MT",
#     "catNRB"          : "MT",
#     "catTOP"          : "MT",
#     "catDY"           : "MT",
#     "njet"            : "njet",
#     "balance"         : "balance",
#     "phizmet"         : "phizmet"
# }

names = {
    "signal"  : "E_{T}^{miss} (GeV)",
    "catSignal-0jet"  : "E_{T}^{miss} (GeV)",
    "catSignal-1jet"  : "E_{T}^{miss} (GeV)",
    "catEM"  : "E_{T}^{miss} (GeV)",
    "cat3L"  : "emulated E_{T}^{miss} (GeV)",
#    "cat4L"  : "emulated E_{T}^{miss} (GeV)",
    "catNRB" : "E_{T}^{miss} (GeV)",
    "catTOP" : "E_{T}^{miss} (GeV)",
    "catDY"  : "E_{T}^{miss} (GeV)",
    "cat4Jet": "E_{T}^{miss} (GeV)",
#    "catDYLmet" : "E_{T}^{miss} (GeV)",
#    "catDYHmet" : "E_{T}^{miss} (GeV)",
    "catWW"  : "emulated E_{T}^{miss} (GeV)",
    "njet"   : "N_{jet}",
    "balance": "balance",
    "phizmet": "#phi(Z,E_{T}^{miss})/#pi"
}

ranges = {
    "signal"  : [50, 800],
    "catSignal-0jet"  : [50, 800],
    "catSignal-1jet"  : [50, 800],
    "catEM"  : [ 50, 600],
    "cat3L"  : [ 50, 600],
#    "cat4L"  : [ 50, 600],
    "catNRB" : [ 0, 100],
    "catTOP" : [ 0, 100],
    "catDY"  : [ 50, 200],
    "cat4Jet": [ 50, 200],
#    "catDYLmet" : [50, 200],
#    "catDYHmet" : [50, 200],
    "catWW"  : [ 0, 600],
    "njet"   : [  0,   6],
    "balance": [  0,   2],
    "phizmet": [  0,   1]
}

# ranges = {
#     "catSignal-0jet"  : [0, 2000],
#     "catSignal-1jet"  : [0, 2000],
#     "catEM"  : [0, 2000],
#     "cat3L"  : [0, 2000],
#     "cat4L"  : [0, 2000],
#     "catNRB" : [0, 2000],
#     "catTOP" : [0, 2000],
#     "catDY"  : [0, 2000],
#     "njet"   : [  0,   6],
#     "balance": [  0,   2],
#     "phizmet": [  0,   1]
# }

def get_channel_title(text):
    text = text.replace("_","")
    cat = {
        "signal" : "VBS signal",
        "catEM" : "e#mu"  ,
        "catSignal-0jet" : "0 jets",
        "catSignal-1jet" : "1 jets",
        "cat3L" : "WZ"    ,
#        "cat4L" : "ZZ"    ,
        "catWW" : "WW"    ,
        "catNRB": "NRB"   ,
        "catTOP": "TOP"   ,
        "catDY" : "DY"    ,
        "cat4Jet": ">4Jets",
        "njet"  : "N_{jets}",
        "balance" : "balance",
        "phizmet": ""

    }
    return cat[text]




def checkShape(shapeHist):
    negativeBins = False
    zeroBins = False
    for iBin in range(shapeHist.GetNbinsX()):
        b = shapeHist.GetBinContent(iBin + 1)
        if b < 0.:
            negativeBins = True
            shapeHist.SetBinContent(iBin + 1, 0.)
            shapeHist.SetBinError(iBin + 1, -b)
        elif b == 0.:
            zeroBins = True
    if shapeHist.GetBinContent(0) != 0.:
        shapeHist.SetBinContent(0, 0.)
    if shapeHist.GetBinContent(shapeHist.GetNbinsX()+1) != 0.:
        shapeHist.SetBinContent(shapeHist.GetNbinsX()+1, 0.)

def customizeHisto(hist, ratioplot = True):
    hist.GetYaxis().SetTitleSize  (21)
    hist.GetYaxis().SetTitleFont  (43)
    hist.GetYaxis().SetTitleOffset(1.8)
    hist.GetYaxis().SetLabelFont  (43)
    hist.GetYaxis().SetLabelSize  (18)
    hist.GetXaxis().SetTitleSize  (21)
    hist.GetXaxis().SetTitleFont  (43)
    hist.GetXaxis().SetTitleOffset(3.5)
    hist.GetXaxis().SetLabelOffset(0.02)
    hist.GetXaxis().SetLabelFont  (43)
    hist.GetXaxis().SetLabelSize  (18)

def draw_cms_headlabel(label_left  ='#scale[1.2]{#bf{CMS}} #it{Preliminary}',
                       label_right ='#sqrt{s} = 13 TeV, L = 2.56 fb^{-1}'):
    tex_left  = ROOT.TLatex()
    tex_left.SetTextAlign (11);
    tex_left.SetTextFont  (42);
    tex_left.SetTextSize  (0.036);
    tex_right = ROOT.TLatex()
    tex_right.SetTextAlign(31);
    tex_right.SetTextFont (42);
    tex_right.SetTextSize (0.036);
    tex_left.DrawLatexNDC (0.14,
                           1.01 - ROOT.gStyle.GetPadTopMargin(),label_left)
    tex_right.DrawLatexNDC(1-0.05,
                           1.01 - ROOT.gStyle.GetPadTopMargin(),label_right)

def makeRatio(hist1,hist2,ymax=2.1,ymin=0,norm=False, isdata =False):
    """returns the ratio plot hist2/hist1
    if one of the histograms is a stack put it in as argument 2!"""
    if norm:
        try:
            hist1.Scale(1/hist1.Integral())
            hist2.Scale(1/hist2.Integral())
        except(ZeroDivisionError):
            pass
    retH = hist1.Clone()
    retH.Divide(hist2)
    if isdata:
        for ibin in range(hist2.GetNbinsX()+1):
            ymc  = hist2.GetBinContent(ibin);
            stat = hist1.GetBinError  (ibin);
            if (ymc>0):
                retH.SetBinError  (ibin,stat/ymc);
            else:
                retH.SetBinError  (ibin,0);
    ROOT.SetOwnership(retH,0)
    return retH

def draw_error_band(myHisto,systematics={},systematic_only=True, combine_with_systematic=True):
    """
    Draw this histogram with the statistical
    precision error in each bin
    """

    statPrecision = myHisto.Clone('_statErrors_')
    ROOT.SetOwnership(statPrecision,0)
    statPrecision.SetFillColorAlpha(error_band_color,error_band_opacity)
    statPrecision.SetFillStyle(error_band_style)
    statPrecision.SetLineWidth(2)
    statPrecision.SetMarkerColorAlpha(0,0)

    systPrecision = myHisto.Clone('_systErrors_')
    ROOT.SetOwnership(systPrecision,0)
    systPrecision.SetFillColorAlpha(syst_error_band_color,syst_error_band_opacity)
    systPrecision.SetFillStyle(syst_error_band_style)
    systPrecision.SetLineWidth(2)
    systPrecision.SetMarkerColorAlpha(0,0)


    if combine_with_systematic : systematic_only = True
    if systematic_only:
        for ibin in range(myHisto.GetNbinsX()+1):
            y    = statPrecision.GetBinContent(ibin);
            stat = statPrecision.GetBinError  (ibin);

            up_err_sum2 = stat**2
            dw_err_sum2 = stat**2
            for key, syst in systematics.items():
                up_diff   = syst.get("Up").GetBinContent(ibin)   - y
                dw_diff   = syst.get("Down").GetBinContent(ibin) - y
                if up_diff > 0 :
                    up_err_sum2 += up_diff*up_diff
                if dw_diff < 0 :
                    dw_err_sum2 += dw_diff*dw_diff
            up_error = math.sqrt(up_err_sum2)
            dw_error = math.sqrt(dw_err_sum2)

            band_max   = y + up_error
            band_min   = y - dw_error

            systPrecision.SetBinContent(ibin, (band_max + band_min)/2.0);
            systPrecision.SetBinError  (ibin, (band_max - band_min)/2.0);

            statPrecision.SetBinContent(ibin,   y    )
            statPrecision.SetBinError  (ibin,   stat )
            # ------
    return (statPrecision, systPrecision)

def make_stat_progression(myHisto,systematics={},
                          systematic_only=True,
                          combine_with_systematic=True):
    """
        This function returns a function with
        the statistical precision in each bin
    """

    statPrecision = myHisto.Clone('_ratioErrors_')
    systPrecision = myHisto.Clone('_ratioSysErrors_')
    statPrecision.SetFillColorAlpha(ratio_error_band_color,ratio_error_band_opacity)
    statPrecision.SetFillStyle(ratio_error_band_style)
    statPrecision.SetMarkerColorAlpha(0,0)
    systPrecision.SetFillColorAlpha(ratio_syst_band_color,ratio_error_band_opacity)
    systPrecision.SetFillStyle(ratio_syst_band_style)
    systPrecision.SetMarkerColorAlpha(0,0)

    if len(systematics)==0 : systematic_only = False
    for ibin in range(myHisto.GetNbinsX()+1):
        y    = statPrecision.GetBinContent(ibin)
        stat = statPrecision.GetBinError  (ibin)
        if( y > 0 ):
            statPrecision.SetBinContent(ibin,      1 )
            statPrecision.SetBinError  (ibin, stat/y )
        else:
            statPrecision.SetBinContent(ibin,   1 )
            statPrecision.SetBinError  (ibin,   0 )
        if systematic_only:
            up_err_sum2 = 0
            dw_err_sum2 = 0
            if( y > 0 ):
                up_err_sum2 = (stat/y)*(stat/y)
                dw_err_sum2 = (stat/y)*(stat/y)
                for key, syst in systematics.items():
                    up_diff   = (syst.get("Up"  ).GetBinContent(ibin)- y)/y
                    dw_diff   = (syst.get("Down").GetBinContent(ibin)- y)/y
                    if( up_diff > 0 ):
                        up_err_sum2  += up_diff*up_diff
                    if( dw_diff < 0 ):
                        dw_err_sum2  += dw_diff*dw_diff
            up_error = math.sqrt(up_err_sum2)
            dw_error = math.sqrt(dw_err_sum2)
            band_max   = 1 + up_error
            band_min   = 1 - dw_error
            systPrecision.SetBinContent(ibin, (band_max + band_min)/2.0);
            systPrecision.SetBinError  (ibin, (band_max - band_min)/2.0);
    statPrecision.GetYaxis().SetRangeUser(0, 2)
    systPrecision.GetYaxis().SetRangeUser(0, 2)

    return (statPrecision, systPrecision)

def makeRatioPlotCanvas(name=''):
    """
    returns a divided canvas for ratios
    """
    canv  = ROOT.TCanvas("c_" + name, name, canvas_width, canvas_height)
    canv.cd()
    padup = ROOT.TPad("padup", "padup", 0, 0.3, 1, 1.0)
    padup.SetNumber(1)
    paddw = ROOT.TPad("paddw", "paddw", 0, 0.0, 1, 0.3)
    paddw.SetNumber(2)
    padup.Draw()
    padup.SetTopMargin(0.08)
    padup.SetBottomMargin(0.00)
    padup.SetLeftMargin(0.14)
    padup.SetRightMargin(0.05)
    padup.SetFrameBorderMode(0)
    padup.SetFrameBorderMode(0)
    paddw.Draw()
    paddw.SetTopMargin(0.00)
    paddw.SetBottomMargin(0.37)
    paddw.SetLeftMargin(0.14)
    paddw.SetRightMargin(0.05)
    paddw.SetFrameBorderMode(0)
    canv.cd()
    ROOT.SetOwnership(padup,0)
    ROOT.SetOwnership(paddw,0)
    return canv

def check_nuisance(process, nuisance, ch, hist_nm, hist_up, hist_dw):
    c = ROOT.TCanvas(
        "{}_{}_{}".format(process, ch, nuisance),
        "{} {} {}".format(process, ch, nuisance),
        400, 700
    )
    hup_ratio = hist_up.Clone("hratio_up")
    hup_ratio.Divide(hist_nm)
    hdw_ratio = hist_dw.Clone("hratio_dw")
    hdw_ratio.Divide(hist_nm)

    c.Divide(1,2)
    c.cd(1)
    hist_nm.SetLineColor(ROOT.kBlack)
    hist_nm.SetLineWidth(2)
    hist_nm.SetFillStyle(0)
    hist_nm.Draw("hist")

    hist_up.SetLineColor(ROOT.kRed)
    hist_up.SetLineWidth(2)
    hist_up.SetFillStyle(0)
    hist_up.Draw("hist,same")

    hist_dw.SetLineColor(ROOT.kBlue)
    hist_dw.SetLineWidth(2)
    hist_dw.SetFillStyle(0)
    hist_dw.Draw("hist,same")

    if hist_nm.Integral() != 0:
        text = c.GetName() + " lnN {:1.3f}/{:1.3f}".format(
            hist_up.Integral()/hist_nm.Integral(),
            hist_dw.Integral()/hist_nm.Integral()
        )
        l = ROOT.TLatex()
        ROOT.SetOwnership(l, False)
        l.SetNDC()
        l.SetTextSize(1.3*ROOT.gPad.GetTopMargin())
        l.SetTextFont(22)
        l.SetY(1-ROOT.gPad.GetTopMargin()-.1)
        l.SetTextAlign(33)
        l.SetX(1-ROOT.gPad.GetRightMargin()-.1)
        l.SetTitle(text)
        l.Draw()
    c.cd(2)
    hup_ratio.GetYaxis().SetTitle("Ratio")
    hup_ratio.Draw("hist")
    hup_ratio.GetYaxis().SetRangeUser(0.5, 1.5)
    hdw_ratio.Draw("histsame")
    if not os.path.exists("shape_check"):
        os.makedirs("shape_check")
    c.Print("shape_check/%s.png" % c.GetName())
    c.Print("shape_check/%s.pdf" % c.GetName())


def drawing(channel="_3L", ylog=True, lumi=41.5, blind=True, rebin=1):
    x_vec = collections.OrderedDict()
    w_vec = collections.OrderedDict()

    root_legend = ROOT.TLegend(0.4, 0.7, 0.95, 0.90)
    root_legend.SetNColumns(3)
    #root_legend.SetColumnSeparation(0.1)

    first = 0
    stack_mc = ROOT.THStack("", "")
    data_pts = None
    root_histos = []
    root_signal = []
    root_histos_syt = {}
    for procname, cmd  in processes.items():
        files     = cmd["files"]
        hist_objs = []
        dic_root_histos = {}
        for fn in files:
            fn_root = uproot.open(fn)
            bn_root = ROOT.TFile.Open(fn)
            hist_names = []
            syst_names = []
            for nm in fn_root.keys():
                if 'sys' in str(nm):
                    syst_names.append(nm)
                    continue
                if channel not in str(nm):
                    continue
                if observable[channel.replace('_','')] not in str(nm):
                    continue
                hist_names.append(str(nm))
            for hist_name in hist_names:
                hname = hist_name.replace("b'","")
                hname = hname.replace(";1","")
                hist  = bn_root.Get(hname)
                if cmd.get("type").lower() == "data":
                    if blind and (channel=="signal" or channel=="catSignal-0jet" or channel=="catSignal-1jet"):
                        for ibin in range(hist.GetNbinsX()+1):
                            hist.SetBinContent(ibin, 0)
                            hist.SetBinError(ibin, 0)
                    if blind and (channel=="njet"):
                        hist.SetBinContent(1, 0)
                if cmd.get("type").lower() == "background":
                    scale  = xsections[os.path.basename(os.path.dirname(fn))]["xsec"]
                    scale *= xsections[os.path.basename(os.path.dirname(fn))]["kr"]
                    scale *= xsections[os.path.basename(os.path.dirname(fn))]["br"]
                    scale *= 1000.0
                    scale *= lumi/genEventSumw[os.path.basename(os.path.dirname(fn))]["genEventSumw"]
                    scale *= cmd.get("kfactor", 1.0)
                    if procname=="DY":
                        scale *= 0.8
                    hist.Sumw2()
                    hist.Scale(scale)
                    hist.SetDirectory(0)
                    for syst in systematics_sources:
                        try:
                            _h_syst_up = bn_root.Get(hname + "_sys_"+syst+"Up")
                            _h_syst_up.SetDirectory(0)
                            _h_syst_up.Sumw2()
                            _h_syst_up.Scale(scale)
                            _h_syst_dw = bn_root.Get(hname + "_sys_"+syst+"Down")
                            _h_syst_dw.SetDirectory(0)
                            _h_syst_dw.Sumw2()
                            _h_syst_dw.Scale(scale)
                            if options.debug:
                                print(colored(
                                        "{:20} lnN {:1.3f}/{:1.3f}".format(
                                            syst,
                                            _h_syst_up.Integral()/hist.Integral() if hist.Integral() else 1.0,
                                            _h_syst_dw.Integral()/hist.Integral() if hist.Integral() else 1.0,
                                        ), "blue"
                                    ))
                            if root_histos_syt.get(syst, None) is None:
                                root_histos_syt[syst] = {
                                    "Up"   : _h_syst_up,
                                    "Down" : _h_syst_dw
                                }
                            else:
                                root_histos_syt[syst]["Up"  ].Add(_h_syst_up)
                                root_histos_syt[syst]["Down"].Add(_h_syst_dw)
                        except:
                            pass
                elif cmd.get("type").lower() == "signal":
                    print(colored(fn, "red"))

                hist.SetDirectory(0)
                hist_objs.append(hist)
        assert(len(hist_objs)!=0)

        hist_com = hist_objs[0]
        for _h_ in hist_objs[1:]:
            hist_com.Add(_h_)

        hist_com.SetTitle(";{};Events".format(names[channel.replace("_","")]))
        hist_com.SetFillColor(cmd.get("color",1))
        hist_com.SetLineColor(ROOT.kBlack)
        hist_com.SetLineStyle(1)
        hist_com.SetLineWidth(1)
        hist_com.SetDirectory(0)

        if cmd.get("type") == "background" and hist_com.Integral() > 0:
            stack_mc.Add(hist_com)
            print(colored(" -- %5s : %1.3f"%(procname, hist_com.Integral()), "blue"))
            root_histos.append(hist_com)
            root_legend.AddEntry(hist_com, procname, "f" )
        elif cmd.get("type") == "data":
            hist_com.SetBinErrorOption(ROOT.TH1.kPoisson)
            hist_com.SetLineWidth(2)
            hist_com.SetFillStyle(0)
            hist_com.SetMarkerStyle(20)
            hist_com.SetFillColorAlpha(0,0)
            hist_com.SetMarkerSize (1.2)
            hist_com.SetMarkerColor(1)
            data_pts = hist_com
        else:
            root_signal.append(hist_com)

    c = makeRatioPlotCanvas(name = channel)
    c.cd(1)
    _htmp_ = root_histos[0].Clone('__htmp__')
    ROOT.SetOwnership(_htmp_, 0)
    _htmp_.Reset()
    _ymax_ = max([x.GetMaximum() for x in root_histos])
    _ymin_ = min([x.GetMinimum() for x in root_histos])
    if ylog :
        _ymin_ = (0.01 - 0.003) if _ymin_ <= 0 else _ymin_
        _ymax_ = stack_mc.GetMaximum()*1000
        _htmp_.GetYaxis().SetRangeUser(_ymin_,_ymax_)
        ROOT.gPad.SetLogy()
    else:
        _ymin_ = 0
        _ymax_ = _ymax_ + _ymax_ * 0.5
        _htmp_.GetYaxis().SetRangeUser(_ymin_,_ymax_)
    customizeHisto(_htmp_)
    _htmp_.Draw('hist')
    _htmp_.GetXaxis().SetRangeUser(
        ranges[channel.replace("_","")][0],
        ranges[channel.replace("_","")][1]
    )
    stack_mc.Draw('hist,same')
    data_pts.SetFillStyle(0)
    data_pts.Draw("E,same")
    # Error bars
    (herrstat, herrsyst) = draw_error_band(stack_mc.GetStack().Last(),root_histos_syt)
    herrsyst.Draw("E2,same")
    # this to check the different varations
    if options.debug:
        for n, syst in root_histos_syt.items():
            syst['Up'].SetLineColor(2)
            syst['Up'].Draw('hist,same')
            syst['Down'].SetLineColor(4)
            syst['Down'].Draw('hist,same')

    # this is for the legend
    root_legend.SetTextAlign( 12 )
    root_legend.SetTextFont ( 43 )
    root_legend.SetTextSize ( 18 )
    root_legend.SetLineColor( 0 )
    root_legend.SetFillColor( 0 )
    root_legend.SetFillStyle( 0 )
    root_legend.SetLineColorAlpha(0,0)
    root_legend.SetShadowColor(0)

    t = ROOT.TLatex()
    t.SetTextAlign(13)
    t.SetTextFont (text_font)
    t.SetTextSize (text_size)

    t.DrawLatexNDC((0.02 + ROOT.gStyle.GetPadLeftMargin()),
                   (0.93 - ROOT.gStyle.GetPadTopMargin()),
                   "%s region" % get_channel_title(channel))
    draw_cms_headlabel(
        label_right='#sqrt{s} = 13 TeV, L = %1.2f fb^{-1}' % lumi
    )
    ROOT.gPad.RedrawAxis()

    c.cd(2)
    (errorHist,systHist) = make_stat_progression(
        stack_mc.GetStack().Last(),
        systematics=root_histos_syt
    )
    ROOT.SetOwnership(errorHist,0)
    ROOT.SetOwnership(systHist ,0)

    errorHist.GetXaxis().SetTitle(_htmp_.GetXaxis().GetTitle())
    errorHist.GetYaxis().SetTitle('Data/MC')
    errorHist.GetYaxis().CenterTitle(True)
    systHist.GetXaxis ().SetTitle(_htmp_.GetXaxis().GetTitle())
    systHist.GetYaxis ().SetTitle('Data/MC')
    systHist.GetYaxis ().CenterTitle(True)
    systHist.GetXaxis().SetRangeUser(
        ranges[channel.replace("_","")][0],
        ranges[channel.replace("_","")][1]
    )
    customizeHisto(errorHist)
    customizeHisto(systHist)

    systHist.Draw('E2')
    errorHist.Draw('E2,same')

    ratioHist = makeRatio(
        hist1 = data_pts,
        hist2 = stack_mc.GetStack().Last(),
        isdata = True
    )
    ROOT.SetOwnership(ratioHist,0)
    ratioHist.GetXaxis().SetTitle(_htmp_.GetXaxis().GetTitle())
    ratioHist.GetYaxis().SetTitle(_htmp_.GetYaxis().GetTitle())
    ratioHist.Draw('same')
    line = ROOT.TLine(
        ranges[channel.replace("_","")][0],1,
        ranges[channel.replace("_","")][1],1
    )
    line.SetLineColor(4)
    line.SetLineStyle(7)
    line.Draw()
    ROOT.SetOwnership(line,0)
    print(" Lumi : %1.3f" % lumi)
    print(" MC   : %1.3f" % stack_mc.GetStack().Last().Integral())
    print(" DATA : %1.3f" % data_pts.Integral())
    c.cd(1)
    root_legend.AddEntry(systHist, "Uncert", "f"   )
    root_legend.AddEntry(data_pts, "Data"  , "lep" )
    root_legend.Draw()

    if not os.path.exists("plots/UL_withsignal{}/{}".format(options.era,options.tag)):
        os.makedirs("plots/UL_withsignal{}/{}".format(options.era,options.tag))
    c.SaveAs("plots/UL_withsignal{}/{}/plot_MET_{}_region.pdf".format(options.era, options.tag, channel))
    c.SaveAs("plots/UL_withsignal{}/{}/plot_MET_{}_region.png".format(options.era, options.tag, channel))


def main():
    lumi = {
        "2016" : 35.9,
        "2017" : 41.5,
        "2018" : 60.0
    }
    if options.tag == 'ZZinclusive':
        drawing("catSignal-1jet" , lumi=lumi[options.era],blind=True)
        drawing("catSignal-0jet" , lumi=lumi[options.era],blind=True)
    else:
        drawing("signal" , lumi=lumi[options.era],blind=True)
    drawing("cat3L"          , lumi=lumi[options.era])
    drawing("catEM"          , lumi=lumi[options.era])
    drawing("catDY"          , lumi=lumi[options.era])
#    drawing("cat4Jet"          , lumi=lumi[options.era])
#    drawing("catWW"          , lumi=lumi[options.era])
    #
#    drawing("njet"          , lumi=lumi[options.era])
#    drawing("balance"       , lumi=lumi[options.era])
#    drawing("phizmet"       , lumi=lumi[options.era])

if __name__=="__main__":
    main()
