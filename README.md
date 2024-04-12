A Python script selecting and printing the best concentrated liquidity pools on Orca and Raydium (Solana). Selection is based on my own arbitrary taste: Non-shitcoin pools with high APR and some reasonable TVL.

usage: best_pools.py [-h] [-v] [-t] [-r] [-f FILTER] [-d DISPLAY_LIMIT]

Best Pools - selection of the best liquidity pools on Solana

options:

  -h, --help            show this help message and exit

  -v, --verbose         In verbose mode, you can also see the tokens' addresses

  -t, --tvl             Sorts the pools by sqrt(TVL)*APR instead of APR

  -r, --risk-off        In risk-off mode, only lower risk pools are listed

  -f FILTER, --filter FILTER
                        Filter the pools by token symbol

  -d DISPLAY_LIMIT, --display-limit DISPLAY_LIMIT
                        Set the number of pools to display
