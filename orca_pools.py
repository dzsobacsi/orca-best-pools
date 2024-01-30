#!/usr/bin/python3
# coding: utf-8
'''#!/usr/bin/env python'''

import requests
import sys

pools = requests.get('https://api.mainnet.orca.so/v1/whirlpool/list').json()['whirlpools']
include  = ['usd', 'eur', 'sol', 'eth', 'btc', 'uxd', 'cad', 'chf', 'xau']
exclude = ['solape', 'sols', 'solzilla', 'solfnd', 'solama', 'solana', 'sobtc', 'solnic']
apr_threshold = 100  # in %
tvl_threshold = 1    # in kUSD
display_limit = int(sys.argv[1]) if len(sys.argv) > 1 else 6

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


good_pools = [p for p in pools if isgood_pool(p)]

good_pools = [{
    'pool': f"{p['tokenA']['symbol']}-{p['tokenB']['symbol']}",
    'fee': p['lpFeeRate'],
    'tvl': p['tvl'],
    'apr': min(p['totalApr']['month'], p['totalApr']['week']),
    'volume': min(p['volume']['month'], p['volume']['week'])
} for p in good_pools]

good_pools.sort(key = lambda p: p['apr'], reverse=True)

for p in good_pools[:display_limit]:
    print (f"""
        {p['pool']}
        APR: {round(p['apr'] * 100)}%
        fee: {p['fee'] * 100}%
        TVL: {round(p['tvl'] / 1000)} kUSD
        volume: {round(p['volume'] / 1000)} kUSD"""
    )
