from typing import Optional , List,Dict
from ..models.wallet import Wallet,Chain
from ..repositories.wallet import WalletRepository
import logging
from beanie.odm.fields import PydanticObjectId
from datetime import datetime
import logging
# from solana.keypair import Keypair
from solders.keypair import Keypair
from solders.pubkey import Pubkey
# from solana.publickey import PublicKey
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from dotenv import load_dotenv
from ..models.wallet import Token,Wallet,Chain,StableCoin
import bcrypt
import os

load_dotenv()

logger = logging.getLogger(__name__)

class WalletService:
    def __init__(self, wallet_repository: WalletRepository):
        self.repository = wallet_repository
        self.encrypt_private_key = os.getenv("ENCRYPTION_KEY")

    async def create_wallet(
        self,
        user_id: str,
        chain: Chain,
        address: str,
        encrypted_private_key: str
    ) -> Wallet:
        """
        Creates a new wallet for a user
        """
        existing_wallet = await self.repository.get_by_address(address)
        if existing_wallet:
            logger.warning(f"Wallet creation failed - address exists: {address}")
            raise ValueError("Wallet with this address already exists")

        wallet = Wallet(
            user_id=PydanticObjectId(user_id),
            chain=chain,
            address=address,
            encrypted_private_key=encrypted_private_key,
            created_at=datetime.utcnow(),
            tokens=[]
        )

        try:
            created_wallet = await self.repository.create(wallet)
            logger.info(f"Created new wallet {created_wallet.id} for user {user_id}")
            return created_wallet
        except Exception as e:
            logger.error(f"Failed to create wallet: {str(e)}")
            raise RuntimeError("Failed to create wallet") from e

    async def get_wallet(self, wallet_id: str) -> Optional[Wallet]:
        """
        Retrieves a wallet by its ID
        """
        try:
            return await self.repository.get_by_id(wallet_id)
        except Exception as e:
            logger.error(f"Error fetching wallet {wallet_id}: {str(e)}")
            raise RuntimeError("Failed to fetch wallet") from e

    async def get_user_wallets(
        self,
        user_id: str,
        chain: Optional[Chain] = None
    ) -> List[Wallet]:
        """
        Retrieves all wallets for a user, optionally filtered by chain
        """
        try:
            if chain:
                return await self.repository.get_by_user_and_chain(user_id, chain)
            return await self.repository.find_many({"user_id": ObjectId(user_id)})
        except Exception as e:
            logger.error(f"Error fetching wallets for user {user_id}: {str(e)}")
            raise RuntimeError("Failed to fetch user wallets") from e

    async def add_token_to_wallet(
        self,
        wallet_id: str,
        token_data: Dict
    ) -> Optional[Wallet]:
        """
        Adds a token to a wallet's token list
        """
        try:
            # Validate token data structure
            if not all(k in token_data for k in ['symbol', 'contract_address', 'decimals']):
                raise ValueError("Invalid token data structure")
            
            return await self.repository.add_token_to_wallet(wallet_id, token_data)
        except ValueError as e:
            logger.warning(f"Invalid token data: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error adding token to wallet {wallet_id}: {str(e)}")
            raise RuntimeError("Failed to add token to wallet") from e

    async def update_token_balance(
        self,
        wallet_id: str,
        token_symbol: str,
        new_balance: str
    ) -> Optional[Wallet]:
        """
        Updates the balance of a specific token in a wallet
        """
        try:
            wallet = await self.get_wallet(wallet_id)
            if not wallet:
                raise ValueError("Wallet not found")
            
            token_exists = any(t.symbol == token_symbol for t in wallet.tokens)
            if not token_exists:
                raise ValueError("Token not found in wallet")
            
            return await self.repository.update_token_balance(
                wallet_id,
                token_symbol,
                new_balance
            )
        except ValueError as e:
            logger.warning(f"Balance update validation failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error updating balance for {token_symbol} in wallet {wallet_id}: {str(e)}")
            raise RuntimeError("Failed to update token balance") from e

    async def get_wallet_balance_summary(
        self,
        wallet_id: str
    ) -> Dict[str, float]:
        """
        Returns a summary of all token balances in a wallet
        """
        try:
            wallet = await self.get_wallet(wallet_id)
            if not wallet:
                raise ValueError("Wallet not found")
            
            return {
                token.symbol: float(token.balance)
                for token in wallet.tokens
            }
        except ValueError as e:
            logger.warning(f"Balance summary failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error generating balance summary for wallet {wallet_id}: {str(e)}")
            raise RuntimeError("Failed to generate balance summary") from e

    async def get_wallets_with_token(
        self,
        user_id: str,
        token_symbol: str
    ) -> List[Wallet]:
        """
        Finds all wallets of a user that contain a specific token
        """
        try:
            return await self.repository.get_wallets_with_token(user_id, token_symbol)
        except Exception as e:
            logger.error(f"Error finding wallets with token {token_symbol} for user {user_id}: {str(e)}")
            raise RuntimeError("Failed to find wallets with token") from e

    async def update_encrypted_private_key(
        self,
        wallet_id: str,
        new_encrypted_key: str
    ) -> Optional[Wallet]:
        """
        Updates the encrypted private key for a wallet
        """
        try:
            return await self.repository.update(
                wallet_id,
                {"$set": {"encrypted_private_key": new_encrypted_key}}
            )
        except Exception as e:
            logger.error(f"Error updating private key for wallet {wallet_id}: {str(e)}")
            raise RuntimeError("Failed to update private key") from e

    async def delete_wallet(self, wallet_id: str) -> bool:
        """
        Deletes a wallet (soft delete implementation)
        """
        try:
            wallet = await self.get_wallet(wallet_id)
            if not wallet:
                raise ValueError("Wallet not found")
            
            # Instead of actual deletion, mark as inactive
            result = await self.repository.update(
                wallet_id,
                {"$set": {"is_active": False, "deleted_at": datetime.utcnow()}}
            )
            return result is not None
        except ValueError as e:
            logger.warning(f"Wallet deletion failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error deleting wallet {wallet_id}: {str(e)}")
            raise RuntimeError("Failed to delete wallet") from e

    def generate_encryption_key():
       """Generate and return a Fernet key"""
       return Fernet.generate_key()
    
    def encrypt_private_key(private_key: bytes) -> str:
       """Encrypt a private key using Fernet symmetric encryption"""
       return fernet.encrypt(private_key).decode('utf-8')

    def decrypt_private_key(encrypted_key: str) -> bytes:
       """Decrypt an encrypted private key"""
       return fernet.decrypt(encrypted_key.encode('utf-8'))
    

    async def create_solana_wallet(user_id:str)->Wallet:
        """
        Creates a new solana wallet , encypts the private key , and stores it in MongoDB

        Args:
           user_id:The ID of the user who owns this wallet

        Returns:
           Wallets: The created wallet document
           
        """
        keypair = Keypair()
        public_key = str(keypair.public_key)
        private_key = bytes(keypair.seed)

        encrypted_private_key = encrypted_private_key(private_key)
        usdc_token = Token(
           symbol=StableCoin.USDC,
           balance=0.0,
           contract_address="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
           decimals=6
        )
        usdt_token = Token(
            symbol=StableCoin.USDT,
            balance=0.0,
            contract_address="Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
            decimals=6
        )

        wallet = Wallet(
            user_id=user_id,
            chain=Chain.SOLANA,
            address=public_key,
            encrypted_private_key=encrypted_private_key,
            created_at=datetime.utcnow(),
            tokens=[usdc_token,usdt_token]
        )
        await wallet.insert()
        return wallet
 
