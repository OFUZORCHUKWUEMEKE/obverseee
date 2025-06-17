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
from cryptography.hazmat.backends import default_backend
from beanie.odm.fields import PydanticObjectId
from solana.rpc.api import Client
import bcrypt
import os
import base64

load_dotenv()

logger = logging.getLogger(__name__)

class WalletService:
    def __init__(self, wallet_repository: WalletRepository):
        self.repository = wallet_repository
        self.rpc = os.getenv("SOLANA_RPC_URL")
        # self.encrypt_private_key = os.getenv("ENCRYPTION_KEY")

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
    
    async def get_user_wallet(self,user_id,chain:Optional[Chain]=None)->Wallet:
        """
        Retrieves Single Wallet for a user
        """
        try:
            wallet = self.repository.get_single_user_wallet(user_id,chain)
            return wallet
        except Exception as e:
            logger.error(f"Error fetching wallet {user_id}: {str(e)}")
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
            return await self.repository.find_many({"user_id": PydanticObjectId(user_id)})
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
    
    def generate_fernet_key(self,password: str = None, salt: bytes = None) -> tuple:
        """
        Generate a Fernet encryption key.
    
        Args:
            password: If provided, generates key from password (otherwise random)
            salt: Salt for password derivation (random if None)
        
        Returns:
            tuple: (encryption_key, salt_used) if password, else (encryption_key,)
        """
        if password:
            salt = salt or os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            return key, salt
        else:
            return Fernet.generate_key(),    

    def generate_encryption_key():
       """Generate and return a Fernet key"""
       return Fernet.generate_key()
    
    def encrypt_private_key(self,keypair: Keypair, encryption_key: bytes) -> str:
        """
        Encrypt a Solana private key.
    
        Args:
            keypair: Keypair from solders library
            encryption_key: Fernet encryption key
        
        Returns:
            str: Base64 encoded encrypted private key
        """
        fernet = Fernet(encryption_key)
        private_key_bytes = bytes(keypair)
        encrypted = fernet.encrypt(private_key_bytes)
        return base64.b64encode(encrypted).decode('utf-8')

    def decrypt_to_keypair(self,encrypted_key: str, encryption_key: bytes) -> Keypair:
        """
        Decrypt an encrypted private key back to Keypair.
    
        Args:
            encrypted_key: Base64 encoded encrypted private key
            encryption_key: Fernet encryption key used to encrypt
        
        Returns:
            Keypair: Restored Solana keypair
        """
        fernet = Fernet(encryption_key)
        encrypted_bytes = base64.b64decode(encrypted_key.encode('utf-8'))
        private_key_bytes = fernet.decrypt(encrypted_bytes)
        return Keypair.from_bytes(private_key_bytes)
    
    def generate_new_keypair(self,encryption_key: bytes) -> tuple:
        """
        Generate new keypair and return both keypair and encrypted private key.
        Args:
            encryption_key: Fernet encryption key
        Returns:
            tuple: (Keypair, encrypted_private_key_str)
        """
        keypair = Keypair()
        encrypted = self.encrypt_private_key(keypair, encryption_key)
        return keypair, encrypted    

    async def restore_keypair_from_wallet(self, wallet_id: str, password: str = "my-strong-password-123") -> Keypair:
       """
       Restore a Solana keypair from an encrypted private key stored in a wallet.
    
       Args:
           wallet_id: The ID of the wallet containing the encrypted private key
           password: The password used to derive the encryption key (should match creation password)

       Returns:
           Keypair: The restored Solana keypair
    
       Raises:
           ValueError: If wallet not found or decryption fails
           RuntimeError: If there's an error fetching the wallet
       """
       try:
           # Get the wallet from database
           wallet = await self.get_wallet(wallet_id)
           if not wallet:
            raise ValueError("Wallet not found")
        
           # Derive the encryption key using the same password and method as creation
           # Note: In production, you should store the salt with the wallet or derive it consistently
           salt = b"obverse-109/*767^&%^%"  # In production, store this with the wallet
           derived_key, _ = self.generate_fernet_key(password=password, salt=salt)
        
           # Decrypt the private key to restore the keypair
           restored_keypair = self.decrypt_to_keypair(wallet.encrypted_private_key, derived_key)
        
           # Verify the restored keypair matches the wallet address
           if str(restored_keypair.pubkey()) != wallet.address:
               raise ValueError("Restored keypair does not match wallet address")
        
           logger.info(f"Successfully restored keypair for wallet {wallet_id}")
           return restored_keypair
        
       except ValueError as e:
            logger.warning(f"Keypair restoration failed: {str(e)}")
            raise
       except Exception as e:
            logger.error(f"Error restoring keypair for wallet {wallet_id}: {str(e)}")
            raise RuntimeError("Failed to restore keypair") from e

    async def restore_keypair_from_encrypted_key(self, encrypted_private_key: str, password: str = "my-strong-password-123", salt: bytes = None) -> Keypair:
        """
        Restore a Solana keypair directly from an encrypted private key string.
    
        Args:
            encrypted_private_key: The base64 encoded encrypted private key
        password: The password used to derive the encryption key
        salt: The salt used during key derivation (if None, uses fixed salt)
    
        Returns:
            Keypair: The restored Solana keypair
    
        Raises:
            ValueError: If decryption fails
        """
        try:
        # Use provided salt or default
           if salt is None:
              salt = b"obverse-109/*767^&%^%"  # Should match the salt used during encryption
        
           # Derive the encryption key
           derived_key, _ = self.generate_fernet_key(password=password, salt=salt)
        
           # Decrypt and restore the keypair
           restored_keypair = self.decrypt_to_keypair(encrypted_private_key, derived_key)
           print(restored_keypair.pubkey()) 

           logger.info("Successfully restored keypair from encrypted key")
        #    print(restored_keypair)
           return restored_keypair 
        except Exception as e:
           logger.error(f"Error restoring keypair from encrypted key: {str(e)}")
           raise ValueError("Failed to decrypt private key") from e 
    
    async def create_solana_wallet(self,user_id:str)->Wallet:
        """
        Creates a new solana wallet , encypts the private key , and stores it in MongoDB
        Args:
           user_id:The ID of the user who owns this wallet
        Returns:
           Wallets: The created wallet document  
        """
        # Password-based encryption
        password = "my-strong-password-123"
        salt = b"obverse-109/*767^&%^%"
        derived_key ,salt = self.generate_fernet_key(password=password,salt=salt)
        kp,enc_priv = self.generate_new_keypair(derived_key)

        # Encrypt existing keypair with password
        pw_encrypted = self.encrypt_private_key(kp,derived_key)
        # print(f"Password-Encrypted: {pw_encrypted}")
        # Decrypt with password (must use same password and salt)
        pw_restored = self.decrypt_to_keypair(pw_encrypted, derived_key)
        print(f"Password-Restored: {pw_restored.pubkey()}")
        public_key = str(pw_restored.pubkey())
        private_key = pw_encrypted

       
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
        print(f"Public Key: {public_key}")
        wallet = Wallet(
            user_id=PydanticObjectId(user_id),
            chain=Chain.SOLANA,
            address=public_key,
            encrypted_private_key=pw_encrypted,
            created_at=datetime.utcnow(),
            tokens=[usdc_token,usdt_token]
        )
        await wallet.insert()
        return wallet

    async def check_wallet_balance(self,wallet_address)->float:
        """
        Check the SOL balance of a Solana wallet address using a Helium RPC endpoint.

        Args:
        wallet_address (str): The public key of the wallet to check (base-58 encoded string).
        helium_rpc_url (str): The Helium RPC endpoint URL.
    
        Returns:
        float: The wallet balance in SOL.
    
        Raises:
        ValueError: If the wallet address is invalid.
        Exception: If there's an error connecting to the RPC or fetching the balance.
        """
        try:
            # Initialise solana client with Helium RPC endpoint
            client = Client(self.rpc)
            try:
                pubkey = Pubkey.from_string(wallet_address)
            except ValueError as e:
                raise ValueError(f"Invalid wallet address: {str(e)}")
            response = client.get_balance(pubkey)
            # Check if response is valid and access balance
            if not hasattr(response, 'value'):
                raise Exception("Failed to fetch balance: Invalid RPC response")
        
            balance_lamports = response.value
        
            # Convert lamports to SOL (1 SOL = 1_000_000_000 lamports)
            balance_sol = balance_lamports / 1_000_000_000
        
            return balance_sol
            
            # if "results" not in response or "value" not in response["result"]:
            #     raise Exception("Failed to fetch balance:Invalid RPC Response")
            # balance_lamports = response["result"]["value"]
            # balance_sol = balance_lamports / 1_000_000_000
            # return balance_sol
        except Exception as e:
            raise Exception(f"Error fetching wallet balance : {str(e)}")

 
