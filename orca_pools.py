#!/usr/bin/python3
# coding: utf-8
'''#!/usr/bin/env python'''

import requests
import sys

include  = [
    'usd', 'eur', 'sol', 'eth', 'btc', 'uxd', 'cad', 'chf', 'xau', 'hbb', 'dai',
    'lst', 'jup', 'rndr', 'link', 'grt', 'hnt', 'pyth', 'jlp'
]
exclude = [
    'solape', 'sols', 'solzilla', 'solfnd', 'solama', 'solana', 'sobtc', 
    'solnic', 'solbird', 'sole', 'mockjup', 'solami', 'solsponge', 'solcade', 
    'solamo', 'plink', 'gst-sol', 'soladog', 'solbro'
]
url = 'https://api.mainnet.orca.so/v1/whirlpool/list'
apr_threshold = 75   # in %
tvl_threshold = 5    # in kUSD
default_display_limit = 10

def isgood_token(token):
    sym = token['symbol'].lower()
    for i in include:
        if i.lower() in sym and sym not in exclude:
            return True
    return False

def isgood_pool(pool):
    if not (pool.get('totalApr', {}).get('month', 0) and pool.get('totalApr', {}).get('week', 0)):
        return False
    if      isgood_token(pool['tokenA']) \
        and isgood_token(pool['tokenB']) \
        and min(pool['totalApr']['month'], pool['totalApr']['week']) > apr_threshold / 100 \
        and pool['tvl'] > tvl_threshold * 1000:
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
        'week_or_month': week_or_month
    }

def main():
    display_limit = int(sys.argv[1]) if len(sys.argv) > 1 else default_display_limit

    pools = requests.get(url).json()['whirlpools']
    pools = [p for p in pools if isgood_pool(p)][:display_limit]
    pools = [pool_dict(p) for p in pools]
    pools.sort(key = lambda p: p['apr'], reverse=True)

    for p in pools:
        print (f"""
        {p['pool']} - {p['week_or_month']}ly
        APR: {p['apr']:>14.0%}
        fee: {p['fee']:>14.2%}
        TVL: {p['tvl'] / 1000:>13,.0f} kUSD
        volume: {p['volume'] / 1000:>10,.0f} kUSD""")

if __name__ == '__main__':
    main()
