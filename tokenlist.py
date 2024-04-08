import requests
import pandas as pd

def get_tokenlist():
    url = 'https://api.mainnet.orca.so/v1/whirlpool/list'
    pools = requests.get(url).json()['whirlpools']
    tokens = {}

    for p in pools:
        if p['tokenA']['mint'] not in tokens:
            tokens[p['tokenA']['mint']] = p['tokenA']['symbol']

        if p['tokenB']['mint'] not in tokens:
            tokens[p['tokenB']['mint']] = p['tokenB']['symbol']

    df_dir = {
        'symbol': [],
        'address': []
    }

    for k, v in tokens.items():
        df_dir['symbol'].append(v)
        df_dir['address'].append(k)

    df = pd.DataFrame(df_dir)
    df = df.dropna()
    df = df[df['symbol'].apply(lambda x: x.isalnum() and len(x) <= 10)]

    df.to_csv('tokens.csv', index=False)
    print(f'{df.shape[0]} tokens were found and saved to tokens.csv.')

if __name__ == '__main__':
    get_tokenlist()