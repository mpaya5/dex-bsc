import pandas as pd
import numpy as np
from web3 import Web3
import time

from blockchain.account.account import CryptoAccount
from blockchain.utils.analyzer import CryptoAnalyzer
from blockchain.utils.logger import AppLogger
logger = AppLogger('my_app')

from config import min_amount_sell, max_price_impact, volumen_percentage, times_current_exc, offset_blocks, query_time_seconds,deadline_sum 

from utils import get_unix_time_now, get_surplus_token, get_price_impact, get_sniping, approve_token

import os
from dotenv import load_dotenv
load_dotenv()

addresses = os.getenv("ADDRESSES")
skeys = os.getenv("SKEYS")
support = os.getenv('SUPPORT')


# Approve token for each account of your addresses
""" for i in range(len(accounts)):
     sb, chain = get_sniping()
     approve_token(chain, accounts[i])
     time.sleep(5) """

def sell(sb, chain, accounts, buy_pressure_sell):
    """
    IDEA TO YOU:
    Within the sell(sb, chain) function, a series of operations are carried out to perform the sale of cryptocurrencies. Below is the code flow explanation:

    - The current block number is obtained, and a block range is calculated for calculations related to the token surplus.
    - The get_surplus_token function is called to calculate the token surplus between the specified blocks.
    - sb.get_current_exchange_rate() is used to obtain the current exchange rate.
    - The amount of token and BUSD to sell is calculated based on the token surplus and the exchange rate.
    - If the amount of BUSD to sell exceeds the minimum threshold (min_amount_sell), the price impact is calculated using the get_price_impact function.
    - If the price impact is below the maximum threshold (max_price_impact), a minimum exchange rate is calculated, and a random crypto account is selected.
    - Transaction parameters are configured, and the sale is executed using the sb.buy function.
    - The program runs in an infinite loop (while True) to continuously perform sale operations. In case an exception occurs during execution, the error is captured, displayed in the output, and a wait time is applied before continuing the loop.
    """
    # This function needs to be completed for you 
    pass


def run_loop():
    logger.info('We start our service')
    while True:
        try:
            # This is an example, using my CryptoAnalyzer
            analyzer = CryptoAnalyzer()
            analyzer.collect_close_prices()
            analyzer.calculate_percentages()
            result = analyzer.analyze()

            if result[0] == True:
                accounts = []

                pk = Web3.to_checksum_address(addresses)
                sk = skeys + support
                crypto_account = CryptoAccount(pk, sk)
                accounts.append(crypto_account)
                try:
                    sb, chain = get_sniping()
                    sell(sb, chain, accounts, result[1])
                except Exception as e:
                    logger.error(f"ERROR: {e}")
            else:
                pass
        
        except Exception as e:
            logger.error(f"ERROR: {e}")

        time.sleep(60)