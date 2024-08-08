#!./venv/bin/python
# coding: utf-8

from config import args
from orca_pools import get_orca_pools, pool_print, my_key
from raydium_pools import get_rayd_pools
from tokenlist import token_list_age, get_tokenlist

def main():
    age = token_list_age()
    if age > 7:
        print('The token list was updated more than a week ago. It is being updtated now...')
        get_tokenlist() 

    orca_pools = get_orca_pools()
    rayd_pools = get_rayd_pools()
    
    pools = orca_pools + rayd_pools
    pools.sort(key = my_key(), reverse=True)

    for p in pools[:args.display_limit]:
        pool_print(p)

if __name__ == '__main__':
    main()