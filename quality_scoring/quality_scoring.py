import pandas as pd
import os
import gzip
import json
import time
import sys

from argparse import ArgumentParser

from pyterrier_quality import QualT5

#all input files need to be located in this directory
INPUT_PATH = '/inputs'
OUTPUT_PATH = '/outputs/output'

"""
Accepted Data Formats:
-csv (pyterrier)
-parquet (OWS)
-json.gz (ClueWeb)
"""
FORMATS = ('.csv', '.parquet', 'json','.json.gz')

arg_parser = ArgumentParser()
arg_parser.add_argument('--model', '-m', default='small', choices=['tiny', 'small', 'base'], dest='model')
arg_parser.add_argument('--output-format', '-f', default='csv', choices=['csv', 'json', 'parquet'], dest='output_format')
args = arg_parser.parse_args()

files = [os.path.join(INPUT_PATH,f) for f in os.listdir(INPUT_PATH) if str(f).endswith(FORMATS)]

while not files:
    sys.stderr.write('Warning: Input folder is empty. Please check your mounted file path or your Docker configuration (particularly if running on Windows).')
    time.sleep(5)
    files = [os.path.join(INPUT_PATH, f) for f in os.listdir(INPUT_PATH) if str(f).endswith(FORMATS)]
    print('Files:',files)

df = pd.DataFrame({})

if args.model=='tiny':
    qmodel = QualT5('pyterrier-quality/qt5-tiny')
elif args.model=='base':
    qmodel = QualT5('pyterrier-quality/qt5-base')
else:
    #default: small
    qmodel = QualT5('pyterrier-quality/qt5-small')

for f in files:
    if f.endswith('.csv'):
        #terrier format
        dfin = pd.read_csv(f)
        df = pd.concat([df, dfin], axis=0, ignore_index=True)
    elif f.endswith('.json'):
        #assume terrier format
        dfin = pd.read_json(f)
        df = pd.concat([df, dfin], axis=0, ignore_index=True)
    elif f.endswith('.parquet'):
        #OWS format
        dfin = pd.read_parquet(f)
        # rename into terrier format
        dfin = dfin.rename({'id': 'docno', 'plain_text': 'text'}, axis=1)
        df = pd.concat([df, dfin], axis=0, ignore_index=True)
    elif f.endswith('.gz'):
        with gzip.open(f) as fin:
            for i, line in enumerate(fin):
                dfin = pd.DataFrame(json.loads(line), index=[i])
                # rename into terrier format
                df = df.rename({'ClueWeb22-ID': 'docno', 'Clean-Text': 'text'}, axis=1)
                df = pd.concat([df, dfin], axis=0, ignore_index=True)
    else:
        print("Invalid file format")
        pass

#print(df)
scored = qmodel.transform(df)
print(scored)

if args.output_format=='json':
    scored.to_json(OUTPUT_PATH+'.json')
elif args.output_format=='parquet':
    scored.to_parquet(OUTPUT_PATH+'.parquet')
else:
    #default: csv
    scored.to_csv(OUTPUT_PATH+'.csv')

#print(os.listdir('/outputs'))