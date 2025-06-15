from fastapi import FastAPI,Depends
from fastapi import APIRouter
from ..services.wallet import WalletService
from ..repositories.wallet import WalletRepository
from typing import Annotated

wallet_router = APIRouter(prefix="/wallets",tags=["wallets"])

async def get_wallet_repository()->WalletRepository:
    """
    Creates and Returns a WalletRepository instance
    """
    return WalletRepository()

async def get_wallet_service(wallet_repository:WalletRepository=Depends(get_wallet_repository))->WalletService:
    """
    Creates and Returns a UserService instance with injected dependency
    """
    return WalletService(wallet_repository)

WalletServiceDep = Annotated[WalletService,Depends(get_wallet_service)]


@wallet_router.get("/")
async def get_all_wallets(wallets:WalletService=Depends(get_wallet_service)):
    """
    Get all wallets
    """
    try:
        wallet = await wallets.repository.get_all()
        return wallet
    except RuntimeError as e:
        raise
