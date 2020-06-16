#!/usr/bin/env python3

import json
import numpy as np
import argparse
import os
from datetime import datetime
from glob import glob
import re
import pandas as pd

import countrydata

# XXX path to folder with output from `request_country.py`
datafolder = "."
df = countrydata.CollectCountryData(datafolder)
df = countrydata.AppendInferred(df, datafolder)
df = countrydata.AppendOfficalLockdown(df)

fpath = "tint.csv"
print(fpath)
with open(fpath, 'w') as f:
    f.write("country,inferred,official,delay\n")
    for i, row in enumerate(df.sort_values(by='fullname').itertuples()):
        inferred = row.tint_mean
        official = row.official_lockdown
        if not pd.isnull(official):
            delay = "{:+d}".format((inferred - official).days)
            official = official.strftime('%Y-%m-%d')
        else:
            delay = ""
            official = ""
        inferred = inferred.strftime('%Y-%m-%d')
        f.write(','.join([row.fullname, inferred, official, delay]) + '\n')
