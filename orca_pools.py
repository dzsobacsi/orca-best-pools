#!./venv/bin/python
# coding: utf-8

from config import args, params, tokens
from math import log10
import requests


def get_orca_pools():
    pools = requests.get(params['orca_url']).json()['whirlpools']
    pools = [pool_dict_orca(p) for p in pools if isgood_pool_orca(p)]
    if args.filter:
        pools = pool_filter(pools)
    return pools


def isgood_token(addr):
    if addr not in tokens:
        return False
    
    sym = tokens[addr].lower()

    if not args.risk_off and addr in params['risk_include']:
        return True
    
    for i in params['include']:
        if i.lower() in sym \
            and sym not in params['exclude'] \
            and addr not in params['addr_exclude']:
                return True
    return False


def isgood_pool_orca(pool):
    min_tvl = 0 if args.disable_tvl_limit else params['tvl_min'] * 1000

    if not (
            pool.get('totalApr', {}).get('month', 0) \
        and pool.get('totalApr', {}).get('week', 0)):
            return False
    
    if      isgood_token(pool['tokenA']['mint']) \
        and isgood_token(pool['tokenB']['mint']) \
        and min(pool['totalApr']['month'], pool['totalApr']['week']) > params['apr_min'] / 100 \
        and min(pool['totalApr']['month'], pool['totalApr']['week']) < params['apr_max'] / 100 \
        and pool['tvl'] > min_tvl:
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
        'address': pool['address'],
    }


def pool_filter(pools):
    return [p for p in pools \
            if args.filter.lower() == p['symbolA'].lower() \
            or args.filter.lower() == p['symbolB'].lower()]


def pool_print(p):
    print (f"""
    {p['pool']} - {p['platform']} - {p['week_or_month']}ly
    APR: {p['apr']:>14.0%}
    fee: {p['fee']:>14.2%}
    TVL: {p['tvl'] / 1000:>13,.0f} kUSD
    volume: {p['volume'] / 1000:>10,.0f} kUSD""")

    if args.verbose:
        print(f"    token A:      {p['tokenA']}")
        print(f"    token B:      {p['tokenB']}")
        print(f"    pool address: {p['address']}")


def my_key():
    return lambda p: p['apr'] * log10(p['tvl']) if args.tvl_weighted_sort else p['apr']


def main():
    pools = get_orca_pools()
    pools.sort(key = my_key(), reverse=True)

    for p in pools[:args.display_limit]:
        pool_print(p)


if __name__ == '__main__':
    main()
