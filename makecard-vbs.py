import yaml
import os
import argparse
import dctools
import numpy as np
from termcolor import colored

lumis = {
    "2016" : 35.9,
    "2017" : 41.5,
    "2018" : 60.0
}

lumi_unc = {
    "2016" : 1.025,
    "2017" : 1.023,
    "2018" : 1.025
}

def main():
    parser = argparse.ArgumentParser(description='The Creator of Combinators')
    parser.add_argument("-i"  , "--input"   , type=str, default="config/inputs-NanoAODv5-2018.yaml")
    parser.add_argument("-v"  , "--variable", type=str, default="measMET")
    parser.add_argument("-o"  , "--outdir"  , type=str, default="fitroom")
    parser.add_argument("-c"  , "--channel" , nargs='+', type=str)
    parser.add_argument("-s"  , "--signal"  , nargs='+', type=str)
    parser.add_argument("-t"  , "--stack"   , nargs='+', type=str)
    parser.add_argument("-era", "--era"     , type=str, default="2018")
    parser.add_argument("-f"  , "--force"   , action="store_true")
    parser.add_argument("-ns" , "--nostatuncert", action="store_false")
    parser.add_argument("--binrange" ,nargs='+', type=float, default=0)
    parser.add_argument("--rebin" ,type=int, default=1)
    parser.add_argument("-xs" , "--xsection", type=str, default="")
    parser.add_argument("--onexsec", action="store_true")

    options = parser.parse_args()
    
    print("range =", options.binrange)
    # create a working directory where to store the datacards
    try:
        os.mkdir(options.outdir)
        print("Directory " , options.outdir ,  " Created ")
    except:
        if options.force:
            os.rmdir(options.outdir)
            os.mkdir(options.outdir)
            print("Directory " , options.outdir ,  " Re-created ")

    inputs = None
    with open(options.input) as f:
        try:
            inputs = yaml.safe_load(f.read())
        except yaml.YAMLError as exc:
            print (exc)

    xsections = None
    if len(options.xsection) != 0:
        with open(options.xsection.replace("ERA", options.era)) as f:
            print(" -- cross section file : ", options.xsection.replace("ERA", options.era))
            try:
                xsections = yaml.safe_load(f.read())
            except yaml.YAMLError as exc:
                print (exc)
    if options.onexsec:
        xsections = { s: {'br': 1.0, 'kr': 1.0, 'xsec': 1.0} for s, xs in xsections.items()}

    if len(options.channel) == 1:
        options.channel = options.channel[0]

    # make datasets per prcess
    datasets = {}
    nsignals = 0
    signal = ""
    for dg in options.stack:
        p = dctools.datagroup(
            inputs[dg]["files"],
            ptype      = inputs[dg]["type"],
            observable = options.variable,
            name       = dg,
            kfactor    = inputs[dg].get("kfactor", 1.0),
            xsections  = xsections,
            channel    = options.channel,
            rebin      = options.rebin,
            binrange   = options.binrange,
            luminosity = lumis[options.era]
        )
        #p.save()
        datasets[p.name] = p
        if p.ptype == "signal":
            signal = p.name
            
    card_name = "ch"+options.era
    if isinstance(options.channel, str):
      if "catSignal" in options.channel:
        card_name = options.channel.replace('catSignal', 'catSR').replace('-','').replace('jet','J')+options.era
      else:
        card_name = options.channel+options.era 

    # elif isinstance(options.channel, list):
    #     if np.all(["signal" in c.lower() for c in options.channel]):
    #         card_name = "catSR"+options.era

    card = dctools.datacard(
        name = signal,
        channel= card_name
    )
    card.shapes_headers()

    data_obs = datasets.get("data").get("nom")
    card.add_observation(data_obs)

    for n, p in datasets.items():
      #name = "Sig" if p.ptype=="signal" else p.name
      if p.ptype=="data":
        continue
      card.add_nominal(p.name, p.get("nom"))
      print("nominal vlaues : ", p.get("nom").values(0))

      card.add_nuisance(p.name, "{:<21}  lnN".format("CMS_lumi_{}".format(options.era)), lumi_unc[options.era])
      card.add_nuisance(p.name, "{:<21}  lnN".format("CMS_RES_e"),  1.005)
      card.add_nuisance(p.name, "{:<21}  lnN".format("CMS_RES_m"),  1.005)
      
      card.add_shape_nuisance(p.name, "CMS_EFF_e", p.get("ElecronSF" ), symmetrise=False)
      card.add_shape_nuisance(p.name, "CMS_EFF_m", p.get("MuonSF")    , symmetrise=False)
      
      card.add_shape_nuisance(p.name, "CMS_JES_{}".format(options.era), p.get("jesTotal") , symmetrise=False)
      card.add_shape_nuisance(p.name, "CMS_JER_{}".format(options.era), p.get("jer")      , symmetrise=False)

      #card.add_shape_nuisance(name, "CMS_BTag_{}".format(options.era), p.get("btagEventWeight"), symmetrise=False)
      card.add_shape_nuisance(p.name, "CMS_Trig_{}".format(options.era), p.get("TriggerSFWeight"), symmetrise=False)
      
      if options.era in ['2016','2017']:
        card.add_shape_nuisance(p.name, "CMS_pfire_{}".format(options.era), p.get("PrefireWeight"))

      card.add_shape_nuisance(p.name, "CMS_PU_{}".format(options.era), p.get("puWeight"  ), symmetrise=False)
      
      #QCD scale, PDF and other theory uncertainty
      if 'DY' not in p.name:
        card.add_qcd_scales(
          p.name, "CMS_QCDScale{}_{}".format(p.name, options.era), 
          [p.get("QCDScale0w"), p.get("QCDScale1w"), p.get("QCDScale2w")]
        )
      
      # PDF uncertaintites
      if p.name != "TOP":
        card.add_shape_nuisance(p.name, "PDF", p.get("PDF"), symmetrise=False)  
      
      # Underlying events
      card.add_nuisance(p.name, "{:<21}  lnN".format("UEPS"),  1.020) 
      
      # EWK uncertainties
      if p.name in ["ZZ"]:
        card.add_shape_nuisance(p.name, "EWKZZ", p.get("EWK"), symmetrise=False)
      if p.name in ["WZ"]:
        card.add_shape_nuisance(p.name, "EWKWZ", p.get("EWK"), symmetrise=False)                          
      
      # define rates
      if p.name  in ["WW"]:
        if "catEM" in card_name:
          card.add_rate_param("NormWW_" + options.era, "catEM*", p.name)
        elif "signal" in card_name:
          card.add_rate_param("NormWW_" + options.era, card_name+'*', p.name)

      # define rate 3L category
      elif p.name in ["WZ"]:
        if ("cat3L" in card_name):
          card.add_rate_param("NormWZ_" + options.era, "cat3L*", p.name)
        elif "signal" in card_name:
          card.add_rate_param("NormWZ_" + options.era, card_name+'*', p.name)

      # define rate for DY category
      elif p.name in ["DY"]:
        if "DY" in card_name:
          card.add_rate_param("NormDY_" + options.era, "catDY*", p.name)
        elif "signal" in card_name:
          card.add_rate_param("NormDY_" + options.era, card_name+'*', p.name)

      # define rate for TOP category
      elif p.name in ["TOP"]:
        if "TOP" in card_name:
          card.add_rate_param("NormTOP_" + options.era, "catTOP*", p.name)
        elif "signal" in card_name:
          card.add_rate_param("NormTOP_" + options.era, card_name+'*', p.name) 
      # adding statistical uncertainties
    card.add_auto_stat()
    card.dump()


if __name__ == "__main__":
    main()
