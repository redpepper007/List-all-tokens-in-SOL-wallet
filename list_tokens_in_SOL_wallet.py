from solders.pubkey import Pubkey  #type: ignore
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TokenAccountOpts
import asyncio
from solana.rpc.api import Client
import requests
import aiohttp
import time
import os
os.system('color'); green = '\033[32m'; red = '\033[31m'; yellow = '\033[33m'; reset = '\033[0m'
tokens_in_wallet = []
trash_tokens_in_wallet = []

async def fetch_symbol(token_address):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.dexscreener.com/latest/dex/tokens/{token_address}") as response:
            try:
                if response.status == 200:
                    data = await response.json() 
                    symbol = data['pairs'][0]['baseToken']['symbol']
                    price = float(data['pairs'][0]['priceUsd']) 
                    return symbol, price
                else:
                    print(f"Failed to fetch data for {token_address}, status code: {response.status}")
                    return None
            except Exception:
                return "not_found",0

async def get_tokens_in_wallet(wallet_address: str):
        SOLANA_ENDPOINT = 'https://api.mainnet-beta.solana.com'
        SOL_PROGRAM_ID  = 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA'

        payload = {'jsonrpc': '2.0','id': 1,'method': 'getTokenAccountsByOwner','params': [f'{wallet_address}',{'programId': f'{SOL_PROGRAM_ID}'},{'encoding': 'jsonParsed'}]}
        response = requests.post(SOLANA_ENDPOINT, json=payload)
        jsondata = response.json()

        if 'result' in jsondata and 'value' in jsondata['result']:
            for token in jsondata['result']['value']:
                mint = token['account']['data']['parsed']['info']['mint']
                amount = token['account']['data']['parsed']['info']['tokenAmount']['uiAmount']
                decimals = token['account']['data']['parsed']['info']['tokenAmount']['decimals']
                symbol, price = await fetch_symbol(mint)
                value = float(amount*price)
                if value > 0.01:
                    print(f"[ {symbol:<10} ] [ {mint:<45} ] ${value:1.2f}")
                    tokens_in_wallet.append(symbol)
                else: trash_tokens_in_wallet.append(symbol)
                
        return tokens_in_wallet

async def main():
    print(f'\nWorking...\n')
    await get_tokens_in_wallet(WALLET_ADDRESS)
    print(f"\n{green}Total {len(tokens_in_wallet) + len(trash_tokens_in_wallet)} tokens found in {WALLET_ADDRESS}\n\tof which {len(trash_tokens_in_wallet)} are below $0.01{reset}\n")
    print('Done')
    time.sleep(999)

# Run the async function:
print(f"\n{green}Script will list all the tokens inside SOL wallet of your choice{reset}\n")
WALLET_ADDRESS = input('> Enter SOL wallet address: ')
asyncio.run(main())
