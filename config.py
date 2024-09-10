import yaml
import argparse
import csv

def load_params(file_path='parameters.yaml'):
    with open(file_path) as f:
        return yaml.safe_load(f)

def load_tokens(file_path='tokens.csv'):
    with open(file_path) as f:
        reader = csv.DictReader(f)
        return {row['address']: row['symbol'] for row in reader}

def get_args(params):
    parser = argparse.ArgumentParser(
        description="Best Pools - selection of the best liquidity pools on Solana")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Display detailed information including pool and token addresses")
    parser.add_argument("-t", "--tvl-weighted-sort", action="store_true", 
                        help="Sort pools by log(TVL) * APR instead of just APR")
    parser.add_argument("--disable-tvl-limit", action="store_true",
                        help="Show all pools regardless of the TVL limit")
    parser.add_argument("-r", "--risk-off", action="store_true", 
                        help="List only lower risk pools")
    parser.add_argument("-f", "--filter", type=str, 
                        help="Filter pools by token symbol")
    parser.add_argument("-d", "--display-limit", type=int, 
                        default=params['default_display_limit'],
                        help="Set the maximum number of pools to display")
    return parser.parse_args()

params = load_params()
tokens = load_tokens()
args = get_args(params)