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

    





