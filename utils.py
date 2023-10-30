import pandas as pd
from datetime import datetime

import boto3
s3 = boto3.resource('s3', region_name='ap-southeast-2')
import base64
import json

import os
from dotenv import load_dotenv
load_dotenv()

addressPancake = os.getenv('ADDRESS_PANCAKE')
addressToken = os.getenv('ADDRESS_TOKEN')
addressPair = os.getenv('ADDRESS_PAIR')
addressOut = os.getenv('ADDRESS_OUT')

from web3 import Web3
import pandas as pd
from decimal import Decimal

from blockchain.chains.chains import BinanceSmartChain

from blockchain.contracts.interfaces.erc20 import ERC20Contract
from blockchain.contracts.dex.pancake_contract import PancakeContract

from blockchain.api.scanners import Bscscan

from blockchain.utils.logger import AppLogger
logger = AppLogger('my_app')

from blockchain.utils.utils import send_transaction
from blockchain.utils.chain_utils import get_chain
from blockchain.utils.web3_utils import format_address
from blockchain.utils.kmsaws import AWSKMS

from blockchain.bots.pancake_bot import SnipeBotPancake

def load_df(df_path):
    return pd.read_csv(df_path)

def add_row(df, tx_hash, from_, token_amount, busd_amount, exchange_rate_min):
    d = {}
    d['tx_hash'] = tx_hash
    d['from'] = from_
    d['token_amount'] = token_amount
    d['busd_amount'] = busd_amount
    d['exchange_rate_min'] = exchange_rate_min
    d['timestamp'] = str(datetime.now())[:10]
    return pd.concat([df, pd.DataFrame([d])])

def save_df(df, df_path):
    df.to_csv(df_path, index=False)

def get_unix_time_now():
    return int(datetime.timestamp(datetime.now()))

def get_last_block_number(chain):
    return chain.w3.eth.block_number

def get_connection():
    # connect to chain and set gwei
    max_gwei = 5
    fast_gwei = 1
    chain = BinanceSmartChain()
    chain.set_gwei_config(max_gwei, fast_gwei)
    return chain

def get_balances(chain, t_in, t_out, pk):
    logger.info("Current balance: {} TOKEN".format(t_in.get_balance(pk) / 1e18 / 1e6))
    logger.info("Current balance: {} BUSD".format(t_out.get_balance(pk) / 1e18))
    logger.info("BNB available : {}".format(chain.w3.eth.get_balance(pk) / 1e18))

def approve_token(chain, crypto_account):
    #approve token in
    approve_amount_in = 500000000
    address_pancake =  Web3.to_checksum_address(addressPancake)
    token_address_in = Web3.to_checksum_address(addressToken) 
    t_in = ERC20Contract(chain, token_address_in)

    amount = int(approve_amount_in * 10**18)
    signed_tx = t_in.approve_if_not_approved(crypto_account, address_pancake, amount)
    if signed_tx is not None:
        tx_receipt = send_transaction(chain, signed_tx)
        logger.info("Approve TOKEN: {}".format(tx_receipt))
        return

# get price impact on price
def get_price_impact(sb, amount_in_token):
    exc_now = sb.get_current_exchange_rate()
    exc_future = sb.get_affected_exchange_rate(amount_in=amount_in_token)
    price_impact = 1 - exc_future / exc_now
    return price_impact
    
    
def get_sniping():
    chain = get_chain('binance-smart-chain')
    address_pancake = format_address(addressPancake)
    pc = PancakeContract(chain, address_pancake)

    token_address_in = format_address(addressToken) 
    t_in = ERC20Contract(chain, token_address_in)

    token_address_out = format_address(addressOut) 
    t_out = ERC20Contract(chain, token_address_out)

    path = [token_address_in, token_address_out]
    sb = SnipeBotPancake(pc, token_contract_in=t_in, token_contract_out=t_out, path=path)
    return sb, chain

def get_surplus_token(start_block, end_block):
    pair_address = addressPair
    address_token_busd = format_address(pair_address) 

    scanner = Bscscan()
    txs = scanner.get_erc20_transactions(address_token_busd, start_block, end_block, page=1, offset=10000, sort='desc')
    # logger.info(txs)

    df_transfers = pd.DataFrame(txs['result'])
    surplus_token = 0
    vol_token = 0

    if len(df_transfers) > 0:
        columns=['from','to','value','contractAddress','hash']
        df_transfers = df_transfers[columns]

        df_transfers = df_transfers[df_transfers['contractAddress'] == addressToken]
        df_transfers['value'] = df_transfers['value'].astype(float) / 1e18

        buy = df_transfers[(df_transfers['from'] == pair_address) & (df_transfers['to'] != pair_address)]
        sold = df_transfers[(df_transfers['from'] != pair_address) & (df_transfers['to'] == pair_address)]
    
        vol_token = buy['value'].sum() + sold['value'].sum()
        surplus_token = buy['value'].sum() - sold['value'].sum()
    return [surplus_token, vol_token]