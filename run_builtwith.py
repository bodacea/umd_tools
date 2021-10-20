#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Run builtwith to get list of sites associated with an input list of domains. 
Needs a builtwith account to run.

'''

import pandas as pd
import requests
import json 
import re
import os
import sys
from datetime import datetime

datadir = 'data/builtwith'
#Make sure there's somewhere to put the data
if not os.path.exists(datadir):
    os.makedirs(datadir)

def check_builtwith(bwdom):

    matches = pd.DataFrame([])
    identifiers = pd.DataFrame([])
    bwapi = 'rv1' # 'free1' is the free api

    try:
        bwurl = 'https://api.builtwith.com/{}/api.json?KEY={}&LOOKUP={}'.format(bwapi, bwkey, bwdom)
        bwresp = requests.get(bwurl)

        with open(datadir+'/{}.json'.format(bwdom), 'w') as outfile:
            json.dump(bwresp.json(), outfile)


        rs = bwresp.json()['Relationships']
        for thisr in rs:
            fromdomain = thisr['Domain']
            rsi = thisr['Identifiers']

            ids = pd.DataFrame(rsi).drop('Matches', axis=1)
            ids['FromDomain'] = fromdomain
            identifiers = identifiers.append(ids)

            for rsix in rsi:
                rsimatches = pd.DataFrame(rsix['Matches'])
                rsimatches['Type'] = rsix['Type']
                rsimatches['Value'] = rsix['Value']
                rsimatches['FromDomain'] = fromdomain
                if len(rsimatches) > 0:
                    matches = matches.append(rsimatches)
        matches.to_csv(datadir+'/{}_matches.csv'.format(bwdom), index=False)
        identifiers.to_csv(datadir+'/{}_identifiers.csv'.format(bwdom), index=False)
    except:
        print('builtwith failed for {}'.format(bwdom))
    return matches, identifiers

    # Main starts here
if __name__ == '__main__':
    # Add your own API key values here
    f = open('/Users/sara/builtwithkey.txt', 'r')
    bwkey = f.readline().strip()
    f.close()
 
    # Check that search terms were provided at the command line
    fromdomains = []
    if (len(sys.argv) > 1):
        fromdomains = sys.argv[1:]
    else:
        print("No search terms provided. Exiting.")
        sys.exit(0)

    allmatches = pd.DataFrame([])
    allidentifiers = pd.DataFrame([])

    num_domains = len(fromdomains)
    for count, bwdom in enumerate(fromdomains):
        print('{}/{} searching on domain: {}'.format(count+1, num_domains, bwdom))
        matches, identifiers = check_builtwith(bwdom)
        if len(matches) > 0:
            allmatches = allmatches.append(matches)
        if len(identifiers) > 0:
            allidentifiers = allidentifiers.append(identifiers)

    timestamp = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
    matches.to_csv(datadir+'/{}_matches.csv'.format(timestamp), index=False)
    identifiers.to_csv(datadir+'/{}_identifiers.csv'.format(timestamp), index=False)
    