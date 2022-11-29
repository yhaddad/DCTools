import yaml
import os
import gzip
import pickle
import argparse
import dctools
import hist
import matplotlib.pyplot as plt
from dctools import plot as plotter
from typing import Any, IO


class config_input:
    def __init__(self, cfg):
        self._cfg = cfg 
    
    def __getitem__(self, key):
        v = self._cfg[key]
        if isinstance(v, dict):
            return config_input(v)

    def __getattr__(self, k):
        try:
            v = self._cfg[k]
            if isinstance(v, dict):
                return config_input(v)
            return v
        except:
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
    filename = os.path.abspath(os.path.join(loader._root, loader.construct_scalar(node)))
    extension = os.path.splitext(filename)[1].lstrip('.')

    with open(filename, 'r') as f:
        if extension in ('yaml', 'yml'):
            return yaml.load(f, config_loader)
        elif extension in ('json', ):
            return json.load(f)
        else:
            return ''.join(f.readlines())

yaml.add_constructor('!include', construct_include, config_loader)




def main():
    parser = argparse.ArgumentParser(description='The Creator of Combinators')
    parser.add_argument("-i"  , "--input"   , type=str , default="./config/input_UL_2018-algiers.yaml")
    parser.add_argument("-v"  , "--variable", type=str , default="nnscore")
    parser.add_argument("-y"  , "--era"     , type=str , default='2018')
    parser.add_argument("-c"  , "--channel" , nargs='+', type=str)
    parser.add_argument("-s"  , "--signal"  , nargs='+', type=str)
    parser.add_argument('-n'  , "--name"    , type=str , default='')
    parser.add_argument('-p'  , "--plot"    , action="store_true")
    parser.add_argument('--rebin', type=int, default=1, help='rebin')
    parser.add_argument("--bins", 
            type=lambda s: [float(item) for item in s.split(',')], 
            help='input a comma separated list. ex: --bins="-1.2,0,1.2"'
    )
    parser.add_argument('--blind', action='store_true', help='blinding the channel')
    parser.add_argument('--checksyst', action='store_true')

    options = parser.parse_args()
    
    config = None
    with open(options.input) as f:
        try:
            config = config_input(
                yaml.load(f.read(), config_loader)
            )
        except yaml.YAMLError as exc:
            print (exc)

    boosthist = {}
    for fname in config.boosthist:
        if '.gz' in fname:
            with gzip.open(fname, "rb") as f:
                boosthist.update(pickle.load(f))
        else:
            with open(fname, 'rb') as f:
                boosthist.update(pickle.load(f))

    if len(options.channel) == 1:
        options.channel = options.channel[0]
    
    # make datasets per prcess
    datasets = {}
    signal = ""

    if options.name=='':
        options.name == options.channel

    if isinstance(list(boosthist.values())[0]["hist"], dict):
        boosthist = {k: {"hist": v["hist"][options.variable], "sumw":v["sumw"]}for k, v in boosthist.items()}
        
    for name in config.groups:
        histograms = dict(
            filter(
                lambda _n: _n[0] in config.groups[name].processes,
                boosthist.items()
            )
        )

        p = dctools.datagroup(
            histograms = histograms,
            ptype      = config.groups[name].type,
            observable = options.variable,
            name       = name,
            xsections  = config.xsections,
            channel    = options.channel,
            luminosity = config.luminosity.value,
            rebin      = options.rebin,
        )

        #p.save()
        datasets[p.name] = p
        if p.ptype == "signal":
            signal = p.name
   
    if options.plot:
        _plot_channel = plotter.add_process_axis(datasets)
        pred = _plot_channel.project('process','systematic', options.variable)[:hist.loc('data'),:,:]
        data = _plot_channel[{'systematic':'nominal'}].project('process',options.variable)[hist.loc('data'),:] 

        plt.figure(figsize=(6,7))
        ax, bx = plotter.mcplot(
            pred[{'systematic':'nominal'}].stack('process'),
            data=None if options.blind else data, 
            syst=pred.stack('process'),
        )

        ax.set_yscale('log')
        bx.set_ylim([0.1, 1.9])
        plt.savefig(f'plot-{options.channel}-{options.variable}-{options.era}.pdf')


    if options.checksyst:        
        _plot_channel = plotter.add_process_axis(datasets)
        pred = _plot_channel.project('process','systematic', options.variable)[:hist.loc('data'),:,:]
        data = _plot_channel[{'systematic':'nominal'}].project('process',options.variable)[hist.loc('data'),:] 
        plotter.check_systematic(
            pred[{'systematic':'nominal'}].stack('process'),
            syst=pred.stack('process'),
            plot_file_name=f'check-sys-{options.channel}-{options.era}'
        )

    card_name = 'noname'
    if options.name == '':
        card_name = options.channel+options.era
    else:
        card_name = options.name+options.era
    card = dctools.datacard(
        name = signal,
        channel= card_name
    )
    card.shapes_headers()

    data_obs = datasets.get("data").get("nominal")
    card.add_observation(data_obs)

    for n, p in datasets.items():
        if p.ptype=="data":
            continue

        card.add_nominal(p.name, p.get("nominal"), p.ptype)

        card.add_log_normal(p.name, f"CMS_lumi_{options.era}", config.luminosity.uncer)
        # card.add_log_normal(p.name, "CMS_res_e",  1.005)
        # card.add_log_normal(p.name, "CMS_RES_m",  1.005) 
        # card.add_log_normal(p.name, "UEPS"     ,  1.020)


        #card.add_shape_nuisance(p.name, "CMS_res_e", p.get("ElectronEn"), symmetrise=False)
        #card.add_shape_nuisance(p.name, "CMS_eff_e", p.get("ElecronSF" ), symmetrise=False)
        #card.add_shape_nuisance(p.name, "CMS_res_m", p.get("MuonEn")    , symmetrise=False)
        #card.add_shape_nuisance(p.name, "CMS_eff_m", p.get("MuonSF")    , symmetrise=False)

        # JES/JES and UEPS
        card.add_shape_nuisance(p.name, f"CMS_jes_{options.era}", p.get("JES"), symmetrise=False) 
        card.add_shape_nuisance(p.name, f"CMS_jer_{options.era}", p.get("JER"), symmetrise=False)
        card.add_shape_nuisance(p.name, f"CMS_UES_{options.era}", p.get("UES"), symmetrise=False)
        
        # Can maybe ne correlated over era's? 
        card.add_shape_nuisance(p.name, f"CMS_UEPS_FRS_{options.era}", p.get("UEPS_FSR"), symmetrise=False)
        card.add_shape_nuisance(p.name, f"CMS_UEPS_ISR_{options.era}", p.get("UEPS_ISR"), symmetrise=False)
        

        # b-tagging uncertainties
        card.add_shape_nuisance(p.name, f"CMS_btag_sf_bc_{options.era}" , p.get(f"btag_sf_bc_{options.era}")   , symmetrise=False)
        card.add_shape_nuisance(p.name, f"CMS_btag_sf_uds_{options.era}", p.get(f"btag_sf_light_{options.era}"), symmetrise=False)

        # b-tagging uncertainties correlated over years
        card.add_shape_nuisance(p.name, "CMS_btag_sf_bc"  , p.get("btag_sf_bc_correlated")   , symmetrise=False)
        card.add_shape_nuisance(p.name, "CMS_btag_sf_uds" , p.get("btag_sf_light_correlated"), symmetrise=False)
        card.add_shape_nuisance(p.name, "CMS_btag_df_stat", p.get("btag_sf_stat")            , symmetrise=False)

        # other uncertainties
        card.add_shape_nuisance(p.name, f"CMS_pileup_{options.era}", p.get("pileup_weight"), symmetrise=False)
       
        #QCD scale, PDF and other theory uncertainty
        if 'DY' not in p.name:
            card.add_qcd_scales(
                    p.name, "CMS_QCDScale{}_{}".format(p.name, options.era), 
                    [p.get("QCDScale0w"), p.get("QCDScale1w"), p.get("QCDScale2w")]
        )
        
        # PDF uncertaintites / not working for the moment
        card.add_shape_nuisance(p.name, "PDF"   , p.get("PDF_weight")  , symmetrise=False)
        card.add_shape_nuisance(p.name, "AlphaS", p.get("PDFaS_weight"), symmetrise=False)

        # EWK uncertainties
        #if p.name in ["ZZ"]:
        #    card.add_shape_nuisance(p.name, "EWKZZ", p.get("EWK"), symmetrise=False)
        #if p.name in ["WZ"]:
        #    card.add_shape_nuisance(p.name, "EWKWZ", p.get("EWK"), symmetrise=False)                          
        # define rates
        if p.name  in ["WW"]:
            if "catEM" in card_name:
                card.add_rate_param("NormWW_" + options.era, "catEM*", p.name)
            elif "SR" in card_name:
                card.add_rate_param("NormWW_" + options.era, card_name+'*', p.name)
        # define rate 3L categoryel 
        elif p.name in ["WZ"]:
            if "cat3L" in card_name:
                card.add_rate_param("NormWZ_" + options.era, "cat3L*", p.name)
            elif "SR" in card_name:
                card.add_rate_param("NormWZ_" + options.era, card_name+'*', p.name)
        # define rate for DY category
        elif p.name in ["DY"]:
            if "DY" in card_name:
                card.add_rate_param("NormDY_" + options.era, "catDY*", p.name)
            elif "SR" in card_name:
                card.add_rate_param("NormDY_" + options.era, card_name+'*', p.name)
        # define rate for TOP category
        elif p.name in ["TOP"]:
            if "TOP" in card_name:
                card.add_rate_param("NormTOP_" + options.era, "catTOP*", p.name)
            elif "SR" in card_name:
                card.add_rate_param("NormTOP_" + options.era, card_name+'*', p.name) 
        card.add_auto_stat()

    # saving the datacard
    card.dump()

if __name__ == "__main__":
    main()
