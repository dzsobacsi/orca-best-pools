import argparse
import csv
from icecream import ic
import requests
import yaml

url = 'https://api.raydium.io/v2/ammV3/ammPools'

with open('parameters.yaml') as f:
    params = yaml.safe_load(f)

with open('tokens.csv') as f:
    reader = csv.DictReader(f)
    tokens = {row['address']: row['symbol'] for row in reader}

def get_args():
    parser = argparse.ArgumentParser(
        description="Raydium Pools - selection of the best pools on Raydium")
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


def isgood_pool(pool, risk_off):
    if not (
            pool.get('week', {}).get('feeApr', 0) \
        and pool.get('month', {}).get('feeApr', 0)):
            return False
    
    if      isgood_token(pool['mintA'], risk_off=risk_off) \
        and isgood_token(pool['mintB'], risk_off=risk_off) \
        and min(pool['week']['feeApr'], pool['month']['feeApr']) > params['apr_min'] \
        and min(pool['week']['feeApr'], pool['month']['feeApr']) < params['apr_max'] \
        and pool['tvl'] > params['tvl_min'] * 1000:
            return True
    return False

def pool_dict(pool):
    apr = {
        'week':  pool['week']['feeApr']  + sum(pool['week']['rewardApr'].values()),
        'month': pool['month']['feeApr'] + sum(pool['month']['rewardApr'].values()),
    }
    week_or_month = 'week' if apr['week'] < apr['month'] else 'month'
    return {
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

def my_key(is_tvl):
    return lambda p: p['apr'] * p['tvl'] ** 0.5 if is_tvl else p['apr']

def main():
    args = get_args()

    pools = requests.get(url).json()['data']
    pools = [pool_dict(p) for p in pools if isgood_pool(p, risk_off=args.risk_off)]

    if args.filter:
        pools = [p for p in pools \
                if args.filter.lower() == p['symbolA'].lower() \
                or args.filter.lower() == p['symbolB'].lower()]
        
    pools.sort(key = my_key(args.tvl), reverse=True)

    ic(pools[:args.display_limit])

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