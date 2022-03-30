import yaml
import os
import uproot
import argparse


def main():
    parser = argparse.ArgumentParser(description='The Creator of Combinators')
    parser.add_argument("-i"  , "--input"   , type=str, default="config/inputs-NanoAODv5-2018.yaml")
    options = parser.parse_args()

    inputs = None
    with open(options.input) as f:
        try:
            inputs = yaml.safe_load(f.read())
        except yaml.YAMLError as exc:
            print (exc)

    processes = {}
    for i,c in inputs.items():
      if c['type'].lower() != 'data':
        for fi in c['files']:
          proc = fi.split('/')[-2]
          if proc not in processes.keys():
            processes[proc] = []
          processes[proc].append(fi)
          if not os.path.exists('./data/' + proc):
            os.mkdir('./data/' + proc)
      else:
        processes['data'] = c['files']

    if not os.path.exists('./data/data'):
      os.mkdir('./data/data')

    for p, files in processes.items():
      print('merging ... ', p)
      outfile = uproot.recreate('./data/' + p + "/merged.root")
      fileHadle = [uproot.open(fn) for fn in files]
      for e in fileHadle[0].keys():
        if outfile[e].classname != 'TH1D': continue
        print(e)
        outfile[e] = fileHadle[0][e].to_boost()

      for e in fileHadle[0].keys():
        if outfile[e].classname != 'TH1D': continue
        for fn in fileHadle[1:]:
          outfile[e] = outfile[e].to_boost() + fn[e].to_boost() 
        



if __name__ == "__main__":
    main()


