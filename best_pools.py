#!./venv/bin/python
# coding: utf-8

import csv
import requests
import yaml
from orca_pools import *
from raydium_pools import *

with open('parameters.yaml') as f:
    params = yaml.safe_load(f)

with open('tokens.csv') as f:
    reader = csv.DictReader(f)
    tokens = {row['address']: row['symbol'] for row in reader}

def main():
    args = get_args()
    orca_pools = requests.get(params['orca_url']).json()['whirlpools']
    orca_pools = [pool_dict_orca(p) for p in orca_pools if isgood_pool_orca(p, risk_off=args.risk_off)]

    rayd_pools = requests.get(params['raydium_url']).json()['data']
    rayd_pools = [pool_dict_rayd(p) for p in rayd_pools if isgood_pool_rayd(p, risk_off=args.risk_off)] 

    pools = orca_pools + rayd_pools

    if args.filter:
        pools = pool_filter(pools, args.filter)
        
    pools.sort(key = my_key(args.tvl), reverse=True)

    for p in pools[:args.display_limit]:
        pool_print(p, args.verbose)

if __name__ == '__main__':
    main()