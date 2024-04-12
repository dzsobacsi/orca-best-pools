#!./venv/bin/python
# coding: utf-8

from orca_pools import get_args, get_orca_pools, pool_print, my_key
from raydium_pools import get_rayd_pools

def main():
    args = get_args()
    orca_pools = get_orca_pools(args.risk_off, args.filter)
    rayd_pools = get_rayd_pools(args.risk_off, args.filter)
    
    pools = orca_pools + rayd_pools
    pools.sort(key = my_key(args.tvl), reverse=True)

    for p in pools[:args.display_limit]:
        pool_print(p, args.verbose)

if __name__ == '__main__':
    main()