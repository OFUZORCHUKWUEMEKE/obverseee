import requests
import json
from typing import Dict, Any, Optional
from solana.rpc.api import Client
from solana.keypair import Keypair
from solana.transaction import Transaction
from solders.pubkey import Pubkey
import base64
import time
import os
from dotenv import load_dotenv

load_dotenv()


class JupiterSwap:
    """
    A class to swap SOL for USDC/USDT using Jupiter API on Solana
    """
    def __init__(self):
        """
          Initialize the Jupiter swapper
          Args:
            rpc_url: Solana RPC endpoint URL
        """
        self.rpc_url = os.getenv("SOLANA_RPC_URL")
        self.client = Client(rpc_url)
        self.jupiter_base_url = "https://quote-api.jup.ag/v6"

         # Token addresses
        self.tokens = {
            "SOL": "So11111111111111111111111111111111111111112",
            "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            "USDT": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB"
        }

    def get_quote(self,input_mint: str, output_mint: str, amount: int, slippage_bps: int = 50)->Dict:
         """
        Get a quote for swapping tokens
        Args:
            input_mint: Input token mint address
            output_mint: Output token mint address
            amount: Amount in smallest unit (lamports for SOL)
            slippage_bps: Slippage in basis points (50 = 0.5%)
            
        Returns:
            Quote data or None if failed
        """
         try:
            url = f"{self.jupiter_base_url}/quote"
            params = {
                "inputMint": input_mint,
                "outputMint": output_mint,
                "amount": amount,
                "slippageBps": slippage_bps,
                "onlyDirectRoutes": "false",
                "asLegacyTransaction": "false"
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
         except requests.exceptions.RequestException as e:
            print(f"Error getting quote: {e}")
            return None

    def get_swap(self, quote: Dict, user_public_key: str)->Optional[str]:
        """
           Get swap transaction from Jupiter        
           Args:
               quote: Quote data from get_quote
               user_public_key: User's wallet public key as string
           Returns:
               Serialized transaction or None if failed
        """
        try:
            url = f"{self.jupiter_base_url}/swap"
            params = {
                "quote": quote,
                "userPublicKey": user_public_key,
                "wrapAndUnwrapSol": True,
                "dynamicComputeUnitLimit": True,
                "prioritizationFeeLamports": "auto"
            }
            response = requests.post(url, json=params,headers={"Content-Type": "application/json"})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting swap: {e}")

    def execute_swap(self,keypair:Keypair,swap_transaction:str)->Optional[str]:
        """
        Execute the swap transaction
        Args:
          keypair: User's Solana Keypair
          swap_transaction: Serialized transaction from get_swap
        Returns:
          Transaction signature or None if failed
        """
        try:
            transaction_bytes = base64.b64decode(swap_transaction)
            transation = Transaction.deserialize(transaction_bytes)
            # sign transaction
            transaction.sign(keypair)
            # send transaction
            response = self.client.send_transaction(transation)
            if response.value:
                print(f"Transaction sent: {response.value}")
                return response.value
            else:
                print(f"Transaction failed to send")
                return None
        except Exception as e:
            print(f"Error executing swap: {e}")
            return None

    def swap_sol_to_usdc(self,keypair:Keypair,sol_amount:float,slippage_bps:int=50)->Optional[str]:
        """
        Swap SOL to USDC
        Args: 
          Keypair : User's Solana keypair
          sol_amount: Amount of SOL to swap
          slippage_bps: Slippage in basis points (50 = 0.5%)

        Returns:
          Transaction signature or None if failed
        """
        print(f"Swapping {sol_amount} SOL for USDC")
        sol_amount_lamports = int(sol_amount * 10**9)
        quote = self.get_quote(self.tokens["SOL"], self.tokens["USDC"], sol_amount_lamports, slippage_bps)
        if not quote:
            return None
        swap_transaction = self.get_swap(quote, str(keypair.pubkey()))
        if not swap_tx:
            return None
        return self.execute_swap(keypair,swap_transaction)
    
    def swap_sol_to_usdt(self,keypair:Keypair,sol_amount:float,slippage_bps:int=50)->Optional[str]:
        """
        Swap SOL to USDT
        Args: 
          Keypair : User's Solana keypair
          sol_amount: Amount of SOL to swap
          slippage_bps: Slippage in basis points (50 = 0.5%)
        Returns:
          Transaction signature or None if failed
        """
        print(f"Swapping {sol_amount} SOL for USDT...")
        lamports = int(sol_amount * 1_000_000_000)
        # Get quote
        quote = self.get_quote(
            self.tokens["SOL"],
            self.tokens["USDT"],
            lamports,
            slippage_bps
        )
        if not quote:
            return None
        print(f"Quote received: ~{float(quote['outAmount']) / 1_000_000:.2f} USDT") 
        # Get swap transaction
        swap_tx = self.get_swap_transaction(quote, str(keypair.pubkey()))        
        if not swap_tx:
            return None       
        # Execute swap
        return self.execute_swap(keypair,swap_tx)

    def get_token_balance(self,wallet_addressLstr,token_mint:str)->float:
        """
          Get token balance for a wallet
        Args:
            wallet_address: Wallet public key as string
            token_mint: Token mint address
        Returns:
            Token balance
        """
        try:
            if token_mint == self.tokens["SOL"]:
                # Get SOL balance
                response = self.client.get_balance(Pubkey.from_string(wallet_address))
                return response.value / 1_000_000_000  # Convert lamports to SOL
            else:
                # Get SPL token balance
                response = self.client.get_token_accounts_by_owner(
                    Pubkey.from_string(wallet_address),
                    {"mint": Pubkey.from_string(token_mint)}
                )
                if response.value:
                    account_info = self.client.get_account_info(response.value[0].pubkey)
                    # Parse token account data (simplified)
                    return 0.0  # You'd need to properly parse the account data
                else:
                    return 0.0
        except Exception as e:
            print(f"Error getting balance: {e}")
            return 0.0


    





