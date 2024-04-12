#!./venv/bin/python
# coding: utf-8

import argparse
import requests
import yaml

with open('parameters.yaml') as f:
    params = yaml.safe_load(f)

def get_args():
    parser = argparse.ArgumentParser(
        description="Orca Pools - selection of the best pools on Orca")
    parser.add_argument("-v", "--verbose", action="store_true",
                help="In verbose mode, you can also see the tokens' addresses")
    parser.add_argument("-t", "--tvl", action="store_true", 
                help="Sorts the pools by sqrt(TVL)*APR instead of APR")
    parser.add_argument("-r", "--risk-off", action="store_true", 
                help="In risk-off mode, only lower risk pools are listed")
    parser.add_argument("-f", "--filter", type=str, 
                help="Filter the pools by token symbol")
    parser.add_argument("-d", "--display-limit", type=int, 
                default=params['default_display_limit'],
                help="Set the number of pools to display")
    return parser.parse_args()

def isgood_token(token, risk_off):
    sym = token['symbol'].lower()
    addr = token['mint']

    if not risk_off and addr in params['risk_include']:
        return True
    
    for i in params['include']:
        if i.lower() in sym \
            and sym not in params['exclude'] \
            and addr not in params['addr_exclude']:
                return True
    return False

def isgood_pool(pool, risk_off):
    if not (
            pool.get('totalApr', {}).get('month', 0) \
        and pool.get('totalApr', {}).get('week', 0)):
            return False
    
    if      isgood_token(pool['tokenA'], risk_off=risk_off) \
        and isgood_token(pool['tokenB'], risk_off=risk_off) \
        and min(pool['totalApr']['month'], pool['totalApr']['week']) > params['apr_min'] / 100 \
        and min(pool['totalApr']['month'], pool['totalApr']['week']) < params['apr_max'] / 100 \
        and pool['tvl'] > params['tvl_min'] * 1000:
            return True
    return False

def pool_dict(pool):
    week_or_month = 'week' if pool['totalApr']['week'] < pool['totalApr']['month'] else 'month'
    return {
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

def my_key(is_tvl):
    return lambda p: p['apr'] * p['tvl'] ** 0.5 if is_tvl else p['apr']

def main():
    args = get_args()

    pools = requests.get(params['orca_url']).json()['whirlpools']
    pools = [pool_dict(p) for p in pools if isgood_pool(p, risk_off=args.risk_off)]

    if args.filter:
        pools = [p for p in pools \
                if args.filter.lower() == p['symbolA'].lower() \
                or args.filter.lower() == p['symbolB'].lower()]
        
    pools.sort(key = my_key(args.tvl), reverse=True)

    for p in pools[:args.display_limit]:
        print (f"""
        {p['pool']} - {p['week_or_month']}ly
        APR: {p['apr']:>14.0%}
        fee: {p['fee']:>14.2%}
        TVL: {p['tvl'] / 1000:>13,.0f} kUSD
        volume: {p['volume'] / 1000:>10,.0f} kUSD""")

        if args.verbose:
            print(f"        tokenA: {p['tokenA']}")
            print(f"        tokenB: {p['tokenB']}")

if __name__ == '__main__':
    main()
