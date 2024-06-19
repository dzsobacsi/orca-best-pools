#!./venv/bin/python
# coding: utf-8

import requests
from orca_pools import *

def isgood_pool_rayd(pool, risk_off):
    if not (
            pool.get('week', {}).get('feeApr', 0) \
        and pool.get('month', {}).get('feeApr', 0)):
            return False
    
    if      isgood_token(pool['mintA'], risk_off=risk_off) \
        and isgood_token(pool['mintB'], risk_off=risk_off) \
        and min(pool['week']['feeApr'], pool['month']['feeApr']) > params['apr_min'] / 100 \
        and min(pool['week']['feeApr'], pool['month']['feeApr']) < params['apr_max'] / 100 \
        and pool['tvl'] > params['tvl_min'] * 1000:
            return True
    return False

def pool_dict_rayd(pool):
    apr = {
        'week':  pool['week']['feeApr']  + sum(pool['week']['rewardApr'].values()),
        'month': pool['month']['feeApr'] + sum(pool['month']['rewardApr'].values()),
    }
    week_or_month = 'week' if apr['week'] < apr['month'] else 'month'
    return {
        'platform': 'Raydium',
        'pool': f"{tokens[pool['mintA']]}-{tokens[pool['mintB']]}",
        'apr': apr[week_or_month] / 100,
        'fee': pool['ammConfig']['tradeFeeRate'] / 1000000,
        'tvl': pool['tvl'],
        'volume': pool[week_or_month]['volume'],
        'week_or_month': week_or_month,
        'tokenA': pool['mintA'],
        'tokenB': pool['mintB'],
        'symbolA': tokens[pool['mintA']],
        'symbolB': tokens[pool['mintB']],
    }

def get_rayd_pools(risk_off, filter):
    pools = requests.get(params['raydium_url']).json()['data']
    pools = [pool_dict_rayd(p) for p in pools if isgood_pool_rayd(p, risk_off=risk_off)]
    if filter:
        pools = pool_filter(pools, filter)
    return pools


def main():
    args = get_args()
    pools = get_rayd_pools(args.risk_off, args.filter)
    pools.sort(key = my_key(args.tvl), reverse=True)

    for p in pools[:args.display_limit]:
        pool_print(p, args.verbose)

if __name__ == '__main__':
    main()