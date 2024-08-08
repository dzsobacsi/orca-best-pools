#!./venv/bin/python
# coding: utf-8

from config import args, params, tokens
import requests
from orca_pools import isgood_token, my_key, pool_filter, pool_print


def isgood_pool_rayd(pool):
    min_tvl = 0 if args.tvl_limit_off else params['tvl_min'] * 1000

    if not (
            pool.get('week', {}).get('apr', False) \
        and pool.get('month', {}).get('apr', False)):
            return False
    
    if      isgood_token(pool['mintA']['address']) \
        and isgood_token(pool['mintB']['address']) \
        and min(pool['week']['apr'], pool['month']['apr']) > params['apr_min'] \
        and min(pool['week']['apr'], pool['month']['apr']) < params['apr_max'] \
        and pool['tvl'] > min_tvl:
            return True
    
    return False


def pool_dict_rayd(pool):
    apr = {
        'week':  pool['week']['apr'],
        'month': pool['month']['apr']
    }
    week_or_month = 'week' if apr['week'] < apr['month'] else 'month'
    return {
        'platform': 'Raydium',
        'pool': f"{tokens[pool['mintA']['address']]}-{tokens[pool['mintB']['address']]}",
        'apr': apr[week_or_month] / 100,
        'fee': pool['feeRate'],
        'tvl': pool['tvl'],
        'volume': pool[week_or_month]['volume'],
        'week_or_month': week_or_month,
        'tokenA': pool['mintA']['address'],
        'tokenB': pool['mintB']['address'],
        'symbolA': tokens[pool['mintA']['address']],
        'symbolB': tokens[pool['mintB']['address']],
        'address': pool['id'],
    }


def get_rayd_pools():
    pools = requests.get(params['raydium_url']).json()['data']['data']
    pools = [pool_dict_rayd(p) for p in pools if isgood_pool_rayd(p)]
    if args.filter:
        pools = pool_filter(pools)
    return pools


def main():
    pools = get_rayd_pools()
    pools.sort(key = my_key(), reverse=True)

    for p in pools[:args.display_limit]:
        pool_print(p)


if __name__ == '__main__':
    main()