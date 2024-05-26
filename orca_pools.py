#!./venv/bin/python
# coding: utf-8

import argparse
import csv
from math import log10
import os
import requests
from tokenlist import get_tokenlist
import yaml

if not os.path.exists('tokens.csv'):
    get_tokenlist()

with open('parameters.yaml') as f:
    params = yaml.safe_load(f)

with open('tokens.csv') as f:
    reader = csv.DictReader(f)
    tokens = {row['address']: row['symbol'] for row in reader}

def get_args():
    parser = argparse.ArgumentParser(
        description="Best Pools - selection of the best liquidity pools on Solana")
    parser.add_argument("-v", "--verbose", action="store_true",
                help="In verbose mode, you can also see the tokens' addresses")
    parser.add_argument("-t", "--tvl", action="store_true", 
                help="Sorts the pools by log(TVL)*APR instead of APR")
    parser.add_argument("-r", "--risk-off", action="store_true", 
                help="In risk-off mode, only lower risk pools are listed")
    parser.add_argument("-f", "--filter", type=str, 
                help="Filter the pools by token symbol")
    parser.add_argument("-d", "--display-limit", type=int, 
                default=params['default_display_limit'],
                help="Set the number of pools to display")
    return parser.parse_args()

def get_orca_pools(risk_off, filter):
    pools = requests.get(params['orca_url']).json()['whirlpools']
    pools = [pool_dict_orca(p) for p in pools if isgood_pool_orca(p, risk_off=risk_off)]
    if filter:
        pools = pool_filter(pools, filter)
    return pools

def isgood_token(addr, risk_off):
    if addr not in tokens:
        return False
    
    sym = tokens[addr].lower()

    if not risk_off and addr in params['risk_include']:
        return True
    
    for i in params['include']:
        if i.lower() in sym \
            and sym not in params['exclude'] \
            and addr not in params['addr_exclude']:
                return True
    return False

def isgood_pool_orca(pool, risk_off):
    if not (
            pool.get('totalApr', {}).get('month', 0) \
        and pool.get('totalApr', {}).get('week', 0)):
            return False
    
    if      isgood_token(pool['tokenA']['mint'], risk_off=risk_off) \
        and isgood_token(pool['tokenB']['mint'], risk_off=risk_off) \
        and min(pool['totalApr']['month'], pool['totalApr']['week']) > params['apr_min'] / 100 \
        and min(pool['totalApr']['month'], pool['totalApr']['week']) < params['apr_max'] / 100 \
        and pool['tvl'] > params['tvl_min'] * 1000:
            return True
    return False

def pool_dict_orca(pool):
    week_or_month = 'week' if pool['totalApr']['week'] < pool['totalApr']['month'] else 'month'
    return {
        'platform': 'Orca',
        'pool': f"{pool['tokenA']['symbol']}-{pool['tokenB']['symbol']}",
        'apr': pool['totalApr'][week_or_month],
        'fee': pool['lpFeeRate'],
        'tvl': pool['tvl'],
        'volume': pool['volume'][week_or_month],
        'week_or_month': week_or_month,
        'tokenA': pool['tokenA']['mint'],
        'tokenB': pool['tokenB']['mint'],
        'symbolA': pool['tokenA']['symbol'],
        'symbolB': pool['tokenB']['symbol'],
    }

def pool_filter(pools, filter):
    return [p for p in pools \
            if filter.lower() == p['symbolA'].lower() \
            or filter.lower() == p['symbolB'].lower()]

def pool_print(p, verbose):
    print (f"""
    {p['pool']} - {p['platform']} - {p['week_or_month']}ly
    APR: {p['apr']:>14.0%}
    fee: {p['fee']:>14.2%}
    TVL: {p['tvl'] / 1000:>13,.0f} kUSD
    volume: {p['volume'] / 1000:>10,.0f} kUSD""")

    if verbose:
        print(f"        tokenA: {p['tokenA']}")
        print(f"        tokenB: {p['tokenB']}")

def my_key(is_tvl):
    return lambda p: p['apr'] * log10(p['tvl']) if is_tvl else p['apr']

def main():
    args = get_args()
    pools = get_orca_pools(args.risk_off, args.filter)
    pools.sort(key = my_key(args.tvl), reverse=True)

    for p in pools[:args.display_limit]:
        pool_print(p, args.verbose)

if __name__ == '__main__':
    main()
